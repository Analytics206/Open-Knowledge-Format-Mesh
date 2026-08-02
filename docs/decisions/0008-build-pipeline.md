---
type: Decision
title: DR-0008 — What each component requires, and what the rebuild actually does
description: "Workflows are classified by what they expose — nothing, a human, a model, secrets — and a composite inherits the union of its steps, which is what puts the model-dependent half of the refresh loop at level 3 and keeps the rest runnable on a pull request from a fork."
status: draft
verified: { by: "human:analytics206", at: 2026-08-02T02:54:00Z }
tags: [workflows, tiers, ci]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0008-build-pipeline.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:3f01a5c6ada3a0a958995116a3a59848985ece3f4021228bdd926adf191cf067", at: 2026-08-01 }
okfm_scope: project
---
# DR-0008 — What each component requires, and what the rebuild actually does

- **Status:** accepted 2026-08-01 — `Feedback` destination split still open below
- **Date:** 2026-08-01
- **Revisions:** r1 tiers classified fields · r2 tiers classify components · r3 credentials
  became a tier · **r4 ordered by exposure; components declare an explicit `needs` set**
- **Affects:** spec §8.4, §10, §11.6, §13.6, §16; depends on [DR-0007](0007-two-layers.md)

## Two problems

**§8.4's refresh workflow mixes work that needs a model with work that does not.**
Re-resolving a pointer and comparing a hash is arithmetic. Rewriting a concept's
description because its source changed needs a model. The specification describes them as
one workflow, which forces the whole thing behind an API key and out of CI.

**Nothing says who may write which field.** §11.6 gets close — agent-derived concepts are
`draft` with no `verified` entry — but that is one rule about two keys, not a model.

## Precedent: this was already solved once

`project_template`'s `okf-update.yaml` states the split in its own header:

> *Deterministic sync (no AI) → AI enrichment of only the stale concepts → drift check.*
> *API key required for the enrich node; sync and done are deterministic.*

And `okf.py` adds a further division that this record adopts wholesale. `_MACHINE_KEYS` are
recomputed every reconcile. Prose fields are rewritten by the agent. And `relations` is
neither — the comment beside it is the whole argument:

> *"`relations` is CURATED, not machine-managed. Nothing here is inferred from prose — an
> edge asserted by a producer that guessed is worse than no edge, because traversal treats
> it as fact."*

That is correct and it generalizes.

## Decision: an explicit `needs` set, and a tier derived from it

Every component — a script, a resolver, a prompt, a workflow node — declares what it
requires, from a closed vocabulary:

```yaml
needs: []                  # pure
needs: [human]
needs: [model]
needs: [secrets]
needs: [model, secrets]    # legal, and it will happen
```

The **tier** is the highest requirement in the set, ordered by **exposure** — how far the
component reaches beyond pure local computation:

| Tier | Requirement | Reaches |
|---|---|---|
| **1 — pure** | nothing | local files and arithmetic |
| **2 — human** | a person | a decision made in the room |
| **3 — agent** | a model | delegation to a nondeterministic external service |
| **4 — credentialed** | secrets | live external systems, with keys |

**A human gate is a control, not a hazard.** It sits low deliberately: requiring a person
is the least risky thing a component can require after requiring nothing. Credentials sit
at the top because a component holding them can read and write systems the bundle does not
own.

### Propagation is a union, not a maximum

> **A composite's `needs` is the union of its own requirements and those of everything it
> invokes.** Its tier follows from that union.

Union rather than max, because the set is the thing that carries information. `okfm-release`
needs `[human, model]`; a refresh-and-enrich workflow needs `[model, secrets]`. Both would
collapse to a single number under a maximum, and the second one — an agent evaluating
something it had to query a warehouse to see — is unrepresentable any other way. It will
exist in Phase 3.

The build fails if a component's declared set is smaller than the union of what it invokes.
Without that check, "deterministic" decays into "deterministic except that one step" within
a release or two, and nobody notices until CI starts asking for an API key.

### Composition is not a tier

An earlier revision gave composed workflows a tier of their own. They do not need one —
`okfm-release` is `build` (∅) plus `enrich-concept` (`model`) plus sign-off (`human`), so
propagation makes it `[human, model]` without any special case. Composition is inheritance,
not a level.

### CI gates on the set, not the number

The number is a summary. The gate is a subset test:

