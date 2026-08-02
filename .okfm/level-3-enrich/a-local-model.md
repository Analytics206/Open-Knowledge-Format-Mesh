---
type: Document
title: A local model
description: "OKFM drafts descriptions itself using Ollama on the adopter's own machine — level 3's local variant, which removes the key without removing the model and so sits at `needs-model` with no `needs-secrets`."
status: draft
tags: [needs-model]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T06:55:00Z }
sources:
  - id: source
    resource: ../../docs/okfm-guide/level-3-enrich/a-local-model.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:f2556f63976827e5d4f9f333ccd4d9f79ce27ca678140040dc8904f98bf1aa2b", at: 2026-08-02 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# A local model

The text is in [`docs/okfm-guide/level-3-enrich/a-local-model.md`](../../docs/okfm-guide/level-3-enrich/a-local-model.md).
This concept records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.

`needs-model` is the whole point of the tag being here. This is the **only** concept in a
level bundle whose component actually calls a model, and the first thing in the drop-in
folder that is not `needs: []`. It is also absent from the pipeline, which is what keeps the
default run at `needs: []` under the union rule — see
[DR-0013](../../docs/decisions/0013-the-local-model-variant.md).
