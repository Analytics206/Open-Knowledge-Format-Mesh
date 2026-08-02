---
type: Index
title: "Level 4 — the suite"
description: Providers, packs, the negotiation half of federation, and the benchmark. Mostly not built yet, and this bundle says which parts.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_level: 4
okfm_needs: [secrets]
---

# What this level is

The full harness: you supply a key, choose a provider, and OKFM runs the loop itself instead
of handing work to your agent. Packs carry domain vocabulary, federation gains transport, and
the benchmark measures whether any of it is worth the trouble.

# Components

| Component | State | Needs today |
|---|---|---|
| [The benchmark](the-benchmark.md) | prototype runs | — |
| [Providers and keys](providers-and-keys.md) | designed, not built | — |
| [Packs](packs.md) | partly built — vocabulary overlays work | — |
| [Federation, the negotiation half](federation-negotiation.md) | designed, not built | — |
| [The web UI](the-web-ui.md) | designed, not built | — |

Four of five are `status: draft` and say so. A level bundle that described unbuilt components
as though they shipped would be the mesh lying about itself in the one place it cannot afford
to.

# What actually changes at this level

The direction reverses. At [level 3](../level-3/index.md) your agent drives OKFM and
you are already authenticated in your own tool. Here OKFM drives a provider, which means OKFM
holds a credential — and that single fact is why keys appear at this level and not one
earlier.

Everything else on this list follows from having a process that can act on its own: a
provider to act through, packs so it knows a domain's words, transport so it can reach another
owner's bundle, and a benchmark because a system that writes its own knowledge unattended
needs a way to find out whether the knowledge helps.

# The honest reading of this bundle

It is a plan with one working piece. That is worth registering as a bundle anyway, because
the level ladder is data — the mesh should be able to answer *what exists at level 4* without
anyone reading a roadmap, and today the answer is "the benchmark prototype, and vocabulary
overlays."
