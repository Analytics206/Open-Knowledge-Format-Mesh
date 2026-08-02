---
type: Index
title: "Level 1 — view"
description: Download the repository and open the web UI. Nothing to install, nothing to run.
status: stable
tags: [needs-nothing]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: registered_by, target: /mesh/index.md }
---

# What this level is

A download. Clone or unzip the repository, open `okfm-web-ui.html` in a browser, and read.
There is no install step, no build, no configuration, and nothing to run.

That is the whole of level 1, and the brevity is deliberate: the cheapest way to find out
whether a knowledge format is worth anything is to look at one.

# Components

- [The web UI](the-web-ui.md) — the graph, the health panel, the closure ledger
- [The shipped mesh](the-shipped-mesh.md) — six real bundles to read, not a worked example
- [Your own agent](your-own-agent.md) — point it here and ask for whatever you want

# Where the line is

Every component here is tagged `needs-nothing`. OKFM asks nothing of you at this level — no
runtime, no key, no network.

[Your own agent](your-own-agent.md) is the one that looks like an exception and is not. The
model is yours, running in a tool you already pay for; OKFM is supplying files it reads.
the `needs-*` tag records what **OKFM** requires to deliver a component, not what you happen to
bring. The distinction is what stops the levels collapsing into "you could always use an
agent" — which is true, and which would make the whole ladder meaningless.

# What you cannot do here

Build a bundle for your own project. That is [level 2](../level-2-build/index.md), and it is
one folder and one command away.
