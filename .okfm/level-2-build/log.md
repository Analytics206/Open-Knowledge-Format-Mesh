---
type: Log
title: Level 2 changelog
description: Append-only history of the deterministic build.
status: stable
generated: { by: "process:okfm-scaffold", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# 2026-08-01 — bundle created

Level 2 became a bundle. Every component it names already existed and had been run against a
scratch project: `docs/architecture/`, `docs/guides/`, `src/`, and `node_modules/`, with no
config. It found both doc directories, skipped the noise, wrote four concepts and two
indexes, and left every source file untouched.

# What the build taught the design

Three rules in [extraction](extraction.md) exist because the corpus broke the previous
version, not because they were designed in:

- Splitting on `## ` headings left the heading text as the first paragraph, which made seven
  descriptions into bare heading names.
- The not-prose filter matched `**`, which silently discarded every paragraph opening with a
  bold lead-in — most of this project's own prose.
- Extracted concepts were landing `status: stable`, contradicting the record that says
  extraction produces drafts.

# The drift bug worth remembering

In-place concepts reported drift on every file. The captured hash had been computed before
frontmatter was added, so a whole-file comparison could never match. The fix was to compare
bodies when the concept and its source are the same file — see
[drift observation](drift-observation.md).

Eleven false positives is the failure mode that matters most here: a drift signal nobody
believes is worse than no drift signal.
