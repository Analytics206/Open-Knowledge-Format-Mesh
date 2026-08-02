---
type: Document
title: Config validation
description: "Every consumer ignores keys it does not recognise, so a misspelled key does not fail — it builds the wrong thing quietly. This is the step that says so, and the rules it reads are the same table the web UI's config form is generated from."
status: draft
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T00:00:00Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-2-build/config-validation.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:26f6719ff79256008554cf9a4a47841f227b1c0839735676774df8558ce1654a", at: 2026-08-02 }
  - id: rules
    resource: ../../dropin/config_schema.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:a1dc9772faf379d3220d90196db610497f2fdcd99d101a3ad540e97ecbc260a7", at: 2026-08-02 }
  - id: implementation
    resource: ../../dropin/check_config.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:312dac2a9a60a0bac91ffa0def192a1a8401b824c80e9fb0a92124742abb60a6", at: 2026-08-02 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Config validation

The text is in [`docs/okfm-guide/level-2-build/config-validation.md`](../../docs/okfm-guide/level-2-build/config-validation.md). This concept
records what that document is, what it needs to run, and where it sits in the level ladder —
none of which the document itself states.

It pins **three** sources rather than the usual two, because the rules and the checker are
separate files on purpose: [`config_schema.py`](../../dropin/config_schema.py) holds the rules as data so the web
UI can read them too, and [`check_config.py`](../../dropin/check_config.py) is only the terminal half. Editing
either one marks this documentation drifted, which is the property the split has to keep.

`needs-nothing`: reading a JSON file and comparing strings. It runs first in the pipeline so
a config that does not say what you think it says stops the build rather than steering it.
