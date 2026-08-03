---
type: Decision
title: DR-0015 — The tool, the mesh and the config are three things, because upgrading is a thing
description: "The documented install fused tool, config and knowledge into one directory, which works on day one and has no upgrade path on day two — re-running the install nests a silent copy, and deleting first destroys every enriched concept."
status: draft
tags: [distribution, install, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0007-two-layers.md }
---

# Context

§13.7's distribution test — *a stranger reaches a running mesh in under an hour, with only
the README* — was attempted mechanically: run the page's own commands against a fresh
project and see what happens.

The first run was clean. 7 concepts, 3 bundles, valid mesh, no intervention. The failure was
on the second day, and it was invisible from inside this repository.

# What was wrong

The README said:

```bash
cp -r Open-Knowledge-Format-Mesh/dropin my-project/.okfm
```

That puts the tool, the adopter's configuration and the adopter's knowledge in one
directory. `.okfm/` then holds three bundles intermixed alphabetically with fourteen Python
modules, `vocab/`, `references/` and `__pycache__` — and the config, which is the one file
the page tells them to edit, is somewhere in that list.

**There is then no way to replace any one of the three.**

* Re-running the install to upgrade does not upgrade. `cp -r a b` with `b` present nests
  `b/a`, so the adopter gets `.okfm/dropin/` holding the new code while `.okfm/*.py` stays
  old. No error, no output, no upgrade. Verified, not reasoned about.
* Deleting first — the obvious repair — takes the mesh with it. Mirrored concepts rebuild;
  every concept anyone enriched, verified, or hand-authored does not. That is the adopter's
  work, and the documented recovery destroys it.

This repository never met either problem, because it keeps `dropin/` and `.okfm/` apart and
its config at the project root. **The builder's own layout was the safe one and the page
described the other.** That gap is the entire reason §13.7 exists as a criterion.

# Decision

**Three directories, named for what they are.**

| | Holds | Replacing it costs |
|---|---|---|
| `okfm/` | the tool | nothing |
| `.okfm/` | the mesh | your enrichment, not your documents |
| `okfm.json` | your configuration | your configuration |

Upgrading is `rm -rf okfm` and a re-copy. Safe because those are separate, and for no other
reason.

**The synthesized config is written to the project, not to `HERE`.** `find_config` already
looked at the project first, so this writes where it looks. A config already inside a
drop-in still loads; nothing an adopter has today moves.

**Both layouts still work, and the fused one now says so.** `bundle_root` supports either
arrangement deliberately, and an adopter who wants one hidden folder can still have it. What
they could not have before was a warning, and the build prints one when it finds the tool
directory and the bundle root are the same path. Said at the top of the run, because by the
time the problem bites, there are concepts worth losing.

# What this does not settle

**This is not the distribution test.** `dev/check_readme.py` executes the page's commands
and checks that what lands matches what the page says landed. It cannot check the thing
§13.7 is actually about — whether a person who has never seen this project understands what
they are reading. That needs a stranger, and the author is the one person who cannot
substitute for one.

Recording the distinction because the check is the kind that invites being mistaken for the
criterion. A green tick on "the commands run" would otherwise close a phase exit that is
still open.

# Consequences

The check interprets the README's commands rather than shelling out, and **a command form it
does not recognise fails**. A check that skips reports success for the wrong reason, which
this project has paid for more than once. Adding a command to the quickstart now breaks the
check until somebody teaches it that command — the correct amount of friction for a page
whose instructions are load-bearing.

`.okfm/` holding only bundles is now asserted, which is what makes it both deletable and
legible: an adopter opening it finds their own knowledge, not the machinery that wrote it.
