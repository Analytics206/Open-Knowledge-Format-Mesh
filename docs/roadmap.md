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
| 11 | Proving Ground B: SugarPaws3d Patron Analytics | *this document* |
| 12 | Federation — the OKF Mesh | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 13 | Drop-In Instantiation and Distribution | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 14 | The Mesh Viewer | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 15 | Roadmap | *this document* |
| 16 | Proving Ground A: arXiv Loop Retrofit | *this document* |
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

### 4.1 The harness (project_template)

Python harness engine wrapping AI/MCP tools with hooks, workflows, loops, and logging. Multiple "2nd brain" projects act as UIs over the same engine. A shared workflow library is planned; the loop defined here should become one of its reusable workflows.

### 4.2 arxiv_pipeline

MongoDB + Qdrant + MCP. ~1M papers across selected categories, built from the bulk dump, the API, and parsed PDFs (text and images into Qdrant). Scale and data type are exactly why this lives in dedicated stores. Bundles reference its records; they never duplicate them.

### 4.3 The current OKF

A markdown-file graph: documents related down to the line level, with sidecar files describing each file so an agent need not read everything, plus a refresh workflow that flags files needing update. §7.4 and §8 describe how these map onto — and extend — official v0.2.

### 4.4 The running research acquisition loop

Topic in → arXiv MCP vector search → gather and rank → evaluate each paper against the active project's system docs → human-in-the-loop summary (reject / trial) → documentation updates → detailed per-paper feedback (score + reasons) back to the arXiv MCP → everything logged. This loop already runs; §15 formalizes what it emits.

### 4.5 SugarPaws3d (port target)

Patron API data captured continuously for ~9 months. Curation in progress: system documentation, database schema and metadata, queries, business rules. Existing reports already produced for the business serve as a **golden answer set**. Target: an analytics chat system answering churn, acts, deacts, and revenue questions for a non-technical consumer. Details in §11.

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

## 11. Proving Ground B: SugarPaws3d Patron Analytics

Presented before the arXiv retrofit because it exercises the most profile surface. Delivery order remains §15.

### 11.1 The consumer

The end user is a non-technical business owner who mostly wants answers, not reports. That drives three requirements:

1. **Actor-aware defaults.** Each actor has a steward-configured default perspective per concept. She is never asked to choose between "billing churn" and "engagement churn" in those terms; the answer states the resolved perspective in plain language, and alternatives surface only when they materially change the number.
2. **Legible trust.** Attestation verdicts, staleness, and claim classification render as sentences.
3. **Attestation gating.** A failing attestation means no number displayed (§9.4).

### 11.2 Concepts and perspectives

Illustrative; the curated business rules are authoritative.

| Concept | Candidate perspectives | Question each answers |
|---|---|---|
| `churn` | billing (pledge ended / payment permanently failed) vs. engagement (no qualifying activity in N days) | "Who stopped paying?" vs. "Who stopped caring?" |
| `activation` | new patron vs. reactivation | "How is the top of funnel?" |
| `deactivation` | voluntary cancel vs. involuntary (payment failure) | "Why are we losing patrons?" |
| `revenue` | gross pledge vs. net of platform fees; booked vs. collected | "What was committed?" vs. "What landed?" |

Each `Perspective` concept names its owner-purpose and links to its `Rule`s, each of which links to an `Attested Computation`. Nobody owns churn; each perspective owns its view.

### 11.3 Declared vs. observed

```markdown
---
type: Rule
title: Churn — billing perspective
status: stable
generated: { by: curation_agent/claude-opus, at: 2026-07-20T10:00:00Z }
verified: { by: "human:geminia", at: 2026-07-22T14:00:00Z }
sources:
  - id: policy
    resource: /systems/business-rules.md#L40-L55
    okfm_role: defines
    okfm_captured: { version: "git:abc1234", at: 2026-07-20 }
  - id: impl
    resource: sys://sp3d-db/query/monthly_churn.sql
    okfm_role: implementation
    okfm_captured: { hash: "sha256:4b1e...", at: 2026-07-28 }
okfm_relations:
  - { predicate: perspective_on, target: /perspectives/churn-billing.md }
  - { predicate: implemented_by, target: /computations/churn-billing.md }
okfm_declared: policy
okfm_observed: impl
okfm_reconciliation:
  status: unreviewed        # unreviewed | consistent | material_mismatch | acknowledged
  method: run both variants over the same months; diff patron sets
---

# Declared

A patron churns when their pledge is cancelled or payment permanently fails.[^policy]

# Observed

The monthly query counts a patron as churned only after the final failed retry,
and nets out same-month cancel-and-repledge.[^impl]
```

