# The path most people will actually take

Clone the repository, open it in whatever coding agent you already use, and say *read this
and build one for my project's `docs/` folder*. No component of OKFM is involved. It works
because the format is markdown a model already reads well, and because the guide and the
specification are in the repository you just handed it.

This is worth naming as a level 1 component rather than leaving it as a footnote, because it
is the cheapest useful thing anyone can do with the project and it is invisible in a feature
list.

# Why this does not make it level 3

`okfm_needs` records what **OKFM** requires to deliver a component, not what you brought with
you. Here OKFM supplies files; your agent reads them; the model is yours, running in a tool
you were already paying for.

[Level 3](../../../.okfm/level-3/index.md) is different in kind. There OKFM ships a workflow that
does not terminate without a model — the enrichment loop has a step no arithmetic can
perform. That is OKFM requiring a model, and it is why the level boundary sits exactly on the
`model` line and can be checked mechanically.

Without that distinction the ladder collapses. Anyone can attach an agent to anything at any
level, which is true and which would make every level level 3.

# What you give up

Whatever your agent builds is a one-off. It will not have the drift hashes, the tier guard,
or the validation pass, so nothing will tell you later that a concept has stopped matching
its source. That is what [level 2](../../../.okfm/level-2/index.md) adds, and it is one folder and
one command.

# What to hand it

The specification, [`spec/okfm-v0.2.1.md`](../../../spec/okfm-v0.2.1.md), is the normative
document — what makes a bundle legal. The [guide](../../../.okfm/guide/index.md) is the short
version. If you want an agent to *maintain* a bundle rather than create one,
[`templates/AGENTS.md`](../../../templates/AGENTS.md) is the contract, and that is level 3.
