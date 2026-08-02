# Extraction is not drafting

Copying a sentence that already exists cannot invent. Writing a new one can. Everything about
level 2 follows from that one distinction: a description lifted verbatim from your file can be
unhelpful, but it cannot be *wrong about what your file says*, and no model is needed to
copy.

A drafted description is a claim. A copied one is a quotation. Only the second is safe to
generate unattended, and only the second can be checked against its source by hashing.

# What counts as prose

The extractor looks for the first paragraph that reads like an explanation, and most of the
rules for what to skip came from a corpus breaking the previous version:

- Headings, list items, tables, and fenced blocks are never prose.
- A blockquote counts only in the **lead** position — the first block after the H1. Further
  down it is usually a citation or an aside.
- A bold-led chunk is judged by length: under about 100 characters it is a metadata header
  (`**Status:** accepted`), above it is a real paragraph. The filter used to reject `**`
  outright, which silently discarded every paragraph opening in bold — most of this
  project's prose.
- A paragraph ending in a colon is a lead-in to the thing after it, so it is skipped.

# What it stamps

Full sha256 digests, not truncated ones — a prefix compares fine and rewrites badly.
`status: draft` with no `verified` entry, because nobody has reviewed anything.
`generated: { by: "process:okfm-bootstrap" }`, which is a load-bearing value rather than a
label.

# Why the actor is load-bearing

`--refresh` recomputes descriptions **only** where `generated.by` names that process. That is
how the extractor knows which text it owns and which a human wrote.

It is also why `generated` is deliberately not in the tier guard's protected set: a model
pass must be able to rewrite it, or the next refresh would clobber the prose the model just
produced. Before that was understood, a refresh silently overwrote a hand-written
description.
