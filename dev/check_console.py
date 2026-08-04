#!/usr/bin/env python3
"""The console's writes, against a real server, over real HTTP.

    python dev/check_console.py

## Why this exists

`dev/check_readme.py` starts the console and asks `/api/ping` whether anything is alive. That
is all the coverage the console had. Everything it can actually *do* to a file — approve, save,
undo — was untested, which is an odd place to draw the line: the endpoints that only read were
the ones being checked, and the endpoints that write were not.

Four of these are regression tests for defects that shipped.

  * **A second console could bind a port the first was serving.** `socketserver` sets
    `allow_reuse_address = 1`; on POSIX that skips TIME_WAIT and is wanted, and on Windows it
    lets a process take a port another process is actively serving on, with the older socket
    keeping the connections. A console left over from a deleted sandbox answered `/api/ping`
    with a different project's name while a console started in this repository, printing a
    banner about 73 concepts, received nothing. An Approve clicked in that browser would have
    written to a mesh the person clicking had never heard of.
  * **`--by` must be `human:<id>`.** The same refusal `revalidate` makes. A console that
    supplied a default identity would be a process signing a person's name with a web page in
    between to make it look otherwise.
  * **Path safety is a property, not a filter.** The browser addresses concepts by mesh path
    and the server resolves them through a dict. A traversal string is refused because no such
    key exists, not because it looked dangerous — so this asserts the 404 rather than trusting
    a pattern to have been written correctly.
  * **A mutation needs the `X-OKFM` header.** A local server that writes files on a POST is a
    file-write primitive for every page the browser has open.

Run against a sandbox — a temporary project with its own `dropin/`, its own config and two
concepts — because a check that approves things to prove it can approve things would leave this
repository's review queue holding decisions nobody made. `needs: []`.
"""
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

CONFIG = {
    "okfm": "0.2.1",
    "bundles": {"notes": "./notes"},
    "read": {"web_ui": {"path": "./nothing-here.html"}},
}

SOURCE = "the thing a concept points at\n"

# A deliberately wrong hash, so a repin is observable rather than assumed. Approve promises
# four edits and the fourth — repinning every capture — is the one that is silent when it does
# not happen, which is exactly why it is worth asserting separately.
STALE = "sha256:" + "0" * 64


def concept(title: str, resource: str) -> str:
    return f"""---
type: Document
title: {title}
description: "A concept that exists so the console has something to write to."
status: draft
tags: [needs-nothing]
sources:
  - id: subject
    resource: {resource}
    okfm_role: subject
    okfm_captured: {{ hash: "{STALE}", at: 2020-01-01 }}
okfm_scope: project
okfm_relations:
  - {{ predicate: part_of, target: /index.md }}
---

# First

first section

# Second

second section
"""


def sandbox(root: Path) -> Path:
    """A project the console can serve, with nothing of this repository's in it but the code."""
    shutil.copytree(PROJECT / "dropin", root / "dropin",
                    ignore=shutil.ignore_patterns("__pycache__", ".okfm-cache"))
    (root / "okfm.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8", newline="\n")
    notes = root / "notes"
    notes.mkdir()
    (notes / "source.txt").write_text(SOURCE, encoding="utf-8", newline="\n")
    (notes / "index.md").write_text(concept("Index", "./source.txt"), encoding="utf-8",
                                    newline="\n")
    (notes / "alpha.md").write_text(concept("Alpha", "./source.txt"), encoding="utf-8",
                                    newline="\n")
    return root


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def start(project: Path, port: int, by: str) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, str(project / "dropin" / "console.py"),
         "--by", by, "--port", str(port), "--no-open"],
        cwd=project, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", start_new_session=(os.name != "nt"))


