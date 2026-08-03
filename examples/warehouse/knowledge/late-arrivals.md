---
type: Decision
title: Absorb late rows by rerun, not by a wider window
status: draft
description: Widening the capture window would have delayed every day's numbers to accommodate the tail, so the tail is repaired instead — reruns are already idempotent, and the cost lands on the rare day rather than on all of them.
tags: [needs-nothing]
generated: { by: "human:example", at: 2026-08-03T00:00:00Z }
sources:
  - id: pipeline-doc
    resource: ../docs/orders-pipeline.md
    okfm_role: subject
    okfm_captured: { at: 2026-08-03 }
okfm_scope: project
okfm_reason_codes: [late_arriving_fact, backfill_pending]
okfm_relations:
  - { predicate: part_of, target: /knowledge/index.md }
  - { predicate: depends_on, target: /knowledge/orders-contract.md }
---

# Decision

Late rows are repaired by rerunning the affected date. The 05:30 capture window stays where
it is.

# Why

Widening the window to catch the tail would push the 06:00 job later, and the finance extract
at 07:00 is not movable. Every day would pay for the shape of a few days.

Reruns are already idempotent — the pipeline replaces a date's partition rather than appending
— so the repair path existed before the problem was named. Choosing it costs nothing new.

# What would change this

Late arrivals becoming routine rather than exceptional. If the tail stops being a tail, the
window is in the wrong place and no amount of repair fixes that.

# What this cost

A period under repair is not comparable to a period that is settled, and nothing in the data
says which is which. That is what `backfill_pending` is for — it is carried on the affected
records so a reader knows the number is provisional, which the row itself cannot say.
