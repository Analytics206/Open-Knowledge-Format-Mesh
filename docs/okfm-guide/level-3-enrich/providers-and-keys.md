# Half built

The local half exists — [a local model](a-local-model.md) drives Ollama with no key and no
adapter layer. What is not built is the *provider abstraction*: the second adapter, the config
list of endpoints, and the credential handling that comes with a hosted API.

The rest of this records the shape and the reasoning so the decision does not have to be made
twice.

# Two adapters covers the field

Most hosted providers speak an OpenAI-compatible chat API, and so does Ollama, so one adapter
reaches local models and the majority of remote ones. Anthropic's API differs enough to need
its own. That is two pieces of code and a config list of endpoints — adding a provider becomes
a configuration line rather than a pull request.

Writing four adapters would mean maintaining four surfaces against four release cadences to
serve a difference that is mostly a base URL.

# Local models are a first-class path, not a consolation

Enrichment is short, bounded, repetitive work: read one document, write one description that
says what it is for. That is the shape small local models handle well, and it is the shape
where a key is most annoying to require.

If the loop works on Ollama, the credentialed variant stops being gated on a billing relationship — which
matters more for adoption than any provider feature.

That was written before any of it was built, and it is what [DR-0013](../../decisions/0013-the-local-model-variant.md)
acted on. The loop does work on Ollama, and it needed one endpoint rather than an abstraction
over four — which is the argument for two adapters arriving a step early.

# Why the key appears here and nowhere earlier

Three variants, and only the last holds a credential:

| Variant | Who drives | Who holds a key | Exposure |
|---|---|---|---|
| your agent | your agent drives OKFM | your agent | `needs-model` on the loop |
| local | OKFM drives a model on your machine | nobody | `needs-model` |
| credentialed | OKFM drives a hosted provider | OKFM | `needs-model`, `needs-secrets` |

The first two make no credentialed call, which is why neither carries `secrets`. This one
does, so its needs set will be `secrets` once it exists, and anything invoking it inherits
that — which is what keeps it out of the workflow that runs on pull requests from forks.

The reversal that defines the boundary is *who drives*, and both of the last two reverse it.
What separates them is the key alone. `okfm.py config` warns when `enrich.base_url` stops
being loopback, because that is the moment the two become hard to tell apart from the
config — and a distinction nothing checks decays into one nothing means.
