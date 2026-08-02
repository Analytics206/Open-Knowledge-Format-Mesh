---
type: Document
title: The benchmark
description: "Two arms over one corpus, blind grading, and a harness that reports what it found about this repository rather than producing a flattering number. The deterministic half runs today."
status: draft
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:09:28Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-3-enrich/the-benchmark.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:a69ee059b02c504c51cd0dc73fb41a86c615eb301d191721f81e52abccd8f18b", at: 2026-08-01 }
  - id: implementation
    resource: ../../benchmark/run.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:ff61dc6dd30f1ef5ac43cc469e19112de57a667dca2a421a2aa95b2a7f7e7020", at: 2026-08-01 }
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
