#!/usr/bin/env python3
"""What an agent would actually be handed.

    python okfm/okfm.py index              # the context, as an agent gets it
    python okfm/okfm.py index --json       # the same, machine-readable
    python okfm/okfm.py index --check      # would it fit the budget? writes nothing

`validate` tells you whether a bundle is legal. **This tells you whether it is useful**,
which is usually the more interesting answer — a mesh can be perfectly conformant and still
hand an agent sixty descriptions that say nothing, or hand it the wrong sixty.

## Why this exists

It was documented before it was written. `okfm index` appears four times across the guide,
the README and §13.7 — including in `first-concept.md`, which is the page a first-time
author reads — and running it printed `unknown command`. The config carried the knobs for it
the whole time: `read.index.max_concepts` and `read.index.priority_types` were synthesized
into every adopter's config on their first build and read by nothing at all, and so was
`read.exclude_scopes`. That is the third config key this project has found in that state.

A knob that adjusts nothing is worse than a missing feature. The adopter tunes it, sees no
change, and concludes the tool is broken in some way they cannot see — which it was.

## What ordering means here

Injection is a budget problem. An agent gets a finite context, so the question is not *what
is in the mesh* but *what survives the cut*, and the cut has to be explicable:

  the mesh first    it is the map. Handing an agent concepts without the routing layer is
                    handing it a pile, and `okfm_member.answers` is what turns "where do I
                    read about X" into a path instead of a search.
  priority_types    in the order the config lists them. A domain says which types carry its
                    load — `Attested Computation` before `Document`.
  everything else   by bundle, then path, so two runs agree.

**Nothing is dropped silently.** What the budget cut is printed with its types, because a
truncated index that looks complete is how an agent ends up confidently answering from
half a mesh. That rule is the project's own and it is the reason this prints a tail.

`needs: []` — reads files, sorts, prints.
"""
import json
import sys
from pathlib import Path

from okfm_core import (PROJECT, RESERVED, configured_bundles, frontmatter,
                       load_or_create_config, reject_unknown, scalar, trust, utf8_stdout)

utf8_stdout()

# Concepts an agent is handed, when the config says nothing. Sixty is what `synthesize_config`
# has always written; it is a starting point, not a measurement.
DEFAULT_BUDGET = 60


def concepts(cfg: dict) -> list[dict]:
    """Every concept in the mesh, with the fields injection actually uses."""
    out = []
    for bid, root in sorted(configured_bundles(cfg).items()):
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            block, _ = frontmatter(f)
            if not block:
                continue
            ctype = scalar(block, "type")
            if not ctype:
                continue
            rel = f.relative_to(root).as_posix()
            out.append({
                "path": f"/{bid}/{rel}",
                "bundle": bid,
                "type": ctype,
                "title": scalar(block, "title") or f.stem,
                "description": scalar(block, "description") or "",
                "status": scalar(block, "status") or "draft",
                "scope": scalar(block, "okfm_scope"),
                "trust": trust(block),
                "stale_after": scalar(block, "stale_after"),
                "reserved": f.name in RESERVED,
            })
    return out


def rank(cfg: dict, items: list[dict]) -> list[dict]:
    """Mesh first, then `priority_types` in the order given, then the rest."""
    mesh = cfg.get("mesh", "mesh")
    priority = list((cfg.get("index") or {}).get("priority_types") or [])
    order = {t: i for i, t in enumerate(priority)}
    return sorted(items, key=lambda c: (
        0 if c["bundle"] == mesh else 1,
        order.get(c["type"], len(order)),
        c["bundle"],
        c["path"],
    ))


def main() -> int:
    argv = sys.argv[1:]
    reject_unknown(argv, ("--json", "--check"), __doc__)

    _, cfg, _ = load_or_create_config(write=False)
    items = concepts(cfg)
    if not items:
        print("No concepts found. Run the build first, or point `bundles` at one.")
        return 0

    # `okfm_scope` is how a bundle says what it is FOR. The shipped guide is teaching
    # material about OKFM, not knowledge about the adopter's project, so the default config
    # excludes it — otherwise every adopter's agent is handed ten concepts explaining a
    # format instead of ten explaining their own system.
    dropped_scope = list((cfg.get("exclude_scopes") or []))
    scoped_out = [c for c in items if c["scope"] in dropped_scope]
    kept = [c for c in items if c["scope"] not in dropped_scope]

    budget = int((cfg.get("index") or {}).get("max_concepts") or DEFAULT_BUDGET)
    ranked = rank(cfg, kept)
    shown, cut = ranked[:budget], ranked[budget:]

    if "--json" in argv:
        print(json.dumps({"budget": budget, "shown": len(shown), "cut": len(cut),
                          "excluded_scopes": dropped_scope, "concepts": shown},
                         indent=2, ensure_ascii=False))
        return 0

    print(f"budget  : {budget} concepts  (read.index.max_concepts)")
    print(f"mesh    : {len(items)} concept(s) across {len(configured_bundles(cfg))} bundles")
    if scoped_out:
        by = sorted({c["scope"] for c in scoped_out})
        print(f"excluded: {len(scoped_out)} in scope {', '.join(by)}  (read.exclude_scopes)")
    print()

    width = max(len(c["path"]) for c in shown)
    bundle = None
    for c in shown:
        if c["bundle"] != bundle:
            bundle = c["bundle"]
            print(f"── {bundle} ".ljust(width + 22, "─"))
        # The three signals a reader weighs before relying on a concept, exactly as the
        # authoring contract lists them. Shown rather than resolved into a verdict: a
        # verdict is the one thing this format never stores, and printing one here would
        # be storing it in an agent's context instead of in a file.
        marks = []
        if c["trust"] == "human":
            marks.append("✓human")
        elif c["trust"] == "machine":
            marks.append("✓machine")
        if c["status"] != "stable":
            marks.append(c["status"])
        if c["stale_after"]:
            marks.append(f"stale_after {c['stale_after']}")
        tail = f"  [{', '.join(marks)}]" if marks else ""
        print(f"  {c['path']:<{width}}  {c['type']}{tail}")
        if c["description"]:
            print(f"  {'':<{width}}  {c['description'][:150]}")

    # Said out loud, always. An index that silently fits its budget and an index that
    # silently lost a third of the mesh look identical from the outside, and the second one
    # is how an agent answers confidently from half a corpus.
    print()
    if cut:
        types = {}
        for c in cut:
            types[c["type"]] = types.get(c["type"], 0) + 1
        listed = ", ".join(f"{n} {t}" for t, n in sorted(types.items(), key=lambda kv: -kv[1]))
        print(f"CUT BY BUDGET: {len(cut)} concept(s) did not fit — {listed}")
        print(f"  Raise `read.index.max_concepts`, or narrow the mesh. They are not")
        print(f"  unreachable — an agent following the mesh index still finds them.")
    else:
        print(f"All {len(shown)} concept(s) fit the budget — nothing was cut.")

    if "--check" in argv:
        # A budget that cuts is a decision, not an error: an adopter may well mean it.
        # Failing here would make `--check` refuse a mesh that is merely larger than its
        # injection window, which is most meshes eventually.
        print("\n(--check: nothing was written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