def kill_tree(proc: subprocess.Popen) -> None:
    """The tree. Leaking one of these is how the port-hijack bug got its second half."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], capture_output=True)
    else:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def wait_for(port: int, proc: subprocess.Popen) -> str | None:
    for _ in range(60):
        if proc.poll() is not None:
            return (proc.stdout.read() or "")[-800:]
        try:
            with socket.create_connection(("127.0.0.1", port), 0.25):
                return None
        except OSError:
            time.sleep(0.25)
    return "nothing answered within 15s"


def call(port: int, path: str, body=None, headers=None) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers=headers if headers is not None else {"X-OKFM": "1"},
        method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw.startswith(("{", "[")) else {"raw": raw})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        return e.code, (json.loads(raw) if raw.startswith("{") else {"raw": raw})


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        project = sandbox(Path(tmp) / "proj")
        alpha = project / "notes" / "alpha.md"

        # --- the sandbox has to be valid, or nothing below means anything ----
        r = subprocess.run([sys.executable, str(project / "dropin" / "check_bundles.py")],
                           cwd=project, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        if r.returncode != 0:
            print("the sandbox mesh does not validate, so `save` reporting a validation "
                  "failure would prove nothing:\n" + (r.stdout or "")[-1200:], file=sys.stderr)
            return 2
        print("  ok  the sandbox is a valid mesh before anything touches it")

        # --- who it will not sign as ----------------------------------------
        # A refusal happens before the socket is bound, so these come back immediately. If one
        # does not come back it did not refuse — and it must be reported as that, not left to
        # surface as a TimeoutExpired traceback sixty seconds later with no rule named.
        signed = []
        for args, why in ((["--by", "process:agent"], "a process actor"),
                          (["--by", "human:"], "an empty handle"),
                          ([], "no identity at all")):
            proc = subprocess.Popen([sys.executable, str(project / "dropin" / "console.py"),
                                     *args, "--port", str(free_port()), "--no-open"],
                                    cwd=project, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                    errors="replace", start_new_session=(os.name != "nt"))
            try:
                code = proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                code = 0                            # it is serving, which is the failure
            finally:
                kill_tree(proc)
            if code == 0:
                signed.append(why)
        if signed:
            problems.append(f"the console agreed to run as {', '.join(signed)} — every write it "
                            f"makes is attributed, and it refuses `process:` for the same "
                            f"reason `revalidate` does")
        else:
            print("  ok  it refuses to run as a process, as an empty handle, or as nobody")

        # --- serving ---------------------------------------------------------
        port, by = free_port(), "human:checkbot"
        proc = start(project, port, by)
        second = None
        try:
            died = wait_for(port, proc)
            if died is not None:
                print(f"the console did not serve: {died}", file=sys.stderr)
                return 2

            code, ping = call(port, "/api/ping")
            if ping.get("by") != by:
                problems.append(f"/api/ping reports {ping.get('by')!r}, not the handle it was "
                                f"started with — the masthead would name the wrong person")
            else:
                print(f"  ok  /api/ping names the handle it was started with ({by})")

            # --- a second console must not take the port --------------------
            second = start(project, port, by)
            time.sleep(2.0)
            if second.poll() is None:
                problems.append(f"a second console bound 127.0.0.1:{port} while the first was "
                                f"serving it — on Windows the older socket keeps the "
                                f"connections, so the browser talks to whichever mesh it "
                                f"happens to reach")
            else:
                out = (second.stdout.read() or "")
                if "already serving" not in out and "cannot listen" not in out:
                    problems.append(f"the second console exited but did not say what was "
                                    f"holding the port: {out.strip()[-300:]!r}")
                else:
                    print("  ok  a second console refuses the port and names what holds it")

            # --- the queue ---------------------------------------------------
            code, q = call(port, "/api/queue")
            paths = sorted(row["p"] for row in q.get("queue", []))
            if paths != ["/notes/alpha.md", "/notes/index.md"]:
                problems.append(f"/api/queue listed {paths}, not both drafts")
            else:
                print("  ok  /api/queue lists every draft, by mesh path")

            # --- nothing the client sends is joined to a path ----------------
            escapes = ["../okfm.json", "/notes/../../okfm.json", "/../dropin/console.py",
                       "notes/alpha.md", "", "/notes/alpha.md/../../okfm.json"]
            leaked = [e for e in escapes if call(port, "/api/concept?p=" + e)[0] != 404]
            if leaked:
                problems.append(f"/api/concept resolved {leaked} — a mesh path is a dict key, "
                                f"and anything that is not one has no file behind it")
            else:
                print(f"  ok  {len(escapes)} paths that are not mesh paths resolve to nothing")

            # --- a mutation must come from the page --------------------------
            # The payload is deliberately inert — no `sections` key, so even if the guard is
            # gone the write is a no-op. A probe for a refusal that would *destroy* the file
            # when the refusal fails turns one clear failure into a cascade: the first run of
            # this check emptied the concept's body and then reported an IndexError three
            # assertions later, which names nothing and blames the wrong line.
            before = alpha.read_bytes()
            unguarded = []
            for label, headers in (("no X-OKFM header", {}),
                                   ("a cross-origin Origin",
                                    {"X-OKFM": "1", "Origin": "https://evil.example"})):
                code, _ = call(port, "/api/save", {"p": "/notes/alpha.md", "fields": {}},
                               headers=headers)
                if code != 403:
                    unguarded.append(f"{label} → {code}")
            if unguarded:
                problems.append(f"a POST was accepted with {', '.join(unguarded)} — this is a "
                                f"file-write primitive for whatever else the browser has open")
            elif alpha.read_bytes() != before:
                problems.append("a refused POST still changed the file")
            else:
                print("  ok  a POST without the header, or from another origin, is refused")
            if alpha.read_bytes() != before:
                alpha.write_bytes(before)       # so what follows still tests what it says it does

            # --- save, and undo ----------------------------------------------
            code, doc = call(port, "/api/concept?p=/notes/alpha.md")
            secs = [dict(s) for s in doc["sections"]]
            secs[0]["text"] = "REWRITTEN"
            fields = {f["key"]: f["raw"] for f in doc["fields"] if not f["locked"]}
            code, res = call(port, "/api/save",
                             {"p": "/notes/alpha.md", "fields": fields, "sections": secs})
            now = alpha.read_text(encoding="utf-8")
            if "REWRITTEN" not in now:
                problems.append(f"/api/save did not write the edit: {res}")
            elif "second section" not in now:
                problems.append("/api/save lost the section that was not edited")
            elif not res.get("validated"):
                problems.append(f"/api/save wrote, but reported the mesh invalid: "
                                f"{str(res.get('output'))[-300:]}")
            else:
                print("  ok  /api/save writes the edited section, keeps the rest, revalidates")

            code, res = call(port, "/api/undo", {"p": "/notes/alpha.md"})
            if alpha.read_bytes() != before:
                problems.append("/api/undo did not put the file back exactly as it was")
            else:
                print("  ok  /api/undo restores the previous bytes exactly")

            # --- a machine key is refused over HTTP too ----------------------
            code, res = call(port, "/api/save",
                             {"p": "/notes/alpha.md", "fields": {"sources": "sources: []"},
                              "sections": None})
            if code == 200 or alpha.read_bytes() != before:
                problems.append("/api/save accepted an edit to `sources` — a machine key must "
                                "be refused at the server, not only hidden in the page")
            else:
                print("  ok  /api/save refuses a machine key, and changes nothing when it does")

            # --- approve does all four ----------------------------------------
            code, res = call(port, "/api/approve", {"p": "/notes/alpha.md"})
            text = alpha.read_text(encoding="utf-8")
            missing = []
            if "status: stable" not in text:
                missing.append("status is still draft")
            if f'verified: {{ by: "{by}"' not in text:
                missing.append("verified does not name the approver")
            if STALE in text:
                missing.append("okfm_captured was not repinned — the drift comes straight back")
            if "first section" not in text or "second section" not in text:
                missing.append("the body did not survive")
            if missing:
                problems.append("approve left the concept incomplete: " + "; ".join(missing)
                                + f"  [{str(res.get('output'))[-200:]}]")
            else:
                print("  ok  approve promotes, stamps the approver, and repins every capture")
        finally:
            kill_tree(proc)
            if second is not None:
                kill_tree(second)

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — the console writes what it says, to the file it says, as the person who ran it"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
