---
type: Document
title: The web UI bake
description: "Regenerates the index the level 1 web UI reads, so disagreement between the web UI and the mesh is a state that cannot exist rather than a bug you can have."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T07:29:12Z }
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:09:28Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-2-build/the-web-ui-bake.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:0d157e95fc1b14727eb5f87a2203d9ecb3369e1aea29964ac1c5115102a8826d", at: 2026-08-03 }
  - id: implementation
    resource: ../../dropin/bake_web_ui.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:99dae27ec47a90e0719fdb985fe00a6184e7b507bb99cab57349aa9f200bfde8", at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: depends_on, target: /drift-observation.md }
---

# The web UI bake

The text is in [`docs/okfm-guide/level-2-build/the-web-ui-bake.md`](../../docs/okfm-guide/level-2-build/the-web-ui-bake.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
