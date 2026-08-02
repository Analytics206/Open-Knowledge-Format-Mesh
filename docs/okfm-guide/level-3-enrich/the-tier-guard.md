# What it checks

```bash
python okfm/okfm.py guard
python okfm/okfm.py guard --allow=status,verified   # you edited those, on purpose
```

It reads `git diff` over markdown and fails if a protected field changed, naming the field
and the reason. It also fails if `generated` did *not* change, because content that was
rewritten without a new provenance stamp is content whose provenance is now wrong.

# The protected set, and the one field deliberately outside it

Protected: `verified`, `okfm_relations`, `status`, `type`, `title`, `okfm_captured`. Each is
a place where trust, traversal, or the drift signal would be silently corrupted.

`generated` is **not** protected, and getting that wrong caused a real failure. A model pass
must rewrite it — the record that defines the tier model has it stamped by whatever produced
the content. It is also how the extractor decides which descriptions it owns, so protecting
it meant a refresh could overwrite prose a person had written, which is exactly what happened
before the mistake was traced.

The lesson generalises: a protected-field list is a claim about who owns what, and an
incorrect entry is not a harmless extra safeguard.

# Why after, not during

The guard runs on the result. It does not sandbox the agent, intercept writes, or hold a
lock, because none of those are available to a process that is handed a repository after the
fact — and a check that runs afterwards on a diff is both simpler and harder to circumvent by
accident.

`--allow` exists because a person editing their own bundle is not a violation, and a guard
with no legitimate override gets disabled instead of used.

# It needs nothing, and it is still level 3

Reading a diff is arithmetic. But there is nothing to guard until something has drafted, so
the guard has no reason to exist at level 2 — the same reasoning that places
[the work list](the-work-list.md) here.

# Scope it to the pass you are checking

```bash
python okfm/okfm.py guard .okfm/level-3-enrich/    # only what the pass touched
```

Without a path the diff is *everything uncommitted*, which is right when an enrichment pass is
the only thing in flight and wrong the moment it is not. Run it after a pass that landed
alongside a rename or a restructure and it reports the restructure's title changes as
violations — true, unhelpful, and indistinguishable from a real one.

That failure mode matters more than it looks. A guard that fires on unrelated edits is a guard
people learn to clear with `--allow`, and `--allow` used reflexively is the same as no guard
at all. Naming paths costs nothing and keeps the signal worth reading.

This was found by running it in the wrong order: enrichment on top of a half-finished rename,
thirteen flagged fields, and no way to tell which four mattered.
