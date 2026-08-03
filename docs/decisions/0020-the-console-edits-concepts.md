---
type: Decision
title: DR-0020 — Approve is a button, and the console edits concepts
description: "Approving a draft was four hand edits across two parts of a file, one of which is silent when forgotten. It is one click now. DR-0011 said the console would be a separate artifact editing metadata only; both halves are overturned here, deliberately, with the reasons."
status: draft
tags: [console, web-ui, level-2, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: supersedes, target: /decisions/0011-viewer-and-console.md }
  - { predicate: depends_on, target: /decisions/0017-two-viewers.md }
---

# Context

> *"I think we need to update the web ui for level 2 to include a way to do things like
> `revalidate --by human:analytics206`. Right now I need to open each file and edit. We may
> limit what could be edited right now but it might end up being a full edit of each section.
> I don't want an editor that just opens files, it should parse sections to edit."*
>
> *"I would just like an approve button."*

Approving a draft was: open the file, change `status: draft` to `stable`, add a `verified`
entry with your handle and today's timestamp, and repin every `okfm_captured`. Four edits
across two parts of a file, per concept. The fourth is the one that matters and the one
nobody remembers — skip it and the drift you just reviewed is back tomorrow, with no
indication that the review was incomplete.

`revalidate --by human:<id> --stable` already did all four in one command. The gap was never
the capability. It was that reaching it meant leaving the page where you had just decided the
concept was fine.

# Decision

**Approve is a button.** It runs `revalidate --by <you> --stable`. There is a Review page
listing every `status: draft` concept with one button per row, and the same button in the
detail panel of any concept.

**The console is Level 2, not Level 3.** DR-0011 placed it at Level 3 by association with
enrichment. That is wrong by this project's own mechanical test: `dev/check_levels.py` reads
`needs:`, and a review console needs no model and no key, so `needs: []` — which is Level 2.
The review queue *exists* at Level 2, because drift and drafts are produced by the build, and
putting its only interface a level above the thing that creates the work was an error nobody
had cause to notice until somebody wanted to use it.

**One page, not two.** DR-0011 called for a separate served console. That was decided before
[DR-0017](0017-two-viewers.md) split the viewer in two and immediately required a generator
and a CI check to stop the markup diverging. A third copy is the larger risk, so the edit
surface lives in `okfm-web-ui.html` and is dark unless `okfm console` answers `/api/ping`.
DR-0011's actual requirement — *"an adopter who wants no server deletes the console and keeps
a fully functional viewer"* — is met by deleting `console.py`.

DR-0011 objected that this is *"one artifact with two security postures, distinguished by how
it was launched."* The objection is answered by narrowing it to something checkable:

> The page has exactly one switch for its edit surface — `probeConsole()` succeeding — and
> `dev/check_viewer_template.py` fails if `EDIT.on` is assigned anywhere else, in either
> viewer.

Falsified: adding a second assignment, of the kind a "force edit" query parameter would be,
fails the check naming both places.

**The console edits knowledge, not only metadata.** This is the rule that breaks. DR-0011:
*"the console edits metadata decisions, never knowledge… rewriting a concept body is
authoring, and authoring happens against files where git can see it."*

Overturned on the ask, and the argument for it does not survive the reason it was made.
Authoring belongs where git can see it — and git sees these edits exactly as well, because
they are writes to the same files in the same repository. The rule was protecting a property
that was never at risk. What it did cost was real: the one interface that knew which concepts
needed attention could not act on any of it.

Editable: everything except two keys. Not editable: `generated` and `sources`, which record
*when a machine did something*. Editing those is not an edit, it is a claim about history,
and the commands that wrote them are the only things that change them.

`status` and `okfm_relations` being editable was flagged as putting a browser form where the
tier guard's protected fields live, and taken anyway. The guard's purpose is intact: it
distinguishes an **agent** writing `verified` from a person doing it, and the console cannot
run without `--by human:<id>`. A console that supplied a default identity would be a process
signing a person's name with a web page in between to make it look otherwise.

# How it is built

**It never writes a concept field itself.** Approve shells out to `revalidate.py`; saving
goes through `concept_edit.py`; the pipeline button runs `okfm.py`. Every one is what the CLI
runs, so a mutation cannot behave one way in a browser and another in a terminal. That was
DR-0011's one practical rule and it is kept verbatim.

**`concept_edit.py` splits, it does not reformat.** A concept is two documents in one file:
frontmatter a validator reads by key, and a body a person reads by heading. Top-level keys are
edited as raw text — there is no YAML parser in `dropin/` and adding one would be a second
parser disagreeing with the first at the margins. A key you do not touch is returned byte for
byte.

Proven rather than claimed: **all 74 concepts in this repository parse and rewrite to
byte-identical files.** That test found the one real bug in the module — the body rebuilder
prepended a newline unconditionally, which put a one-line diff into the thirteen concepts
whose body starts immediately after the closing `---`. A save that changes nothing must
change nothing, or nobody can trust the saves that do.

**The browser addresses concepts by mesh path only** — `/decisions/0001.md`, never a
filesystem path. The server resolves it against a map built from the same `mesh_path()` the
bake stamps into the page. That function was inlined in `bake_web_ui`; it is hoisted now,
because the same string computed in two places is this project's most-repeated defect and
here it would have meant every Open button landing on the wrong file. Path safety falls out
as a property rather than a filter: nothing the client sends is ever joined to a directory.

Mutations also require an `X-OKFM` header — which a cross-origin page cannot set without a
preflight this server does not answer — and the server binds the loopback only.

# Two servers on one port, both believing they were serving

The last thing found, and the worst. Running the console against this repository to look at
the real review queue returned **zero drafts** — from a mesh holding fifty.

`/api/ping` answered `{"by": "human:you", "project": "my-project"}`. That was
`dev/check_readme.py`'s sandbox console, still running against a temporary directory that had
already been deleted, holding port 7345. The console started afterwards printed a banner
saying it was serving 73 concepts from this repository, and received nothing.

Two independent defects had to meet:

**The check leaked the server.** `okfm.py console` is a dispatcher that runs `console.py` as
a child. `proc.kill()` killed the wrapper and left the server. Every run leaked one — which
is also the true cause of a `PermissionError` traceback printed after a green tick, blamed at
the time on a Windows file-handle race. It is a process tree now, `taskkill /T` or a killed
process group.

**`socketserver` sets `allow_reuse_address = 1`.** On POSIX that only skips TIME_WAIT and is
wanted. **On Windows it lets a process bind a port another process is actively serving**, and
the older socket keeps the connections. So the second console did not fail; it succeeded,
silently, into a socket nobody would ever call.

The consequence is the part worth writing down. A browser showing a review queue that looked
correct was talking to a mesh that no longer existed on disk, under a different steward
handle, and **an Approve clicked there would have written to somewhere the person clicking
had never heard of.** The console binds with `allow_reuse_address` off on Windows now, so a
second one refuses to start and says what is already using the port.

Neither bug is about the console being wrong. Both are about a process that outlives what it
was serving, which is a shape worth remembering the next time anything here starts a server.

# What would change this

A second person editing the same mesh. Everything here assumes one steward at one keyboard:
there is no auth, no locking, and undo is one step deep in the server's memory. A hosted
instance ([DR-0010](0010-okfm-self-hosts-as-a-mesh.md)'s remote member) is where that stops
being adequate, and DR-0011 named the same trigger.
