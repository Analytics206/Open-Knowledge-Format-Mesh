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
from okfm_core import (HERE, PROJECT, configured_bundles, find_config,
                       load_or_create_config, parse_relations, reject_unknown)

ROOT = PROJECT
CACHE = HERE / ".okfm-cache" / "observations.json"

VIEWER_NAME = "okfm-web-ui.html"


def viewer_path(cfg: dict) -> Path:
    """Where the viewer is, honouring `read.web_ui.path`.

    That key described the viewer's location and nothing read it — the one config key able to
    fail the pipeline was ignored by the component that failed. Setting it now moves the file
    for real, which is what an adopter reasonably expects when a config names a path.

    Falls back to the project root, then to this folder: pasting the drop-in in as `.okfm/`
    and dropping the viewer beside it both work without configuring anything.
    """
    named = ((cfg.get("read") or {}).get("web_ui") or {}).get("path") \
        or (cfg.get("web_ui") or {}).get("path")
    if named:
        return (PROJECT / str(named).removeprefix("./")).resolve()
    for candidate in (PROJECT / VIEWER_NAME, HERE / VIEWER_NAME):
        if candidate.is_file():
            return candidate
    return PROJECT / VIEWER_NAME

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
    out = []
    for pred, tgt in parse_relations(block):
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


def mesh_owners(cfg: dict) -> dict:
    """Bundle owners, read from the mesh's `OKF Member` concepts.

    Naming the accountable person is the one thing no process can infer (§12.1), so it is read
    where a person actually wrote it and left absent everywhere else. Inventing a plausible
    value here is how this repository's steward ended up credited in other people's viewers.
    """
    out = {}
    mesh = configured_bundles(cfg).get(cfg.get("mesh", "mesh"))
    if not mesh or not (mesh / "members").is_dir():
        return out
    for f in sorted((mesh / "members").glob("*.md")):
        m = _FM.match(f.read_text(encoding="utf-8"))
        if not m:
            continue
        owner = re.search(r"^\s+owner:[ \t]*(.+)$", m.group(1), re.M)
        value = owner.group(1).strip().strip("\"'") if owner else ""
        out[f.stem] = None if value in ("", "null", "~") else value
    return out


def mesh_title(cfg: dict) -> str:
    """What to call this mesh in the viewer's header.

    The mesh index's own `title` if a person wrote one, otherwise the project's folder name.
    Never a constant: a hardcoded "OKFM mesh (bundled)" meant every adopter's viewer announced
    the tool instead of their project.
    """
    mesh = configured_bundles(cfg).get(cfg.get("mesh", "mesh"))
    if mesh and (mesh / "index.md").is_file():
        m = _FM.match((mesh / "index.md").read_text(encoding="utf-8"))
        title = scalar(m.group(1), "title") if m else None
        if title:
            return title
    return f"{PROJECT.name} mesh"


def collect():
    _, cfg, _ = load_or_create_config(write=False)
    obs = load_observations()
    owners = mesh_owners(cfg)
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
            # `owner: None` when nothing declares one. This used to hardcode the handle of
            # THIS repository's steward, which every adopter then found baked into their own
            # viewer, once per bundle, attributing their documentation to a stranger. The
            # generated concepts had it right all along — `owner: null` with a comment saying
            # why — and only the baked page invented an answer.
            bundles.append({"id": bundle_id, "title": bundle_id, "owner": owners.get(bundle_id)})

    concepts.sort(key=lambda c: c["p"])
    return {
        # The adopter's project, not this one. A viewer titled "OKFM mesh" over somebody
        # else's documents is the tool talking about itself in a window that belongs to them.
        # The mesh's own index title wins when there is one, because a person wrote it.
        "name": mesh_title(cfg),
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
    reject_unknown(sys.argv[1:], ("--check",))
    check = "--check" in sys.argv
    _, cfg = find_config()
    viewer = viewer_path(cfg or {})

    if not viewer.is_file():
        # Skipped, not failed. The viewer is a *reader*; the mesh is built and valid without
        # it, and taking down the whole pipeline for a missing convenience meant an adopter's
        # first run ended in a raw FileNotFoundError naming a file they had never heard of.
        # That reads as "this tool is broken", not "you are missing a step" — and a stranger
        # who greps the documentation for the filename finds twenty-eight mentions and no
        # instruction to install it.
        where = viewer.relative_to(PROJECT) if viewer.is_relative_to(PROJECT) else viewer
        print(f"no viewer at {where} — skipping the bake.", file=sys.stderr)
        print(f"The mesh is built and valid; this step only bakes an index into the page.",
              file=sys.stderr)
        print(f"To read it in a browser, copy `{VIEWER_NAME}` from the OKFM download — it "
              f"sits at the\ndownload's root, NOT inside the folder you pasted in — to "
              f"{PROJECT.name}/, then re-run.", file=sys.stderr)
        print(f"Or point `read.web_ui.path` at wherever you keep it.", file=sys.stderr)
        return 0

    mesh = collect()
    html = viewer.read_text(encoding="utf-8")

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
    viewer.write_text(html, encoding="utf-8")

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
