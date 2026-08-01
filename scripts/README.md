# scripts/

Early cuts of the Level 2 deterministic build. All four are stdlib-only, take no network,
hold no secrets, and need no model — `needs: []` under
[DR-0008](../docs/decisions/0008-build-pipeline.md). They run from any working directory and
exit non-zero on failure, so they work as CI gates today.

| Script | Does |
|---|---|
| `bootstrap.py` | Turns plain markdown into concepts. Extracts `title` and `description` from text that already exists, computes `resource` and `okfm_captured`. Dry-run by default. |
| `bake_viewer.py` | Regenerates the viewer's baked index from the real bundles. `--check` fails if the committed viewer is stale. |
| `check_bundles.py` | Validates every bundle: conformance, profile, strip test, controlled predicates, link and footnote resolution. |
| `check_docs.py` | Validates the four-document spec corpus: one home per section, every §N.M reference resolves, every link exists. |

```bash
python scripts/bootstrap.py docs/decisions --type Decision --scope project
```

```bash
python scripts/bake_viewer.py && python scripts/check_bundles.py && python scripts/check_docs.py
```

## What they demonstrate

**A bundle can be bootstrapped with no model.** `bootstrap.py` created all eleven decision
concepts by extraction alone — every `description` copied from prose the record already
contained. That is the evidence behind
[DR-0009](../docs/decisions/0009-adoption-levels.md)'s Level 2 claim and behind
[DR-0008](../docs/decisions/0008-build-pipeline.md)'s *extraction is not drafting*
distinction. Extraction can be unhelpful; it cannot be wrong about what the source says.
Results land `status: draft` with no `verified` entry, so the trust machinery reports them
accurately with no special case.

**Zero dependencies is viable.** Between them these parse frontmatter for 26 concepts with
about 40 lines of regex and no PyYAML — the working evidence for
[DR-0001](../docs/decisions/0001-runtime-and-packaging.md).

**Generation beats checking.** `bake_viewer.py` replaced an earlier `check_guide.py` that
compared the guide against a hand-maintained viewer index. Generating the index makes that
drift impossible by construction, so the check became unnecessary rather than merely passing.

## These are temporary

They exist because `okfm validate` and `okfm build` do not yet. In Phase 1 they fold into the
Level 2 drop-in folder and this directory goes away:

- `check_bundles.py` → the conformance, profile, and strip-test passes
- `bootstrap.py` → the build's extraction step
- `bake_viewer.py` → `okfm view`
- `check_docs.py` → a docs-corpus lint, or retired if the spec corpus becomes a bundle
