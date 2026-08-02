# Generated, not checked

The index inside [`okfm-web-ui.html`](../../../okfm-web-ui.html) is written by this component and
verified by `--check`, which fails if the committed copy disagrees with the mesh.

That ordering matters. The obvious alternative — maintain the index by hand, add a test that
compares it to the bundles — makes disagreement a bug you can have. Generating it makes
disagreement a state that cannot exist, and the two cost about the same to build.

It is the same rule the format applies to itself: knowledge lives in one place and everything
else is a derivation, never edited.

# What goes in and what stays out

In: path, bundle, title, type, status, trust inputs, relations, drift state.

Out: concept bodies. The web UI sends you to the file on disk instead. A single file
containing every concept's prose is a complete second copy of the bundle, and a second copy
contaminates any control arm it is left lying around near — a trap borrowed from a published
benchmark rather than learned here.

# The drift dependency

Drift state comes from the observation cache, which is why this step runs after refresh
rather than beside it. Baking first would publish an index whose drift column is one run
stale — and a freshness indicator that is itself stale is worse than no indicator.
