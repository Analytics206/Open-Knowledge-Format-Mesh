# What it does

```bash
python okfm/okfm.py revalidate <path> --by human:you
python okfm/okfm.py revalidate <path> --by human:you --stable
```

Refreshes `okfm_captured` to what the source says now and adds a `verified` entry. That is
the act that clears drift, and it is the one thing the build must never do on its own.

# Why the build cannot do this for you

Refreshing a capture automatically would make the concept agree with whatever the source now
says — which is indistinguishable from never having checked. The drift signal exists to say
*a person should look at this*, and a process that resolves it has deleted the signal rather
than answered it.

The mechanics are arithmetic. The assertion is not: naming a path and an actor is how you
say you read the source and the concept still holds.

# It refuses a process actor

`--by process:anything` is rejected outright. This command exists so a person can assert
review, and a process actor here would be the backfill dishonesty rule broken while wearing a
command's clothes — the most convincing possible form, because it would appear in the record
as a legitimate re-validation.

# Why a review queue needs an exit at all

The specification gives the queue three: re-validate, supersede, or acknowledge. Only the
first needed a command; the other two are ordinary edits — a `deprecated` status with a
`supersedes` relation, or a `stale_after` pushed further out.

Without a cheap first exit the queue never drains, and a queue that never drains stops being
read. That failure is quiet and total: the signal is still emitted, still correct, and no
longer looked at.
