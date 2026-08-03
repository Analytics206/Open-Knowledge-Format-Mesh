#!/usr/bin/env python3
"""The review console — the same page, served, with the edit surface switched on.

    python okfm/okfm.py console --by human:you
    python okfm/okfm.py console --by human:you --port 7345

Open http://127.0.0.1:7345. Opened from `file://` the very same page is the read-only
viewer it has always been; the edit controls appear only when this server answers.

## What it is for

Approving a concept was: open the file, find `status:`, change `draft` to `stable`, find
`verified:`, write today's date and your own handle, then remember that `okfm_captured` also
needed repinning or the drift you just reviewed comes back tomorrow. Four hand edits across
two parts of a file, per concept, with the fourth easy to forget and silent when forgotten.

It is now a button, and the button runs `revalidate --by <you> --stable` — the command that
already existed and already did all four.

## The rules this holds

**One page, not two.** [DR-0011](../docs/decisions/0011-viewer-and-console.md) called for a
separate console artifact. That was written before the viewer had to be split in two for
[DR-0017](../docs/decisions/0017-two-viewers.md), which immediately needed a generator and a
CI check to stop two copies of the markup diverging. A third copy is the larger risk, so the
edit surface lives in the one page and is dark unless something answers `/api/ping`. Delete
this file and a fully working viewer remains, which was DR-0011's real requirement.

**It never writes a concept field itself.** Approving shells out to `revalidate.py`; saving
goes through `concept_edit.py`. Both are what the CLI runs. A mutation that behaved one way
in the browser and another in the terminal would be two implementations of one rule, which
is the mistake this project has undone more times than any other.

**Every write is attributed.** `--by` is required and must be `human:<id>`, exactly as
`revalidate` requires it, because the console does not make a machine's edit into a person's
by being a web page. The handle is displayed in the masthead the entire time it is running.

## What it deliberately does not do

Bind to anything but the loopback, answer a cross-origin request, or serve a file outside the
project. A local server that edits files on a POST is a file-write primitive for any page the
browser happens to have open, so mutations require an `X-OKFM` header — which a cross-origin
form cannot set without a preflight this server does not answer — and every path is resolved
and checked to be a concept inside a configured bundle before it is opened.

`needs: []`.
"""
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import concept_edit
from okfm_core import (HERE, PROJECT, configured_bundles, frontmatter, is_concept,
                       load_or_create_config, mesh_path, reject_unknown, scalar,
                       utf8_stdout)

utf8_stdout()

DEFAULT_PORT = 7345
# Held in memory, one deep, per path. A `.bak` beside a concept is a file the build has to be
# taught to ignore, and this project has already shipped one directory of those.
UNDO: dict[str, str] = {}


def viewer_path(cfg: dict) -> Path:
    rel = (((cfg.get("read") or {}).get("web_ui") or {}).get("path")) or "./okfm-web-ui.html"
    p = (PROJECT / rel).resolve()
    return p if p.is_file() else (HERE / "okfm-web-ui.html")


def concept_map(cfg: dict) -> dict[str, Path]:
    """`/<bundle>/<path>` → the file, for every concept the configured bundles hold.

    **The browser addresses concepts by mesh path and never sends a filesystem path.** That
    is the entire path-safety story, and it is a property rather than a filter: a request
    naming `../../etc/passwd` is not rejected for looking dangerous, it is rejected because
    no such key exists in this map. There is nothing to escape from, because nothing the
    client says is ever joined to a directory.

    It is also the address the page already uses — `bake_web_ui` stamps the same string into
    every baked concept, from the same function — so the queue's rows and the graph's nodes
    are the same identifiers and Open lands on the concept you clicked.
    """
    out = {}
    for bundle_id, root in configured_bundles(cfg).items():
        base = (PROJECT / root).resolve() if not Path(root).is_absolute() else Path(root)
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if is_concept(p):
                out[mesh_path(bundle_id, base, p)] = p.resolve()
    return out


def run(script: str, args: list[str]) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HERE / script), *args], cwd=PROJECT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


