# OKFM v0.2.1 — Specification

Normative. What makes a bundle a legal OKFM bundle, and what the scaffolding must do. This is the document an adopter needs; the other three explain how it got this way and where it is going.

### A distributable knowledge-mesh scaffolding for OKF bundles

**Version:** OKFM v0.2.1
**Baseline:** Open Knowledge Format (OKF) v0.2 — GoogleCloudPlatform/knowledge-catalog
**Concept:** Actionable Knowledge — evidence that changed what a project knows or does, preserved so the *why* stays queryable
**Date:** 2026-07-31
**Audience:** The builder, adopters of the scaffolding, and the AI agents working the codebase

### Status of this document

**A working specification, not a standard.** It was written to think the system through
before building it, and parts of it are wrong in ways that only become visible once
something runs.

Where this document and the implementation disagree, **the implementation is right.** The
document gets updated and a record goes in [`docs/decisions/`](../docs/decisions/index.md)
saying what changed and why. An unmet clause here is not a defect in the code.

This is §3.10 — *the spec follows the implementation* — meant literally. Treating a clause
as binding because it is written down inverts it, and produces decision records for things
that should just be decided.

Read it for the shape of the system and the reasoning behind it. The `okfm_` key rules, the
strip test, and the vocabularies in §7 and §10 are the parts that genuinely must hold,
because other people's bundles depend on them.

### Versioning policy

OKFM versions are `<okf-major>.<okf-minor>.<okfm-revision>`. **The first two numbers name the OKF baseline this release targets; the third is OKFM's own revision against it.**

- `v0.2.1` — first OKFM revision targeting OKF v0.2.
- `v0.2.2` — further OKFM work, same baseline.
- `v0.3.0` — retarget to OKF v0.3 when it lands.

A reader never has to ask which OKF version a given OKFM release speaks. Document revisions are not tracked separately; the OKFM version is the only version that matters.

---

## Where everything lives

**Section numbers are global across the OKFM document set.** They are preserved from the unified v0.2.1 specification, so a reference like §12.3 means the same thing in every file. Gaps in this document's numbering are intentional — the map says where each section lives.

| # | Section | Lives in |
|---|---|---|
| 0 | What This Release Changes | [`docs/rationale.md`](../docs/rationale.md) |
| 1 | What Changed from v2, and Why | [`docs/rationale.md`](../docs/rationale.md) |
| 2 | Vision | [`docs/rationale.md`](../docs/rationale.md) |
| 3 | Design Principles | *this document* |
| 4 | Existing Assets | [`docs/roadmap.md`](../docs/roadmap.md) |
| 5 | Architecture Overview | *this document* |
| 6 | Baseline: What We Inherit from OKF v0.2 | *this document* |
| 7 | The OKFM Profile | *this document* |
| 8 | Evidence, Drift, and Staleness | *this document* |
| 9 | Governed Numbers: Attested Computation | *this document* |
| 10 | Workflow Instrumentation | *this document* |
| 11 | Proving Ground B: SugarPaws3d Patron Analytics | [`docs/roadmap.md`](../docs/roadmap.md) |
| 12 | Federation — the OKF Mesh | *this document* |
| 13 | Drop-In Instantiation and Distribution | *this document* |
| 14 | The Mesh Viewer | *this document* |
| 15 | Roadmap | [`docs/roadmap.md`](../docs/roadmap.md) |
| 16 | Proving Ground A: arXiv Loop Retrofit | [`docs/roadmap.md`](../docs/roadmap.md) |
| 17 | Deferred — Parking Lot with Re-entry Triggers | [`docs/roadmap.md`](../docs/roadmap.md) |
| 18 | Evaluating the Bundle | *this document* |
| 19 | Open Questions | [`docs/roadmap.md`](../docs/roadmap.md) |
| 20 | Success Measures | [`docs/roadmap.md`](../docs/roadmap.md) |
| 21 | Ecosystem and Prior Art | [`docs/prior-art.md`](../docs/prior-art.md) |
| 22 | Closing Note | [`docs/rationale.md`](../docs/rationale.md) |
| A | Legacy Draft → OKFM v0.2.1 Field Mapping | *this document* |

---

## 0. What This Release Changes

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 1. What Changed from v2, and Why

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 2. Vision

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## 3. Design Principles

1. **Conformance first.** Anything expressible in official OKF v0.2 is expressed that way. Invention requires a stated reason. Every OKFM addition must survive being read by an official consumer that ignores it.
2. **Memory before learning.** At solo scale, feedback volume cannot train rankers; it can absolutely power organizational memory. Design every record to be queryable first.
3. **Files are the substrate.** Anything that fits in files lives in files. Anything that does not — a million papers, raw API history — lives in its native store and is referenced.
4. **Record signals, not verdicts.** (Adopted from official OKF §5.1.) Store the objective facts that support a judgement; let consumers derive the judgement. Scores are subjective, unportable, and go stale. This applies to OKFM's own flags — none of trust tier, staleness, drift, or reconciliation status is ever frozen into a file. A stored verdict is a stored opinion with an expiry date.
    **Where they are derived differs by cost.** Trust tier, staleness, and reconciliation are pure functions of frontmatter already in hand, so they are computed on every read. Drift requires re-resolving a pointer against the outside world, so it is **observed during the build and cached**, and nothing on the read path resolves it (§8.3). Caching an observation is not storing a verdict: *this pointer hashed to X at time T* does not become false later, and the verdict is still derived from it.
5. **Evidence pointers reach into systems, not just files.** A source may be a file span, another concept, an external store record, a database column, a query, or a captured payload.
6. **Drift detection is the refresh workflow, generalized.** When the pointed-at thing changes, dependent concepts go stale.
7. **Schema stability is a feature.** Telemetry and reason codes are versioned, controlled vocabularies. Six months of logs are an asset only if comparable.
8. **Never collapse distinct trust events.** Official separates *verification* (the definition still matches policy) from *attestation* (this run produced the value the sanctioned way). OKFM separates *evaluation* from *outcome* (good ideas fail; mediocre ideas succeed). Both distinctions are load-bearing.
9. **Declared truth and observed truth are separate assertions,** linked by a reconciliation status.
10. **The spec follows the implementation.** Every element must be justified by what the running loop emits or what the port demonstrably needs. Speculation goes to §16.
11. **Split on ownership, not size.** Bundle boundaries follow accountability seams (§12.1).
12. **Distributable before ported.** If a stranger cannot stand it up from a README, it is not modular — it is merely tidy (§13.7).
13. **Write down what the code cannot say.** A concept that restates what a source
    already states is a maintenance liability that measurably buys nothing, and can
    actively mislead by dropping detail the source had. A concept that records the
    *why* — the rationale, the rejected alternative, the decision behind a number —
    answers questions the source cannot. Evidence: §21.1.
14. **No duplicate knowledge.** Knowledge lives in exactly one authoritative place
    and is referenced everywhere else. Rendered views, exports, and caches are
    derivations, marked as such and never edited. Two copies of a fact means one of
    them is silently wrong later (§21.3).

---

---

## 4. Existing Assets

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 5. Architecture Overview

