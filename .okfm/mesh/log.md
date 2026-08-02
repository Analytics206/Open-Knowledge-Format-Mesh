---
type: Log
title: Mesh changelog
description: Append-only history of mesh membership.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# 2026-08-01 — four level bundles joined; the mesh moved to `.okfm/`

Membership went from two to six. `okfm-level-1` through `okfm-level-4` were authored as
component inventories: one concept per thing the level actually ships, each carrying
`okfm_needs` and `okfm_level`, each pinning a hash of both the document that explains it and
the code that implements it.

The bundles moved out of the repository root into `.okfm/`, one subfolder each, and the
registry folder was renamed from `okfm-registry/` to `okfm-mesh/` to `.okfm/mesh/`. Two
reasons, and the second is the real one:

- **Findability.** "Registry" is jargon for the thing this project is named after. A visitor
  looking for the mesh should not have to learn a synonym first.
- **One folder.** Everything OKFM writes now lives under `.okfm/`, beside documents it never
  touches. That is the property an adopter cares about, and a project that arranges itself
  differently from the arrangement it recommends is telling on itself.

# The rule that came out of it

Mirrored bundles live in `.okfm/`; in-place bundles live with their sources. `docs/decisions/`
stays where it is because those files *are* the concepts — burying the decision records in a
hidden folder would trade the one thing they are good for.

# What the reorganisation exposed

`build.py` overwrote any concept it had generated, unconditionally. It went unnoticed while
every bundle was hand-authored, and it would have destroyed level 3's output on the first
rebuild after enrichment — silently, on the run an adopter performs most often.

Fixed: the build now writes only concepts nothing else has touched, judged by `generated.by`
and the presence of `verified`.

# 2026-08-01 — registry created with two members

`okfm-guide` and `okfm-decisions` registered. Both already existed as content; neither was
authored to populate the mesh.

The decision records were converted to concepts by `dropin/bootstrap.py` — deterministic
extraction, no model — so every description is copied from text the record already contained
and every concept landed `status: draft` with no `verified` entry. That is the honest state:
extraction produced them, nobody has reviewed them.

# Two scopes, and what they mean

`okfm_scope: guide` — teaching material. Excluded from health statistics, the injected index,
and benchmark corpora everywhere, including here. It renders in the viewer and counts toward
nothing.

`okfm_scope: project` — OKFM's own knowledge about itself. Counted in *this* repository's
statistics, because the decision records genuinely are this project's mesh. An adopter who
vendors OKFM adds `project` to their `exclude_scopes` so it stays out of theirs.

A first finding from standing the mesh up: the viewer hardcodes the excluded scope to
`guide` rather than reading `exclude_scopes` from configuration. Correct today by
coincidence rather than by construction, and worth fixing when `okfm view` is built.
