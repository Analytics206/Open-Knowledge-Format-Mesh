---
type: Decision
title: <what was decided, as a claim>
description: <the decision and its reason, in one sentence — this is what an agent sees first>
status: draft
generated: { by: "human:<you>", at: 2026-01-01T00:00:00Z }
sources:
  - id: bench
    resource: /path/to/the/thing/this/rests/on.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:…", at: 2026-01-01 }
---

# Decision

What was decided. One or two sentences, no preamble.

# Why

The reasoning — and this is the part that earns the file. Cite sources with footnotes keyed
to `sources[].id`, so reordering the list cannot silently misattribute a claim.[^bench]

# What was rejected

The alternative, and what was wrong with it. This is usually the highest-value section: the
code shows what you built, git shows when, and neither shows what you decided against.

# What would change this

The condition that would reverse the decision. If you cannot name one, the decision may be
a preference rather than a decision.

[^bench]: <short label for the source>

<!--
Before keeping this file, answer: does it say something its sources cannot?

  Admit  — why a threshold is 1,000; why an approach was rejected; which definition a
           number uses
  Reject — restating a schema; paraphrasing a query; summarizing a README

`status: draft` and no `verified` entry is the correct starting state. A human adds
`verified` after reviewing; nothing else may.
-->