```text
+---------------------------------------------------------------+
|                    Harness workflows                          |
|  research acquisition | question answering | curation         |
|  refresh/drift | reconciliation | attestation gate            |
+------------------------------+--------------------------------+
                               |  reads/writes concepts,
                               |  assembles context,
                               |  emits telemetry
                               v
+---------------------------------------------------------------+
|            OKF bundles (files, git) — v0.2 + OKFM profile       |
|  concepts | index.md | log.md | references/ (telemetry,       |
|  vocab, attesters, computations, edges)                       |
+------------------------------+--------------------------------+
                               |  sources[].resource
                               |  (by reference, never by copy)
                               v
+---------------------------------------------------------------+
|                External stores and systems                    |
|  arxiv_pipeline (Mongo+Qdrant via MCP) | SugarPaws3d patron   |
|  DB/API captures | project repos and docs | SQL engines       |
+---------------------------------------------------------------+
```

- **Harness** = runtime, context assembler, telemetry producer, attestation gate. No separate service tier.
- **Bundles** = the knowledge. One per ownership domain; portable, diffable, reviewable in git.
- **External stores** = evidence at scale. Authoritative for their bytes; bundles are authoritative for meaning, decisions, and history.
- **MCP** = the API surface.

---

---

## 6. Baseline: What We Inherit from OKF v0.2

Summarized so this document is usable without the official spec open. Official spec is normative where they differ.

### 6.1 Bundle structure

A directory tree of markdown files. `index.md` (directory listing, progressive disclosure) and `log.md` (chronological update history) are reserved at any level; all other `.md` files are concept documents. A `references/` subdirectory conventionally holds mirrored external material, run instructions, and code. Distributed as a git repo (recommended), archive, or subdirectory.

### 6.2 Concept documents

UTF-8 markdown: YAML frontmatter + body. `type` is the only always-required key, is not centrally registered, and consumers must tolerate unknown values. Recommended: `title`, `description`, `resource`, `tags`. Conventional body headings: `# Schema`, `# Examples`, `# Computation`.

### 6.3 Provenance and trust

- `sources` — materials the concept derives from. Each entry requires `resource` (absolute URL, bundle-relative path, relative path, or a scope descriptor); optional `id`, `title`, and the credibility signals `author`, `usage_count`, `last_modified`, framed by a `usage_window` sibling.
- Per-claim attribution uses markdown footnotes keyed to `sources[].id` — keyed, not positional, so agent rewrites cannot silently misattribute.
- `generated: { by, at }` — how current content was produced.
- `verified: [{ by, at }]` — who or what confirmed it. Distinct from `generated` because the writer need not be the confirmer. A bare mapping counts as a one-element list.
- Actor convention: `<producer>/<version>`, `human:<id>`, `process:<id>`.
- Trust tiers are **derived**, not stored: no `verified` ⇒ unverified; non-human verifiers ⇒ machine-confirmed; a `human:` verifier ⇒ human-reviewed.

### 6.4 Lifecycle

- `status: draft | stable | deprecated` (absent ⇒ stable).
- `stale_after: YYYY-MM-DD` — absolute date; stale when today is on or after it.

### 6.5 Links

Standard markdown links, bundle-relative (`/path.md`, recommended) or relative. Links are **untyped** — the relationship kind lives in surrounding prose. Consumers must tolerate broken links.

### 6.6 Attested Computation

A concept type carrying a sanctioned way to compute a value: `runtime`, typed `parameters`, the computation (inline under `# Computation` or a `computation` file path), an `executor` (run instructions + declared `receipt` fields), and an `attester` (deterministic, no-LLM code that inspects a receipt and returns a verdict). See §9.

### 6.7 Conformance

Conformant if every non-reserved `.md` file has parseable frontmatter with a non-empty `type`, and reserved files follow their structure. Consumers must not reject bundles for missing optional fields, unknown types, unknown keys, broken links, or missing indexes.

**The consequence OKFM depends on:** producers may add any keys, and consumers must preserve unknown keys and must not reject documents carrying them. The OKFM profile is legal by construction.

---

---

## 7. The OKFM Profile

### 7.1 Extension rules

1. Every OKFM-specific frontmatter key is prefixed `okfm_`. Greppable, collision-free, obviously optional to an official consumer.
2. An OKFM key never contradicts an official key. Where official has a field, OKFM uses it (`status`, not `okfm_state`).
3. OKFM keys may appear inside official structures (e.g. `okfm_role`, `okfm_captured` within a `sources` entry). Official consumers preserve them.
4. **Every OKFM concept is readable without OKFM tooling.** The body carries the human-readable content; `okfm_` keys carry machine structure. Strip every `okfm_` key and the bundle is still a useful OKF bundle.
5. High-volume machine records are **not** `.md` concepts. Telemetry, edge indexes, and vocabularies are YAML/JSONL under `references/`, invisible to conformance (which governs `.md` files) and absent from the concept graph.

### 7.2 Identity

Official concept ID is the file path minus `.md`. OKFM adopts this. Layout encodes type, so paths stay meaningful:

```text
<bundle>/
  index.md
  log.md
  goals/            evidence/        evaluations/
  decisions/        experiments/     outcomes/
  feedback/inbox/   feedback/outbox/ answers/
  concepts/         perspectives/    rules/
  computations/     systems/
  references/
    telemetry/runs/<run_id>.yaml     # YAML, not concepts
    vocab/reason_codes.yaml
    vocab/predicates.yaml
    edges/edges.jsonl                # line-level and high-volume edges
    attesters/<name>.py
    computations/<name>.sql
```

Because path IDs break when files move, any concept referenced across bundles or cited in telemetry SHOULD carry a stable key:

```yaml
okfm_key: eval-arxiv-2607-01234-spec-decode
```

`okfm_key` is the join key of last resort — for reconnecting references after a reorganization, not a replacement for path IDs.

### 7.3 Typed relations

Official links are untyped by design. OKFM needs typed edges for impact analysis and graph traversal, so it carries both:

```yaml
okfm_relations:
  - predicate: evaluates
    target: /evidence/arxiv-2607-01234.md
  - predicate: serves
    target: /goals/spec-decode-latency.md
```

...alongside ordinary markdown links in the body. An official consumer sees links; an OKFM consumer sees predicates. Predicates come from `references/vocab/predicates.yaml`, grouped into families with defined domain and range:

- **Evidential:** `supports`, `contradicts`, `evaluates`, `derived_from`
- **Structural:** `serves`, `part_of`, `depends_on`, `implements`, `implemented_by`
- **Semantic:** `perspective_on`, `defines`, `measures`, `differs_from`
- **Lifecycle:** `supersedes`, `superseded_by`, `resulted_in`

Freeform predicates are rejected by the validator. High-volume or line-level edges go to `references/edges/edges.jsonl` rather than frontmatter.

### 7.4 Progressive disclosure: sidecars reconsidered

Official achieves progressive disclosure with `description` in frontmatter plus generated `index.md` per directory. Where a current sidecar is only a summary, it collapses into exactly that — one file class deleted.

Sidecars survive only where they carry more than a summary (per-line anchors, extraction notes, retrieval hints). When they do, they live at `references/sidecars/<mirrored-path>.md` and are pointed to by:

```yaml
okfm_sidecar: /references/sidecars/tables/orders.md
```

**Action for Phase 1:** audit existing sidecars against this test before migrating. Anything that is summary-only becomes `description` + generated index.

### 7.5 OKFM concept types

Official `type` values, Title Case, following official convention. Two families.

**Loop family** — workflow residue. Nothing in official OKF covers this; `log.md` is a prose changelog, not structured telemetry.

