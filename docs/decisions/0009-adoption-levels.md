---
type: Decision
title: DR-0009 — Four adoption levels
description: "Four adoption levels, each usable on its own, with the boundary between 2 and 3 sitting exactly on the model line and credentials appearing only at 4 — because that is where the direction reverses and OKFM drives a provider instead of an agent driving OKFM."
status: draft
tags: [levels, adoption, boundaries]
generated: { by: "agent:claude-opus-5", at: 2026-08-02T02:07:15Z }
sources:
  - id: self
    resource: /0009-adoption-levels.md
    okfm_role: subject
    okfm_captured: { hash: "sha256:1efbd92c95dbcb33...", at: 2026-08-01 }
okfm_scope: project
---
# DR-0009 — Four adoption levels

- **Status:** accepted 2026-08-01
- **Date:** 2026-08-01
- **Revisions:** r1 levels 2/3 split on *who does the work* · **r2 they split on whether the
  shipped components reason; "minimal but full featured" made the governing constraint**
- **Affects:** spec §13.1, §13.3, §13.6, §13.7; refines [DR-0007](0007-two-layers.md)

## Not the same axis as DR-0008

Worth stating plainly, because the two were conflated during drafting.

[DR-0008](0008-build-pipeline.md) classifies **components** by what they require to execute
— `[]`, `human`, `model`, `secrets`. It decides which CI job may run a thing and which
fields it may write. An adopter never sees it.

This record classifies **adopters** by how deeply they engage. It decides what ships, what
the README promises, and how the repository is laid out. An adopter picks their own level.

The two align at exactly one boundary, noted below.

## The governing constraint

> **Every level is minimal but full featured: a complete, usable process, which is also the
> example you modify.**

No level is a teaser for the next one. Someone can stop at Level 2 and maintain a mesh
indefinitely — by hand, with no key and no model — and be running a real system, not a
crippled preview.

And the bar for "usable" is stated honestly rather than oversold: **a workflow that works
and is a sound starting point, not one that fits every project unmodified.** An adopter is
expected to edit a workflow for their use case. What they must not have to do is write one
from scratch, or reverse-engineer what a correct one looks like.

This is §14.5's guide philosophy — *teaches by being the thing it describes* — applied to
processes instead of documents.

## What is not a level

**Pointing a coding agent at the repository.** An adopter can do that at any level and ask
for anything: copy this into my project, build me one for X, explain why my bundle fails
validation. It needs nothing from OKFM beyond readable documents, so it is available from
Level 1 and is not a rung on the ladder.

An earlier revision made "agent-generated" Level 3. That was wrong: it described what the
*adopter's* agent does, not what OKFM ships.

## The levels

Cumulative — each includes everything below it.

### Level 1 — download it

Download the project. Open `okfm-viewer.html`. Read the guide.

That is the entire level. There is nothing to install and nothing to run.

**Ships:** `spec/`, `okfm-guide/`, `okfm-viewer.html`, `docs/`, `examples/`, `templates/`.

### Level 2 — the deterministic process, as a drop-in folder

**Copy the folder into your project and run it.** It defaults to the location it sits in,
scans the files around it, and produces a bundle. Open the viewer and see the result —
unenriched, but real.

Not a process the adopter builds from an example. A process they paste and run.

**Ships:** + every component whose `needs` excludes `model` — including credentialed
resolvers, which are deterministic even when they reach a warehouse.
**Adopter supplies:** Python 3.13, and their own credentials if they resolve live pointers.
**Installs:** nothing. Standard library only — see [DR-0001](0001-runtime-and-packaging.md).
**Shape:** a self-contained directory, copy-pasteable, with no assumption that it was
installed as a package.

Two constraints, and both matter. **Liftable**: the folder is pasted into a stranger's
repository and run there, so it may not reach outside itself. **No install step**: a
dependency means that stranger resolves a package tree before anything happens, in whatever
environment they have — which is the friction this level exists to remove.

#### Mirror by default; in-place on request

The folder is pasted into other people's repositories, so the first run must not rewrite
their files.

**Mirror (default).** Concepts are written into the bundle and point back at the source via
`resource` and `okfm_captured`. The adopter's markdown is never touched. If they delete the
folder, nothing of theirs changed.

**In-place (`--in-place`).** Frontmatter is added to their markdown, so their files *become*
the concepts. Right when the documents are themselves the knowledge — this project's own
decision records, for instance — and wrong for a docs tree that concepts are merely *about*.

The distinction is whether the source *is* the knowledge or merely *carries* it. Mirror is
the safe default because a stranger pasting a folder into their repository has not consented
to a rewrite of every markdown file in it.

#### Where it writes, and what it scans

Two separate questions, and the second is the one that matters.

**The bundle is written inside the dropped folder** — `<project>/okfm/bundle/`. The reason is
symmetry with the paste that created it: delete `okfm/` and everything OKFM ever wrote goes
with it, leaving the project exactly as it was. No mystery `.okf/` appearing at the
repository root, and no argument about who owns a directory the adopter did not create. It is
one config key, so an adopter who prefers a mirrored `.okf/` beside their sources changes it
in a line.

