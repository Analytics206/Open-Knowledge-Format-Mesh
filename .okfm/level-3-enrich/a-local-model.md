---
type: Document
title: A local model
description: "Level 2+ — OKFM drafts descriptions itself with Ollama on hardware the adopter owns, keeping level 2's no-key-no-bill terms while the component still declares `needs-model` and the checked 2/3 boundary stays where it was."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T02:15:13Z }
tags: [needs-model]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T08:10:00Z }
sources:
  - id: source
    resource: ../../docs/okfm-guide/level-3-enrich/a-local-model.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:36de1a83aa34ebac61216efa85a0035be401425a5ece9fcb95314e45fc2bce33", at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# A local model — Level 2+

The text is in [`docs/okfm-guide/level-3-enrich/a-local-model.md`](../../docs/okfm-guide/level-3-enrich/a-local-model.md).
This concept records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.

`needs-model` is the whole point of the tag being here. This is the **only** concept in a
level bundle whose component actually calls a model, and the first thing in the drop-in
folder that is not `needs: []`. It is also absent from the pipeline, which is what keeps the
default run at `needs: []` under the union rule — see
[DR-0013](../../docs/decisions/0013-the-local-model-variant.md).
