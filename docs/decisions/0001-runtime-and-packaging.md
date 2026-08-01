# DR-0001 — Runtime and packaging for the reference implementation

- **Status:** proposed — **rescoped by [DR-0007](0007-two-layers.md)**, needs a call before Phase 1
- **Date:** 2026-08-01 (rescoped 2026-08-01)
- **Affects:** spec §13.3, §13.6, §13.7

## Scope correction

This record originally asked "what is *core* written in," treating OKFM as one installable
thing. [DR-0007](0007-two-layers.md) splits it in two: a **base** layer that is a
specification, a guide, a schema, and a viewer — requiring no install at all — and a
**reference implementation** that is optional.

Everything below applies **only to the reference implementation.** The base layer has no
runtime, no package, and no install step, which is the point of it.

An earlier version of this record justified zero dependencies partly by a "single file,
drop it anywhere" property. That phrase was borrowed from §21.2's description of the
ecosystem's *validator*, which genuinely is one file. It does not describe OKFM and has
been struck.

## The gap

§13 never says what the implementation is written in or how it installs.
`references/attesters/<name>.py` and `okfm validate` imply Python and a CLI, but nothing
states it. That choice decides packaging, CI, the dependency surface, and whether §13.7's
"stranger with a README and an hour" is achievable at all.

## Proposal

**Python 3.11+, installable with `uvx okfm` or `pipx install okfm`, standard library only
in core.**

Three reasons:

1. **Zero dependencies is why the ecosystem's validator is adoptable.** §21.2 records
   that its single-file, zero-config shape is the thing that makes it usable in someone
   else's CI without negotiation. The moment core needs a resolver for a dependency
   tree, the hour in §13.7 is gone.
2. **Attesters are Python already.** §6.6 and §9 put deterministic, LLM-free attesters
   in the bundle. A Python core runs them without a bridge.
3. **`uvx` gives a genuine no-install path.** `uvx okfm validate` in a foreign CI job is
   one line and leaves nothing behind.

Adapters, packs, and the benchmark harness **may** take dependencies. Core may not.

## The one real cost

YAML. Frontmatter parsing is the only place core needs it, and PyYAML would be the
single dependency. Options:

| | Cost |
|---|---|
| Depend on PyYAML | One dependency in the validator — the one component an adopter may want to run in their own CI without adopting the toolchain |
| Vendor a minimal parser | ~150 lines to write and own; handles the frontmatter subset only |
| Require frontmatter be JSON | Non-conformant — official OKF says YAML |

The dependency only really bites in the **validator**. It is the component most likely to
be lifted into someone else's pipeline on its own, and the one where "add a requirements
file first" is the difference between adopted and ignored. The rest of the implementation
may take dependencies freely.

**Recommendation: vendor a minimal parser.** The frontmatter subset in play is small
(scalars, lists, one level of nesting, flow mappings). The Phase 0 consistency checks
already parse it with ~40 lines of regex and correctly validated all ten guide concepts,
which is evidence the subset is tractable rather than a guess.

Emit through a real serializer if writing ever needs more than round-tripping.

## Rejected

- **Node/TypeScript** — the viewer is already dependency-free HTML and needs no toolchain;
  attesters would need a second runtime.
- **Go** — best single-binary story, worst attester story, and a compile step between an
  adopter and a fix.
- **Rust** — same, more so.

## Open

Does `okfm` publish to PyPI under that name, and is it available?
