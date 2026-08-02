---
type: Log
title: Level 1 changelog
description: Append-only history of what level 1 ships.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_level: 1
---

# 2026-08-01 — bundle created

Level 1 became a bundle rather than a README section. Its three components already existed;
none was authored to populate the mesh.

The bundle exists so the level ladder is made of data instead of prose. `okfm_needs: []` on
every component here is checked by [`dev/check_levels.py`](../../dev/check_levels.py), which
is what turns *"level 1 needs nothing"* from a claim into a build failure when it stops being
true.
