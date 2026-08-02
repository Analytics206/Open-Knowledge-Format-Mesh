---
type: Index
title: "Level 3 — enrichment"
description: Your agent writes what extraction cannot, a guard checks what it wrote, and you approve it. OKFM holds no credential.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_level: 3
okfm_needs: [model, human]
okfm_relations:
  - { predicate: registered_by, target: /okfm-mesh/index.md }
  - { predicate: depends_on, target: /okfm-level-2/index.md }
---

# What this level is

Level 2 gives you concepts whose descriptions are quotations from your own files. Some are
fine. Many are unhelpful, and no amount of arithmetic will improve them, because saying what
a document is *for* is writing, not copying.

Level 3 is the loop that fixes that: the build says what needs work, your agent drafts it, a
guard checks that the agent stayed inside its authority, and you approve. Four steps, one of
which is a person, one of which is a model, and neither is optional.

# Components

| Component | Does | Needs |
|---|---|---|
| [The enrichment loop](the-enrichment-loop.md) | the whole cycle, end to end | `model`, `human` |
| [The agent contract](the-agent-contract.md) | what an agent may and may not write | `model` |
| [The work list](the-work-list.md) | what needs enriching, and why | — |
| [The tier guard](the-tier-guard.md) | did the edit pass write only what it owns | — |
| [The human exit](the-human-exit.md) | review clears drift; nothing else does | `human` |

Two of the five need nothing mechanically. They are here because they exist only to serve a
step that does — a work list with nothing to enrich it is a report about nothing.

# OKFM holds no credential here

Your agent drives OKFM. You are already authenticated in your own tool, and OKFM never sees a
key, never chooses a provider, and never makes a network call. That is the whole reason keys
first appear at [level 4](../level-4-suite/index.md), where the direction reverses and OKFM
drives a provider.

# The boundary is exactly the model line

A workflow containing a step that cannot terminate without a model is level 3, and that is
mechanically checkable rather than a matter of taste. It is also why the level 2 pipeline does
not call anything here: a composite's needs set is the union of its parts, so one model step
would move the whole pipeline up a level and off every fork's pull request.