| Job | Admits |
|---|---|
| pull request, including forks | `needs ⊆ {}` |
| trusted CI on `main` | `needs ⊆ {secrets}` |
| release, by hand | anything |

Note this is deliberately not monotone in the tier number: tier 4 runs in trusted CI while
tier 2 cannot run in CI at all. That is correct, and it is exactly why runnability is read
from the set rather than inferred from the ordering.

## Component inventory

### `needs: []` — tier 1

| Component | Does |
|---|---|
| `okfm validate` | conformance, profile checks, strip test |
| `okfm build` | the deterministic rebuild (steps below) |
| `okfm index` | emit what an agent would be handed |
| `okfm view` | generate `okfm-index.json`, rebake the web UI bootstrap |
| `file://` resolver | hash a local source |

### `needs: [human]` — tier 2

| Component | Does |
|---|---|
| `review-and-promote` | `draft` → `stable`, add the `verified` entry |
| `author-decision` | write a `Decision` body |
| `author-relations` | add typed edges |
| `author-meaning` | perspectives, rules, declared/observed/reconciliation |

These are real workflow nodes, not paperwork — `project_template`'s engine already has an
`interactive` node type for exactly this shape.

### `needs: [model]` — tier 3

| Component | Does |
|---|---|
| `enrich-concept` | rewrite one stale concept's prose from its own sources |
| `propose-concept` | draft a concept for a gap a question exposed (§11.6) |
| `evaluate-evidence` | the loop family's `Evaluation` step (§16) |
| `summarize-changes` | draft `log.md` prose where git alone is not enough |
| `draft-feedback` | compose a `Feedback` payload |

None is a publish step. Each is invoked by a composite that also carries `human`.

### `needs: [secrets]` — tier 4

| Component | Does |
|---|---|
| `okfm refresh` | re-resolve live pointers, write the observation cache |
| `sys://`, `store://` resolvers | reach a warehouse or an API capture |
| `okf://` resolver | reach another bundle's agent (§12.6) |

Tier 4 is why [DR-0006](0006-drift-cost-and-caching.md) keeps drift resolution out of the
injection path: injection is tier 1 and must stay that way.

### Composites

| Workflow | Steps | `needs` |
|---|---|---|
| `okfm-rebuild` | `build` → `enrich-concept` over stale → `build` → `validate` | `[model]` |
| `okfm-guide-refresh` | detect moved spec sections → `enrich-concept` on guide concepts citing them → `build` | `[model]` |
| `okfm-release` | `okfm-rebuild` → corpus checks → rebake viewer → version check → sign-off → publish | `[human, model]` |
| `okfm-drift-sweep` | `okfm refresh` → `enrich-concept` over newly drifted → sign-off | `[human, model, secrets]` |

`okfm-release` is the process run before publishing. It does not rerun unless files change:
the pure steps are idempotent and the `model` step has an empty work list when nothing is
stale, so a no-change release is a fast no-op producing an empty diff.

## Field ownership follows from `needs`

A field may only be written by a component whose set permits it.

| Key | Written by | Note |
|---|---|---|
| `generated: {by, at}` | `[]` | Stamped by whatever produced the content |
| `okfm_key` | `[]` | Generated once, then stable |
| `okfm_run_id`, telemetry | `[]` | |
| `index.md`, `log.md` | `[]` | Generated. `log.md` from git and telemetry, never appended by hand |
| viewer bootstrap, `okfm-index.json` | `[]` | Derivations (§3.14) |
| `okfm_captured` for `file://` | `[]` | Hashing a local file needs no key |
| `type`, `title` | `[human]` | Drive everything downstream |
| `status` | `[human]` | Promotion is a human act by definition |
| `stale_after` | `[human]` | A policy choice, not a computation |
| `verified: [{by, at}]` | `[human]` | The backfill honesty rule (§16). A set without `human` cannot write it |
| `sources[].resource`, `okfm_role` | `[human]` | |
| `okfm_relations` | `[human]` | Never inferred from prose. Traversal treats an edge as fact |
| `okfm_perspective`, `okfm_declared`, `okfm_observed`, `okfm_reconciliation` | `[human]` | Meaning-family semantics |
| `description` — **extracted** | `[]` | Copying an existing sentence cannot invent. See below |
| `description` — **drafted**, `tags` | `[model]` | The index injects `description`; the highest-value drafted field |
| body prose sections | `[model]` | Subject to the per-type ruling below |
| `okfm_reason_codes` | `[model]` | Proposed from the controlled vocabulary; a human confirms |
| `okfm_captured` for `sys://`, `store://`, `okf://` | `[secrets]` | Requires reaching the live system |

