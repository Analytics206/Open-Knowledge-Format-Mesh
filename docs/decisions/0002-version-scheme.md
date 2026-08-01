---
type: Decision
title: DR-0002 — Version scheme
description: "The **release number on OKFM itself** — the `0.2.1` in `\"okfm\": \"0.2.1\"` — in the same sense a library is at `v1.4.2`."
status: draft
generated: { by: "process:okfm-bootstrap", at: 2026-08-01T00:00:00Z }
sources:
  - id: self
    resource: /0002-version-scheme.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:8eee7efd10063864...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0002 — Version scheme

- **Status:** **deferred** — reviewed 2026-08-01, current scheme kept (see Resolution)
- **Date:** 2026-08-01
- **Affects:** spec versioning policy, `okfm.json`, every document masthead

## What this is about

The **release number on OKFM itself** — the `0.2.1` in `"okfm": "0.2.1"` — in the same
sense a library is at `v1.4.2`.

This record has nothing to do with tracking changes to files, drift, staleness, or
refresh. Those are §8, they are specified, and they work by storing `okfm_captured` on
each pointer and re-resolving it later. See [DR-0006](0006-drift-cost-and-caching.md)
for what *is* still open there.

## Current scheme

`<okf-major>.<okf-minor>.<okfm-revision>` — the first two numbers name the OKF baseline,
the third is OKFM's revision against it. `v0.2.1` is the first OKFM revision targeting
OKF v0.2; `v0.3.0` would retarget to OKF v0.3.

Its stated benefit is real: a reader never has to ask which OKF version a release speaks.

## The problem

Two things, and the second is the serious one.

**It looks like semver to every tool that will parse it.** pip, PyPI, GitHub releases,
Dependabot, and any adopter's lockfile will read `0.2.1` as major 0, minor 2, patch 1.
Under that reading, `0.2.1 → 0.3.0` signals a routine minor bump, when it actually means
*the entire baseline moved*. §13.7 makes OKFM a distributable package; the moment it is
installable, the string is machine-read.

**OKFM cannot signal its own breaking changes.** Every number is spoken for. If
`okfm_relations` changes shape at `0.2.5`, adopters get no signal at all — a patch bump
by every convention that exists. §0.1 already concedes that baseline churn is certain and
that migration will be needed; the version scheme is exactly where that should surface.

## Proposal

Split the two facts into two fields, since they are two facts.

```json
{
  "okfm": "1.0.0",
  "okf_baseline": "0.2"
}
```

- `okfm` is ordinary semver over **OKFM's own contract**: the `okfm_` keys, the config
  schema, the CLI surface, the vocabularies.
- `okf_baseline` names the OKF version targeted. A baseline retarget is a major bump when
  it breaks adopters and a minor one when it does not — which is now expressible.

Documents keep a masthead stating both, so §0.1's readability goal survives:

> **OKFM 1.0.0** — targets Open Knowledge Format v0.2

## Cost

Renames the spec file, the mastheads, and the `okfm` key in every config. Cheap now, and
it grows more expensive with every published artifact. This is the last comfortable
moment to change it.

## Counter-argument worth weighing

If OKFM never publishes to a package index, no tool ever parses the string, and the
current scheme's readability wins outright. §13.1 says it *will* publish — but that is a
goal, not a fact, and the counter-argument is only wrong once someone runs
`pipx install okfm`.

## Resolution — 2026-08-01

**Keep `v0.2.1`. Deferred, not rejected.**

The steward's reasoning, and it holds: the version is deliberately pinning to OKF v0.2,
the number is not expected to move for some time, and there is exactly one user until the
project is ready. Every cost in the analysis above is a *publication* cost — pip reading
the string, Dependabot misreading a bump, an adopter's lockfile. None of those exist yet,
and the readability benefit is being collected today.

The cost of switching later is also bounded and known: rename four document mastheads,
one `okfm` key in each config, and one spec section. That is an hour, and it does not
grow while the project has a single user.

### Re-entry trigger

Following the §17 parking-lot pattern. Revisit when **any** of these becomes true:

| Trigger | Why it changes the answer |
|---|---|
| OKFM publishes to a package index | The string becomes machine-read; semver semantics start applying whether intended or not |
| A second person adopts it | Someone else now has to reason about what a bump means to their bundles |
| An `okfm_` key changes shape or is removed | The first genuinely breaking change with no way to signal it |

The third is the one to watch. It can arrive quietly during Phase 1 while the profile
keys are still settling, and it is the case the current scheme cannot express at all.
If it happens before publication, that is the cheap moment to switch.
