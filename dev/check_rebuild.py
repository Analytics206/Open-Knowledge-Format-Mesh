#!/usr/bin/env python3
"""A rebuild that finds nothing new writes nothing.

    python dev/check_rebuild.py

## Why this exists

`generated.at` and `okfm_captured.at` carry the date the build ran. So a build on a *later day*
than the last one rewrote every concept the build still owns, whether or not a single source
file had changed — a full-mesh diff of pure timestamps, saying nothing.

It lands hardest on exactly the person least able to read it. Nothing in a new adopter's mesh
is `verified:` yet, so `_owned` returns true for all of it, so every day's first run restates
the whole mesh. Drift is supposed to be the legible signal in `.okfm/`; a daily rewrite of
every file is noise laid directly over it.

## The trap this check exists to avoid

**Running the build twice and diffing proves nothing.** The stamp is `datetime.now(utc)`
truncated to the day, so two runs a second apart produce identical text and the test passes
whether or not the bug is present. That is a check that reports success for a property it
never examined, which is worse than no check at all.

So this **backdates the built mesh** between the two runs — the same thing a calendar does
overnight — and only then asserts the second run is a no-op.

The negative half matters just as much. A skip that is too eager is a build that stops
updating concepts whose sources really did change, which fails silently and looks like
everything is fine. So a source is edited and the check asserts that its concept **is**
rewritten, with a fresh stamp, and that nothing else is.

`needs: []`.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

CONFIG = {
    "okfm": "0.2.1",
    "build": {"root": "docs", "root_files": True, "out": ".okfm", "mesh": "mesh",
              "mode": "mirror", "exclude": [], "include": []},
}

DOCS = {
    "alpha.md": "# Alpha\n\nThe first document, which will not change.\n",
    "beta.md": "# Beta\n\nThe second document, which will.\n",
    "guide/nested.md": "# Nested\n\nA document in a subfolder, so a second bundle exists.\n",
}

# Any date, anywhere in a built concept. Broad on purpose: this is the fixture being aged, not
# the build's own comparison, and the fixture's sources contain no dates of their own.
ANY_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def build(project: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(project / "dropin" / "build.py"), "--apply"],
                          cwd=project, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=180)


def snapshot(mesh: Path) -> dict[str, bytes]:
    return {p.relative_to(mesh).as_posix(): p.read_bytes() for p in sorted(mesh.rglob("*.md"))}


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "proj"
        shutil.copytree(PROJECT / "dropin", project / "dropin",
                        ignore=shutil.ignore_patterns("__pycache__", ".okfm-cache"))
        (project / "okfm.json").write_text(json.dumps(CONFIG, indent=2), encoding="utf-8",
                                           newline="\n")
        for rel, text in DOCS.items():
            f = project / "docs" / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8", newline="\n")

        mesh = project / ".okfm"
        r = build(project)
        if r.returncode != 0 or not mesh.is_dir():
            print(f"the sandbox build failed, so nothing below means anything:\n"
                  f"{(r.stdout or '')[-1500:]}{(r.stderr or '')[-800:]}", file=sys.stderr)
            return 2
        first = snapshot(mesh)
        if len(first) < 4:
            print(f"the sandbox built only {len(first)} concept(s) — too few to test with",
                  file=sys.stderr)
            return 2
        print(f"  ok  the sandbox builds {len(first)} concepts across "
              f"{len({k.split('/')[0] for k in first})} bundles")

        # --- age the mesh, which is the only reason this check is not vacuous ----
        for p in mesh.rglob("*.md"):
            p.write_text(ANY_DATE.sub("2020-01-01", p.read_text(encoding="utf-8")),
                         encoding="utf-8", newline="\n")
        aged = snapshot(mesh)

        r = build(project)
        after = snapshot(mesh)
        churned = sorted(k for k in aged if after.get(k) != aged[k])
        if r.returncode != 0:
            problems.append(f"the second build failed: {(r.stdout or '')[-600:]}")
        elif churned:
            problems.append(f"{len(churned)} concept(s) were rewritten by a build that found "
                            f"nothing new: {', '.join(churned[:6])}"
                            + (" …" if len(churned) > 6 else "")
                            + " — on a mesh a day old, that is every file the build owns")
        else:
            print(f"  ok  a build a day later rewrites none of {len(aged)} unchanged concepts")

        # --- and a source that DID change is still rewritten ---------------------
        # The half that keeps the skip honest. A comparison that is too eager stops updating
        # real changes, which fails silently and looks exactly like everything working.
        (project / "docs" / "beta.md").write_text(
            "# Beta\n\nThe second document, now saying something else entirely.\n",
            encoding="utf-8", newline="\n")
        r = build(project)
        final = snapshot(mesh)
        moved = sorted(k for k in aged if final.get(k) != aged[k])
        target = next((k for k in final if k.endswith("beta.md")), None)
        if r.returncode != 0:
            problems.append(f"the third build failed: {(r.stdout or '')[-600:]}")
        elif target is None:
            problems.append("no concept was built for docs/beta.md at all")
        elif target not in moved:
            problems.append(f"{target} was NOT rewritten after its source changed — the "
                            f"comparison is too eager, and a real edit now goes unrecorded")
        elif "2020-01-01" in final[target].decode("utf-8"):
            problems.append(f"{target} was rewritten but kept the stale stamp — a concept that "
                            f"really was regenerated has to say when")
        elif len(moved) > 1:
            problems.append(f"changing one source rewrote {len(moved)} concepts: "
                            f"{', '.join(moved)}")
        else:
            print(f"  ok  changing one source rewrites that concept, with a fresh stamp, "
                  f"and nothing else")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — the build writes what changed and leaves the rest alone"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
