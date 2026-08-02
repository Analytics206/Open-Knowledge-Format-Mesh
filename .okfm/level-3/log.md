---
type: Log
title: Level 3 changelog
description: Append-only history of the enrichment loop.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
okfm_level: 3
---

# 2026-08-01 — the loop closed end to end

Run on this repository's own drifted concepts: eight drifted, two enriched, guard green, two
re-validated, six drifted remaining. The first two human-verified concepts in the mesh came
out of it.

# The guard was negative-tested before it was trusted

Three edits an agent might plausibly make, all of which it must not:

- promoting a concept from `draft` to `stable`
- adding a `verified` entry
- inventing a `supersedes` relation

All three failed with a stated reason and a non-zero exit. A guard that has only ever been
run against well-behaved input is an untested guard.

# One field had to be taken back out of the protected set

`generated` was protected at first, which is wrong twice over. The record that defines the
tier model has it stamped by whatever produced the content, so a model pass **must** rewrite
it. It is also load-bearing: the extractor decides which descriptions it owns by reading
`generated.by`, so protecting it meant a later refresh could clobber prose a person had
written — which it had already done once, silently.
