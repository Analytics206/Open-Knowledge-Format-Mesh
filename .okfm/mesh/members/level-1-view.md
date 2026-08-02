---
type: OKF Member
title: Level 1 — view
description: The download. The viewer, the shipped bundles, and pointing your own agent at the repository.
resource: ../../level-1-view
status: stable
tags: [level-1, viewer, no-install]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  owner: "human:analytics206"
  aliases: ["level 1", "the viewer level"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_level: 1
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /okfm-level-1/index.md }
---

# Scope

Owns the three things you get without running anything: the viewer, the bundles it renders,
and the practice of handing the repository to an agent you already use.

Does not own the format. That is [`okfm-guide`](guide.md) and the specification.

# Cadence

Slowest of the six. A change here means the *entry experience* moved, which affects everyone
who has ever opened the project.

# Why it is a member and not a README section

Because the level ladder needs to be data. `okfm_needs: []` on every concept in this bundle
is checked by [`dev/check_levels.py`](../../../dev/check_levels.py), so *"level 1 asks nothing of
you"* fails the build when it stops being true rather than quietly becoming marketing.
