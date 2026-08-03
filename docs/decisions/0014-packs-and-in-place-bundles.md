---
type: Decision
title: DR-0014 — A pack is a directory, and in-place bundles are authored not built
description: "Vocabulary overlays become directories so a pack's reason code can no longer become a legal predicate; `pack` becomes a path because a bare name needs a search order; and `--in-place` is removed rather than implemented, because a build that edits your documents cannot also promise it never touches them."
status: draft
tags: [packs, vocabulary, build, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0007-two-layers.md }
---

# Context

Phase 2's exit is *a toy second domain stood up via pack + config with zero core edits*. It
was never attempted, and attempting it is what produced this record: four defects, none of
them visible from inside this repository, three of which had shipped.

The claim CI had been checking since Phase 1 — no domain word appears in `dropin/` — is a
much smaller claim than the one the project rests on. Grepping for `arxiv` proves the code
carries no *existing* domain's words. It says nothing about whether a **new** domain can be
added without touching core. Only standing one up answers that.

# Decision

**1. A vocabulary overlay is a directory, and the filename inside it names the family.**

Overlays were a flat list of file paths, appended to every family's read. One pack file
declaring one reason code registered that term as a valid reason code, type, role **and
predicate**. Measured, not theorised — `dev/check_vocab.py` fails on the old code.

The predicate is the damage. An unknown type warns and an unknown reason code warns; an
unknown predicate is *rejected*, because impact analysis and drift propagation read a typed
edge as fact. So the mechanism for adding domain words was also the mechanism for widening
the one list that is controlled on purpose, and a pack author could mint a legal edge
without ever intending to.

Reordering the read would have fixed the instance. Taking the family from the filename makes
the next instance unable to happen, which is the fix that counts.

**2. `pack` is a path, and it does something.**

`pack` was a required config key, validated, referenced in four comments, and read by
nothing at all. Setting it had no effect of any kind.

§13.4's example writes `"pack": "warehouse"` — a bare name. A bare name needs a search path,
a search path needs a resolution order, and a resolution order picks the wrong directory
silently. `"pack": "packs/warehouse"` is checked by the path machinery that already exists.
The spec example is amended rather than the implementation.

A pack's vocabulary sits at `<pack>/vocab/`, mirroring core's own `dropin/vocab/`, which
leaves the pack root free for the one adapter file §13.2 allows.

**3. A named pack that does not resolve is an error, not a skip.**

Skipping validates the mesh against core vocabulary alone, so every domain term reports "not
in core vocabulary" at once — a hundred errors whose single cause is one wrong path.

**4. In-place bundles are authored, not built. `--in-place` is removed.**

`build.py` declared `--in-place`, documented it in its module docstring, printed
`mode : in-place` in the run header, and consumed the flag in exactly that one print. The
source file was never touched; a mirror was written instead.

That is worse than a missing feature. It *reported* doing the one thing this tool promises
not to do, and then did not do it.

It is removed rather than implemented, and the reason is the promise it collided with:

> the adopter's own documents are never written into. `docs/` belongs to them, `.okfm/`
> belongs to the tool.

`rm -rf .okfm` returning the project to exactly what it was depends on that, and so does
pasting the folder into a stranger's repository. A build that edits your markdown cannot
make either claim. The mode was worth less than the promise.

In-place bundles themselves are unaffected and now work properly for the first time: you add
the frontmatter, you name the folder in `bundles`, and the build **registers** it in the mesh
without writing into it.

# What it cost to find

**This repository's own in-place bundle was invisible.** `docs/decisions` was excluded from
mirroring for the right reason and named in no `bundles` entry, so `check_bundles` had never
read it. Fourteen concepts — carrying `verified` entries, typed relations and cross-bundle
links — validated by nothing since the day they were written. The validator reported 49
concepts across 6 bundles while 63 existed. One of the fourteen carried
`generated.by: "claude-opus-5/level3-enrich"`, an actor form the profile does not recognise,
which the validator would have caught immediately.

The process fix is in `config_schema`: an excluded folder that holds concepts and appears in
no `bundles` entry is now a warning naming the line to add. `build.exclude` means two
different things — *nothing here worth mirroring* and *these files are already concepts* —
and the config cannot tell them apart. Saying so is the fix.

**The config rejected the build's own output.** A config naming `.okfm/docs` failed
validation at step one, before the build that creates it. Every project, first run, with an
error about a missing directory and no hint that the next step makes it. Paths under
`build.out` are now a warning; `check_bundles` runs after the build and still fails on one
that never appears, so nothing is lost.

**The benchmark's control arm deleted source documents.** Registering `decisions` made the
control arm remove files that are simultaneously concept and source, and four of eight
questions correctly failed §18.1's rule that every fact be answerable in both arms. The
questions were fine; the arm was wrong. An in-place concept is now **stripped** in the
control arm rather than deleted — the document as it stood before anyone typed `type:` —
which is the strip test taken one step further.

# Consequences

Adding a domain is one config line and a directory of YAML. `dev/check_pack_example.py`
stands `examples/warehouse/` up in a temporary directory on every CI run and asserts four
things: it builds, `dropin/` is byte-identical afterwards, the pack is vocabulary with no
code, and — the one that matters — **removing the pack makes the same mesh fail**. A pack
that changes nothing when removed is a pack that was doing nothing, and that is the shape
this exit criterion could most easily have been faked in.

The toy domain needed **no sixth source role**, which is evidence for closing that
vocabulary at five rather than an absence of anyone trying, and **no adapter**, so a pack of
pure vocabulary is a real shape and probably the common one.

# What would change this

A domain that genuinely cannot be expressed in vocabulary alone. §13.2 already allows one
adapter file per pack; the first pack that needs one tells us whether "a directory of YAML
plus at most one adapter" is the right boundary or merely the current one.
