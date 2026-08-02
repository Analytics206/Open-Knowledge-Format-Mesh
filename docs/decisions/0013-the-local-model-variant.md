---
type: Decision
title: DR-0013 — A local model is a variant of level 3, not a level between 2 and 3
description: "Running the model on your own machine removes the key, not the model — so it lands where `needs-model` without `needs-secrets` already sat, and the level 2/3 line stays exactly on the `model` boundary that CI checks."
status: draft
tags: [levels, adoption, boundaries, local-models]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T06:40:00Z }
sources:
  - id: self
    resource: /0013-the-local-model-variant.md
    okfm_role: subject
okfm_scope: project
---
# DR-0013 — A local model is a variant of level 3, not a level between 2 and 3

- **Status:** accepted 2026-08-02
- **Date:** 2026-08-02
- **Affects:** [DR-0009](0009-adoption-levels.md) level 3; [DR-0008](0008-build-pipeline.md)
  `needs` vocabulary; `dropin/enrich_local.py`, `dropin/config_schema.py`

## The question

Enrichment needs a model, and a model has meant an API key. Ollama removes the key without
removing the model. So does that make a "soft level 3" — or a level 2+, since the thing that
made level 3 expensive is gone?

Worth asking, because the fee is the part an adopter actually feels. The rest of this record
is why the fee is not what the ladder measures.

## Decision

**Level 3, local variant.** Level 3 now has three, distinguished by who drives and who holds
the key:

| Variant | Who drives | Who holds a key | Exposure | Built |
|---|---|---|---|---|
| your agent | your agent drives OKFM | your agent — OKFM holds none | `needs-model` on the loop, `[]` on every OKFM component | yes |
| **local** | OKFM drives a model on your machine | nobody | `needs-model` | **this record** |
| credentialed | OKFM drives a hosted provider | OKFM | `needs-model`, `needs-secrets` | no |

## Why not 2+

**The level 2/3 line is the `model` line, exactly, and it is a check rather than a claim.**
[DR-0009](0009-adoption-levels.md) states it and `dev/check_levels.py` enforces it: nothing in
a level 1 or 2 bundle may declare `needs-model`. Putting a component that calls a model at
level 2 does one of two things — breaks the check, or forces it to be rewritten around
"key / no key" instead. The second is worse, because a rule loosened to admit the first thing
that did not fit is no longer a rule.

**The distinction being reached for already exists, one rung up.** `nothing < human < model <
secrets` is ordered by exposure, and *model without secrets* has been a legal set since
DR-0008 was written. Local Ollama does not need a new position on the ladder; it is the first
component OKFM ships that actually occupies that one. What changed is that the rung stopped
being hypothetical.

**A level is what OKFM asks of you before you can start, not what it costs.** Level 3's ask is
*something has to reason*, and that is true whether the reasoning happens in a data centre or
on the laptop it was called from. Nondeterminism, output that must be reviewed, a guard on
what may be written, and a human gate before promotion are all unchanged. Cost is real and it
is not the axis.

The same argument retired level 4 in DR-0009's amendment — holding the key yourself is a
change of *direction*, not a step up. This is that argument run in the other direction and
reaching the same place.

## What it buys, which is the part worth being clear about

Level 3 previously had one buildable variant and it required an agent the adopter supplies.
That is a fair ask and it is still a dependency on something outside the project. With this,
the enrichment loop runs end to end on a machine with no account, no key, and no billing
relationship — which is the claim level 2 makes about the build, now made about the loop.

[Providers and keys](../okfm-guide/level-3-enrich/providers-and-keys.md) predicted exactly
this and is why it was written before any of it was built: *"if the loop works on Ollama, the
credentialed variant stops being gated on a billing relationship."*

## Consequences

**One component in `dropin/` is no longer `needs: []`.** `enrich_local.py` declares
`needs: [model]`, and it is the first thing in that folder to declare anything. It is
reachable as `okfm.py enrich-local` and **absent from `STEPS`**, because a workflow's set is
the union of everything it invokes — listing it in the pipeline would take the whole default
run out of CI on a fork's pull request. The folder's promise narrows accurately from *every
component here is `needs: []`* to *every component the pipeline runs is `needs: []`*.

