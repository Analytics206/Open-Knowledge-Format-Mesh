#!/usr/bin/env python3
"""Re-validate a reviewed concept — the human end of the review queue.

    python okfm/okfm.py revalidate <path> --by human:you
    python okfm/okfm.py revalidate <path> --by human:you --stable

Refreshes `okfm_captured` to what the source says now, and adds a `verified` entry. That
is the act that clears drift, and it is the one thing the build must never do for you:
refreshing a capture automatically would erase the signal drift exists to carry (DR-0006).

`needs: [human]` under DR-0008 — the mechanics are arithmetic, but the *decision* that a
concept still says what it should is a person's, and this tool cannot make it. Naming a
path and an actor is how you assert you made it.

## Why this exists

§8.4 gives the review queue three exits: re-validate, supersede, or acknowledge. Without a
tool for the first, drift accumulates and the queue never drains — which turns a signal
into noise, and a noisy signal gets ignored.

This is the exit. Supersede is `status: deprecated` plus a `supersedes` relation;
acknowledge is a `stale_after` further out. Both are edits, not commands.
"""
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from okfm_core import PROJECT, frontmatter, scalar, utf8_stdout

utf8_stdout()

# `\.*` tolerates the trailing ellipsis on hashes written before full digests were
# stored. They compare as prefixes; they rewrite as whole values.
_CAPTURED = re.compile(r'(okfm_captured:\s*\{\s*hash:\s*")sha256:[0-9a-f]+\.*(")')


def main() -> int:
    argv = sys.argv[1:]
    by, promote, paths, skip = None, False, [], False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a.startswith("--by="):
            by = a.split("=", 1)[1]
        elif a == "--by":
            by = argv[i + 1] if i + 1 < len(argv) else None
            skip = True                    # the actor is a value, not a path
        elif a == "--stable":
            promote = True
        elif not a.startswith("--"):
            paths.append(a)

    if not paths or not by:
        print(__doc__)
        print("error: a path and --by are both required", file=sys.stderr)
        return 2
    if not by.startswith(("human:", "process:")):
        print(f"error: --by must be an actor like `human:you` (got {by!r})", file=sys.stderr)
        return 2
    if not by.startswith("human:"):
        # The whole point of this command is a person asserting review. A process actor
        # here would be the backfill dishonesty §16 forbids, wearing a command's clothes.
        print("error: re-validation is a human act — --by must be `human:<id>`",
              file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    changed = 0

    for raw in paths:
        p = (PROJECT / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if not p.is_file():
            print(f"  skip  {raw} — not found")
            continue
        block, body = frontmatter(p)
        if not block or not scalar(block, "type"):
            print(f"  skip  {raw} — not a concept")
            continue

        text = p.read_text(encoding="utf-8")
        # In-place concepts hash the body, matching how refresh observes them.
        sha = hashlib.sha256((body if body is not None else text).encode("utf-8")).hexdigest()

        new_block, n = _CAPTURED.subn(rf"\g<1>sha256:{sha}\g<2>", block)
        if n == 0:
            print(f"  skip  {raw} — no okfm_captured to refresh")
            continue

        entry = f'verified: {{ by: "{by}", at: {now} }}'
        if re.search(r"^verified:", new_block, re.M):
            new_block = re.sub(r"^verified: .*$", entry, new_block, count=1, flags=re.M)
        else:
            new_block = re.sub(r"^(status: .*)$", rf"\1\n{entry}", new_block, count=1, flags=re.M)

        if promote:
            new_block = re.sub(r"^status: draft$", "status: stable", new_block,
                               count=1, flags=re.M)

        p.write_text(f"---\n{new_block}\n---\n{body}", encoding="utf-8", newline="\n")
        print(f"  revalidated  {raw}"
              + ("  → stable" if promote else "  (still draft)"))
        changed += 1

    if changed:
        print(f"\n{changed} concept(s) re-validated by {by}")
        print("Re-run `okfm.py refresh` to see them leave the queue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
