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
model anything — that step needs one, and who holds the key decides whether it is level 3 or
level 4.

# The question set is a placeholder

Three questions, one per shape, chosen to exercise the harness rather than to measure
anything. Real ones get backfilled.

When they are written, the provenance rule applies: draw them from real behaviour, real
business questions, and real past confusion — never from a bundle's own table of contents,
which flatters the bundle by construction. Every question must be answerable from source in
**both** arms, because the bundle is meant to be a shortcut and not the only copy of a fact.

That last requirement is mechanical here rather than aspirational. Each question names the
files its answer lives in, and the harness fails if any of them is missing from the control
arm.

# What the harness found about this repository

Two things, on its first run, both worth keeping:

**The decision records cannot be benchmarked.** They are in-place concepts — the record *is*
the concept — so removing the bundle removes the facts, and the control arm would be missing
the knowledge rather than merely missing the shortcut. That measures file deletion, not
curation. The harness detects the condition and says so instead of producing a flattering
number.

**A derivation is a copy.** `okfm-viewer.html` carries a baked index of the mesh. Leaving it
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
