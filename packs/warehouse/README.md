# The warehouse pack

A domain pack: four YAML files, no code. Point a config at it and a mesh gains this
domain's vocabulary without core changing by a line.

```json
{ "pack": "packs/warehouse" }
```

That is the whole installation. `packs/` is not under `build.root`, so nothing here is
scanned as a concept — a pack contributes *vocabulary*, never content.

## What it adds

| File | Family | Adds | Unknown term is |
|---|---|---|---|
| `predicates.yaml` | typed edges | 3 | **rejected** |
| `types.yaml` | concept types | 4 | a warning |
| `reason_codes.yaml` | why a call went that way | 6 | a warning |

Each file is read **only** by the family its filename names. A term in
`reason_codes.yaml` reaches the reason-code vocabulary and cannot reach the predicate one.
Before DR-0014 that was untrue: overlays were a flat list of files appended to every
family's read, so this pack would have made `late_arriving_fact` a legal predicate.

## What it deliberately does not add

**No `roles.yaml`.** Core's five source roles are closed, with a stated re-entry trigger:
*the first real domain that needs a sixth.* This domain was built as that test and did not
need one — `golden_reference` covers reconciling against a trusted report,
`constraint_source` covers a freshness SLO, and `defines` covers a data contract. So the
closed-at-five decision stands on evidence rather than on nobody having tried.

**Three predicates, not fifteen.** `predicates.yaml` lists what was considered and dropped
because core already said it. A pack that adds a predicate is widening the one vocabulary
the validator refuses to guess about, and the honest default is to find the core predicate
that already fits.

**No adapter.** §13.2 allows a pack one adapter file, for binding a discovery source. This
one has nothing to discover — it is vocabulary alone, which is the smallest a pack gets and
the shape most packs should be.

## Why this pack exists

It is the Phase 2 exit test: *a toy second domain stood up via pack + config with zero core
edits.* `examples/warehouse/` is the standing-up. The claim being tested is not "OKFM has
no domain words in its code" — CI has grepped for that since Phase 1 — but the much larger
one that a **new** domain needs none. Those are different claims, and only the second
supports calling the thing distributable.
