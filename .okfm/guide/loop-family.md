---
type: Concept
title: The loop family
description: Concept types that record how a decision was reached, not just what is true.
status: stable
tags: [loop, workflow-residue]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: depends_on, target: /what-is-okfm.md }
---

# The residue problem

Every workflow run either consumes knowledge, produces knowledge, or both. Almost all
of the second kind is lost the moment the run ends. What survives is the artifact — the
merged PR, the chosen library, the number in the report — and not the reasoning that
produced it.

Six months later nobody can answer *why*, so the work is done again.

# Eight types

```text
Goal → Evidence → Evaluation → Decision → Experiment → Outcome → Feedback
                                                                    ↓
                                                                 Answer
```

| `type` | Records |
|---|---|
| `Goal` | The question or acquisition target, and the project it serves |
| `Evidence` | What was gathered, from where, and what was seen at capture |
| `Evaluation` | Assessment against the goal: signals, reason codes, a recommendation |
| `Decision` | The human call — reject, monitor, trial, or adopt — with rationale |
| `Experiment` | Hypothesis, baseline, success metrics, guardrails |
| `Outcome` | What actually happened, and whether the value was durable |
| `Feedback` | Structured signal sent back to a source or another bundle |
| `Answer` | A delivered answer, kept as a precedent |

# The distinction that carries the weight

`Evaluation` and `Outcome` are separate records and must never be collapsed.

An evaluation says *this looks useful*. An outcome says *this was useful*. Good ideas
fail and mediocre ideas succeed, and a system that stores only the first one is storing
optimism. The gap between the two is the only place a project can learn how good its
judgement actually is.

The same discipline appears one level down, in the baseline itself: `generated` records
who wrote something, `verified` records who confirmed it, and they are different keys
because the writer need not be the confirmer.

# Closing the loop is the measurable part

A `Decision` with no `Outcome` is an open loop. The web UI draws every goal as a
five-slot track with the missing slots as visible gaps, precisely so that a mesh full
of decisions and empty of outcomes cannot look healthy.

Populating the loop family is easy. Closing it is the part that says whether any of
this is working.
