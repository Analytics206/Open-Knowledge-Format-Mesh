---
type: Decision
title: DR-0012 — Reach is configured, not discovered
description: "A concept is recognised anywhere but read only where the config says — `exclude` drops a folder inside a scan root, `include` adds a tree outside one — because a sweep wide enough to be convenient is wide enough to turn an adopter's templates and vendored docs into concepts on the first run."
status: draft
tags: [discovery, config, adoption]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T00:00:00Z }
sources:
  - id: self
    resource: /0012-reach-is-configured.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:e5b38fd5720e1feeb9dc3d4cec98f23eaad1c442efbec7c68bec3c7441728e38", at: 2026-08-02 }
okfm_scope: project
---
# DR-0012 — Reach is configured, not discovered

- **Status:** accepted 2026-08-01
- **Date:** 2026-08-01
- **Affects:** spec §13.4, §13.5, §21.4

## The gap

§13.5 said a concept is any `.md` with a non-empty `type:`, "wherever it sits in the
project," and that `bundles` merely *narrows a scan*. Read as an instruction to a tool, that
is a project-wide sweep: walk the repository, collect every file already carrying a `type:`.
It was adopted from §21.4's prior art, where a project wiki does exactly that.

Nothing ever built it, and the divergence sat in the spec as a note. What the build does
instead is read the folders it is pointed at and **create** concepts from the documents
there. Those are two different jobs: one collects concepts that already exist, the other
makes them out of documents that are not concepts yet.

## Decision

Two configuration keys, and no sweep.

| | |
|---|---|
| `build.exclude` | drops a folder **inside** a scan root |
| `build.include` | adds a tree **outside** one |

Neither can be said with the other — no exclusion reaches a directory the scan never
entered — which is why there are two rather than one clever list. An `include` path that
resolves inside a root already being scanned is dropped rather than scanned twice; it is
inside, so it is `exclude`'s business. Each included tree is then scanned exactly as the
root is, so `include` adds a path and not a second set of rules.

**Recognition is unchanged.** A `.md` with a non-empty `type:` *is* a concept wherever the
tool encounters one — that is what makes in-place bundles work, and why the build refuses to
mirror a file that is already a concept. What changed is reach: the tool never goes looking.

## Why not the sweep

1. **A first run has to be safe.** A scan wide enough to be convenient picks up an adopter's
   `templates/`, their vendored dependencies' documentation, and any example frontmatter
   sitting in a README — before they have any idea what the tool does. This repository had
   already written itself a note to remember that `templates/` would need a default ignore
   list. A design whose safety depends on a growing list of exceptions is the wrong design.
2. **Two lists are auditable.** The config states the reach in full. A folder is in the mesh
   because somebody said so, and `git blame` says who. A sweep's reach is emergent, and
   the answer to "why is this in my mesh?" becomes a walk of the algorithm.
3. **The goal was incremental adoption, and configuration reaches it anyway.** Nothing has to
   move and there is no migration project: the build reads where the documents already are.
   The sweep was one way to get that property, not the property itself.

## What it costs

A concept in a folder nobody named is invisible. It is legal and portable and does nothing.
The build cannot warn about it either, because finding it in order to warn *is* the sweep.

That cost is stated plainly in §13.5 and in the guide rather than smoothed over, because the
failure is silent and the fix — add one line to `include` — is only obvious to someone who
knows the rule.

## Consequence

§13.5 stops carrying a divergence note and describes what runs. §21.4 records the prior-art
item as adopted *with a change* rather than adopted. `templates/` is safe to ship by
construction instead of by a note asking a future maintainer to remember something.

## Revisit when

Adopters report writing concepts that stayed invisible often enough that naming a folder is
the wrong default. The narrow fix then is a warn-only pass behind a flag — report `.md`
files carrying a `type:` that no scan root reaches — which pays the cost when asked instead
of making the sweep the default.
