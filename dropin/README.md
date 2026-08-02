# dropin/

The Level 2 deterministic build. **Copy this folder into a project as `.okfm/` and run it.**

```bash
cp -r dropin my-project/.okfm && cd my-project
```

```bash
python .okfm/okfm.py             # the whole pipeline: build, observe, bake, validate
python .okfm/okfm.py --check     # same, but writes nothing and fails on mismatch (CI)
```

Individual steps stay runnable — `okfm.py build`, `refresh`, `view`, `check` — but one
command is the one to remember.

## What the first run does

With no configuration it finds `docs/`, gives **every folder of documents its own OKF**, adds
one for the loose files at the top, and writes a mesh OKF over all of them:

```text
my-project/
  docs/guides/          →   .okfm/guides/
  docs/architecture/    →   .okfm/architecture/
  docs/*.md             →   .okfm/docs/
                            .okfm/mesh/      ← the mesh OKF — read this first
```

Then it writes the config it used, so the first thing you edit is a file it made for you.
Config is grouped — `build`, `bundles`, `read`, `stores`, `federation`. Four keys inside
`build` control what gets read:

```json
"build": { "root": "docs", "root_files": true, "exclude": ["archive"], "include": ["adr"] }
```

`root` points somewhere other than `docs/`. **`exclude` drops a folder inside it; `include`
adds a tree outside it** — you cannot exclude your way to a directory the scan never reached,
which is why there are two keys rather than one. An included tree is scanned exactly as the
root is. `root_files: false` skips the loose documents at the top, which in many projects are
a landing page and two stubs rather than knowledge.

**Nothing else is read.** There is no scan of your project looking for files that already
carry a `type:`; a folder is in the mesh because you named it or because it sits under the
root. That keeps a first run from producing concepts out of your templates and a vendored
SDK's documentation.

Discovery runs on **every** build rather than being frozen into the config on the first one. A
folder added next month gets an OKF without anyone remembering to declare it — which is also
what makes `exclude` mean something more than "delete a line". Writing an explicit `sources`
list turns discovery off entirely; someone who wrote one meant it.

Your documents are never written to. Everything the tool produces lands under `.okfm/`, so
`rm -rf .okfm` leaves the project exactly as it was.

## The config is checked before anything reads it

```bash
python .okfm/okfm.py config
```

Every consumer of a config ignores keys it does not recognise, so a misspelled `exlude` does
not fail — it builds the wrong thing quietly. This is the step that says so:

```text
  FAIL  build.exlude
        not a key anything reads
        → did you mean `exclude`?
```

It runs first in the pipeline. It checks unknown keys, types, enums and ranges, whether the
paths exist, that `build.out` does not sit inside `build.root` (the build would read its own
output), and that a `stores` credential is a **handle** — `env:`, `vault:`, `op:` — and not
the secret itself.

It also catches the one seam in this config that reliably surprises people: **`exclude` says
what gets read, `bundles` says what the mesh is.** Exclude a folder that `bundles` still
names and nothing visible changes, because the build was never going to mirror it and every
reader still finds it by path. Same for a bundle the build has stopped writing — the folder
stays on disk and stays listed. Both now say so, and say which line to remove. Errors stop the build; warnings do not, because a folder you have not
created yet is the normal case during setup.

**There is also a form.** Open `okfm-web-ui.html` and switch to the **Config** tab: the same
rules, live, with one line of help per key. It saves through the browser's own file dialog
and runs nothing — the build stays a terminal command, which is what keeps this a folder of
scripts with no server in it.

The rules themselves live in `config_schema.py` as a table, and the bake embeds that table in
the page. One source, three readers. Two lists of what keys exist would agree until somebody
added a key to one of them, and the page would start accepting configs the build rejects.

**Re-running is safe.** The build writes only concepts nothing else has touched, judged by
`generated.by` and the presence of `verified`. A tool that eats your edits on the second run
gets deleted after the second run.

Python 3.13, **standard library only**. No install step, no requirements file. Every component
**the pipeline runs** is `needs: []` under
[DR-0008](../docs/decisions/0008-build-pipeline.md): no network, no secrets, no model.

There is exactly one exception and it is never in the pipeline: `enrich_local.py` declares
`needs: [model]` because it calls one. A workflow's set is the union of everything it invokes,
so listing it in the default run would take the whole thing out of CI on a fork's pull request.

