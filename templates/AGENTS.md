# Working with an OKFM mesh

Copy this file into your project — as `AGENTS.md`, `CLAUDE.md`, a cursor rule, or whatever
your tool reads. It is the whole contract. No installation, no runtime, no key.

This is **Level 3**: your agent drives OKFM. OKFM never holds a credential.

If nobody is pointing an agent at the mesh, `okfm.py enrich-local` does this same work with a
model on the machine — same contract, same guard, same person at the end. This file stays the
authority on what may be written either way.

---

## What a mesh is

Markdown files with YAML frontmatter. Any `.md` file with a non-empty `type:` is a concept,
wherever it sits. `index.md` is a directory map; `log.md` is a changelog; everything else
with a `type:` is knowledge.

The mesh records **why this project believes what it believes** — the reasoning that the code
cannot state. It is not a summary of the code.

## Before you act

**Read `.okfm/mesh/index.md` first**, then the `index.md` of whichever bundle it sends you
to. Both are maps, not content — open only the concepts they point you at.

The mesh is where routing happens. Each member concept carries `okfm_member.answers`, a list
of the questions its bundle can answer, so *"where do I read about X?"* resolves to a path
without you having to know what bundles exist. If there is no mesh — a single-bundle project —
start at that bundle's `index.md`.

Nothing dispatches for you. The mesh is a directory you read; deciding which member to open,
and assembling an answer from more than one, is your job.

**Weigh three signals before relying on a concept.** They are stored deliberately so you can
judge, rather than being pre-judged for you:

| Signal | Means |
|---|---|
| no `verified` entry | nobody has confirmed this. Treat as a draft, whatever it says |
| `verified: [{ by: "human:…" }]` | a person reviewed it |
| `status: draft` | not ready to rely on |
| `status: deprecated` | superseded — look for what replaced it |
| `stale_after` on or before today | old enough to deserve review; say so rather than silently trusting it |

**Follow `sources` when the answer needs detail.** A concept that abstracts a source cites it
with `okfm_role: implementation`. The detail is downstream — go get it. A concept is never a
reason to stop reading.

## What you may write

Three rules, and the third is the one people get wrong.

**1. Draft freely, but land as `draft`.**

Anything you write carries:

```yaml
status: draft
generated: { by: "agent:<tool>/<model>", at: <ISO-8601> }
```

The `agent:` prefix is required and is read rather than displayed — the build decides what it
may overwrite from it, and the trust tier a reader sees is derived from it. Three kinds exist:
`human:`, `agent:`, `process:`. An unrecognised prefix resolves to *machine*, so a typo here
silently downgrades rather than failing. (This said `<your-agent>/<model>`, with no prefix at
all, while every shipped concept used `agent:`.)

and **no `verified` entry**. Ever. Verification is a human act; writing one you did not earn
silently promotes a trust tier nobody granted, which is worse than an honest gap.

**2. Never infer typed relations.**

`okfm_relations` carries predicates that impact analysis and drift propagation treat as
*fact*. A wrong edge is worse than a missing one. If you believe two concepts are related,
say so in your response or in a review file — do not write the edge.

Ordinary markdown links in the body are fine and encouraged.

**3. Extraction is not drafting.**

Copying a sentence that already exists cannot invent. Writing a new one can. When you are
filling a `description`, prefer to lift the source's own words; when you must summarize, say
in the body that you are abstracting and cite the source.

## What not to write down

Before creating a concept, answer one question:

> **Does this say something its sources cannot?**

| Verdict | Example | Do |
|---|---|---|
| **Admit** | why a threshold is 1,000; why an approach was rejected; which definition a number uses | write it |
| **Reject** | restating a schema; paraphrasing a query; summarizing a README | cite the source, write nothing |

This is not style advice. It was measured: a bundle that summarized a validator **lost** a
question the raw source would have answered, because the summary dropped the detail and the
agent stopped there. A concept standing between a reader and a better answer is a regression,
and deleting it is a fix.

## After you change something

1. Update the concept you touched — including `okfm_captured` if you changed what a pointer
   points at.
2. Add a line to `log.md`.
3. Do **not** flip `status` to `stable` or add `verified`. Leave that for a human.
4. If the project has a validator, run it before committing.

## Never store a verdict

Trust, staleness, and drift are **computed when read**, from `verified`, `stale_after`, and
`okfm_captured`. Never write `okfm_stale: true`, `okfm_drifted`, or a trust field into a
file. A stored verdict is wrong the moment somebody fixes the source, and nothing says so.

If you want to report that something looks stale, say it in your response.

## Numbers

If a figure has an `Attested Computation` concept, use it: supply values for its declared
`parameters` only. Do not author, edit, or reimplement the computation, and do not present a
number whose attestation failed. The computation carries its own query precisely so that it
cannot drift from the thing it describes.

## In short

Read the index. Trust what is verified, flag what is not. Write drafts, never verdicts.
Record why, never what the code already says. Leave the human gate to the human.
