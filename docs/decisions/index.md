---
type: Index
title: Decision records
description: What was decided about OKFM, why, and what would reverse it.
status: stable
generated: { by: "human:analytics206", at: 2026-08-01T00:00:00Z }
okfm_scope: project
---

# Decision records

Dated, numbered, short. One decision per file, kept even when superseded — the record of
what was decided and why is worth more than a tidy list of what is currently true.

`accepted` was decided. `deferred` was decided *not* to decide, and carries a re-entry
trigger. Nothing here is a blocking question — where a detail was open, it was decided and
noted rather than left to resurface.

These records exist so a rule that gets broken later is broken on purpose and on the record.
The [specification](../../spec/okfm-v0.2.1.md) is a working document, not law: where it and
the implementation disagree, the implementation is right and a record here says what changed.

| # | Decision | Status | Affects |
|---|---|---|---|
| [0001](0001-runtime-and-packaging.md) | Runtime and packaging for the implementation | partial | §13.3, §13.6, §13.7 |
| [0002](0002-version-scheme.md) | Version scheme | deferred | versioning policy, `okfm.json` |
| [0003](0003-phase-ordering.md) | Where federation sits in the delivery order | accepted | §15 — amended by 0010 |
| [0004](0004-split-the-spec-preserve-numbers.md) | Split the spec, preserve section numbers | accepted | all four documents |
| [0005](0005-path-resolution.md) | Bundle-relative in files, mesh-relative in the index | accepted | §6.5, §7.3, §12.3, §14.2 |
| [0006](0006-drift-cost-and-caching.md) | Drift is observed at build time, never at read time | accepted | §3.4, §8.3–8.5, §13.4, §14.4, §20.8 |
| [0007](0007-two-layers.md) | Base installs nothing; the implementation is optional | accepted | §13.2, §13.3, §13.6, §13.7, §14 |
| [0008](0008-build-pipeline.md) | What each component requires, and what the rebuild does | accepted | §8.4, §10, §11.6, §13.6, §16 |
| [0009](0009-adoption-levels.md) | Adoption levels — three, with level 3 credentialed as a variant | accepted, amended | §13.1, §13.3, §13.6, §13.7 |
| [0010](0010-okfm-self-hosts-as-a-mesh.md) | OKFM's own repository is the first mesh | accepted | §12, §14.5, §21.5 |
| [0011](0011-viewer-and-console.md) | Viewer stays read-only; a console is separate | accepted, built last | §14.3, §14.7 |
| [0012](0012-reach-is-configured.md) | Reach is configured, not discovered | accepted | §13.4, §13.5, §21.4 |
| [0013](0013-the-local-model-variant.md) | Level 2+ — a local model, on level 2's terms | accepted, amended | DR-0008, DR-0009 |
| [0014](0014-packs-and-in-place-bundles.md) | A pack is a directory; in-place bundles are authored, not built | accepted | §13.2, §13.4, DR-0007 |
| [0015](0015-the-install-has-an-upgrade.md) | The tool, the mesh and the config are three things | accepted | §13.3, §13.7, DR-0007 |
| [0016](0016-documented-commands-must-exist.md) | Documentation may not name a command that does not exist | accepted | §13.6, DR-0011 |
| [0017](0017-two-viewers.md) | Two viewers — the demo has data baked in, the adopter's must not | accepted | §13.7, §14.1, DR-0015 |
| [0018](0018-the-viewer-carries-the-mesh.md) | The viewer carries the mesh — bodies embedded, not fetched | accepted | §14.2, §14.3, DR-0011 |

## Two different axes, easily confused

**[0009](0009-adoption-levels.md) classifies adopters** by how deeply they engage — read and
copy, run the process, enrich, full suite. It decides what ships, what the README promises,
and how the repository is laid out. An adopter picks their own level.

**[0008](0008-build-pipeline.md) classifies components** by what they require to execute —
`[]`, `human`, `model`, `secrets`. It decides which CI job may run a thing and which fields
it may write. An adopter never sees it.

They meet at exactly one boundary: **the Level 2 / Level 3 line is the `model` line.** If
anything shipped at Level 2 declares `model`, the build fails. That is what keeps "never
needs an API key" true as the implementation grows, rather than a promise that quietly rots.

[0013](0013-the-local-model-variant.md) is the first thing that tested that boundary from the
other side — a model that costs nothing and needs no key — and it held. Removing the fee does
not move the line, because the line is about what has to reason and not about what it costs.

## Still open

**0001** — settled: Python 3.13, standard library only in `dropin/`. Packaging for the
credentialed variant (`uvx` vs `pipx`, the PyPI name) is still open and not blocking, because
nothing publishes yet.

Two smaller questions sit inside accepted records: 0008's `Feedback` destination split, and
0010's registry location. Neither blocks anything.

## Settled

**0002 — deferred.** Keep `v0.2.1`. The number pins to OKF v0.2 deliberately, is not expected
to move soon, and has a single user. Every cost in that analysis is a publication cost, and
nothing publishes yet. The re-entry trigger to watch is the first breaking change to an
`okfm_` key, which can arrive quietly while the profile is still settling in Phase 1.

**0004** — the spec is split four ways with section numbers preserved.

**0005** — bundle-relative paths in files, mesh-relative in the generated index.

**0007** — OKFM is a format contract that installs nothing, plus an optional, replaceable
reference implementation.

**0008** — every component declares what it requires, ordered by exposure, with a
composite's set being the *union* of everything it invokes. CI gates on the set, not the
tier number.

