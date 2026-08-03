#!/usr/bin/env python3
"""`okfm.schema.json` must be what the rule table says, and must know the same keys.

    python dev/check_schema.py

## Why a third validator, and why it is generated

`okfm.json` is now validated in three places: `check_config.py` in the terminal, the config
panel in the web UI, and — with this file on disk and a `$schema` line in the config — the
adopter's editor, as they type. That is the earliest of the three by a wide margin. A
misspelled key caught before the file is saved never becomes a build that quietly does the
wrong thing.

Three validators is two more than the number of places the rules may live. So the schema is
**generated** from `config_schema.FIELDS`, and this file fails when the committed copy and
that table disagree. Hand-writing it would have made a fourth copy of the key list, and a
fourth copy is precisely how a UI comes to accept a config the build rejects.

## What it checks

  regenerates   the committed file is byte-identical to what the table produces now
  same keys     every path the terminal validator knows is in the schema, and the reverse
  accepts ours  this repository's own config satisfies the schema

The middle one is the check that matters. Byte-identity catches a stale file; agreeing key
sets catches the thing that actually goes wrong, which is a field added to the table in a
shape the emitter does not translate.

The third uses a small structural validator rather than a library, because `dropin/` is
standard-library-only under DR-0001 and adding a dependency to check a config would trade the
zero-install property for a convenience. It covers exactly the constructs the emitter emits —
types, enums, required keys, unknown keys — and nothing else, which is honest: it validates
what we generate rather than claiming general JSON Schema conformance.

`needs: []`.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DROPIN = PROJECT / "dropin"
sys.path.insert(0, str(DROPIN))

import config_schema  # noqa: E402

SCHEMA_FILE = DROPIN / "okfm.schema.json"


def schema_paths(node: dict, prefix: str = "") -> set[str]:
    """Every dotted key the schema declares, ignoring open-ended objects."""
    out = set()
    for name, child in (node.get("properties") or {}).items():
        if name.startswith("$"):
            continue
        path = f"{prefix}{name}"
        out.add(path)
        if isinstance(child, dict) and child.get("properties"):
            out |= schema_paths(child, path + ".")
    return out


def validate(value, node: dict, path: str, out: list[str]) -> None:
    """The subset the emitter emits. Not a general JSON Schema implementation."""
    types = node.get("type")
    if types:
        allowed = types if isinstance(types, list) else [types]
        actual = ("null" if value is None else
                  "boolean" if isinstance(value, bool) else
                  "integer" if isinstance(value, int) else
                  "array" if isinstance(value, list) else
                  "object" if isinstance(value, dict) else "string")
        if actual not in allowed:
            out.append(f"{path or '(root)'}: is {actual}, schema says {'/'.join(allowed)}")
            return
    if "enum" in node and value not in node["enum"]:
        out.append(f"{path}: `{value}` is not one of {', '.join(map(str, node['enum']))}")
    if isinstance(value, dict) and node.get("properties") is not None:
        known = node["properties"]
        for key, sub in value.items():
            if key.startswith("_") or key.startswith("$"):
                continue
            if key in known:
                validate(sub, known[key], f"{path}.{key}" if path else key, out)
            elif node.get("additionalProperties") is False:
                out.append(f"{path}.{key}" if path else key + ": not a key the schema knows")
    for name in node.get("required", []):
        if isinstance(value, dict) and name not in value:
            out.append(f"{path}.{name}" if path else f"{name}: required, and missing")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []
    fresh = config_schema.schema_text()

    # Regeneration lives HERE rather than in a shell redirect, and the reason is not style.
    # `python … --json-schema > file` on Windows writes CRLF through stdout while the
    # generator produces LF, so the file was stale the instant it was created and the check
    # said so with an instruction that could not fix it — the same shape of defect as the
    # stale-viewer message that named the wrong remedy.
    if "--write" in sys.argv:
        SCHEMA_FILE.write_text(fresh, encoding="utf-8", newline="\n")
        print(f"wrote {SCHEMA_FILE.relative_to(PROJECT).as_posix()}")
        return 0

    # --- regenerates ------------------------------------------------------
    if not SCHEMA_FILE.is_file():
        problems.append(f"{SCHEMA_FILE.relative_to(PROJECT)} does not exist — generate it "
                        f"with `python dev/check_schema.py --write`")
        committed = None
    else:
        committed = SCHEMA_FILE.read_text(encoding="utf-8")
        if committed != fresh:
            problems.append(f"{SCHEMA_FILE.relative_to(PROJECT)} is stale — the rule table "
                            f"has changed since it was generated. Regenerate it with "
                            f"`python dev/check_schema.py --write`")
        else:
            print(f"  ok  {SCHEMA_FILE.relative_to(PROJECT).as_posix()} matches the table")

    schema = json.loads(fresh)

    # --- same keys --------------------------------------------------------
    # `stores` and `federation.*` hold adopter-named keys, so the table declares the group
    # and not its contents; the schema leaves them open for the same reason.
    table = {f["path"] for f in config_schema.FIELDS}
    # A dotted path implies its parents — `read.web_ui.path` means `read` and `read.web_ui`
    # are both real keys, and the schema declares them as objects.
    for p in list(table):
        parts = p.split(".")
        for i in range(1, len(parts)):
            table.add(".".join(parts[:i]))

    declared = schema_paths(schema)
    missing = sorted(table - declared)
    extra = sorted(declared - table)
    if missing:
        problems.append(f"in the table and not the schema: {', '.join(missing)} — the "
                        f"emitter does not translate that field's shape")
    if extra:
        problems.append(f"in the schema and not the table: {', '.join(extra)}")
    if not missing and not extra:
        print(f"  ok  the same {len(table)} key(s) in both, including nested groups")

    # --- accepts ours -----------------------------------------------------
    cfg = json.loads((PROJECT / "okfm.json").read_text(encoding="utf-8"))
    failures: list[str] = []
    validate(cfg, schema, "", failures)
    if failures:
        problems.extend(f"this repository's own okfm.json fails the schema — {f}"
                        for f in failures)
    else:
        print(f"  ok  this repository's okfm.json satisfies it")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — the schema is the table, and the table is what the build reads"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
