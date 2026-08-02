---
type: Decision
title: "DR-0010 — OKFM's own repository is the first mesh"
description: "OKFM's own repository is the first mesh — one OKF per folder of documents under .okfm/, a generated master OKF over them, and federation's addressing half proven on real content. The master maps the mesh and deliberately does not run it."
status: draft
verified: { by: "human:analytics206", at: 2026-08-02T03:08:50Z }
tags: [mesh, federation, self-hosting]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0010-okfm-self-hosts-as-a-mesh.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:66dd4977a4231d7add92f6faa87a8f47c82d3e63193deb840f14cd5a560c1a05", at: 2026-08-01 }
okfm_scope: project
---
# DR-0010 — OKFM's own repository is the first mesh

- **Status:** accepted 2026-08-01 — registry location still open below
- **Date:** 2026-08-01
- **Affects:** spec §12, §14.5, §21.5; changes the premise of [DR-0003](0003-phase-ordering.md)

## The problem it solves

§21.5 names federation as the least-evidenced thing in the design: *"Nothing in the
ecosystem so far covers the loop family, federation, content-based drift, perspectives, or
declared-versus-observed — which is both an opportunity and a warning that those parts have
no prior art to borrow from and will have to be proven here."*

Meanwhile the repository ships one bundle. The concept the project is named for — a **mesh**,
an OKF of OKFs — is described at length in §12 and demonstrated nowhere. A visitor opens the
viewer and sees a single bundle, which is exactly the thing OKFM says is not enough.

## Decision

**Each adoption level is its own bundle, with a registry bundle over them.** OKFM's
repository becomes a working mesh of five bundles, and the web UI opens on the thing the
project is about.

```text
okfm-registry/          the map — one OKF Member concept per bundle below
okfm-guide/             level 1 — the format, the guide, the web UI
okfm-process/           level 2 — the deterministic build
okfm-enrich/            level 3 — the reasoning components
okfm-suite/             level 4 — providers, packs, federation, workflows
```

The registry owns **only the map**: membership, scopes, aliases, cross-member links. It
never owns member content (§12.2).

## Is this really federation, or is it theatre?

Worth answering honestly, because overclaiming here would be the exact failure §21.5 warns
about.

**What it genuinely proves:** the registry bundle, `OKF Member` concepts, mesh-level
progressive disclosure, cross-bundle references with commit pinning, cross-bundle drift, and
a web UI rendering more than one bundle. All of that is real and none of it currently exists.

**What it does not prove:** transport, an agent as the access-control point, or feedback
between separate accountable owners. Co-located bundles under one steward call in-process,
which §12.6 explicitly permits — *"do not make them converse through chat completions for
theater."*

**Is the split legitimate under §12.1?** Yes, and not by size. §12.1 gives three criteria —
a different accountable person, a different change cadence, or an access boundary. The
levels differ sharply on the second: Level 1 changing means the **format** changed and every
adopter is affected; Level 4 changing is a routine release nobody downstream notices. That
is a real seam, and pinning across it is meaningful rather than ceremonial — a Level 2
concept citing a Level 1 concept should pin, because the format moving under it matters.

## The remote member closes the gap

The one part of federation a single repository cannot prove is transport. A **hosted OKFM
instance** — see [DR-0009](0009-adoption-levels.md) on Level 4 as an online reference —
supplies it: a bundle that lives somewhere else, is reached through its own agent, is pinned
by commit, and decides for itself what to share.

That single addition turns the demonstration from "several directories" into a mesh with a
real network boundary, and it exercises `okf://` resolution, pinning, and §12.6's
access-control property against something that can actually refuse.

## Consequence for DR-0003

[DR-0003](0003-phase-ordering.md) argued for moving federation *after* the SugarPaws3d port,
on the grounds that it is unproven work standing between the project and its only measurable
payoff.

That argument was about the **expensive** half — transport, agent interfaces, the feedback
ledger, cross-owner negotiation. It still holds for that half.

But this record splits federation in two, and the cheap half is nearly free:

| Half | Contains | When |
|---|---|---|
| **Addressing** | registry bundle, `OKF Member`, cross-bundle refs, pinning, cross-bundle drift, multi-bundle web UI | **Phase 1** — the content already exists |
| **Negotiation** | agent interfaces, transport, feedback inbox/outbox, cross-owner routing | after the port, per DR-0003 |

DR-0003 should be amended rather than reversed: the addressing half moves into Phase 1
because it costs almost nothing and proves the project's central metaphor on day one; the
negotiation half stays where DR-0003 put it.

## Amendment — the mesh grows as levels ship

The decision above implies authoring five bundles at once, four of which describe levels that
do not exist yet. That is exactly the failure the "What this costs" section warns about, and
it is avoidable: **the registry starts with the bundles that are real and gains a member when
a level ships.**

Today two bundles are real, and neither requires inventing anything:

| Bundle | Is | Why it qualifies |
|---|---|---|
| `okfm-guide/` | level 1, the format | Already exists |
| `docs/decisions/` | the decision record set | Already exists, and every file is literally a `Decision` |

`okfm-process/`, `okfm-enrich/`, and `okfm-suite/` join when Phases 1, 2, and 3 build them.
A registry naming a member that does not exist would be the mesh lying about itself in the
one place it cannot afford to.