| `type` | Records |
|---|---|
| `Goal` | An acquisition or question goal: topic/question, constraints, project served |
| `Evidence` | A pointer record: what was gathered, from where, what was seen at capture |
| `Evaluation` | Assessment of evidence against a goal: signals, reason codes, recommendation |
| `Decision` | The human call: reject / monitor / trial / adopt, with rationale |
| `Experiment` | Hypothesis, baselines, success metrics, guardrails |
| `Outcome` | What actually happened: measurements, adoption status, durable value |
| `Feedback` | Structured signal sent to a source or another bundle (§12.4) |
| `Answer` | A delivered answer: resolved perspective, method, classified claims, citations — a precedent |

**Meaning family** — what a domain's knowledge is made of.

| `type` | Records |
|---|---|
| `Concept` | A business or technical concept: churn, activation, net revenue |
| `Perspective` | A named viewpoint on a concept: whose, and what question it answers |
| `Rule` | A definition under a perspective, with declared/observed/reconciliation (§11.3) |
| `Attested Computation` | Official type: the sanctioned computation behind a number (§9) |
| `Metric` | The meaning of a measurable; links to its Attested Computation |
| `Source System` | A registered system — the anchor for `sys://` pointers |
| `OKF Member` | A bundle registered in the federation registry (§12.2) |

Domain packs (arXiv, subscription business, software engineering) add reason codes and body conventions. They do not add frontmatter families.

### 7.6 Worked example

```markdown
---
type: Evaluation
title: "Paper 2607.01234 against the speculative-decoding goal"
description: Promising method; deployment profile mismatch is the open risk.
status: stable
tags: [research, inference, latency]
generated: { by: research_agent/claude-opus, at: 2026-07-30T18:45:00Z }
verified: { by: "human:geminia", at: 2026-07-31T09:12:00Z }
sources:
  - id: paper
    resource: store://arxiv_pipeline/papers/2607.01234
    title: "Draft-and-verify decoding at small batch sizes"
    okfm_role: subject
    okfm_captured: { hash: "sha256:9f2c...", at: 2026-07-30 }
  - id: arch
    resource: /systems/inference-architecture.md#L120-L164
    okfm_role: constraint_source
    okfm_captured: { version: "git:abc1234", at: 2026-07-30 }
okfm_key: eval-arxiv-2607-01234-spec-decode
okfm_relations:
  - { predicate: evaluates, target: /evidence/arxiv-2607-01234.md }
  - { predicate: serves, target: /goals/spec-decode-latency.md }
okfm_reason_codes: [promising_monitor, infra_mismatch]
okfm_run_id: run_01K7Z8...
---

# Assessment

The method reduces draft-verify overhead at batch sizes matching our serving
profile.[^paper] Our current architecture pins KV cache per replica, which the
method assumes is elastic.[^arch]

# Recommendation

Trial behind a flag; the memory profile is the thing to measure.

[^paper]: Draft-and-verify decoding at small batch sizes
[^arch]: Inference architecture, lines 120-164
```

Every official field does official work. Every `okfm_` key is ignorable. Strip them and a generic OKF consumer still gets a titled, described, sourced, human-verified concept.

### 7.7 Concept admission test

Before writing a concept, answer: **does this say something its sources cannot?**

| Verdict | Example | Action |
|---|---|---|
| **Admit** | Why a threshold is 1,000; why an approach was rejected; which perspective a number uses; what a trial produced | Write the concept |
| **Reject** | Restating a schema the catalog already exposes; paraphrasing a query; summarizing a README | Cite the source; write nothing |
| **Attest, don't summarize** | The definition of churn, the revenue calculation | Write an Attested Computation carrying the computation (§9) |

The failure mode this prevents is measured, not hypothetical (§21.1): a concept that
summarized a validator was *worse* than the source, because the summary had dropped
the detail the question needed, and the agent stopped at the concept instead of
reading on. A concept that stands between an agent and a better answer is a
regression.

Three corollaries:

1. **Prefer pointing to summarizing.** A concept whose value is orientation should
   say where to look and why it matters, then link — not restate.
2. **Where a summary is unavoidable, mark its limits.** If a concept abstracts a
   source, say so in the body and cite the source with `okfm_role: implementation` so
   a reader knows detail exists downstream.
3. **Attestation beats summary for numbers.** An Attested Computation cannot drift
   from the query, because it *carries* the query and proves what ran (§9.1).

This test applies hardest to the meaning family during SugarPaws3d curation, where
the temptation to document every table is strongest and the payoff is lowest.

---

---

## 8. Evidence, Drift, and Staleness

### 8.1 Pointer schemes inside `sources`

Official `sources[].resource` accepts an absolute URL, a bundle-relative path, a relative path, or a scope descriptor. OKFM rides inside that field rather than building a parallel system:

```text
/path/to/concept.md                       # bundle-relative (official)
/path/to/file.md#L120-L164                # file span — OKFM line anchoring
https://...                               # external reference (official)
all queries in project X                  # scope descriptor (official)
store://arxiv_pipeline/papers/2607.01234  # external store record  (OKFM scheme)
sys://sp3d-db/table/patrons               # live system element    (OKFM scheme)
sys://sp3d-db/column/pledges.amount_cents
sys://sp3d-db/query/monthly_churn.sql
sys://sp3d-api/capture/2026-06
```

An official consumer sees a resource URI it may not resolve — which conformance requires it to tolerate. An OKFM consumer resolves it through the registered `Source System` concept.

### 8.2 What was seen at capture

Every OKFM pointer records what it saw, as an extension inside the source entry:

```yaml
sources:
  - id: churn-sql
    resource: sys://sp3d-db/query/monthly_churn.sql
    okfm_role: implementation
    okfm_captured:
      hash: "sha256:4b1e..."
      version: "git:abc1234"      # or schema version, or capture date
      at: 2026-07-30
```

`okfm_role` names why the source is cited (`subject`, `implementation`, `constraint_source`, `golden_reference`, `defines`). `okfm_captured` is what makes content drift detectable.

### 8.3 Two orthogonal staleness mechanisms

Official `stale_after` and OKFM drift answer different questions; use both.

| | Official `stale_after` | OKFM drift |
|---|---|---|
| Question | Has enough time passed that this deserves review? | Has the thing this depends on actually changed? |
| Mechanism | Date comparison, no resolver | Re-resolve pointer, compare `okfm_captured` |
| Cost | Free | One resolution per pointer |
| Good for | Policy-driven review cadence | Schema changes, query edits, superseded concepts |

### 8.4 The drift workflow

1. A refresh run re-resolves every OKFM pointer in scope.
2. Current hash/version differs from `okfm_captured` ⇒ pointer marked drifted.
3. The citing concept is reported stale, with the drifted source `id` and reason. **Staleness is derived at read time, not written into the concept** (§3.4): the stored signal is `okfm_captured`, and the flag is recomputed from it. A `okfm_stale: true` frozen into a file is wrong the moment the source is fixed.
4. Drift propagates along `okfm_relations` (bounded traversal): concepts depending on stale concepts inherit the flag.
5. Stale concepts enter a review queue workflow: re-validate (refresh `okfm_captured`, add a `verified` entry), supersede (`status: deprecated` + `supersedes` relation), or acknowledge.

For files this is today's behavior. For `sys://` pointers it is the new capability: edit the SugarPaws3d churn query and every rule citing it goes stale automatically.

---

### 8.5 Push, don't wait: the injected index

Measured evidence (§21.4) is unambiguous on where the efficiency comes from: not from
a bundle existing, but from a compact typed index being **injected before the agent
acts**. An agent left to discover a bundle often does not, and answers from training
data instead — accuracy without tools drops to a fraction of what injection achieves.

