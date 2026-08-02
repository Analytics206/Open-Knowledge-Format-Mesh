# ebd0ecab2c5a

## Answer

Because a markdown link has no predicate in it to copy, and the moment the tool picks one it
has stopped extracting and started asserting — into the one field the rest of the system reads
as fact.

### The rule extraction actually relies on

`dropin/bootstrap.py`'s docstring states the property that makes a no-model Level 2 legal:
every field it writes is *extracted or computed* — `title` from the first `# H1` (`_title`)
else the de-slugged filename, `description` from a lead blockquote else the first real
paragraph (`_extract_description`), `okfm_captured` from a sha256 of the text, `generated.by`
from a constant. DR-0008's "Extraction is not drafting" section draws the line precisely:

- **Extraction** copies text that already exists. "It cannot invent. Worst case it is
  unhelpful; it is never wrong about what the source says. `needs: []`."
- **Drafting** writes a new sentence that did not exist. "It can be wrong in ways nobody
  notices. `needs: [model]`."

`docs/okfm-guide/level-2-build/extraction.md` puts it as: a drafted description is a claim, a
copied one is a quotation, and only the second is safe unattended.

### A link is a target; a relation is a target *plus a claim about kind*

Spec §6.5 (`spec/okfm-v0.2.1.md:185`): "Links are **untyped** — the relationship kind lives in
surrounding prose." §7.3 exists *because* of that: OKFM carries `okfm_relations` alongside
ordinary body links so "an official consumer sees links; an OKFM consumer sees predicates."

So the link supplies `target:` and nothing else. To emit an edge the tool must also supply
`predicate:`, chosen from the closed vocabulary in `dropin/vocab/predicates.yaml` —
`supports`, `contradicts`, `evaluates`, `derived_from`, `serves`, `part_of`, `depends_on`,
`implements`, `implemented_by`, `registers`, `registered_by`, `perspective_on`, `defines`,
`measures`, `differs_from`, `supersedes`, `superseded_by`, `resulted_in`. Deciding that
`[extraction](../extraction.md)` means `depends_on` rather than `part_of` or `differs_from` is
a judgement about meaning, not a substring lifted from the file. It is drafting, wearing a
link's clothes — and there is no fallback of writing an untyped placeholder, because
`dropin/check_bundles.py` rejects any predicate not in the vocabulary
(`f"{rid}: predicate `{pred}` not in the vocabulary"`).

### The failure modes are not symmetric

An unhelpful extracted description is self-limiting: it lands `status: draft` with no
`verified` entry, so the trust machinery "reports this accurately with no special case"
(`bootstrap.py`, and DR-0008's same section).

A wrong edge is not self-limiting, because everything downstream consumes it as ground truth.
`predicates.yaml`'s header is the whole argument: "Impact analysis, drift propagation, and
neighbour surfacing all read these as fact, which is why the validator REJECTS a predicate that
is not listed here. **An edge asserted by a producer that guessed is worse than no edge at
all.**" DR-0008 inherited that verbatim from `project_template`'s `okf.py` comment
("`relations` is CURATED, not machine-managed…") and says "That is correct and it generalizes."
Its "Against" section concedes the restriction will chafe and holds anyway. Spec §14.6 adds the
consumer side: typed relations "are what make the edges mean anything." DR-0013 generalizes the
principle to `needs-*` tags: "a guessed value in a field something treats as fact is worse than
no value."

### So `okfm_relations` is `[human]` — stricter than the model tier

DR-0008's field-ownership table: `okfm_relations` | `[human]` | "Never inferred from prose.
Traversal treats an edge as fact". The component inventory lists `author-relations` ("add typed
edges") under `needs: [human]`, alongside `review-and-promote` and `author-decision`. DR-0009's
Level 2 tables make the same split concretely — "body links | markdown links preserved,
**untyped**" sits in the *derived deterministically* column, while `okfm_relations` sits in the
other one marked "never inferred at all — `[human]` (DR-0008)".

Note this is one rung stricter than drafted `description`, which is `[model]`. Adding a model
does not unlock relations; only a person does.

### It is enforced, not merely documented

- `dropin/guard.py` `PROTECTED` includes `"okfm_relations": "typed edges are never inferred;
  traversal reads them as fact"` and fails a diff that touches it.
- `dropin/enrich.py` lists it in `FORBIDDEN` and the prompt `BRIEF` says "Do NOT add
  `verified`, touch `okfm_relations`, or edit any field in: {forbidden}."
- `templates/AGENTS.md` rule 2, "Never infer typed relations", closes with the exact
  concession the question asks about: "Ordinary markdown links in the body are fine and
  encouraged."

Body links are still used — just as links. DR-0008's build step 5 resolves every markdown link
and `§N.M` cross-reference (ignoring fenced blocks), and `check_bundles.py` walks body links
only to report `broken link [{label}]({tgt})`. They are validated, never promoted to edges.

### The apparent exception confirms the rule

`dropin/build.py` *does* write `okfm_relations` with `needs: []` — `part_of -> /index.md` and
`registers -> /<bundle-id>/index.md` on generated `OKF Member` concepts, and `registered_by ->
/<mesh_id>/index.md` on a generated bundle index. Those are computed from `okfm.json`'s
`bundles` map and the mesh layout (`_bundle_id()` resolves the configured id so the target
actually resolves), not read out of anyone's prose. That is arithmetic over configuration, the
same class of operation as hashing a file. The contrast is written into the same generated
file: `owner: null` "because nothing can infer it."

### What you do instead

DR-0008's settled details: "A `[model]` component may write proposals to `review/`, never to a
concept… a proposal file is not a concept." `templates/AGENTS.md`: "If you believe two concepts
are related, say so in your response or in a review file — do not write the edge." A human then
merges them via `author-relations`. `templates/README.md` sums the contract up as "never infer
typed relations, leave the human gate to the human."

## Files used

- dropin/bootstrap.py
- dropin/build.py
- dropin/guard.py
- dropin/enrich.py
- dropin/check_bundles.py
- dropin/vocab/predicates.yaml
- dropin/README.md
- docs/decisions/0008-build-pipeline.md
- docs/decisions/0009-adoption-levels.md
- docs/decisions/0013-the-local-model-variant.md
- docs/okfm-guide/level-2-build/extraction.md
- docs/okfm-guide/level-3-enrich/the-agent-contract.md
- .okfm/level-2-build/extraction.md
- spec/okfm-v0.2.1.md
- templates/AGENTS.md
- templates/README.md
- README.md
