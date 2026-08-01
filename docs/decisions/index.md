# Decision records

Dated, numbered, short. One decision per file, kept even when superseded — the record of
what was decided and why is worth more than a tidy list of what is currently true.

`proposed` means it needs a call before the affected work starts. `accepted` means it was
made and acted on.

| # | Decision | Status | Affects |
|---|---|---|---|
| [0001](0001-runtime-and-packaging.md) | Runtime and packaging for core | **proposed** | §13.3, §13.6, §13.7 |
| [0002](0002-version-scheme.md) | Version scheme | deferred | versioning policy, `okfm.json` |
| [0003](0003-phase-ordering.md) | Where federation sits in the delivery order | **proposed** | §15 |
| [0004](0004-split-the-spec-preserve-numbers.md) | Split the spec, preserve section numbers | accepted | all four documents |
| [0005](0005-path-resolution.md) | Bundle-relative in files, mesh-relative in the index | accepted | §6.5, §7.3, §12.3, §14.2 |
| [0006](0006-drift-cost-and-caching.md) | What drift costs, and where the answer is cached | **proposed** | §3.4, §8.3–8.5, §13.4, §14.4, §20.8 |
| [0007](0007-two-layers.md) | Base installs nothing; the implementation is optional | **proposed** | §13.2, §13.3, §13.6, §13.7, §14 |
| [0008](0008-build-pipeline.md) | What each component requires, and what the rebuild does | **proposed** | §8.4, §10, §11.6, §13.6, §16 |
| [0009](0009-adoption-levels.md) | Four adoption levels | **proposed** | §13.1, §13.3, §13.6, §13.7 |
| [0010](0010-okfm-self-hosts-as-a-mesh.md) | OKFM's own repository is the first mesh | **proposed** | §12, §14.5, §21.5 — amends 0003 |
| [0011](0011-viewer-and-console.md) | Viewer stays read-only; a console is separate | **proposed** | §14.3, §14.7 |

## Two different axes, easily confused

**[0009](0009-adoption-levels.md) classifies adopters** by how deeply they engage — read and
copy, run the process, agent-generated, full suite. It decides what ships, what the README
promises, and how the repository is laid out. An adopter picks their own level.

**[0008](0008-build-pipeline.md) classifies components** by what they require to execute —
`[]`, `human`, `model`, `secrets`. It decides which CI job may run a thing and which fields
it may write. An adopter never sees it.

They meet at exactly one boundary: **the Level 2 / Level 3 line is the `model` line.** If
anything shipped at Level 2 declares `model`, the build fails. That is what keeps "never
needs an API key" true as the implementation grows, rather than a promise that quietly rots.

## Read these three together

0007, 0008 and 0001 are one architectural decision seen from three angles, and 0007 is the
one that moves first.

**0007** says OKFM is a format contract that installs nothing, plus a reference
implementation that is optional and replaceable. **0008** has every component declare what
it requires — `[]`, `human`, `model`, `secrets` — ordered by exposure, with a composite's
set being the *union* of everything it invokes. CI gates on the set, not on the tier
number. **0001** then only has to answer a much smaller question, because it now applies to
the optional layer alone.

## Still open

**0009** blocks the Phase 1 directory layout and the README's shape, and it is the one to
settle first — the other records are easier to answer once it is clear who each level is
for.

**0007** blocks the same layout from the other direction. Cheap now; expensive once the CLI
has quietly become load-bearing for reading the format.

**0008** blocks Phase 1's validator, because the tier model decides what the build is
allowed to rewrite.

**0001** decides language and install path for the implementation. Rescoped by 0007.

**0006** must be settled before the Phase 2 resolvers, because it decides what a resolver
returns on a cold cache.

**0010** makes OKFM's own repository a five-bundle mesh, which is how the project stops
describing federation and starts running it. Blocks the Phase 1 layout alongside 0009.

**0011** keeps the read-only viewer intact and puts writes in a separate console. Not urgent
— Phase 3 — but it decides where DR-0008's `[human]` tier gets an interface.

**0003** decides whether the *negotiation* half of federation lands before or after the
SugarPaws3d port. Amended by 0010, which moved the *addressing* half into Phase 1.

## Settled

**0002** — keep `v0.2.1`. The number pins to OKF v0.2 deliberately, is not expected to move
soon, and has a single user. Every cost in that analysis is a publication cost, and nothing
publishes yet. The record carries a re-entry trigger; the one to watch is the first
breaking change to an `okfm_` key, which can arrive quietly while the profile is still
settling in Phase 1.

**0004** — the spec is split four ways with section numbers preserved.

**0005** — bundle-relative paths in files, mesh-relative in the generated index.

## Settled

**0002** — keep `v0.2.1`. The number pins to OKF v0.2 deliberately, is not expected to move
soon, and has a single user. Every cost in that analysis is a publication cost, and nothing
publishes yet. The record carries a re-entry trigger; the one to watch is the first
breaking change to an `okfm_` key, which can arrive quietly while the profile is still
settling in Phase 1.
