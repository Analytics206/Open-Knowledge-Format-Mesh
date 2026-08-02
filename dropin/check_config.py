#!/usr/bin/env python3
"""Validate `okfm.json` before anything reads it.

    python okfm/okfm.py config            # what is wrong, and where
    python okfm/okfm.py config --check    # same; identical exit codes (CI)
    python okfm/okfm.py config --strict   # warnings fail too

Exit 1 on an error, 0 otherwise, so the pipeline stops before building the wrong thing.

The rules live in `config_schema.py` and are shared with the web UI's config panel. This
file is the terminal half: it adds the checks that need a filesystem — does `build.root`
exist, does a named bundle, is a vocabulary overlay actually there.

Why this exists: every consumer of a config ignores keys it does not recognise, so a
misspelled `exlude` does not fail. It builds the wrong thing, quietly, and the adopter is
left comparing what they wrote against what they got. A validator turns that into a line of
output.

`needs: []` — no network, no secrets, no model.
"""
import json
import sys

from config_schema import BY_PATH, FIELDS, dig, validate
from okfm_core import PROJECT, find_config, utf8_stdout

utf8_stdout()

MARK = {"error": "FAIL", "warn": "warn"}


def defaults_in_use(cfg: dict) -> list[tuple[str, object]]:
    """Fields nobody set. Printed because the commonest config question is not "what is
    wrong" but "what is it actually doing", and an unset key is doing something."""
    out = []
    for field in FIELDS:
        _, present = dig(cfg, field["path"])
        if not present and field.get("default") not in (None, [], {}):
            out.append((field["path"], field["default"]))
    return out


def main() -> int:
    argv = sys.argv[1:]
    strict = "--strict" in argv
    quiet = "--quiet" in argv

    path, cfg = find_config()
    if path is None:
        print("no okfm.json — the first build writes one for you", file=sys.stderr)
        return 0

    raw = json.loads(path.read_text(encoding="utf-8"))
    findings = validate(raw, PROJECT)
    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]

    print(f"config  : {path}")
    print(f"fields  : {len(FIELDS)} known, {len(BY_PATH)} paths\n")

    for f in findings:
        print(f"  {MARK[f['level']]:>4}  {f['path']}")
        print(f"        {f['msg']}")
        if f.get("hint"):
            print(f"        → {f['hint']}")

    if findings:
        print()

    if not quiet:
        unset = defaults_in_use(raw)
        if unset:
            print("Using defaults for:")
            for key, value in unset:
                print(f"  {key:<28} {json.dumps(value)}")
            print()

    if errors:
        print(f"{len(errors)} error(s), {len(warns)} warning(s) — the build would read a "
              f"config that does not say what you think it says.", file=sys.stderr)
        return 1
    if warns and strict:
        print(f"{len(warns)} warning(s), and --strict", file=sys.stderr)
        return 1
    print(f"OK — config is readable" + (f" ({len(warns)} warning(s))" if warns else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
