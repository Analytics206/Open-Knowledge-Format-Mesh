---
type: Index
title: OKFM mesh registry
description: The map of this repository's bundles. Owns membership, never member content.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# What this is

The registry is itself an OKF bundle — the format describing the mesh in its own terms. Each
member below is a concept of `type: OKF Member` naming a bundle, its owner, and its scope.

**The registry owns only the map.** Membership, scopes, aliases, and cross-member links live
here. Member content never does. It is index-*over*, not authority-*over*; calling this a
master bundle would smuggle central authority back into a design that exists to prevent it.

# Members

- [okfm-guide](members/okfm-guide.md) — the format, and a bundle that demonstrates it
- [okfm-decisions](members/okfm-decisions.md) — why this project is shaped the way it is

# Why only two

The mesh names the bundles that exist. `okfm-process`, `okfm-enrich`, and `okfm-suite` join
when Phases 1, 2, and 3 build them — a registry naming a member that does not exist would be
the mesh lying about itself in the one place it cannot afford to.

See [DR-0010](../docs/decisions/0010-okfm-self-hosts-as-a-mesh.md).

# What this proves, and what it does not

**Proves:** the registry pattern, `OKF Member` concepts, mesh-level progressive disclosure,
and a viewer rendering more than one bundle.

**Does not prove:** transport, an agent as the access-control point, or feedback between
separate accountable owners. These bundles are co-located under one steward and resolve
in-process, which §12.6 permits explicitly — *"do not make them converse through chat
completions for theater."* The negotiation half of federation is later work.
