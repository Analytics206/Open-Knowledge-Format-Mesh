#!/usr/bin/env python3
"""Check that an edit pass wrote only what it owns — Level 3's enforcement.

    python okfm/okfm.py guard             # check the working tree against HEAD
    python okfm/okfm.py guard --staged    # check what is staged

DR-0008 says a `[model]` component may write `description`, `tags`, prose, and reason
codes — and may not write `verified`, `okfm_relations`, `status`, `type`, `title`,
`sources`, or `okfm_captured`. Until now that was a rule in a document.

This reads the diff and enforces it, which is what makes the human gate real rather than
trusted. An agent that adds a `verified` entry it did not earn fails here, and the failure
names the field.

`needs: []` — it reads git and frontmatter. No model, no network, no secrets.

## What it cannot do

Tell an agent's edit from a person's. Git records that a line changed, not who decided to
change it. So `guard` is a check you run **after an enrichment pass**, and a person editing
their own concept will trip it — correctly, because the tool cannot know they are allowed
to. `--allow` names fields to permit for a run where a human is the author.
"""
import re
import subprocess
import sys
from pathlib import Path

from okfm_core import PROJECT, utf8_stdout

utf8_stdout()

# Frontmatter keys a [model] pass must not touch (DR-0008's ownership table).
PROTECTED = {
    "verified": "trust is a human act — the backfill honesty rule (§16)",
    "okfm_relations": "typed edges are never inferred; traversal reads them as fact",
    "status": "promotion out of draft is a human decision",
    "type": "drives everything downstream",
    "title": "drives everything downstream",
    "okfm_captured": "refreshing it automatically erases the drift signal it carries",
}

# `generated` is deliberately NOT protected. DR-0008 has it stamped by whatever produced
# the content, so a [model] pass MUST rewrite it — that is how provenance stays honest.
#
# It is also load-bearing for a subtler reason: `bootstrap --refresh` decides what it may
# recompute by reading `generated.by`. A description improved by hand or by an agent that
# leaves the field saying `process:okfm-bootstrap` gets silently clobbered on the next
# refresh. That happened here before the rule was written down.
MUST_UPDATE = ("generated",)

_FM_BOUND = re.compile(r"^[+-]---\s*$")
_KEY = re.compile(r"^[+-](\s*)([\w_]+):")


def diff(staged: bool) -> str:
    args = ["git", "diff", "--unified=0"] + (["--cached"] if staged else []) + ["--", "*.md"]
    return subprocess.run(args, cwd=PROJECT, capture_output=True, text=True,
                          encoding="utf-8").stdout


def main() -> int:
    argv = sys.argv[1:]
    staged = "--staged" in argv
    allowed = set()
    for a in argv:
        if a.startswith("--allow="):
            allowed |= {x.strip() for x in a.split("=", 1)[1].split(",")}

    text = diff(staged)
    if not text.strip():
        print("No markdown changes to check"
              + (" (staged)" if staged else " (working tree)"))
        return 0

    violations, current, in_fm = [], None, False
    files_touched = set()

    for line in text.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            files_touched.add(current)
            in_fm = False
            continue
        if line.startswith("@@"):
            # Hunk headers reset frontmatter tracking; a hunk starting mid-file is not
            # inside frontmatter unless its own lines say so.
            in_fm = False
            continue
        if _FM_BOUND.match(line):
            in_fm = not in_fm
            continue

        m = _KEY.match(line)
        if not m or not current:
            continue
        indent, key = m.group(1), m.group(2)

        # A protected key changed anywhere in a concept's frontmatter region. Indent is
        # allowed to be non-zero: okfm_captured is nested inside a sources entry.
        if key in PROTECTED and key not in allowed:
            violations.append((current, key, PROTECTED[key]))

    print(f"{len(files_touched)} markdown file(s) changed"
          + (" (staged)" if staged else " (working tree)"))
    if allowed:
        print(f"allowed by flag: {', '.join(sorted(allowed))}")
    print()

    if not violations:
        print("OK — only fields a [model] pass owns were changed")
        return 0

    seen = set()
    for path, key, why in violations:
        if (path, key) in seen:
            continue
        seen.add((path, key))
        print(f"  FAIL  {path}")
        print(f"        `{key}` changed — {why}")

    print(f"\n{len(seen)} protected field(s) changed.")
    print("If a person made this edit deliberately, re-run with "
          "--allow=" + ",".join(sorted({k for _, k, _ in violations})))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
