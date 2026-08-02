#!/usr/bin/env python3
"""Regenerate the web UI's baked index from the real bundles.

An early cut of `okfm view`'s baking step (decisions/0008 build step 9). The committed
viewer must carry METADATA ONLY -- never concept bodies. A rendered copy of a bundle is a
second home for its knowledge (spec 3.14), it goes stale silently, and a published incident
records a benchmark control arm being contaminated by exactly this (spec 21.3).

Trust and staleness are NOT written here. They are derived by the web UI at render time
(spec 3.4) from the signals this script copies out: `verified`, `stale_after`,
`okfm_captured`.

`needs: []` -- no network, no secrets, no model.

    python dropin/bake_web_ui.py [--check]

--check exits non-zero if the committed viewer is out of date, for CI.
"""
import json
import re
import sys
from pathlib import Path

import config_schema
from okfm_core import HERE, PROJECT, configured_bundles, find_config, load_or_create_config

ROOT = PROJECT
VIEWER = PROJECT / "okfm-web-ui.html"
CACHE = HERE / ".okfm-cache" / "observations.json"

RESERVED_TYPES = {"Index", "Log"}
_FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)

# Each baked block: the constant it fills, and how to produce its contents. The config panel
# needs two of them — the rules, so the page can validate without asking anything, and the
# config itself, so it opens showing what is actually on disk rather than a blank form.
_BLOCKS = [
    ("BOOTSTRAP", re.compile(r"(const BOOTSTRAP = )(\{.*?\n\});", re.S)),
    ("CONFIG_SCHEMA", re.compile(r"(const CONFIG_SCHEMA = )(\{.*?\n\});", re.S)),
    ("CONFIG", re.compile(r"(const CONFIG = )(\{.*?\n\});", re.S)),
]


def scalar(block: str, key: str):
    m = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    v = " ".join(p.strip() for p in m.group(1).splitlines()).strip()
    if v.startswith(('"', "'")) and v.endswith(('"', "'")):
        v = v[1:-1]
    return v.replace('\\"', '"') or None


def relations(block: str, bundle_root: str, bundle_ids: set[str] | None = None):
    """Bundle-relative in the file, mesh-relative in the index (decisions/0005).

    An absolute target whose first segment names a bundle is already mesh-absolute and must
    be left alone. Prefixing it would rewrite every cross-bundle edge into a dangling
    same-bundle one -- and a mesh whose members cannot point at each other is a directory
    listing with extra steps.
    """
    m = re.search(r"^okfm_relations:\s*\n((?:[ \t]*-.*\n?)+)", block, re.M)
    if not m:
        return []
    out = []
    for pred, tgt in re.findall(r"predicate:\s*([\w_]+),\s*target:\s*([^\s}]+)", m.group(1)):
        if tgt.startswith("/") and (tgt.lstrip("/").split("/", 1)[0] not in (bundle_ids or ())):
            tgt = f"{bundle_root}{tgt}"
        out.append([pred, tgt])
    return out


def trust(block: str):
    """DERIVED, never stored. A human verifier outranks a machine one; absent is unverified."""
    if not re.search(r"^verified:", block, re.M):
        return None
    return "human" if re.search(r"^verified:.*human:", block, re.M) else "machine"


_CAPTURED = re.compile(r"resource:\s*(\S+)[\s\S]*?hash:\s*\"?sha256:([0-9a-f]+)")


def load_observations() -> dict:
    """The cache holds OBSERVATIONS, never verdicts (DR-0006). Baking derives the verdict
    by comparing what was observed against what the concept captured — a comparison, not a
    resolution, so it stays `needs: []`."""
    if not CACHE.is_file():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def drift_of(block: str, rid: str, obs: dict) -> int | None:
    """1 drifted, 0 match, None never observed.

    None is emitted as JSON `null` and the web UI renders it `unknown`. Defaulting it to
    0 would be the stored-opinion failure spec §3.4 exists to prevent.
    """
    pairs = _CAPTURED.findall(block)
    if not pairs:
        return 0                            # nothing pinned means nothing to drift from
    seen_any = False
    for uri, captured in pairs:
        entry = obs.get(f"{uri}@{rid}")
        if not entry:
            continue
        seen_any = True
        if not entry.get("observed", "").removeprefix("sha256:").startswith(captured):
            return 1
    return 0 if seen_any else None


