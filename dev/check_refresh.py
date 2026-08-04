#!/usr/bin/env python3
"""Every pointer is observed, and the observer, the repinner and the viewer agree.

    python dev/check_refresh.py

## Why this exists

Drift is the signal every trust verdict in this project derives from, and nothing asserted a
single verdict it produced. `refresh` ran in CI on every pipeline invocation, so it was
*executed* constantly and *checked* never — which is a distinction worth naming, because a
component that runs green a hundred times a day looks tested.

Reading source entries had **three** implementations. `refresh` matched an entry with a
continuation group of `(?:\\n\\s+.*)*` — any indented line, including the next `- id:` — so the
first entry swallowed the rest and only its resource was read. `revalidate` and `bake_web_ui`
each had their own regex; both were correct, both were different.

The one that disagreed was the one that produces the signal. In this repository:

    59 source pointers exist
    42 were observed
    17 were invisible, and 11 of those were drifted

Every invisible pointer was a second entry, and second entries are systematically the
**implementation** a concept documents — `the-tier-guard.md → guard.py`,
`validation.md → check_bundles.py`, `the-agent-contract.md → templates/AGENTS.md`. The mesh's
whole claim is that these concepts describe this code. Drift was watching the prose and never
the code, so `revalidate` was faithfully repinning captures nothing ever read.

Two smaller ones came with it. `bake_web_ui.drift_of` rendered a concept whose pointers carry
no capture as **fresh**, four lines below a docstring saying that defaulting to fresh is the
failure §3.4 exists to prevent — while `refresh` called the same concept `unknown`. And the
observation cache was only ever appended to: 81 of its 137 entries pointed at concepts and
sources that no longer existed.

Everything below runs against a sandbox mesh with known hashes, because the only way to test a
drift detector is to drift something on purpose. `needs: []`.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT / "dropin"))

from bake_web_ui import drift_of  # noqa: E402
from okfm_core import (configured_bundles, frontmatter, load_or_create_config,  # noqa: E402
                       scalar, source_entries)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def concept(title: str, status: str, pins: list[tuple[str, str, str | None]]) -> str:
    """`pins` is (id, resource, hash-or-None) — None meaning a pointer nobody has pinned yet."""
    rows = []
    for sid, res, h in pins:
        rows += [f"  - id: {sid}", f"    resource: {res}", "    okfm_role: subject"]
        if h is not None:
            rows.append(f'    okfm_captured: {{ hash: "sha256:{h}", at: 2026-08-01 }}')
    body = "sources:\n" + "\n".join(rows) if rows else ""
    return (f"---\ntype: Document\ntitle: {title}\n"
            f'description: "A concept with {len(pins)} pointer(s)."\n'
            f"status: {status}\ntags: [needs-nothing]\n"
            f'generated: {{ by: "process:okfm-build", at: 2026-08-01T00:00:00Z }}\n'
            f"{body}\nokfm_scope: project\n---\n\n# Body\n\nProse.\n")


FILES = {"a.txt": "alpha source\n", "b.txt": "beta source\n", "c.txt": "gamma source\n"}


def sandbox(root: Path) -> Path:
    root.mkdir(parents=True)
    shutil.copytree(PROJECT / "dropin", root / "dropin",
                    ignore=shutil.ignore_patterns("__pycache__", ".okfm-cache"))
    (root / "okfm.json").write_text('{"okfm":"0.2.1","bundles":{"notes":"./notes"}}',
                                    encoding="utf-8", newline="\n")
    n = root / "notes"
    n.mkdir()
    for name, text in FILES.items():
        (n / name).write_text(text, encoding="utf-8", newline="\n")

    # Three pointers, each pinned to ITS OWN file. If entries are paired wrongly this is where
    # it shows: a parser that reads the first hash for every resource still produces a legal
    # file, and reports two false drifts the moment anything is compared.
    (n / "three.md").write_text(
        concept("Three", "draft", [("a", "./a.txt", sha(FILES["a.txt"])),
                                   ("b", "./b.txt", sha(FILES["b.txt"])),
                                   ("c", "./c.txt", sha(FILES["c.txt"]))]),
        encoding="utf-8", newline="\n")
    (n / "unpinned.md").write_text(
        concept("Unpinned", "draft", [("a", "./a.txt", None)]),
        encoding="utf-8", newline="\n")
    (n / "bare.md").write_text(concept("Bare", "draft", []), encoding="utf-8", newline="\n")
    (n / "index.md").write_text(
        concept("Index", "draft", [("a", "./a.txt", sha(FILES["a.txt"]))]),
        encoding="utf-8", newline="\n")
    return root


def run(project: Path, script: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(project / "dropin" / script), *args],
                       cwd=project, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def cache_of(project: Path) -> dict:
    f = project / "dropin" / ".okfm-cache" / "observations.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []

    # --- the real corpus: one entry read per entry written --------------------
    # Cheap, and it is the assertion that would have caught the original bug on day one.
    _, cfg, _ = load_or_create_config(write=False)
    declared = found = 0
    for _bid, root in sorted(configured_bundles(cfg).items()):
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            block, _b = frontmatter(f)
            if not block or not scalar(block, "type"):
                continue
            declared += len(re.findall(r"^\s+- id:", block, re.M))
            found += len([e for e in source_entries(block) if e["resource"]])
    if declared != found:
        problems.append(f"the mesh declares {declared} source pointers and the parser finds "
                        f"{found} — every missing one is a pointer nothing observes")
    else:
        print(f"  ok  all {declared} source pointers in the mesh are read, not just the first "
              f"of each")

    with tempfile.TemporaryDirectory() as tmp:
        p = sandbox(Path(tmp) / "proj")
        n = p / "notes"

        # --- each pointer is paired with its own capture ----------------------
        block, _b = frontmatter(n / "three.md")
        got = [(e["id"], e["resource"], e["hash"]) for e in source_entries(block)]
        want = [("a", "./a.txt", sha(FILES["a.txt"])), ("b", "./b.txt", sha(FILES["b.txt"])),
                ("c", "./c.txt", sha(FILES["c.txt"]))]
        if got != want:
            problems.append(f"three pointers did not parse to three independent pairs: {got}")
        else:
            print("  ok  each pointer keeps its own resource and its own capture")

        # --- a clean mesh reports no drift ------------------------------------
        code, out = run(p, "refresh.py")
        if "0 drifted" not in out:
            problems.append(f"a mesh pinned to its own sources reported drift: "
                            f"{out.splitlines()[0] if out else out!r}")
        elif "1 unknown" not in out:
            problems.append(f"the unpinned pointer was not counted as unknown: "
                            f"{out.splitlines()[0] if out else out!r}")
        else:
            print("  ok  a mesh pinned to its own sources: 0 drifted, the unpinned one unknown")

        # --- drift in a pointer that is not the first -------------------------
        # The whole finding, reduced to one assertion. Before the fix this reported 0 drifted.
        (n / "c.txt").write_text("gamma source, changed\n", encoding="utf-8", newline="\n")
        code, out = run(p, "refresh.py")
        if "1 drifted" not in out or "./c.txt" not in out:
            problems.append(f"changing the THIRD source of a concept was not reported — a "
                            f"concept's later pointers are its implementation, and they are "
                            f"the ones worth watching: {out.strip()[:400]}")
        else:
            print("  ok  drift in a concept's third pointer is observed and named")

        # --- and the first still works ----------------------------------------
        (n / "a.txt").write_text("alpha source, changed\n", encoding="utf-8", newline="\n")
        code, out = run(p, "refresh.py")
        if "3 drifted" not in out:
            problems.append(f"with a.txt and c.txt changed, expected 3 drifted pointers "
                            f"(three.md twice, index.md once): {out.strip()[:300]}")
        else:
            print("  ok  drift is counted per pointer, not per concept")

        # --- the viewer and the observer agree --------------------------------
        # They disagreed: `refresh` called an unpinned pointer unknown and the page rendered
        # it fresh. A person reads the page.
        obs = cache_of(p)
        verdicts = {}
        for name in ("three.md", "unpinned.md", "bare.md"):
            b, _x = frontmatter(n / name)
            verdicts[name] = drift_of(b, f"notes/{name}", obs)
        if verdicts["unpinned.md"] is not None:
            problems.append(f"the viewer renders an unpinned pointer as "
                            f"{verdicts['unpinned.md']!r}; refresh calls it unknown — and the "
                            f"viewer is the one a person reads")
        elif verdicts["bare.md"] != 0:
            problems.append(f"a concept with no pointers at all rendered "
                            f"{verdicts['bare.md']!r}; it cannot drift, and saying `unknown` "
                            f"would flood the page with a non-question")
        elif verdicts["three.md"] != 1:
            problems.append(f"the viewer rendered {verdicts['three.md']!r} for a concept "
                            f"refresh reports as drifted")
        else:
            print("  ok  the viewer's verdict matches the observer's, unknown included")

        # --- revalidate repins every entry, each from its own file ------------
        code, out = run(p, "revalidate.py", "notes/three.md", "--by", "human:checkbot")
        block, _b = frontmatter(n / "three.md")
        pins = {e["id"]: e["hash"] for e in source_entries(block)}
        want = {"a": sha("alpha source, changed\n"), "b": sha(FILES["b.txt"]),
                "c": sha("gamma source, changed\n")}
        if pins != want:
            wrong = [k for k in want if pins.get(k) != want[k]]
            problems.append(f"revalidate did not repin each pointer from its own file — "
                            f"{wrong} wrong. Two files cannot share a hash, so a pointer "
                            f"pinned to another's would report drift forever: {out.strip()[:200]}")
        else:
            print("  ok  revalidate repins every pointer, each from the file it points at")

        # --- and then the observer agrees ------------------------------------
        # The round trip is the point: repinning that the observer disagrees with is drift
        # that never clears.
        code, out = run(p, "refresh.py")
        if "1 drifted" not in out or "index.md" not in out:
            problems.append(f"after revalidating three.md, exactly index.md should still be "
                            f"drifted: {out.strip()[:300]}")
        else:
            print("  ok  what revalidate writes is what refresh observes")

        # --- the cache holds what the mesh holds ------------------------------
        stale = dict(cache_of(p))
        stale["./gone.txt@notes/deleted.md"] = {"observed": "sha256:" + "0" * 64,
                                                "observed_at": "2020-01-01T00:00:00+00:00",
                                                "resolver": "file"}
        (p / "dropin" / ".okfm-cache" / "observations.json").write_text(
            json.dumps(stale, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        run(p, "refresh.py")
        if "./gone.txt@notes/deleted.md" in cache_of(p):
            problems.append("an observation for a concept that no longer exists survived a "
                            "refresh — the cache only ever grew, and the viewer bakes drift "
                            "state out of it")
        else:
            print("  ok  observations for pointers the mesh no longer holds are dropped")

        # --- --check blocks on stable, not on draft ---------------------------
        code, _out = run(p, "refresh.py", "--check")
        if code != 0:
            problems.append("--check failed on drift in `draft` concepts; a draft is expected "
                            "to be out of step with its source, which is what draft means")
        else:
            (n / "index.md").write_text(
                (n / "index.md").read_text(encoding="utf-8")
                .replace("status: draft", "status: stable"), encoding="utf-8", newline="\n")
            code, _out = run(p, "refresh.py", "--check")
            if code == 0:
                problems.append("--check passed with a drifted source in a `stable` concept, "
                                "which is the one thing it exists to stop")
            else:
                print("  ok  --check blocks on drift in a stable concept, and only then")

    print()
    for x in problems:
        print(f"  FAIL  {x}")
    print("OK — every pointer is observed, and all three readers agree"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
