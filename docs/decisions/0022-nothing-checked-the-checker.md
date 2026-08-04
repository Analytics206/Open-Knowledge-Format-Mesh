---
type: Decision
title: DR-0022 — The guard that makes the human gate real could be switched off by a plausible typo
description: "`guard --allow verified` parsed the field name as a path, checked nothing, and exited 0 with a reassuring message. Four more defects sat beside it. The one component whose entire job is enforcement was the one nothing enforced."
status: draft
tags: [guard, checks, level-3, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0008-build-pipeline.md }
  - { predicate: depends_on, target: /decisions/0020-the-console-edits-concepts.md }
---

# Context

[DR-0020](0020-the-console-edits-concepts.md) widened the console's edit surface to include
`status` and `okfm_relations` — the tier guard's own protected fields — and answered the
obvious objection like this:

> The guard's purpose is intact: it distinguishes an **agent** writing `verified` from a
> person doing it.

That is a claim about `guard.py`, and nothing checked it. `dev/check_commands.py` asserted
`guard` is a command that answers `--help`. `dev/check_levels.py` asserted it declares
`needs: []`. Neither ran it against a single edit.

A coverage audit of `dropin/` — which modules any check actually imports or invokes — is how
this surfaced. Six modules had nothing behavioural on them at all. `guard.py` was the one
worth opening first, because a guard that does not work is not a missing feature, it is a
false assurance: the whole point of writing it was to stop `[model]` ownership being a rule in
a document, and a broken one puts it back there while looking like it did not.

Five defects. Three come from one root cause — reading `git diff` output as though a line
beginning `+status:` meant a field had changed.

**`guard --allow verified` examined nothing and exited 0.** The space-separated spelling is
how every other command in this project takes a value (`revalidate --by human:you`), so it is
the one a person reaches for. `--allow` was recognised only as `--allow=`, so `verified`
fell through to the path list, scoped the diff to a file that does not exist, and printed

    No markdown changes to check (working tree)

while an agent-written `verified` entry sat in the working tree. This is the worst of the
five: silent, plausible, and the message actively reassures.

**A protected key inside a fenced code block in a *body* was flagged.** The parser tracked
whether it was inside frontmatter and then never consulted the answer — and could not have,
because `--unified=0` emits no context lines, so the `---` boundaries are almost never in the
diff to be seen. Every document here that shows an example concept in a ```` ```yaml ````
block tripped it. `guard.py`'s own docstring names the consequence: *"a guard people learn to
pass is worse than no guard."* It was training people to pass it by firing on documentation.

**A deleted file's fields were blamed on another file.** git writes `+++ /dev/null` for a
deletion, which never matches `+++ b/`, so lines kept being attributed to whichever file came
before. Deleting one concept produced four violations against an innocent neighbour, and the
summary line miscounted.

**`sources` was protected in the documentation and not in the code.** DR-0008's ownership
table gives `sources[].resource` and `okfm_role` to `[human]`, and `guard.py`'s docstring
repeated it — while `PROTECTED` did not contain the key. A pass could repoint a concept at a
different document and nothing said anything.

**A new file was invisible in the default mode.** `git diff` compares the index against the
working tree, and an untracked file is in neither. `CREATED_PROTECTED` exists for exactly one
scenario — a pass that *authors* a concept already carrying `verified`, claiming a review that
did not happen — and in the mode people actually run, that scenario never reached it.

# Decision

**The guard compares frontmatter, not diff text.** For each changed file it takes the
concept's frontmatter before and after and compares it key by key, through
`concept_edit.split_frontmatter` — the same function the console edits through. Two components
disagreeing about what a top-level key is would mean a field the console can write and the
guard cannot see, which is the shape three of these bugs had.

That single change fixes the body-fence false positive (bodies are never read), the deletion
misattribution (files are enumerated explicitly, by status), and the miscount.

**`sources` joins the protected table**, compared with the `okfm_captured` mappings inside it
blinded — those have their own rule and their own build exemption, and comparing them twice
would report every routine rebuild as a repointed source.

**Untracked markdown counts as created**, so the default mode judges a newly-authored concept.

**A pathspec matching nothing tracked is an error, not a clean pass.** This is
[DR-0019](0019-help-is-a-command.md)'s rule — *a skip that looks like a pass* — arriving in the
place where it costs the most.

**`--allow` accepts both spellings and refuses a field this guard does not protect.**
`--allow=verifed` now stops rather than silently waiving nothing while appearing to waive
something.

# What this cost to get right

`dev/check_guard.py` runs sixteen edits against a real git repository in a temporary
directory — a guard is a thing you can only test by giving it a diff — and asserts both the
verdict and that the message names the right field, so a case cannot pass by failing for an
unrelated reason. Against the previous implementation it reports eight problems.

The cases that matter most are the ones asserting a **pass**: prose and tags rewritten with
`generated` restamped, a `yaml` example in a body, a deletion alongside a legitimate edit. A
guard is only as good as its false-positive rate, because every false positive is an argument
for `--allow`, and `--allow` is how the real one gets waved through.

# What would change this

An enrichment pass that runs as a git commit rather than as edits in a working tree. Then the
question stops being *what changed since HEAD* and becomes *what did this actor write*, which
is a better question and one git can answer directly through authorship. Everything here is a
consequence of having to infer an actor from a diff, which the docstring has always said it
cannot do.
