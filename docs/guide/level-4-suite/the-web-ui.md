# Not built

Designed. This concept records why it is a second artifact rather than an upgrade to the
viewer.

# Two artifacts, not one

[The viewer](../level-1-view/the-viewer.md) opens from `file://` with no server, no build, and
no dependencies, and that property is the whole of level 1. Adding write access to it would
require a server, which would take a browser-openable file and turn it into an install.

So the console is separate: served, able to edit configuration, run the loop, and show a run
in progress. The viewer stays read-only and stays a file.

# The commands come out of building it

The CLI is not a separate design exercise. Every action the console performs needs a
programmatic entry point, and those entry points are the commands — `okfm validate`,
`okfm build`, `okfm refresh`, `okfm enrich`. Building the console first means the CLI is a
surface over things that already exist, rather than a guess at what people will want to type.

The alternative order produces a CLI designed against an imagined user and a console that
reimplements it.

# What it must not become

An editor for concepts. Concepts are git-tracked markdown and belong to whatever edits
git-tracked markdown — a console that owned concept editing would need conflict resolution,
permissions, and validation-on-save, three problems with better existing answers.

Configuration, orchestration, and observation. Not content.
