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

from build import MINE                     # the actor the build stamps on what it writes
from config_schema import BY_PATH, FIELDS, dig, validate
from okfm_core import (PROJECT, bundle_root, configured_bundles, find_config, frontmatter,
                       reject_unknown, resolve_sources, scalar, utf8_stdout)

utf8_stdout()

MARK = {"error": "FAIL", "warn": "warn"}


def _is_build_output(path) -> bool:
    """Did THIS build write the concepts in here?

    `.okfm/` holds two kinds of bundle: ones the build mirrors from documents, and ones a
    person wrote by hand — the guide is the second kind and always has been. Judging by
    location alone would call the guide orphaned output on every correct config, so judge by
    the same `generated.by` stamp `build.py` uses to decide what it may overwrite.
    """
    for f in path.rglob("*.md"):
        block, _ = frontmatter(f)
        if block and MINE in (scalar(block, "generated") or ""):
            return True
    return False


def orphaned_bundles(cfg: dict) -> list[dict]:
    """Bundles in the output folder that this build no longer produces.

    Turning off `root_files`, or adding to `exclude`, stops the build WRITING a bundle. It
    does not delete what a previous run already wrote, and it does not touch `bundles` — so
    the folder sits there, stays listed, and keeps showing up in the web UI looking like the
    setting did nothing.

    Needs the build's own view of what it would write, which is why it lives here and not in
    the shared rule table: a browser cannot answer it.
    """
    bundles = configured_bundles(cfg)
    if "bundles" not in cfg or not bundles:
        return []
    out_root = bundle_root(cfg)
    produced = {s["bundle"] for s in resolve_sources(cfg)} | {cfg.get("mesh", "mesh")}

    findings = []
    for bid, path in bundles.items():
        # Only this build's own output. An in-place bundle living with its sources is not
        # this build's to produce, and neither is a hand-authored one that happens to sit
        # under the output folder — saying so would be noise on every correct config.
        if not path.resolve().is_relative_to(out_root) or bid in produced:
            continue
        if not _is_build_output(path):
            continue
        findings.append({
            "level": "warn", "path": f"bundles.{bid}",
            "msg": "this build no longer writes it, but it is still listed and still on disk "
                   "— so every reader still shows it",
            "hint": f"the build stopped producing `{bid}` (check `build.exclude` and "
                    f"`build.root_files`). Remove the `bundles.{bid}` line and delete "
                    f"{path.relative_to(PROJECT)}, or put back the setting that built it.",
        })
    return findings


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
    reject_unknown(argv, ("--strict", "--quiet"), __doc__)
    strict = "--strict" in argv
    quiet = "--quiet" in argv

    path, cfg = find_config()
    if path is None:
        print("no okfm.json — the first build writes one for you", file=sys.stderr)
        return 0

    raw = json.loads(path.read_text(encoding="utf-8"))
    findings = validate(raw, PROJECT) + orphaned_bundles(cfg)
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
