---
type: Decision
title: DR-0023 — Drift was watching the prose and never the code
description: "A concept pins its document and its implementation. `refresh` read only the first pointer of each concept, so 17 of this mesh's 59 were invisible and 11 of those were drifted — every one of them a concept-to-code pointer. Source entries are read in one place now."
status: draft
tags: [drift, refresh, level-2, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0006-drift-cost-and-caching.md }
  - { predicate: depends_on, target: /decisions/0022-nothing-checked-the-checker.md }
---

# Context

Continuing the audit that produced [DR-0022](0022-nothing-checked-the-checker.md): which
`dropin/` modules does any check actually import or invoke? `refresh.py` was on the list of
those nothing touched, and it is the one that matters most, because drift is what every trust
verdict in this project derives from.

It ran in CI on every pipeline invocation. So it was **executed constantly and checked never**,
which is a distinction worth naming — a component that runs green a hundred times a day looks
tested, and the greenness is reporting that it did not crash.

Reading a concept's source entries had **three implementations**:

| | pairing | result |
|---|---|---|
| `refresh._SOURCE` | continuation group `(?:\n\s+.*)*` | matched any indented line, **including the next `- id:`** |
| `revalidate._SOURCE` | non-greedy `resource` → `okfm_captured` | correct |
| `bake_web_ui._CAPTURED` | non-greedy `resource` → `hash` | correct |

The first entry swallowed every entry after it, and `_RESOURCE.search` then returned the first
resource found inside the lot. **A concept with two sources had exactly one of them observed.**

    59 source pointers exist in this mesh
    42 were observed
    17 were invisible — and 11 of those were drifted

The eleven are the finding. Every one is a concept-to-implementation pointer:

    level-2-build/the-tier-guard.md      → dropin/guard.py
    level-2-build/validation.md          → dropin/check_bundles.py
    level-2-build/mirror-mode.md         → dropin/build.py
    level-3-enrich/the-work-list.md      → dropin/enrich.py
    level-3-enrich/the-agent-contract.md → templates/AGENTS.md
    …

A mirrored concept pins two things: the document it was extracted from, and the code that
document describes. The first pointer is the doc. So drift was watching the **prose** and never
the **code** — and the prose is the half that changes when somebody rewrites a sentence, while
the code is the half that changes when the concept stops being true.

The one that disagreed was the one that *produces* the signal, so `revalidate` was faithfully
repinning captures nothing ever read, and `bake_web_ui` was rendering a page from a cache that
had never been told about half the mesh.

Two smaller defects came with it.

**The viewer and the observer disagreed about `unknown`.** `bake_web_ui.drift_of` returned `0`
— fresh — for a concept whose pointers carry no capture, four lines below its own docstring
saying that defaulting to 0 is *"the stored-opinion failure spec §3.4 exists to prevent."*
`refresh` called the same concept `unknown`. The page a person reads was the generous one.

**The observation cache only ever grew.** 81 of its 137 entries pointed at concepts and
sources that no longer existed.

# Decision

**`okfm_core.source_entries` is the one parser.** `refresh` observes with it, `revalidate`
rewrites through it, `bake_web_ui` renders from it. Each entry carries its own resource, its
own capture, and its own line span, so a caller rewriting one entry cannot reach into another.

**Unknown means unknown in both places.** A concept with *no* source pointers cannot drift, and
`0` is a fact about it — saying `unknown` there would flood the page with a non-question. A
concept with pointers that are *not yet pinned* has something to say and has not said it, which
is `unknown`. That distinction is what the two implementations were papering over from opposite
sides.

**The cache holds what the mesh holds.** Observations for pointers that no longer exist are
dropped on each run, because the viewer bakes its drift state out of that file and a record
nobody is asking about is not evidence of anything.

**`max_age` does not govern a local file, and stops claiming to.** [DR-0006](0006-drift-cost-and-caching.md)
sized it for resolvers that cost a network or database round trip — *"how old an observation may
be before the next build re-observes it"* — and `refresh` never applied it, because hashing a
file on disk costs microseconds and always-current beats maybe-current. That is the right
behaviour and it was being reported as something else: the run printed `max_age file=3600s`
beside the cache path, from a default nobody had configured, as though it were the rule the
cache follows. The knob stays for the credentialed resolvers it was designed for; the line now
says what actually happens.

This is the rule that breaks, stated plainly: **DR-0006's three states are two, for `file`.**
`match`, `drifted`, and an `unknown` that means *cannot resolve* or *not yet pinned* — never
*observed too long ago*, because a file pointer is never observed long ago. The third state
returns when a resolver exists that cannot be re-read for free.

# What this cost to get right

`dev/check_refresh.py` runs against a sandbox mesh with known hashes — the only way to test a
drift detector is to drift something on purpose — and asserts ten properties. Against the
previous implementation it reports four problems.

The assertion that would have caught the original bug on day one is the cheapest one in the
file, and it runs against the real corpus: **the number of `- id:` lines the mesh declares must
equal the number of entries the parser finds.** 59 against 42. No sandbox, no fixture, four
lines.

That is worth remembering. The bug was not subtle and it was not deep; it was invisible because
nothing ever counted.

# What would change this

A resolver that costs something — `sys://` against a live database, `store://` against an
object store. Then `max_age` starts governing, the cache stops being a convenience and becomes
the thing that keeps a build affordable, and `unknown` gets its third meaning back.
