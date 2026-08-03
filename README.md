# OKFM — the OKF Mesh

A knowledge-mesh scaffolding for [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundles.

OKFM records **why a project believes what it believes** — the reasoning behind a decision,
the alternative that was rejected, the definition a number actually uses — as git-tracked
markdown, and hands it to an agent before the agent starts work.

It is a profile over OKF v0.2 plus the tooling that runs it. It does not fork the format:
strip every `okfm_` key and what remains is still a valid OKF bundle.

---

## How it sits in a project

```text
my-project/
  docs/                  your documents. OKFM reads these and never writes to them.
    guides/
    architecture/
  .okfm/                 the mesh OKFM wrote. Delete it and the project is as it was.
    mesh/                  read this first — an OKF whose concepts are the other OKFs
    docs/                  an OKF for the loose files at the top of docs/
    guides/                an OKF for docs/guides/
    architecture/          an OKF for docs/architecture/
  okfm/                  the tool. Replace this folder to upgrade; the mesh survives.
  okfm.json              your configuration. The build writes a first one for you.
```

**The tool and the mesh are separate folders on purpose.** Put them together and there is no
way to replace one without risking the other — see [Level 2](#level-2--paste-and-run).

**Every folder of documents gets its own OKF, and one OKF over them says which to read.** That
is the default with no configuration: `docs/` is found, each subfolder becomes a bundle, the
loose files at the top become one, and the mesh indexes them.

Two keys change what gets read, and they are the config worth knowing: **`exclude` drops a
folder inside the root, `include` adds a tree outside it** — an `adr/` at the top of the
project, a sibling package's docs. Nothing else is read. There is no scan of your repository
hunting for files that already carry a `type:`, so a first run cannot turn your templates and
a vendored SDK's documentation into concepts.

## One entry point instead of several

`.okfm/mesh/` is the OKF you read first. Its concepts are the *other* OKFs, and each one
carries the questions its bundle answers:

```yaml
okfm_member:
  answers:
    - how do I use my own key and provider
    - what may an agent write, and what may it not
    - how do I clear drift
```

Point an agent at that one file and it finds the rest itself, instead of you naming four
bundles up front and hoping you picked the right ones. Ask *"where do I read about using my
own key?"* and the mesh answers with a path.

**`answers` is the one thing you write yourself.** The build creates every member and leaves
the list empty, because what a bundle is *for* is a judgement no process can make — and a
guessed entry sends an agent to the wrong bundle with confidence. Three or four questions per
bundle, in the words somebody would actually ask them, is the whole job.

It is a **directory, not an orchestrator**. Nothing in it dispatches a question, calls a
member, or merges an answer — your agent does that, reading the map. A registry that
orchestrated would have to decide on behalf of bundles it does not own, which is the central
authority federation exists to avoid.

## Three levels, and a plus

Each includes the one below it. Stop wherever the value stops being worth the cost.

| | What you do | What OKFM needs from you |
|---|---|---|
| **1 — view** | Download it. Open the web UI. Read the guide. | a browser |
| **2 — build** | Paste one folder into your project and run one command. | Python 3.13 |
| **2+ — local drafting** | Point it at Ollama on your own hardware and let it draft. | a machine that runs a model |
| **3 — enrichment** | Let a model fill in what extraction cannot. | an agent you already use |

**Level 2+ keeps level 2's terms — no key, no account, no bill — and adds the enrichment
loop.** `ollama pull`, one switch in the config, one command. It is the enrichment machinery
reachable at level 2's price, which is why it gets a `+` rather than a number of its own.

Level 3 proper has three variants, differing by who drives and who holds a key:

| Variant | Who drives | Who holds a key |
|---|---|---|
| your agent | your agent drives OKFM | your agent — OKFM holds none |
| **local (2+)** | OKFM drives a model you host | **nobody** |
| credentialed | OKFM drives a hosted provider | OKFM |

The credentialed one carries what follows from acting unattended: providers, packs,
federation's negotiation half, the console app, the benchmark.

The `+` is exact rather than decorative. Under the hood the component declares `needs: [model]`
and sits in the level 3 bundle, and **nothing at level 2 may declare `model`** — that boundary
is still checked in CI and still where it was. The ladder measures what OKFM asks of you before
you can start; the name measures what it costs you. Those were the same number until a model
became free ([DR-0013](docs/decisions/0013-the-local-model-variant.md)).

Levels 1 and 2 never need a model or a key. That is enforced in CI by
[`dev/check_levels.py`](dev/check_levels.py), which reads the `needs-*` tag on every
component and fails when one exceeds what its level allows.

You can also just point your coding agent at this repository and ask it for whatever you want.
That works from level 1 and needs nothing from us.

## Status

Phase 1 closed, Phase 2 in progress. The specification is stable enough to build against and
the deterministic tooling runs. The commands are there — `validate`, `index`, `build`,
`view`, `refresh`, `enrich`, `guard`, `revalidate` — reached as `python okfm/okfm.py <name>`.
What is missing is a packaged `okfm` on your PATH, which needs an install step that
[DR-0001](docs/decisions/0001-runtime-and-packaging.md) deliberately does not have yet.

| | |
|---|---|
| Specification, rationale, roadmap, prior art | ✅ |
| The mesh — 7 bundles, 67 concepts, self-hosted | ✅ |
| `okfm-web-ui.html` — graph, closure ledger, health panel, config editor | ✅ works offline |
| `dropin/` — paste into a project, build a mesh | ✅ level 2, deterministic |
| Config validation — one rule table, terminal and browser | ✅ |
| `templates/AGENTS.md`, enrich / guard / revalidate | ✅ level 3 |
| `enrich-local` — the loop on Ollama, no key, no bill | ✅ level 2+, proof of concept |
| Benchmark harness | ✅ first run recorded — 8 real questions, no measurable gap |
| Domain packs — a second domain on config alone | ✅ `packs/warehouse`, checked every CI run |
| Distribution test (§13.7) — a stranger, with only this page | ◐ the commands run; whether they *read* is untested |
| `okfm index` — what an agent would actually be handed | ✅ budgeted, and says what it cut |
| Packaged `okfm` command, live resolvers, console app | ⬜ Phase 2 |
| Providers, federation's negotiation half | ⬜ Phase 3+ |

See the [roadmap](docs/roadmap.md) for phases, and [decisions](docs/decisions/index.md) for
what is settled and what is open.

---

## Level 1 — download it

```bash
git clone https://github.com/Analytics206/Open-Knowledge-Format-Mesh
```

Open `okfm-web-ui.html` in a browser. No server, no build, no dependencies.

You get the mesh as a graph, coloured by concept type, with a health panel and a closure
ledger. Then read [`.okfm/guide/index.md`](.okfm/guide/index.md) — every file in that folder
is a legal OKF concept, so the guide demonstrates the format by being written in it.

Delete the guide whenever you like: `rm -rf .okfm/guide/`.

## Level 2 — paste and run

```bash
cp -r Open-Knowledge-Format-Mesh/dropin my-project/okfm
cp Open-Knowledge-Format-Mesh/okfm-web-ui.html my-project/
cd my-project
```

**Two things, not one.** The viewer sits at the download's root rather than inside `dropin/`,
because it is the whole of level 1 and does not belong to the build. Skip it and the build
still produces a valid mesh — it says so and carries on — you just have nothing to open.

```bash
python okfm/okfm.py
```

It finds `docs/`, builds one OKF per folder plus a mesh OKF over them, and writes the config
it used — so the first thing you edit is a file it made for you rather than a blank page.

That config is **validated before anything reads it**. Misspell a key and you get
*"not a key anything reads — did you mean `exclude`?"* rather than a build that quietly does
something else. The same rules drive a form in the web UI's **Config** tab, because they are
one table read by both.

Descriptions are **extracted** from your files rather than written, so they can be unhelpful
but never wrong about what your source says. Everything lands `status: draft` with no
`verified` entry, because nobody has reviewed it. Drift detection works from the first build,
because the captured hashes are real.

Re-running is safe: the build writes only concepts nothing else has touched.

Python 3.13 or newer, standard library only. No install step.

### Three directories, and why they are three

| | Holds | Yours to delete |
|---|---|---|
| `okfm/` | the tool — fourteen modules and the core vocabulary | any time; the mesh survives |
| `.okfm/` | the mesh the build wrote | any time; a rebuild recreates all but your enrichment |
| `okfm.json` | your configuration | it is the file you edit |

**Upgrading is a delete and a copy**, and it is safe precisely because those are separate:

```bash
rm -rf my-project/okfm && cp -r Open-Knowledge-Format-Mesh/dropin my-project/okfm
```

Your config and every concept you enriched or verified are untouched, because neither lives
in the folder being replaced.

> Earlier versions of this page said `cp -r .../dropin my-project/.okfm`, putting the tool,
> the config and the mesh in one directory. It works on day one and traps you on day two:
> running that same command again does not upgrade anything — it nests a second copy inside
> and reports nothing — and deleting first takes every enriched concept with it. The build
> now says so out loud if it finds that arrangement. Both still work; only one has an
> upgrade path.

## Level 3 — enrichment

Your agent, LLM, or MCP server fills in what extraction cannot: summaries, tags, section
purposes. Level 2 detects what went stale, level 3 drafts the prose, you approve it.

```bash
python okfm/okfm.py enrich                          # what needs work, and why
#                                                      your agent does it
python okfm/okfm.py guard                           # did it stay in its lane?
python okfm/okfm.py revalidate <path> --by human:you
```

OKFM holds no credential here — your agent drives OKFM, and you are already authenticated in
your own tool. Drafts stop at `status: draft` until a human says otherwise.

The whole contract is one file: [`templates/AGENTS.md`](templates/AGENTS.md). Copy it into
your project as whatever your agent reads.

## Level 2+ — local drafting, still no key and no bill

Don't have an agent to point at it, or don't want to spend one on this? Run the model yourself.

```bash
ollama pull qwen3.5:9b
```

Switch it on in `okfm.json`, or on the **Config** page of the web UI:

```json
"enrich": { "enabled": true, "base_url": "http://localhost:11434", "model": "qwen3.5:9b" }
```

```bash
python okfm/okfm.py enrich-local            # what it would write
python okfm/okfm.py enrich-local --apply    # write it
```

Then `guard` and `revalidate` exactly as above — the model moved onto your machine and nothing
else moved at all. Enrichment is short, bounded, repetitive work, which is the shape a small
local model handles well and the shape where a key is most annoying to require.

**The model must already be pulled on that Ollama instance** — nothing here downloads one.
`base_url` takes any host, so a box on your network works too; that box needs
`OLLAMA_HOST=0.0.0.0`, and `okfm.py config` will note that the address is no longer loopback.

`enrich_local.py` is the one component in `dropin/` that declares `needs: [model]`, and it is
deliberately kept out of the pipeline so the default run stays runnable on a fork's pull
request. It writes `description` and `tags`; it may not write a `needs-*` tag, because those
are the level ladder and CI reads them as fact. Thinking is disabled and temperature is 0, so
two runs return identical text.

**Treat this as a proof of concept.** It proves the loop closes with no key and no bill. It
does not yet prove enrichment is worth it — that needs a corpus that extracts badly, a model
that fits your machine, and the benchmark rather than a few descriptions read by eye. First
reading on 8 GB of VRAM: honest, deterministic, and slightly worse than descriptions already
written by hand.

## Level 3, credentialed *(Phase 3+)*

Providers, packs, federation's negotiation half, the console app, and the benchmark. Two
adapters — OpenAI-compatible and Anthropic — plus a config list of endpoints, so adding a
provider is a config line rather than code.

The direction reverses at level 2+ — OKFM drives the model instead of your agent driving
OKFM — and the **key** appears only here, which is the whole difference between the two.
`okfm.py config` warns when `enrich.base_url` stops being loopback, because that is the moment
the two become hard to tell apart from the config alone.

---

## Repository map

```text
.okfm/                   the mesh — every bundle this repository publishes
  mesh/                  read first — one OKF Member concept per bundle, with what it answers
  level-1-view/          ┐
  level-2-build/         │ one OKF per adoption level, built from docs/okfm-guide/
  level-3-enrich/        ┘
  docs/                  the loose documents at the top of docs/
  guide/                 the format, and a bundle that demonstrates it

docs/                    the documents the mesh is built from
  okfm-guide/            raw material for the three level bundles
  rationale.md           why the system is shaped this way
  roadmap.md             phases, open questions, success measures
  prior-art.md           the ecosystem, and the measurements that went against us
  decisions/             why this project is shaped the way it is — also a bundle

spec/okfm-v0.2.1.md      normative — what makes a bundle a legal OKFM bundle
dropin/                  the level 2 build — paste this into a project as .okfm/
benchmark/               the benchmark harness — prototype
okfm-web-ui.html         read-only, opens from disk — for people, not agents
okfm.json                this repository's config; it self-hosts its own mesh
templates/               AGENTS.md and a starter bundle — copy these
dev/                     this repository's own maintenance scripts
```

Section numbers are global across the four specification documents and preserved from the
unified original, so `§12.3` means the same thing everywhere. Each document opens with a map
saying where every section lives.

## Two rules about where things live

**Mirrored bundles live in `.okfm/`. In-place bundles live with their sources.**
`docs/decisions/` is in place — those files *are* the concepts — so burying them in a hidden
folder would trade away the one thing they are good for. The mesh registers both by path.

**Nothing generated is ever edited.** The web UI's index, the master OKF, and the drift cache
are all regenerated by the build and fail CI when the committed copy disagrees. A map
maintained by hand disagrees with its territory eventually, and the disagreement is silent.

## What OKFM adds to OKF

OKF v0.2 brings provenance, trust tiers, lifecycle, staleness dates, and attested computation.
OKFM adds six things and deliberately no more:

| Addition | The question it answers |
|---|---|
| The loop family | Why did we decide that? |
| Federation | Who owns this, and what did they say when we disagreed? |
| Content-based drift | Has the thing this depends on actually changed? |
| Perspectives, declared-vs-observed | Whose definition, and does the code agree with the policy? |
| Typed relations | *How* are these two concepts related? |
| Versioned telemetry | What actually happened on that run? |

## Design commitments

**Write down what the code cannot say.** A concept that restates its source is a maintenance
liability that buys nothing measurable, and it can cost you an answer the source would have
given. This rule comes from a published experiment where the bundle *lost* a question because
a concept summarised a validator and the agent stopped there. See
[prior art](docs/prior-art.md) §21.1.

**Derive verdicts, never store them.** Trust and staleness are computed when read. Drift is
observed during the build and cached. A stored verdict is a stored opinion with an expiry date.

**No duplicate knowledge.** Knowledge lives in one place and is referenced everywhere else.
Rendered views, exports, and caches are derivations, never edited. This is why the web UI never
embeds concept bodies.

**Extraction is not drafting.** Copying a sentence that already exists cannot invent; writing a
new one can. That distinction is what makes level 2 work with no model.

**No domain words in code.** Enforced by CI, so the tooling stays portable while it is
developed against specific domains.

## Contributing

Early. The specification is stable enough to read and argue with; much of the implementation
does not exist. The live questions are §19 in the [roadmap](docs/roadmap.md) and anything
marked **proposed** in [decisions](docs/decisions/index.md).

## License

MIT — see [LICENSE](LICENSE). OKFM is an independent project, not endorsed by or affiliated
with Google. See [NOTICE](NOTICE) for attribution of the OKF specification (Apache-2.0) and the
prior art this design draws on.
