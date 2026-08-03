---
type: OKF Member
title: decisions
description: 15 concept(s) authored in place in docs/decisions.
resource: ../../../docs/decisions
status: draft
generated: { by: "process:okfm-build", at: 2026-08-03T00:00:00Z }
okfm_member:
  answers: []          # what questions does this bundle answer? yours to write
  owner: null
  agent: null
  sync_policy: pull
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /decisions/index.md }
---

# decisions

Authored in place in [`docs/decisions`](../../../docs/decisions). Those files carry their own frontmatter, so they *are* the concepts — this build registers the bundle and never writes into it.

`owner` is null because nothing can infer it. Naming the accountable person is
the one thing this file is for that a directory listing does not already do.

`answers` is empty for the same reason, and it is the more valuable of the two.
It is what lets an agent pick a bundle by reading frontmatter instead of opening
every one — the whole difference between a mesh and a folder. Write three or four
questions this bundle actually answers, in the words somebody would ask them:

```yaml
okfm_member:
  answers:
    - how do I run the ingest job locally
    - what happens when a payment fails
```

Nothing will fill these in for you. A build cannot know what a bundle is *for*,
and a guess here sends an agent to the wrong bundle with confidence.
