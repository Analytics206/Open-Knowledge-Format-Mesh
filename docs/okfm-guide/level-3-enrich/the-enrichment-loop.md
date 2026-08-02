# The cycle

```bash
python okfm/okfm.py              # 1. build and observe        needs: []
python okfm/okfm.py enrich       # 2. what needs work, and why needs: []
#                                  3. your agent drafts        needs: [model]
python okfm/okfm.py guard        # 4. did it stay in bounds    needs: []
python okfm/okfm.py revalidate <path> --by human:you
#                                  5. you approve              needs: [human]
```

Step 3 is the only one OKFM does not perform. It hands the work list and
[the contract](the-agent-contract.md) to whatever you already use and gets out of the way.

# Why the union rule puts this at level 3

A composite's needs set is the union of everything it invokes. Three of these five steps need
nothing; two need a model and a person. The union is `[model, human]`, so the loop is level 3
even though most of it is arithmetic.

That rule is what stops level numbers drifting into marketing. You cannot describe a workflow
as level 2 because *most* of it is deterministic — the one step that needs a model decides,
because that is the step that will not run on a fork's pull request.

# Why a human is in the loop and cannot be removed

The model's output is a draft. Promoting it to `stable` and adding a `verified` entry are
assertions that somebody checked, and no process can make that assertion truthfully on a
person's behalf.

This is the backfill honesty rule: an unverified concept is honest, a falsely verified one
poisons every trust reading downstream. So the guard blocks a process from writing those
fields at all, and [the human exit](the-human-exit.md) refuses a `process:` actor outright.

# Where it stops

The loop does not run itself. There is no watcher, no schedule, and no automatic invocation
of your agent, because every one of those requires deciding when a model gets to write into
your repository unattended. That is a credentialed-variant question, and it needs a key.
