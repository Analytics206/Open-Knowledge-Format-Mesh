---
type: OKF Member
title: Level 3 — enrichment
description: The loop that turns extracted quotations into written descriptions, using an agent you already have.
resource: ../../level-3-enrich
status: stable
tags: [level-3, enrichment, agent]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  owner: "human:analytics206"
  aliases: ["level 3", "enrichment"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_level: 3
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /okfm-level-3/index.md }
---

# Scope

Owns the enrichment cycle: the work list, the agent contract, the tier guard, and the human
exit. Does not own the model, the provider, or the tool the agent runs in — all three are
yours, and that is the defining property of this level.

# Cadence

Fast. The contract changes whenever a class of agent mistake is discovered, and each change
is additive.

# Where the boundary actually sits

At the `model` line, and mechanically. A workflow containing a step that cannot terminate
without a model is level 3; a composite inherits the union of what it invokes. That rule is
what keeps the level numbers from becoming a marketing gradient.

Two of this bundle's five components need nothing mechanically. They are here because they
exist only to serve a step that does — which is recorded in the concepts rather than hidden,
because a level assignment that cannot explain itself is a level assignment nobody will trust.

# Two variants, one level

By default your agent drives OKFM: no network call, no key, no provider choice. The
**credentialed variant** reverses the direction — OKFM drives a provider and holds the key —
and carries the components that follow from acting unattended: providers, packs, federation's
negotiation half, the console app, and the benchmark.

That was a fourth level until it kept needing re-explaining. The ladder asks for a browser,
then Python, then a model, and there is nothing further to ask for; who holds the key is a
change of direction rather than another step up. `okfm_needs` still records `secrets` per
component, which is where the distinction does work.