The old rule *"never let a model write `verified`"* now falls out of the model rather than
sitting beside it: `verified` requires `human`, and `enrich-concept` declares `[model]`.

### Extraction is not drafting

`description` appears twice above, and the split is load-bearing:

- **Extraction** copies text that already exists — the first blockquote, the first
  paragraph, the `# H1`. It cannot invent. Worst case it is unhelpful; it is never wrong
  about what the source says. `needs: []`.
- **Drafting** writes a new sentence that did not exist. It can be wrong in ways nobody
  notices. `needs: [model]`.

This is the same reasoning as §3.4 — record signals, not verdicts — applied to prose. It is
also what makes [DR-0009](0009-adoption-levels.md)'s Level 2 possible at all: a complete
bundle can be bootstrapped from a folder of markdown with no model anywhere, because every
field it fills is extracted or computed.

`project_template` already implements exactly this (`okf.py:312`), preferring a leading
blockquote and falling back to the first real paragraph. The extracted value lands with
`status: draft` and no `verified` entry, so the trust machinery reports it accurately
without any special case.

## The loop family, ruled per type

The eight types do not share a requirement. The split is between **commitments** and
**observations** — the same line §3.8 draws between evaluation and outcome.

| Type | Needs | Why |
|---|---|---|
| `Goal` | `[human]` | Sets what the loop is for. A misstated goal quietly misdirects every downstream record |
| `Decision` | `[human]` | *The* gate. Reject / monitor / trial / adopt is the commitment the loop exists to capture |
| `Evidence` | `[model]` | A pointer record — what was gathered, from where, what was seen |
| `Evaluation` | `[model]` | Agent-written by design (§16). The whole point is volume |
| `Experiment` | `[model]` | Drafted from the decision, which already carried the judgement |
| `Outcome` | `[model]` | A measurement. Agent-written, human-verified like anything else |
| `Answer` | `[model]` | Gated by attestation (§9.4), not by authorship |
| `Feedback` | destination-dependent | See below |

### `Feedback` splits on destination

Stated for override — this is the one type not put to the steward:

- **To a source system** (a score and reason codes back to the arXiv MCP, §16 item 4) —
  `[model]`. High volume, per-candidate, and the payload goes to a system this project
  owns. Hand-gating each one kills the loop.
