# What you get

Six bundles registered in [`okfm-mesh/`](../../../.okfm/mesh/index.md): the four levels, the
guide, and the decision records. Every file in them is a legal OKF v0.2 concept.

They are a working mesh rather than a demonstration of one. The split is by **change
cadence**, which is a §12.1 ownership criterion: a guide change means the format moved and
every adopter is affected; a decision record is appended weekly and nobody downstream
notices. Splitting by size would have been theatre.

# What makes it worth reading

The decision records are the best of the six, and the reason is the admission test (§7.7). A
decision record says what its sources cannot — the alternative rejected, the reasoning, what
would reverse the call. Code shows *what* was built and git shows *when*; neither shows why.

That shape is not a guess. The one published benchmark of this idea found that a bundle
**loses** questions when its concepts restate their sources, and wins on the questions no
source file can answer. See [prior art](../../../docs/prior-art.md) §21.1.

# The guide is deletable

`rm -rf okfm-guide/` is the entire removal procedure. Every concept in it carries
`okfm_scope: guide`, which the default config excludes — so the guide renders in the viewer
and counts toward nothing: not health statistics, not the injected index, not a benchmark
corpus.

Deleting it leaves a dangling member in the registry, which the mesh treats as a resolvable
condition rather than an error. That is §6.7's tolerance requirement applied one level up,
and it is worth proving on something harmless.

# Honest about its own state

Most concepts here are `status: draft` with no `verified` entry, so the viewer reads them as
unverified. That is accurate rather than broken — deterministic extraction produced them and
nobody has reviewed them. Adding a `verified` line you did not earn is the one thing the
specification forbids outright.
