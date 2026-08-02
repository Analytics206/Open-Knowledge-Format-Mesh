---
type: Runbook
title: What you may claim
description: "Four rules for writing a concept by hand — land as draft, never write verified, never invent an edge, and copy before you summarise. Every one of them is about not asserting something nobody did."
status: stable
tags: [getting-started, authoring, trust]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T17:30:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Four rules, and they are all the same rule

Writing a concept is easy. Writing one that does not claim something nobody did is the part
worth learning, and it is where a first-time author goes wrong — not on syntax.

These lived only in `templates/AGENTS.md`, a file presented throughout as Level 3 material for
when a model is doing the writing. So an author hand-writing their first bundle — which is
Level 1's entire promise — had no reason to open it, and the templates they *were* pointed at
shipped `status: stable` and `generated.by: "human:<you>"`. Following the documented path
produced a concept claiming a review that never happened.

# 1. Land as `draft`, with no `verified` entry

```yaml
status: draft
generated: { by: "human:you", at: 2026-08-02T00:00:00Z }
```

`verified` is not a formality you fill in while you are there. It is the assertion **somebody
read this and stands behind it**, and it is the only thing separating a note from knowledge a
reader will act on. A concept with no `verified` entry is honest; one carrying an unearned
entry poisons every trust reading downstream, and nothing will ever flag it, because the whole
system takes that field at its word.

`draft` is not an apology either. It is accurate: you just wrote it and nobody has checked.

# 2. Say who, with the right prefix

Three kinds of actor, and the prefix is read rather than displayed:

| | |
|---|---|
| `human:alex` | a person |
| `agent:claude-opus-5` | a model, driven by somebody |
| `process:okfm-build` | deterministic code |

The build decides what it may overwrite from `generated.by`; a re-validation refuses anything
but a `human:`; the trust tier a reader sees comes from `verified.by`. An unrecognised prefix
resolves to *machine*, so a typo quietly downgrades rather than failing loudly.

Never claim `human:` for something a model produced. It is the one field that cannot be
checked against anything.

# 3. Never invent a typed relation

Ordinary markdown links in the body are free — write as many as you like. `okfm_relations` is
different: impact analysis and drift propagation read a predicate as **fact**, so a wrong edge
is worse than a missing one. It does not degrade the graph, it corrupts it.

If you think two concepts are related but you are not certain how, say so in prose. Prose is
allowed to be uncertain; an edge is not.

# 4. Copy before you summarise

Lifting a sentence that already exists cannot invent. Writing a new one can. When you fill a
`description`, prefer the source's own words — and when you genuinely must summarise, say in
the body that you are abstracting and cite what you abstracted.

This is not modesty. A bundle that summarised a validator **lost** a question the raw source
would have answered, because the summary dropped the detail and the reader stopped there. A
concept standing between somebody and a better answer is a regression, and deleting it is a
fix. That is [the admission test](admission-test.md) in one line.

# What you cannot compute by hand, and do not have to

You are running nothing, so you cannot hash a source. Do not invent one — a fabricated
`okfm_captured.hash` pins a value that never matches and reports drift forever, which is worse
than no pointer at all.

Leave it out, or record only when you looked:

```yaml
sources:
  - id: design
    resource: ../docs/system-design.md
    okfm_role: subject
    okfm_captured: { at: 2026-08-02 }
```

A pointer with no hash reads as **unknown** — not fresh, not drifted. That is the true answer,
and the format has a state for it precisely so you are never pushed into guessing.

# If a model is doing the writing

Same four rules. [`templates/AGENTS.md`](../../templates/AGENTS.md) is the copy to hand your
agent — it states these plus what a `[model]` pass may not touch, and
`okfm.py guard` checks the result against them afterwards.
