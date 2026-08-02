---
type: Document
title: The tier guard
description: "Reads the diff after an edit pass and fails on any field the editor does not own, naming the field and the reason. Scope it to the paths the pass touched, or it reports everything else in flight."
status: draft
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:28:25Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-3-enrich/the-tier-guard.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:4c46f7d397be9d48b18fe0642726604f765e9ed7bd58216d1940e4a4cd0969ef", at: 2026-08-01 }
  - id: implementation
    resource: ../../dropin/guard.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:047b8565796a4fa7ab9e0e06fb0bed62693107cad4a52e227a137386f8a7121a", at: 2026-08-01 }
okfm_scope: project
okfm_level: 3
okfm_needs: []
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: implements, target: /the-agent-contract.md }
---

# The tier guard

The text is in [`docs/okfm-guide/level-3-enrich/the-tier-guard.md`](../../docs/okfm-guide/level-3-enrich/the-tier-guard.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
