---
type: Decision
title: DR-0018 — The viewer carries the mesh, because file:// is the whole of Level 1
description: "Bodies were fetched at click time and file:// blocks fetch, so the one thing Level 1 promises — open the page and read the guide — was the one thing the page could not do. It said so, and recommended a flag that never existed."
status: draft
tags: [web-ui, level-1, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: supersedes, target: /decisions/0011-viewer-and-console.md }
  - { predicate: depends_on, target: /decisions/0017-two-viewers.md }
---

# Context

Reviewing Google's OKF reference viewer against ours. Theirs embeds every concept body and
renders it in a detail panel; ours fetched bodies at click time and embedded none.

Ours also loads nothing from a network. Theirs pulls `cytoscape` and `marked` from a CDN, so
with the network off it renders no graph and no markdown at all. That trade is not one to
copy — a viewer that needs the internet to read a local file has given up the property that
makes shipping it as one file worth anything.

But the feature gap was real, and checking it surfaced something worse than a gap.

# The defect

**Level 1 could not read anything.** `fetch` is blocked on `file://`, and `file://` is how
Level 1 is used — download a folder, open the page. So clicking any concept produced:

> **Body not available here.** … Open `<path>`, or run the viewer with a `--serve` flag
> to read bodies live.

That flag was never a flag. Running it printed `unknown option: --serve` and exited 2. It was recommended in the viewer, in §14.2, and in two decision records.

So the whole of Level 1 — *open the file, read the guide* — resolved to a page that showed
the shape of the knowledge, refused to show the knowledge, and pointed at a command that
did not exist.

# Decision

**Bodies are baked in.** 117 KB → 309 KB for 69 concepts. It is one file, it opens
instantly, and every concept is fully readable with no server and no network.

The old rule's three justifications are answered in §14.3 rather than dropped. The first —
*an embedded body is a snapshot that silently diverges* — is the one that governed, and it
does not survive: the page already embedded titles, descriptions, trust tiers and drift, and
`bake --check` fails the pipeline the moment any of it disagrees with the mesh. Bodies fall
under the same guard at no new cost. **Access control is the justification that survives**,
scoped to a federation with a real boundary, and it belongs to the served console rather
than to this page.

**Four features taken from Google's viewer, all without a dependency:**

| | Theirs | Ours |
|---|---|---|
| markdown rendering | `marked`, from a CDN | ~60 lines, inline, escapes first |
| search | title / id / tag | title, path, type, description **and body text** |
| layouts | five cytoscape layouts | four, including **bundles-as-columns** |
| node size | body length | body length **and** inbound references |

Bundles-as-columns is not in theirs and could not be: their viewer renders one bundle.
Ownership is the thing a mesh exists to show and the thing a force layout scrambles.

Searching bodies rather than metadata matters more than it sounds. A mesh answers *why did
we decide X*, and the sentence that answers it lives in a body far more often than in a
title; metadata-only search finds the concepts that happen to be *named* after the question.

# What this cost to get right

**The contamination guard was a filename list, and the filename was never in the corpus.**
§21.3 records a published incident — a rendered bundle page carrying every body was found by
a control agent and an arm had to be rebuilt. `DERIVATIONS` excluded `okfm-web-ui.html` by
name, and printed a reassuring note about doing so, while `CORPUS_GLOBS` did not include
`*.html` at all. The file was absent from both arms by accident, and the note described a
protection that was not doing anything. The day anyone added html to that tuple, a page with
every concept body would have walked into the control arm unopposed.

Now `*.html` is in the corpus so the viewer is considered and *then* excluded, and the guard
is structural: a control-arm file carrying the text of three or more concepts is a rendered
view, whatever it is called. Verified by removing the filename allow-list — it catches the
viewer at 62 concepts.

**An enforcement that was documented and never built.** §14.3 listed *"`okfm validate` fails
if a committed artifact under `viewer.path` contains concept body text."* There was no such
check. Had it existed it would have caught this change on the first run — which is the
argument for writing an enforcement at the same time as the rule, not after.

**The phantom flag was invisible to the command checker**, which reads markdown and matches
command names. `--serve` is a flag, on a command that does exist. `dev/check_commands.py`
now reads the viewer too, skipping its baked data blocks, and checks documented flags
against the allow-lists the scripts declare. It immediately found two more mentions in
decision records and one in the specification.

# What would change this

A mesh large enough that the page stops opening instantly. At 69 concepts and 309 KB it is
not close, and the honest answer at that size is pagination or a served console, not a
return to a page that cannot show its own content.
