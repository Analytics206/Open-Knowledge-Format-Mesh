# Two places a concept can live

**Mirror (the default).** Concepts are written into `.okfm/`, each pointing back at the
source file through `resource`. Your markdown is never opened for writing. Deleting the
folder leaves the project exactly as it was.

**In place (`--in-place`).** Frontmatter is added to the source files themselves. The concept
and the document become one file, which is the format at its best — one thing to edit, no
pointer to keep in sync.

# Why the safe one is the default

The first thing a stranger does with a tool they have just pasted into their project is run
it. If that rewrites every markdown file in `docs/`, the tool has spent all its credibility
before producing anything. Mirror mode makes the first run reversible with `rm -rf`, and
in-place is a flag you pass once you have seen what it produces.

This is the same reasoning as `--check` mode existing at all: the reversible operation is the
default and the irreversible one is opt-in.

# What in-place costs

The concept and its source become the same file, so the hash of the source now includes the
frontmatter that describes it. Comparing whole files can then never match, and every concept
reports drift forever.

The fix is to compare bodies when the two are the same file. It is two lines in
[drift observation](drift-observation.md) and it was found by eleven false positives out of
eleven concepts — which is the useful shape of that bug, because a signal that fires on
everything is indistinguishable from a signal that fires on nothing.