## Files

| File | Does |
|---|---|
| `okfm.py` | One entry point. Runs the pipeline, or dispatches a single step. |
| `config_schema.py` | The config's rules, as data. Read by the validator *and* by the web UI. |
| `check_config.py` | Validates `okfm.json` before anything reads it. Runs first. |
| `build.py` | Markdown → concepts, one bundle per folder, plus the mesh OKF. |
| `okfm_core.py` | Locating and frontmatter parsing. Knows nothing about where it was installed. |
| `bootstrap.py` | Extraction — `title`, `description` — and in-place concept creation. |
| `bake_web_ui.py` | Regenerates the web UI's index from the bundles. `--check` gates CI. |
| `check_bundles.py` | Conformance, profile, strip test, predicates, links, footnotes. |
| `refresh.py` | Observes pointers, writes the observation cache, reports drift. `--check` gates CI. |
| `enrich.py` | What needs enriching and the brief for doing it. Prints work; calls no model. |
| `enrich_local.py` | Level 2+ — drafts with a model you host. The one `needs: [model]` file. |
| `guard.py` | Checks a diff wrote only fields a `[model]` pass owns. |
| `revalidate.py` | The human end: refresh a capture, add `verified`, clear the drift. |
| `telemetry.py` | Writes one run record per pipeline run. |
| `vocab/` | Controlled vocabularies — predicates and reason codes, in files rather than code. |

## Two modes

**Mirror (default).** Concepts are written into `.okfm/` and point back at your files via
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

## Drift

```bash
python okfm/refresh.py            # observe, cache, report
python okfm/refresh.py --check    # exit 1 on drift in a `stable` concept
```

**Drift is observed here and nowhere else.** Nothing on the read path resolves a pointer —
not the web UI, not an injected index, not an agent. That is what keeps reading a mesh free
([DR-0006](../docs/decisions/0006-drift-cost-and-caching.md)).

Three states, never two: `match`, `drifted`, and **`unknown`** for a pointer never observed.
Unknown renders as unknown. Defaulting it to fresh would be a stored opinion wearing a
computed one's clothes.

The cache holds **observations, not verdicts** — *this pointer hashed to X at time T* stays
true forever, which is why caching it does not violate derive-don't-store. The verdict is
recomputed by whoever reads.

Only `status: stable` concepts fail the build. A draft is expected to be out of step with its
source; that is what draft means.

**A human refreshes `okfm_captured`, never the build.** Doing it automatically would erase
the very signal drift exists to carry.

For in-place concepts — where the file *is* the concept — the body is hashed rather than the
whole file. The captured hash was taken before frontmatter existed, so comparing whole files
would report drift forever. Hashing the body gives it a useful meaning instead: *the prose
changed since the description was extracted*, which is the enrichment work list.

## Level 3

OKFM holds **no credential** at Level 3. Your agent drives OKFM, not the other way round
([DR-0009](../docs/decisions/0009-adoption-levels.md)) — so the components here print work
and check results. The reasoning is your agent's; the list and the check are arithmetic.

```bash
python okfm/okfm.py enrich --brief                       # 1. what to do, and how
#                                                          2. your agent does it
python okfm/okfm.py guard                                # 3. did it stay in its lane?
python okfm/okfm.py revalidate <path> --by human:you     # 4. you sign off
```

