---
type: OKF Member
title: OKFM guide
description: The format, and a working bundle that demonstrates it by being one.
resource: /okfm-guide
status: stable
tags: [level-1, format, documentation]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  owner: "human:analytics206"
  aliases: ["the guide", "level 1"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# Scope

Owns the explanation of what OKFM is and how to write a first concept: the profile, the
admission test, the loop family, attested computation, drift, federation, and removal.

Does not own the specification — that is [`spec/okfm-v0.2.1.md`](../../spec/okfm-v0.2.1.md),
which is a document rather than a bundle. The guide points at it and never restates it.

# Cadence

Slow. A change here means the **format** moved, which affects every adopter. That is the
ownership seam separating this bundle from the others: not size, but blast radius (§12.1).

# Notes

Every concept carries `okfm_scope: guide`, so the guide renders in the viewer and counts
toward nothing — not health statistics, not the injected index, not a benchmark corpus.

Deletable. `rm -rf okfm-guide/` is the whole procedure, and this member concept becomes a
dangling reference — which the registry must tolerate rather than error on, per §6.7 applied
at the mesh level.
