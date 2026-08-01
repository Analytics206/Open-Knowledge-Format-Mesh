---
type: Runbook
title: Deleting this guide
description: How to remove the guide bundle, and what it affects.
status: stable
tags: [getting-started, housekeeping]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The whole procedure

```bash
rm -rf okfm-guide/
```

Nothing references it. No configuration needs editing. The viewer notices it is gone
and falls back to its empty state, which explains what a concept is and names the two
commands that matter.

To bring it back:

```bash
okfm init --guide
```

# You probably do not need to

Every file in this bundle carries `okfm_scope: guide`, and the default configuration
excludes that scope:

```json
"exclude_scopes": ["guide"]
```

That one line keeps the guide out of health statistics, out of the injected index and
its budget, out of benchmark corpora, and out of any context assembled for an agent.
It renders in the viewer and counts toward nothing.

So the guide is not costing you tokens, skewing your freshness numbers, or competing
with your own concepts for space in an agent's context. Deleting it is tidiness, not
hygiene.

# When you should delete it

- You are vendoring OKFM into a repository where an extra ten markdown files is noise.
- Your organization requires that shipped documentation not sit inside a knowledge
  bundle.
- You have read it and want the empty state back as a clean starting point.

# One thing to check first

If you removed `exclude_scopes` from your config — or set it to `[]` — the guide *is*
in your mesh, and its concepts are competing with yours in the injected index. Either
restore the exclusion or delete the folder. Do not leave it half-in: a mesh where the
sample data and the real data are indistinguishable is a mesh nobody trusts.
