# OKFM — Rationale

Why the system is shaped this way: what changed against earlier drafts, what the baseline already solved, and what this release is for. Non-normative.

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
| 0 | What This Release Changes | *this document* |
| 1 | What Changed from v2, and Why | *this document* |
| 2 | Vision | *this document* |
| 3 | Design Principles | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 4 | Existing Assets | [`docs/roadmap.md`](../docs/roadmap.md) |
| 5 | Architecture Overview | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 6 | Baseline: What We Inherit from OKF v0.2 | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 7 | The OKFM Profile | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 8 | Evidence, Drift, and Staleness | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 9 | Governed Numbers: Attested Computation | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 10 | Workflow Instrumentation | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 11 | Proving Ground B: SugarPaws3d Patron Analytics | [`docs/roadmap.md`](../docs/roadmap.md) |
| 12 | Federation — the OKF Mesh | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 13 | Drop-In Instantiation and Distribution | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 14 | The Mesh Viewer | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 15 | Roadmap | [`docs/roadmap.md`](../docs/roadmap.md) |
| 16 | Proving Ground A: arXiv Loop Retrofit | [`docs/roadmap.md`](../docs/roadmap.md) |
| 17 | Deferred — Parking Lot with Re-entry Triggers | [`docs/roadmap.md`](../docs/roadmap.md) |
| 18 | Evaluating the Bundle | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |
| 19 | Open Questions | [`docs/roadmap.md`](../docs/roadmap.md) |
| 20 | Success Measures | [`docs/roadmap.md`](../docs/roadmap.md) |
| 21 | Ecosystem and Prior Art | [`docs/prior-art.md`](../docs/prior-art.md) |
| 22 | Closing Note | *this document* |
| A | Legacy Draft → OKFM v0.2.1 Field Mapping | [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md) |

---

## 0. What This Release Changes

Two things define OKFM v0.2.1 against the prior drafts.

**OKFM is a distributable project, not a private design.** The scaffolding is meant
to live in its own repository, be downloaded by someone with no connection to these
proving grounds, and run against their project — or standalone — with configuration
only. §13 specifies that shape, and it is now the primary architectural constraint:
anything that cannot be handed to a stranger does not belong in core.

**The name and version pin to the baseline.** The system is OKFM (OKF Mesh),
versioned against the OKF release it targets (see policy above). Extension keys are
prefixed `okfm_`.

This release also incorporates evidence and tooling from the wider OKF ecosystem
(§21), chiefly the only published measurement of whether an OKF bundle helps an
agent at all:

- **New principle: write down what the code cannot say** (§3.13), with a concept
  admission test (§7.7). Evidence-backed, and it reverses a common curation instinct.
- **New principle: no duplicate knowledge** (§3.14). Derived from a real
  contamination incident, not theory.
- **Phase 1 adopts an existing validator, migrator, and CI action** instead of
  building them (§15, §21.2).
- **A benchmark harness** enters Phase 1 and Phase 3 exit criteria (§18.4).
- **Backfill honesty rule** (§15): never synthesize a `verified` entry.
- **Derived-not-stored** extended to OKFM's own flags (§3.4, §8.4).
- **Spec-churn resilience** made explicit (§0.1).
- **Push-don't-wait context injection** (§8.5), from measured evidence that the
  savings come from injecting a compact index, not from the agent finding one.
- **§13 rewritten** as drop-in instantiation and distribution.

### 0.1 On chasing this rabbit

Official OKF was announced in June 2026 and went v0.1 → v0.2 within weeks. More
revisions are certain, and some will require refactoring here. That is an accepted
cost, for three reasons:

1. **The knowledge transfers even when the encoding does not.** Perspectives,
   declared-vs-observed, the loop family, federation, and ownership seams are design
   positions, not field names. A future OKF revision changes how they are written
   down, not whether they were the right things to record.
2. **The profile is separable by construction.** Every OKFM addition is an `okfm_`
   key, and the strip test (§7.1) is enforced in CI. Baseline churn touches
   official fields; OKFM keys move independently.
3. **Migration is mechanical.** The ecosystem already demonstrates textual,
   idempotent, comment-preserving migration between spec versions (§21.2). This is
   a rewrite job, not a redesign job.

**The one commitment that must not churn:** the vocabularies (§10.2) and telemetry
schema (§10.1). Reason codes and run records are the assets whose value comes
entirely from being comparable across time. Field names can move; a reason code's
meaning may not.

---

---

## 1. What Changed from v2, and Why

v2 designed a knowledge format from scratch. Official OKF v0.2 turned out to have independently converged on the same philosophy — markdown + YAML frontmatter, git-native bundles, permissive consumption, provenance and trust as first-class concerns — and to have solved several problems v2 solved worse.

v3 therefore **rebases onto official OKF v0.2 as the baseline** and defines the rest as a named profile: **OKFM** (OKF Mesh). A bundle produced by this system is simultaneously a conformant OKF v0.2 bundle and a fully functional OKFM bundle.

