---
type: Index
title: OKFM guide
description: A working OKF bundle that documents OKFM. Delete this folder any time.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
---

# What this is

Two things at once: documentation for OKFM, and a real OKF v0.2 bundle you can open,
read, validate, and copy. Every file here is a legal concept — the guide teaches by
being an example of the thing it describes.

The viewer you are probably reading this in loaded these concepts because no other
mesh was found.

# Start here

- [What OKFM is](what-is-okfm.md) — the shape of the system in one page
- [Your first concept](first-concept.md) — the smallest useful thing to write
- [The admission test](admission-test.md) — what *not* to write down
- [The loop family](loop-family.md) — recording decisions, not just facts
- [Attested computation](attested-computation.md) — numbers that prove themselves
- [Drift and staleness](drift-and-staleness.md) — knowing when knowledge rots
- [Federation](federation.md) — many bundles, many owners
- [Deleting this guide](deleting-this-guide.md) — how, and what happens

# How to read these

Each concept here is deliberately short and points at the specification rather than
restating it. That is not laziness — it is [the admission test](admission-test.md)
applied to the guide itself. A concept whose job is orientation should tell you where
to look and why it matters, then get out of the way.

The specification lives in [`spec/okfm-v0.2.1.md`](../spec/okfm-v0.2.1.md).

# This bundle is scoped

Every file here carries `okfm_scope: guide`, and the default config excludes that
scope. The guide renders in the viewer and counts toward nothing — not health
statistics, not the injected index, not a benchmark corpus, not any context assembled
for an agent. It cannot pollute your mesh, which is why it is safe to leave installed.

# Reserved files

`index.md` is this map. `log.md` is the changelog. Everything else with a `type:` in
its frontmatter is a concept.

# Nothing here is verified yet

These concepts carry `generated` but no `verified` entry, so every trust tier you see
in the viewer reads *unverified*. That is honest rather than broken: nobody has
reviewed them. Adding a `verified` entry you did not earn is the one thing the
specification forbids outright — see the backfill honesty rule in the roadmap.

Reviewing this guide and adding your own `verified` line to each file is a fair first
exercise in the workflow it describes.
