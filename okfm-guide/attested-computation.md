---
type: Concept
title: Attested computation
description: A number that proves it was produced the sanctioned way.
status: stable
tags: [governance, numbers, official-type]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The failure mode

Ask a model a business question and it will re-derive your semantic layer on the spot.
It will guess what churn means, write a query that looks reasonable, and hand you a
number with no indication that the definition it invented is not the one your board
deck uses.

The number will be wrong in a way that is invisible.

# Convention is not enough

The obvious fix is a rule: *always use the registered query.* That is governance by
convention, and it fails silently the first time an agent decides it knows better.

Attested computation makes it mechanical instead. This is an **official** OKF type, not
an OKFM invention — it is the most valuable thing the baseline brings.

# Four parts

- **The computation** is a standalone concept with a declared `runtime` and typed
  `parameters`. It *carries* the query rather than describing it.
- **The agent may supply parameter values only.** It must not author or edit the
  computation.
- **The executor** runs it and returns a receipt: what actually executed, and what came
  back.
- **The attester** is deterministic, LLM-free code that re-derives what should have run
  and compares it to the receipt.

A rewritten query, a swapped file, or a mutated dependency fails the comparison.
*"Did the sanctioned thing run"* stops being a judgement call.

# The gate

A question-answering workflow discovers the computation, supplies parameters, executes,
attests — and **refuses to display a failing attestation**. A non-technical reader does
not have to audit anything. The number either attested or it did not, and that verdict
renders as a sentence rather than a metadata panel.

# Why this beats writing it down

It is the direct answer to [the admission test](admission-test.md). A concept that
*describes* how a number is produced can drift from the code that produces it, and the
drift is undetectable by reading either one. A computation that carries its own query
cannot.

One figure, one computation. Churn, activations, deactivations, and revenue are four
attested computations, not one — each verifies, goes stale, and attests on its own
schedule.
