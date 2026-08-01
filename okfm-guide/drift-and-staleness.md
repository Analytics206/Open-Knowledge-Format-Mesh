---
type: Concept
title: Drift and staleness
description: Two independent ways knowledge goes wrong, and why both are computed.
status: stable
tags: [freshness, drift, derived]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Two different questions

| | Staleness | Drift |
|---|---|---|
| Asks | Has enough time passed that this deserves review? | Has the thing this depends on actually changed? |
| Mechanism | Compare `stale_after` to today | Re-resolve the pointer, compare to `okfm_captured` |
| Cost | Free | One resolution per pointer |
| Catches | Policy that ages out | Schema changes, query edits, superseded concepts |

They are orthogonal. A concept can be fresh by date and drifted in fact, or untouched
by drift and long past its review window. Use both.

Staleness is the baseline's; drift is OKFM's.

# What makes drift possible

Every OKFM pointer records what it saw at the moment it was written:

```yaml
sources:
  - id: churn-sql
    resource: sys://sp3d-db/query/monthly_churn.sql
    okfm_role: implementation
    okfm_captured:
      hash: "sha256:4b1e..."
      at: 2026-07-30
```

That is the entire mechanism. Re-resolve the pointer, hash what comes back, compare.
Edit the query and every rule citing it goes stale — automatically, without anyone
remembering to check.

Because pointers reach into systems and not just files, this works for a database
column, a live query, or a captured API payload, not only a file on disk.

# The rule that surprises people

**Neither flag is ever written into a file.**

A concept stores `okfm_captured`, `verified`, and `stale_after` — objective signals. It
never stores `okfm_stale: true`. The flag is recomputed every time anything reads the
mesh, which is why the same bundle rendered on two different days shows different
badges.

That is correct behaviour, not a bug.

A stored verdict is a stored opinion with an expiry date. `okfm_stale: true` is wrong
the instant somebody fixes the source, and nothing tells you it went wrong. The same
reasoning applies to trust tier, drift, and reconciliation status: all derived, none
stored.

# What happens next

A drifted pointer marks its citing concept stale, and staleness propagates along typed
relations to concepts that depend on it. Those land in a review queue where exactly
three things can happen: re-validate it, supersede it, or acknowledge it and move on.

Acknowledging is a legitimate answer. Silence is not.
