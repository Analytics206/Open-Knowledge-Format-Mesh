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

## A note for when discovery-by-convention lands

§13.5 makes any `.md` with a non-empty `type:` a concept, anywhere in a project. What is
built today is discovery by *folder* — the build reads `docs/` and creates concepts from
documents — so nothing currently sweeps a project looking for files that already carry a
`type:`.

These template files do carry one, and are concept-shaped by design. So `templates/` must be
in the default ignore list if convention-based scanning arrives, or every adopter inherits
four placeholder concepts on their first build.

Recorded here rather than discovered later.
