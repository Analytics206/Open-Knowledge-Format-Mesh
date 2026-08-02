# Not built

Designed and settled, no code. This concept records the shape and the reasoning so the
decision does not have to be made twice.

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

If the loop works on Ollama, level 4 stops being gated on a billing relationship — which
matters more for adoption than any provider feature.

# Why the key appears here and nowhere earlier

At level 3 your agent drives OKFM and holds its own credential; OKFM never makes a network
call. Here OKFM drives the provider, so OKFM holds the key.

That reversal is the whole definition of the boundary. It is also why this component's needs
set will be `secrets` once it exists, and why anything that invokes it inherits `secrets` —
which is what keeps it out of the workflow that runs on pull requests from forks.
