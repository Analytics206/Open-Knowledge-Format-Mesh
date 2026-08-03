#!/usr/bin/env python3
"""The Phase 2 exit, run as a test: a second domain via pack + config, zero core edits.

    python dev/check_pack_example.py

Stands `examples/warehouse/` up in a temporary directory — the drop-in pasted in unmodified,
the pack copied beside it, one `okfm.json` — runs the whole pipeline, and checks four things.

## Why it is a script and not a paragraph in the roadmap

"A toy second domain stood up via pack + config with zero core edits" is a claim about code
that changes every week. Asserted once, it is true on the day it is written and unverified
forever after; the CI grep for domain words has the same shape and proves a much smaller
thing — that no domain word appears in `dropin/`, not that a NEW domain needs none.

Standing the example up on every run is the difference. It is also how the three defects
below were found, none of which were visible from inside this repository:

  the config rejected the build's own output   `bundles` naming `.okfm/docs` failed
                                               validation at step one, before the build that
                                               creates it. Every project, first run.
  in-place bundles were never registered       a bundle authored by hand and named in
                                               `bundles` got no `OKF Member`, so the mesh
                                               check rejected the mesh the build had just
                                               written. This repository's own
                                               `docs/decisions` had been in that state,
                                               unvalidated, since it was created.
  one overlay reached every vocabulary         a pack's reason code became a legal
                                               `predicate` — see `dev/check_vocab.py`.

## The four assertions

  builds        the pipeline reaches "mesh is valid" on a project it has never seen
  falsifiable   with `pack` set to null, the SAME mesh fails — on predicates, which are
                rejected rather than warned about. A pack that changes nothing when removed
                is a pack that was doing nothing.
  no core edits `dropin/` is byte-identical afterwards. The domain lives in YAML and one
                config line, which is the whole claim.
  no code       the pack is vocabulary only. §13.2 allows one adapter file; needing none is
                the stronger result and worth holding onto.

`needs: []`.
"""
import filecmp
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
EXAMPLE = PROJECT / "examples" / "warehouse"
PACK = PROJECT / "packs" / "warehouse"
DROPIN = PROJECT / "dropin"

# What `okfm.json` names. Kept here rather than parsed out of it so a rename of the pack
# directory fails loudly in one place instead of silently standing up a mesh with no pack.
PACK_REL = "packs/warehouse"


def run(cwd: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


# Runtime state the drop-in writes into its own folder, none of it source: bytecode, the
# config it synthesizes on a first run, the telemetry record per run, and the drift
# observation cache. All four are gitignored here for the same reason they are ignored
# there — "zero core edits" is a claim about the CODE, and a run that left the code
# unchanged but wrote a cache has not edited core.
RUNTIME = ["__pycache__", "okfm.json", "references", ".okfm-cache"]


def tree_differs(a: Path, b: Path) -> list[str]:
    """Every file that differs between two directories, ignoring runtime residue."""
    out, cmp = [], filecmp.dircmp(a, b, ignore=RUNTIME)

    def walk(d: filecmp.dircmp, prefix: str) -> None:
        out.extend(prefix + n for n in d.left_only + d.right_only + d.diff_files
                   + d.funny_files if n not in RUNTIME)
        for name, sub in d.subdirs.items():
            if name not in RUNTIME:
                walk(sub, f"{prefix}{name}/")

    walk(cmp, "")
    return sorted(out)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    for required in (EXAMPLE, PACK, DROPIN):
        if not required.is_dir():
            print(f"missing: {required.relative_to(PROJECT)}", file=sys.stderr)
            return 2

    problems = []

    # --- the pack is vocabulary, not code --------------------------------
    # Checked before anything is copied, because "zero core edits" means nothing if the
    # domain smuggled its logic into a pack-shaped folder instead.
    code = sorted(p.relative_to(PACK).as_posix() for p in PACK.rglob("*")
                  if p.is_file() and p.suffix not in (".yaml", ".yml", ".md"))
    if code:
        problems.append(f"the pack carries non-vocabulary files: {', '.join(code)}")
    else:
        n = len(list(PACK.rglob("*.yaml")))
        print(f"  ok  the pack is {n} YAML file(s) and a README — no code")

    with tempfile.TemporaryDirectory() as tmp:
        proj = Path(tmp) / "adopter"
        proj.mkdir()

        # Exactly what §13.7 tells an adopter to do: copy the drop-in, copy a pack,
        # bring your own documents and one config.
        shutil.copytree(EXAMPLE, proj, dirs_exist_ok=True)
        shutil.copytree(DROPIN, proj / "dropin",
                        ignore=shutil.ignore_patterns("__pycache__", "okfm.json"))
        shutil.copytree(PACK, proj / PACK_REL)
        shutil.copy2(PROJECT / "okfm-web-ui.html", proj / "okfm-web-ui.html")

        if not (proj / PACK_REL).is_dir():
            problems.append(f"okfm.json names `{PACK_REL}` but nothing was copied there")

        # --- builds -------------------------------------------------------
        r = run(proj, "dropin/okfm.py")
        if r.returncode != 0 or "OK — mesh is valid" not in r.stdout:
            problems.append("the pipeline did not reach a valid mesh on a fresh project")
            print(r.stdout[-2500:] or r.stderr[-2000:])
        else:
            counts = [ln.strip() for ln in r.stdout.splitlines()
                      if ln.strip().endswith("concepts across 3 bundles")]
            print(f"  ok  pipeline reaches a valid mesh  ({counts[-1] if counts else 'built'})")

        # --- in-place bundle actually registered --------------------------
        # The mesh check would have caught its absence, but naming it here means a
        # regression reports what broke instead of only that something did.
        member = proj / ".okfm" / "mesh" / "members" / "knowledge.md"
        if not member.is_file():
            problems.append("the in-place `knowledge` bundle got no OKF Member concept")
        elif "authored in place" not in member.read_text(encoding="utf-8"):
            problems.append("the `knowledge` member describes itself as built, not authored")
        else:
            print("  ok  the in-place bundle is registered, not mirrored")

        # --- falsifiable --------------------------------------------------
        cfg = proj / "okfm.json"
        kept = cfg.read_text(encoding="utf-8")
        cfg.write_text(kept.replace(f'"pack": "{PACK_REL}"', '"pack": null'),
                       encoding="utf-8", newline="\n")
        if f'"pack": "{PACK_REL}"' not in kept:
            problems.append("could not find the pack line in okfm.json to remove")

        r2 = run(proj, "dropin/check_bundles.py")
        if r2.returncode == 0:
            problems.append("validation PASSED with no pack — the pack is not doing the "
                            "work, so this example proves nothing")
        elif "predicate `produced_by` not in the vocabulary" not in r2.stdout:
            problems.append("removing the pack failed for some reason other than its "
                            "predicates — the test is not measuring what it claims")
        else:
            bad = len([ln for ln in r2.stdout.splitlines() if "FAIL" in ln or "warn" in ln])
            print(f"  ok  without the pack the same mesh fails ({bad} finding(s), "
                  f"predicates rejected)")
        cfg.write_text(kept, encoding="utf-8", newline="\n")

        # --- no core edits ------------------------------------------------
        drifted = tree_differs(DROPIN, proj / "dropin")
        if drifted:
            problems.append(f"dropin/ differs after standing up the domain: "
                            f"{', '.join(drifted[:6])}")
        else:
            n = len(list(DROPIN.glob("*.py")))
            print(f"  ok  dropin/ byte-identical afterwards ({n} modules untouched)")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — a second domain stands up on pack + config alone"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
