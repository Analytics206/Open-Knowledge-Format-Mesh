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
