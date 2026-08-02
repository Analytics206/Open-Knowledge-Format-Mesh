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
    HERE, PROJECT, RESERVED, bundle_root, configured_bundles, frontmatter,
    load_or_create_config, resolve_sources, scalar,
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
    """Write one concept per source document, pointing back at the source.

    Reserved filenames are skipped and **said out loud**. `README.md` is the one that hurts:
    in most projects it is the orientation document — the file you would most want an agent to
    read first — and it was the file guaranteed to be missing from the bundle, silently, while
    the documentation promised that every folder of documents becomes an OKF.

    Still skipped rather than mirrored: `index.md` is regenerated here, and a README is
    conventionally *about the folder* rather than knowledge in it, so mirroring it would put a
    table of contents in the graph. But an adopter who wants it as a concept needs to know it
    was dropped before they can decide, so the build names what it left behind.
    """
    written, skipped = [], []
    for f in sorted(src_dir.glob("*.md")):
        if f.name in RESERVED:
            if f.name not in ("index.md", "log.md"):
                skipped.append(f.name)
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
    if skipped:
        print(f"  note   {src_dir.name}/: skipped {', '.join(skipped)} — reserved names are "
              f"about the folder, not knowledge in it")
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


def prune_members(cfg: dict, mesh_dir: Path, built: list[tuple[str, str, int]],
                  apply: bool) -> int:
    """Drop member concepts for bundles that are no longer part of the mesh.

    Removing a bundle from `bundles` used to leave its `OKF Member` concept behind, still
    carrying `registers -> /<gone>/index.md`. The mesh then advertised a member nobody could
    read, and the failure surfaced two steps away as a dangling relation in a different
    bundle -- so the config change looked like it had broken something rather than like it
    had left something behind.

    This is the only place the build deletes anything, and it is deliberately narrow: `.md`
    files, in the mesh's own `members/` folder, that this process wrote. A member somebody
    edited is reported and left alone -- if a person put content there, a config edit is not
    grounds for a tool to throw it away.
    """
    members = mesh_dir / "members"
    if not members.is_dir():
        return 0

    known = set(configured_bundles(cfg)) | {name for name, _, _ in built} | {mesh_dir.name}
    removed = 0
    for f in sorted(members.glob("*.md")):
        if f.stem in known:
            continue
        if not _owned(f):
            print(f"  stale    {f.relative_to(mesh_dir.parent)} — registers `{f.stem}`, "
                  f"which is not a bundle any more. Not mine to delete; remove it yourself.",
                  file=sys.stderr)
            continue
        print(f"  {'removed ' if apply else 'would rm '} {f.relative_to(mesh_dir.parent)}"
              f"  — `{f.stem}` is not a bundle any more")
        if apply:
            f.unlink()
        removed += 1
    return removed


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
    written = prune_members(cfg, mesh_dir, built, apply)

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
            # Empty, and PRESENT. `answers` is the reason a mesh beats a folder — it is what
            # lets an agent route on frontmatter instead of reading every bundle — and it was
            # the one field the build never emitted at all. So it existed only in bundles
            # somebody had hand-written, while the documentation led with it as a feature,
            # and an adopter's generated mesh silently lacked the capability being sold.
            #
            # It cannot be derived: naming the questions a bundle answers is a judgement about
            # what it is for. But an empty key an adopter can see is a prompt to fill it, and
            # an absent one is a gap nobody knows they have.
            "  answers: []          # what questions does this bundle answer? yours to write",
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
            "`answers` is empty for the same reason, and it is the more valuable of the two.",
            "It is what lets an agent pick a bundle by reading frontmatter instead of opening",
            "every one — the whole difference between a mesh and a folder. Write three or four",
            "questions this bundle actually answers, in the words somebody would ask them:",
            "",
            "```yaml",
            "okfm_member:",
            "  answers:",
            "    - how do I run the ingest job locally",
            "    - what happens when a payment fails",
            "```",
            "",
            "Nothing will fill these in for you. A build cannot know what a bundle is *for*,",
            "and a guess here sends an agent to the wrong bundle with confidence.",
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

    mirrored, indexes, built, targets = 0, 0, [], {}
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
            indexes += 1
        shown = out_dir.relative_to(PROJECT) if out_dir.is_relative_to(PROJECT) else out_dir
        print(f"  {'wrote' if a.apply else 'would'}  {len(names):>3}  {rel}  →  {shown}")
        mirrored += len(names)
        if out_dir.is_dir() or names:
            built.append((name, rel, len(names) or
                          sum(1 for f in out_dir.glob("*.md") if f.name not in RESERVED)))

    mesh_name = cfg.get("mesh", "mesh")
    mesh_n = 0
    if mesh_name and built:
        mesh_n = write_mesh(cfg, out_root, mesh_name, sorted(built), stamp, a.apply)
        print(f"  {'wrote' if a.apply else 'would'}  {mesh_n:>3}  the mesh  →  "
              f"{(out_root / mesh_name).relative_to(PROJECT)}")

    # Every number said out loud, and they add up. The total used to exclude the mesh line
    # printed directly above it, so the per-folder figures summed to more than the stated
    # total, and neither counted the generated indexes — three unlabelled counts for one
    # build, which an adopter could only reconcile by counting files.
    #
    # This says what THIS RUN wrote, and deliberately does not predict what the viewer will
    # show: the viewer counts every concept on disk, which is the same number only on a first
    # run and diverges the moment the build becomes incremental.
    total = mirrored + mesh_n
    verb = "written" if a.apply else "planned"
    print(f"\n{total} concept(s) {verb} this run: {mirrored} from your documents"
          + (f", {mesh_n} in the mesh" if mesh_n else "")
          + (f", plus {indexes} generated index.md" if indexes else ""))
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
