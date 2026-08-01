# DR-0010 — OKFM's own repository is the first mesh

- **Status:** **accepted** 2026-08-01 — *"a big key to this project is the OKF of OKFs. I
  think we need to show that."* Registry location still open below
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
repository becomes a working mesh of five bundles, and the viewer opens on the thing the
project is about.

```text
okfm-registry/          the map — one OKF Member concept per bundle below
okfm-guide/             level 1 — the format, the guide, the viewer
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
a viewer rendering more than one bundle. All of that is real and none of it currently exists.

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
| **Addressing** | registry bundle, `OKF Member`, cross-bundle refs, pinning, cross-bundle drift, multi-bundle viewer | **Phase 1** — the content already exists |
| **Negotiation** | agent interfaces, transport, feedback inbox/outbox, cross-owner routing | after the port, per DR-0003 |

DR-0003 should be amended rather than reversed: the addressing half moves into Phase 1
because it costs almost nothing and proves the project's central metaphor on day one; the
negotiation half stays where DR-0003 put it.

## What this costs

Real but small:

- The guide's concepts move from `okfm-guide/` root into a bundle that is now one member
  among five. The viewer's baked index gains a `bundles` array with five entries instead of
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

## Open

- Does the registry live at `okfm-registry/` or at the repository root? Root reads as
  "master bundle," which §12.2 explicitly warns against.
- Do the four level bundles carry `okfm_scope: guide` like the current guide does, so they
  stay out of an adopter's statistics? Probably yes for all of them, with `exclude_scopes`
  doing the same work it does today.
- Does a hosted instance need to exist before Phase 1 exits, or is it a Phase 2 addition
  with the local four-bundle mesh sufficient for now?
