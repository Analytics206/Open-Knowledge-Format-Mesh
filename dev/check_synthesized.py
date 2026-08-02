#!/usr/bin/env python3
"""The config the build writes for a new adopter must pass the validator the build runs.

    python dev/check_synthesized.py

## Why this exists

It did not, and the gap was invisible in exactly the way that costs most.

`okfm_core.synthesize_config()` writes `okfm.json` on a first run, so the first thing an
adopter edits is a file the tool made for them. `check_config.py` validates `okfm.json` as step
one of the pipeline. Nothing compared the two, and they disagreed: the generator emitted
`read.web_ui.path: "../okfm-web-ui.html"` while the schema declares that key relative to the
project and rejects `..`.

**The failure could not happen on the first run.** No config exists yet, so step one passes
trivially, step two writes the bad file, and the run succeeds. It failed on the *second* run,
for every adopter, on a line they did not write — after they already believed the tool worked.
"It worked, then it broke" is the worst available framing for someone deciding whether to keep
going, and it was reached by a config the tool authored itself.

Fixing the string was a minute's work. This file is the part that matters: the two halves are
now compared on every CI run, so a default that the validator would reject cannot ship again.

Project-local, like the other checks in here — it tests this repository's code, not an
adopter's data.

`needs: []` — no network, no secrets, no model.
"""
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "dropin"))

import config_schema                                    # noqa: E402
from okfm_core import synthesize_config                 # noqa: E402


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    utf8_stdout()
    cfg = synthesize_config(PROJECT)

    # Without a project path, so the disk checks are skipped. A synthesised config names
    # paths that do not exist yet by design — `docs/` may be the only one that does — and
    # failing on that would be testing the fixture rather than the defaults. What must hold
    # is everything structural: unknown keys, types, enums, ranges, shapes, cross-checks.
    findings = config_schema.validate(cfg)
    errors = [f for f in findings if f["level"] == "error"]

    for f in findings:
        mark = "FAIL" if f["level"] == "error" else "warn"
        print(f"  {mark:>4}  {f['path']}")
        print(f"        {f['msg']}")
        if f.get("hint"):
            print(f"        → {f['hint']}")

    # Every field the schema says must be present has to survive into the written file. A
    # generator that omits a required key produces a config that fails on the adopter's
    # second run for a reason they cannot see in anything they did.
    missing = [f["path"] for f in config_schema.FIELDS
               if f.get("required") and not config_schema.dig(cfg, f["path"])[1]]
    for path in missing:
        print(f"  FAIL  {path}\n        required by the schema, absent from the "
              f"synthesised config")

    total = len(errors) + len(missing)
    print()
    if total:
        print(f"{total} problem(s) — the build would write a config its own validator "
              f"rejects.", file=sys.stderr)
        return 1
    print(f"OK — the synthesised config passes the validator "
          f"({len(findings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
