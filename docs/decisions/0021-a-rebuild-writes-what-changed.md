---
type: Decision
title: DR-0021 — A rebuild that finds nothing new writes nothing
description: "The build stamped today's date into every concept it owned, so the first run on any new day rewrote the whole mesh whether or not a source had changed. `generated.at` now means when the content was generated, which is what the specification always said it meant."
status: draft
tags: [build, drift, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0006-drift-cost-and-caching.md }
---

# Context

Found by running the pipeline for real rather than with `--check`, which is the only way it
shows: seven concepts came back modified, and the diffs were entirely

    -generated: { by: "process:okfm-build", at: 2026-08-03T00:00:00Z }
    +generated: { by: "process:okfm-build", at: 2026-08-04T00:00:00Z }
    -    okfm_captured: { hash: "sha256:8b5a8e…", at: 2026-08-03 }
    +    okfm_captured: { hash: "sha256:8b5a8e…", at: 2026-08-04 }

Same hash. Same source, untouched for days. The date had rolled over in UTC, and the stamp is
`datetime.now(timezone.utc)` truncated to the day, so every concept the build still owned was
restated.

Seven is the misleading number. `_owned` stops the build touching anything carrying a
`verified:` entry, so in this repository most concepts are protected by having been reviewed.
**In a new adopter's project nothing is verified yet**, so the build owns all of it and the
first run on each new day is a whole-mesh diff of timestamps. The person best placed to be
confused by that is the person with the least context for it.

It also lands in the wrong place. `.okfm/` is where drift is supposed to be legible; a daily
rewrite of every file in it is noise laid directly over the signal.

# Decision

**A generated file is written only when its content changed.** `_put` compares what the build
would write against what is on disk, with the two `at:` stamps blinded and **the hash left
visible**, and skips the write when they agree. One helper, used by all four write sites —
mirrored concepts, bundle indexes, mesh member concepts, the mesh index.

This is not a new rule so much as the specification's existing one, finally observed. §6.3:

> `generated: { by, at }` — how **current content** was produced.

A concept whose bytes are identical did not have its current content produced today. It was
*checked* today, found unchanged, and left alone — and the honest record of that is the date
it actually was generated. The reading being replaced treated `generated.at` as *when the
build last ran*, which is a fact about the tool rather than about the concept, and is already
recorded properly in `references/telemetry/runs/`.

`okfm_captured.at` follows for the same reason: it is the date the pinned hash was observed,
and re-observing a value that has not changed does not create a new pin. Note the asymmetry
with [DR-0006](0006-drift-cost-and-caching.md) — this cannot mask drift, because drift
*is* the hash changing, and a changed hash always writes.

# What this cost to get right

**The obvious test for this is vacuous, and it took a moment to see why.** Build twice, diff,
assert nothing changed — which passes whether or not the bug exists, because two runs a second
apart compute the same stamp. It would have been a green tick reporting on a property it never
examined, which is the shape [DR-0019](0019-help-is-a-command.md) named: a skip and a pass look
identical from outside.

`dev/check_rebuild.py` therefore **backdates the built mesh between the two runs** — the same
thing a calendar does overnight — and only then asserts the second build is a no-op.

**The negative half is the one that keeps this honest.** A comparison that skips too eagerly is
a build that quietly stops updating concepts whose sources really did change, and that failure
is invisible: everything looks fine, and the mesh is describing a document that no longer says
what it says. So the check also edits a source and asserts that concept **is** rewritten, with
a fresh stamp, and that nothing else is. Both directions were falsified by breaking the rule
each way and confirming the check names the right one.

# What would change this

A reason to know when the build last *considered* a concept, as distinct from when it last
wrote one. That is a genuine question and this decision gives up the ability to answer it from
the concept itself — deliberately, because the run log already answers it and a field that
changes daily on every file is an expensive place to keep an answer nobody was asking for.
