# templates/

Copy-paste starting points. Nothing here is scanned as part of this repository's mesh —
`templates/` is not listed in `okfm.json`'s `bundles`.

| File | Copy it to | Level |
|---|---|---|
| `AGENTS.md` | your project root, as whatever your agent reads (`AGENTS.md`, `CLAUDE.md`, a cursor rule) | 3 |
| `bundle/` | `.okfm/<name>/`, if you are writing a bundle by hand | 1 |

## `AGENTS.md` is the whole of Level 3

No install, no runtime, no key. It states the contract in prose: read the mesh first, weigh
trust before relying on a concept, write drafts and never verdicts, never infer typed
relations, leave the human gate to the human.

Weaker than injection, and portable to any agent tool you already have. That trade is the
point — see spec §13.6 mode 2.

## `bundle/` is three files

`index.md` (the map), `log.md` (the changelog), and `first-concept.md` — a `Decision`
template whose sections are chosen to make the admission test hard to fail: *what was
decided*, *why*, *what was rejected*, *what would change this*.

Replace the angle-bracket placeholders. Delete the HTML comment once you have read it.

**You usually will not need this.** The drop-in build writes bundles for you, one per folder
of documents, and hand-authoring is for the case where a bundle has no source documents —
the way this repository's guide and mesh bundles do. If you are pointing OKFM at an existing
`docs/` tree, run the build instead.

## Why this folder is safe to copy

These files carry a `type:` — they are concept-shaped by design, which is what makes them
templates rather than prose about templates. In a tool that swept a project looking for
frontmatter, that would mean every adopter inherited four placeholder concepts on their
first build.

Nothing sweeps. A build reads `build.root` and whatever `build.include` names, and nothing
else (§13.5), so a `templates/` folder is invisible until somebody points at it. That is the
concrete reason the sweep was rejected rather than deferred: a scan wide enough to be
convenient is wide enough to pick up files that only *look* like knowledge.
