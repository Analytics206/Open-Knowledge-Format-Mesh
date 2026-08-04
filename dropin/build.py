#!/usr/bin/env python3
"""The drop-in build. Paste this folder into a project, run this file, get a mesh.

    python okfm/build.py            # dry run: says what it would do
    python okfm/build.py --apply    # writes

It defaults to the directory it was dropped into. On a first run with no configuration it
scans that directory, reports what it found, and writes the config it used — so the first
thing you edit is a file it made for you rather than a blank page.

One mode. Concepts are written into the bundle and point back at your files via
`resource`; your markdown is never touched. That is not a default, it is the guarantee —
`.okfm/` belongs to the tool, your documents belong to you, and `rm -rf .okfm` returns the
project to exactly what it was.

**In-place bundles exist, and this build does not make them.** Where the documents *are*
the knowledge — decision records, for instance — you add the frontmatter yourself and name
the folder in `bundles`. The build then registers it in the mesh and writes nothing into
it. That is Level 1 with the mesh wrapped around it, and it is the arrangement
`docs/decisions` uses here.

> There was a `--in-place` flag and a `mode: "in-place"` config value for a long time.
> Neither was ever read: the flag reached exactly one line of code, the header that prints
> `mode : in-place`, and the build then mirrored. So it announced doing the one thing this
> tool promises not to do, and did not do it — the failure mode of a claim, not of a
> feature. Removed rather than implemented ([DR-0014](../docs/decisions/0014-packs-and-in-place-bundles.md)):
> a build that edits your documents cannot also promise it never touches them, and the
> promise is worth more than the mode.

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
    HERE, PROJECT, RESERVED, bundle_root, configured_bundles, frontmatter, is_concept,
    load_or_create_config, reserved_only_dirs, resolve_sources, scalar,
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


# The two places the build records *when*, and the only two values that may differ between
# two runs that found nothing new. Scoped to these exact shapes rather than "any date", so a
# real change to a title or description that happens to contain a date is still a change.
_STAMPS = (
    re.compile(r'(generated: \{ by: "[^"]*", at: )[^}]*(\})'),
    re.compile(r'(okfm_captured: \{ hash: "[^"]*", at: )[^}]*(\})'),
)


def _put(dest: Path, text: str) -> bool:
    """Write a generated file, unless the only thing that changed is when it was written.

    A rebuild that finds nothing new must change nothing. `generated.at` and
    `okfm_captured.at` carry today's date, so without this every build on a *later day* than
    the last one rewrites every concept the build still owns — a diff of pure timestamps
    across the whole mesh, on a mesh where nothing happened.

    That is worse than untidy. It is noise in exactly the place drift is supposed to be
    legible, and it lands hardest on a new adopter: nothing in their mesh is `verified:` yet,
    so the build owns all of it and every day's run is a full-mesh diff saying nothing.

    Leaving the older stamp is also the more honest record. `generated.at` means *when this
    was generated*, and a concept whose content is byte-identical was not regenerated today —
    it was checked today, found unchanged, and left alone. The hash stays visible to the
    comparison, so anything that actually changed still writes, with fresh stamps.
    """
    def blind(s: str) -> str:
        for pat in _STAMPS:
            s = pat.sub(r"\1<when>\2", s)
        return s

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and blind(dest.read_text(encoding="utf-8")) == blind(text):
        return False
    dest.write_text(text, encoding="utf-8", newline="\n")
    return True


def mirror(src_dir: Path, out_dir: Path, ctype: str, stamp: str, apply: bool,
           tags: list[str] | None = None) -> list[str]:
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
            # Declared per bundle in `build.bundle_tags`, because some claims are properties
            # of the folder rather than of any one file — every component in a level-2 bundle
            # is `needs-nothing` by definition, and extraction cannot derive that from prose.
            #
            # Emitted by the BUILD rather than added by hand afterwards, which is the whole
            # point. A tag typed into a build-owned concept is erased on the next run, so the
            # only way a claim survives is for the thing that rewrites the file to know it.
            *([f"tags: [{', '.join(tags)}]"] if tags else []),
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
            _put(dest, concept)
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
        _put(out_dir / "index.md", "\n".join(lines))


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

    # A bundle's directory is `build.out/<name>` when this build mirrored it, and wherever
    # `bundles` says when somebody authored it in place. Deriving it from the name alone
    # produced a member whose `resource` pointed into the output folder at a bundle that was
    # never there — a dangling pointer on the one concept whose job is to say where a bundle is.
    configured = {bid: (PROJECT / str(rel).removeprefix("./")).resolve()
                  for bid, rel in (cfg.get("bundles") or {}).items()}

    for name, path, count in built:
        dest = mesh_dir / "members" / f"{name}.md"
        if not _owned(dest):
            continue
        src_dir = configured.get(name, out_root / name)
        in_place = not src_dir.is_relative_to(out_root)
        body = "\n".join([
            "---",
            "type: OKF Member",
            f"title: {_yaml_str(name)}",
            f"description: {_yaml_str(f'{count} concept(s) ' + ('authored in place in' if in_place else 'derived from') + f' {path}.')}",
            f"resource: {_rel(dest, src_dir)}",
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
            f"target: /{_bundle_id(cfg, src_dir, name)}/index.md }}",
            "---",
            "",
            f"# {name}",
            "",
            (f"Authored in place in [`{path}`]({_rel(dest, src_dir)}). Those files carry "
             f"their own frontmatter, so they *are* the concepts — this build registers "
             f"the bundle and never writes into it."
             if in_place else
             f"Built from [`{path}`](../../../{path}). Its documents are the source; these "
             f"concepts point at them and never restate them."),
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
            _put(dest, body)
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
            _put(index, "\n".join(lines))
        written += 1
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write; otherwise dry-run")
    a = ap.parse_args()

    cfg_path, cfg, created = load_or_create_config(write=a.apply)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    out_root = bundle_root(cfg)

    print(f"project : {PROJECT}")
    print(f"dropin  : {HERE}")
    print(f"config  : {cfg_path}" + ("  (synthesized)" if created else ""))
    print(f"bundle  : {out_root}")
    print(f"mode    : {cfg.get('mode', 'mirror')} — your documents are never written to\n")

    # The drop-in pasted in AS the bundle root: tool, config and knowledge in one directory.
    # It works, and it is a trap on the second day rather than the first. There is then no
    # way to replace the tool without risking the knowledge — `rm -rf` before re-copying
    # takes every enriched and verified concept with it, and re-copying without deleting
    # nests a second copy and upgrades nothing, silently. Said once, at the top, because by
    # the time it matters the adopter has concepts worth losing.
    if HERE.resolve() == out_root.resolve():
        print(f"  note   the tool and the mesh share {HERE.name}/. That works, but there is")
        print(f"         then no way to upgrade one without risking the other. Keeping them")
        print(f"         apart — the tool in `okfm/`, the mesh in `.okfm/` — makes an")
        print(f"         upgrade `rm -rf okfm` and a re-copy, with your concepts untouched.\n")

    sources = resolve_sources(cfg)
    if not sources:
        print("No source directories found.")
        print("Nothing was written. Point `discover.root` at a directory that holds")
        print("markdown, or list folders explicitly under `sources`.")
        return 0

    # Folders the scan reached and dropped for holding nothing but reserved filenames.
    # Said before the build output rather than after, because it explains a bundle an adopter
    # may be expecting and will otherwise go looking for.
    bare = reserved_only_dirs(PROJECT, cfg)
    if bare:
        print(f"  note   no bundle for {', '.join(bare)} — only reserved filenames inside "
              f"(README.md, index.md, log.md), so no documents to mirror")

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
        names = mirror(src, out_dir, ctype, stamp, a.apply,
                       (cfg.get("bundle_tags") or {}).get(name))
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

    # ---- in-place bundles the build did not produce --------------------------
    # A bundle can reach the mesh two ways: this build mirrors it, or somebody wrote
    # frontmatter into their own files and named the folder in `bundles`. Only the first
    # kind was ever registered, so an in-place bundle was a member of the mesh that the
    # mesh had no concept for — and `check_bundles` rejects exactly that, with an error
    # naming the bundle rather than the reason.
    #
    # This project shipped with its own instance: `docs/decisions`, 14 concepts, excluded
    # from mirroring because the files ARE the concepts, listed in no `bundles` map, and
    # therefore validated by nothing at all for its whole life. The toy second domain in
    # `examples/warehouse` hit the same wall independently, which is how it was found.
    #
    # Registering is all that happens here. The build still never writes into an in-place
    # bundle — those files belong to whoever authored them.
    for bid, rel in sorted((cfg.get("bundles") or {}).items()).__iter__():
        if bid == mesh_name or any(b[0] == bid for b in built):
            continue
        src = (PROJECT / str(rel).removeprefix("./")).resolve()
        if not src.is_dir() or src.is_relative_to(out_root):
            continue                      # build output, or not there — not in-place
        n = sum(1 for f in src.rglob("*.md")
                if f.name not in RESERVED and is_concept(f))
        if not n:
            continue
        shown = src.relative_to(PROJECT).as_posix() if src.is_relative_to(PROJECT) else str(src)
        print(f"  in-place {n:>3}  {shown}  →  registered, not written")
        built.append((bid, shown, n))

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
