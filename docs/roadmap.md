# OKFM — Roadmap

The assets in hand, the two proving grounds, the delivery phases, what is deliberately deferred, what is still open, and how success is measured. Non-normative and expected to change.

### A distributable knowledge-mesh scaffolding for OKF bundles

**Version:** OKFM v0.2.1
**Baseline:** Open Knowledge Format (OKF) v0.2 — GoogleCloudPlatform/knowledge-catalog
**Concept:** Actionable Knowledge — evidence that changed what a project knows or does, preserved so the *why* stays queryable
**Date:** 2026-07-31
**Audience:** The builder, adopters of the scaffolding, and the AI agents working the codebase

---

## Where everything lives

**Section numbers are global across the OKFM document set.** They are preserved from the unified v0.2.1 specification, so a reference like §12.3 means the same thing in every file. Gaps in this document's numbering are intentional — the map says where each section lives.

| # | Section | Lives in |
|---|---|---|
| 0 | What This Release Changes | [`docs/rationale.md`](../docs/rationale.md) |
| 1 | What Changed from v2, and Why | [`docs/rationale.md`](../docs/rationale.md) |
| 2 | Vision | [`docs/rationale.md`](../docs/rationale.md) |
| 3 | Design Principles | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 4 | Existing Assets | *this document* |
| 5 | Architecture Overview | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 6 | Baseline: What We Inherit from OKF v0.2 | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 7 | The OKFM Profile | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 8 | Evidence, Drift, and Staleness | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 9 | Governed Numbers: Attested Computation | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 10 | Workflow Instrumentation | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 11 | Adoption Profile: an Analytics Domain | *this document* |
| 12 | Federation — the OKF Mesh | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 13 | Drop-In Instantiation and Distribution | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 14 | The Mesh Web UI | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 15 | Roadmap | *this document* |
| 16 | Adoption Profile: retrofitting a loop that already runs | *this document* |
| 17 | Deferred — Parking Lot with Re-entry Triggers | *this document* |
| 18 | Evaluating the Bundle | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 19 | Open Questions | *this document* |
| 20 | Success Measures | *this document* |
| 21 | Ecosystem and Prior Art | [`docs/prior-art.md`](../docs/prior-art.md) |
| 22 | Closing Note | [`docs/rationale.md`](../docs/rationale.md) |
| A | Legacy Draft → OKFM v0.2.1 Field Mapping | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |

---

## 0. What This Release Changes

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 1. What Changed from v2, and Why

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 2. Vision

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 3. Design Principles

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 4. Existing Assets

What OKFM was designed against, described by shape rather than by name. The projects behind these are the author's and are not part of this repository — see [DR-0003](decisions/0003-phase-ordering.md) on why naming them here was a mistake.

### 4.1 A harness

A Python engine wrapping AI and MCP tools with hooks, workflows, loops, and logging, with several project UIs over the same engine. A shared workflow library is planned; the loop defined here should become one of its reusable workflows.

### 4.2 A large evidence store

Document database plus vector index behind an MCP server, holding roughly a million records. Scale and data type are exactly why this lives in a dedicated store: bundles reference its records and never duplicate them.

### 4.3 A pre-OKF markdown graph

Documents related down to the line level, with sidecar files describing each file so an agent need not read everything, plus a refresh workflow that flags files needing update. §7.4 and §8 describe how these map onto — and extend — official v0.2.

### 4.4 A running acquisition loop

Topic in, vector search, gather and rank, evaluate each candidate against the active project's system docs, human-in-the-loop summary (reject / trial), documentation updates, per-candidate feedback with scores and reasons sent back to the source, everything logged. This loop already runs; §16 describes the shape of formalizing what it emits.

### 4.5 An analytics domain

API data captured continuously for months. Curation in progress: system documentation, database schema and metadata, queries, business rules. Reports already produced for the business serve as a **golden answer set**. Target: a chat system answering loss, growth and revenue questions for a non-technical consumer. Details in §11.

---

---

## 5. Architecture Overview

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 6. Baseline: What We Inherit from OKF v0.2

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 7. The OKFM Profile

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 8. Evidence, Drift, and Staleness

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 9. Governed Numbers: Attested Computation

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 10. Workflow Instrumentation

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 11. Adoption Profile: an Analytics Domain

The shape of the adoption that exercises the most profile surface — a data domain with existing trusted reports, a non-technical consumer, and definitions that quietly disagree with each other.

