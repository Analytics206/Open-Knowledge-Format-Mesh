---
type: Decision
title: DR-0011 — The web UI stays read-only; a console is a separate artifact
description: "The read-only viewer stays one file that opens from disk and configuration editing goes to a separate served console, because write access would turn a browser-openable file into an install — and the CLI falls out of building the console rather than being designed against an imagined user."
status: draft
verified: { by: "human:analytics206", at: 2026-08-02T02:54:00Z }
tags: [viewer, console, cli]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0011-viewer-and-console.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:304f764f22bfa64ae628a5024102babcefc298a45b925c31bc0aa32570ab2c46", at: 2026-08-01 }
okfm_scope: project
---
# DR-0011 — The web UI stays read-only; a console is a separate artifact

- **Status:** accepted 2026-08-01, **built last** — a full web UI is planned; only the
  timing is deferred
- **Date:** 2026-08-01
- **Affects:** spec §14.3, §14.7; depends on [DR-0009](0009-adoption-levels.md), [DR-0008](0008-build-pipeline.md)

## The ask

An OKFM console app at level 3 that can edit configuration, and view at minimum.

## The tension

§14.7 is categorical: *"Read-only. Not an editor, not a search index, not a context source.
Agents read the bundle; the web UI is for people."*

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

### The web UI — unchanged, Level 1

`okfm-web-ui.html`. Opens from `file://`, no server, no build, no writes, no bodies embedded.
Every constraint in §14.3 and §14.7 stands exactly as written.

This is non-negotiable because it *is* Level 1's promise. The moment the web UI can write, it
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
the web UI already follows (§14.3), for the same three reasons.

**It never becomes a context source.** Agents read the bundle. The console is for people,
exactly as the web UI is.

## Why Level 3 and not Level 4

A console that only drives the review queue needs no model and no key — it is a UI over
DR-0008's `[human]` components. Placing it at Level 3 rather than 4 means the enrichment
lifecycle has a review surface at the level where enrichment first appears, which is where
it is needed. Waiting until Level 4 would ship drafting without a way to approve it.

Configuration editing is likewise level-independent.

## Why not just make the web UI serveable

Because `okfm view --serve` already exists in the design (§14.2 source 1) and does the
read-only half. Adding writes to the same file means one artifact with two security postures
and two threat models, distinguished by how it was launched. That is the shape of a mistake.

Separate files also keep the deletion story clean: an adopter who wants no server deletes the
console and keeps a fully functional viewer.

## Against

**Two UIs is duplicated effort.** Some, but less than it appears — the console can render the
same three views by importing the web UI's rendering, and differs in adding a review queue
and write endpoints. The duplication is in shell and transport, not in the graph.

**A console invites scope creep toward editing concepts.** It does, and the line must be
stated now: **the console edits *metadata decisions*, never *knowledge*.** Promoting a
status, adding a `verified` entry, accepting a relation — all decisions about a concept.
Rewriting a concept body is authoring, and authoring happens in an editor against files,
where git can see it.

## The console is planned; it is built last

A full web UI is the intended end state. This is a sequencing decision, not a doubt about
whether it happens.

**Built last**, because it is the natural consumer of everything below it. The review queue
it serves currently holds 26 concepts and promoting them is a text editor and a few minutes;
by the time Level 3 enrichment is producing drafts at volume, the workflow it should support
will be known rather than guessed.

The half of this record that is a *constraint* is already in force and costs nothing to
hold: **the web UI stays read-only**, §14.3 and §14.7 unchanged.

## The CLI and the UI are one surface

They are not competing interfaces, and the boundary between them does not need deciding in
advance:

> **Every mutation has exactly one implementation. The UI calls it; the CLI exposes it.**

Whether a given command exists because the CLI needed it or because the UI needed it is
immaterial — building the UI is what reveals which commands are actually required, and those
commands are the CLI. That is a better way to arrive at a command surface than designing one
up front and discovering later that half of it is unused.

The practical consequence, and the only rule worth stating: **the console never writes files
directly.** It calls the same components the CLI calls. Slower, and it means a mutation
cannot behave one way in the UI and another on the command line.

## When it is built

- **Auth.** Single-user local needs none. A hosted instance
  ([DR-0010](0010-okfm-self-hosts-as-a-mesh.md)'s remote member) does, and that is the point
  at which it stops being optional.
- **Scope.** The console edits *metadata decisions* — promote a status, add a `verified`
  entry, accept a proposed relation, edit configuration. Rewriting a concept body is
  authoring, and authoring happens against files where git can see it.
