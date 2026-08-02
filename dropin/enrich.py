#!/usr/bin/env python3
"""What needs enriching, and the brief for doing it — Level 3.

    python okfm/okfm.py enrich            # the work list
    python okfm/okfm.py enrich --brief    # full instructions, one block per concept

**This does not call a model.** It is `needs: []`: it reads the drift cache and prints
work. At Level 3 the adopter's agent drives OKFM, so OKFM never holds a credential
(DR-0009) — your agent reads this, does the work, and `okfm.py guard` checks the result.

That split is what makes Level 3 need no key. The reasoning is the agent's; the work list
and the check are arithmetic.

## Why a concept lands here

Drift, and only drift. A concept whose source hashes differently than `okfm_captured`
recorded has prose that moved since its description was extracted — which is exactly the
enrichment trigger. One mechanism, two uses (DR-0008).

Never a stored `stale: true` flag. The work list is derived every time, so fixing a concept
removes it from the queue with nothing to clear.

## Drift alone is not enough to decide whose work it is

Drift says the source moved. It does not say whether anybody has responded, and `generated.by`
does: a description still owned by an extraction process has never been drafted, while one
stamped by a model or a person has.

So the queue is split. **Drafting** is the agent's; **review** is not, and only a human
revalidation clears drift. Printing both under one heading sends an agent to rewrite prose it
wrote an hour ago — and to rewrite it differently every run, because nothing in a second pass
converges. A queue that regenerates its own work looks busy and drains never.
"""
import json
import re
import sys
from pathlib import Path

from okfm_core import (
    HERE, configured_bundles, frontmatter, load_or_create_config, scalar, utf8_stdout, reject_unknown,
)

utf8_stdout()

CACHE = HERE / ".okfm-cache" / "observations.json"

# Fields a `[model]` component may write. Everything else belongs to a person or to the
# deterministic build (DR-0008).
WRITABLE = ["description", "tags", "body prose sections", "okfm_reason_codes",
            "generated.by (required — see the brief)"]
FORBIDDEN = ["verified", "okfm_relations", "status", "type", "title",
             "sources", "okfm_captured"]

_CAPTURED = re.compile(r"resource:\s*(\S+)[\s\S]*?hash:\s*\"?sha256:([0-9a-f]+)")

BRIEF = """\
── {rid}
   title       {title}
   description {desc}
   source      {uri}
   why         {why}

   Read ONLY that source. Rewrite `description` so it states what the concept now says —
   a claim, not a topic. Add `tags` if useful.

   Set `generated.by` to yourself. This is required, not optional: `bootstrap --refresh`
   decides what it may recompute by reading that field, so a description you improve
   while leaving it saying `process:okfm-bootstrap` gets silently clobbered later.

   Leave as `status: draft`. Do NOT add `verified`, touch `okfm_relations`, or edit any
   field in: {forbidden}.

   If the concept restates its source and adds nothing the source cannot say, the right
   answer is to propose deleting it. Say so instead of improving the prose.
"""


def work_list():
    _, cfg, _ = load_or_create_config(write=False)
    obs = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.is_file() else {}
    if not obs:
        return None, []

    items = []
    for bid, root in sorted(configured_bundles(cfg).items()):
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.md")):
            block, _ = frontmatter(f)
            if not block or not scalar(block, "type"):
                continue
            rid = f"{bid}/{f.relative_to(root).as_posix()}"
            for uri, captured in _CAPTURED.findall(block):
                entry = obs.get(f"{uri}@{rid}")
                if not entry:
                    continue
                if not entry["observed"].removeprefix("sha256:").startswith(captured):
                    raw = scalar(block, "generated") or ""
                    actor = re.search(r'by:\s*"?([^",}]+)', raw)
                    by = actor.group(1).strip() if actor else ""
                    drafted = bool(by) and not by.startswith("process:")
                    items.append({
                        "rid": rid,
                        "path": f,
                        "uri": uri,
                        "title": scalar(block, "title") or f.stem,
                        "desc": scalar(block, "description") or "(empty)",
                        "status": scalar(block, "status") or "stable",
                        "drafted": drafted,
                        "by": by,
                        "why": ("a draft exists and the source has moved since it was captured"
                                if drafted else
                                "source changed since the description was extracted"),
                    })
                    break
    return obs, items


def main() -> int:
    reject_unknown(sys.argv[1:], ("--brief",))
    full = "--brief" in sys.argv
    obs, items = work_list()

    if obs is None:
        print("No observations yet — run `okfm.py refresh` first.")
        return 0
    if not items:
        print("Nothing to enrich. Every observed pointer matches what its concept captured.")
        return 0

    todo = [i for i in items if not i["drafted"]]
    waiting = [i for i in items if i["drafted"]]

    if todo:
        print(f"{len(todo)} concept(s) to draft\n")
        for it in todo:
            if full:
                print(BRIEF.format(**it, forbidden=", ".join(FORBIDDEN)))
            else:
                print(f"  {it['status']:<6} {it['rid']}")
                print(f"         {it['desc'][:88]}")
        if not full:
            print("\nRun with --brief for instructions per concept.")
        print("Writable by a model: " + ", ".join(WRITABLE))
        print("After editing:  python okfm/okfm.py guard")
    else:
        print("Nothing to draft. Every drifted concept already has one.")

    if waiting:
        # Not agent work, and saying so is the point. A second drafting pass over an
        # existing draft produces different prose, not better prose, and the concept stays
        # exactly as drifted as it was.
        print(f"\n{len(waiting)} concept(s) waiting on you — a draft exists, drift stands\n")
        for it in waiting:
            print(f"  {it['status']:<6} {it['rid']}")
            print(f"         drafted by {it['by'] or 'unknown'}")
        print("\nRead the source, then clear the drift:")
        print("  python okfm/okfm.py revalidate <path> --by human:you")
        print("\nOnly a person can. Refreshing a capture automatically would erase the signal")
        print("drift exists to carry — see revalidate.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
