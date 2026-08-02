---
type: Index
title: "Level 3 — enrichment"
description: Your agent writes what extraction cannot, a guard checks it, and you approve. Its credentialed variant is where OKFM holds the key instead of your agent.
status: stable
tags: [needs-model, needs-human, needs-secrets]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: registered_by, target: /mesh/index.md }
  - { predicate: depends_on, target: /level-2-build/index.md }
---

# What this level is

Level 2 gives you concepts whose descriptions are quotations from your own files. Some are
fine. Many are unhelpful, and no amount of arithmetic will improve them, because saying what
a document is *for* is writing, not copying.

Level 3 is the loop that fixes that: the build says what needs work, your agent drafts it, a
guard checks that the agent stayed inside its authority, and you approve. Four steps, one of
which is a person, one of which is a model, and neither is optional.

It is the last level. There is nothing to graduate to.

# Components

| Component | Does | Needs |
|---|---|---|
| [The enrichment loop](the-enrichment-loop.md) | the whole cycle, end to end | `model`, `human` |
| [The agent contract](the-agent-contract.md) | what an agent may and may not write | `model` |
| [A local model](a-local-model.md) | OKFM drafts it, on your machine, with no key | `model` |
| [The work list](the-work-list.md) | what needs enriching, and why | — |
| [The tier guard](the-tier-guard.md) | did the edit pass write only what it owns | — |
| [The human exit](the-human-exit.md) | review clears drift; nothing else does | `human` |

Two of the six need nothing mechanically. They are here because they exist only to serve a
step that does — a work list with nothing to enrich it is a report about nothing.

# Three variants, split on who holds the key

Everything above assumes **your agent drives OKFM**. You are already authenticated in a tool
you were using anyway; OKFM never sees a key, never chooses a provider, and never makes a
network call.

| Variant | Who drives | Who holds a key | Exposure |
|---|---|---|---|
| your agent | your agent drives OKFM | your agent | `model` |
| [local](a-local-model.md) | OKFM drives a model on your machine | nobody | `model` |
| credentialed | OKFM drives a hosted provider | OKFM | `model`, `secrets` |

The last two reverse the direction — **OKFM drives the model** — and only the third pays for
it with a credential. That is why the middle one needed no new rung: `model` without `secrets`
has been a legal set since [DR-0008](../../docs/decisions/0008-build-pipeline.md) and was
simply unoccupied until something ran locally. See
[DR-0013](../../docs/decisions/0013-the-local-model-variant.md) for why removing the fee does
not move the level.

# The credentialed variant

Same loop, opposite direction from the first — plus everything that follows from a process
able to act unattended.

| Component | State | Needs today |
|---|---|---|
| [The benchmark](the-benchmark.md) | prototype runs | — |
| [Providers and keys](providers-and-keys.md) | half built — the local half runs | — |
| [Packs](packs.md) | partly built — vocabulary overlays work | — |
| [Federation, the negotiation half](federation-negotiation.md) | designed, not built | — |
| [The console app](the-console-app.md) | designed, not built | — |

Four of the five are `status: draft` and say so in their first line. A level that described
unbuilt components as though they shipped would be the mesh lying about itself in the one
place it cannot afford to.

# Why the credentialed case is a variant and not a fourth level

It was one for a while, and the number kept needing to be re-explained.

The ladder is about **what OKFM asks of you before you can start**: a browser, then Python,
then a model. After that there is nothing further to ask for — holding the key yourself
instead of your agent holding it is a change of *direction*, not another step up. And since
anyone can point an agent at any level and do as they like, a fourth level read as a gate
where none existed.

Nothing is lost by collapsing it. the `needs-*` tags still record `secrets` per component, and CI
still gates on the set rather than the number, so the distinction survives exactly where it
does work. What went away is a level nobody could place from memory.

# The boundary that is left

Levels 1 and 2 admit nothing beyond a human. Level 3 admits `model` and `secrets`.
[`dev/check_levels.py`](../../dev/check_levels.py) enforces it, and it is the only boundary
the level model needs.
