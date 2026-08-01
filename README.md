# OKFM — the OKF Mesh

A distributable knowledge-mesh scaffolding for [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundles.

OKFM records **why a project believes what it believes** — the evidence that changed
what it knows or does — as git-tracked markdown, and hands it to an agent as a compact
index before the agent starts work. It is a profile over OKF v0.2 plus the scaffolding
that runs it. It does not fork the format: strip every `okfm_` key and what remains is
still a valid OKF bundle.

---

## Status: Phase 0 — specification and guide

**There is no CLI yet.** Nothing in this repository executes. What exists today is the
design, a working example bundle, and a viewer for it.

| | State |
|---|---|
| Specification, rationale, roadmap, prior art | ✅ written |
| `okfm-guide/` — a real OKF bundle documenting OKFM | ✅ 10 concepts |
| `okfm-viewer.html` — graph, closure ledger, health panel | ✅ works offline |
| `okfm validate` / `index` / `refresh` / `view` | ⬜ Phase 1 |
| Resolvers, drift detection, federation, packs | ⬜ Phase 2+ |

The [roadmap](docs/roadmap.md) has the phases and their exit criteria.

## See it now

```bash
git clone <this-repo> && cd okfm
```

Open `okfm-viewer.html` in a browser. No server, no build, no dependencies.

You will see the bundled guide as a graph, colored by concept type, with a health
panel and a closure ledger. Every concept in it reads *unverified* — that is honest,
not broken. Nobody has reviewed those files yet, and inventing a `verified` entry is
the one thing the specification forbids outright.

Then read [`okfm-guide/index.md`](okfm-guide/index.md). It is documentation and a
working example at the same time: every file in that folder is a legal OKF concept, so
the guide teaches by *being* the thing it describes.

Delete it whenever you like — `rm -rf okfm-guide/` is the entire procedure.

## What the quickstart will be

Once Phase 1 lands, standing up a mesh on your own project is configuration only:

```bash
okfm init --pack warehouse
```

```bash
okfm validate
```

```bash
okfm index
```

`init` writes `okfm.json`, an `index.md`, a `log.md`, and one starter concept.
`validate` is green on an empty mesh. `index` shows you exactly what an agent would be
handed — usually the more interesting answer of the two.

**The bar this project holds itself to:** a competent stranger, given only this README,
reaches a running mesh answering one real question about their own project in under an
hour, editing configuration and concepts only — never core.

## Repository map

```text
spec/okfm-v0.2.1.md      normative — what makes a bundle a legal OKFM bundle
docs/rationale.md        why the system is shaped this way
docs/roadmap.md          assets, proving grounds, phases, open questions, measures
docs/prior-art.md        the ecosystem, and the measurements that went against us
docs/decisions/          dated decision records
okfm-guide/              the bundled guide: documentation AND a real bundle
okfm-viewer.html         the mesh viewer — read-only, for people not agents
okfm.json                this repo's own config; it self-hosts the guide
examples/minimal/        what an adopter's config looks like instead
```

Section numbers are **global across the four documents** and preserved from the
unified specification, so a reference like §12.3 means the same thing everywhere. Each
document opens with a map saying where every section lives.

## What OKFM adds to the baseline

OKF v0.2 already brings provenance, trust tiers, lifecycle, staleness dates, and
attested computation. OKFM adds six things and deliberately no more:

| Addition | The question it answers |
|---|---|
| The loop family | Why did we decide that? |
| Federation | Who owns this, and what did they say when we disagreed? |
| Content-based drift | Has the thing this depends on actually changed? |
| Perspectives, declared-vs-observed | Whose definition, and does the code agree with the policy? |
| Typed relations | *How* are these two concepts related? |
| Versioned telemetry | What actually happened on that run? |

## Four commitments worth knowing before you read further

**Write down what the code cannot say.** A concept that restates its source is a
maintenance liability that measurably buys nothing — and can lose you an answer the
source would have given. This is the one rule here derived from a measurement that
went *against* the premise. See [prior art](docs/prior-art.md) §21.1.

**Derive verdicts, never store them.** Trust tier, staleness, drift, and reconciliation
status are computed at read time from stored signals. A stored verdict is a stored
opinion with an expiry date.

**No duplicate knowledge.** Knowledge lives in exactly one place and is referenced
everywhere else. Rendered views, exports, and caches are derivations, marked as such
and never edited. This is why the viewer never embeds concept bodies.

**Anything that cannot be handed to a stranger does not belong in core.** Core carries
no domain words, and CI enforces it by grepping for them.

## Contributing

Too early. The specification is stable enough to read and argue with; the code does not
exist. If you have opinions about §19's open questions, those are the live ones.

## License

MIT — see [LICENSE](LICENSE). OKFM is an independent project, not endorsed by or
affiliated with Google. See [NOTICE](NOTICE) for attribution of the OKF specification
(Apache-2.0) and of the prior art this design draws on.
