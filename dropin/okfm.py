#!/usr/bin/env python3
"""One entry point for the drop-in build.

    python okfm/okfm.py                 # the whole deterministic pipeline
    python okfm/okfm.py --check         # same, but fail instead of writing (CI)

    python okfm/okfm.py config          # is okfm.json readable, and what is it doing?
    python okfm/okfm.py build [--apply] # markdown -> concepts
    python okfm/okfm.py refresh         # observe pointers, report drift
    python okfm/okfm.py view            # bake the web UI index
    python okfm/okfm.py check           # validate every bundle

Level 3, outside the pipeline because none of it belongs in an unattended run:

    python okfm/okfm.py enrich [--brief]  # what needs enriching, and how
    python okfm/okfm.py enrich-local      # draft it with a model on this machine
    python okfm/okfm.py guard             # did an edit pass write only what it owns?
    python okfm/okfm.py revalidate P --by human:you   # human review clears drift

The default run is `okfm-rebuild` from decisions/0008 with the model step left out: build,
observe, bake, validate. Every step is `needs: []` for local sources -- no network, no
secrets, no model -- so the whole thing is safe on a pull request from a fork.

Enrichment is deliberately absent. It needs a model, which makes any workflow containing it
`needs: [model]` and moves it to Level 3. `enrich-local` runs that model on your own machine
and still needs no key, which changes what it costs you and not which level it is.
"""
import subprocess
import sys
import time
from pathlib import Path

from okfm_core import utf8_stdout

utf8_stdout()

HERE = Path(__file__).resolve().parent

# (name, script, args when running the full pipeline, args in --check mode)
#
# `config` runs first and stops the pipeline on an error. A build that reads a config with a
# misspelled key does not fail — it quietly does something else, and the adopter is left
# comparing what they wrote against what they got.
STEPS = [
    ("config",  "check_config.py",  ["--quiet"], ["--quiet"]),
    ("build",   "build.py",         ["--apply"], []),
    ("refresh", "refresh.py",       [],          ["--check"]),
    ("view",    "bake_web_ui.py",   [],          ["--check"]),
    ("check",   "check_bundles.py", [],          []),
]

# Not in the pipeline, and deliberately so. `enrich` prints work for a person or an agent to
# do; `guard` checks the result afterwards. Neither belongs in an unattended run.
#
# `enrich-local` is the one component here that declares `needs: [model]`. A workflow's set
# is the union of everything it invokes, so listing it in STEPS would take the whole pipeline
# out of CI on a fork's pull request. It stays reachable and stays out of the run.
EXTRA = {"enrich": "enrich.py", "enrich-local": "enrich_local.py",
         "guard": "guard.py", "revalidate": "revalidate.py"}

BY_NAME = {name: script for name, script, *_ in STEPS} | EXTRA


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
    from telemetry import Run

    rec = Run(workflow="okfm-rebuild@1.0" + (" --check" if check else ""),
              trigger="cli")
    width = max(len(n) for n, *_ in STEPS)
    failed = None

    for i, (name, script, apply_args, check_args) in enumerate(STEPS, 1):
        args = check_args if check else apply_args
        print(f"\n{'─' * 62}\n {i}/{len(STEPS)}  {name:<{width}}  "
              f"{script} {' '.join(args)}\n{'─' * 62}")
        t0 = time.monotonic()
        rc = run(script, args)
        rec.step(name, script, args, rc, time.monotonic() - t0)
        if rc != 0:
            # Stop on the first failure. A later step reading what an earlier one failed
            # to write reports a second, misleading problem.
            failed = (name, rc)
            break

    out = rec.write()
    if failed:
        name, rc = failed
        print(f"\n{name} failed (exit {rc}) — stopping", file=sys.stderr)
        if out:
            print(f"run record: {out.relative_to(HERE)}", file=sys.stderr)
        return rc

    print(f"\n{'─' * 62}")
    print(" done" + ("  (check mode — nothing was written)" if check else ""))
    if out:
        print(f" run {rec.id}  →  {out.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