class Server(ThreadingHTTPServer):
    """A second console must not be able to bind a port the first one is serving.

    `socketserver` sets `allow_reuse_address = 1`, which on POSIX only skips TIME_WAIT and is
    wanted. **On Windows the same flag lets any process bind a port another process is
    actively serving on**, and the older socket keeps taking the connections. Observed here,
    not reasoned about: a console left running against a deleted temporary directory answered
    `/api/ping` with `project: my-project` while a second console — started afterwards, in
    this repository, printing a banner that said it was serving 73 concepts from here — was
    bound to the same port and receiving nothing.

    Both processes believed they were serving. The browser was talking to a mesh that no
    longer existed on disk, and every approval typed into that page would have been written
    somewhere the person clicking had never heard of. Failing to bind is the correct
    behaviour and it is one line.
    """
    allow_reuse_address = (os.name != "nt")
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    server_version = "okfm-console"
    by = "human:unknown"
    cfg: dict = {}

    def log_message(self, fmt, *args):
        pass                                    # the console prints what matters itself

    # ---- plumbing --------------------------------------------------------
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        # No CORS header, on purpose: a page from another origin must not read this.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode("utf-8"), "application/json; charset=utf-8")

    def _guard(self) -> bool:
        """A mutation must come from this page, not from whatever else the browser has open."""
        if self.headers.get("X-OKFM") != "1":
            self._json({"error": "missing X-OKFM header — mutations must come from the "
                                 "console page itself"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).hostname not in ("127.0.0.1", "localhost"):
            self._json({"error": f"cross-origin request from {origin} refused"}, 403)
            return False
        return True

    def _concept(self, p: str) -> Path | None:
        """A mesh path to a file, or None. Nothing the client sends is joined to a path."""
        return concept_map(self.cfg).get(p or "")

    # ---- reads -----------------------------------------------------------
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path in ("/", "/index.html"):
            html = viewer_path(self.cfg).read_bytes()
            return self._send(200, html, "text/html; charset=utf-8")

        if u.path == "/api/ping":
            return self._json({"ok": True, "by": self.by,
                               "project": PROJECT.name, "version": "0.2.1"})

        if u.path == "/api/concept":
            mp = (q.get("p") or [""])[0]
            p = self._concept(mp)
            if not p:
                return self._json({"error": "not a concept in a configured bundle"}, 404)
            try:
                parsed = concept_edit.parse(p)
            except ValueError as e:
                return self._json({"error": str(e)}, 400)
            block, _ = frontmatter(p)
            return self._json({**parsed, "p": mp,
                               "file": p.relative_to(PROJECT).as_posix(),
                               "status": scalar(block, "status"),
                               "undo": mp in UNDO})

        if u.path == "/api/queue":
            return self._json({"queue": self.review_queue()})

        return self._json({"error": "no such endpoint"}, 404)

    def review_queue(self) -> list[dict]:
        """Every `status: draft` concept — what an Approve button is for."""
        out = []
        for mp, p in sorted(concept_map(self.cfg).items()):
            block, _ = frontmatter(p)
            if not block:
                continue
            if (scalar(block, "status") or "").strip() == "draft":
                out.append({"p": mp, "file": p.relative_to(PROJECT).as_posix(),
                            "title": scalar(block, "title") or p.stem,
                            "verified": bool(re.search(r"^verified:", block, re.M))})
        return out

    # ---- writes ----------------------------------------------------------
    def do_POST(self):
        if not self._guard():
            return
        u = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._json({"error": "body must be JSON"}, 400)

        if u.path == "/api/pipeline":
            code, out = run("okfm.py", [])
            return self._json({"ok": code == 0, "output": out[-4000:]})

        mp = payload.get("p") or ""
        p = self._concept(mp)
        if not p:
            return self._json({"error": "not a concept in a configured bundle"}, 404)
        rel = p.relative_to(PROJECT).as_posix()

        if u.path in ("/api/approve", "/api/revalidate"):
            args = [rel, "--by", self.by] + (["--stable"] if u.path.endswith("approve") else [])
            code, out = run("revalidate.py", args)
            return self._json({"ok": code == 0, "output": out.strip()[-2000:]})

        if u.path == "/api/save":
            fields = payload.get("fields") or {}
            sections = payload.get("sections")
            try:
                UNDO[mp] = concept_edit.write(p, fields=fields, sections=sections)
            except (ValueError, OSError) as e:
                return self._json({"error": str(e)}, 400)
            # Validate AFTER, and say so plainly. There is no YAML parser here to check a
            # frontmatter edit before it lands, so the honest design is to make the mistake
            # cheap rather than to pretend it cannot happen.
            code, out = run("check_bundles.py", [])
            return self._json({"ok": code == 0, "validated": code == 0,
                               "output": out.strip()[-2000:], "undo": True})

        if u.path == "/api/undo":
            text = UNDO.pop(mp, None)
            if text is None:
                return self._json({"error": "nothing to undo for this concept"}, 400)
            concept_edit.restore(p, text)
            return self._json({"ok": True})

        return self._json({"error": "no such endpoint"}, 404)


def main() -> int:
    argv = sys.argv[1:]
    reject_unknown(argv, ("--by", "--port", "--no-open"), __doc__)

    by, port = None, None
    for i, a in enumerate(argv):
        if a.startswith("--by="):
            by = a.split("=", 1)[1]
        elif a == "--by" and i + 1 < len(argv):
            by = argv[i + 1]
        elif a.startswith("--port="):
            port = a.split("=", 1)[1]
        elif a == "--port" and i + 1 < len(argv):
            port = argv[i + 1]

    if not by or not by.startswith("human:") or len(by) <= len("human:"):
        # The same refusal `revalidate` makes, for the same reason and in the same words.
        # A console that supplied a default identity would be a process signing a person's
        # name, with a browser in between to make it look like it was not.
        print("error: the console writes as a person — --by must be `human:<id>`",
              file=sys.stderr)
        print("       python okfm/okfm.py console --by human:you", file=sys.stderr)
        return 2

    _, cfg, _ = load_or_create_config(write=False)
    if port is None:
        port = ((cfg.get("read") or {}).get("web_ui") or {}).get("serve_port") or DEFAULT_PORT
    try:
        port = int(port)
    except (TypeError, ValueError):
        print(f"error: --port must be a number, not {port!r}", file=sys.stderr)
        return 2

    Handler.by, Handler.cfg = by, cfg
    n = len(concept_map(cfg))
    try:
        httpd = Server(("127.0.0.1", port), Handler)
    except OSError as e:
        print(f"error: cannot listen on 127.0.0.1:{port} — {e}", file=sys.stderr)
        print("       something else is already serving it; pass --port to pick another",
              file=sys.stderr)
        return 2

    url = f"http://127.0.0.1:{port}/"
    print(f"OKFM console  →  {url}")
    print(f"  signing as   {by}")
    print(f"  editing      {n} concept(s) in {PROJECT}")
    print(f"  loopback only, and nothing outside those concepts is readable or writable")
    print("\nCtrl-C to stop.")
    if "--no-open" not in argv:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