**Scope is explicit, because the default is wrong for most people.** Projects have many
folders under `docs/` and few adopters want concepts for all of them. So:

- First run with no config **scans the parent directory, reports what it found, and writes
  the config it used.**
- That generated config lists the scanned paths, so pruning is deleting a line rather than
  reading documentation about scoping.

This keeps the "paste and run" promise — something real happens with zero configuration —
while making the first thing an adopter edits a file OKFM already wrote for them. A usable
process that is also its own example.

#### Bootstrap from zero, without a model

The open question at this level was whether a bundle can be created for files that have no
concepts yet, with no agent involved. **It can, and `project_template` already proves it.**

The distinction that makes it work is **extraction versus drafting**. Extraction copies text
that already exists and cannot invent; drafting writes new text and can. Only drafting needs
a model.

| Derived deterministically | How |
|---|---|
| `type` | directory or filename convention |
| `title` | first `# H1`, else the filename de-slugged |
| `description` | first blockquote, else first paragraph, capped — skipping headings and bold metadata blocks (`okf.py:312`) |
| `resource`, `okfm_captured` | path and hash |
| `generated: {by, at}` | `process:okfm-build` |
| section anchors | parsed headings with line ranges |
| body links | markdown links preserved, **untyped** |
| `index.md` | generated from descriptions |

| Needs a model | Why |
|---|---|
| `tags` | topic extraction is judgement |
| `# Summary`, `# Covers` | new prose |
| section purposes | new prose |
| `okfm_relations` | never inferred at all — `[human]` (DR-0008) |
| `verified` | never machine, ever |

The result is honest by construction: an extracted description plus `status: draft` plus no
`verified` entry renders in the viewer as exactly what it is — a real concept nobody has
reviewed. Drift detection works on it immediately, because `okfm_captured` is real.

Extraction quality tracks how the source corpus is written — a docs tree that opens each
file with a summary line extracts beautifully; one that opens with a wall of prose extracts
adequately. That variance is precisely what Level 3 fixes, and it is not a reason to
withhold Level 2.

### Level 3 — the reasoning components

Full enrichment lifecycle, driven by whatever the adopter already uses to reason: a coding
agent, an LLM, an MCP server. Configurable by preference rather than pinned to one.

**Ships:** + every component whose `needs` includes `model`, the workflows composing them
with Level 2, and the prose contract an agent follows.
**Adopter supplies:** their own agent or endpoint.
**Installs:** nothing that presumes a specific provider.
**Keys:** none. This is the point.

**At Level 3 the adopter's agent drives OKFM. At Level 4 OKFM drives a provider.** That is
why keys appear at Level 4 and not here — a Level 3 adopter is already authenticated in
their own tool, and OKFM never holds a credential.

The complete process is *maintain a mesh with drafting help*: Level 2 detects what went
stale, Level 3 drafts the prose, a human promotes it. Fully usable without any of Level 4.

### Level 4 — the full suite

Supply a key, pick a provider, write a small config, run. Every OKFM capability wired
together and demonstrated end to end.

**Ships:** + provider abstraction, packs, federation, the loop-family workflows, benchmark,
and a full worked harness integration.
**Adopter supplies:** an API key, a provider choice, `okfm.json`.
**Installs:** the reference implementation.

Level 4's contribution is **integration**, not new capability. It is where the pieces stop
being pieces.

#### Providers

One OpenAI-compatible adapter covers most of the field — OpenAI, OpenRouter, Groq, Together,
LM Studio, vLLM, and Ollama all speak it. Anthropic does not natively, and it is what the
harness already uses. So the realistic shape is **two adapters, not four**: OpenAI-compatible
and Anthropic, plus a config list of known-good base URLs for the popular endpoints. Adding
a provider then becomes a config line rather than code, which matches §13.2's "packs are
contributions, not forks."

Two things worth stating rather than discovering:

- **A lowest-common-denominator interface flattens provider-specific features** — prompt
  caching, extended thinking, structured tool use. For enrichment (short, bounded, high
  volume) that is fine. The loop-family workflows will want more, and should be allowed to
  use a richer adapter where one exists.
- **Local models are a serious option here, not a checkbox.** Enrichment is cheap and
  repetitive, which is exactly the workload a small local model handles well. Ollama makes
  "run the whole thing at zero cloud cost" a real path, and that is worth protecting as a
  first-class configuration.

#### A hosted instance: additive, not a substitute

Level 4 as an online reference rather than code in the repository is appealing, and half
right.

**Wrong as a substitute.** Level 4's acceptance test is that a stranger reaches a running
mesh *on their own project*. A demo they can browse proves nothing about that, and moving
the code out of reach fails the test at exactly the level where the project claims most.

**Right as an addition, and it earns its place for a reason that has nothing to do with
demos.** A hosted OKFM instance is a bundle that lives somewhere else, is reached through its
own agent, is pinned by commit, and can decide what to share. That is the one part of
federation a single repository cannot demonstrate — see
[DR-0010](0010-okfm-self-hosts-as-a-mesh.md). It turns §12.6's "the agent is the
access-control point" from a design position into something with a network boundary that can
actually refuse.

