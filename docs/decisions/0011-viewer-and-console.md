---
type: Decision
title: DR-0011 — The viewer stays read-only; a console is a separate artifact
description: A web UI at Level 3 or 4 that can edit configuration, and view at minimum.
status: draft
generated: { by: "process:okfm-bootstrap", at: 2026-08-01T00:00:00Z }
sources:
  - id: self
    resource: /0011-viewer-and-console.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:89fbb25f902c59c1...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0011 — The viewer stays read-only; a console is a separate artifact

- **Status:** **deferred** 2026-08-01 — picked up at the end, not before. See the re-entry
  triggers at the foot of this record
- **Date:** 2026-08-01
- **Affects:** spec §14.3, §14.7; depends on [DR-0009](0009-adoption-levels.md), [DR-0008](0008-build-pipeline.md)

## The ask

A web UI at Level 3 or 4 that can edit configuration, and view at minimum.

## The tension

§14.7 is categorical: *"Read-only. Not an editor, not a search index, not a context source.
Agents read the bundle; the viewer is for people."*

That rule is load-bearing for reasons §14.3 spells out — an editor needs bodies loaded, and
a file containing every concept body is the artifact that contaminated a benchmark control
arm (§21.3) and that routes around an owning agent's access control (§12.6).

But the ask is legitimate, and the stronger half of it is not configuration at all.
[DR-0008](0008-build-pipeline.md) created an entire tier of `[human]` components —
`review-and-promote`, `author-relations`, `author-decision` — and gave them **no interface**.
Promoting a draft, adding a `verified` entry, and accepting or rejecting a typed relation are
now first-class steps in the model with nothing but a text editor behind them.

## Decision

**Two artifacts, not one artifact with a mode flag.**

### The viewer — unchanged, Level 1

`okfm-viewer.html`. Opens from `file://`, no server, no build, no writes, no bodies embedded.
Every constraint in §14.3 and §14.7 stands exactly as written.

This is non-negotiable because it *is* Level 1's promise. The moment the viewer can write, it
needs to be served, which needs a runtime, which means Level 1 no longer installs nothing.

### The console — new, Level 3

A served application. It may write, because it is behind a runtime the adopter has already
chosen to install.

| Does | Why it is safe here |
|---|---|
| Edit `okfm.json` | Configuration is not knowledge. §3.14 governs facts, not settings |
| Drive the review queue: `draft` → `stable`, add `verified` | The missing interface for DR-0008's `[human]` tier |
| Accept or reject proposed `okfm_relations` | Answers DR-0008's open question about a review artifact |
| Show drift, staleness, and the observation cache age | The tier-4 side of [DR-0006](0006-drift-cost-and-caching.md) made visible |
| Trigger a rebuild | It is running the same components the CLI runs |

**It reads bodies from the bundle at request time and never embeds them** — the same rule
the viewer already follows (§14.3), for the same three reasons.

**It never becomes a context source.** Agents read the bundle. The console is for people,
exactly as the viewer is.

## Why Level 3 and not Level 4

A console that only drives the review queue needs no model and no key — it is a UI over
DR-0008's `[human]` components. Placing it at Level 3 rather than 4 means the enrichment
lifecycle has a review surface at the level where enrichment first appears, which is where
it is needed. Waiting until Level 4 would ship drafting without a way to approve it.

Configuration editing is likewise level-independent.

## Why not just make the viewer serveable

Because `okfm view --serve` already exists in the design (§14.2 source 1) and does the
read-only half. Adding writes to the same file means one artifact with two security postures
and two threat models, distinguished by how it was launched. That is the shape of a mistake.

Separate files also keep the deletion story clean: an adopter who wants no server deletes the
console and keeps a fully functional viewer.

## Against

**Two UIs is duplicated effort.** Some, but less than it appears — the console can render the
same three views by importing the viewer's rendering, and differs in adding a review queue
and write endpoints. The duplication is in shell and transport, not in the graph.

**A console invites scope creep toward editing concepts.** It does, and the line must be
stated now: **the console edits *metadata decisions*, never *knowledge*.** Promoting a
status, adding a `verified` entry, accepting a relation — all decisions about a concept.
Rewriting a concept body is authoring, and authoring happens in an editor against files,
where git can see it.

## Deferred — 2026-08-01

Not built yet, and deliberately last.

The half of this record that is a *constraint* is already in force: **the viewer stays
read-only**, and §14.3 and §14.7 hold unchanged. That costs nothing to keep and is the part
that protects Level 1.

The half that is a *build* — the console — waits. Nothing depends on it. The review queue it
would serve currently holds 26 concepts, all `draft`, and promoting them is a text editor and
a few minutes. A UI for that is a convenience, and conveniences built before the workflow they
serve is exercised tend to be built for an imagined workflow.

Deferring also keeps a decision open that would otherwise be made by accident: whether the
console is a served application at all, or whether the review gate belongs in the CLI, in an
agent's own interface via `AGENTS.md`, or in a pull request.

### Re-entry triggers

Revisit when **any** of these becomes true:

| Trigger | Why it changes the answer |
|---|---|
| Level 3 enrichment ships and produces drafts at volume | Promoting by hand stops being a few minutes |
| A second person reviews | Two people editing frontmatter by hand will diverge on convention |
| A hosted instance exists ([DR-0010](0010-okfm-self-hosts-as-a-mesh.md)'s remote member) | It needs an interface and an auth answer regardless |
| Configuration outgrows one small file | The editing case, which is currently the weaker half of the ask |

The first is the one to watch, and it arrives in Phase 2.

## Open, when it is picked up

- Does the console write files directly, or shell out to the same CLI components so there is
  exactly one implementation of every mutation? The second is slower and much safer.
- Does it require auth? Single-user local is fine at first; a hosted instance is not.
- Is a served application the right shape at all, or does the review gate belong in the CLI,
  in `AGENTS.md`, or in a pull request?
