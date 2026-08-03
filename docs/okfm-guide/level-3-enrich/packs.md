# Built, and standing up a second domain on every CI run

A pack is a directory of YAML. `"pack": "packs/warehouse"` in the config is the whole
installation, and the validator reads core plus the pack as one vocabulary. A domain that
needs `Incident` or `data_gap` declares it and the warning goes away.

`packs/warehouse/` is a real one — three files, no code. `examples/warehouse/` is a project
standing on it, and `dev/check_pack_example.py` builds that project from scratch on every CI
run, checking both that it works and that **removing the pack makes the same mesh fail**. A
pack that changes nothing when removed was decorative.

**The vocabulary is per-family, and that was the defect worth knowing about.** Overlays were
once a flat list of files read into every family at once, so a pack declaring one reason code
also registered that term as a valid type, role and *predicate* — and predicates are the one
vocabulary the validator rejects on, because traversal reads a typed edge as fact. An overlay
is now a directory and the filename inside names the family, which makes it unreachable
rather than fixed.

What does not exist is the rest of a pack: workflows, prompts, resolver configuration, and a
single command that installs the set. Installing one is a copy and a config line, and there
is no invocation for it — naming one here would put a command in the corpus that nothing
answers to.

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

It sits in the credentialed variant because that is where the pack *system* ships — discovery, layering,
installation, and the workflows a pack carries. But the level assignment is about a release,
not about a capability boundary, and that is a weaker reason than the ones behind the other
three levels.
