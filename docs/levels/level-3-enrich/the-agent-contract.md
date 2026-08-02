# What it is

[`templates/AGENTS.md`](../../../templates/AGENTS.md). Copy it into your project as whatever
your agent reads — `AGENTS.md`, `CLAUDE.md`, a system prompt, an MCP instruction block. It is
prose, not code, and there is nothing to install.

# Why the whole integration is a file

Every alternative binds OKFM to a particular agent. A plugin needs a host; an MCP server needs
a runtime and a transport; an SDK needs a language. All three make "bring your own agent" into
"bring the agent we support," and the point of this level is that you already have one.

A markdown file works with every agent that reads markdown files, which is all of them, and
it costs nothing to keep working when the tools change.

# What it forbids, and why those specific things

The contract names the fields an agent must never write: `verified`, `status`,
`okfm_relations`, `type`, `title`, and `okfm_captured`. The list is not about tidiness. Each
one is a place where a plausible-looking edit becomes a lie the system will repeat:

- `verified` asserts a person checked. A model writing it fabricates a reviewer.
- `okfm_relations` are read as fact by traversal. An inferred edge is a guess presented as a
  citation.
- `okfm_captured` carries the drift signal. Refreshing it makes the concept agree with a
  source nobody reread.

# It is a contract, not a permission system

The agent can write anything it likes; nothing here prevents it. [The tier
guard](the-tier-guard.md) is what notices afterwards, by reading the diff.

That split is deliberate and honest about what is enforceable. Preventing an agent from
editing a file it has write access to is not a problem a markdown file can solve, and
pretending otherwise would be worse than checking the result.
