---
type: OKF Member
title: OKFM decision records
description: Why this project is shaped the way it is — the rationale no source file can state.
resource: ../../../docs/decisions
status: stable
tags: [decisions, rationale, loop-family]
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_member:
  answers:
    - why is the project shaped this way
    - why was X rejected
    - what would reverse this decision
    - when does a deferred thing come back
  owner: "human:analytics206"
  aliases: ["decisions", "DRs", "ADRs"]
  agent: null
  sync_policy: pull
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /okfm-decisions/index.md }
---

# Scope

Owns the record of what was decided and why: the alternative rejected, the reasoning, the
re-entry trigger for anything deferred. Each file is a `Decision` of the loop family (§7.5).

Does not own what the decisions describe. A record about the drift cache does not own drift —
[`spec/okfm-v0.2.1.md`](../../../spec/okfm-v0.2.1.md) §8 does, and the record cites it.

# Why this is the mesh's best member

It passes the admission test (§7.7) outright. A decision record says what its sources cannot:
the code shows *what* was built, git shows *when*, and neither shows why one option beat
another or what would reverse the call. That rationale exists in exactly one place, which
§21.1 measured as the shape a bundle actually wins on.

It also serves success measure §20.2 directly — *"Why did we decide X?" answered from the
bundle in one query* — against real content rather than a worked example.

# Cadence

Fast, and append-mostly. Records are added continuously and kept even when superseded. A
change here never affects an adopter, which is precisely the seam separating it from the
guide.

# Provenance, honestly

These concepts were created by `dropin/bootstrap.py`: deterministic extraction, no model.
Every `description` is copied from prose the record already contained, so it can be
unhelpful but never wrong about what the record says.

They are `status: draft` with no `verified` entry, and both facts are accurate rather than
placeholder. Promoting them is a human act (§16), and the first enrichment pass is what the
Level 3 components exist to do.
