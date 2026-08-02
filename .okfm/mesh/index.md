---
type: Index
title: The OKFM mesh
description: Read this first. An OKF whose concepts are the other OKFs — it answers "which one should I open?" and owns nothing else.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# Start here

This is the **entry point**. Point an agent at this file and it can find the rest without
being told what exists — which is the difference between a mesh and a folder of bundles
somebody has to enumerate for you.

Each member below is a concept of `type: OKF Member` naming a bundle, its owner, its aliases,
and the questions it answers. Nothing else lives here: membership is all this bundle owns.

# Which OKF should I read?

| If you want to know | Open | Start at |
|---|---|---|
| What makes a bundle legal — frontmatter, reserved files, the strip test | not a bundle | [`spec/okfm-v0.2.1.md`](../../spec/okfm-v0.2.1.md) |
| How to write a first concept, and what *not* to write down | [okfm-guide](members/guide.md) | [`.okfm/guide/`](../guide/index.md) |
| What I get by downloading this and running nothing | [okfm-level-1](members/level-1-view.md) | [`.okfm/level-1-view/`](../level-1-view/index.md) |
| How to build a mesh from my own docs, and what the build will and will not write | [okfm-level-2](members/level-2-build.md) | [`.okfm/level-2-build/`](../level-2-build/index.md) |
| How to point **my own agent** at it — the contract, the work list, the guard | [okfm-level-3](members/level-3-enrich.md) | [`.okfm/level-3-enrich/`](../level-3-enrich/index.md) |
| How to use **my own key and provider** | [okfm-level-3](members/level-3-enrich.md) | [providers and keys](../level-3-enrich/providers-and-keys.md) |
| Whether a CLI exists yet, and what it will be | [okfm-level-3](members/level-3-enrich.md) | [the console app](../level-3-enrich/the-console-app.md) |
| Whether curated knowledge actually helps, and how that gets measured | [okfm-level-3](members/level-3-enrich.md) | [the benchmark](../level-3-enrich/the-benchmark.md) |
| Phases, open questions, success measures, prior art | [okfm-docs](members/docs.md) | [`docs/roadmap.md`](../../docs/roadmap.md) |
| Why the project is shaped this way, and what would reverse a call | not a bundle | [`docs/decisions/`](../../docs/decisions/index.md) |

Every member carries its own share of this table as `okfm_member.answers`, so an agent can
route on frontmatter instead of parsing prose.

# Members

| Member | Owns |
|---|---|
| [okfm-level-1](members/level-1-view.md) | the download — the web UI, the bundles, your own agent |
| [okfm-level-2](members/level-2-build.md) | the deterministic build |
| [okfm-level-3](members/level-3-enrich.md) | the enrichment loop, and its credentialed variant |
| [okfm-guide](members/guide.md) | the format, and a bundle that demonstrates it |
| [okfm-docs](members/docs.md) | rationale, roadmap, prior art |

# What this does not do

**It does not route for you.** Nothing here dispatches a question, calls a member, or merges
an answer. It is a directory an agent reads; the agent does the rest.

Deliberate rather than unfinished. A registry that orchestrates has to *decide*, and a thing
deciding on behalf of bundles it does not own is central authority wearing a map's clothes —
the failure federation exists to avoid. See
[DR-0010](../../docs/decisions/0010-okfm-self-hosts-as-a-mesh.md).

**It does not own member content.** Membership, scopes, aliases, and cross-member links live
here; everything else lives in the member. Index-*over*, not authority-*over*.

# Where the members live

All of them are under [`.okfm/`](..), one subfolder each.

The general rule has two halves, and only one of them is in use here: mirrored bundles live
in `.okfm/`, and **in-place** bundles — where the documents *are* the concepts — live with
their sources, registered by path. [`docs/decisions/`](../../docs/decisions/index.md) is the
in-place case, and it is deliberately **not** a member: the records are readable where they
sit, and putting them in the mesh adds a second way to reach the same files without adding a
second thing to know.

Reinstating it is one line in `bundles`. Removing it took one, plus deleting the member
concept the build refused to throw away on its behalf.

# Why the split is legitimate

Not by size. The bundles differ on **change cadence**, a §12.1 ownership criterion: a level 1
change means the entry experience moved and everyone is affected; a decision record is
appended weekly and nobody downstream notices. Splitting a repository by size would be
theatre; splitting on a real seam is what makes cross-bundle pinning mean anything.

# What this proves, and what it does not

**Proves:** the registry pattern, `OKF Member` concepts, mesh-level progressive disclosure,
cross-bundle references, and a web UI rendering seven bundles at once.

**Does not prove:** transport, an agent as the access-control point, or feedback between
separate accountable owners. These bundles are co-located under one steward and resolve
in-process, which §12.6 permits explicitly — *"do not make them converse through chat
completions for theater."* What is missing is a member that can **refuse**, and that needs a
bundle somewhere else. See [the credentialed variant](members/level-3-enrich.md).
