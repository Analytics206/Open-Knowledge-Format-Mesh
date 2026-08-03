---
type: Document
title: The tier guard
description: "Reads the diff after an edit pass and fails on any field the editor does not own, naming the field and the reason. Scope it to the paths the pass touched, or it reports everything else in flight."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T02:15:13Z }
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:28:25Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-3-enrich/the-tier-guard.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:02100e544646947a1be54a24fb7b7e2bbd71010c195ab913def47f45956b3d4e", at: 2026-08-03 }
  - id: implementation
    resource: ../../dropin/guard.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:fcd121282e05f114733eb64d8214f91b4c9a7fd7e9415fe46457d1c2596ded2d", at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: implements, target: /the-agent-contract.md }
---

# The tier guard

The text is in [`docs/okfm-guide/level-3-enrich/the-tier-guard.md`](../../docs/okfm-guide/level-3-enrich/the-tier-guard.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
