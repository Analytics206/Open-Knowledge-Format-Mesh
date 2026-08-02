#!/usr/bin/env python3
"""Check that every component sits at a level its exposure actually allows.

    python dev/check_levels.py

## This is a project-local check, and the data it reads is project-local too

The adoption levels are OKFM's own documentation ladder. They are not part of the format,
they are not something an adopter inherits, and nothing about them belongs in the OKFM
profile — a bundle describing somebody's warehouse should not carry a field about how OKFM's
own guide is organised.

So there is no `okfm_level` and no `okfm_needs`. A concept's level is the level of the
bundle it sits in, which `LEVELS` below records. Its exposure is an ordinary `tag` —
`needs-nothing`, `needs-human`, `needs-model`, `needs-secrets` — using an official OKF field
that every consumer already understands and no profile has to define.

That is the whole reason this file exists rather than a spec section: a project-specific rule
enforced by a project-specific script, reading data that costs an adopter nothing.

## The rule

Exposure comes from decisions/0008 — `[] < human < model < secrets` — and each level admits
a prefix of it:

    level 1   nothing.          A download. No component runs at all.
    level 2   + human.          Deterministic; a person may have to decide something.
    level 3   + model, secrets. Something has to reason, and its credentialed variant is
                                where OKFM holds the key rather than your agent.

A component's exposure is a **floor**, not an equality. `guard.py` needs nothing mechanically
and still belongs to level 3, because there is nothing to guard until something has drafted.
So the rule is `needs ⊆ allowed(level)`, which catches the failure that matters — a level 2
component that quietly acquired a model dependency — without forcing every deterministic tool
down to level 2.

`needs: []` — no network, no secrets, no model.
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
TAGS = re.compile(r"^tags:[ \t]*\[(.*?)\][ \t]*$", re.M)

# Which bundle is which level. Project-local, so it lives here and not in okfm.json —
# an adopter's config has no business carrying OKFM's documentation structure.
LEVELS = {"level-1-view": 1, "level-2-build": 2, "level-3-enrich": 3}

LADDER = ["nothing", "human", "model", "secrets"]
ALLOWED = {1: set(), 2: {"human"}, 3: {"human", "model", "secrets"}}


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def needs_of(block: str) -> set[str] | None:
    """Exposure read from tags. None when the concept declares none."""
    m = TAGS.search(block)
    if not m:
        return None
    found = {t.strip()[6:] for t in m.group(1).split(",")
             if t.strip().startswith("needs-")}
    return found or None


def main() -> int:
    utf8_stdout()
    cfg = json.loads((PROJECT / "okfm.json").read_text(encoding="utf-8"))
    bundles = cfg.get("bundles", {})

    errors, notes = [], []
    checked = 0

    for bid, level in sorted(LEVELS.items(), key=lambda kv: kv[1]):
        if bid not in bundles:
            errors.append(f"{bid}: no such bundle in okfm.json")
            continue
        # removeprefix, not lstrip -- lstrip takes a character SET, so "./.okfm/level-1-view"
        # would lose its dot-folder and silently resolve somewhere else.
        path = (PROJECT / bundles[bid].removeprefix("./")).resolve()
        if not path.is_dir():
            errors.append(f"{bid}: configured path does not exist ({path})")
            continue

        declared, seen = None, set()
        for f in sorted(path.rglob("*.md")):
            m = FM.match(f.read_text(encoding="utf-8"))
            if not m:
                continue
            block = m.group(1)
            rid = f"{bid}/{f.relative_to(path).as_posix()}"
            checked += 1

            n = needs_of(block)
            if n is None:
                if f.name != "log.md":
                    errors.append(f"{rid}: no `needs-*` tag — the level boundary is made of "
                                  f"this, so an absent one is an unchecked claim")
                continue

            unknown = n - set(LADDER)
            if unknown:
                errors.append(f"{rid}: unknown exposure {sorted(unknown)} — the ladder is "
                              f"{LADDER}")
            real = n - {"nothing"}
            over = real - ALLOWED[level] - unknown
            if over:
                errors.append(f"{rid}: needs {sorted(over)}, which level {level} does not "
                              f"allow (level {level} admits "
                              f"{sorted(ALLOWED[level]) or 'nothing'})")

            if f.name == "index.md":
                declared = real
            else:
                seen |= real

        if declared is not None and declared - seen:
            # Not an error. A level whose index declares an exposure no component has yet is
            # designed and unbuilt, which is legitimate as long as the bundle says so.
            notes.append(f"{bid}: index declares {sorted(declared - seen)}, which no component "
                         f"needs yet — unbuilt, or the index is ahead of itself")

        print(f"  level {level}  {bid}")

    print(f"\n{checked} concepts across {len(LEVELS)} level bundles")
    for n in notes:
        print(f"  note  {n}")
    for e in errors:
        print(f"  FAIL  {e}")
    print()
    print("OK — every component fits its level" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
