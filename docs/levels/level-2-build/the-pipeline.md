# What it runs

```bash
python okfm/okfm.py           # build --apply, refresh, view, check
python okfm/okfm.py --check   # the same four, writing nothing
```

`--check` is what CI runs: the build dry-runs, and drift and the viewer index fail on
mismatch instead of updating. One command, because that is the command the README gives
people — if CI needs a different incantation than the documentation, one of them is wrong.

# It stops at the first failure

Deliberately. A later step reading what an earlier one failed to write reports a second,
misleading problem, and the second problem is the one people chase.

# Why enrichment is not in it

The pipeline is a composite, and a composite's needs set is the **union** of everything it
invokes. Adding a step that needs a model would make the whole pipeline `needs: [model]` and
move it to level 3 — not as a naming convention, but because it would then be unrunnable on a
fork's pull request.

So the level 3 components — the work list, the guard, the human exit — are reachable by name
and are not in the default run. Neither belongs in an unattended one anyway: one prints work
for a person to do, the other checks the result afterwards.

# The cheapest thing this buys

There is exactly one command to remember, and it is the same one in CI, in the README, and on
your machine. Every alternative — a Makefile, four documented invocations, a shell alias —
costs someone a wrong incantation eventually.
