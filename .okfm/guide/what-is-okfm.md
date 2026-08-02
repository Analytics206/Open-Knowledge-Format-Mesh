---
type: Concept
title: What OKFM is
description: A profile and scaffolding that turns OKF bundles into a self-evolving mesh.
status: stable
tags: [orientation, profile]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
sources:
  - id: spec
    resource: /spec/okfm-v0.2.1.md
    title: "OKFM v0.2.1 specification"
    okfm_role: defines
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Three layers, and only one of them is invented

**OKF** is the format: markdown files with YAML frontmatter, distributed as a git
repository, vendor-neutral, published by the Google Cloud Data Cloud team. It brings
provenance, trust tiers, lifecycle, and attested computation. OKFM does not compete
with it and does not fork it.[^spec]

**OKFM** is a profile on top of that format. Every addition is a frontmatter key
prefixed `okfm_`. Strip every one of them and what remains is still a useful OKF
bundle — that property is called the strip test, and it is enforced in CI rather than
promised in prose.

**The scaffolding** is the part you run: a validator, an index injector, resolvers,
and the workflows that read and write concepts. It ships as its own project so that
someone with no connection to its origins can point it at their own work and have it
function with configuration only.

# What it adds that the baseline does not

Six things, and the list is deliberately short:

| Addition | The question it answers |
|---|---|
| The loop family | Why did we decide that? |
| Federation | Who owns this, and what did they say when we disagreed? |
| Content-based drift | Has the thing this depends on actually changed? |
| Perspectives, declared-vs-observed | Whose definition, and does the code agree with the policy? |
| Typed relations | *How* are these two concepts related? |
| Versioned telemetry | What actually happened on that run? |

Everything else — provenance, trust, lifecycle, staleness dates, attestation — was a
wheel already turning.

# The one-sentence version

A mesh of git-tracked markdown bundles that record why a project believes what it
believes, kept honest by computing trust rather than storing it, and handed to an
agent as a compact index before it starts work.

[^spec]: OKFM v0.2.1 specification
