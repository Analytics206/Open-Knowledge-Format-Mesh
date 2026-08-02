---
type: Index
title: The OKFM mesh
description: The master OKF — an OKF whose concepts are the other OKFs. Owns membership, never member content.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# What this is

The OKF of OKFs. This bundle's concepts are the other bundles: each member below is a concept
of `type: OKF Member` naming a bundle, its owner, its aliases, and its scope.

It is the format describing the mesh in the format's own terms, which is the point — a project
about knowledge meshes that could not represent its own would be arguing from nothing.

**It owns only the map.** Membership, scopes, aliases, and cross-member links live here.
Member content never does. This is index-*over*, not authority-*over*: an owning bundle would
smuggle central authority back into a design that exists to prevent it.

# Members

| Member | Is |
|---|---|
| [okfm-level-1](members/okfm-level-1.md) | the download — viewer, bundles, your own agent |
| [okfm-level-2](members/okfm-level-2.md) | the deterministic build |
| [okfm-level-3](members/okfm-level-3.md) | the enrichment loop |
| [okfm-level-4](members/okfm-level-4.md) | providers, packs, federation, the benchmark |
| [okfm-guide](members/okfm-guide.md) | the format, and a bundle that demonstrates it |
| [okfm-decisions](members/okfm-decisions.md) | why this project is shaped the way it is |

# Where the members live

Five of the six are under [`.okfm/`](..), one subfolder each. The sixth,
[`docs/decisions/`](../../docs/decisions/index.md), is **in place** — those files are the
decision records *and* the concepts, so they stay where a person would look for them.

That is the general rule rather than an exception for this repository: mirrored bundles live
in `.okfm/`, in-place bundles live with their sources, and the mesh registers both by path.

# Why the split is legitimate

Not by size. The bundles differ on **change cadence**, which is a §12.1 ownership criterion: a
level 1 change means the entry experience moved and everyone is affected; a decision record is
appended weekly and nobody downstream notices. Splitting a repository by size would be
theatre; splitting it on a real seam is what makes cross-bundle pinning mean something.

# What this proves, and what it does not

**Proves:** the registry pattern, `OKF Member` concepts, mesh-level progressive disclosure,
cross-bundle references, and a viewer rendering seven bundles at once.

**Does not prove:** transport, an agent as the access-control point, or feedback between
separate accountable owners. These bundles are co-located under one steward and resolve
in-process, which §12.6 permits explicitly — *"do not make them converse through chat
completions for theater."* What is missing is a member that can **refuse**, and that needs a
bundle somewhere else. See [level 4](members/okfm-level-4.md).

See [DR-0010](../../docs/decisions/0010-okfm-self-hosts-as-a-mesh.md) for how the mesh got
here, including the parts of that record this layout has since overtaken.
