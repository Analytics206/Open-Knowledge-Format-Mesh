---
type: Document
title: The agent contract
description: One file that tells an agent what it may write, what it may not, and how to tell the difference. No install, no key.
status: draft
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
sources:
  - id: doc
    resource: ../../docs/guide/level-3-enrich/the-agent-contract.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:1b042e6bf6cf092f20f069e70c92fd432ffe1bbc4d410c8385212070bdd429ec", at: 2026-08-01 }
  - id: implementation
    resource: ../../templates/AGENTS.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:ae6680b5f4086eb71db02fc04800751008c7fdc849cc0999659c5806a2304e88", at: 2026-08-01 }
okfm_scope: project
okfm_level: 3
okfm_needs: [model]
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: implements, target: /the-enrichment-loop.md }
---

# The agent contract

The text is in [`docs/guide/level-3-enrich/the-agent-contract.md`](../../docs/guide/level-3-enrich/the-agent-contract.md). This concept
records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.