**Or run step 2 here — Level 2+.** `ollama pull` a model, switch it on in `okfm.json` (or on
the web UI's Config page), and OKFM drafts instead of printing:

```json
"enrich": { "enabled": true, "base_url": "http://localhost:11434", "model": "qwen3.5:9b" }
```

```bash
python okfm/okfm.py enrich-local --apply
```

Same steps 3 and 4, unchanged. **Level 2's terms — no key, no account, no bill — plus the
enrichment loop**, because OKFM drives a model you host rather than your agent driving OKFM.
Mechanically it is `needs-model` without `needs-secrets`, still in the level 3 bundle, and the
checked 2/3 boundary has not moved ([DR-0013](../docs/decisions/0013-the-local-model-variant.md)).

The model must already be pulled on that instance — nothing here downloads one. `base_url`
takes any host, so a box on your network works; that box needs `OLLAMA_HOST=0.0.0.0`, and
`okfm.py config` notes when the address stops being loopback, since that is exactly where the
local and credentialed cases part company.

It writes `description` and `tags` and restamps `generated.by`; it may not write a `needs-*`
tag, because those are the level ladder and CI reads them as fact. Nothing is written without
`--apply`, and a malformed answer is refused rather than repaired. Thinking is off and
temperature is 0, so two runs return identical text — a second pass is a no-op, not a rewrite.

A proof of concept, and labelled one: it proves the loop closes with no key, not yet that
enrichment pays for itself.

**Step 3 is what makes the human gate real.** `guard` reads the diff and fails if the pass
touched `verified`, `okfm_relations`, `status`, `type`, `title`, `sources`, or
`okfm_captured` — and fails when a field the pass *owns* changed while `generated` did not,
because content rewritten without a new provenance stamp gets clobbered by the next extraction
refresh. Until it existed, those were rules in a document.

A rebuild re-pins `okfm_captured` legitimately, so on a file the build still owns that one key
is not counted, and the run says how many it passed over. Exactly one key, on exactly that kind
of file: everything else protected is checked on build output as it is anywhere else.

A **created** file is judged on a shorter list — `verified`, and a `status` that is not
`draft` — because on a new file every field is an addition and the full list would flag all
of them. Authorship is not overwriting; arriving pre-verified is.

**Step 4 is the only thing that clears drift**, and no build does it for you. Refreshing a
capture automatically would erase the signal drift exists to carry. Naming a path and a
`human:` actor is how you assert you actually reviewed it — a `process:` actor is rejected,
because that is the backfill dishonesty §16 forbids wearing a command's clothes.

Enrichment **must** set `generated.by` to itself. That is not bookkeeping:
`bootstrap --refresh` decides what it may recompute by reading that field, so an improved
description that leaves it saying `process:okfm-bootstrap` gets silently clobbered later.
This project lost a description that way before the rule was written down.

## Telemetry

Every pipeline run writes one record to `references/telemetry/runs/` — schema version,
run id, workflow, timings, each step and its exit code. Not a concept: it does not belong
in the concept graph and would swamp it, so it sits outside the bundles and is invisible
to conformance.

`telemetry_schema` is versioned because the point is comparability. Six months of records
are an asset only if a question asked of them means the same thing across all of them, so
renaming or repurposing a field bumps the version.

Two deliberate divergences from §10.1, both explained in `telemetry.py`: records live under
the drop-in folder rather than inside a bundle (a run belongs to no single bundle), and they
are gitignored by default rather than committed (per-machine run history, not shared bundle
content — remove the ignore if your team wants it shared).

## Vocabularies

`vocab/types.yaml`, `vocab/predicates.yaml` and `vocab/reason_codes.yaml` hold the
controlled lists. They are
files rather than constants so a pack can overlay domain terms without forking core — point
`vocab_overlays` in your config at additional files and they merge by family.

**Types only warn when unknown.** Official OKF §6.2 says `type` is not centrally
registered and consumers must tolerate unknown values, so rejecting one would break
conformance and stop you inventing the type your domain needs. The list catches typos —
`Decison`, `Attested computation` — not vocabulary you meant.

**Predicates are rejected when unknown.** Typed relations drive impact analysis and drift
propagation, which read an edge as fact, so a guessed edge is worse than a missing one
(§7.3).

**Reason codes only warn when unknown**, because core ships the four codes every domain
shares and domain codes belong in packs. Failing would reject every legitimate domain code
before there is a way to declare one.

Adding a code is one line. **Changing what a code means is forbidden** — add a new one and
deprecate the old, because every historical record carrying it was written under the old
meaning.

## What the pipeline is

`okfm.py` with no arguments runs `okfm-rebuild` from
[DR-0008](../docs/decisions/0008-build-pipeline.md) with the model step left out:

    build → refresh → view → check

Enrichment is deliberately absent. It needs a model, which under DR-0008 makes any workflow
containing it `needs: [model]` and moves the whole thing to Level 3. Keeping it out is what
lets this run on a pull request from a fork with no secrets.

The pipeline stops at the first failure. A later step reading what an earlier one failed to
write reports a second, misleading problem.
