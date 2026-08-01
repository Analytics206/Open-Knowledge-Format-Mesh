# OKFM — the OKF Mesh

A knowledge-mesh scaffolding for [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundles.

OKFM records **why a project believes what it believes** — the reasoning behind a decision,
the alternative that was rejected, the definition a number actually uses — as git-tracked
markdown, and hands it to an agent before the agent starts work.

It is a profile over OKF v0.2 plus the tooling that runs it. It does not fork the format:
strip every `okfm_` key and what remains is still a valid OKF bundle.

---

## Four levels

Each level includes the one below it. Stop wherever the value stops being worth the cost.

| | What you do | What you need |
|---|---|---|
| **1 — the format** | Download it. Open the viewer. Read the guide. | a browser |
| **2 — the build** | Paste a folder into your project and run it. | Python 3.13 |
| **3 — enrichment** | Let your own agent fill in what extraction cannot. | an agent you already use |
| **4 — the suite** | Providers, packs, federation, workflows. | an API key |

Levels 1 and 2 never need a model or a key. That boundary is enforced in CI, not promised
here.

You can also just point your coding agent at this repository and ask it for whatever you
want. That works from level 1 and needs nothing from us.

## Status

Early Phase 1. The specification is stable enough to build against, the deterministic tooling
runs, and there is no CLI yet.

| | |
|---|---|
| Specification, rationale, roadmap, prior art | ✅ |
| The mesh — registry, guide, decision records | ✅ 3 bundles, 26 concepts |
| `okfm-viewer.html` — graph, closure ledger, health panel | ✅ works offline |
| `templates/AGENTS.md` — the level 3 agent contract | ✅ |
| `dropin/` — bootstrap, bake, validate | 🟡 runs; not yet a paste-and-go folder |
| `okfm` CLI, resolvers, drift cache | ⬜ Phase 1 |
| Enrichment, providers, packs, federation | ⬜ Phase 2+ |

See the [roadmap](docs/roadmap.md) for phases, and [decisions](docs/decisions/index.md) for
what is settled and what is open.

---

## Level 1 — download it

```bash
git clone https://github.com/Analytics206/Open-Knowledge-Format-Mesh
```

Open `okfm-viewer.html` in a browser. No server, no build, no dependencies.

You get the mesh as a graph, colored by concept type, with a health panel and a closure
ledger. Then read [`okfm-guide/index.md`](okfm-guide/index.md) — every file in that folder is
a legal OKF concept, so the guide demonstrates the format by being written in it.

Delete the guide whenever you like: `rm -rf okfm-guide/`.

## Level 2 — paste and run *(Phase 1)*

Copy the folder into your project and run it. It defaults to where it sits, scans the files
around it, and writes a bundle.

```bash
cp -r okfm/dropin my-project/okfm && cd my-project
```

```bash
python okfm/build
```

Descriptions are **extracted** from your files rather than written, so they can be unhelpful
but never wrong about what your source says. Everything lands `status: draft` with no
`verified` entry, because nobody has reviewed it. Drift detection works from the first build,
because the captured hashes are real.

The first run writes the config it used, listing what it scanned — most projects have many
folders under `docs/` and want concepts for only some, so pruning is deleting a line.

Python 3.13, standard library only. No install step.

## Level 3 — enrichment *(Phase 2)*

Your agent, LLM, or MCP server fills in what extraction cannot: summaries, tags, section
purposes. Level 2 detects what went stale, level 3 drafts the prose, you approve it.

OKFM holds no credential here — your agent drives OKFM, and you are already authenticated in
your own tool. Drafts stop at `status: draft` until a human says otherwise.

The whole contract is one file: [`templates/AGENTS.md`](templates/AGENTS.md). Copy it into
your project as whatever your agent reads.

## Level 4 — the full suite *(Phase 3+)*

```bash
okfm init --pack warehouse && okfm validate && okfm index
```

Providers, packs, federation, the loop-family workflows, and the benchmark. Two adapters —
OpenAI-compatible and Anthropic — plus a config list of endpoints, so adding a provider is a
config line rather than code. Local models via Ollama are a supported path: enrichment is
short, bounded, repetitive work that a small local model handles well.

---

## Repository map

```text
spec/okfm-v0.2.1.md      normative — what makes a bundle a legal OKFM bundle
docs/rationale.md        why the system is shaped this way
docs/roadmap.md          proving grounds, phases, open questions, success measures
docs/prior-art.md        the ecosystem, and the measurements that went against us

okfm-registry/           the mesh map — one OKF Member concept per bundle
okfm-guide/              level 1 — documentation, and a real bundle
docs/decisions/          why this project is shaped the way it is — also a bundle

okfm-viewer.html         read-only viewer — opens from disk, for people not agents
okfm.json                this repo's config; it self-hosts its own mesh
templates/               AGENTS.md and a starter bundle — copy these
examples/minimal/        an adopter-shaped config
dropin/                  the deterministic build, runnable today
.github/workflows/       CI — no secrets, runs on forks
```

The three bundles are a working mesh rather than a demonstration. They have genuinely
different change cadences — a guide change means the format moved; a decision is appended
weekly — which is the §12.1 ownership seam rather than a split by size. More bundles join as
levels ship.

Section numbers are global across the four documents and preserved from the unified
specification, so `§12.3` means the same thing everywhere. Each document opens with a map
saying where every section lives.

## What OKFM adds to OKF

OKF v0.2 brings provenance, trust tiers, lifecycle, staleness dates, and attested
computation. OKFM adds six things and deliberately no more:

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
a concept summarized a validator and the agent stopped there. See
[prior art](docs/prior-art.md) §21.1.

**Derive verdicts, never store them.** Trust and staleness are computed when read. Drift is
observed during the build and cached. A stored verdict is a stored opinion with an expiry
date.

**No duplicate knowledge.** Knowledge lives in one place and is referenced everywhere else.
Rendered views, exports, and caches are derivations, never edited. This is why the viewer
never embeds concept bodies.

**Extraction is not drafting.** Copying a sentence that already exists cannot invent; writing
a new one can. That distinction is what makes level 2 work with no model.

**No domain words in code.** Enforced by CI, so the tooling stays portable while it is
developed against specific domains.

## Contributing

Early. The specification is stable enough to read and argue with; most of the implementation
does not exist. The live questions are §19 in the [roadmap](docs/roadmap.md) and anything
marked **proposed** in [decisions](docs/decisions/index.md).

## License

MIT — see [LICENSE](LICENSE). OKFM is an independent project, not endorsed by or affiliated
with Google. See [NOTICE](NOTICE) for attribution of the OKF specification (Apache-2.0) and
the prior art this design draws on.
