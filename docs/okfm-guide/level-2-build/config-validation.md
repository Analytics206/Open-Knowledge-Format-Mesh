# The failure it exists to stop

Every consumer of a config ignores keys it does not recognise. That is the right behaviour
for forward compatibility and it is a terrible property when you have just typed `exlude`:
nothing fails. The build runs, reads a config missing the key you meant to set, and produces
something subtly wrong. The symptom is not an error message — it is an afternoon spent
comparing what you wrote against what you got.

`okfm config` turns that into one line of output:

```text
  FAIL  build.exlude
        not a key anything reads
        → did you mean `exclude`?
```

It runs first in the pipeline, so a config that does not say what you think it says stops the
build instead of steering it.

# The rules are data, not code

They live in `dropin/config_schema.py` as a table — one row per key, carrying its type, its
default, whether it is required, and one line of help written for a person. Three things read
that table: the terminal validator, the web UI's config form, and the web UI's live
validation.

That is not tidiness. A second copy of "what keys exist" would agree with the first until
somebody added a key to one of them, and the disagreement would be silent in the worst
direction — a form that accepts a config the build rejects.

The help text is the same string in all three places, which means writing it well pays twice.

# What it checks, and what it refuses to guess

| | |
|---|---|
| Unknown keys | with a closest-match suggestion |
| Types, enums, ranges | `mode` must be one of two words; a port is 1–65535 |
| Required keys | `pack` must be present even when null |
| Path shape | no absolute paths, no `..` — a config that only works on your machine is not a config |
| Paths exist | `build.root`, each `bundles` entry, each vocabulary overlay |
| Credential handles | a `stores` profile must name a handle, never hold the secret |
| `build.out` inside `build.root` | the build would read its own output next run |
| `build.include` inside `build.root` | it will be dropped; `exclude` is what controls the inside |
| A bundle id that is not its folder name | two names for one bundle |

Two levels, and the distinction is load-bearing. **Error** means the build would do the wrong
thing. **Warning** means it will do what you asked and you may not have meant it — a path that
does not exist yet is the common case, and failing on it would make the validator useless
during setup.

The credential check is the one with teeth. A `profile` must match a handle prefix —
`env:`, `vault:`, `op:` and a few others — and anything else is an error, with a louder
message when the value contains `://` because that is what a live connection string looks
like. A config file gets committed. A credential does not.

# One problem, one message

An early version reported a path that escaped the project *and* reported that it did not
exist. Both were true; the second was noise, and noise is how a checker teaches people to
skim it. Structural checks now run first and suppress the existence check for anything they
already rejected.

# The half a browser cannot do

The web UI runs every rule above except the ones that touch a filesystem, because a page
opened from `file://` cannot see your disk. It says so in the panel rather than guessing or
staying quiet. That split is why the same table can serve both without either pretending to
be the other.
