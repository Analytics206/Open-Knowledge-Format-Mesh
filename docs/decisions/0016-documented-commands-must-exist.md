---
type: Decision
title: DR-0016 — The documentation may not name a command that does not exist
description: "`okfm validate` and `okfm index` were documented ten times between them and neither ran; index's config knobs shipped to every adopter reading nothing. The rule is wider than fixing three commands: a phantom name in prose is a promise the corpus cannot keep."
status: draft
tags: [cli, documentation, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0011-viewer-and-console.md }
---

# Context

§13.6 mode 1 promises a plain CLI: `okfm validate`, `okfm index`, `okfm build`, `okfm view`.
Auditing what the corpus tells a reader to type against what the dispatcher answers to found
three names that did not exist.

| Documented | Times | Reality |
|---|---|---|
| `okfm validate` | 6 | the dispatcher knew it as `check` |
| `okfm index` | 4 | existed in no form at all |
| an `init` subcommand | 2 | never existed, and one use could not have worked |

`index` is the one that cost something. `read.index.max_concepts`,
`read.index.priority_types` and `read.exclude_scopes` were synthesized into **every**
adopter's config on their first build and read by nothing. That is the third config key
this project has found in that state, after `pack` and the build's phantom second mode.

A knob that adjusts nothing is worse than a missing feature. The adopter turns it, sees no
change, and concludes the tool is broken somewhere they cannot see — which it was.

`okfm index` was also named in `first-concept.md`, the page a first-time author reads before
writing anything, alongside `okfm validate`. Both printed `unknown command` and exited 2. The
documented first experience of this tool was two failures in a row.

# Decision

**`okfm index` is built.** It prints what an agent would actually be handed: the mesh first
because it is the map, then `priority_types` in the order given, then the rest, cut at
`max_concepts` — and it **says what the budget cut**, with types. An index that silently fits
and one that silently lost a third of the mesh look identical from outside, and the second is
how an agent answers confidently from half a corpus.

**`validate` is a name the dispatcher answers to.** One command with two names is a coin toss
decided by which document you opened, and the name the documentation gave you was the one
that failed.

**The `init` subcommand is not built, and its two uses were wrong in different ways.** One offered to
restore the shipped guide — content the drop-in does not carry, so no command could have done
it; copying from the download is the real answer. The other installed a pack, which is a copy
and a config line that `examples/warehouse/` demonstrates and CI stands up on every run.

**The rule, wider than the three commands:** the documentation may not *name* a command that
does not exist — not in a fence, not in inline code, not in a sentence about what is coming
later. A reader scanning for something to type cannot distinguish a roadmap entry from an
instruction. Describe the capability instead of its invocation.

`dev/check_commands.py` enforces it, reading both the command names out of the corpus and the
dispatch table out of `okfm.py`, so neither side is restated in a third place. The reverse
direction is a note rather than a failure: a command that exists and is undocumented is a gap
in the writing, and there are legitimate ones.

> Restricting the scan to fenced blocks was tried first, to spare a page that mentions a
> future command in prose. It let a real instruction through — `okfm view` is told to readers
> seven times and almost always mid-sentence — and the page it was sparing is better fixed by
> naming the capability instead. The narrower rule was also the wrong one.

# A second thing this surfaced

Adding the first new guide page since the `needs-*` rule landed failed `check_levels`
immediately: a build-written concept has no tag, and extraction cannot read a level claim off
prose. Adding one by hand does not survive, because `_owned()` lets the build rewrite what it
generated.

`build.bundle_tags` closes it — bundle id → tags every concept the build writes there
carries. The claim belongs to the folder, not to any file in it: **every component in a
level-1 or level-2 bundle is `needs-nothing` by definition**, which is the boundary
`check_levels` exists to enforce. `level-3-enrich` is deliberately absent from the map,
because its components differ and a blanket tag there would assert something false.

The general shape is worth keeping: a claim the build cannot derive and a human cannot make
stick has to be declared where the build can read it.

# What would change this

A command that is genuinely planned and genuinely useful to name early. The answer then is a
`⬜` row in the README status table, which is a place the corpus already says what does not
exist yet without putting an invocation in front of somebody.
