#!/usr/bin/env python3
"""The drop-in build. Paste this folder into a project, run this file, get a mesh.

    python okfm/build.py            # dry run: says what it would do
    python okfm/build.py --apply    # writes

It defaults to the directory it was dropped into. On a first run with no configuration it
scans that directory, reports what it found, and writes the config it used — so the first
thing you edit is a file it made for you rather than a blank page.

Two modes:

    mirror (default)  Concepts are written into the bundle and point back at your files
                      via `resource`. Your markdown is never touched. This is the safe
                      default because the folder gets pasted into other people's
                      repositories.

    in-place          Frontmatter is added to your markdown, so your files *become* the
                      concepts. Right when the documents are themselves the knowledge —
                      decision records, for instance — and wrong for a docs tree the
                      concepts are merely *about*.

`needs: []` — no network, no secrets, no model. Python 3.13, standard library only.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from okfm_core import (
    HERE, PROJECT, RESERVED, bundle_root, frontmatter, load_or_create_config,
    resolve_sources, scalar,
)
from bootstrap import _extract_description, _title, _yaml_str


def _rel(frm: Path, to: Path) -> str:
    """Relative path from a concept file to the source it points at, POSIX-style."""
    import os
    return Path(os.path.relpath(to, frm.parent)).as_posix()


MINE = "process:okfm-build"


def _owned(dest: Path) -> bool:
    """May this build overwrite an existing concept?

    Only if nothing but this process has ever touched it. A concept stamped by a model, or
    carrying a `verified` entry, is somebody's work — and regenerating it would throw away
    the enrichment that is the entire point of level 3, silently, on a routine rebuild.

    This is the rule that makes the build safe to re-run, which it has to be: an adopter runs
    it after every documentation change, and a tool that eats your edits on the second run
    gets deleted after the second run.
    """
    if not dest.exists():
        return True
    block, _ = frontmatter(dest)
    if not block:
        return True
    if re.search(r"^verified:", block, re.M):
        return False
    return (scalar(block, "generated") or "").find(MINE) >= 0


def mirror(src_dir: Path, out_dir: Path, ctype: str, stamp: str, apply: bool) -> list[str]:
    """Write one concept per source document, pointing back at the source."""
    written = []
    for f in sorted(src_dir.glob("*.md")):
        if f.name in RESERVED:
            continue
        block, _ = frontmatter(f)
        if block and scalar(block, "type"):
            continue                      # already a concept in its own right
        if not _owned(out_dir / f.name):
            continue                      # somebody has since worked on it — leave it alone

        text = f.read_text(encoding="utf-8")
        # Hash the TEXT, never raw bytes — universal-newline translation normalizes CRLF
        # so the digest is stable across platforms. See .gitattributes.
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        dest = out_dir / f.name

        concept = "\n".join([
            "---",
            f"type: {ctype}",
            f"title: {_yaml_str(_title(text, f))}",
            f"description: {_yaml_str(_extract_description(text))}",
            "status: draft",
            f'generated: {{ by: "{MINE}", at: {stamp} }}',
            "sources:",
            "  - id: source",
            f"    resource: {_rel(dest, f)}",
            "    okfm_role: subject",
            f'    okfm_captured: {{ hash: "sha256:{sha}", at: {stamp[:10]} }}',
            "---",
            "",
            f"# {_title(text, f)}",
            "",
            "This concept points at its source; it does not restate it. Add here only what",
            "the source cannot say — why a choice was made, what was rejected, what would",
            "change it. If there is nothing to add, the pointer alone is the right answer.",
            "",
        ])
        if apply:
            out_dir.mkdir(parents=True, exist_ok=True)
            dest.write_text(concept, encoding="utf-8", newline="\n")
        written.append(f.name)
    return written


def write_index(out_dir: Path, name: str, names: list[str], stamp: str, apply: bool,
                mesh_id: str | None = None) -> None:
    lines = [
        "---", "type: Index", f"title: {_yaml_str(name)}",
        f"description: Concepts derived from {name}.", "status: draft",
        f'generated: {{ by: "{MINE}", at: {stamp} }}',
    ]
    if mesh_id:
        # The other half of the edge the mesh writes. Either direction alone would draw the
        # graph; both are true, and a bundle that cannot name the mesh it belongs to is
        # findable only from outside.
        lines += ["okfm_relations:",
                  f"  - {{ predicate: registered_by, target: /{mesh_id}/index.md }}"]
    lines += ["---", "", f"# {name}", ""]
    for n in names:
        lines.append(f"- [{n[:-3]}]({n})")
    lines.append("")
    if apply:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _bundle_id(cfg: dict, out_dir: Path, fallback: str) -> str:
    """The id this bundle is known by across the mesh.

    Usually the folder name. A config with an explicit `bundles` map may call it something
    else, and relation targets are resolved against the id -- so writing the folder name into
    a cross-bundle edge would produce one that resolves to nothing.
    """
    for bid, rel in (cfg.get("bundles") or {}).items():
        if (PROJECT / rel.removeprefix("./")).resolve() == out_dir.resolve():
            return bid
    return fallback


def write_mesh(cfg: dict, out_root: Path, mesh_name: str, built: list[tuple[str, str, int]],
               stamp: str, apply: bool) -> int:
    """Write the mesh OKF: one `OKF Member` concept per bundle, plus the map.

    The mesh is the point of the format, so a project that ends up with four bundles and no
    way to say how they relate has been given the parts and not the thing. It is generated
    rather than authored for the same reason the web UI index is: a map maintained by hand
    disagrees with the territory eventually, and the disagreement is silent.

    It owns the map and never member content -- index-*over*, not authority-*over*.
    """
    mesh_dir = out_root / mesh_name
    written = 0

    for name, path, count in built:
        dest = mesh_dir / "members" / f"{name}.md"
        if not _owned(dest):
            continue
        body = "\n".join([
            "---",
            "type: OKF Member",
            f"title: {_yaml_str(name)}",
            f"description: {_yaml_str(f'{count} concept(s) derived from {path}.')}",
            f"resource: ../../{name}",
            "status: draft",
            f'generated: {{ by: "{MINE}", at: {stamp} }}',
            "okfm_member:",
            "  owner: null",
            "  agent: null",
            "  sync_policy: pull",
            "okfm_relations:",
            "  - { predicate: part_of, target: /index.md }",
            # Mesh-absolute, and the reason this edge exists at all: without it the mesh
            # knows its members and the graph does not. Filter a web UI to the registry and
            # one member bundle and nothing connects them -- which is the single
            # relationship a mesh is for.
            f"  - {{ predicate: registers, "
            f"target: /{_bundle_id(cfg, out_root / name, name)}/index.md }}",
            "---",
            "",
            f"# {name}",
            "",
            f"Built from [`{path}`](../../../{path}). Its documents are the source; these",
            "concepts point at them and never restate them.",
            "",
            "`owner` is null because nothing can infer it. Naming the accountable person is",
            "the one thing this file is for that a directory listing does not already do.",
            "",
        ])
        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(body, encoding="utf-8", newline="\n")
        written += 1

    index = mesh_dir / "index.md"
    if _owned(index):
        lines = [
            "---", "type: Index", "title: The mesh",
            "description: The mesh OKF — read first. Its concepts are the other OKFs.",
            "status: draft", f'generated: {{ by: "{MINE}", at: {stamp} }}', "---", "",
            "# Members", "",
        ]
        lines += [f"- [{n}](members/{n}.md) — {c} concept(s) from `{p}`" for n, p, c in built]
        lines += [
            "",
            "# What this owns",
            "",
            "Membership, and nothing else. Member content lives in the member. This file is",
            "regenerated on every build, so editing it is not the way to change it — add or",
            "remove a source folder instead.",
            "",
        ]
        if apply:
            mesh_dir.mkdir(parents=True, exist_ok=True)
            index.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        written += 1
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write; otherwise dry-run")
    ap.add_argument("--in-place", action="store_true",
                    help="add frontmatter to your files instead of mirroring them")
    a = ap.parse_args()

    cfg_path, cfg, created = load_or_create_config(write=a.apply)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    out_root = bundle_root(cfg)

    print(f"project : {PROJECT}")
    print(f"dropin  : {HERE}")
    print(f"config  : {cfg_path}" + ("  (synthesized)" if created else ""))
    print(f"bundle  : {out_root}")
    print(f"mode    : {'in-place' if a.in_place else cfg.get('mode', 'mirror')}\n")

    sources = resolve_sources(cfg)
    if not sources:
        print("No source directories found.")
        print("Nothing was written. Point `discover.root` at a directory that holds")
        print("markdown, or list folders explicitly under `sources`.")
        return 0

    total, built, targets = 0, [], {}
    for entry in sources:
        rel = entry["path"] if isinstance(entry, dict) else entry
        ctype = (entry.get("type") if isinstance(entry, dict) else None) or "Document"
        src = (PROJECT / rel).resolve()
        if not src.is_dir():
            print(f"  skip  {rel} — not a directory")
            continue

        # `bundle` names the output folder. Without it a nested source path turns into
        # `docs-levels-level-1-view`, which is accurate and unusable as a bundle id.
        name = (entry.get("bundle") if isinstance(entry, dict) else None) \
            or ("root" if rel == "." else rel.replace("/", "-"))
        out_dir = out_root / name
        # Two source folders resolving to one bundle is not a data-loss risk -- concepts
        # this build does not own are never written -- but a bundle fed from two places is
        # confusing enough to say out loud rather than let someone discover later.
        if name in targets:
            print(f"  note  {rel} and {targets[name]} both build `{name}` — "
                  f"rename one folder, or name the bundle in `sources`")
        targets[name] = rel
        names = mirror(src, out_dir, ctype, stamp, a.apply)
        if names and _owned(out_dir / "index.md"):
            write_index(out_dir, name, names, stamp, a.apply,
                        _bundle_id(cfg, out_root / cfg.get("mesh", "mesh"),
                                   cfg.get("mesh", "mesh")))
        shown = out_dir.relative_to(PROJECT) if out_dir.is_relative_to(PROJECT) else out_dir
        print(f"  {'wrote' if a.apply else 'would'}  {len(names):>3}  {rel}  →  {shown}")
        total += len(names)
        if out_dir.is_dir() or names:
            built.append((name, rel, len(names) or
                          sum(1 for f in out_dir.glob("*.md") if f.name not in RESERVED)))

    mesh_name = cfg.get("mesh", "mesh")
    if mesh_name and built:
        n = write_mesh(cfg, out_root, mesh_name, sorted(built), stamp, a.apply)
        print(f"  {'wrote' if a.apply else 'would'}  {n:>3}  the mesh  →  "
              f"{(out_root / mesh_name).relative_to(PROJECT)}")

    print(f"\n{total} concept(s) {'written' if a.apply else 'planned'}")
    if not a.apply:
        print("\nDry run — nothing was written, including the config.")
        print("Run again with --apply.")
    else:
        print("\nEvery concept is `status: draft` with no `verified` entry: descriptions")
        print("were extracted from your files, not written, and nobody has reviewed them.")
        print("\nNext:  python okfm/check_bundles.py")
    return 0


if __name__ == "__main__":
    # Running `python <dir>/build.py` puts <dir> on sys.path[0], so the sibling
    # imports above resolve wherever this folder was pasted.
    raise SystemExit(main())
