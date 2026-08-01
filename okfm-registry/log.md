---
type: Log
title: Registry changelog
description: Append-only history of mesh membership.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# 2026-08-01 — registry created with two members

`okfm-guide` and `okfm-decisions` registered. Both already existed as content; neither was
authored to populate the mesh.

The decision records were converted to concepts by `scripts/bootstrap.py` — deterministic
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
