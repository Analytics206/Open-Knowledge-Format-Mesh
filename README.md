# OKFM — the OKF Mesh

A distributable knowledge-mesh scaffolding for [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundles.

OKFM records **why a project believes what it believes** — the evidence that changed what it
knows or does — as git-tracked markdown, and hands it to an agent as a compact index before
the agent starts work. It is a profile over OKF v0.2 plus the scaffolding that runs it. It
does not fork the format: strip every `okfm_` key and what remains is still a valid OKF
bundle.

---

## Four levels. Pick one.

Each level is cumulative, and each is a complete usable process — not a teaser for the next.
Stop wherever the value stops being worth the cost.

| | You get | You supply | Never needed |
|---|---|---|---|
| **1 — the format** | spec, guide, viewer, examples | a browser | anything |
| **2 — the process** | a drop-in folder that builds a bundle from your files | a runtime | a key, a provider, a model |
| **3 — enrichment** | the full enrichment lifecycle | your own agent, LLM, or MCP | a credential held by OKFM |
| **4 — the suite** | providers, packs, federation, workflows | a key, a provider, a config | — |

The **level 2 / level 3 line is the model line**: nothing shipped at level 2 may require an
LLM, and that is enforced in CI rather than promised here.

Pointing your coding agent at this repository and asking it for whatever you want works from
level 1. It is not a level.

## Status: Phase 0 — specification and guide

**There is no CLI yet.** Nothing in this repository executes. What exists today is the
design, a working example bundle, and a viewer for it.

| | State |
|---|---|
| Specification, rationale, roadmap, prior art | ✅ written |
| `okfm-guide/` — a real OKF bundle documenting OKFM | ✅ 10 concepts |
| `okfm-viewer.html` — graph, closure ledger, health panel | ✅ works offline |
| Level 2 — the deterministic drop-in build | ⬜ Phase 1 |
| Levels 3–4 — enrichment, providers, packs, federation | ⬜ Phase 2+ |

The [roadmap](docs/roadmap.md) has the phases and exit criteria; [decisions](docs/decisions/index.md)
has what is settled and what is still open.

---

## Level 1 — see it now

```bash
git clone <this-repo> && cd okfm
```

Open `okfm-viewer.html` in a browser. No server, no build, no dependencies.

You will see the bundled guide as a graph, colored by concept type, with a health panel and
a closure ledger. Every concept reads *unverified* — that is honest, not broken. Nobody has
reviewed those files, and inventing a `verified` entry is the one thing the specification
forbids outright.

Then read [`okfm-guide/index.md`](okfm-guide/index.md). It is documentation and a working
example at the same time: every file in that folder is a legal OKF concept, so the guide
teaches by *being* the thing it describes.

Delete it whenever you like — `rm -rf okfm-guide/` is the entire procedure.

## Level 2 — paste and run *(Phase 1)*

Copy the folder into your project and run it. It defaults to the location it sits in, scans
the files around it, and writes a bundle.

```bash
cp -r okfm/dropin my-project/okfm && cd my-project
```

```bash
python okfm/build
```

Open the viewer and your mesh is there. Unenriched, because no model was involved —
descriptions are **extracted** from your files rather than written, which means they can be
unhelpful but never wrong about what your source says. Drift detection works immediately,
because the captured hashes are real.

The first run also **writes the config it used**, listing what it scanned. Most projects have
many folders under `docs/` and want concepts for only some, so pruning scope is deleting a
line rather than reading documentation about scoping.

Dependencies are permitted here. A key is not.

## Level 3 — enrichment *(Phase 2)*

Your agent, LLM, or MCP server fills in what extraction cannot: summaries, tags, section
purposes. Level 2 detects what went stale, level 3 drafts the prose, you promote it.

**OKFM holds no credential at this level.** Your agent drives OKFM; you are already
authenticated in your own tool. Drafts land as `status: draft` with no `verified` entry, and
stop there until a human says otherwise.

## Level 4 — the full suite *(Phase 3+)*

```bash
okfm init --pack warehouse
```

```bash
okfm validate
```

```bash
okfm index
```

Providers, packs, federation, the loop-family workflows, and the benchmark. This is where a
key comes in — two adapters, OpenAI-compatible and Anthropic, plus a config list of
endpoints, so adding a provider is a config line rather than code. Local models via Ollama
are a first-class path, not a checkbox: enrichment is short, bounded, repetitive work that a
small local model handles well.

**The bar this project holds itself to** at this level: a competent stranger, given only this
README, reaches a running mesh answering one real question about their own project in under
an hour, editing configuration and concepts only — never core.

---

## Repository map

```text
spec/okfm-v0.2.1.md      normative — what makes a bundle a legal OKFM bundle
docs/rationale.md        why the system is shaped this way
docs/roadmap.md          assets, proving grounds, phases, open questions, measures
docs/prior-art.md        the ecosystem, and the measurements that went against us
docs/decisions/          dated decision records
okfm-guide/              the bundled guide: documentation AND a real bundle
okfm-viewer.html         read-only viewer — opens from disk, for people not agents
okfm.json                this repo's own config; it self-hosts the guide
examples/minimal/        what an adopter's config looks like instead
scripts/                 Phase 0 consistency checks, runnable today
```

Section numbers are **global across the four documents** and preserved from the unified
specification, so a reference like §12.3 means the same thing everywhere. Each document opens
with a map saying where every section lives.

## What OKFM adds to the baseline

OKF v0.2 already brings provenance, trust tiers, lifecycle, staleness dates, and attested
computation. OKFM adds six things and deliberately no more:

| Addition | The question it answers |
|---|---|
| The loop family | Why did we decide that? |
| Federation | Who owns this, and what did they say when we disagreed? |
| Content-based drift | Has the thing this depends on actually changed? |
| Perspectives, declared-vs-observed | Whose definition, and does the code agree with the policy? |
| Typed relations | *How* are these two concepts related? |
| Versioned telemetry | What actually happened on that run? |

## Five commitments worth knowing before you read further

**Write down what the code cannot say.** A concept that restates its source is a maintenance
liability that measurably buys nothing — and can lose you an answer the source would have
given. This is the one rule here derived from a measurement that went *against* the premise.
See [prior art](docs/prior-art.md) §21.1.

**Derive verdicts, never store them.** Trust tier, staleness, drift, and reconciliation
status are computed at read time from stored signals. A stored verdict is a stored opinion
with an expiry date.

**No duplicate knowledge.** Knowledge lives in exactly one place and is referenced everywhere
else. Rendered views, exports, and caches are derivations, marked as such and never edited.
This is why the viewer never embeds concept bodies.

**Extraction is not drafting.** Copying a sentence that already exists cannot invent; writing
a new one can. That distinction is what makes level 2 possible with no model anywhere.

**Anything that cannot be handed to a stranger does not belong in core.** Core carries no
domain words, and CI enforces it by grepping for them.

## Contributing

Too early. The specification is stable enough to read and argue with; the code does not
exist. If you have opinions about §19's open questions, or about anything still marked
**proposed** in [decisions](docs/decisions/index.md), those are the live ones.

## License

MIT — see [LICENSE](LICENSE). OKFM is an independent project, not endorsed by or affiliated
with Google. See [NOTICE](NOTICE) for attribution of the OKF specification (Apache-2.0) and
of the prior art this design draws on.