Every OKFM run therefore opens with an index injection:

```text
<okfm>
Knowledge: 14 concepts in this mesh

Recent (log.md):
  2026-07-28 — churn rule reconciled against Q2 report

  /computations/churn-billing.md   [Attested Computation]  verified · fresh
  /rules/churn-billing.md          [Rule]                  verified · fresh
  /perspectives/churn-billing.md   [Perspective]           verified
  /concepts/churn.md               [Concept]               verified
  /decisions/trial-2607-01234.md   [Decision]              unverified · stale
  ...
</okfm>
```

Rules:

1. **Path, type, one-line description, derived trust and staleness badges.** Bodies
   are pulled on demand; the index is a map, not the content.
2. **Budgeted.** `max_concepts` caps the index; `priority_types` orders it. For a
   business mesh, `[Attested Computation, Rule, Metric, Perspective]` — the concepts
   that govern numbers come first.
3. **Derived at injection time** (§3.4). Trust tier and staleness are computed, never
   read from a stored field.
4. **Zero overhead when absent.** No concepts found ⇒ inject nothing and exit
   immediately. This is what makes OKFM safe to leave enabled everywhere.
5. **Neighbor surfacing on read.** When a concept is read, surface its typed
   neighbors — `implemented_by`, `perspective_on`, `supersedes` — rather than every
   link equally. Typed relations (§7.3) make this more useful than a flat link list.

The index is a derivation, never a second home for knowledge (§3.14): it is rebuilt
from the bundle every time and is never edited or committed.

---

---

## 9. Governed Numbers: Attested Computation

This is the most valuable thing adopted from official v0.2, and it directly solves the failure mode that motivates the whole SugarPaws3d project — a model re-deriving the semantic layer on every question and guessing the definition.

### 9.1 Why it is stronger than v2's design

v2 governed metrics by *convention*: the workflow was supposed to use the registered query. Attested Computation makes it *mechanical*:

- The computation is a standalone concept with a declared `runtime` and typed `parameters`.
- The agent may supply **values for declared parameters only**. It must not author or edit the computation.
- The `executor` returns a receipt containing evidence of what actually ran (e.g. `job_id`, `executed_sql`, `result`).
- The `attester` is deterministic, LLM-free consumer-side code that re-derives the expected binding and compares it against the receipt.
- A rewritten query, a swapped computation file, or a mutated dependency fails the check.

"Did the sanctioned thing run" becomes a comparison, not a judgement call.

It also answers the measured failure mode in §21.1 directly. The one question the
bundle *lost* was lost because a concept summarized a source and dropped the detail
that mattered. An Attested Computation cannot fail that way: it does not summarize
the computation, it carries it — and the attester proves the carried version is what
executed. For every number a business consumer sees, this is strictly safer than any
prose description of how the number is produced.

### 9.2 One computation per figure

Churn, acts, deacts, and revenue are four Attested Computations, not one. Each verifies, goes stale, and attests independently. A `Metric` concept explains meaning and links to its computation; readable business documents link to several.

### 9.3 SugarPaws3d shape

```markdown
---
type: Attested Computation
title: Monthly churned patrons (billing perspective)
description: Patrons whose pledge ended or whose payment permanently failed in a month.
status: stable
runtime: bigquery
parameters:
  - { name: month, type: string, required: true }
executor:
  resource: /references/skills/run-on-warehouse.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: /references/attesters/churn_billing.py
generated: { by: curation_agent/claude-opus, at: 2026-07-20T10:00:00Z }
verified: { by: "human:geminia", at: 2026-07-22T14:00:00Z }
stale_after: 2026-10-22
sources:
  - id: rules-doc
    resource: /rules/churn-billing.md
    okfm_role: defines
okfm_relations:
  - { predicate: implements, target: /rules/churn-billing.md }
okfm_perspective: /perspectives/churn-billing.md
---

# Computation

    SELECT COUNT(DISTINCT patron_id) AS churned
    FROM patron_pledge_events
    WHERE event_month = @month
      AND event_type IN ('pledge_ended', 'payment_failed_final')

Counts each patron once per month, per the billing perspective.[^rules-doc]

[^rules-doc]: Churn, billing perspective
```

### 9.4 The attestation gate

Question-answering workflows must:

1. Discover the computation by `type` and perspective link.
2. Supply parameter values only.
3. Execute via the executor; capture the receipt.
4. Run the attester over the receipt.
5. **Refuse to display a failing attestation.** Warn or refuse when `today >= stale_after`.
6. Surface the verdict so trust is visible.

This is what makes an answer for a non-technical consumer trustworthy without her having to audit anything: the number either attested or it did not.

### 9.5 Verification, attestation, evaluation, outcome

Four distinct records; never collapse them.

| Record | Question | Cadence | Stored? |
|---|---|---|---|
| `verified` | Does the definition still match policy? | Slow, doc-level | In bundle |
| Attestation | Did this run produce the value the sanctioned way? | Per call | Runtime only |
| `Evaluation` | Does this evidence look useful for the goal? | Per candidate | In bundle |
| `Outcome` | Did it produce durable value? | Post-trial | In bundle |

The first two are official; the last two are OKFM. The pattern is identical — appealing and correct are different, and only one of them survives contact with reality.

---

---

## 10. Workflow Instrumentation

### 10.1 Versioned telemetry

One YAML record per run under `references/telemetry/runs/`. Not a concept — it does not belong in the concept graph and would swamp it.

```yaml
telemetry_schema: "1.0"
run_id: run_01K7Z8...
workflow: research_acquisition@2.3
trigger: /goals/spec-decode-latency.md
started_at: 2026-07-30T18:30:00Z
finished_at: 2026-07-30T18:52:00Z

context:
  assembled_from:
    - /goals/spec-decode-latency.md
    - /systems/inference-architecture.md#L1-L400
    - /decisions/reject-paged-kv.md
  tokens_in: 41200

steps:
  - id: discover
    tool: mcp://arxiv/search
    params_hash: "sha256:..."
    candidates_returned: 40
  - id: evaluate
    model: reasoning-model-id
    produced: [/evaluations/arxiv-2607-01234.md]
  - id: human_review
    decisions: [/decisions/trial-2607-01234.md]
    edit_distance: moderate        # none|light|moderate|rewrite

attestations: []                   # question workflows record verdicts here
cost: { usd: 1.84, tokens_total: 195000, latency_s: 1320 }
produced: [/evaluations/..., /decisions/...]
feedback_sent: [/feedback/outbox/arxiv-2607-01234.md]
```

Workflow revisions may add fields; renaming or repurposing one requires a `telemetry_schema` bump. This is the cheapest decision in the system and the one protecting every six-months-later query.

Concepts link back with `okfm_run_id`. Retention: indefinite for now — small text files.

### 10.2 Controlled reason codes

`references/vocab/reason_codes.yaml`, layered core + domain packs. Carried as `okfm_reason_codes` on evaluations, decisions, and feedback, alongside freeform prose in the body.

```yaml
core:
  - already_evaluated
  - insufficient_evidence
  - superseded_by_better
  - out_of_scope
research:
  - wrong_scale
  - incompatible_architecture
  - infra_mismatch
  - no_novelty_vs_adopted
  - promising_monitor
subscription:
  - definition_conflict
  - grain_mismatch
  - data_gap
  - stale_source
  - seasonal_expected
```