`okfm_declared` and `okfm_observed` are `sources[].id` references — the same keyed-join discipline official uses for footnotes, so reordering sources cannot silently misattribute.

Nine months of raw captures make reconciliation **testable**: run both variants over the same history and characterize the difference patron by patron. This is deterministic verification on a dataset that already exists.

### 11.4 Golden answer set

The reports already produced for the business encode correct numbers under the steward's definitions. They are registered as concepts with `okfm_role: golden_reference`, and reconciliation targets them: a new Attested Computation must reproduce the trusted report before it is `verified`. The answer key and the exam both already exist.

### 11.5 Question workflows

**MRR bridge.** `new + reactivation + upgrades − downgrades − voluntary deacts − involuntary deacts`, each component an attested computation under a stated perspective. The bridge is *attested*; "the spring promo drove reactivations" is *inferred* and labeled.

**Churn driver check.** Resolve perspective → check freshness and `data_gap` flags → decompose by voluntary/involuntary, tenure cohort, pledge tier → retrieve prior `Decision` and `Answer` precedents → rank explanations → record the resulting `Decision`, and later its `Outcome`.

### 11.6 Questions produce knowledge — the consumer is a curator

The actor split is about **authority, not write access**. The steward authors and approves meaning-family concepts and is the only `human:` verifier; the consumer never edits a rule. But every consumer interaction writes to the bundle:

1. **Gap-triggered curation.** A question landing on under-documented territory triggers derivation (schema introspection, query inventory, targeted analysis), producing concepts as `status: draft` with `generated.by` set to the agent and no `verified` entry — unverified by construction, per official trust tiers. They enter the steward's review queue; once verified and `stable`, the next such question answers from knowledge instead of derivation.
2. **Demand signal.** Question history is telemetry: which concepts get asked about, which answers draw follow-ups, which questions go unanswered. Curation priority follows demand.
3. **Precedents.** Accepted answers persist as `Answer` concepts. Past facts become templates for future facts.

Same loop as research acquisition: question = goal, gap-fill = discovery + evaluation, steward review = human gate, accepted answer = published knowledge, follow-up behavior = feedback.

### 11.7 Discovery adapter

The port's discovery step is not vector search but source understanding: schema introspection, query inventory, capture-coverage profiling (finding `data_gap`s across the 9-month history). It implements the same `DiscoveryAdapter` interface as the arXiv MCP (§13) — same loop, different evidence source.


---

---

## 12. Federation — the OKF Mesh

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 13. Drop-In Instantiation and Distribution

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 14. The Mesh Viewer

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 15. Roadmap

Four slices, each end-to-end. No phase builds platform without a user-visible query working at its end.

### Phase 1 — Baseline adoption + arXiv retrofit

Scope: migrate the current OKF to conformant v0.2 using an **existing migrator** rather than a hand-written one (§21.2); the §7.4 sidecar audit, applying the §7.7 admission test to every existing concept; OKFM profile keys frozen; loop-family types; telemetry 1.0; initial reason vocabulary. Validation is **adopted, then extended**: an existing conformance validator and CI action handle official §11; a second OKFM pass adds vocab-checked predicates and reason codes, pointer resolvability, and the strip test. Retrofit the running loop to write concepts and telemetry, send stored `Feedback` to the arXiv MCP, and check `already_evaluated` before evaluating a candidate. Stand up the benchmark harness (§18.4) and take a baseline reading.

Also in Phase 1, per [DR-0003](decisions/0003-phase-ordering.md) and
[DR-0010](decisions/0010-okfm-self-hosts-as-a-mesh.md): **federation's addressing half** —
the registry bundle, `OKF Member` concepts, cross-bundle references with commit pinning, and
a viewer that renders more than one bundle. It costs almost nothing because OKFM's own
repository is already a mesh of three bundles, and it proves the project's central metaphor
now rather than at the end.
**Exit:** "Why did we reject paper X?" answered from the bundle alone; one run fully reconstructable from telemetry; bundle passes official conformance in CI with every `okfm_` key stripped; a first benchmark run recorded, whatever it says.

