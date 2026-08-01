---
type: Concept
title: Federation
description: Many bundles, many owners, feedback instead of writes.
status: stable
tags: [mesh, ownership, federation]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# You probably do not need this yet

A single bundle is the common case, and `federation: null` is a valid mesh. Federation
appears when a *second owner* does — not when a bundle gets big.

That is the split criterion, and it is the whole design in one line:

> **Split on ownership, not size.**

Split where a different person is accountable, where change cadence differs, or where
an access boundary exists. Splitting for size alone just produces agents negotiating
across an arbitrary line.

# The registry is a bundle too

The mesh describes itself in its own format. Members are concepts of type `OKF Member`
carrying an owner, aliases, and how to reach that bundle's agent.

The registry owns **only the map** — membership, scopes, cross-member links. It never
owns member content. It is index-*over*, not authority-*over*; calling it a master
bundle would smuggle central authority back into a design that exists to prevent it.

Routing is scatter-gather: a question goes to the registry, the registry names the
relevant members, those members answer from their own bundles, and citations resolve
back into each contributing bundle. There is no global index over everything, ever.

# Two invariants

**Cross-bundle references pin a commit.** Your meaning must not change because another
owner published. Their newer commit is an *offer*; moving to it is a recorded decision
in your bundle. Git history is the version system — nothing here invents a version
integer.

**No cross-bundle writes, ever.** Feedback is the only inbound channel. You file a
`Feedback` concept into another bundle's inbox; its owner accepts it (a commit in
*their* bundle, plus a response) or declines it with reason codes. Either way the
exchange is durable.

That ledger is quietly one of the most valuable things in a mesh: the record of
inter-domain negotiation that in most organizations happens in chat and evaporates.

# Nobody owns "churn"

A shared concept lives in the registry. Each domain bundle owns its own `Perspective`
and `Rule` for it, linked across bundles. Billing churn and engagement churn are both
correct, they answer different questions, and the mesh holds both simultaneously
without either winning.

Bundles may disagree indefinitely and visibly. There is no consensus requirement, and
any feature that would add one is a design smell.

# What federation does not add

No central ontology. No global search index. No cross-bundle writes. No consensus.
Each of those would re-centralize the mesh.