Adding a code is one line and one commit. **Changing a code's meaning is forbidden** — add a new one and deprecate the old. This is what makes historical logs comparable.

### 10.3 Claim classification

Answers and evaluations classify each substantive claim in the body, so a reader can tell a computed figure from a hypothesis:

- **Attested** — produced by an Attested Computation with a passing verdict.
- **Calculated** — computed from bundle data without attestation.
- **Stated** — asserted by a cited source.
- **Inferred** — the model's reasoning over the above.
- **Hypothetical** — explicitly speculative.

Rendered in the body as plain language for non-technical readers, not as a metadata panel.

---

---

## 11. Proving Ground B: SugarPaws3d Patron Analytics

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 12. Federation — the OKF Mesh

Official OKF stops at the bundle: no registry, no cross-bundle addressing, no ownership model, no inter-bundle channel. Federation is the largest OKFM addition and is built entirely from official primitives plus `okfm_` keys.

### 12.1 Motivation and split criterion

Two pressures, one design. **Scale:** a single bundle eventually outgrows progressive disclosure; bounded bundles keep each one navigable. **Ownership:** "who owns this data" has one durable answer — bounded stores with accountable owners.

This is domain-mesh thinking applied to knowledge: each bundle is a bounded context with an owner, exposed through a defined interface; cross-domain influence flows through feedback, not writes. One bundle may own the data warehouse; another owns accounting rules and subject matter. Feedback is gold to the owner — and it is the only inbound channel.

**Split on ownership, not size.** Split where a different person is accountable, where change cadence differs, or where an access boundary exists. Splitting for size alone produces chatty agents negotiating across an arbitrary line.

### 12.2 The registry

The registry is itself an OKF bundle — the format describes the mesh in its own terms. Members are concepts of `type: OKF Member`:

```markdown
---
type: OKF Member
title: SugarPaws3d business rules
description: Concepts, perspectives, rules, and computations for the patron business.
resource: https://git.internal/sp3d-rules
status: stable
tags: [sp3d, business-rules]
generated: { by: "human:geminia", at: 2026-07-31T12:00:00Z }
okfm_member:
  owner: "human:geminia"
  aliases: ["sp3d business", "patron rules"]
  agent: mcp://sp3d-rules-agent      # or in-process binding
  sync_policy: pull                   # pull | subscribe
---

# Scope

Owns definitions of churn, activation, deactivation, and revenue, and the
attested computations behind each. Does not own the warehouse schema — see
[sp3d data](/members/sp3d-data.md).
```

The member's `description` plus the registry's generated `index.md` give progressive disclosure **at the mesh level** — the official index pattern, recursed. Sidecars describe files so agents need not read every file; the registry describes bundles so agents need not search every bundle.

The registry owns **only the map**: membership, scopes, aliases, cross-member concept links. It never owns member content. It is index-over, not authority-over — calling it a "master" bundle would smuggle central authority back into a design that exists to prevent it.

**Cross-mesh routing** is scatter-gather: question → registry resolves relevant members → those members' agents answer from their own bundles → the asking workflow assembles, citations resolving into each contributing bundle. No global index over everything, ever (§12.7).

### 12.3 Cross-bundle references and pinning

Cross-bundle sources name the bundle and **pin a commit**. Git history is the version system — v3 invents no version integer.

```yaml
sources:
  - id: churn-def
    resource: okf://sp3d-rules/rules/churn-billing.md
    okfm_role: defines
    okfm_pin: { bundle: sp3d-rules, commit: abc1234 }
    okfm_captured: { at: 2026-07-30 }
```

Two rules:

1. **Pinning is mandatory across bundles.** A consumer's meaning must not change because another owner published. The owner's newer commit is an *offer*; moving to it is a recorded `Decision` in the consuming bundle.
2. **Local references are unchanged.** Federation adds nothing inside a bundle.

### 12.4 Addressed feedback — inbox and outbox

`Feedback` concepts gain routing and live in ledger directories:

```markdown
---
type: Feedback
title: "Grain mismatch in pledges.amount_cents"
status: stable
generated: { by: curation_agent/claude-opus, at: 2026-07-29T16:00:00Z }
sources:
  - id: target
    resource: okf://sp3d-data/systems/pledges.md
    okfm_pin: { bundle: sp3d-data, commit: def5678 }
okfm_feedback:
  from_bundle: sp3d-rules
  to_bundle: sp3d-data
  target_source: target
okfm_reason_codes: [grain_mismatch]
---

Rules assume per-pledge grain; captured payloads suggest per-charge.
```

Each bundle keeps `feedback/outbox/` (filed elsewhere) and `feedback/inbox/` (arrived). Inbox items flow into the owner's normal review queue. Accept ⇒ a new commit **in the owner's bundle** plus a response concept; decline ⇒ a response with reason codes. Either way the exchange is durable.

**The invariant: no cross-bundle writes, ever.** Feedback is the only inbound channel. The ledger is quietly among the most valuable artifacts in the mesh — the record of inter-domain negotiation that in most organizations happens in chat and evaporates.

### 12.5 Drift across bundles

- **Pull (the guarantee):** each bundle's refresh re-resolves pinned cross-refs through the owning bundle's agent. A newer commit touching the pinned path, or a `status: deprecated` target, is drift — handled exactly as §8.4.
- **Push (the optimization):** an owner deprecating a concept may notify bundles known to pin it (`sync_policy: subscribe`). Best-effort; pull is the backstop. Correctness never depends on notifications arriving.

Because refs are pinned, drift never silently changes a consumer's answers — it flags that the consumer now cites a superseded truth, and the consumer decides, on record.

### 12.6 Shared concepts and agents

**Shared concepts.** "Churn" exists wherever patron data and accounting rules both live. Nobody owns churn: the `Concept` lives in the registry (or a designated shared bundle); each domain bundle owns its `Perspective` and `Rule`s, linked by `perspective_on` relations that cross bundles. `equivalent_to` / `differs_from` mappings live in the registry beside the concept. The multiple-truths principle, scaled one level up.

**Agents.** Each bundle's agent is a harness workflow bound to it, exposing a small MCP surface: `answer_from_bundle`, `resolve_ref`, `accept_feedback`, `notify`. Two rules keep this honest:

- **Interface everywhere, transport as needed.** The agent boundary is the contract. Co-located bundles sharing a trust boundary may call in-process — do not make them converse through chat completions for theater. Real transport is earned where ownership or access differs.
- **The agent is the access-control point.** Cross-bundle consumers never read another bundle's files; they ask its agent, and the owner's agent decides what to share. Access control falls out of the topology.

### 12.7 What federation does not add

No central ontology. No global search index. No cross-bundle writes. No consensus requirement — bundles may disagree indefinitely and visibly. Any future feature violating one of these re-centralizes the mesh and should be treated as a design smell.

---

---

## 13. Drop-In Instantiation and Distribution

### 13.1 The requirement

OKFM ships as its own repository. Someone with no connection to these proving grounds
downloads it, points it at their project — or runs it standalone — and it works, with
**configuration only**. External sources still need their own setup; the mesh itself
does not.

This is the primary architectural constraint, and it is stricter than "well-factored
code": **anything that cannot be handed to a stranger does not belong in core.**

### 13.2 Two layers, four levels

**OKFM is a format contract that installs nothing, plus a reference implementation that is
optional and replaceable.** Someone who writes their own implementation against this
specification has an OKFM implementation; the base is what they conformed to.

