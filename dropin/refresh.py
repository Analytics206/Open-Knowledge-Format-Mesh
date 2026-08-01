#!/usr/bin/env python3
"""Observe pointers and report drift — DR-0006.

    python okfm/refresh.py            # observe, write the cache, report
    python okfm/refresh.py --check    # exit 1 if a `stable` concept has a drifted source

Drift is **observed here and nowhere else.** Nothing on the read path — not the viewer, not
an injected index, not an agent — resolves a pointer. That is what keeps reading a mesh free
and what stops an agent paying a database round trip before it has done anything.

Three states, never two:

    match      the source hashes to what `okfm_captured` recorded
    drifted    it does not
    unknown    never observed, or observed longer ago than `max_age`

`unknown` renders as unknown. Defaulting it to `match` would be a stored opinion wearing a
computed one's clothes, which is the failure spec 3.4 exists to prevent.

**The cache stores observations, not verdicts.** *This pointer hashed to X at time T* does
not become false later — it is the same kind of fact as `okfm_captured`, which the format
already stores. The verdict is still derived, here, from the two of them.

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

from okfm_core import HERE, PROJECT, configured_bundles, frontmatter, load_or_create_config, scalar

CACHE = HERE / ".okfm-cache" / "observations.json"

# Schemes this tier can resolve. Everything else needs a credential.
LIVE_SCHEMES = ("sys://", "store://", "okf://", "http://", "https://")

_SOURCE = re.compile(
    r"^\s+- id:\s*(?P<id>\S+)(?P<rest>(?:\n\s+.*)*)", re.M)
_RESOURCE = re.compile(r"^\s+resource:\s*(\S+)", re.M)
_HASH = re.compile(r"hash:\s*\"?sha256:([0-9a-f]+)", re.M)

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
    check = "--check" in sys.argv
    _, cfg, _ = load_or_create_config(write=False)
    drift_cfg = cfg.get("drift", {})
    max_age = {k: parse_age(v) for k, v in (drift_cfg.get("max_age") or {}).items()}
    default_age = max_age.get("file", 3600)

    now = datetime.now(timezone.utc)
    cache = load_cache()
    counts = {"match": 0, "drifted": 0, "unknown": 0}
    drifted, unresolvable = [], []

    for bid, root in sorted(configured_bundles(cfg).items()):
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            block, _ = frontmatter(f)
            if not block or not scalar(block, "type"):
                continue
            status = scalar(block, "status") or "stable"
            rid = f"{bid}/{f.relative_to(root).as_posix()}"

            for m in _SOURCE.finditer(block):
                entry = m.group("rest")
                res = _RESOURCE.search(entry)
                cap = _HASH.search(entry)
                if not res or not cap:
                    continue               # no captured hash means nothing to compare
                uri, captured = res.group(1), cap.group(1)

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

    save_cache(cache)

    total = sum(counts.values())
    print(f"observed {total} pointer(s) — "
          f"{counts['match']} match, {counts['drifted']} drifted, {counts['unknown']} unknown")
    print(f"cache: {CACHE.relative_to(HERE)}  (max_age file={default_age}s)\n")

    for rid, uri, status in drifted:
        print(f"  DRIFTED  [{status}]  {rid}\n           → {uri}")
    for u in unresolvable[:10]:
        print(f"  unknown  {u}")
    if len(unresolvable) > 10:
        print(f"  unknown  … and {len(unresolvable) - 10} more")

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
