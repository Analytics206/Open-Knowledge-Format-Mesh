---
type: Document
title: Config validation
description: "Every consumer ignores keys it does not recognise, so a misspelled key does not fail — it builds the wrong thing quietly. This is the step that says so, and the rules it reads are the same table the web UI's config form is generated from."
status: draft
verified: { by: "human:analytics206", at: 2026-08-03T08:03:33Z }
tags: [needs-nothing]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T00:00:00Z }
sources:
  - id: doc
    resource: ../../docs/okfm-guide/level-2-build/config-validation.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:9cfb8c1a3b0938cef3a5d771d481863170bb8e9577f6a9ff2b0b41b5c305f8d1", at: 2026-08-03 }
  - id: rules
    resource: ../../dropin/config_schema.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:3e8686aa692270b2696cd3ba3f7b1720c156ecdda8986df84e37530eea6cdda3", at: 2026-08-03 }
  - id: implementation
    resource: ../../dropin/check_config.py
    okfm_role: subject
    okfm_captured: { hash: "sha256:21b06d111f307e398b874197c609f9dc92fdf4e8428c5163f4b16d7289174a7b", at: 2026-08-03 }
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
