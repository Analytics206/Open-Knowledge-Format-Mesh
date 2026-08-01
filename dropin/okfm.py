#!/usr/bin/env python3
"""One entry point for the drop-in build.

    python okfm/okfm.py                 # the whole deterministic pipeline
    python okfm/okfm.py --check         # same, but fail instead of writing (CI)

    python okfm/okfm.py build [--apply] # markdown -> concepts
    python okfm/okfm.py refresh         # observe pointers, report drift
    python okfm/okfm.py view            # bake the viewer index
    python okfm/okfm.py check           # validate every bundle

The default run is `okfm-rebuild` from decisions/0008 with the model step left out: build,
observe, bake, validate. Every step is `needs: []` for local sources -- no network, no
secrets, no model -- so the whole thing is safe on a pull request from a fork.

Enrichment is deliberately absent. It needs a model, which makes any workflow containing it
`needs: [model]` and moves it to Level 3.
"""
import subprocess
import sys
from pathlib import Path

from okfm_core import utf8_stdout

utf8_stdout()

HERE = Path(__file__).resolve().parent

# (name, script, args when running the full pipeline, args in --check mode)
STEPS = [
    ("build",   "build.py",         ["--apply"], []),
    ("refresh", "refresh.py",       [],          ["--check"]),
    ("view",    "bake_viewer.py",   [],          ["--check"]),
    ("check",   "check_bundles.py", [],          []),
]
BY_NAME = {name: script for name, script, *_ in STEPS}


def run(script: str, args: list[str]) -> int:
    return subprocess.run([sys.executable, str(HERE / script), *args]).returncode


def main(argv: list[str]) -> int:
    check = "--check" in argv
    rest = [a for a in argv if a != "--check"]
    cmd = rest[0] if rest and not rest[0].startswith("-") else None

    if cmd in ("-h", "--help", "help"):
        print(__doc__)
        return 0

    if cmd:
        if cmd not in BY_NAME:
            print(f"unknown command: {cmd}\n", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            return 2
        return run(BY_NAME[cmd], rest[1:] + (["--check"] if check else []))

    # ---- full pipeline ----------------------------------------------------
    width = max(len(n) for n, *_ in STEPS)
    for i, (name, script, apply_args, check_args) in enumerate(STEPS, 1):
        args = check_args if check else apply_args
        print(f"\n{'─' * 62}\n {i}/{len(STEPS)}  {name:<{width}}  "
              f"{script} {' '.join(args)}\n{'─' * 62}")
        rc = run(script, args)
        if rc != 0:
            # Stop on the first failure. A later step reading what an earlier one failed
            # to write reports a second, misleading problem.
            print(f"\n{name} failed (exit {rc}) — stopping", file=sys.stderr)
            return rc

    print(f"\n{'─' * 62}")
    print(" done" + ("  (check mode — nothing was written)" if check else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
