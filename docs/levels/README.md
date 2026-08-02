# The four levels

This folder is the **raw material**. One subfolder per adoption level, plain markdown with no
frontmatter — the kind of documentation any project already keeps in `docs/`.

The OKF built from it lives in [`.okfm/`](../../.okfm), one subfolder per level. That split is
the drop-in build's default behaviour applied to this repository: your documents stay yours,
and everything OKFM generates lands in one folder you can delete.

| Level | Raw material | Its OKF | What OKFM needs from you |
|---|---|---|---|
| 1 — view | [`level-1-view/`](level-1-view) | [`.okfm/level-1/`](../../.okfm/level-1/index.md) | a browser |
| 2 — build | [`level-2-build/`](level-2-build) | [`.okfm/level-2/`](../../.okfm/level-2/index.md) | Python 3.13 |
| 3 — enrichment | [`level-3-enrich/`](level-3-enrich) | [`.okfm/level-3/`](../../.okfm/level-3/index.md) | an agent you already use |
| 4 — the suite | [`level-4-suite/`](level-4-suite) | [`.okfm/level-4/`](../../.okfm/level-4/index.md) | an API key |

Every level includes the ones below it. Stop wherever the value stops being worth the cost.

## What the concepts add that these documents do not

Each document here explains one component. The concept beside it in `.okfm/` records three
things the document never states about itself: which level it belongs to, what it needs to run
(`okfm_needs`), and a hash of the document as it stood when the concept was written.

The first two are what the level ladder is actually made of.
[`dev/check_levels.py`](../../dev/check_levels.py) fails the build when a component's needs
exceed what its level allows, so *"level 2 never needs a model"* is a checked property rather
than a promise. The third is drift: edit a document here and its concept is flagged until
somebody rereads both.

## Where the components themselves live

`okfm-viewer.html`, `dropin/`, and `templates/AGENTS.md` stay where they are. The concepts
point at them and pin their hashes too, so changing the code marks the documentation drifted —
the same machinery an adopter gets, aimed at this repository.
