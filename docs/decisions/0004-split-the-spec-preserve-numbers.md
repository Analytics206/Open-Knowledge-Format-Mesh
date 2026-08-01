---
type: Decision
title: DR-0004 — Split the spec, preserve section numbers
description: "The unified `okfm-spec-v0.2.1.md` was 1,535 lines carrying four jobs at once: a normative specification, a rationale, a roadmap, and a lab notebook. For a project whose primary constraint is that a…"
status: draft
generated: { by: "process:okfm-bootstrap", at: 2026-08-01T00:00:00Z }
sources:
  - id: self
    resource: /0004-split-the-spec-preserve-numbers.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:e5854f2c400eed7f...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0004 — Split the spec, preserve section numbers

- **Status:** accepted — done in Phase 0
- **Date:** 2026-08-01
- **Affects:** all four documents

## Problem

The unified `okfm-spec-v0.2.1.md` was 1,535 lines carrying four jobs at once: a normative
specification, a rationale, a roadmap, and a lab notebook. For a project whose primary
constraint is that a stranger can pick it up (§13.1), an adopter had to read the
builder's roadmap and proving-ground notes to find out what makes a bundle legal.

It also made §3.10 — *"the spec follows the implementation"* — uncheckable, because there
was no normative text to diff against code.

## Decision

Split four ways:

| Document | Sections |
|---|---|
| `spec/okfm-v0.2.1.md` | 3, 5–10, 12–14, 18, Appendix A |
| `docs/rationale.md` | 0, 1, 2, 22 |
| `docs/roadmap.md` | 4, 11, 15–17, 19, 20 |
| `docs/prior-art.md` | 21 |

**Section numbers are preserved and global across the set.** Numbers were not
reassigned.

## Why numbers were preserved

Renumbering would have required rewriting all 121 cross-references by hand. That is
precisely the class of error the split was partly meant to fix — the original document
had six genuinely broken references, including a §18 whose subsections were numbered
17.1–17.4.

Preserving numbers means every existing reference stays literally correct and only needs
a map to say which file to open. Each document opens with that map, and every gap carries
a one-line pointer stub so a reader who hits one is not left guessing.

The cost is cosmetic: the specification runs §3, §5, §6 … with visible gaps. The map and
the stubs make that legible.

## Verification

A corpus checker confirms, and should run in CI from Phase 1:

- 24 sections, each with **exactly one** real home (stubs do not count as content)
- 121 cross-references, **all resolving** somewhere in the corpus
- every relative markdown link resolves, ignoring fenced example blocks
- subsection numbers match the section containing them

## Consequence

The unified `okfm-spec-v0.2.1.md` was **deleted**, not archived alongside the split.
Keeping it would have violated §3.14 — two copies of a fact means one of them is
silently wrong later — and git history preserves it regardless.