| Layer | Contains | Installs |
|---|---|---|
| **Base** | this specification, the schema, the guide bundle, the viewer, templates, examples, and the deterministic build | nothing beyond a runtime |
| **Implementation** | CLI, reasoning components, providers, packs, federation, console, benchmark | the reference implementation |

An adopter engages at one of four **levels**, each cumulative, each a complete and usable
process rather than a teaser for the next:

| Level | What it is | Adopter supplies | Never needs |
|---|---|---|---|
| **1 — the format** | spec, guide, viewer, examples | a browser | anything |
| **2 — the deterministic process** | a drop-in folder that builds a bundle from your files | a runtime | a key, a provider, a model |
| **3 — the reasoning components** | the enrichment lifecycle | their own agent, LLM, or MCP | a key held by OKFM |
| **4 — the full suite** | providers, packs, federation, workflows | a key, a provider, `okfm.json` | — |

The **Level 2 / Level 3 boundary is exactly the model boundary**: nothing shipped at Level 2
may require an LLM. That is mechanically checkable, and it is what keeps the promise true as
the implementation grows.

Pointing a coding agent at the repository and asking it for anything is available from Level
1 and is not a level.

#### The implementation's own decomposition

Within the implementation layer, four sub-layers govern what an adopter touches:

| Sub-layer | Contains | Who edits it | Domain-specific? |
|---|---|---|---|
| **Core** | Loop workflows, resolvers, validator, index injector, core vocabulary, federation primitives | Nobody, normally — it is upgraded, not modified | Never |
| **Domain pack** | Reason codes, type conventions, prompt fragments, discovery adapter binding | Pack author | Yes |
| **Config** | `okfm.json` — pack, paths, stores, budgets | Adopter, once | Yes |
| **Bundle** | The concept files | Everyone, continuously | It *is* the domain |

Only the bottom two are touched to stand up a new mesh. A pack is a directory of
YAML plus at most one adapter file — packs are contributions, not forks.

### 13.3 Repository layout

Entries marked ✓ exist today; the rest are the target shape.

```text
okfm/
  README.md                  # quickstart: install, init, first question          ✓
  LICENSE                    # MIT                                                ✓
  NOTICE                     # Apache-2.0 attribution for OKF (§13.8)             ✓
  okfm.json                  # this repo's own config — it self-hosts the guide   ✓
  okfm.schema.json           # config schema
  okfm-viewer.html           # the mesh viewer (§14)                              ✓
  spec/
    okfm-v0.2.1.md           # normative specification                            ✓
  # ---- documents: what a person reads and edits. Never written to. -------
  docs/
    rationale.md             # §0-2, §22 — why the system is shaped this way      ✓
    roadmap.md               # §4, §11, §15-17, §19-20 — assets, phases, measures ✓
    prior-art.md             # §21 — ecosystem, and the evidence against          ✓
    levels/                  # raw material for the four level bundles            ✓
    decisions/               # dated decision records — an IN-PLACE bundle        ✓
  templates/
    bundle/                  # index.md, log.md, one starter concept     ✓
    AGENTS.md                # the prose contract — level 3, mode 2 (§13.6)  ✓
  examples/
    minimal/                 # an adopter-shaped config                            ✓
  benchmark/                 # §18 harness — deterministic half                   ✓

  # ---- the mesh: OKFM described in its own format (§12) -------------------
  # One OKF per folder of documents, plus a master OKF over them. Mirrored
  # bundles live here; in-place bundles stay with their sources and are
  # registered by path. `rm -rf .okfm` returns the project to what it was.
  .okfm/
    mesh/                    # the master OKF — one OKF Member per bundle         ✓
    level-1-view/            # level 1 — the format, the viewer (§14.5)           ✓
    level-2-build/           # level 2 — the deterministic build                  ✓
    level-3-enrich/          # level 3 — the enrichment loop                      ✓
    level-4-suite/           # level 4 — providers, packs, federation, benchmark  ✓
    docs/                    # the loose documents at the top of docs/            ✓
    guide/                   # the format, and a bundle that demonstrates it      ✓

  # ---- level 2: the drop-in folder. Copy this whole directory. ------------
  dropin/                    # paste into a project as .okfm/               ✓
    okfm                     # one entry point, dispatches the pipeline      ✓
    build                    # one bundle per folder, plus the master OKF    ✓
    refresh                  # observe pointers, report drift (§8.4)         ✓
    okfm_core                # locating, discovery, frontmatter, vocabularies ✓
    bootstrap                # extraction: title, description                ✓
    bake_viewer              # regenerate the viewer index                   ✓
    check_bundles            # conformance, profile, strip test              ✓
    enrich / guard / revalidate   # level 3 — outside the pipeline           ✓
    telemetry                # one run record per run (§10.1)                ✓
    resolvers/               # file:// only — live schemes need credentials
    vocab/                   # types, predicates, reason codes              ✓
    # Python 3.13, standard library only. No requirements file, by design.

  dev/                       # this repository's own maintenance — ships to nobody ✓
    check_docs               # the four-document spec corpus                 ✓
    check_levels             # every component fits the level it claims      ✓

  # ---- levels 3-4: the implementation. Optional, replaceable. -------------
  tools/
    cli/                     # validate, build, index, refresh, view, init
    enrich/                  # the components that require a model
    providers/               # openai-compatible + anthropic adapters
    resolvers/               # okf:// store:// sys:// — credentialed
    federate/                # registry, cross-bundle refs, feedback ledger
    packs/                   # research, warehouse, codebase
    console/                 # the served write UI (§14.7)
    benchmark/               # the §18 harness, runnable on any adopter's mesh
  .github/workflows/         # forks run pure components; main adds credentialed ✓
```

**The dependency direction is one-way and enforced.** `tools/` may import from `dropin/`;
`dropin/` may never import from `tools/`. That single rule is what makes Level 2 liftable by
construction rather than by discipline — if the drop-in folder needed anything outside
itself, pasting it into a stranger's project would not work, and the build would have caught
it.

Two further boundaries are checked mechanically, not intended:

1. **Base validates with `tools/` deleted.** CI runs it as an actual arm: remove the
   directory, validate every bundle, open the viewer.
2. **`dropin/` and `core` carry no domain words.** CI greps for project and domain names
   (`arxiv`, `sugarpaws`, `patron`, …) and fails on a hit. That test is what keeps the
   scaffolding distributable while it is developed against two specific domains.

### 13.4 The config surface

One file, small enough to read in full:

```json
{
  "okfm": "0.2.1",
  "pack": "warehouse",
  "bundles": { "primary": "./okf" },
  "index": {
    "max_concepts": 60,
    "priority_types": ["Attested Computation", "Rule", "Metric", "Perspective"]
  },
  "stores": {
    "sp3d-db": { "kind": "sql", "adapter": "bigquery", "profile": "env:SP3D_DSN" }
  },
  "federation": { "registry": null }
}
```

- **Everything optional except `pack`,** which must be present but may be `null` — a
  mesh with no domain pack is valid, and this repository's own config is one. Omit
  `bundles` and discovery falls back to convention (§13.5). Omit `stores` and only
  file and object pointers resolve.
- **Credentials by reference only** (`env:` / secret-manager handles). A config file
  is committed; a credential is not.
- **`federation: null` is a valid mesh.** A single bundle is the common case; the
  registry appears only when a second owner does (§12).

### 13.5 Discovery by convention

Any `.md` file with a non-empty `type:` in its frontmatter is a concept, wherever it
sits in the project. No dedicated directory is required, and `bundles` merely narrows
the scan.

