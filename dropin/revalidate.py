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
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from okfm_core import (PROJECT, frontmatter, reject_unknown, scalar, source_entries,
                       utf8_stdout)
# The same function `refresh.py` observes with, deliberately. If the re-pinner and the
# observer computed a hash differently by so much as a line ending, re-validation would
# write a value the next observation disagrees with, and drift would never clear.
from refresh import observe_file as observe

utf8_stdout()

# Entries come from `okfm_core.source_entries`, which is also what `refresh` observes with and
# `bake_web_ui` renders from. There were three parsers for this; `refresh`'s saw only the first
# entry of each concept, so this command was faithfully repinning captures that nothing ever
# read. Each entry is rewritten inside its own line span, so a concept that pins several
# sources cannot have one entry's hash written into another's.
#
# It did that once. This rewrote every `okfm_captured` in a concept to a single value — the
# hash of the concept file itself — which is right only for an in-place concept, where the file
# IS its source. For a mirrored concept it pinned the wrong file, and pinned the same wrong file
# twice. Two different files cannot share a hash, so those pointers reported drift forever and
# carried no signal at all. `check_bundles.py` now fails on the impossible state.
#
# `\.*` tolerates the trailing ellipsis on hashes written before full digests were stored.
# They compare as prefixes; they rewrite as whole values.
_HASH = re.compile(r'(hash:\s*"?)sha256:[0-9a-f]+\.*')
_AT = re.compile(r"(at:\s*)\d{4}-\d{2}-\d{2}")


def main() -> int:
    argv = sys.argv[1:]
    reject_unknown(argv, ("--by", "--stable"), __doc__)
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

    stamp = datetime.now(timezone.utc)
    now = stamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    today = stamp.strftime("%Y-%m-%d")
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

        # Each source gets the hash of the file IT points at, and today's date.
        #
        # `okfm_captured.at` is *when this hash was observed*. Rewriting the hash and leaving
        # the date is a capture that says it is older than it is, which is the kind of small
        # lie that makes the whole field untrustworthy.
        missing, lines, n = [], block.splitlines(), 0
        for entry in reversed(source_entries(block)):
            # Reversed, so splicing one entry never moves the span of one not yet rewritten.
            if not entry["resource"] or not entry["hash"]:
                continue
            target = (p.parent / entry["resource"]).resolve()
            if not target.is_file():
                missing.append(entry["resource"])
                continue
            # In-place concepts hash the body, matching how refresh observes them: the
            # capture was taken before frontmatter existed, so comparing whole files would
            # report drift forever.
            sha = observe(target, body_only=(target == p.resolve()))
            fresh = _AT.sub(rf"\g<1>{today}", _HASH.sub(rf'\g<1>sha256:{sha}', entry["raw"]))
            lines[entry["start"]:entry["end"]] = fresh.splitlines()
            n += 1

        if n == 0 and not missing:
            print(f"  skip  {raw} — no okfm_captured to refresh")
            continue
        if missing:
            print(f"  skip  {raw} — cannot read {', '.join(missing)}", file=sys.stderr)
            continue
        new_block = "\n".join(lines)

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