Written as a profile rather than a project. An earlier draft named a specific application here, which made a domain-free scaffolding read as one project's delivery plan; see the amendment in [DR-0003](decisions/0003-phase-ordering.md). What follows is what Phase 3 needs from whichever domain arrives first, and nothing about who that is.

### 11.1 The consumer

A non-technical owner who wants answers, not reports. Three requirements follow:

1. **Actor-aware defaults.** Each actor has a steward-configured default perspective per concept, so nobody is asked to choose between two definitions in the vocabulary of the definitions. The answer states the resolved perspective in plain language, and alternatives surface only when they materially change the number.
2. **Legible trust.** Attestation verdicts, staleness, and claim classification render as sentences.
3. **Attestation gating.** A failing attestation means no number displayed (§9.4).

### 11.2 Concepts and perspectives

The pattern, not a vocabulary. Every domain has at least one metric whose name hides two definitions, and that metric is where to start.

| Shape | Two perspectives | Question each answers |
|---|---|---|
| A **loss** metric | contractual end vs. behavioural end | "Who stopped paying?" vs. "Who stopped caring?" |
| A **growth** metric | first-time vs. returning | "Where is the top of the funnel?" |
| A **money** metric | gross vs. net; committed vs. collected | "What was promised?" vs. "What landed?" |

Each `Perspective` names its owner-purpose and links to its `Rule`s, each of which links to an `Attested Computation`. Nobody owns the metric; each perspective owns its view.

### 11.3 Declared vs. observed

The most valuable thing this profile exercises: a written policy and the query that supposedly implements it, held in one concept and reconciled.

```markdown
---
type: Rule
title: Loss metric — contractual perspective
status: stable
generated: { by: "agent:curation", at: 2026-07-20T10:00:00Z }
verified: { by: "human:steward", at: 2026-07-22T14:00:00Z }
sources:
  - id: policy
    resource: /systems/business-rules.md#L40-L55
    okfm_role: defines
    okfm_captured: { version: "git:abc1234", at: 2026-07-20 }
  - id: impl
    resource: sys://warehouse/query/monthly_loss.sql
    okfm_role: implementation
    okfm_captured: { hash: "sha256:4b1e...", at: 2026-07-28 }
okfm_relations:
  - { predicate: perspective_on, target: /perspectives/loss-contractual.md }
  - { predicate: implemented_by, target: /computations/loss-contractual.md }
okfm_declared: policy
okfm_observed: impl
okfm_reconciliation:
  status: unreviewed        # unreviewed | consistent | material_mismatch | acknowledged
  method: run both variants over the same months; diff the resulting sets
---

# Declared

An account is lost when its contract is cancelled or payment permanently fails.[^policy]

# Observed

The monthly query counts an account as lost only after the final failed retry,
and nets out same-month cancel-and-resubscribe.[^impl]
```

`okfm_declared` and `okfm_observed` are `sources[].id` references — the same keyed-join discipline official uses for footnotes, so reordering sources cannot silently misattribute.

A domain with months of raw captures makes reconciliation **testable**: run both variants over the same history and characterize the difference row by row. Deterministic verification against data that already exists.

### 11.4 Golden answer set

Reports the business already trusts encode correct numbers under the steward's definitions. They are registered as concepts with `okfm_role: golden_reference`, and reconciliation targets them: a new Attested Computation must reproduce the trusted report before it is `verified`.

This is the requirement that decides which domain is worth porting first. The answer key and the exam both have to already exist; a domain without them can be built but not checked.

### 11.5 Question workflows

**A bridge question** — decompose a period-over-period change into named components, each an attested computation under a stated perspective. The decomposition is *attested*; any causal story about it is *inferred* and labeled as such.

**A driver question** — resolve perspective, check freshness and `data_gap` flags, decompose by the domain's natural cuts, retrieve prior `Decision` and `Answer` precedents, rank explanations, then record the resulting `Decision` and later its `Outcome`.

### 11.6 Questions produce knowledge — the consumer is a curator

The actor split is about **authority, not write access**. The steward authors and approves meaning-family concepts and is the only `human:` verifier; the consumer never edits a rule. But every consumer interaction writes to the bundle:

1. **Gap-triggered curation.** A question landing on under-documented territory triggers derivation — schema introspection, query inventory, targeted analysis — producing concepts as `status: draft` with `generated.by` set to the agent and no `verified` entry. Unverified by construction, per official trust tiers. They enter the steward's review queue; once verified and `stable`, the next such question answers from knowledge instead of derivation.
2. **Demand signal.** Question history is telemetry: which concepts get asked about, which answers draw follow-ups, which questions go unanswered. Curation priority follows demand.
3. **Precedents.** Accepted answers persist as `Answer` concepts. Past facts become templates for future facts.

