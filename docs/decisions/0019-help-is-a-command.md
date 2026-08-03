---
type: Decision
title: DR-0019 — Nine of eleven commands did not answer --help, and four did their job instead
description: "Asking `okfm config` for help wrote a config file; asking `okfm guard` for help ran the guard. The check that was supposed to catch this probed commands by running them and accepted any exit code it liked, so it reported all eleven as fine."
status: draft
tags: [cli, checks, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0016-documented-commands-must-exist.md }
---

# Context

A rewrite two commits ago replaced a block of `docs/roadmap.md` whose last line was the
*next* section's heading. `### Phase 3 — The credentialed half` disappeared. The roadmap
went on defining Phase 1, Phase 2 and Phase 4, and Phase 3 is referenced twelve times across
the corpus — from the README, the specification, `docs/rationale.md`, and four decision
records.

A reader falling out of Phase 2's exit criteria lands directly on `Scope: sys:// resolvers,
attested computations, reconciliation against a trusted report` and reads Phase 3's
requirements as Phase 2's. Phase 2 was declared met last week. Under that reading it never
can be.

Nothing noticed, because the corpus has two heading systems and only one of them was guarded.

# Decision

**A named ordinal series must be contiguous inside the document that defines it, and a
mention must land on a heading that document gives.** `dev/check_docs.py` has enforced
exactly this for the numbered spine — `## 15.`, `### 7.3`, one home per section, no dangling
`§` — since the specification was split. The rule now covers `### Phase 3` and `## Level 2`
as well. Series names are discovered from the headings rather than listed, for the reason
`check_commands.py` gives: a list would be a second place to keep the same set in sync.

**The scoping is the whole design.** `Level 4` is referenced twenty-two times and has no
heading in the README or the roadmap, because DR-0009 defined it and then folded it into
Level 3 as the credentialed variant. A history of superseded ordinals is precisely what a
decision record is for. A corpus-wide *every ordinal mentioned must have a heading* rule
would report those twenty-two, be right about none of them, and be switched off within a
week. Contiguity inside the defining document reports one failure and it is the real one.

Verified by falsification: removing the heading again produces five failures naming the gap
and each of the four orphaned references.

# The larger finding

Restoring the heading meant re-running the checks, and `dev/check_commands.py` failed with:

> `okfm guard --help` exited 1 — documented, dispatched, and broken

Three claims, none of them true. `guard` is documented, is dispatched, and works. What
happened is that `guard` never handled `--help` at all, so the check's *probe* ran the guard
for real, against the working tree, which held an uncommitted human revalidation. The guard
correctly reported it. The check read exit 1 as "this command is broken".

That check's verdict therefore depended on uncommitted local state: green on a clean CI
checkout, red on the builder's machine whenever a review had happened and not yet been
committed.

**Measured across all eleven commands, nine did not answer `--help`:**

| | |
|---|---|
| `okfm config --help` | wrote an `okfm.json`, exit 0 |
| `okfm check --help` | ran the validator, exit 0 |
| `okfm validate --help` | ran the validator, exit 0 |
| `okfm guard --help` | ran the guard, exit 1 on unrelated uncommitted edits |
| `okfm view --help` | `unknown option: --help`, exit 2 |
| `okfm refresh --help` | `unknown option: --help`, exit 2 |
| `okfm enrich --help` | `unknown option: --help`, exit 2 |
| `okfm enrich-local --help` | printed a configuration message, exit 2 |
| `okfm revalidate --help` | printed a usage error, exit 2 |

Four commands did their entire job in response to a request for *help*, and three refused
the one flag every command-line tool accepts. Only `build` (argparse) and `index` were
right.

So a documentation checker was performing a build, a config write and two validations on
every CI run — and the reason none of this was visible is that the probe accepted **exit 0
or exit 2** as a pass, which is satisfied both by printing help and by doing the work.

**`-h` and `--help` are now answered inside `reject_unknown`**, which already existed in
`okfm_core` for the neighbouring rule, and every command passes its `__doc__`. The module
docstrings were already written as help text and were reachable from nowhere. They are
implicitly allowed there too, so a caller cannot forget to list them and reintroduce this.

**The probe now asserts the specific thing:** `--help` must print that script's own docstring
(or argparse's usage line) and exit 0. Tolerating an exit code cannot tell help from work;
requiring the help text can. The docstring is read by parsing the file, not by importing it —
importing `dropin/` to read `__doc__` would run every module-level statement, which is the
same mistake as probing a command by executing it.

# What this cost to find

**The flag check covered five of eleven commands and printed a number that read like
coverage.** The dispatcher holds two tables in two shapes — `STEPS` is a list of tuples,
`EXTRA` is a dict — and the pattern reading them matched only the tuple form. Six commands
resolved to no script at all. Nothing said so, because a command that resolved to *nothing*
was skipped by the same branch as a command that had nothing to declare, and the summary line
read `1 documented flag(s) match what the script accepts`. It is 4 now.

That is the third time in this project that a check has been found reporting confidently
about work it was not doing — after the vocabulary overlay that reached every family, and the
contamination guard that was a filename list for a file the corpus never contained. The
common shape is a **skip that looks like a pass**. Worth stating as a rule: when a check
declines to examine something, it must say so in its output, because a silent skip and a
successful check produce the same green tick.

# What would change this

If a command ever grows a genuine reason to reject `--help` — none exists today — the
assertion in `check_commands.py` is the place to record the exemption, with the reason, in
the file that would otherwise fail.
