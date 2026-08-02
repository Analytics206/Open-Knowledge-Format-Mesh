---
type: Decision
title: DR-0003 — Where federation sits in the delivery order
description: "Federation's negotiation half lands after the credentialed phase while its addressing half moved into Phase 1, because the repository is already a mesh; amended to take the proving-ground projects out of the phase plan entirely — they are the feedback loop, not steps this repository performs."
status: draft
verified: { by: "human:analytics206", at: 2026-08-02T02:53:59Z }
tags: [phases, federation, sequencing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0003-phase-ordering.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:8dac493bc9de31c746fed1f3fdf732a27fa1e12a693e3ae0e168173a89d8b0bd", at: 2026-08-01 }
okfm_scope: project
---
# DR-0003 — Where federation sits in the delivery order

- **Status:** accepted 2026-08-01 — the negotiation half of federation moves after the
  SugarPaws3d port; the addressing half already landed early per
  [DR-0010](0010-okfm-self-hosts-as-a-mesh.md)
- **Date:** 2026-08-01
- **Affects:** spec §15 (roadmap phases)

## Current order

Phase 1 arXiv retrofit → Phase 2 extraction → **Phase 2.5 federation** → Phase 3
SugarPaws3d port.

§15's stated reason: SugarPaws3d sits on at least two ownership seams — a data bundle
(schema, queries, captures) and a business-rules bundle (concepts, perspectives, rules) —
so the port should be "born federated rather than split later."

## Proposal

Move federation **after** the port.

## Why

**The spec already argues federation is retrofittable.** §12.3 rule 2 states it outright:
*"Local references are unchanged. Federation adds nothing inside a bundle."* If that is
true — and it is the design's own load-bearing claim — then splitting one bundle into two
later costs re-pinning cross-references and moving files. That is mechanical work.

Doing it first costs building a registry, a cross-bundle resolver, an agent interface, a
feedback ledger, and cross-bundle drift **before knowing whether the meaning-family
concepts are right at all**.

**The port has ground truth and federation does not.** §11.4 registers existing trusted
business reports as a golden answer set: the answer key and the exam both already exist.
§20.4 (golden-set agreement) is the only success measure in the whole list that can be
checked against something that predates this project. Everything gating it is delay
against the one measurable payoff.

**§21.5 flags federation as the least-evidenced part of the design.** Nothing in the
ecosystem covers it, so it has no prior art to borrow and must be proven here. Unproven
work belongs after the thing that validates the foundation, not before it.

**Two directories in one repo is a real rehearsal.** Building `sp3d-data/` and
`sp3d-rules/` as sibling directories with a genuine ownership seam between them exercises
the boundary — separate concepts, separate stewardship, no cross-writes — without the
transport, registry, and pinning machinery. When federation lands, there are two real
bundles with a real disagreement history to federate, which is a far better test than a
toy pair.

## Against

Two arguments, both real:

1. **Re-pinning may be worse than it looks.** If the port accumulates hundreds of
   cross-references before the split, mechanical still means a migration. Mitigation:
   keep the seam explicit from day one — no concept in `sp3d-rules/` reads a file in
   `sp3d-data/` directly, even though nothing yet enforces it.
2. **The steward knows the seams better than this analysis does.** If the data and rules
   domains genuinely have different owners and cadences *today*, born-federated is the
   honest shape and this proposal is wrong.

## Recommendation

Reorder, and enforce the seam by convention during the port so the eventual split stays
mechanical. Reverse this if the two SugarPaws3d domains already have distinct
accountable owners — that is the §12.1 split criterion, and it beats sequencing
convenience.

## Amended by DR-0010 — 2026-08-01

[DR-0010](0010-okfm-self-hosts-as-a-mesh.md) splits federation in two, and only the second
half is what this record was arguing about.

| Half | Contains | When |
|---|---|---|
| **Addressing** | registry bundle, `OKF Member` concepts, cross-bundle refs, commit pinning, cross-bundle drift, multi-bundle viewer | **Phase 1** |
| **Negotiation** | agent interfaces, transport, feedback inbox/outbox, cross-owner routing | after the port, as argued above |

The addressing half moves earlier because OKFM's own repository becomes a mesh at
effectively no cost — the content already exists — and it proves the project's central
metaphor on day one rather than at the end.

The argument above stands unchanged for the negotiation half, which is the expensive,
unproven, no-prior-art part that should not stand between the project and its only
measurable payoff.

## Resulting phase order

| Phase | Delivers |
|---|---|
| **1** | Baseline adoption, the Level 2 build, the Level 3 loop, **federation's addressing half** — registry, `OKF Member` concepts, cross-bundle refs, commit pinning, multi-bundle viewer |
| **2** | Extraction into a distributable project: core/packs/config split, the three runtime modes, the distribution tests |
| **3** | **The credentialed half** — `sys://` resolvers, meaning-family curation, attested computations, reconciliation against a report its owner already trusts |
| **4** | **Federation's negotiation half** — agent interfaces, transport, the feedback inbox/outbox ledger, cross-owner routing |

Phase 3 builds a domain's data and rules as sibling bundles with an explicit seam: no
concept in the rules bundle reads a file in the data bundle directly, even though nothing
yet enforces it. That convention is what keeps the eventual split mechanical, and it is the
mitigation for the first counter-argument above.

By Phase 4 there are two real bundles with a real disagreement history to federate, which
is a better test than a toy pair.

## Amendment 2026-08-01 — the proving grounds are not phases of this project

Phase 1 named an arXiv loop retrofit and Phase 3 a SugarPaws3d port. Both are gone from the
plan, and the correction is worth stating precisely because it is easy to read as a
cancellation.

They were never work this repository performs. They are **other projects** — one of them a
loop that already runs, in a repository this one does not touch. Writing them into the phase
plan made OKFM look like a project with a domain, and a scaffolding that has a domain is one
step from having that domain's assumptions compiled into it. The CI grep forbidding domain
words in code was already defending against exactly this; the roadmap was undermining it in
prose.

What they actually are is the **feedback loop**: adopt OKFM in a real project, find what
breaks, bring the finding back here as a change. That is a validation channel, and a valuable
one, but it belongs outside the plan rather than inside it — nothing here should be blocked on
a repository this one cannot see, and nothing here should be built to fit one.

**What replaces them.** The exit criteria that depended on a specific corpus now depend on
this repository's own mesh, which is real content with the same properties: eight bundles,
genuine cross-bundle references, a working drift signal, and a benchmark harness pointed at
it. Where a criterion genuinely needs a domain — a `sys://` resolver against a live database,
attested computations reconciled against existing trusted reports — it stays in the roadmap as
a capability with no named corpus attached, and the corpus arrives when someone adopts it.

## Amendment 2026-08-02 — federation's addressing half is level 1

Where federation sits in the *delivery* order was this record's question. Where it sits in
the **level** model was never answered, and the answer is level 1.

The mesh is what you get when you download the project and open the viewer: several bundles,
a master OKF over them, typed edges between them, and a graph that draws the whole thing.
Nothing runs. That is the definition of level 1, and it means federation's addressing half is
already the most complete demonstration in the project rather than a thing waiting on a
phase.

**Level 2 supports what it can, and says what it cannot.** The build writes a master OKF and
both halves of every membership edge, so a mesh built by the drop-in is connected without
anyone authoring an edge by hand. What level 2 cannot do is resolve `okf://` across a network
or ask another bundle's agent anything — those need transport, which is the negotiation half.
The right behaviour for an unsupported capability at a level is to name it as unsupported,
not to half-implement it.

And the standing escape applies here as everywhere: anyone can point an agent at the mesh and
have it do whatever they want, at any level. That is not a gap in the level model, it is the
reason the level model describes what *OKFM* provides rather than what an adopter can achieve.
