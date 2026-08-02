---
type: OKF Member
title: docs
description: "Rationale, roadmap and prior art — the loose documents at the top of docs/, and the only member whose concepts the build wrote."
resource: ../../docs
status: draft
generated: { by: "agent:claude-opus-5", at: 2026-08-02T03:25:26Z }
okfm_member:
  aliases: ["the documents", "rationale", "roadmap", "prior art"]
  answers:
    - what are the phases and what is still open
    - what does success look like
    - what has the ecosystem already proven or disproven
  owner: null
  agent: null
  sync_policy: pull
okfm_relations:
  - { predicate: part_of, target: /index.md }
  - { predicate: registers, target: /docs/index.md }
---

# docs

Built from [`docs`](../../../docs). Its documents are the source; these
concepts point at them and never restate them.

`owner` is null because nothing can infer it. Naming the accountable person is the one thing
this file is for that a directory listing does not already do.

Stamped by an enrichment pass rather than the build, which is what stops the next rebuild
overwriting the `answers` list. That is the ownership rule working as designed: the build
owns what it generated until something else improves it, and improving it means saying so.
