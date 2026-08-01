#!/usr/bin/env python3
"""Regenerate the viewer's baked index from the real bundles.

An early cut of `okfm view`'s baking step (decisions/0008 build step 9). The committed
viewer must carry METADATA ONLY -- never concept bodies. A rendered copy of a bundle is a
second home for its knowledge (spec 3.14), it goes stale silently, and a published incident
records a benchmark control arm being contaminated by exactly this (spec 21.3).

Trust and staleness are NOT written here. They are derived by the viewer at render time
(spec 3.4) from the signals this script copies out: `verified`, `stale_after`,
`okfm_captured`.

`needs: []` -- no network, no secrets, no model.

    python dropin/bake_viewer.py [--check]

--check exits non-zero if the committed viewer is out of date, for CI.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWER = ROOT / "okfm-viewer.html"
CONFIG = ROOT / "okfm.json"

RESERVED_TYPES = {"Index", "Log"}
_FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
_BOOTSTRAP = re.compile(r"(const BOOTSTRAP = )(\{.*?\n\});", re.S)


def scalar(block: str, key: str):
    m = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    v = " ".join(p.strip() for p in m.group(1).splitlines()).strip()
    if v.startswith(('"', "'")) and v.endswith(('"', "'")):
        v = v[1:-1]
    return v.replace('\\"', '"') or None


def relations(block: str, bundle_root: str):
    """Bundle-relative in the file, mesh-relative in the index (decisions/0005)."""
    m = re.search(r"^okfm_relations:\s*\n((?:[ \t]*-.*\n?)+)", block, re.M)
    if not m:
        return []
    out = []
    for pred, tgt in re.findall(r"predicate:\s*([\w_]+),\s*target:\s*([^\s}]+)", m.group(1)):
        out.append([pred, tgt if not tgt.startswith("/") else f"{bundle_root}{tgt}"])
    return out


def trust(block: str):
    """DERIVED, never stored. A human verifier outranks a machine one; absent is unverified."""
    if not re.search(r"^verified:", block, re.M):
        return None
    return "human" if re.search(r"^verified:.*human:", block, re.M) else "machine"


def collect():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    bundles, concepts = [], []

    for bundle_id, rel in cfg["bundles"].items():
        root = "/" + rel.lstrip("./").rstrip("/")
        src = (ROOT / rel).resolve()
        if not src.is_dir():
            print(f"  warn: bundle '{bundle_id}' -> {rel} does not exist", file=sys.stderr)
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
                # Drift needs a live resolution and a cache with a TTL (decisions/0006).
                # The bake step is `needs: []`, so it reports 0 rather than guessing.
                "drift": 0,
                "r": relations(block, root),
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


def main() -> int:
    check = "--check" in sys.argv
    mesh = collect()
    html = VIEWER.read_text(encoding="utf-8")

    m = _BOOTSTRAP.search(html)
    if not m:
        print("FATAL: BOOTSTRAP block not found in viewer", file=sys.stderr)
        return 2

    new = json.dumps(mesh, indent=1, ensure_ascii=False)
    if new.strip() == m.group(2).strip():
        print(f"up to date — {len(mesh['concepts'])} concepts in {len(mesh['bundles'])} bundles")
        return 0

    if check:
        print("STALE: committed viewer does not match the bundles — run bake_viewer.py",
              file=sys.stderr)
        return 1

    VIEWER.write_text(html[:m.start(2)] + new + html[m.end(2):], encoding="utf-8")
    by_bundle = {}
    for c in mesh["concepts"]:
        by_bundle[c["b"]] = by_bundle.get(c["b"], 0) + 1
    print(f"baked {len(mesh['concepts'])} concepts across {len(mesh['bundles'])} bundles")
    for b, n in sorted(by_bundle.items()):
        print(f"  {n:>3}  {b}")

    if "body" in new.lower() and '"body"' in new:
        print("FATAL: bodies leaked into the index", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
