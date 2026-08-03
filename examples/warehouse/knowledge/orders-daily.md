---
type: Dataset
title: orders_daily
description: One row per order per fulfilment date — not per order, which is the mistake every new query makes because the table name suggests otherwise.
status: draft
tags: [needs-nothing]
generated: { by: "human:example", at: 2026-08-03T00:00:00Z }
sources:
  - id: pipeline-doc
    resource: ../docs/orders-pipeline.md
    okfm_role: implementation
    okfm_captured: { at: 2026-08-03 }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /knowledge/index.md }
  - { predicate: produced_by, target: /docs/orders-pipeline.md }
---

# Grain

**One row per order per fulfilment date.** An order fulfilled in two shipments has two rows.

This is the thing worth writing down. The table is called `orders_daily`, so every query
written against it for the first time assumes one row per order and joins accordingly, then
double-counts split shipments. The schema does not say this and cannot — a column list shows
`order_id` is not unique, but not that the duplication is meaningful rather than a defect.

# What the pipeline doc does not cover

The doc describes *when* the job runs and that reruns are safe. It does not state the grain,
because the grain was never in question for the person who wrote it.

Detail on scheduling and reruns is in the source. Follow it rather than restating it here.
