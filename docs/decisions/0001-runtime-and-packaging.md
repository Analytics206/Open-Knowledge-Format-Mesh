---
type: Decision
title: DR-0001 — Runtime and packaging for the reference implementation
description: "Python 3.13 and the standard library only, so levels 1 and 2 have no install step — a dependency here would make the first thing a stranger hits a package-resolution problem in a language they may not use."
status: draft
tags: [runtime, packaging, zero-dependency]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0001-runtime-and-packaging.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:1370fb0a7bb871bc...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0001 — Runtime and packaging for the reference implementation

- **Status:** partially settled 2026-08-01 — language and Level 2 dependency rule decided;
  Level 4 packaging still open
- **Date:** 2026-08-01
- **Revisions:** r1 asked what "core" is written in · **r2 rescoped by
  [DR-0007](0007-two-layers.md) and settled for the lower levels**
- **Affects:** spec §13.3, §13.6, §13.7

## Scope

[DR-0007](0007-two-layers.md) splits OKFM in two: a **base** that is a specification, a
guide, and a viewer, and a **reference implementation** that is optional. This record is
about the implementation only.

[DR-0009](0009-adoption-levels.md) then splits the implementation by level, and the levels
have different dependency rules — which is the whole answer.

## Decision

**Python 3.13.**

**`dropin/` (Level 2) is standard library only.** No `requirements.txt`, no install step
beyond having Python. It is a folder you paste into a project and run, and every dependency
added to it is friction on the one level whose promise is that there is none.

**`tools/` (Levels 3–4) may take dependencies freely.** An adopter at those levels has
already chosen to install something.

## Why Level 2 holds the line

The drop-in folder is copied into a stranger's repository and run there. A dependency means
that stranger now resolves a package tree before anything happens, in whatever environment
they happen to have — which is exactly the friction Level 2 exists to remove.

This is not theoretical. The four components in `dropin/` today parse frontmatter for 26
concepts across 3 bundles using about 40 lines of regex and no PyYAML. The subset of YAML
that OKF frontmatter actually uses is small: scalars, lists, one level of nesting, and flow
mappings. Standard library is sufficient, demonstrated rather than assumed.

If writing frontmatter ever needs more than round-tripping, that is the moment to reopen
this — and the answer would be a vendored parser, not a dependency.

## On 3.13

Nothing in `dropin/` currently uses anything newer than Python 3.9. Pinning 3.13 narrows the
audience more than the code requires, and the floor can drop later without changing a line if
adoption ever argues for it. CI runs 3.13 so the supported version is the tested one.
2. **Attesters are Python already.** §6.6 and §9 put deterministic, LLM-free attesters
   in the bundle. A Python core runs them without a bridge.
## Why Python

Attesters are Python by specification (§6.6, §9), so a Python implementation runs them
without a bridge. The viewer is already dependency-free HTML and needs no toolchain of its
own.

Rejected: **Node/TypeScript** (attesters would need a second runtime), **Go** and **Rust**
(best single-binary story, worst attester story, and a compile step between an adopter and a
fix they want to make).

## Still open

Level 4 packaging. `uvx okfm` and `pipx install okfm` are the obvious candidates, and the
name's availability on PyPI is unchecked. Not blocking — Level 4 does not exist yet.
