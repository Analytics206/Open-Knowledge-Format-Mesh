# scripts/

Phase 0 scaffolding. These are stdlib-only consistency checks written while building the
guide bundle and splitting the specification. They run from any working directory:

```bash
python scripts/check_docs.py
```

```bash
python scripts/check_guide.py
```

| Script | Checks |
|---|---|
| `check_docs.py` | Every section has exactly one real home across the four documents; every §N.M cross-reference resolves; every relative markdown link exists. Ignores fenced blocks — those are examples, not document. |
| `check_guide.py` | `okfm-guide/` matches the viewer's baked index: type, title, description, source count, relations, scope. Confirms trust tier is **derived** and that no concept stores a verdict (spec 3.4). |

Both exit non-zero on failure, so they work as CI gates today.

## These are temporary

They exist because `okfm validate` does not yet. In Phase 1 their checks fold into
`core/validate/` and this directory goes away:

- link and reference resolution → the pointer-resolvability pass
- "no stored verdict" → the derived-not-stored profile check
- frontmatter parsing → the vendored parser proposed in
  [DR-0001](../docs/decisions/0001-runtime-and-packaging.md)

`check_guide.py` is also the working evidence for that decision record: it parses all ten
guide concepts with about forty lines of regex and no YAML dependency, which is what
makes a zero-dependency core look tractable rather than optimistic.
