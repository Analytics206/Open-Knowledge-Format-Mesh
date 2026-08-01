---
type: Decision
title: DR-0006 — What drift costs, and where the answer is cached
description: If drift is derived on every read, and injection is a read that happens at the start of every run, then every run pays one resolution per pointer in the mesh. For a `file://` pointer that is a stat…
status: draft
generated: { by: "process:okfm-bootstrap", at: 2026-08-01T00:00:00Z }
sources:
  - id: self
    resource: /0006-drift-cost-and-caching.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:6702ebe5c8c720ce...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0006 — What drift costs, and where the answer is cached

- **Status:** proposed — needs a call before the resolvers are built in Phase 2
- **Date:** 2026-08-01
- **Affects:** spec §3.4, §8.3, §8.4, §8.5, §13.4, §14.4, §20.8

## The contradiction

Four statements in the specification cannot all be true at once:

| Where | Says |
|---|---|
| §3.4 | Trust tier, staleness, **drift**, and reconciliation status are computed at read time, never stored |
| §8.3 | Drift costs one resolution per pointer |
| §8.5 | Every run opens with an index injection, and rule 4 promises **zero overhead when absent** |
| §14.4 | The viewer computes drift **at render time** |

If drift is derived on every read, and injection is a read that happens at the start of
every run, then every run pays one resolution per pointer in the mesh. For a `file://`
pointer that is a stat and a hash. For `sys://sp3d-db/query/monthly_churn.sql` it is a
database round trip, on a credentialed connection, before the agent has done anything.

Injection latency then scales with mesh size times pointer count, and "zero overhead" is
only true for a mesh with no concepts at all.

§14.4 has a second problem independent of cost: a viewer that resolves `sys://` pointers
needs live store credentials. §12.6 says the owning agent is the access-control point, and
a flat HTML file holding warehouse credentials routes around it entirely.

## The distinction the spec is missing

§3.4 lists four derived signals as though they cost the same. They do not — two are pure
functions of data already in hand, and one requires the outside world:

| Signal | Input | Cost | Derive when |
|---|---|---|---|
| Trust tier | `verified[]` in frontmatter | free — already parsed | every read |
| Staleness | `stale_after` vs. today | free — a date compare | every read |
| Reconciliation | `okfm_reconciliation.status` | free | every read |
| **Drift** | re-resolve pointer, compare to `okfm_captured` | **I/O per pointer** | refresh |

§3.4 is correct for the first three and wrong for the fourth.

Notably §8.5's own worked example already agrees: its index shows `verified · fresh` and
`unverified · stale` — trust and staleness badges, and **no drift badge**. The design
already leans this way. It just never says so.

## Proposal

### 1. Caching an observation is not storing a verdict

This is the crux, and it is why the proposal does not violate §3.4.

§3.4 forbids stored verdicts because a stored verdict is indistinguishable from a fresh
one and carries no expiry — `okfm_stale: true` is wrong the moment someone fixes the
source, and nothing says so.

An observation is a different kind of thing. *"At 14:32 on 2026-08-01 this pointer
resolved to `sha256:4b1e…`"* does not become false later. It is the same category as
`okfm_captured`, which the specification already stores without embarrassment.

> **The cache stores observations. The verdict stays derived.**

"This concept is stale" is still computed at read time, from stored `okfm_captured`, plus
the cached observation, plus how old that observation is.

### 2. Three states, never two

A pointer is `match`, `drifted`, or **`unknown`** — never observed, or observed too long
ago to trust.

Two states force a lie, and it is always the same lie: an unobserved pointer gets rendered
as fresh. That is precisely the stored-opinion failure mode §3.4 exists to prevent,
reintroduced through a default. Unknown renders as unknown, in the index, in the viewer,
and in CI.

### 3. The cache

`.okfm-cache/` — already gitignored, which was the right instinct with no rule behind it.
It must stay gitignored: it is a derivation (§3.14), and a committed cache of resolved
content is exactly the artifact that contaminated the benchmark control arm in §21.3.

Keyed by **resolved pointer URI, not by concept** — many concepts cite one query, and it
should be resolved once per refresh, not once per citation.

```yaml
"sys://sp3d-db/query/monthly_churn.sql":
  observed: "sha256:4b1e..."
  observed_at: 2026-08-01T14:32:00Z
  resolver: sys/bigquery
```

### 4. Per-scheme budgets in config

Costs differ by two orders of magnitude, so one TTL cannot serve them all:

```json
"drift": {
  "cache": ".okfm-cache/",
  "max_age": { "file": "1h", "okf": "24h", "store": "7d", "sys": "24h" },
  "inline": ["file"],
  "on_unknown": "report"
}
```

- **`max_age`** — an observation older than this is `unknown` until re-observed.
- **`inline`** — schemes cheap enough to resolve during injection on a cold cache.
  Everything else returns `unknown` rather than blocking the agent.
- Injection **never** blocks on a network or database resolution. Ever.

### 5. `okfm refresh` becomes the only thing that resolves

The §8.4 workflow, with a defined trigger and cost model: re-resolve every pointer whose
observation is older than `max_age`, write the cache, report newly-drifted concepts, and
propagate along typed relations into the review queue.

Runs on a schedule, on demand, or in CI as `okfm refresh --check`, which fails on drift in
`stable` concepts.

### 6. The viewer reads the cache

§14.4 changes from *resolve at render time* to *derive from the cache at render time*,
displaying observation age alongside. The viewer never holds a store credential, and
§12.6's access-control boundary holds.

## The payoff nobody has noticed yet

§20.8 makes **drift latency** a success measure: *"time from a source change to dependent
concepts flagged stale."*

Under this proposal that stops being something to measure after the fact. `max_age` per
scheme **is** the upper bound on drift latency, set in config. The metric and the knob are
the same number, and the measurement becomes a check that refreshes are actually running
at the configured cadence rather than an open question.

## Cost

Six specification edits: §3.4 (split the four signals by cost), §8.3 (state the cache),
§8.4 (name the trigger), §8.5 (say injection never blocks), §13.4 (the `drift` config
block), §14.4 (viewer reads cache, holds no credentials).

None of them changes a stored field, so no bundle migrates.

## Rejected

**Resolve everything at injection and accept the latency.** Honest, and dead on arrival
the first time a `sys://` pointer sits behind a slow warehouse. It also makes OKFM unsafe
to leave enabled by default, which §8.5 rule 4 exists to guarantee.

**Store `okfm_drifted` in the concept.** The thing §3.4 forbids, for good reasons.

**One global TTL.** Would be tuned for the slowest scheme, making local file drift — the
cheapest and most frequent kind — needlessly stale.

## Open

- Does `okfm_captured` need a scheme-specific comparator? A git commit, a schema version,
  and a content hash are not compared the same way, and §8.2 already permits all three in
  the same field.
- What invalidates the cache on a resolver change? A `sys/bigquery` resolver that changes
  how it normalizes SQL would silently produce a different hash for unchanged content.
  The `resolver` field is recorded above so this is *detectable*; the policy is not decided.
