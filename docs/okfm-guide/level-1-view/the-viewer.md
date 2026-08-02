# What it is

[`okfm-viewer.html`](../../../okfm-viewer.html) — one file, opened with `file://`. No server, no
build step, no network request. It carries a baked index of the mesh: every concept's path,
type, status, trust inputs, relations, and drift state.

# Why it never contains the prose

The index holds pointers and metadata. It does not hold concept bodies, and that is a
correctness rule rather than a size optimisation: a file containing every concept body is a
second copy of the bundle, and a second copy is the artifact that contaminated a published
benchmark's control arm (§18.3, §21.3). Click a concept and the viewer sends you to the file
on disk.

The index is **baked, not hand-maintained** — `dropin/bake_viewer.py` regenerates it and CI
fails if the committed copy disagrees. That makes viewer-versus-mesh drift impossible by
construction rather than by discipline.

# What it shows that a file listing cannot

Trust and staleness are **derived at read time** (§3.4), so the viewer computes them from
`generated`, `verified`, and `stale_after` every time it loads. Drift is different: it is
observed during the build and cached, because observing it means reading every source.

Drift renders in three states — `match`, `drifted`, `unknown` — never two. A concept whose
source could not be read is `unknown`, and showing it as fresh would be the one failure this
whole design exists to prevent.

# Read-only, on purpose

There is no edit affordance. Concepts are git-tracked markdown and belong to whatever edits
git-tracked markdown in your life. A viewer that could write would need to own conflict
resolution, permissions, and validation — three problems that already have better answers.
