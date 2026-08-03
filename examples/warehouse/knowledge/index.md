---
type: Index
title: Warehouse knowledge
description: Hand-authored concepts using the warehouse pack's vocabulary — an in-place bundle, so these files are the concepts.
status: draft
generated: { by: "human:example", at: 2026-08-03T00:00:00Z }
okfm_scope: project
---

# Warehouse knowledge

An **in-place** bundle: these files carry frontmatter, so they *are* the concepts. Nothing
mirrors them and nothing generated them. That is Level 1 — the format with no tooling — and
it is why this folder is registered by path in `okfm.json` rather than produced by the build.

| Concept | Type | What it says that its sources cannot |
|---|---|---|
| [orders-daily](orders-daily.md) | `Dataset` | which pipeline owns the table, and what its grain actually is |
| [orders-contract](orders-contract.md) | `Data Contract` | what the producer promises, and what happens when the promise breaks |
| [late-arrivals](late-arrivals.md) | `Decision` | why late rows are absorbed by rerun rather than by a wider window |

Every `type` here and every predicate on these concepts comes from the warehouse pack. Remove
`"pack"` from `okfm.json` and validation fails — which is the point of the example.
