# DR-0005 — Bundle-relative in files, mesh-relative in the index

- **Status:** accepted — provisional, revisit when `okfm view` is built
- **Date:** 2026-08-01
- **Affects:** spec §6.5, §7.3, §12.3, §14.2

## The gap

The specification defines bundle-relative paths (`/rules/churn-billing.md`) and
cross-bundle addressing (`okf://sp3d-rules/rules/churn-billing.md`), but never says how a
bundle-relative path becomes a path in a **mesh-level** index spanning several bundles.

Writing the guide bundle forced the question. The viewer's baked index uses
`/okfm-guide/index.md` — bundle directory included. A concept file inside that bundle
should, per §6.5, write `/index.md`.

## Decision

Three layers, three forms:

| Where | Form | Example |
|---|---|---|
| `okfm_relations` targets, `sources[].resource` | **bundle-relative** | `/index.md` |
| Markdown links in bodies | **relative** | `what-is-okfm.md` |
| `okfm-index.json`, viewer `p` and `r` fields | **mesh-relative** | `/okfm-guide/index.md` |

`okfm view` resolves bundle-relative to mesh-relative by prefixing the bundle root. The
transformation is one-way and lives entirely in the index builder; nothing in a bundle
ever stores a mesh path.

## Why relative links in bodies

§6.5 permits bundle-relative or relative and recommends the former. The guide breaks that
recommendation deliberately: a `/what-is-okfm.md` link resolves to the *repository* root
when rendered on GitHub, so it is broken for every reader who reads the guide before
cloning it. Since the guide's entire job is the first five minutes (§14.5), rendering
correctly in a web view outranks the recommendation. Relative links stay conformant.

For a mesh not read on a code host, follow the recommendation instead.

## Consequence

Bundles stay portable. Moving `okfm-guide/` to `docs/guide/` changes only the index that
`okfm view` regenerates, and no concept file needs editing — which is the property that
makes §13.5 discovery-by-convention work at all.

## Revisit when

`okfm view` is implemented, and when federation makes `okf://` a third form in play. If
resolving three forms turns out to be a recurring source of bugs, collapse to one and
accept the GitHub rendering cost.
