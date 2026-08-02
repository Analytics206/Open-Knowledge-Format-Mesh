---
type: Concept
title: The admission test
description: Write down what the code cannot say — and nothing else.
status: stable
tags: [curation, evidence-backed]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
sources:
  - id: benchmark
    resource: /docs/prior-art.md
    title: "The published OKF benchmark"
    okfm_role: subject
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The question

Before writing a concept, answer one thing:

> **Does this say something its sources cannot?**

| Verdict | Example | Action |
|---|---|---|
| **Admit** | Why a threshold is 1,000; why an approach was rejected; which perspective a number uses | Write the concept |
| **Reject** | Restating a schema; paraphrasing a query; summarizing a README | Cite the source; write nothing |
| **Attest** | The definition of churn; the revenue calculation | Write an [attested computation](attested-computation.md) |

# Why this is the most important rule here

It is the only rule in OKFM derived from a measurement that went *against* the
premise.[^benchmark]

Someone ran the obvious experiment: one repository in two states, with and without a
knowledge bundle, twelve fresh agents, blind grading. The bundle won the *why*
questions — rationale that existed in exactly one place and nowhere else in the
repository. It tied on everything mechanical. And it **lost** one question, because a
concept had summarized a validator, dropped the detail the question actually needed,
and the agent stopped at the summary instead of reading on.

The bundle became a detour around the file with the answer.

It also cost about 5% *more* tokens, not fewer. The "read three small files instead of
three thousand lines" pitch does not survive contact with evidence, and OKFM does not
make it.

# Three corollaries

1. **Prefer pointing to summarizing.** A concept whose value is orientation should say
   where to look and why it matters, then link. This guide is written that way on
   purpose.
2. **Where a summary is unavoidable, mark its limits.** Say in the body that you are
   abstracting, and cite the source with `okfm_role: implementation` so a reader knows
   detail exists downstream.
3. **Attestation beats summary for numbers.** An attested computation cannot drift
   from the query, because it carries the query.

# The failure mode, stated plainly

A concept that stands between an agent and a better answer is a regression. Deleting
it is a fix, not a loss.

[^benchmark]: The published OKF benchmark