So: ship Level 4 in the repository, and stand up a hosted instance as a **remote mesh
member** an adopter can federate against.

#### The harness is an example, not the substrate

Level 4 including a full harness integration is right — it is the reference runtime and the
best demonstration of §13.6 mode 1. The risk is that "full example" quietly becomes
"required," at which point Level 4 is unusable to anyone not running that harness and
DR-0007's stranger test fails at the top level.

**Level 4 must stay runtime- and provider-agnostic, with the harness as one worked
integration among possible others.** The CLI path (mode 3) has to remain a complete way to
use Level 4.

## Where this meets DR-0008

The levels align with component requirements at exactly one boundary:

| Level | Components it admits |
|---|---|
| 1 | none runnable — documents and a viewer |
| 2 | `model ∉ needs` — so `[]`, `[human]`, `[secrets]`, `[human, secrets]` |
| 3 | adds `model` |
| 4 | any, plus composition and provider configuration |

**The Level 2 / Level 3 line is the `model` line, exactly.** That single fact makes the
packaging claim mechanically checkable against the component manifest: if anything shipped
at Level 2 declares `model`, the build fails. It is what keeps "never needs an API key"
true as the implementation grows, rather than a promise that quietly rots.

Above and below that boundary the levels are about scope and integration, not requirements —
Level 4 admits nothing Level 3 does not; it composes and configures it.

The levels also line up with §13.6's three runtime modes, seen from the adopter's side
rather than the implementer's:

| Level | §13.6 mode |
|---|---|
| 2 | mode 3 — plain CLI, no agent |
| 3 | mode 2 — agent instructions, the adopter's agent drives |
| 4 | mode 1 — inside a harness, OKFM orchestrates |

That the two decompositions land on the same boundaries without being designed to is
reasonable evidence the boundaries are real.

## Is four right?

Yes, under r2's framing, and more clearly than under r1.

| Boundary | What separates the two sides |
|---|---|
| 1 → 2 | documents vs. runnable code |
| 2 → 3 | **deterministic vs. reasoning** — the sharpest line in the project |
| 3 → 4 | pieces vs. an integrated suite |

r1 put Level 3 on probation because it split on *who does the work*, which was a difference
in ambition rather than in what shipped. Splitting on whether the shipped components reason
removes that doubt: the 2 → 3 boundary is the same one that decides whether CI needs an API
key, whether output is deterministic, and whether a human must review before publish.

## Consequences

### Repository layout

Levels 1–2 are DR-0007's **base**; Levels 3–4 are the **implementation**. Level 2 is the
seam: it puts runnable code in front of an adopter who installed nothing, so the
deterministic build must be liftable as files rather than reachable only through the CLI.

That constraint lands on [DR-0001](0001-runtime-and-packaging.md) and sharpens it — the
validator is the component most likely to be lifted alone, so it is the one that must carry
no dependency.

### The README declares a level per section

Four quickstarts, each stating its cost, so a reader self-selects instead of reading past
three sections of irrelevant setup.

### The distribution test splits four ways

§13.7's "stranger, README, under an hour" becomes one acceptance test per level. Each is
worded to allow the modification the governing constraint expects:

| Level | Passes when a stranger, given only the README, can… |
|---|---|
| 1 | hand-write a valid concept their own agent reads correctly — **nothing installed** |
| 2 | paste the folder into a project with **no existing bundle**, run it, and open the viewer on a real generated mesh — **no key, no model** |
| 3 | enrich a stale concept with their own agent and get a reviewable draft — **no key held by OKFM** |
| 4 | reach a running mesh answering one real question about their project, in under an hour |

Level 4's is the existing §13.7 wording. Levels 2 and 3 permit editing config or a workflow
first — that is the expected adaptation, not a failure. What none of them permits is writing
a process from scratch.

Level 1's is the strongest claim the project makes.

## Against

**Four levels is marketing unless each has a test.** Correct, which is why each has one.
If a level's test cannot be written, the level is not real.

**Level 2 blurs DR-0007's clean base/implementation line.** It does. The alternative is
worse: telling an adopter who wants only a validator that they must adopt a CLI, a config
schema, and a directory convention to get one.

**"Minimal but full featured" is expensive.** Every level needs a process that genuinely
works, which is more work than a single integrated product plus documentation. It is also
the only version of this that survives someone taking one piece and ignoring the rest —
which, per DR-0007, is the intended mode.

## Open

- Does Level 1 ship `templates/`, or does that belong at Level 2? An adopter copying by hand
  wants a starter bundle; a starter bundle is arguably part of the format.
- Should the viewer state which level an adopter is operating at? It already distinguishes a
  live mesh from the bundled guide, which is close to the same signal.
- Does Level 3 ship an MCP server, or only components callable from one? The distinction
  decides whether "an agent they already use" is really sufficient.
