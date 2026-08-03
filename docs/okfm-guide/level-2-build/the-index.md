# What an agent would actually be handed

`validate` answers whether a bundle is legal. `index` answers whether it is *useful*, which
is usually the more interesting question — a mesh can be perfectly conformant and still hand
an agent sixty descriptions that say nothing, or hand it the wrong sixty.

```bash
python okfm/okfm.py index
```

It prints the context an agent gets: path, type, description, and the three signals a reader
weighs before relying on a concept — whether a human verified it, whether it is still a
draft, whether it is past its `stale_after`. Signals, not a verdict. Resolving them into one
score here would be storing a verdict in an agent's context instead of in a file, which is
the one thing this format never does.

# Injection is a budget problem

An agent has a finite context, so the question is never *what is in the mesh* but *what
survives the cut*. Three config keys decide it, and until recently all three were written
into every adopter's config and read by nothing at all.

| Key | Decides |
|---|---|
| `read.index.max_concepts` | how many survive |
| `read.index.priority_types` | which types go first |
| `read.exclude_scopes` | which scopes never enter |

Ordering is the mesh bundle, then `priority_types` in the order you listed them, then
everything else by bundle and path. The mesh goes first because it is the map: handing an
agent concepts without the routing layer is handing it a pile, and `okfm_member.answers` is
what turns *"where do I read about X"* into a path rather than a search.

`exclude_scopes` is why your agent is not handed ten concepts explaining OKFM. The shipped
guide carries `okfm_scope: guide`, the default config excludes that scope, and what is left
is knowledge about your project.

# Nothing is dropped silently

If the budget cuts, the command says how many and of what type:

```text
CUT BY BUDGET: 44 concept(s) did not fit — 23 Document, 11 Decision, 5 Index, 3 Log, 2 Runbook
```

An index that silently fits and an index that silently lost a third of the mesh look
identical from outside, and the second is how an agent answers confidently from half a
corpus. The cut concepts are not unreachable — an agent following the mesh index still finds
them — but a budget that quietly ate them is a different situation from one that did not,
and only one of those is worth knowing about.

# It was documented before it existed

Four documents told a reader to run this, including the page a first-time author reads
before writing anything. It printed `unknown command` and exited 2.

`validate` had the matching problem in the other direction: the specification, the README and
the guide all called it that — six times between them — while the dispatcher only answered to
`check`. One command with two names is a coin toss decided by which document you happened to
open, and the name the documentation gave you lost.

`dev/check_commands.py` now reads every `okfm <name>` out of the corpus and fails when the
dispatcher does not answer to it. The rule it enforces is slightly wider than it looks: the
documentation must not *name* a command that does not exist, in any form — not in a fence,
not in a sentence about what is coming later. A reader scanning for something to type cannot
tell a roadmap entry from an instruction.
