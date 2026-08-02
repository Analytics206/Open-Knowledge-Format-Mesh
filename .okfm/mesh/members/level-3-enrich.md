---
type: OKF Member
title: Level 3 — enrichment
description: The loop that turns extracted quotations into written descriptions, using an agent you already have — or a model on your own machine, which removes the key without moving the level.
resource: ../../level-3-enrich
status: stable
tags: [level-3, enrichment, agent]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T07:20:00Z }
okfm_member:
  answers:
    - how do I use my own agent to improve descriptions
    - how do I run the loop with no key at all
    - how do I use my own key and provider
    - is there a CLI yet
    - what may an agent write, and what may it not
    - how do I clear drift
    - does curated knowledge actually help, and how is that measured
  owner: "human:analytics206"
  aliases: ["level 3", "enrichment"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /level-3-enrich/index.md }
---

# Scope

Owns the enrichment cycle: the work list, the agent contract, the tier guard, and the human
exit. Does not own the model, the provider, or the tool the agent runs in — all three are
yours, and that is the defining property of this level. It now also owns one component that
*calls* a model, which is a change of what the bundle does and not of where it sits.

# Cadence

Fast. The contract changes whenever a class of agent mistake is discovered, and each change
is additive.

# Where the boundary actually sits

At the `model` line, and mechanically. A workflow containing a step that cannot terminate
without a model is level 3; a composite inherits the union of what it invokes. That rule is
what keeps the level numbers from becoming a marketing gradient.

Two of this bundle's six components need nothing mechanically. They are here because they
exist only to serve a step that does — which is recorded in the concepts rather than hidden,
because a level assignment that cannot explain itself is a level assignment nobody will trust.

# Three variants, one level

By default **your agent drives OKFM**: no network call, no key, no provider choice.

The **local variant, called Level 2+**, has OKFM drive a model on hardware you own — the direction reverses, the
key does not appear, and the level does not move. `model` without `secrets` had been a legal
exposure set since [DR-0008](../../../docs/decisions/0008-build-pipeline.md) and nothing
occupied it until this did.

The **credentialed variant** reverses the direction *and* holds the key, carrying the
components that follow from acting unattended: providers, packs, federation's negotiation
half, the console app, and the benchmark.

That last one was a fourth level until it kept needing re-explaining. The ladder asks for a
browser, then Python, then a model, and there is nothing further to ask for; who holds the key
is a change of direction rather than another step up. The `needs-*` tags still record `secrets`
per component, which is where the distinction does work — and the local variant is the case
that proved it, by removing the fee and staying exactly where it was
([DR-0013](../../../docs/decisions/0013-the-local-model-variant.md)).