Same loop as any acquisition process: question = goal, gap-fill = discovery + evaluation, steward review = human gate, accepted answer = published knowledge, follow-up behaviour = feedback.

### 11.7 Discovery adapter

Discovery in a data domain is not search but **source understanding**: schema introspection, query inventory, and capture-coverage profiling to find `data_gap`s across the history. It implements the same `DiscoveryAdapter` interface as any other evidence source (§13) — same loop, different input.

---

---

## 12. Federation — the OKF Mesh

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 13. Drop-In Instantiation and Distribution

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 14. The Mesh Web UI

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 15. Roadmap

Four slices, each end-to-end. No phase builds platform without a user-visible query working at its end.

> **The proving grounds are not phases.** §11 and §16 describe two real projects — a analytics port and a retrofit of a running research loop — and neither is work this repository performs. They are the **feedback loop**: adopt OKFM somewhere real, find what breaks, bring the finding back. Writing them into the phase plan made a domain-free scaffolding look like a project with a domain, which is one step from having that domain's assumptions compiled into it. See the amendment in [DR-0003](decisions/0003-phase-ordering.md). Where a phase genuinely needs a domain, it names the capability and leaves the corpus unnamed until someone adopts it.

### Phase 1 — Baseline adoption and the self-hosted mesh

Scope: migrate to conformant v0.2 using an **existing migrator** rather than a hand-written one (§21.2); the §7.4 sidecar audit, applying the §7.7 admission test to every existing concept; OKFM profile keys frozen; loop-family types; telemetry 1.0; initial reason vocabulary. Validation is **adopted, then extended**: an existing conformance validator and CI action handle official §11; a second OKFM pass adds vocab-checked predicates and reason codes, pointer resolvability, and the strip test. The Level 2 deterministic build and the Level 3 enrichment loop, each usable on its own. Stand up the benchmark harness (§18.4) and take a baseline reading.

Also in Phase 1, per [DR-0003](decisions/0003-phase-ordering.md) and
[DR-0010](decisions/0010-okfm-self-hosts-as-a-mesh.md): **federation's addressing half** —
the mesh OKF, `OKF Member` concepts, cross-bundle references with commit pinning, and a
viewer that renders more than one bundle. It costs almost nothing because OKFM's own
repository is a mesh of eight bundles, and it proves the project's central metaphor now
rather than at the end.
Also in Phase 1, ahead of where it was planned: **level 3's local variant**
([DR-0013](decisions/0013-the-local-model-variant.md)). A model on the adopter's own machine
needs no key, no provider abstraction and no adapter layer, so the part of Phase 3 that was
expensive is not the part that arrived — one endpoint, one config block, `needs: [model]` and
no `secrets`. It is worth having early because it makes the enrichment loop complete for an
adopter with no agent to spare, which is the case the level model otherwise leaves stranded.
**Exit:** "Why did we decide X?" answered from the mesh alone; one run fully reconstructable from telemetry; every bundle passes official conformance in CI with every `okfm_` key stripped; a first benchmark run recorded, whatever it says.

The benchmark half of that exit is met, and what it says is *nothing measurable*: 29/30 claims with the bundle against 28/30 without, zero false statements in either arm. Recorded as run_seed1 rather than rerun until it produced a better number. The instrument cannot resolve a difference on 70 files of prose written to be read — see [the benchmark](okfm-guide/level-3-enrich/the-benchmark.md) for why that was close to guaranteed by §18.1's own rule that every fact must be answerable in both arms.

### Phase 2 — Extraction into a distributable project

Scope: §13 in full — split core / packs / config / bundle; move the loop into
`core/workflows/`; extract `packs/research/`; write `okfm.json` and its schema;
the three runtime modes (§13.6); the domain-word CI grep;
README quickstart, `templates/`, `examples/minimal/`, `okfm-guide/`, and `okfm view` (§14).
**Exit:** a toy second domain stood up via pack + config with zero core edits, **and**
a first pass at the distribution test (§13.7) — someone other than the builder, or the
builder on a clean machine with only the README, reaches a running mesh in under an
hour.

### Phase 3 — The credentialed half: live sources and attestation

