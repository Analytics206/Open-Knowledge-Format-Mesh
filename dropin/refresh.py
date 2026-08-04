#!/usr/bin/env python3
"""Observe pointers and report drift — DR-0006.

    python okfm/refresh.py            # observe, write the cache, report
    python okfm/refresh.py --check    # exit 1 if a `stable` concept has a drifted source

Drift is **observed here and nowhere else.** Nothing on the read path — not the web UI, not
an injected index, not an agent — resolves a pointer. That is what keeps reading a mesh free
and what stops an agent paying a database round trip before it has done anything.

Three states, never two:

    match      the source hashes to what `okfm_captured` recorded
    drifted    it does not
    unknown    the pointer needs a credential this tier does not have, resolves to nothing,
               or is pinned to no hash at all — the normal shape of a hand-written concept

`unknown` renders as unknown. Defaulting it to `match` would be a stored opinion wearing a
computed one's clothes, which is the failure spec 3.4 exists to prevent.

**Every pointer in a concept is observed, not the first one.** That reads as too obvious to
state, and it is here because it was not true: the entry regex treated any indented line as a
continuation, so the first `- id:` swallowed the ones after it and only its resource was ever
read. In this repository that left **17 of 59 pointers invisible**, and the invisible one was
systematically the second — the implementation file a concept documents, which is the pointer
whose drift matters most. `okfm_core.source_entries` is now the one parser; `revalidate` and
`bake_web_ui` had their own, both correct and both different, so `revalidate` was maintaining
pins that nothing here ever read.

**`max_age` does not govern a local file.** [DR-0006](../docs/decisions/0006-drift-cost-and-caching.md)
sized it for resolvers that cost a network or database round trip, and hashing a file on disk
costs microseconds — so a `file` pointer is re-read every run and is never *stale*, only
*current*. It was being printed beside the cache path as though it were the rule the cache
follows, which is a report of a policy that was not in force.

**The cache stores observations, not verdicts.** *This pointer hashed to X at time T* does
not become false later — it is the same kind of fact as `okfm_captured`, which the format
already stores. The verdict is still derived, here, from the two of them. Observations for
pointers the mesh no longer holds are dropped, because the viewer bakes its drift state out
of this file and a record nobody is asking about is not evidence of anything.

`needs: []` for `file://` and relative paths. Live schemes (`sys://`, `store://`, `okf://`)
need credentials and are `needs: [secrets]`; they are not implemented yet and report
`unknown` rather than guessing.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from okfm_core import (HERE, PROJECT, configured_bundles, frontmatter,
                       load_or_create_config, reject_unknown, scalar, source_entries)

CACHE = HERE / ".okfm-cache" / "observations.json"

# Schemes this tier can resolve. Everything else needs a credential.
LIVE_SCHEMES = ("sys://", "store://", "okf://", "http://", "https://")

_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def parse_age(s: str) -> int:
    m = re.fullmatch(r"(\d+)([smhd])", str(s).strip())
    return int(m.group(1)) * _UNITS[m.group(2)] if m else 3600


def load_cache() -> dict:
    if CACHE.is_file():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}                      # a corrupt cache is a rebuildable one
    return {}


def save_cache(cache: dict) -> None:
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n",
                     encoding="utf-8", newline="\n")


def observe_file(path: Path, body_only: bool = False) -> str | None:
    """sha256 of the TEXT, matching how okfm_captured was computed — see .gitattributes.

    `body_only` handles the in-place case, where the concept and its source are the same
    file. The hash was taken before frontmatter was added, so hashing the whole file
    compares the concept against itself-plus-its-own-metadata and can never match — every
    in-place concept would report drift forever, which is a broken signal rather than a
    loud one.

    Hashing the body instead gives drift a useful meaning here: *the prose changed since
    the description was extracted*, which is exactly the enrichment work list.
    """
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    if body_only:
        _, body = frontmatter(path)
        if body is not None:
            text = body
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    reject_unknown(sys.argv[1:], ("--check",), __doc__)
    check = "--check" in sys.argv
    _, cfg, _ = load_or_create_config(write=False)

    now = datetime.now(timezone.utc)
    cache = load_cache()
    counts = {"match": 0, "drifted": 0, "unknown": 0}
    drifted, unresolvable, unpinned = [], [], []
    # Every pointer the mesh holds right now, observed or not. Used to prune the cache, which
    # otherwise only ever grew: a deleted concept's observations stayed in it forever.
    live_keys: set[str] = set()

    for bid, root in sorted(configured_bundles(cfg).items()):
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            block, _ = frontmatter(f)
            if not block or not scalar(block, "type"):
                continue
            status = scalar(block, "status") or "stable"
            rid = f"{bid}/{f.relative_to(root).as_posix()}"

            for entry in source_entries(block):
                uri, captured = entry["resource"], entry["hash"]
                if not uri:
                    continue               # not a source pointer at all
                live_keys.add(f"{uri}@{rid}")
                if not captured:
                    # A pointer with no captured hash is `unknown`, not nothing. It used to be
                    # skipped entirely — counted in no bucket, invisible in the totals — which
                    # contradicted this file's own promise of three states and no defaulting.
                    #
                    # It is the normal shape of a hand-authored concept: level 1 runs nothing,
                    # so an author cannot compute a sha256, and a fabricated one would report
                    # drift forever. Their bundle reported zero pointers and looked empty.
                    counts["unknown"] += 1
                    unpinned.append(f"{rid} → {uri}")
                    continue

                if uri.startswith(LIVE_SCHEMES):
                    counts["unknown"] += 1
                    unresolvable.append(f"{rid} → {uri}")
                    continue

                target = (f.parent / uri).resolve() if not uri.startswith("/") \
                    else (root / uri.lstrip("/")).resolve()
                observed = observe_file(target, body_only=(target == f.resolve()))
                if observed is None:
                    counts["unknown"] += 1
                    unresolvable.append(f"{rid} → {uri} (not found)")
                    continue

                cache[str(uri) + "@" + rid] = {
                    "observed": f"sha256:{observed}",
                    "observed_at": now.isoformat(timespec="seconds"),
                    "resolver": "file",
                }

                # A truncated stored hash is a PREFIX, and is compared as one. Earlier
                # builds abbreviated it for readability; full digests are stored now, and
                # both compare correctly without a migration.
                if observed.startswith(captured):
                    counts["match"] += 1
                else:
                    counts["drifted"] += 1
                    drifted.append((rid, uri, status))

    # Keep only observations for pointers the mesh still holds. An entry for a concept that
    # was deleted, or a source that was repointed, is a record of something that is no longer
    # being asked about — and the viewer bakes its drift state out of this file.
    dropped = len(cache)
    cache = {k: v for k, v in cache.items() if k in live_keys}
    dropped -= len(cache)
    save_cache(cache)

    total = sum(counts.values())
    print(f"observed {total} pointer(s) — "
          f"{counts['match']} match, {counts['drifted']} drifted, {counts['unknown']} unknown")
    # `max_age` was printed here as though it governed. It does not, and for a local file it
    # should not: DR-0006 sized it for resolvers that cost a round trip, and hashing a file on
    # disk costs microseconds. Always re-observing beats maybe-re-observing when the saving is
    # nothing — but a number printed beside the cache reads as the rule the cache follows.
    print(f"cache: {CACHE.relative_to(HERE)}  ({len(cache)} observation(s), "
          f"file pointers re-read every run)"
          + (f", {dropped} stale entr{'y' if dropped == 1 else 'ies'} dropped" if dropped else "")
          + "\n")

    for rid, uri, status in drifted:
        print(f"  DRIFTED  [{status}]  {rid}\n           → {uri}")
    for u in unresolvable[:10]:
        print(f"  unknown  {u}")
    if len(unresolvable) > 10:
        print(f"  unknown  … and {len(unresolvable) - 10} more")

    if unpinned:
        # Named separately from the unresolvable ones because the remedy is different and
        # the cause is not a fault. These sources exist and were read; nothing has recorded
        # what they looked like, so there is no baseline to drift from yet.
        print(f"\n  {len(unpinned)} pointer(s) carry no captured hash — nothing to compare "
              f"against yet.")
        for u in unpinned[:5]:
            print(f"  unpinned {u}")
        if len(unpinned) > 5:
            print(f"  unpinned … and {len(unpinned) - 5} more")
        print("  This is normal for a hand-written concept: computing a hash means running "
              "something,\n  and level 1 runs nothing. `revalidate <path> --by human:you` "
              "pins one when you are ready.")

    # Only `stable` concepts fail the build. A draft is expected to be out of step with
    # its source; that is what draft means.
    blocking = [d for d in drifted if d[2] == "stable"]
    if check and blocking:
        print(f"\n{len(blocking)} drifted source(s) in stable concepts")
        return 1
    if drifted:
        print("\nDrift is a review queue, not an error. Re-validate, supersede, or "
              "acknowledge —\nand only a human refreshes `okfm_captured`, because doing it "
              "automatically\nwould erase the signal it exists to carry.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
