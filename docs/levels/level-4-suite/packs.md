# Partly built already

The mechanism works today. `vocab_overlays` in the config layers extra predicates, types and
reason codes on top of core, and the validator reads the union. A domain that needs `Incident`
or `data_gap` declares it and the warning goes away.

What does not exist is the rest of a pack: workflows, prompts, resolver configuration, and an
`okfm init --pack <name>` that installs the set.

# Core carries no domain words

Enforced in CI by a grep over the code directories. Bundles and documentation may name
domains freely; code may not. That is what keeps the scaffolding distributable while it is
being developed against specific domains — the usual failure is that the first domain's
vocabulary quietly becomes the framework's vocabulary, and nobody notices until the second
domain arrives.

# A predicate's meaning is a fixed asset

Packs may add predicates. They may not redefine one, and the same holds for reason codes. A
redefined predicate silently changes what every existing edge asserted, retroactively, in
every bundle that used it — which is the one kind of change no validator can catch and no
reader can suspect.

# The awkward part, recorded rather than smoothed over

This component's needs set is `[]`, and the useful half of it runs at level 2. If someone
wants domain vocabulary today, they add an overlay and nothing stops them.

It sits at level 4 because that is where the pack *system* ships — discovery, layering,
installation, and the workflows a pack carries. But the level assignment is about a release,
not about a capability boundary, and that is a weaker reason than the ones behind the other
three levels.