**`needs` stays a closed vocabulary of four.** DR-0008 rejected a `network` rung on the
grounds that nothing needed the open internet without a credential. Loopback is not the open
internet, so that still holds — but this is the closest anything has come, and the re-entry
trigger is now concrete: point `enrich.base_url` at a public host with no key and the rejected
fifth value is exactly what would describe it.

**So the config says where the model runs, and the validator reads it.** `enrich.base_url`
warns when the host is not loopback. Not because a box on your own network is wrong — nothing
holds a key either way — but because that is the line the variant is defined by, and a
distinction nothing checks decays into a distinction nothing means. It is the only place the
local/credentialed boundary is written down in machine-readable form.

**A model may not write a `needs-*` tag.** Those tags are what `dev/check_levels.py` reads as
fact, so a model that could write one could forge the check that keeps components inside their
level. `enrich_local.py` carries existing ones over verbatim and drops any it is offered. This
is the same reasoning DR-0008 gives for never inferring `okfm_relations`: a guessed value in a
field something treats as fact is worse than no value.

## Against

**"Three variants of one level is the complexity four levels had."** It would be, if a variant
were a gate. It is not — the level is level 3 in all three cases, the same components run, the
guard and the human exit are identical, and the variant only names which of three things is
holding the model. An adopter reads one row of a table.

**"A small local model writes worse descriptions than a hosted one."** Probably, for some
models and some corpora. It does not matter as much as it sounds like it should, because
nothing here is published on a model's say-so: output lands `status: draft`, the guard checks
what it wrote, and drift stands until a person clears it. A weaker draft costs a slower review,
not a wrong bundle. And a description drafted from the whole document beats one extracted from
its first paragraph, which is the actual comparison.

Measured, on first contact with real hardware — a 4B, an 8B and a 9B over this repository:
the drafts came back honest, deterministic and *slightly worse than what was there*. That is
the comparison being unfavourable rather than the claim being wrong. This corpus opens its
documents with summary lines, which is precisely the case
[DR-0009](0009-adoption-levels.md) names as extracting well. The claim stands where it was
made — a corpus that opens with a wall of prose — and this repository is not that corpus, so
it cannot be the evidence either way.

**"This will grow into a provider abstraction."** It may, and
[providers and keys](../okfm-guide/level-3-enrich/providers-and-keys.md) already says what that
looks like — two adapters, one of them OpenAI-compatible. Deliberately not built here. There is
one adapter because there is one endpoint that needs no key, and a second arrives with the
credentialed variant that needs it. A `provider` config key was considered and left out for the
same reason: a key whose only legal value is the default can only be got wrong.

## Settled on first contact with hardware

Two things the design got wrong, found by running it against a real Ollama rather than a stub.

**Reasoning models are the wrong tool, and thinking is disabled outright.** The task is *read
one document, write one sentence it already supports*. A reasoning trace re-derives what a
single read gives you: 2.8k characters of thinking on a 4B and 6k on a 9B for a trivial
prompt, 15 and 89 seconds against 1–2 with `think: false`, same answer. At that cost a work
list of any size times out instead of draining. Not offered as a knob — a setting whose right
value is the same for every corpus is a setting nobody should have to find.

It also delivers what `temperature: 0` was chosen for. With both, two runs return
byte-identical text, so a second pass over an already-drafted concept is a no-op rather than
a rewrite.

**The prompt has to forbid describing the document.** Every model tried, across two families,
opened with *"This document explains…"* — the container instead of the content, and the reader
can already see the container. Naming the failure with right/wrong pairs fixed it on short
sources. It returns on long ones, which is a known limit rather than a solved problem.

Worth recording because neither is about Ollama. Both are about what enrichment *is*, and
both would have been got wrong the same way by a hosted provider.

## Re-entry triggers

- A second no-key endpoint that is not Ollama-shaped. Then the adapter split from
  DR-0009 lands, and `enrich.provider` appears with it.
- Anyone pointing `enrich.base_url` at a public host. That is the `network` rung DR-0008
  rejected, arriving.
- Local models becoming good enough that a draft is routinely promoted unread. That would
  not change the level, but it would make the human gate ceremonial, and a ceremonial gate
  should be argued about rather than quietly kept.