The first phase that needs a real domain. It names capabilities, not a corpus — the corpus is
whichever project adopts OKFM first, and §11 describes one candidate in detail.

The *uncredentialed* half of "OKFM drives the model" already landed in Phase 1 — see
[DR-0013](decisions/0013-the-local-model-variant.md). What is left here is everything the
credential brings with it: the second adapter, the endpoint list, handle resolution, and the
question of a process acting unattended.

Scope: `sys://` resolvers for databases and API captures; a discovery adapter interface; curated schema, queries and rules ingested as meaning-family concepts; **Attested Computations with real attesters**; reconciliation against an existing trusted report; declared-vs-observed reconciliation over a real history; the §11.5 question workflows; actor-aware defaults and plain-language trust rendering; the gap → propose → verify loop; drift detection live on `sys://` pointers.
**Exit:** one business question answered with a stated perspective, a **passing attestation**, resolvable citations, claim classification, and the answer recorded as an `Answer` concept. One attested computation reconciled against a report its owner already trusts. One declared/observed mismatch found (or consistency verified). One consumer question driving the full gap → propose → verify cycle. A benchmark run (§18.4) on real questions, graded against ground truth the adopter already has.

### Phase 4 — Federation, the negotiation half

The addressing half — registry bundle, `OKF Member` concepts, cross-bundle references,
commit pinning, a multi-bundle web UI — landed in Phase 1, because OKFM's own repository is
a mesh and the content already existed.

What remains is the expensive, unproven part.

Scope: an agent interface on at least two bundles (in-process transport is fine); cross-bundle
routing from the registry to member agents; the addressed-feedback inbox/outbox ledger; the
agent as the access-control point; optionally a hosted instance as a remote member, which is
the only way to exercise real transport.
**Exit:** a cross-bundle question answered by scatter-gather with citations resolving into two
bundles; one feedback → response pair in both ledgers; one pinned reference correctly flagged
as drifted after the owning bundle deprecates its target.

### Sequencing

Phase 2's exit rehearses Phase 3.

Phase 4 follows the port rather than preceding it — see
[DR-0003](decisions/0003-phase-ordering.md). The original plan put federation first, on the
grounds that an analytics domain sits on two ownership seams and should be born federated. The
counter-argument won: §12.3 states that federation adds nothing *inside* a bundle, so
splitting later is mechanical, while building a registry, transport, and a feedback ledger
before knowing whether the meaning-family concepts are right is not. The port is also the
only work with pre-existing ground truth (§11.4), and nothing unproven should stand between
the project and its one measurable payoff.

The port therefore builds its two domains — data and business rules — as sibling directories
with an explicit seam: no concept in the rules domain reads a file in the data domain
directly, even though nothing yet enforces it. That convention keeps the eventual split
mechanical, and by Phase 4 there are two real bundles with a real disagreement history to
federate, which is a better test than a toy pair.

**Reverse this** if a domain's two halves turn out to have distinct accountable owners
today. That is the §12.1 split criterion, and it beats sequencing convenience.

---

---

## 16. Adoption Profile: retrofitting a loop that already runs

Formalization, not new capability. Where a process already produces decisions, the work is making it write conformant concepts as a side effect.

Written as a profile rather than a project, for the reason in §11 and in [DR-0003](decisions/0003-phase-ordering.md): this repository does not perform the retrofit. It is the shape the retrofit takes wherever someone does.

1. Inspect real logs; derive loop-family body conventions and reason codes from what the process already emits, rather than inventing a vocabulary and asking the process to adopt it.
2. Write `Goal`, `Evidence`, `Evaluation`, `Decision`, `Experiment`, `Outcome`, `Feedback` concepts during runs, with `generated` set to the agent actor and `verified` added only on human review.
3. A telemetry record per run; concepts carry `okfm_run_id`.
4. `Feedback` concepts become the payload sent back to whatever supplied the evidence — the same content as before, now stored and coded.
5. An `already_evaluated` guard: check the bundle before evaluating a candidate a second time.
6. Optional backfill of recent runs from existing logs. **Backfill honesty rule:** never synthesize a `verified` entry, and never attribute `generated.by` to a human for content written before the field existed. Use `process:okfm-backfill`, leaving backfilled concepts correctly *unverified* under official trust tiers. A faked human review is worse than an honest gap, because it silently promotes a trust tier nobody earned.
7. Validator in CI: official conformance, OKFM vocab, pointer resolvability, and the strip test (§7.1 rule 4).
---

---

