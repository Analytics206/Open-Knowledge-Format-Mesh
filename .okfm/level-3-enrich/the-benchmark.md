---
type: Document
title: The benchmark
description: "Two arms over one corpus, blind grading, and a harness that reports what it found about this repository rather than producing a flattering number. The deterministic half runs today."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T08:03:33Z }
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:09:28Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-3-enrich/the-benchmark.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:2f52920c238a09bdabe7b4fcce29be2232ef0dc5b5d83b47543558f40521dee0", at: 2026-08-03 }
  - id: implementation
    resource: ../../benchmark/run.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:997ca8673dbc6a591731b8481e780fc9d44c7a59972820d5b60f3ce4409ca92e", at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: evaluates, target: /mesh/index.md }
---

# The benchmark

The text is in [`docs/okfm-guide/level-3-enrich/the-benchmark.md`](../../docs/okfm-guide/level-3-enrich/the-benchmark.md).
This concept records what that document is, what it needs to run, and where it sits in the
level ladder — none of which the document itself states.

The needs set is `[]` and that is not a placeholder: everything built so far is arithmetic
over files. Asking a model the questions is the step that raises it, and it is deliberately
not built yet.