**0009** — cumulative adoption levels, each a complete usable process rather than a teaser
for the next. Amended: three levels, not four. Who holds the key is a change of direction —
OKFM driving a provider instead of your agent driving OKFM — so the credentialed case is a
*variant* of level 3 and not another step up.

**0013** — level 3 has three variants, split on who drives and who holds the key: your agent,
a model on hardware you own, a hosted provider. The middle one is named **Level 2+**, because
what it costs an adopter is level 2's price — no key, no account, no bill — plus the loop.
Amended to that name after this record argued the other way. The name is not a relocation:
the component still declares `needs-model`, still sits in the level 3 bundle, and
`dev/check_levels.py` is untouched. The ladder measures what OKFM asks of you before you can
start; the name measures what it costs. Those were the same number until a model became free.

**0012** — a concept is recognised anywhere, but read only where the config says. `exclude`
drops a folder inside a scan root; `include` adds a tree outside one. No project-wide sweep:
a scan wide enough to be convenient turns an adopter's templates and vendored documentation
into concepts on their first run.

**0010** — OKFM's own repository becomes a mesh, so the project runs the thing it describes
instead of only specifying it. Amended: the registry names the bundles that exist and gains
members as levels ship.

**0003** — federation's negotiation half lands after the SugarPaws3d port; its addressing
half already landed early under 0010. Phase order: baseline and addressing → distribution →
the port → negotiation.

**0011** — a full web UI is planned and built last, as the natural consumer of everything
below it. The web UI stays read-only regardless. The CLI and the UI are one surface: every
mutation has exactly one implementation, the UI calls it, the CLI exposes it, and building
the UI is what reveals which commands are actually needed.

**0006** — drift is observed during the build and cached; nothing resolves it at read time.
Trust and staleness stay read-time because they are free. The cache stores observations, not
verdicts, and a pointer that has never been observed reports `unknown` rather than defaulting
to fresh.

**0014** — a vocabulary overlay is a directory and the filename inside it names the family,
so a pack's reason code can no longer become a legal predicate. `pack` is a path rather than
a bare name, because a name needs a search order and a search order fails silently. And
`--in-place` is removed rather than implemented: it printed `mode : in-place` and mirrored
anyway, and a build that edits your documents cannot also promise it never touches them.
In-place bundles are authored by hand and registered by path — which is what this bundle is.

**0015** — the documented install put the tool, the config and the adopter's knowledge in one
directory. That works on day one and has no upgrade path on day two: re-running the install
nests a silent copy and updates nothing, and deleting first destroys every enriched concept.
Three directories now — `okfm/`, `.okfm/`, `okfm.json` — so upgrading is a delete and a copy.
Both layouts still work and the build warns when it finds the fused one. This repository had
the safe arrangement all along and the README described the other, which is exactly the gap
§13.7 exists to find.

**0016** — three commands were documented and did not run: `validate` (the dispatcher knew it
as `check`), `index` (which existed in no form while its config knobs shipped to every
adopter and read nothing), and a phantom `init`. Both real ones are built, and the rule is
wider than the fix — the documentation may not *name* a command that does not exist, in any
form, because a reader scanning for something to type cannot tell a roadmap entry from an
instruction. `build.bundle_tags` came out of the same work: a claim the build cannot derive
and a human cannot make stick has to be declared where the build reads it.

**0017** — the viewer at the download root has this project's mesh baked in, which is the
point of it at Level 1 and exactly wrong once copied: an adopter saw 68 of somebody else's
concepts and somebody else's name as owner, in a file they had just added to their
repository. The drop-in now ships a blank one, generated from the shipped page and guarded so
the markup cannot drift, and the build seeds it on a first run. That is also what makes
Level 2 a single folder copy instead of two copies and a paragraph explaining the second.

**0018** — bodies were fetched at click time, `file://` blocks fetch, and `file://` is the
whole of Level 1: the one thing Level 1 promises was the one thing the page could not do,
and it recommended a `--serve` flag that never existed. Bodies are baked in now, guarded by
the same `--check` that already guarded every other embedded field. Four features taken from
Google's reference viewer without taking its CDN dependency — inline markdown, search over
bodies, four layouts including bundles-as-columns, node size by content. The contamination
guard §21.3 left behind turned out to be a filename list for a file the corpus never
included; it is structural now and verified by falsification.

**0019** — `### Phase 3` vanished from the roadmap in a rewrite that ended one line short,
leaving Phase 3's scope and exit criteria sitting under Phase 2's heading while twelve
references pointed at a section that no longer existed. The numbered spine has been guarded
since the split; the corpus's other heading system, a name plus an ordinal, was guarded by
nothing. Finding it surfaced the larger one: nine of eleven commands did not answer `--help`,
four of them did their whole job instead — `okfm config --help` wrote a config file — and the
check meant to catch that probed commands by running them and accepted any exit code it
liked. Help is answered in one place now, and the probe asserts the help text rather than
tolerating an exit status.

**0020** — approving a draft was four hand edits across two parts of a file, and the fourth,
repinning `okfm_captured`, is silent when forgotten and brings back the drift you just
reviewed. It is a button. `okfm console --by human:<id>` serves the same page with an edit
surface that is dark unless it answers, so Level 1 from `file://` is untouched — checked by
requiring `EDIT.on` to have exactly one assignment, inside the probe. Overturns DR-0011 on
three counts with the reasons: the console is Level 2 because `needs: []` is the mechanical
test, it is one page rather than a third copy of the markup, and it edits bodies as well as
metadata. `concept_edit.py` splits a concept into keys and sections and round-trips all 74
concepts byte-identically.