This is what makes adoption incremental: an existing docs tree becomes a mesh by
adding one frontmatter line at a time, with no migration project and nothing to move.
It is also why **zero-overhead-when-absent** (§8.5, rule 4) matters — a project with
no concepts must pay nothing for having OKFM installed.

### 13.6 Runtime independence

OKFM must run three ways. Presented in increasing order of integration, because that is
the order an adopter meets them — the modes are the levels of §13.2 seen from the
implementer's side:

1. **As plain CLI** — *level 2*. `okfm validate`, `okfm index`, `okfm build`, `okfm view`.
   No agent, no key, usable in CI and liftable as a folder.
2. **As agent instructions** — *level 3*. `templates/AGENTS.md` states the contract in
   prose: read the index first; weigh `status`, `stale_after` and a missing `verified`
   before relying on a concept; update the concept and `log.md` after changes; validate
   before committing. Weaker than injection, and portable to any agent tool the adopter
   already has.
3. **Inside a harness** — *level 4*. Workflows call the implementation directly; injection
   is a hook. The reference integration.

Mode 2 is not a fallback. It is the mode most adopters will use, because it requires
nothing they do not already have — and it is the reason **OKFM itself never holds a
credential below level 4.** In mode 2 the adopter's agent drives OKFM; only in mode 3 does
OKFM drive a provider.

The implementation therefore depends on no specific agent runtime, no LLM provider, and no
MCP server. Adapters may; core may not. A harness integration is one worked example of mode
3, never a requirement — the CLI path must remain a complete way to use level 4.

### 13.7 What an adopter does

Four things, one per level. Each is a complete process; none is a teaser for the next.

**Level 2** — paste and run. The folder defaults to the location it sits in, scans the
files around it, and writes a bundle. First run with no config reports what it found and
**writes the config it used**, so pruning scope is deleting a line rather than reading
documentation about scoping.

```shell
cp -r okfm/dropin my-project/okfm && cd my-project
python okfm/build            # bundle written to okfm/bundle/, config written beside it
```

Open `okfm-viewer.html` and the mesh is there — unenriched, because no model was involved,
and honest about it: extracted descriptions, `status: draft`, no `verified` entry anywhere.

**Level 4** — the full suite.

```shell
okfm init --pack warehouse      # writes okfm.json, index.md, log.md, one concept
okfm validate                   # green on an empty mesh
okfm index                      # see what an agent would be handed
```

#### The distribution test, one per level

This replaces the earlier port-effort metric. Port effort measured whether *this builder*
could move between domains; the distribution test measures whether anyone can, which is the
stronger and more honest question.

| Level | Passes when a competent stranger, given only the README, can… |
|---|---|
| **1** | hand-write a valid concept their own agent reads correctly — **nothing installed** |
| **2** | paste the folder into a project with **no existing bundle**, run it, and open the viewer on a real generated mesh — **no key, no model** |
| **3** | enrich a stale concept with their own agent and get a reviewable draft — **no credential held by OKFM** |
| **4** | reach a running mesh answering one real question about their own project in **under an hour**, editing configuration and concepts only — never core |

Levels 2 and 3 permit editing a config or a workflow first. That is the expected
adaptation, not a failure: the promise is **a workflow that works and is a sound starting
point, not one that fits every project unmodified.** What no level permits is an adopter
having to write a process from scratch, or reverse-engineer what a correct one looks like.

Level 1's is the strongest claim the project makes. A format that cannot be understood and
copied without tooling is not a format.

### 13.8 Licensing and attribution

The OKF specification is Apache-2.0 by the Google Cloud Data Cloud team. If the spec
is vendored for offline validation it is included verbatim with attribution, as
ecosystem precedent already establishes (§21.2). OKFM's own code and content are MIT
— the shortest license that lets someone actually use this.

### 13.9 Decoupling work still outstanding

| Coupling today | Decoupled form |
|---|---|
| arXiv specifics in loop code | `packs/research/` — reason codes, prompts, adapter binding |
| Discovery hard-wired to the arXiv MCP | `DiscoveryAdapter` interface; warehouse introspection is a second implementation |
| Evidence = files + arxiv refs | Per-scheme resolvers in `core/resolvers/`; `sys://` added for databases |
| Reason codes inline in prompts | `core/vocab/` + pack overlays |
| Refresh targets files | Refresh targets pointers; the file resolver is one case (§8.4) |
| Loop lives inside one project | Loop in `core/workflows/`, parameterized by pack and config |
| Paths and stores hard-coded | `okfm.json` |
| Harness assumed present | Three runtime modes (§13.6) |

---

---

## 14. The Mesh Viewer

`okfm-viewer.html` ships at the project root and is committed. Open it and you see
the mesh: a graph, a closure ledger, and a health panel. It is in core because a mesh
you cannot see is a mesh you cannot maintain, and because the health panel is where
§20's success measures become visible rather than aspirational.

### 14.1 Location

Default `./okfm-viewer.html`, overridable:

```json
"viewer": {
  "path": "./okfm-viewer.html",
  "index": "./okfm-index.json",
  "serve_port": 7345
}
```

Root is the default because the file has to be *found* — a viewer buried three
directories deep is a viewer nobody opens. A subdirectory is one config line.

### 14.2 Three data sources, tried in order

The page is dynamic. It holds no snapshot of your mesh:

1. **`./okfm-index.json`** — the live metadata index, written by `okfm view` and
   gitignored. When present, this is what renders.
2. **The bundled guide** — a baked-in metadata index for `okfm-guide/` (§14.5),
   shipped with the repository so a fresh clone opens to something real.
3. **Empty state** — no index, no guide: the page explains what a concept is, shows
   a five-line example, and names the two commands that matter. An empty mesh is an
   invitation, not an error.

`file://` blocks `fetch`, so a viewer opened directly from disk lands on source 2 or
3. `okfm view --serve` starts a local server and unlocks source 1 plus live bodies.
The badge in the masthead states which source is showing; the reader is never left
guessing whether they are looking at their own mesh.

### 14.3 Bodies: fetched, never embedded

Concept bodies are **read from the bundle at click time** when the viewer is served,
and simply unavailable when it is not. The page never contains them.

This is one rule with three distinct justifications, and it is enforced by
construction rather than by discipline:

1. **Divergence.** An embedded body is a snapshot. A month later it silently
   disagrees with the file it came from, and nothing says so. A fetched body cannot
   be stale.
2. **Contamination.** §21.3 records a published incident: a committed rendered
   bundle page carried every concept body in its inline data, a benchmark control
   agent found it, and the arm had to be rebuilt. A file with no bodies cannot
   contaminate anything.
3. **Access control.** In a federation the owning agent decides what to share
   (§12.6). A flat file containing every body routes around that.

**Mechanical enforcement, not a note in a document:**

- `okfm-index.json` and any locally-regenerated viewer are **gitignored**; the
  committed `okfm-viewer.html` contains guide metadata only.
- `okfm validate` fails if a committed artifact under `viewer.path` contains concept
  body text.
- The benchmark harness (§18.3) refuses to run when a rendered view is present in a
  control arm — the published mistake, automated away.
- Generated artifacts are excluded from context assembly (§8) by scope, so no agent
  reads the viewer instead of the bundle.

### 14.4 Derived at render time

Trust tier, staleness, drift, and every gauge are computed when the page is built
(§3.4), never read from a stored verdict:

