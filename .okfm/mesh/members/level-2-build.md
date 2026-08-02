---
type: OKF Member
title: Level 2 — build
description: The deterministic pipeline — extraction, mirror mode, drift, validation, the viewer bake, telemetry. No model anywhere in it.
resource: ../../level-2-build
status: stable
tags: [level-2, deterministic, drop-in]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  owner: "human:analytics206"
  aliases: ["level 2", "the drop-in", "the build"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_level: 2
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /okfm-level-2/index.md }
---

# Scope

Owns the seven components of the deterministic build and the reasoning behind each. The code
lives in [`dropin/`](../../../dropin/README.md); this bundle says what it is for, what it needs,
and which mistakes shaped it.

# Cadence

Fast while the pipeline is being built, then slow. A change here is a change to something an
adopter has already pasted into their project, so it carries the same compatibility weight as
a library release.

# Why the split from level 3 is real

Every component here is `okfm_needs: []` — no network, no secrets, no model — which is what
lets the whole pipeline run on a pull request from a fork. That is not a naming convention:
it is the property CI depends on, and one model-dependent step would take it away.

# The concepts pin their own sources

Each component concept captures a hash of the file it describes, so editing `build.py` marks
the concept describing `build.py` drifted. It is the same drift machinery an adopter gets,
pointed at this repository — which means the documentation of the build cannot rot silently
while the build changes.