- **To another bundle** (§12.4, filed into another owner's inbox) — `[human]` to file, and
  `[human, secrets]` when the target bundle is remote and reached through its agent. It is
  an outbound assertion to a separate accountable owner, it lands in a durable negotiation
  ledger, and it cannot be retracted quietly. Volume is low by construction, so the gate is
  cheap.

`draft-feedback` (`[model]`) may compose either. Filing the cross-bundle one is a separate
component that carries `human`. This is the clearest case for why the set beats a number: a
single tier could not say "needs a person *and* a credential, but not a model."

## `okfm build` — the `needs: []` steps, in order

Every step is arithmetic, and the whole thing runs on a fork with no secrets.

1. **Parse** frontmatter for every `.md` with a non-empty `type:` in scope.
2. **Conformance** — parseable frontmatter, non-empty `type`, reserved-file structure
   (official §11).
3. **Profile** — `okfm_` prefix rule; predicates and reason codes checked against
   `vocab/`; **no stored verdicts** (`okfm_stale`, `okfm_drifted`, `okfm_trust` are errors,
   per §3.4).
4. **Strip test** — remove every `okfm_` key, re-run step 2. Fails the build if the bundle
   is only legal *with* the profile (§7.1 rule 4).
5. **Resolve** every markdown link and every `§N.M` cross-reference, ignoring fenced
   blocks — those are examples, not document.
6. **Hash `file://` sources**, write the observation cache. Live schemes need `secrets`.
7. **Regenerate `index.md`** per directory from `description` fields.
8. **Regenerate `log.md`** from git history and telemetry, capped. Never appended by hand —
   an append-only prose log written by every run is a merge-conflict magnet.
9. **Rebake the web UI bootstrap** from the guide bundle. Metadata only; bodies never
   embedded (§14.3).
10. **Emit `okfm-index.json`** — gitignored, what an agent would be handed.
11. **Boundary checks** — every component's declared `needs` covers the union of what it
    invokes; domain-word grep over `tools/`; base validates with `tools/` deleted
    ([DR-0007](0007-two-layers.md)); masthead and version consistency across the corpus.

**Acceptance criterion: running it twice produces an empty diff.** That is the whole
"doesn't need to rerun unless I change files" property, and it is mechanically testable.
`okf.py`'s `_write_if_changed` is the existing shape of it.

## The `[model]` contract

1. **Work list is derived, not stored.** Concepts whose `okfm_captured` disagrees with the
   observed hash. The existing implementation stores `stale: true` and clears it; under
   §3.4 that flag is computed instead, and the work list falls out of the same comparison
   that drives drift. One mechanism, two uses.
2. **Read only that concept's own sources.** Not the whole tree — this keeps context lean
   and cost proportional to what changed.
3. **Write `[model]` fields only**, always as `status: draft`, `generated.by: <agent>`, and
   no `verified` entry.
4. **Stop.** The composite carries a `human` step; a person promotes to `stable` and adds
   the `verified` entry.

## Publication model

The rebuild is a **maintainer** step, not a consumer dependency.

The OKFM repository runs `okfm-release` before publishing. What ships is the *output* — a
validated spec corpus, a guide bundle, a web UI with a current baked index. Someone
downloading OKFM to read the format, point an agent at it, or write their own
implementation runs nothing.

An adopter who chooses the reference implementation runs the same components over their own
bundle. That is their build, not a shared refresh of OKFM's documentation. There is no mesh
anyone else updates.

This is why the web UI can be base while its bootstrap is generated by tools: the artifact
is committed and consumed by everyone; the generator is a dependency for nobody.

## Amendment 2026-08-02 — the tag goes on the workflow, not just the component

This record inventories components by `needs`, which is where the classification starts and
not where it does any work. **A workflow carries the tag too**, and the workflow's tag is the
one anything acts on: CI decides what may run on a fork's pull request by reading a
workflow's set, not by looking up each step.

The two are related by the union rule already stated above — a workflow's set is the union of
everything it invokes — so the workflow tag is derived and never hand-written. But it has to
be *present*, because an untagged workflow is one somebody has to reason about every time,
and that reasoning is exactly what gets skipped when the workflow is running and the change
is small.

Concretely: `okfm-rebuild` is tagged `needs: []` and that is why it is the CI job. Add one
model-dependent step and the tag becomes `[model]` by arithmetic, which takes it out of CI
automatically rather than because someone remembered to move it.

## Against

**Four requirements is more ceremony than two.** The two middle ones are what make it work.
Collapsing `model` into `[]` means machine-written prose nobody reviewed. Collapsing
`secrets` into `[]` means CI needs warehouse credentials to validate a fork's pull request.
Collapsing `model` into `human` loses the ability to say "this needs an API key" separately
from "this needs a person."

**A tier number no longer announces that a human must sign off.** True — `okfm-release` is
tier 3, and its number says `model`, not `human`. The set says both, explicitly, which is
better than implying it from position. Read the set.

**"Never inferred" for `okfm_relations` will feel restrictive.** It will. A wrong typed edge
is worse than a missing one because traversal, impact analysis, and drift propagation all
treat it as fact. A `[model]` component may *propose* relations in a review artifact; it may
not write them.

## Settled details

Decided rather than left open, because none of these is an architecture question.

**A `[model]` component may write proposals to `review/`, never to a concept.** Proposals
are a separate artifact a `[human]` step merges. That is not a back door — the rule is
about which *file* is written, and a proposal file is not a concept.

**`okfm build` warns on an unfilled `[model]` field; it never fails.** An empty
`description` is unhelpful, not malformed. Failing would break Level 2 on something only
Level 3 can fix, which would make the level model a lie.

**The `Feedback` destination split stands as written.** Source-system feedback is
`[model]`; cross-bundle filing is `[human]`, and `[human, secrets]` when the target is
remote. It is Phase 4 work and can be revisited when the ledger exists.

**`needs` stays a closed vocabulary of four.** `network` was considered and rejected: a
fifth value earns its place only when a component genuinely needs the open internet and no
credential, and none does yet.
