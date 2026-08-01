# dropin/

The Level 2 deterministic build. Copy this folder into a project and run it.

Python 3.13, **standard library only** — no install step, no requirements file. Every
component here is `needs: []` under
[DR-0008](../docs/decisions/0008-build-pipeline.md): no network, no secrets, no model. That
is what lets it run in CI on a pull request from a fork, and it is the rule the boundary
checks exist to protect.

| Script | Does |
|---|---|
| `bootstrap.py` | Turns plain markdown into concepts. Extracts `title` and `description` from text that already exists; computes `resource` and `okfm_captured`. Dry-run by default. |
| `bake_viewer.py` | Regenerates the viewer's baked index from the bundles. `--check` fails if the committed viewer is stale. |
| `check_bundles.py` | Validates every bundle: conformance, profile, strip test, controlled predicates, links, footnotes. |
| `check_docs.py` | Validates the spec corpus: one home per section, every §N.M reference resolves, every link exists. |

```bash
python dropin/bootstrap.py docs/decisions --type Decision --scope project
```

```bash
python dropin/bake_viewer.py && python dropin/check_bundles.py && python dropin/check_docs.py
```

All four exit non-zero on failure and run from any working directory.

## What they establish

**A bundle can be built with no model.** `bootstrap.py` created all eleven decision concepts
by extraction alone — every `description` copied from prose the record already contained.
Extraction can be unhelpful; it cannot be wrong about what the source says. Results land
`status: draft` with no `verified` entry, so the trust machinery reports them accurately with
no special case.

**Standard library is enough.** These parse frontmatter for 26 concepts across 3 bundles with
about 40 lines of regex and no PyYAML. The subset of YAML that OKF frontmatter uses is
small — scalars, lists, one level of nesting, flow mappings — which is why
[DR-0001](../docs/decisions/0001-runtime-and-packaging.md) can hold the no-dependency line
here rather than hoping.

**Generating beats checking.** `bake_viewer.py` replaced an earlier checker that compared the
guide against a hand-maintained viewer index. Generating the index makes that drift
impossible rather than merely detected.

## Still to come

This folder is not yet paste-and-go. It reads `okfm.json` from the repository root and
assumes this repository's layout. Phase 1 makes it default to wherever it is dropped, scan
the files around it, and write the config it used.
