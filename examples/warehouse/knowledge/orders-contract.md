---
type: Data Contract
title: orders_daily contract
description: Complete by 07:00 UTC for the prior day, and a breach is announced rather than silently absorbed — the announcement is the contract, not the deadline.
status: draft
tags: [needs-nothing]
generated: { by: "human:example", at: 2026-08-03T00:00:00Z }
sources:
  - id: pipeline-doc
    resource: ../docs/orders-pipeline.md
    okfm_role: constraint_source
    okfm_captured: { at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /knowledge/index.md }
  - { predicate: certifies, target: /knowledge/orders-daily.md }
---

# The promise

`orders_daily` is complete for date D by 07:00 UTC on D+1.

# What "complete" means, and why it is not obvious

Complete against the capture *as it stood at 05:30*, not against reality. A row that arrives
at 09:00 was never in scope for that morning's run, and the table is not wrong for lacking
it — it is correct as of a moment that has passed.

This distinction is the whole reason the contract exists in writing. Without it, every late
row reads as a pipeline failure, and the team spends its attention re-litigating a bound that
was met.

# When it breaks

The breach is announced. A missed deadline that nobody is told about is worse than a missed
deadline, because the downstream extract runs against a partial partition and produces a
number that looks finished.
