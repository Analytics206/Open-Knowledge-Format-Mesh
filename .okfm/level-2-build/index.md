---
type: Index
title: "Level 2 — build"
description: Paste one folder into your project and run one command. A real bundle, with no model anywhere in it.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_level: 2
okfm_needs: []
okfm_relations:
  - { predicate: registered_by, target: /okfm-mesh/index.md }
  - { predicate: depends_on, target: /okfm-level-1/index.md }
---

# What this level is

Copy [`dropin/`](../../dropin/README.md) into your project and run it:

```bash
cp -r okfm/dropin my-project/okfm && cd my-project && python okfm/okfm.py
```

It defaults to where it sits, finds the markdown around it, and writes a bundle. The first
run also writes the config it used, listing what it scanned — most projects have many folders
under `docs/` and want concepts for only some, so pruning is deleting a line.

Python 3.13, standard library only, no install step.

# Components

| Component | Does |
|---|---|
| [The pipeline](the-pipeline.md) | one command that runs the other four in order |
| [Extraction](extraction.md) | turns your markdown into concepts without inventing anything |
| [Mirror mode](mirror-mode.md) | decides where concepts land and whether your files are touched |
| [Drift observation](drift-observation.md) | notices when a source stopped matching its concept |
| [Validation](validation.md) | conformance, the profile rules, and the strip test |
| [The web UI bake](the-web-ui-bake.md) | regenerates the index the level 1 viewer reads |
| [Telemetry](telemetry.md) | one record per run, so a run can be reconstructed later |

# Where the line is

Every component here is `okfm_needs: []`. No network, no secrets, no model — which is what
lets the whole pipeline run on a pull request from a fork, and it is checked rather than
promised.

The property that makes this possible is that **extraction is not drafting**. Copying a
sentence that already exists cannot invent; writing a new one can. Level 2 only ever copies.

# What you get, and what it costs

Descriptions are real sentences from your own files, so they can be unhelpful but never wrong
about what your source says. Everything lands `status: draft` with no `verified` entry,
because nobody has reviewed it. Drift detection works from the first build, because the
captured hashes are real.

Making the unhelpful descriptions good is [level 3](../level-3-enrich/index.md).