**The decision records are the better of the two demonstrations.** They pass §7.7's admission
test outright — a decision record records *why*, the alternative rejected, the reasoning that
would otherwise evaporate, none of which any source file can state. They are also real
`Decision` concepts of the loop family (§7.5), authored by a human, which makes them
tier-`[human]` under [DR-0008](0008-build-pipeline.md) and correct by construction. And they
directly serve success measure §20.2: *"Why did we decide X?" answered from the bundle in one
query.*

Two real members with genuine content beat five with four restating a README.

## What this costs

Real but small:

- The guide's concepts move from `okfm-guide/` root into a bundle that is now one member
  among five. The web UI's baked index gains a `bundles` array with five entries instead of
  one — it already supports this; the field exists and is unused.
- Four new bundles need real concepts, not stubs. The content largely exists already — each
  level's design is written down in this decision record set — but it has to be authored as
  concepts, and the admission test (§7.7) applies. A bundle of five restatements of the
  README is worse than no bundle.
- Cross-bundle pins have to be maintained, which is the point: it is the first time the
  project feels its own pinning discipline.

## Against

**Five bundles for one repository is over-structuring.** It would be, if the split were by
size. It is by change cadence, which is a §12.1 criterion, and the alternative is a project
about meshes that has never run one.

**The guide gets harder to delete.** §14.5's `rm -rf okfm-guide/` currently has no
consequences. Under this record the registry would carry a dangling member. Mitigation: the
registry treats a missing member as a resolvable condition, not an error — which is
§6.7's tolerance requirement applied to the mesh level, and worth proving anyway.

## Amendment 2026-08-01 — the mesh lives in `.okfm/`, and every folder gets one

The four level bundles were built, and building them settled three things this record had
guessed at.

**Layout.** Bundles do not sit at the repository root. Everything OKFM produces lives under
`.okfm/`, one subfolder per bundle, beside a `docs/` tree it never writes to. Two folders,
each with an obvious owner, and `rm -rf .okfm` returns the project to what it was. The naming
below is superseded: `okfm-process` / `okfm-enrich` / `okfm-suite` became
`.okfm/level-2-build` / `level-3-enrich` / `level-4-suite`, matching the folders in
`docs/okfm-guide/` they are built from.

**One OKF per folder of documents, not per level.** The level split was a special case of a
better default: any folder that holds documents is a unit somebody already decided to
separate, so it becomes a bundle. `docs/guides/` and `docs/architecture/` are apart because
they are about different things, and mirroring that arrangement needs no configuration to get
right. Loose files at the top of `docs/` become a bundle too, and both exclusions —
a subtree, or the top-level files — are config keys.

**The master OKF is generated.** `build.py` writes the mesh: one `OKF Member` concept per
bundle plus the map. A map maintained by hand disagrees with its territory eventually, and the
disagreement is silent — the same argument that already made the web UI index generated rather
than checked.

### What this cost, and one thing it caught

Six bundles became eight and the record's arithmetic changed twice, which is the expected
price of a layout decision made before the thing exists.

It also surfaced a real defect. `build.py` overwrote every concept it had generated,
unconditionally. That was invisible while all bundles were hand-authored, and it would have
destroyed level 3's enrichment on the first rebuild afterwards — silently, on the command an
adopter runs most often. The build now writes only concepts nothing else has touched, judged
by `generated.by` and the presence of `verified`.

A layout change is not usually where you expect to find a data-loss bug. It was found because
moving the bundles forced a rebuild against content somebody had already improved, which is
exactly the situation the bug needed and the situation no earlier test had created.

## Settled details

**The registry does not sit at the repository root.** Root would read as a master bundle,
which §12.2 warns against, and a registry that sits beside its members rather than above them
says the right thing about what it owns. It lives at `.okfm/mesh/` — see the amendment above;
the original `okfm-registry/` was renamed for findability, since "registry" is a synonym a
visitor should not have to learn for the thing the project is named after.

**Two scopes.** `guide` for teaching material, excluded everywhere including here. `project`
for OKFM's own knowledge about itself — counted in this repository's statistics, because the
decision records genuinely are this project's mesh. An adopter who vendors OKFM adds
`project` to their exclusions.

**A hosted instance is Phase 4**, with the negotiation half of federation. The local mesh
proves addressing; transport is the thing a hosted member adds, and transport is Phase 4
work per [DR-0003](0003-phase-ordering.md).

## Amendment 2026-08-02 — the master OKF maps the mesh; it does not run it

Asked directly and answered: **no orchestrator.** The master OKF owns membership and nothing
else.

Three things "running the mesh" could have meant, and where each landed:

| Reading | Verdict |
|---|---|
| Routes questions to member bundles and gathers answers | No. That is an agent's job, and it belongs to federation's negotiation half. |
| Drives the build — reads the mesh to decide what to rebuild | No. The build reads configuration; the mesh is an output of the build, and a thing that is both input and output of the same process is a loop waiting to be discovered. |
| Owns membership as data | Yes, and it already does. |

The reason is the one §12.2 gives and this record has stated from the start: index-*over*,
not authority-*over*. A registry that orchestrates has to decide, and a thing that decides on
behalf of bundles it does not own is a central authority wearing a map's clothes — which is
the failure mode federation exists to avoid.

This closes the "registry location still open" note in the status line above. The location is
`.okfm/mesh/`, its job is the map, and the job is not going to grow.
