# Level 2 terms, with drafting

Level 2's promise is *no key, no account, no bill*. **Level 2+ keeps every word of it and adds
the enrichment loop**, by running the model on hardware you already own.

```bash
ollama pull qwen3.5:9b
```

Turn it on in `okfm.json`, or on the **Config** page of the web UI:

```json
"enrich": {
  "enabled": true,
  "base_url": "http://localhost:11434",
  "model": "qwen3.5:9b"
}
```

```bash
python okfm/okfm.py enrich-local             # what it would write
python okfm/okfm.py enrich-local --apply     # write it
```

Then `guard` and `revalidate` exactly as before. The model moved onto your machine and nothing
else moved at all.

**The model must already be pulled on that Ollama instance.** Nothing here downloads one, and
the config page cannot check — a page opened from `file://` cannot see your machine, let alone
another one on your network. A name that is not there fails at run time with a 404 naming it.
`ollama list` says what you have.

Two keys, not one, because they say different things: `model` names which one, `enabled` says
to call it. A config that mentions a model should not start making requests because it
mentions one.

# On your network, not just this machine

`base_url` takes any host. A box on your LAN is still your hardware and still holds no key:

```json
"base_url": "http://10.0.0.42:11434"
```

That host needs `OLLAMA_HOST=0.0.0.0` — Ollama binds to its own loopback by default, so a
remote box refuses every connection until it is told not to. `okfm.py config` warns that the
address is not loopback. That is the check working, not a problem: it is the only place the
line between *your hardware* and *somebody's paid API* is written down in a form something can
read, and a distinction nothing checks decays into one nothing means.

# Why the `+` and not level 3

The component is `needs: [model]`, lives in the level 3 bundle, and
[`dev/check_levels.py`](../../../dev/check_levels.py) is untouched — nothing at level 2 may
declare `model`, and nothing does.

Both are true because they measure different things. **The ladder measures what OKFM asks of
you before you can start; the name measures what it costs you.** Those were the same number
for as long as a model meant an API key. This is the first thing that pulled them apart.

The `+` is load-bearing. This is not level 2 — pretending so would make level 2's *never needs
a model* false. It is level 2's terms plus something you supply.

| | Who drives | Who holds a key |
|---|---|---|
| level 3, your agent | your agent drives OKFM | your agent — OKFM holds none |
| **level 2+** | OKFM drives a model you host | **nobody** |
| level 3, credentialed | OKFM drives a hosted provider | OKFM |

See [DR-0013](../../decisions/0013-the-local-model-variant.md), including the argument that
lost.

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

# Thinking is off, deliberately

Reasoning models are the wrong tool for this and it is not close. The answer is in the
document; a reasoning trace re-derives what one read already gives you. Measured against a
trivial prompt on real hardware: 2.8k characters of thinking on a 4B model and 6k on a 9B,
taking 15 and 89 seconds — against **1 to 2 seconds** with thinking disabled. Same answer.

On a work list of any size that is the difference between a queue that drains and one that
times out, so the request sets `think: false` and does not offer a knob for it.

It also buys the property `temperature: 0` was chosen for. With both set, two runs return
byte-identical text, which is what makes a second pass a no-op instead of a rewrite.

# Context, which is the footgun

Ollama defaults to a 2048-token context and truncates in silence — so a long document gets a
description of its first half and nothing says so. `enrich.num_ctx` defaults to 8192 here for
that reason, and the run reports when a source was still too long to fit. Raise it for a
corpus of long documents; it costs memory on the machine running the model.

# This is a proof of concept, and what it proves

**It proves the loop closes with no key and no bill**: config, request, refusal handling,
write, guard, human exit, all the way through on hardware you own.

**It does not yet prove enrichment is worth it.** That needs three things this does not have —
a corpus that extracts *badly*, a model that fits the machine, and [the
benchmark](the-benchmark.md) rather than a few descriptions read by eye.

The first reading, taken on **8 GB of VRAM** — which bounds it to 4B and 9B models at 4-bit,
and an 8B — was that the drafts came back honest, deterministic, and slightly worse than the
descriptions already there. Read that as *the comparison was unfavourable*, not as *local
models write badly*. This repository opens its documents with summary lines, which is exactly
the case extraction handles well; 16 GB runs a materially better model; and neither fact was
tested against the other.

Either way nothing is published on a model's say-so: output lands `status: draft`, the guard
checks what it wrote, and drift stands until a person clears it. A weaker draft costs a slower
review, not a wrong bundle.
