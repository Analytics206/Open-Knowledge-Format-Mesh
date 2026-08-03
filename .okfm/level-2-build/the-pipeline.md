---
type: Runbook
title: The pipeline
description: "One command that runs build, refresh, bake and validate in order and stops at the first failure, so the second, misleading error never appears."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T02:22:16Z }
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:09:28Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-2-build/the-pipeline.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:3dc7feee781be3f1b2e00596022eb48c51280491fd238ca0432ab6c159a762d0", at: 2026-08-03 }
  - id: implementation
    resource: ../../dropin/okfm.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:6d6ab37bb80641675980e3d2b209c2e7fd0d550f48d2520904ceb564a48a5f0f", at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The pipeline

The text is in [`docs/okfm-guide/level-2-build/the-pipeline.md`](../../docs/okfm-guide/level-2-build/the-pipeline.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
