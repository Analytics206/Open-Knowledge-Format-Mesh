# Why this one is cached and trust is not

Trust and staleness are **derived at read time** and never stored, because they are arithmetic
over fields already in the file — cheap, and a stored copy would be a stored opinion with an
expiry date.

Drift is the exception, and the reason is cost: deciding it means reading every source a
concept points at. So it is observed during the build and cached in
`.okfm-cache/observations.json`. The cache holds observations — *what the source looked like
at this moment* — not verdicts. The verdict is still computed from them.

# Three states, never two

`match`, `drifted`, and `unknown`. A source that could not be read is `unknown`, and it stays
`unknown` all the way through the cache, the index, the filters, and the health panel.

Defaulting `unknown` to fresh is the specific failure this design exists to prevent, and it
is easy to reintroduce by accident: the viewer once tested `if (concept.drift)`, which turned
every `null` into a clean bill of health. A truthy check is how two states come back.

# Live pointers are not resolved here

Pointers with a scheme — `sys://`, `store://`, `okf://`, `http://` — are recorded as
unobservable rather than fetched. Resolving them needs network and usually credentials, which
would make this component `needs: [secrets]` and drag the whole pipeline out of level 2.

They become observable when the credentialed resolvers arrive, in a workflow that is gated on
`main` and never runs on a fork's pull request.

# It never clears drift for you

`okfm_captured` is only ever refreshed by a person, through
[the human exit](../level-3-enrich/the-human-exit.md). Refreshing it automatically would erase
the very signal drift exists to carry — the build would quietly agree with whatever the file
now says, which is the same as not checking.

Only `stable` concepts fail `--check`. A draft that drifts is expected; a stable one that
drifts is a claim that has stopped being true.

# How this rule actually gets broken

Not by anyone deciding to break it. By tidiness.

While these bundles were being built, a throwaway script re-stamped every capture after each
round of edits, because a clean drift report looked like a finished job. Every run of it
erased review signal for concepts nobody had reviewed — the precise thing the rule forbids,
performed by a script rather than by the command that refuses to do it.

Two things make that worth writing down rather than quietly fixing.

**The defence already existed and was not used.** [The tier guard](../level-3-enrich/the-tier-guard.md)
has `okfm_captured` in its protected set and fails on exactly this edit, with the reason
attached. It was run after drafting passes and not after scripted ones, which is backwards:
a script has no judgment to exercise, so it is the case that most needs checking.

**Nothing was forcing the tidying.** A drafted concept is *expected* to drift, and no check
fails on it. The whole exercise was cosmetic, and cosmetic pressure on an honesty signal is
how the signal dies — not in one decision, but in a series of small ones nobody would defend
individually.

The rule that survives is narrower and more useful than "do not refresh captures": **any edit
made by a script gets the guard run over it**, because the situations where a person would
notice they were doing something wrong are exactly the situations a script sails through.
