# What it checks

```bash
python okfm/okfm.py guard
python okfm/okfm.py guard --allow=status,verified   # you edited those, on purpose
```

It reads `git diff` over markdown and fails if a protected field changed, naming the field
and the reason. It also fails when a field a `[model]` pass *owns* changed and `generated` did
not — content rewritten without a new provenance stamp is content whose provenance is now
wrong, and the next extraction refresh will overwrite it for exactly that reason.

That second rule was written down here, and named in the code, long before anything checked
it. It is checked now. A rule stated in three places and enforced in none is the shape most
guarantees rot into, and it took writing a component that had to obey it to notice.

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

# A new file is judged differently

On a file that did not exist a moment ago, *every* field is an addition, so the protected list
would report all of them — four failures every time somebody writes a decision record, none of
them real. So a created file is checked against a shorter list: `verified`, and a `status` that
is anything but `draft`.

That is not a relaxation, it is the actual rule. `type` and `title` and `okfm_captured` on a
new file are authorship — there is no prior value to overwrite and no drift signal to erase.
`verified` and a promoted `status` are different in kind: they are the human gate, and a
concept that arrives already carrying them claims a review that did not happen.

The same reasoning as scoping, below. A guard that fires on the normal case teaches people to
run it with `--allow`, and at that point it has stopped being a guard.

# One exemption, exactly one key wide

A rebuild re-pins `okfm_captured` on every concept whose source moved. That is the build doing
its job, not a pass overreaching — so on a file the build still owns, `okfm_captured` alone is
not counted, and the run says how many it passed over.

The exemption stops there, and the narrowness is the point. `verified`, `status`, `title`,
`type` and `okfm_relations` are checked on build output exactly as anywhere else, because a
whole-file skip would let a `verified` entry added to a build-stamped concept sail through —
the single thing this tool exists to catch. Ownership is read the same way the build reads it,
including that a concept carrying `verified` stops being the build's whatever its stamp says.

What it cannot do is tell a rebuilt description from a drafted one; on a build-owned concept
those are the same bytes. Scoping to the pass is the answer to that, not a cleverer heuristic.

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