### Phase 2 — Extraction into a distributable project

Scope: §13 in full — split core / packs / config / bundle; move the loop into
`core/workflows/`; extract `packs/research/`; write `okfm.json` and its schema;
convention-based discovery; the three runtime modes (§13.6); the domain-word CI grep;
README quickstart, `templates/`, `examples/minimal/`, `okfm-guide/`, and `okfm view` (§14).
**Exit:** a toy second domain stood up via pack + config with zero core edits, **and**
a first pass at the distribution test (§13.7) — someone other than the builder, or the
builder on a clean machine with only the README, reaches a running mesh in under an
hour.

### Phase 3 — SugarPaws3d port

Scope: `sys://` resolver for the patron DB and API captures; discovery adapter; curated schema/queries/rules ingested as meaning-family concepts; churn/acts/deacts/revenue concepts, perspectives, rules; **Attested Computations with real attesters** for each figure; golden-report reconciliation; declared-vs-observed reconciliation over the 9-month history; the §11.5 question workflows; actor-aware defaults and plain-language trust rendering; the gap → propose → verify loop; drift detection live on `sys://` pointers.
**Exit:** one business question answered with a stated perspective, a **passing attestation**, resolvable citations, claim classification, and the answer recorded as an `Answer` concept. One attested computation reconciled against its existing trusted report. One declared/observed mismatch found (or consistency verified). One consumer question driving the full gap → propose → verify cycle. A benchmark run (§18.4) on real business questions, graded against the golden reports.

### Phase 4 — Federation, the negotiation half

The addressing half — registry bundle, `OKF Member` concepts, cross-bundle references,
commit pinning, a multi-bundle viewer — landed in Phase 1, because OKFM's own repository is
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
grounds that SugarPaws3d sits on two ownership seams and should be born federated. The
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

**Reverse this** if the two SugarPaws3d domains turn out to have distinct accountable owners
today. That is the §12.1 split criterion, and it beats sequencing convenience.

---

---

## 16. Proving Ground A: arXiv Loop Retrofit

Formalization, not new capability. The loop already runs; Phase 1 makes it write conformant concepts.

1. Inspect real logs; derive loop-family body conventions and reason codes from what the loop already emits.
2. Write `Goal`, `Evidence`, `Evaluation`, `Decision`, `Experiment`, `Outcome`, `Feedback` concepts during runs, with `generated` set to the agent actor and `verified` added only on human review.
3. Telemetry record per run; concepts carry `okfm_run_id`.
4. `Feedback` concepts become the payload sent to the arXiv MCP — same content as today, now stored and coded.
5. `already_evaluated` guard: check the bundle before evaluating a returned paper.
6. Optional backfill of recent runs from existing logs to seed the store. **Backfill honesty rule:** never synthesize a `verified` entry, and never attribute `generated.by` to a human for content written before the field existed. Use `process:okfm-backfill`, leaving backfilled concepts correctly *unverified* under official trust tiers. A faked human review is worse than an honest gap, because it silently promotes a trust tier that nobody earned.
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
4. **Feedback consumption at the arXiv MCP.** Stored feedback is Phase 1; does the MCP *use* it (filter/boost) now, or store until volume justifies ranking changes?
5. **Telemetry granularity.** Full prompts/outputs per step, or hashes plus concept refs only? (Lean: refs and hashes; bodies are already concepts.)
6. **Registry stewardship.** The registry is a bundle too — who owns the map when a second steward exists?
7. **Transitive feedback.** When bundle A's feedback concerns B's concept that itself cites C, does A file to B only? (Lean: yes — ownership chains stay linear.)
8. **Capture gaps as concepts.** Should `data_gap` be a concept (period + affected metrics) rather than only a reason code, so gaps propagate staleness like drift?
9. **Effective dating.** Rules need `effective_from/to` for SugarPaws3d. Do metrics? Perspectives? Start with rules and see what breaks.
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
6. **Outcome closure:** share of trial decisions that eventually receive an `Outcome`. The loop is closed only if this stays high. Visible directly in the viewer's closure ledger (§14.6).
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