| v2 | v3 |
|---|---|
| Custom envelope (`okf: "2.0"`, `id`, `version`, `state`, `provenance`) | Official frontmatter (`type`, `title`, `description`, `sources`, `generated`, `verified`, `status`, `stale_after`) |
| Custom `provenance` block | `sources` + `generated` + `verified` (§6.3) |
| Six lifecycle states | Official `status: draft \| stable \| deprecated` (§6.4) |
| Object `version` integers + `supersedes` | Git history; cross-bundle refs pinned by **commit SHA** (§12.3) |
| Semantic IDs (`evaluation.foo.bar`) | Path IDs (official) + optional stable `okfm_key` for moves (§7.2) |
| Custom metric governance | **Attested Computation** — official, mechanically enforceable (§9) |
| Custom sidecar file class | `description` + generated `index.md` (official); richer sidecars only where they carry more than a summary (§7.4) |
| Custom pointer grammar as a parallel system | Pointer schemes ride inside official `sources[].resource` (§8.1) |
| Everything invented | Only the genuinely missing things invented, each as a documented `okfm_` key (§7) |

**What v3 keeps that official OKF does not have.** These are the actual contributions, and all are purely additive:

1. **The loop family** — workflow residue as knowledge: goals, evaluations, decisions, experiments, outcomes, feedback, answers (§7.5).
2. **Federation** — an OKF of OKFs: registry, ownership boundaries, addressed feedback, cross-bundle drift (§12).
3. **Content-based drift** — re-resolving pointers and comparing captured hashes, complementing official date-based `stale_after` (§8).
4. **Perspectives and declared-vs-observed** — competing definitions held simultaneously, and the gap between what documents claim and what code does (§11.2–11.3).
5. **Typed relations** — official links stay untyped in prose; OKFM carries the predicate alongside (§7.3).
6. **Versioned telemetry** — structured run records, not a prose changelog (§10).

**Naming.** *OKF* is the format (official, vendor-neutral). *OKFM* is this profile plus the scaffolding that runs it — distributed as its own project (§13). *Actionable Knowledge* is the concept OKFM exists to serve: evidence that changed what a project knows or does, preserved so the *why* stays queryable. *A mesh* is a federation of bundles (§12). *The harness* is whatever runtime drives OKFM — the reference implementation here, but not a requirement (§13.6).

**Scope note.** This document targets OKF v0.2 as published. Aligning with, or contributing to, any future official revision is out of scope here.

---

---

## 2. Vision

Every workflow run either consumes knowledge, produces knowledge, or both. Today most of that is lost the moment the run ends. The purpose of this system is to make the residue durable and queryable:

```text
Goal
  -> discover evidence
  -> evaluate against current project knowledge
  -> human decision (reject / monitor / trial / adopt)
  -> experiment and measure
  -> record outcome
  -> feed usefulness back to the source
  -> improved future discovery
```

The paper, the schema, the query result — none of these is the product. The product is whether that evidence changed what the project knows or does, and a durable record of why.

Six months on, the system should answer from its own bundles, without re-searching:

- "Why aren't we using speculative decoding?" → the papers evaluated, the trial, the regression, the rejection reasons.
- "Why did patron churn rise in June?" → the perspective used, the rule, the attested numbers, the decision, and what happened after.
- "Who consumes this internal API?" → the registered consumers, why each exists, and what breaks if the contract changes.

The first two work at any volume. Statistical learning from telemetry is a later, optional payoff — purchased cheaply now by schema discipline (§10.1).

---

---

## 3. Design Principles

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 4. Existing Assets

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

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

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 12. Federation — the OKF Mesh

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 13. Drop-In Instantiation and Distribution

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 14. The Mesh Viewer

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 15. Roadmap

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 16. Proving Ground A: arXiv Loop Retrofit

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 17. Deferred — Parking Lot with Re-entry Triggers

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 18. Evaluating the Bundle

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

## 19. Open Questions

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 20. Success Measures

> Moved to [`docs/roadmap.md`](../docs/roadmap.md).

## 21. Ecosystem and Prior Art

> Moved to [`docs/prior-art.md`](../docs/prior-art.md).

## 22. Closing Note

v1 asked what an enterprise knowledge platform would look like. v2 asked for the smallest buildable version. v3 asks the sharper question: **what does this system need to invent, given that a vendor-neutral format already exists and solves part of it?**

The answer is a short list — the loop family, federation, content drift, perspectives, declared-vs-observed, typed relations, versioned telemetry — sitting on a conformant baseline that brings provenance, trust tiers, lifecycle, and mechanically-attested computation for free. Everything else was a wheel already turning.

OKFM v0.2.1 adds one constraint on top of that: it has to be **handable**. Not a
private architecture that happens to be tidy, but a project someone downloads and
runs against knowledge this builder will never see. That constraint is the reason
core carries no domain words, why configuration is one small file, and why the
success measure is a stranger with a README and an hour.

The loop stays the same from arXiv papers to patron data. The source changes; the loop doesn't.


---

---

## Appendix A. Legacy Draft → OKFM v0.2.1 Field Mapping

> Moved to [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).
