# dropin/

The Level 2 deterministic build. **Copy this folder into a project and run it.**

```bash
cp -r dropin my-project/okfm && cd my-project
```

```bash
python okfm/build.py            # dry run — says what it would do
python okfm/build.py --apply    # writes
```

It defaults to the directory it was dropped into. With no configuration it scans that
directory, reports what it found, and writes the config it used — so the first thing you
edit is a file it made for you.

Python 3.13, **standard library only**. No install step, no requirements file. Every
component is `needs: []` under [DR-0008](../docs/decisions/0008-build-pipeline.md): no
network, no secrets, no model.

## Files

| File | Does |
|---|---|
| `build.py` | The entry point. Discovers config, scans sources, writes concepts. |
| `okfm_core.py` | Locating and frontmatter parsing. Knows nothing about where it was installed. |
| `bootstrap.py` | Extraction — `title`, `description` — and in-place concept creation. |
| `bake_viewer.py` | Regenerates the viewer's index from the bundles. `--check` gates CI. |
| `check_bundles.py` | Conformance, profile, strip test, predicates, links, footnotes. |
| `vocab/` | Controlled vocabularies — predicates and reason codes, in files rather than code. |

## Two modes

**Mirror (default).** Concepts are written into `bundle/` and point back at your files via
`resource`. Your markdown is never touched.

**In-place (`--in-place`).** Frontmatter is added to your files, so they *become* the
concepts. Right when the documents are themselves the knowledge — decision records, for
instance — and wrong for a docs tree the concepts are merely *about*.

Mirror is the default because this folder gets pasted into other people's repositories.

## What it can and cannot fill

Every field it writes is **extracted or computed**, never drafted:

| Filled | How |
|---|---|
| `title` | first `# H1`, else the filename de-slugged |
| `description` | a lead blockquote if there is one, else the first real paragraph |
| `resource` | relative path back to the source |
| `okfm_captured` | sha256 of the source, as seen now |

Left empty, because filling them needs a model or a person: `tags`, prose sections,
`okfm_relations` (never inferred — a wrong typed edge is worse than a missing one), and
`verified` (never machine, ever).

Everything lands `status: draft` with no `verified` entry. That is accurate, not a
placeholder: extraction produced it and nobody has reviewed it.

## Extraction rules, and why each exists

Each was added because the previous version got something wrong on a real corpus:

- **Skip lists, tables, headings, and fences.** Decision records open with a
  `- **Status:**` block that would otherwise be swallowed whole.
- **A lead blockquote wins.** The first block after the H1 is conventionally a summary.
  Further down it is a pull-quote, so position decides rather than a flag.
- **Bold-led chunks are judged by length.** Short means a metadata header
  (`**Status:** draft`); long means an ordinary paragraph that happens to open in bold.
  Rejecting all of them silently discarded real opening paragraphs.
- **Paragraphs ending in `:` are skipped.** They introduce a list or a quote, and read as
  a fragment torn from its context.

`--refresh` recomputes descriptions on concepts this tool created — identified by
`generated.by` naming `process:okfm-bootstrap`. Anything a person or a model touched is
left alone.

## Vocabularies

`vocab/predicates.yaml` and `vocab/reason_codes.yaml` hold the controlled lists. They are
files rather than constants so a pack can overlay domain terms without forking core — point
`vocab_overlays` in your config at additional files and they merge by family.

**Predicates are rejected when unknown.** Typed relations drive impact analysis and drift
propagation, which read an edge as fact, so a guessed edge is worse than a missing one
(§7.3).

**Reason codes only warn when unknown**, because core ships the four codes every domain
shares and domain codes belong in packs. Failing would reject every legitimate domain code
before there is a way to declare one.

Adding a code is one line. **Changing what a code means is forbidden** — add a new one and
deprecate the old, because every historical record carrying it was written under the old
meaning.

## Still to come

`build.py` writes concepts but does not yet bake the viewer or validate in one pass; run
`bake_viewer.py` and `check_bundles.py` after it. Phase 1 folds them into one command and
adds the drift observation cache from
[DR-0006](../docs/decisions/0006-drift-cost-and-caching.md).