- **Trust** — a `human:` actor in `verified` ⇒ human-reviewed; another verifier ⇒
  machine-confirmed; none ⇒ unverified.
- **Stale** — `stale_after` on or before today.
- **Drifted** — a source whose current hash differs from `okfm_captured`.

The same bundle rendered on a different day reports different badges. That is correct.

### 14.5 The bundled guide

`okfm-guide/` is a real OKF bundle that documents OKFM — ten concepts covering the
profile, the loop family, attestation, drift, federation, and how to write a first
concept. It is documentation and working example at once: the guide teaches by *being*
the thing it describes, and it validates like any other bundle.

The point is the first five minutes. Clone the repository, open the viewer, and there
is a populated graph to explore rather than an empty screen and a README.

**It is scoped, so it never pollutes your mesh.** Every guide concept carries
`okfm_scope: guide`, and `exclude_scopes: ["guide"]` keeps it out of health
statistics, the index budget (§8.5), benchmark corpora (§18), and any context
assembled for an agent. It renders in the viewer; it counts toward nothing.

`rm -rf okfm-guide/` is the entire removal procedure — nothing references it, and the
viewer falls back to its empty state. `okfm init --guide` restores it.

### 14.6 Three views

**Graph.** Force-directed, colored by type, sized by inbound references. Ring encodes
trust (solid human, dashed machine, none unverified); halo encodes staleness (amber)
or drift (rust); dashed edges mark `differs_from` and `supersedes`. Filters on type,
trust, freshness, bundle. Typed relations (§7.3) are what make the edges mean
anything — an untyped link graph shows connectivity, not meaning.

**Closure.** The signature view: every `Goal` as a five-slot track — goal, evaluation,
decision, experiment, outcome — with missing slots drawn as gaps. A committed decision
with no outcome is visibly an open loop. This is success measure §20.6 as a picture,
and the fastest way to see whether the loop family is being closed or merely
populated.

**Health.** Composition, trust, and freshness distributions; loop-closure counts; and
one review queue listing everything the mesh believes needs a human — drifted sources,
passed staleness, unverified concepts, unreconciled rules, orphans.

### 14.7 Scope

Read-only. Not an editor, not a search index, not a context source. Agents read the
bundle; the viewer is for people. The health traversal also exports as JSON, so CI can
fail on thresholds — open loops, drifted sources in `stable` concepts — without a
browser.

---

---

## 15. Roadmap

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 16. Proving Ground A: arXiv Loop Retrofit

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 17. Deferred — Parking Lot with Re-entry Triggers

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 18. Evaluating the Bundle

The premise of this whole system — that curated knowledge makes answers better — is
testable, and the ecosystem has already shown it does not always hold (§21.1). This
section makes testing it a standing practice rather than an act of faith.

### 18.1 Method

Adapted from the published OKF benchmark (§21.1):

1. **Two arms, one corpus.** The project with its bundle, and the same project with
   the bundle removed. Nothing else differs, and every fact the questions ask about
   must be present in both arms — the bundle is a shortcut, never the only source.
2. **Fresh agent per question per arm.** No shared context, same model, read-only,
   and not told the experiment is about knowledge bundles.
3. **Question shapes, deliberately mixed.** Lookup, cross-cutting, change-site, and
   — for OKFM specifically — *why* questions, which are the shape the bundle is
   supposed to win.
4. **Blind grading** against a claim list per question, with answers keyed to opaque
   ids and the arm labels hidden from the grader.
5. **Commit the answers and the key** so any run can be regraded under a different
   rubric later.

### 18.2 What to measure

- **Claims hit** — the headline.
- **Tokens** — harness-billed, not self-reported. Effort, not correctness.
- **False statements** — separately from omissions. An omission is a gap; a false
  statement is a knowledge defect and should be traced to the concept that caused it.
- **For SugarPaws3d only: agreement with the golden reports** — a mechanical rubric
  rather than hand-written claim lists (§11.4). This is a genuine advantage over the
  published benchmark, which had to write its own ground truth.

### 18.3 Two contamination traps

Both are borrowed rather than learned the hard way (§21.3):

1. **Rendered copies are copies.** Any exported view of a bundle — a visualization,
   a static site, a cached context package — contains the bundle's prose and will
   contaminate a control arm. Remove every derivation, not just the source.
2. **Question provenance.** Questions drawn from a bundle's own table of contents
   flatter the bundle. Draw them from real behavior, real business questions, and
   real past confusion, then verify each is answerable from source in both arms.

### 18.4 Cadence

- **Phase 1:** stand up the harness; take a baseline reading on the arXiv bundle.
  Report whatever it says.
- **Phase 3:** run on real business questions against the golden reports.
- **Ongoing:** re-run after any large curation push. A rising claims-hit gap is the
  evidence that curation is working; a flat one is a signal to apply §7.7 harder.

An honest negative result here is more valuable than a favorable one, because it
tells you which knowledge is worth writing down before you have written down the
wrong things at scale.

---

---

## 19. Open Questions

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 20. Success Measures

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 21. Ecosystem and Prior Art

> Moved to [`docs/prior-art.md`](../docs/prior-art.md).

## 22. Closing Note

> Moved to [`docs/rationale.md`](../docs/rationale.md).

## Appendix A — Legacy Draft → OKFM v0.2.1 Field Mapping

| Earlier draft | OKFM v0.2.1 | Notes |
|---|---|---|
| `okf: "2.0"` | `okf_version: "0.2"` in root `index.md` | Official location |
| `id` | file path minus `.md` | Official; `okfm_key` for stability across moves |
| `type` | `type` | Title Case, official convention |
| `version` (integer) | git history | Cross-bundle refs pin commits (§12.3) |
| `state` | `status` | 6 states → `draft`/`stable`/`deprecated` + `supersedes` relation |
| `title` | `title` | Unchanged |
| `relationships` | markdown links + `okfm_relations` | Both readings supported |
| `evidence[]` | `sources[]` + `okfm_role`, `okfm_captured` | Official structure, OKFM extensions inside |
| `provenance.created_by` | `generated.by` | Actor convention |
| `provenance.at` | `generated.at` | Official |
| `provenance.model` | folded into `generated.by` | `agent/model-version` |
| `provenance.run_id` | `okfm_run_id` | Links concept to telemetry |
| `provenance.supersedes` | `supersedes` relation + `status: deprecated` | Official lifecycle |
| (none) | `verified[]` | New: separates writer from confirmer |
| (none) | `stale_after` | New: time-based staleness |
| `scores` | `okfm_reason_codes` + body | "Record signals, not verdicts" (§3.4) |
| `unsubstantiated: true` | omit `sources` | Absence carries meaning |
| Metric governance by convention | `Attested Computation` | Mechanically enforced (§9) |
| `perspective.*` block | `Perspective` concepts + `okfm_perspective` | Concepts, not fields |
| `declared`/`observed`/`reconciliation` | `okfm_declared`/`okfm_observed`/`okfm_reconciliation` | Keyed to `sources[].id` |
| Custom sidecar class | `description` + `index.md`, or `okfm_sidecar` | Audit first (§7.4) |
| `okf.yaml` manifest | root `index.md` frontmatter + OKFM config | Official permits `okf_version` only there |
| `telemetry/runs/` | `references/telemetry/runs/` | YAML, not concepts |
| `vocab/` | `references/vocab/` | Official `references/` convention |
| `edges/edges.jsonl` | `references/edges/edges.jsonl` | Unchanged in spirit |

---

---
