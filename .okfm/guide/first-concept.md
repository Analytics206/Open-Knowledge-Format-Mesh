---
type: Runbook
title: Your first concept
description: The smallest useful concept, and where to put it.
status: stable
tags: [getting-started, authoring]
generated: { by: "process:okfm-scaffold", at: 2026-07-31T00:00:00Z }
okfm_scope: guide
okfm_relations:
  - { predicate: part_of, target: /index.md }
---

# The smallest legal concept

One required key. That is the whole bar:

```markdown
---
type: Decision
---

We kept SQLite instead of Postgres because the harness is single-writer and the
operational cost of a second service outweighed the concurrency we would gain.
```

Everything else is optional. A consumer that rejects this file for missing `title`
is non-conformant.

# The smallest *useful* concept

Four more keys, each earning its place:

```markdown
---
type: Decision
title: SQLite over Postgres for the run store
description: Single-writer workload; a second service cost more than the concurrency was worth.
generated: { by: "human:you", at: 2026-08-01T10:00:00Z }
sources:
  - id: bench
    resource: /benchmarks/write-throughput.md
    okfm_role: subject
---

# Decision

Keep SQLite.

# Why

The harness is single-writer by construction, so the concurrency advantage is
unrealised.[^bench] Running Postgres adds a service to every developer machine and
every CI job.

# What would change this

Concurrent writers, or a second process needing the same store.

[^bench]: Write throughput benchmark
```

`description` is what gets injected into an agent's index, so it is the highest-value
line in the file. Write it as a claim, not a topic: *"Single-writer workload; a second
service cost more than the concurrency was worth"* beats *"Notes on database choice."*

# Where it goes

Wherever the documents it belongs with already are. A concept is any `.md` file with a
non-empty `type:` in its frontmatter — no directory is mandated, and there is no migration
project, so an existing docs tree becomes a mesh one frontmatter block at a time.

One thing to know: the tool does not go looking. It reads `build.root` (`docs/` unless you
say otherwise) and anything `build.include` names, so a concept in a folder outside that is
legal, portable, and invisible until you name it. Nothing scans your whole project, which is
why `templates/` and a vendored SDK's documentation do not turn up in your mesh.

# Then

```bash
okfm validate
```

```bash
okfm index
```

`validate` tells you whether it is legal. `index` shows you what an agent would
actually be handed, which is usually the more interesting answer.

# The mistake to avoid

Do not write a concept that summarizes a file you already have. Read
[the admission test](admission-test.md) before writing your second one — it is the
single rule that decides whether a mesh becomes useful or becomes overhead.
