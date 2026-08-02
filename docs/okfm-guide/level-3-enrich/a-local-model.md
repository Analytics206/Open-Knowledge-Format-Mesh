# The whole loop, no key

```bash
ollama pull llama3.2
```

```json
"enrich": { "base_url": "http://localhost:11434", "model": "llama3.2" }
```

```bash
python okfm/okfm.py enrich-local             # what it would write
python okfm/okfm.py enrich-local --apply     # write it
```

Then the rest is unchanged — `guard` checks what it wrote, and you clear the drift yourself.
That is the point: the model moved onto your machine, and nothing else moved at all.

# Why this is still level 3

The level 2/3 line is the `model` line, and `dev/check_levels.py` enforces it. A component
that calls a model is level 3 whether the model runs in a data centre or on the laptop calling
it — the output is still nondeterministic, still a draft, still guarded, and still waiting on a
person.

What running it locally removes is the key, and that distinction already sits one rung up the
same ladder: this is `needs-model` **without** `needs-secrets`. Level 3 has three variants and
only the last one holds a credential.

| Variant | Who drives | Who holds a key |
|---|---|---|
| your agent | your agent drives OKFM | your agent — OKFM holds none |
| local | OKFM drives a model on your machine | nobody |
| credentialed | OKFM drives a hosted provider | OKFM |

See [DR-0013](../../decisions/0013-the-local-model-variant.md) for why it is not a level 2+.

# The one component that is not `needs: []`

Everything else in the drop-in folder reads files and does arithmetic. This calls a model, so
it declares `needs: [model]` — and it is deliberately **absent from the pipeline**. A
workflow's needs set is the union of everything it invokes, so `okfm.py` with no arguments
would stop being runnable on a pull request from a fork the moment this appeared in it.

Reachable, and out of the run. That is what the union rule is for.

# What it may write

`description` and `tags`, and it must restamp `generated.by` as itself. The rest of DR-0008's
ownership table belongs to a person or the build, and `guard` reads the diff afterwards rather
than trusting the tool to have behaved.

Two rules on top of the shared contract, because a small local model is not your agent:

- **It cannot write a `needs-*` tag.** Those are the level ladder, which `check_levels.py`
  reads as fact. Existing ones are carried over verbatim; proposed ones are dropped. A guessed
  value in a field something treats as fact is worse than no value — the same reason
  `okfm_relations` is never inferred.
- **It is never asked whether a concept should be deleted.** The brief handed to *your* agent
  asks exactly that, because your agent can read the mesh and weigh it. This sees one document.

It also refuses a concept carrying `verified`, or one a person wrote. Neither should reach it —
the work list already excludes anything drafted — but the failure that check prevents is
silently overwriting a review.

# Everything the model returns is a proposal

A malformed answer is not a worse version of a good one, it is a sentence nobody wrote. So the
answer is rejected rather than repaired, and the output names the rule it broke: not JSON, no
description, empty, or past the length cap. Nothing is written by default; `--apply` writes.

# The endpoint is checked, and why that is not fussiness

`okfm.py config` warns when `enrich.base_url` is not loopback. Not because your own hardware on
your own network is wrong — nothing holds a key either way — but because the config is the only
place the local/credentialed boundary is written down in a form something can read.

[DR-0008](../../decisions/0008-build-pipeline.md) rejected a `network` value on the exposure
ladder because nothing needed the open internet without a credential. This is the closest
anything has come. Pointing the endpoint at a public host is that rejected fifth value
arriving, and it should say something rather than nothing.

# Context, which is the footgun

Ollama defaults to a 2048-token context and truncates in silence — so a long document gets a
description of its first half and nothing says so. `enrich.num_ctx` defaults to 8192 here for
that reason, and the run reports when a source was still too long to fit. Raise it for a
corpus of long documents; it costs memory on the machine running the model.

# Thinking is off, deliberately

Reasoning models are the wrong tool for this and it is not close. The answer is in the
document; a reasoning trace re-derives what one read already gives you. Measured against a
trivial prompt on a real box: 2.8k characters of thinking on a 4B model and 6k on a 9B, taking
15 and 89 seconds — against **1 to 2 seconds** with thinking disabled. Same answer.

On a work list of any size that is the difference between a queue that drains and one that
times out, so the request sets `think: false` and does not offer a knob for it.

It also buys the property `temperature: 0` was chosen for. With both set, two runs return
byte-identical text, which is what makes a second pass a no-op instead of a rewrite.

# What it is good at, and what it is not

Enrichment earns its place where extraction has nothing good to copy. Extraction takes the
first blockquote or paragraph, so a corpus whose documents open with a summary line extracts
*well* — and a local model will not beat it. Measured on this repository, whose documents do
open that way, the drafts came back honest, on-shape and slightly worse than what was there.

That is not a defect, it is the comparison being unfavourable. The case this is for is the
corpus that opens with a wall of prose, where the extracted description is a torn-off sentence
and anything written from the whole document beats it.

Either way nothing is published on a model's say-so: output lands `status: draft`, the guard
checks what it wrote, and drift stands until a person clears it. A weaker draft costs a slower
review, not a wrong bundle.
