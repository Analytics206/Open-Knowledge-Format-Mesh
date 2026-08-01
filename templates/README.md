# templates/

Copy-paste starting points. Nothing here is scanned as part of this repository's mesh —
`templates/` is not listed in `okfm.json`'s `bundles`.

| File | Copy it to | Level |
|---|---|---|
| `AGENTS.md` | your project root, as whatever your agent reads (`AGENTS.md`, `CLAUDE.md`, a cursor rule) | 3 |
| `bundle/` | wherever your knowledge should live | 1 |

## `AGENTS.md` is the whole of Level 3

No installation, no runtime, no key. It states the contract in prose: read the index first,
weigh trust before relying on a concept, write drafts and never verdicts, never infer typed
relations, leave the human gate to the human.

Weaker than injection, and portable to any agent tool you already have. That trade is the
point — see spec §13.6 mode 2.

## `bundle/` is three files

`index.md` (the map), `log.md` (the changelog), and `first-concept.md` — a `Decision`
template whose sections are chosen to make the admission test hard to fail: *what was
decided*, *why*, *what was rejected*, *what would change this*.

Replace the angle-bracket placeholders. Delete the HTML comment once you have read it.

## A note for when discovery-by-convention lands

§13.5 makes any `.md` with a non-empty `type:` a concept, anywhere in a project. These
template files carry `type:` and are therefore concept-shaped by design — so `templates/`
must be in the default ignore list when convention-based scanning arrives, or every adopter
inherits four placeholder concepts on their first build.

Recorded here rather than discovered later.