## 17. Deferred — Parking Lot with Re-entry Triggers

| Deferred | Re-enters when |
|---|---|
| Learned ranking from feedback | A task class accumulates enough coded feedback+outcome pairs to beat hand rules |
| Token-budget optimization, redundancy scoring | Context size demonstrably degrades answers |
| REST/GraphQL API | A non-harness, non-MCP client exists |
| Multi-tenancy, roles, residency | A second steward works in the system |
| Embedding index over bundles themselves | Progressive disclosure plus grep measurably misses |
| Publishing OKFM as a reusable profile | The profile has survived both proving grounds |
| Receipt/verdict wire formats, attester sandboxing | Official deferred these too; follow official rather than inventing |
| Bounded autonomous actions | Recommendation → outcome tracking has a solid record |
| Formal bitemporal model | Effective-dated rules prove insufficient |

---

---

## 18. Evaluating the Bundle

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 19. Open Questions

1. **Sidecar audit outcome.** How many current sidecars are summary-only (collapse into `description` + `index.md`) versus carrying anchors and retrieval hints (keep as `okfm_sidecar`)?
2. **Path IDs vs. reorganization.** Is `okfm_key` enough, or does a generated path↔key index in `references/` become necessary?
3. **Attester language and location.** Python attesters in `references/attesters/`, run consumer-side by the harness — but who runs them in the chat app path, and what does a failed verdict look like to a non-technical reader?
4. **Feedback consumption at the source.** Stored feedback is Phase 1; does the evidence source *use* it (filter/boost) now, or store until volume justifies ranking changes?
5. **Telemetry granularity.** Full prompts/outputs per step, or hashes plus concept refs only? (Lean: refs and hashes; bodies are already concepts.)
6. **Registry stewardship.** The registry is a bundle too — who owns the map when a second steward exists?
7. **Transitive feedback.** When bundle A's feedback concerns B's concept that itself cites C, does A file to B only? (Lean: yes — ownership chains stay linear.)
8. **Capture gaps as concepts.** Should `data_gap` be a concept (period + affected metrics) rather than only a reason code, so gaps propagate staleness like drift?
9. **Effective dating.** Rules need `effective_from/to` in any domain whose policy changes. Do metrics? Perspectives? Start with rules and see what breaks.
10. **Baseline version pinning.** The baseline moved v0.1 → v0.2 in weeks. Which OKF version does the validator gate against, and what triggers a baseline bump — an official release, or a feature we need?
11. **Admission test enforcement.** Can "does this say something its sources cannot?" be checked mechanically at all (e.g. flagging a concept body that is largely a restatement of a cited file), or does it stay a review-time judgement?

---

---

## 20. Success Measures

1. **Conformance:** bundles pass official OKF v0.2 conformance, and pass the strip test — remove every `okfm_` key and the bundle is still a useful OKF bundle.
2. **Answer-from-memory:** "Why did we reject/adopt X?" answered from the bundle in one query, with resolvable citations.
3. **Attestation rate:** share of displayed business numbers backed by a passing attestation. Target: all of them.
4. **Golden-set agreement:** attested computations reproduce the existing trusted reports.
5. **Re-evaluation avoidance:** share of discovery candidates short-circuited by `already_evaluated`.
6. **Outcome closure:** share of trial decisions that eventually receive an `Outcome`. The loop is closed only if this stays high. Visible directly in the web UI's closure ledger (§14.6).
7. **Citation resolvability:** share of pointers in `stable` concepts resolving cleanly on refresh.
8. **Drift latency:** time from a source change to dependent concepts flagged stale.
9. **Distribution test:** a stranger reaches a running mesh on their own project in under an hour, editing config and concepts only (§13.7). Interim proxy: Phase 3 measured in pack/config work versus core edits.
10. **Gap closure (the self-evolving test):** share of consumer questions answerable from already-verified knowledge, tracked over time. Each derivation should happen once.
11. **Federation round trip:** cross-bundle questions answered with citations into two or more bundles; median inbox time-to-response. A dead inbox means a dead federation.
12. **Measured usefulness:** claims-hit with the bundle versus without, on the same questions, blind-graded (§18.4). The only measure here that can falsify the premise — which is exactly why it belongs.

---

---

## 21. Ecosystem and Prior Art

> Moved to [`docs/prior-art.md`](../docs/prior-art.md).

## 22. Closing Note

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## Appendix A. Legacy Draft → OKFM v0.2.1 Field Mapping

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).