def collect():
    _, cfg, _ = load_or_create_config(write=False)
    obs = load_observations()
    bundles, concepts = [], []
    all_bundles = configured_bundles(cfg)
    bundle_ids = set(all_bundles)

    for bundle_id, src in all_bundles.items():
        root = f"/{bundle_id}"
        if not src.is_dir():
            print(f"  warn: bundle '{bundle_id}' -> {src} does not exist", file=sys.stderr)
            continue

        found = 0
        for f in sorted(src.rglob("*.md")):
            text = f.read_text(encoding="utf-8")
            fm = _FM.match(text)
            if not fm:
                continue
            block = fm.group(1)
            ctype = scalar(block, "type")
            if not ctype:
                continue

            mesh_path = f"{root}/{f.relative_to(src).as_posix()}"
            concepts.append({
                "p": mesh_path,
                "b": bundle_id,
                "t": ctype,
                "title": scalar(block, "title") or f.stem,
                "d": scalar(block, "description") or "",
                "v": trust(block),
                "sa": scalar(block, "stale_after"),
                "src": len(re.findall(r"^\s+- id:", block, re.M)),
                "drift": drift_of(block, f"{bundle_id}/{f.relative_to(src).as_posix()}", obs),
                "r": relations(block, root, bundle_ids),
                "scope": scalar(block, "okfm_scope"),
            })
            found += 1

        if found:
            bundles.append({"id": bundle_id, "title": bundle_id, "owner": "human:analytics206"})

    concepts.sort(key=lambda c: c["p"])
    return {
        "name": "OKFM mesh (bundled)",
        "generated_at": "2026-08-01",
        "bundles": bundles,
        "concepts": concepts,
    }


def current_config() -> dict:
    """The config exactly as it sits on disk, so the panel opens on the real thing.

    Deliberately the RAW file and not the normalized one. The panel edits what a person
    wrote; showing them keys the normalizer lifted would mean saving a file they did not
    write and cannot recognise.
    """
    path, _ = find_config()
    if path is None:
        return {"_note": "No okfm.json yet. The first build writes one for you."}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"_error": f"okfm.json is not valid JSON: {exc}"}


def main() -> int:
    check = "--check" in sys.argv
    mesh = collect()
    html = VIEWER.read_text(encoding="utf-8")

    schema = json.loads(config_schema.as_json())
    # The command to run, as it would actually be typed in THIS project. The panel cannot
    # work it out — where the drop-in folder was pasted is only knowable from here.
    schema["run"] = f"python {HERE.relative_to(PROJECT).as_posix()}/okfm.py"

    payloads = {
        "BOOTSTRAP": mesh,
        "CONFIG_SCHEMA": schema,
        "CONFIG": current_config(),
    }

    stale, edits = [], []
    for name, pattern in _BLOCKS:
        m = pattern.search(html)
        if not m:
            print(f"FATAL: {name} block not found in viewer", file=sys.stderr)
            return 2
        new = json.dumps(payloads[name], indent=1, ensure_ascii=False)
        if new == "{}":
            # The anchor is a closing brace at column 0. An empty object has none, and the
            # next bake would fail to find its own block.
            new = "{\n}"
        if new.strip() != m.group(2).strip():
            stale.append(name)
            edits.append((m.start(2), m.end(2), new))

    if not stale:
        print(f"up to date — {len(mesh['concepts'])} concepts in {len(mesh['bundles'])} bundles")
        return 0

    if check:
        print(f"STALE: committed viewer does not match the project ({', '.join(stale)}) — "
              f"run bake_web_ui.py", file=sys.stderr)
        return 1

    # Right to left, so an earlier replacement does not move a later one's offsets.
    for start, end, new in sorted(edits, reverse=True):
        html = html[:start] + new + html[end:]
    VIEWER.write_text(html, encoding="utf-8")

    by_bundle = {}
    for c in mesh["concepts"]:
        by_bundle[c["b"]] = by_bundle.get(c["b"], 0) + 1
    print(f"baked {len(mesh['concepts'])} concepts across {len(mesh['bundles'])} bundles"
          f"  [{', '.join(stale)}]")
    for b, n in sorted(by_bundle.items()):
        print(f"  {n:>3}  {b}")

    index = json.dumps(mesh, ensure_ascii=False)
    if '"body"' in index:
        print("FATAL: bodies leaked into the index", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
