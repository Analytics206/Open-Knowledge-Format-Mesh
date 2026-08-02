---
type: Index
title: Decision records
description: What was decided about OKFM, why, and what would reverse it.
status: stable
generated: { by: "human:analytics206", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: registered_by, target: /okfm-mesh/index.md }
---

# Decision records

Dated, numbered, short. One decision per file, kept even when superseded — the record of
what was decided and why is worth more than a tidy list of what is currently true.

`accepted` was decided. `deferred` was decided *not* to decide, and carries a re-entry
trigger. Nothing here is a blocking question — where a detail was open, it was decided and
noted rather than left to resurface.

These records exist so a rule that gets broken later is broken on purpose and on the record.
The [specification](../../spec/okfm-v0.2.1.md) is a working document, not law: where it and
the implementation disagree, the implementation is right and a record here says what changed.

| # | Decision | Status | Affects |
|---|---|---|---|
| [0001](0001-runtime-and-packaging.md) | Runtime and packaging for the implementation | partial | §13.3, §13.6, §13.7 |
| [0002](0002-version-scheme.md) | Version scheme | deferred | versioning policy, `okfm.json` |
| [0003](0003-phase-ordering.md) | Where federation sits in the delivery order | accepted | §15 — amended by 0010 |
| [0004](0004-split-the-spec-preserve-numbers.md) | Split the spec, preserve section numbers | accepted | all four documents |
| [0005](0005-path-resolution.md) | Bundle-relative in files, mesh-relative in the index | accepted | §6.5, §7.3, §12.3, §14.2 |
| [0006](0006-drift-cost-and-caching.md) | Drift is observed at build time, never at read time | accepted | §3.4, §8.3–8.5, §13.4, §14.4, §20.8 |
| [0007](0007-two-layers.md) | Base installs nothing; the implementation is optional | accepted | §13.2, §13.3, §13.6, §13.7, §14 |
| [0008](0008-build-pipeline.md) | What each component requires, and what the rebuild does | accepted | §8.4, §10, §11.6, §13.6, §16 |
| [0009](0009-adoption-levels.md) | Four adoption levels | accepted | §13.1, §13.3, §13.6, §13.7 |
| [0010](0010-okfm-self-hosts-as-a-mesh.md) | OKFM's own repository is the first mesh | accepted | §12, §14.5, §21.5 |
| [0011](0011-viewer-and-console.md) | Viewer stays read-only; a console is separate | accepted, built last | §14.3, §14.7 |

## Two different axes, easily confused

**[0009](0009-adoption-levels.md) classifies adopters** by how deeply they engage — read and
copy, run the process, enrich, full suite. It decides what ships, what the README promises,
and how the repository is laid out. An adopter picks their own level.

**[0008](0008-build-pipeline.md) classifies components** by what they require to execute —
`[]`, `human`, `model`, `secrets`. It decides which CI job may run a thing and which fields
it may write. An adopter never sees it.

They meet at exactly one boundary: **the Level 2 / Level 3 line is the `model` line.** If
anything shipped at Level 2 declares `model`, the build fails. That is what keeps "never
needs an API key" true as the implementation grows, rather than a promise that quietly rots.

## Still open

**0001** — settled for the lower levels: Python 3.13, standard library only in `dropin/`.
Level 4 packaging (`uvx` vs `pipx`, the PyPI name) is still open and not blocking, because
Level 4 does not exist yet.

Two smaller questions sit inside accepted records: 0008's `Feedback` destination split, and
0010's registry location. Neither blocks anything.

## Settled

**0002 — deferred.** Keep `v0.2.1`. The number pins to OKF v0.2 deliberately, is not expected
to move soon, and has a single user. Every cost in that analysis is a publication cost, and
nothing publishes yet. The re-entry trigger to watch is the first breaking change to an
`okfm_` key, which can arrive quietly while the profile is still settling in Phase 1.

**0004** — the spec is split four ways with section numbers preserved.

**0005** — bundle-relative paths in files, mesh-relative in the generated index.

**0007** — OKFM is a format contract that installs nothing, plus an optional, replaceable
reference implementation.

**0008** — every component declares what it requires, ordered by exposure, with a
composite's set being the *union* of everything it invokes. CI gates on the set, not the
tier number.

**0009** — four cumulative adoption levels, each a complete usable process rather than a
teaser for the next.

**0010** — OKFM's own repository becomes a mesh, so the project runs the thing it describes
instead of only specifying it. Amended: the registry names the bundles that exist and gains
members as levels ship.

**0003** — federation's negotiation half lands after the SugarPaws3d port; its addressing
half already landed early under 0010. Phase order: baseline and addressing → distribution →
the port → negotiation.

**0011** — a full web UI is planned and built last, as the natural consumer of everything
below it. The web UI stays read-only regardless. The CLI and the UI are one surface: every
mutation has exactly one implementation, the UI calls it, the CLI exposes it, and building
the UI is what reveals which commands are actually needed.

**0006** — drift is observed during the build and cached; nothing resolves it at read time.
Trust and staleness stay read-time because they are free. The cache stores observations, not
verdicts, and a pointer that has never been observed reports `unknown` rather than defaulting
to fresh.
