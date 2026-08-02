---
type: Decision
title: DR-0006 — Drift is observed at build time, never resolved at read time
description: Trust and staleness are pure functions of data already in hand; drift needs the outside world, and the outside world does not belong on the read path.
status: draft
verified: { by: "human:analytics206", at: 2026-08-01T22:35:38Z }
generated: { by: "claude-opus-5/level3-enrich", at: 2026-08-01T00:00:00Z }
sources:
  - id: self
    resource: /0006-drift-cost-and-caching.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:6fa09958c91c58a9f611cb08ab227ff4b932eafd9840bc59b4a4288fa928a1a1", at: 2026-08-01 }
okfm_scope: project
---
# DR-0006 — Drift is observed at build time, never resolved at read time

- **Status:** accepted 2026-08-01
- **Date:** 2026-08-01
- **Revisions:** r1 proposed a cache with inline resolution for cheap schemes ·
  **r2 nothing resolves at read time; the inline option is gone**
- **Affects:** spec §3.4, §8.3–8.5, §13.4, §14.4, §20.8

## The contradiction

Four statements in the specification could not all be true at once.

| Where | Says |
|---|---|
| §3.4 | Trust tier, staleness, **drift**, and reconciliation are computed at read time, never stored |
| §8.3 | Drift costs one resolution per pointer |
| §8.5 | Every run opens with an index injection, and rule 4 promises zero overhead when absent |
| §14.4 | The web UI computes drift **at render time** |

If drift is derived on every read, and injection is a read at the start of every run, every
run pays one resolution per pointer. For a `file://` pointer that is a stat and a hash. For
`sys://sp3d-db/query/monthly_churn.sql` it is a database round trip, on a credentialed
connection, before the agent has done anything.

§14.4 also requires the web UI to hold store credentials, which routes around §12.6's rule
that the owning agent is the access-control point.

## Decision

**Drift is observed during the build. Nothing resolves it at read time — not the injected
index, not the web UI, not an agent.**

§3.4 was right about three signals and wrong about the fourth. They differ by orders of
magnitude in cost, and the difference is not incidental:

| Signal | Input | Derived when |
|---|---|---|
| Trust tier | `verified[]` in frontmatter | every read — free |
| Staleness | `stale_after` vs. today | every read — a date compare |
| Reconciliation | `okfm_reconciliation.status` | every read — free |
| **Drift** | re-resolve the pointer, compare to `okfm_captured` | **build only** |

The first three are pure functions of data already in hand. The fourth requires the outside
world, and the outside world does not belong on the read path.

§8.5's own worked example already agreed: its index shows `verified · fresh` — trust and
staleness badges, and no drift badge. The design leaned this way; it never said so.

### Caching an observation is not storing a verdict

This is why the decision does not violate §3.4.

A stored verdict is forbidden because it is indistinguishable from a fresh one and carries no
expiry. `okfm_stale: true` is wrong the moment somebody fixes the source, and nothing says so.

An observation is a different kind of thing. *At 14:32 on 2026-08-01 this pointer resolved to
`sha256:4b1e…`* does not become false later. It is the same category as `okfm_captured`,
which the specification already stores without discomfort.

> **The cache stores observations. The verdict stays derived.**

"This concept is stale" is still computed by whoever reads it — from stored `okfm_captured`,
plus the cached observation, plus how old that observation is.

### Three states, never two

A pointer is `match`, `drifted`, or **`unknown`** — never observed, or observed too long ago
to trust.

Two states force a default, and the default is always the same lie: an unobserved pointer
renders as fresh. That is the failure §3.4 exists to prevent, reintroduced through a default
value. `unknown` renders as unknown — in the index, in the web UI, and in CI.

A mesh that has never been built reports every pointer `unknown`. That is correct, and it is
the honest first-run state.

### The cache

`.okfm-cache/` — gitignored, and it stays that way: it is a derivation (§3.14), and a
committed cache of resolved content is the artifact that contaminated a benchmark control arm
in §21.3.

Keyed by **resolved pointer URI, not by concept**. Many concepts cite one query; it is
observed once per build rather than once per citation.

```yaml
"sys://sp3d-db/query/monthly_churn.sql":
  observed: "sha256:4b1e..."
  observed_at: 2026-08-01T14:32:00Z
  resolver: sys/bigquery
```

### Per-scheme budgets

```json
"drift": {
  "cache": ".okfm-cache/",
  "max_age": { "file": "1h", "okf": "24h", "store": "7d", "sys": "24h" }
}
```

`max_age` is how old an observation may be before the next build re-observes it. Past that
age a pointer reports `unknown` rather than its last known state.

There is no `inline` option. An earlier revision proposed letting cheap schemes resolve during
injection on a cold cache; that reintroduces the read path this record exists to close, and
`file://` being cheap today does not make a network filesystem cheap tomorrow.

### Who observes

`okfm refresh` — a build component requiring credentials, `needs: [secrets]` under
[DR-0008](0008-build-pipeline.md). It re-observes every pointer older than `max_age`, writes
the cache, and reports newly-drifted concepts into the review queue.

Runs on a schedule, on demand, or in CI as `okfm refresh --check`, which fails on drift in
`stable` concepts. It is the only component that touches a live source.

The web UI and the injected index read the cache and show observation age beside the state.
Neither holds a credential, and §12.6's access-control boundary holds.

## The payoff

§20.8 makes **drift latency** a success measure: *time from a source change to dependent
concepts flagged stale*.

Under this decision it stops being something to measure after the fact. `max_age` per scheme
is the upper bound on drift latency, set in configuration. The metric and the knob are the
same number, and the measurement becomes a check that builds run at the configured cadence.

## Cost

Six specification edits: §3.4 (separate drift from the read-time signals), §8.3 (name the
cache), §8.4 (the build is the trigger), §8.5 (injection never resolves), §13.4 (the `drift`
config block), §14.4 (the web UI reads the cache and holds no credentials).

None changes a stored field, so no bundle migrates.

## Rejected

**Resolve at read time and accept the latency.** Dead on arrival the first time a `sys://`
pointer sits behind a slow warehouse, and it makes OKFM unsafe to leave enabled by default,
which §8.5 rule 4 exists to guarantee.

**Store `okfm_drifted` in the concept.** What §3.4 forbids, for good reasons.

**One global TTL.** Would be tuned for the slowest scheme, leaving local file drift — the
cheapest and most frequent kind — needlessly stale.

## Open

- Does `okfm_captured` need a per-scheme comparator? A git commit, a schema version, and a
  content hash are not compared the same way, and §8.2 permits all three in the same field.
- What invalidates the cache when a resolver changes? A `sys/bigquery` resolver that alters
  how it normalizes SQL would produce a different hash for unchanged content. The `resolver`
  field makes this detectable; the policy is not decided.
