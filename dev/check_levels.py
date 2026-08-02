#!/usr/bin/env python3
"""Check that every component sits at a level its needs actually allow.

    python dev/check_levels.py

The three adoption levels are only meaningful if they are made of something checkable. They
are: each component concept carries `okfm_needs`, drawn from the exposure ladder in
decisions/0008 — `[]` < `human` < `model` < `secrets` — and each level admits a prefix of it.

    level 1   nothing.        A download. No component runs at all.
    level 2   + human.        Deterministic; a person may have to decide something.
    level 3   + model, secrets. Something in the workflow has to reason.

Level 3 admits `secrets` because its credentialed variant is where OKFM drives a provider
rather than an agent driving OKFM. That was a fourth level for a while and collapsed: the
ladder asks for a browser, then Python, then a model, and there is nothing further to ask
for. Who holds the key is a change of direction, not another step up — and `okfm_needs`
records it either way, which is where the distinction actually does work.

A component's needs set is a **floor**, not an equality. `guard.py` needs nothing
mechanically and still belongs to level 3, because there is nothing to guard until something
has drafted. So the rule is `needs ⊆ allowed(level)`, which catches the failure that matters —
a level 2 component that quietly acquired a model dependency — without forcing every
deterministic tool down to level 2.

This is project-specific: an adopter's mesh has no levels. That is why it lives in dev/ rather
than in the drop-in.

`needs: []` — no network, no secrets, no model.
"""
import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
NEEDS = re.compile(r"^okfm_needs:[ \t]*(\[.*?\]|\n(?:[ \t]*-.*\n?)+)", re.M)

LADDER = ["human", "model", "secrets"]
ALLOWED = {1: set(), 2: {"human"}, 3: {"human", "model", "secrets"}}


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def scalar(block: str, key: str):
    m = re.search(rf"^{key}:[ \t]*(.*)$", block, re.M)
    return m.group(1).strip().strip("\"'") if m else None


def needs_of(block: str) -> set[str] | None:
    """The declared needs set, or None if the concept does not declare one."""
    m = NEEDS.search(block)
    if not m:
        return None
    raw = m.group(1)
    if raw.strip().startswith("["):
        return set(re.findall(r"[\w]+", raw))
    return set(re.findall(r"^\s*-\s*([\w]+)", raw, re.M))


def main() -> int:
    utf8_stdout()
    cfg = json.loads((PROJECT / "okfm.json").read_text(encoding="utf-8"))
    levels = {k: int(v) for k, v in cfg.get("levels", {}).items()}
    bundles = cfg.get("bundles", {})
    if not levels:
        print("no `levels` in okfm.json — nothing to check")
        return 0

    errors, notes = [], []
    checked = 0

    for bid, level in sorted(levels.items(), key=lambda kv: kv[1]):
        # removeprefix, not lstrip -- lstrip takes a character SET, so "./.okfm/level-1"
        # loses its dot-folder and silently resolves to "okfm/level-1".
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

            claimed = scalar(block, "okfm_level")
            if claimed is None:
                errors.append(f"{rid}: no `okfm_level` — a concept in a level bundle has to "
                              f"say which level it claims")
            elif int(claimed) != level:
                errors.append(f"{rid}: claims level {claimed}, but sits in {bid} (level {level})")

            n = needs_of(block)
            if n is None:
                if f.name != "log.md":
                    errors.append(f"{rid}: no `okfm_needs` — the level boundary is made of "
                                  f"this field, so an absent one is an unchecked claim")
                continue

            unknown = n - set(LADDER)
            if unknown:
                errors.append(f"{rid}: unknown need(s) {sorted(unknown)} — the ladder is "
                              f"{LADDER}")
            over = n - ALLOWED[level] - unknown
            if over:
                errors.append(f"{rid}: needs {sorted(over)}, which level {level} does not "
                              f"allow (level {level} admits {sorted(ALLOWED[level]) or 'nothing'})")

            if f.name == "index.md":
                declared = n
            else:
                seen |= n

        if declared is not None and declared - seen:
            # Not an error. A level whose index declares a need no component has yet is a
            # level that is designed and unbuilt, which is a legitimate state as long as the
            # bundle says so out loud.
            notes.append(f"{bid}: index declares {sorted(declared - seen)}, which no component "
                         f"needs yet — unbuilt, or the index is ahead of itself")

        print(f"  level {level}  {bid}")

    print(f"\n{checked} concepts across {len(levels)} level bundles")
    for n in notes:
        print(f"  note  {n}")
    for e in errors:
        print(f"  FAIL  {e}")
    print()
    print("OK — every component fits its level" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
