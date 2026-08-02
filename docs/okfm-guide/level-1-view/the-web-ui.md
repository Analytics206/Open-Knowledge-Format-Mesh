# What it is

[`okfm-web-ui.html`](../../../okfm-web-ui.html) — one file, opened with `file://`. No server, no
build step, no network request. It carries a baked index of the mesh: every concept's path,
type, status, trust inputs, relations, and drift state.

# Why it never contains the prose

The index holds pointers and metadata. It does not hold concept bodies, and that is a
correctness rule rather than a size optimisation: a file containing every concept body is a
second copy of the bundle, and a second copy is the artifact that contaminated a published
benchmark's control arm (§18.3, §21.3). Click a concept and the web UI sends you to the file
on disk.

The index is **baked, not hand-maintained** — `dropin/bake_web_ui.py` regenerates it and CI
fails if the committed copy disagrees. That makes viewer-versus-mesh drift impossible by
construction rather than by discipline.

# What it shows that a file listing cannot

Trust and staleness are **derived at read time** (§3.4), so the web UI computes them from
`generated`, `verified`, and `stale_after` every time it loads. Drift is different: it is
observed during the build and cached, because observing it means reading every source.

Drift renders in three states — `match`, `drifted`, `unknown` — never two. A concept whose
source could not be read is `unknown`, and showing it as fresh would be the one failure this
whole design exists to prevent.

# Read-only about concepts, on purpose

There is no edit affordance for a concept. Concepts are git-tracked markdown and belong to
whatever edits git-tracked markdown in your life. A viewer that could write them would need
to own conflict resolution, permissions, and validation — three problems that already have
better answers.

# The Config tab is the one exception, and it is not one

`okfm.json` is not a concept. It is a settings file with a fixed, small set of keys, no
history worth merging, and a validator — so a form is a straightforwardly better editor than
a text buffer, and none of the three problems above apply.

The tab is the level 2 build's configuration, edited from level 1's page. That is the whole
of the relationship: the page does not run the build, and the build does not need the page.

**It writes nothing on its own.** Saving goes through the browser's own file dialog — written
back in place where the browser allows it, downloaded where it does not — and the build is
run from a terminal. There is no third option that does not mean running a server, and a
server is the thing this file exists without.

**The rules are not written twice.** `dropin/config_schema.py` holds them as data and the
bake embeds that same table in the page, so the form, the live validation, and
`okfm config` in the terminal all read one source. Two lists of what keys exist would agree
right up until somebody added a key to one of them, and the disagreement would be silent —
the page would accept a config the build rejects, which is worse than having no page.

What the page cannot check is whether the paths exist. Opened from `file://` it cannot see
your disk, so it says so and leaves that half to the terminal rather than guessing.
