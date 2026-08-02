# What it is

[`okfm-web-ui.html`](../../../okfm-web-ui.html) — one file, opened with `file://`. No server, no
build step, no network request. It carries a baked index of the mesh: every concept's path,
type, status, trust inputs, relations, and drift state.

# Four pages, one file

Graph, Closure, Health, Config. The **URL hash** decides which — `#graph`, `#closure`,
`#health`, `#config` — so the browser's back button works, a page can be bookmarked, and a
link somebody pastes into a chat opens where they meant. `okfm-web-ui.html#config` opens the
config.

The navigation is links rather than buttons, which is the honest description of what they
are and means no click handler decides anything: the link changes the hash, and the hash
changes the page. An unrecognised hash falls back to the graph rather than showing nothing.

Each page shows only the chrome it uses. Health reads the whole mesh, so filtering it would
be a lie and the filter sidebar is not there; Config is not about concepts at all, so neither
sidebar nor the mesh gauges appear. Giving Health the full width is the reason its four
panels fit side by side instead of stacking in a middle column.

Two bugs were found in doing this, and both had been shipping:

- The selected tab was styled `--paper` on a `--panel` header — a 2% difference, so nothing
  ever looked selected. The active page is now near-black on light, which cannot be missed.
- The graph SVG was never actually hidden. `hidden` on an `<svg>` does nothing when set
  through the `.hidden` property, because `SVGElement` does not implement it — the attribute
  from the markup stayed put for the life of the file, and `#graph { display: block }` beat
  the browser's own `[hidden]` rule anyway. So the graph rendered underneath every other
  view. Views are toggled with `toggleAttribute` now, and one CSS rule makes `[hidden]`
  win everywhere.

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
