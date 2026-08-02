---
type: Document
title: The web UI bake
description: "Regenerates the index the level 1 web UI reads, so disagreement between the web UI and the mesh is a state that cannot exist rather than a bug you can have."
status: draft
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:09:28Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-2-build/the-web-ui-bake.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:7877ee60478b23a7e1509b951d019e81b1008628532ba7bf8c6ac1716a430c8a", at: 2026-08-01 }
  - id: implementation
    resource: ../../dropin/bake_web_ui.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:d90ed39dc8b87df9e70ad7857cf21c5a93a1ad59dd9e28aa742d963037908d2b", at: 2026-08-01 }
okfm_scope: project
okfm_level: 2
okfm_needs: []
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: depends_on, target: /drift-observation.md }
---

# The web UI bake

The text is in [`docs/okfm-guide/level-2-build/the-web-ui-bake.md`](../../docs/okfm-guide/level-2-build/the-web-ui-bake.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
