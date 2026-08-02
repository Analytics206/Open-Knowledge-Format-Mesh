---
type: Document
title: The viewer bake
description: Regenerates the index the level 1 viewer reads, so viewer-versus-mesh drift is impossible rather than merely unlikely.
status: draft
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
sources:
  - id: doc
    resource: ../../docs/levels/level-2-build/the-viewer-bake.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:7877ee60478b23a7e1509b951d019e81b1008628532ba7bf8c6ac1716a430c8a", at: 2026-08-01 }
  - id: implementation
    resource: ../../dropin/bake_viewer.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:709ffdaae2a039aa06f88cbc10b43844cddbed6bb273fb0a23ba529b3b7b9f5c", at: 2026-08-01 }
okfm_scope: project
okfm_level: 2
okfm_needs: []
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: depends_on, target: /drift-observation.md }
---

# The viewer bake

The text is in [`docs/levels/level-2-build/the-viewer-bake.md`](../../docs/levels/level-2-build/the-viewer-bake.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
