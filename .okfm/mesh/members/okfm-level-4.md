---
type: OKF Member
title: Level 4 — the suite
description: Providers, packs, federation's negotiation half, the web UI, and the benchmark. One component works; the bundle says which.
resource: /.okfm/level-4
status: stable
tags: [level-4, suite, planned]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  owner: "human:analytics206"
  aliases: ["level 4", "the suite", "the full harness"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_level: 4
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Scope

Owns the components that exist once OKFM can act on its own: a provider to act through, packs
so it knows a domain's words, transport so it can reach another owner's bundle, a console to
drive it, and a benchmark to find out whether any of it helped.

# Cadence

Slowest of the four levels, because most of it is unwritten. Four of its five concepts are
`status: draft` and say so in their first line.

# Registering an unbuilt level

The registry rule is that a member naming something which does not exist is the mesh lying
about itself. This bundle passes that test on a technicality worth stating: the *bundle*
exists and its concepts are accurate, including the ones whose subject is a plan.

What it buys is that the mesh can answer *what exists at level 4* without anyone reading a
roadmap. Today the answer is the benchmark harness and vocabulary overlays, and the bundle
says exactly that.

# The one thing that changes here

OKFM holds a credential. At [level 3](okfm-level-3.md) your agent drives OKFM and is
authenticated in your own tool; here OKFM drives a provider. Every other component on this
list follows from having a process that can act unattended.
