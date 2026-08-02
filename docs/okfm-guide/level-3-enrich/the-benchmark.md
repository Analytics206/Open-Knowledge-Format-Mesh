# The benchmark

Two arms over one corpus: the project with its bundle, and the same project without it. A
fresh agent per question per arm, no shared context, and grading against a claim list with the
arm labels hidden.

It exists because the premise of the whole project — that curated knowledge makes answers
better — is testable, and the one published test of it did **not** come out uniformly in
favour. A bundle can lose a question by summarising a source the agent would otherwise have
read. Standing practice beats faith.

# What is built

The deterministic half, and it runs today:

```bash
python benchmark/run.py --check   # validate the question set and the arms
python benchmark/run.py           # materialise both arms, emit prompts and the key
```

It builds the two arms as real directories, blinds the prompts behind opaque ids, emits a
grading sheet with the arm labels absent, and writes the key. What it does not do is ask a
model anything.

That step used to be blocked on a key. It is not any more — [a local model](a-local-model.md)
runs a model on your own hardware for nothing, which is what makes a first recorded run
reachable at all. What it is blocked on now is a design question rather than a credential:
**a chat model cannot browse a directory**, so something has to choose which files it sees —
and that chooser is not a detail, it is most of the experiment. Pick it badly in favour of the
bundle and the result is arithmetic dressed as evidence.

# The questions are real now

Eight, drawn from things that actually confused somebody working on this project. Each records
its own provenance in a `from` field, so a reader can check the set was not reverse-engineered
from the answers it wanted.

Two are verbatim: *"I excluded a folder and re-ran the build and it still shows"*, and *"if it
costs nothing and needs no key, why isn't it level 2?"* The rest come from design notes written
after something went wrong, and from the objection each rule keeps attracting.

The provenance rule is the point: never draw a question from a bundle's own table of contents,
which flatters the bundle by construction. A question the bundle was written to answer proves
only that somebody wrote an index.

Every question must be answerable from source in **both** arms, because the bundle is meant to
be a shortcut and not the only copy of a fact. That requirement is mechanical rather than
aspirational — each question names the files its answer lives in, and the harness fails if any
of them is missing from the control arm.

# What the harness found about this repository

Three things, all worth keeping:

**The two arms were the same directory.** Bundle paths were resolved with `lstrip("./")`, and
`lstrip` takes a character *set* — so `./.okfm/mesh` came back as `okfm/mesh`, a folder that
does not exist. Nothing matched, no concept was ever removed, and the harness reported
`0 concepts removed` and exited 0. It had been measuring a corpus against itself.

The fix that matters is not the one-character correction. It is that **`--check` now fails when
the control arm is not smaller than the treatment arm** — because a benchmark whose arms are
identical produces a difference of zero, and a difference of zero reads as *curation does not
help* rather than *the harness is broken*. That is the most expensive way to be wrong here, and
nothing was watching for it.

Worth recording that this was the second appearance of the same `lstrip` mistake in this
repository. Fixing it twice is not a fix; asserting the property it was supposed to produce is.

**The decision records cannot be benchmarked.** They are in-place concepts — the record *is*
the concept — so removing the bundle removes the facts, and the control arm would be missing
the knowledge rather than merely missing the shortcut. That measures file deletion, not
curation. The harness detects the condition and says so instead of producing a flattering
number.

**A derivation is a copy.** `okfm-web-ui.html` carries a baked index of the mesh. Leaving it
in the control arm would quietly turn that arm into a second treatment arm. It is removed by
name, and the harness scans what remains for surviving concept prose.

# What gets measured

Claims hit is the headline. Tokens are counted by the harness rather than self-reported, and
measure effort rather than correctness. False statements are counted **separately from
omissions**: an omission is a gap, but a false statement is a knowledge defect and should be
traced back to the concept that caused it.

Answers and the key are committed, so any run can be regraded later under a different rubric.

# An honest negative result is the valuable one

It tells you which knowledge is worth writing down before you have written down the wrong
things at scale. A rising claims-hit gap is evidence that curation is working; a flat one is a
signal to apply the admission test harder.
