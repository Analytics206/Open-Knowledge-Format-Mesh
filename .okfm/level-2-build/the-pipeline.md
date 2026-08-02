---
type: Runbook
title: The pipeline
description: One command that runs build, refresh, bake and validate in order and stops at the first failure.
status: draft
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
sources:
  - id: doc
    resource: ../../docs/guide/level-2-build/the-pipeline.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:b3f1e4ba75ec26341354120d6d026bef7fdbe6d9432b51784c38340a27d9a2f0", at: 2026-08-01 }
  - id: implementation
    resource: ../../dropin/okfm.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:e143d513b02a19c9088dd029fa91e7b485ceab088895646458ca9b0c490fc249", at: 2026-08-01 }
okfm_scope: project
okfm_level: 2
okfm_needs: []
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The pipeline

The text is in [`docs/guide/level-2-build/the-pipeline.md`](../../docs/guide/level-2-build/the-pipeline.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
