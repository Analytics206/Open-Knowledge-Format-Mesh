#!/usr/bin/env python3
"""Check that an edit pass wrote only what it owns — Level 3's enforcement.

    python okfm/okfm.py guard                    # check the working tree against HEAD
    python okfm/okfm.py guard --staged           # check what is staged
    python okfm/okfm.py guard .okfm/level-3/     # check only what the pass touched

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

A **new** file is judged on whether it arrives already trusted, not on the full protected
list — see `CREATED_PROTECTED`.
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

# A NEW file is judged by a different rule, because on a new file every field is an
# addition and the protected list would report all of them as "changed" — four misleading
# failures every time somebody authors a decision record, which teaches people to reach for
# `--allow` as a matter of routine. A guard that cries wolf on the normal case is worse than
# no guard.
#
# What actually matters on creation is whether the concept arrives carrying trust nobody
# granted it. `type`, `title`, `sources` and `okfm_captured` on a file that did not exist a
# moment ago are authorship, not overwriting; there is no prior value to destroy and no drift
# signal to erase. `verified` and a promoted `status` are different in kind — those are the
# human gate, and a pass that writes them has claimed a review that did not happen (§16).
CREATED_PROTECTED = {
    "verified": "a concept cannot be born verified — trust is a human act (§16)",
    "status": "a new concept starts `draft`; promotion is a separate human decision",
}

_FM_BOUND = re.compile(r"^[+-]---\s*$")
_KEY = re.compile(r"^[+-](\s*)([\w_]+):[ \t]*(.*)$")


def diff(staged: bool, paths: list[str]) -> str:
    args = ["git", "diff", "--unified=0"] + (["--cached"] if staged else [])
    args += ["--", *(paths or ["*.md"])]
    return subprocess.run(args, cwd=PROJECT, capture_output=True, text=True,
                          encoding="utf-8").stdout


def main() -> int:
    argv = sys.argv[1:]
    staged = "--staged" in argv
    allowed, paths = set(), []
    for a in argv:
        if a.startswith("--allow="):
            allowed |= {x.strip() for x in a.split("=", 1)[1].split(",")}
        elif not a.startswith("--"):
            # Naming paths scopes the check to the pass you are actually checking.
            # Without it the diff is "everything uncommitted", which mixes an enrichment
            # pass with whatever structural work happened to be in flight — and a guard
            # that fires on unrelated edits is a guard people learn to pass with --allow.
            paths.append(a)

    text = diff(staged, paths)
    if not text.strip():
        print("No markdown changes to check"
              + (" (staged)" if staged else " (working tree)"))
        return 0

    violations, current, in_fm = [], None, False
    files_touched, created, is_new = set(), set(), False

    for line in text.splitlines():
        if line.startswith("--- "):
            # git writes `--- /dev/null` for an added file, immediately before its `+++`.
            is_new = line.strip() == "--- /dev/null"
            continue
        if line.startswith("+++ b/"):
            current = line[6:]
            files_touched.add(current)
            if is_new:
                created.add(current)
            is_new = in_fm = False
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
        indent, key, value = m.group(1), m.group(2), m.group(3).strip()

        if current in created:
            if key in CREATED_PROTECTED and key not in allowed:
                if key != "status" or value.strip("\"'") != "draft":
                    violations.append((current, key, CREATED_PROTECTED[key]))
            continue

        # A protected key changed anywhere in a concept's frontmatter region. Indent is
        # allowed to be non-zero: okfm_captured is nested inside a sources entry.
        if key in PROTECTED and key not in allowed:
            violations.append((current, key, PROTECTED[key]))

    changed = len(files_touched) - len(created)
    print(f"{changed} markdown file(s) changed, {len(created)} created"
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
        verb = "written on a new file" if path in created else "changed"
        print(f"  FAIL  {path}")
        print(f"        `{key}` {verb} — {why}")

    print(f"\n{len(seen)} protected field(s) flagged.")
    print("If a person made this edit deliberately, re-run with "
          "--allow=" + ",".join(sorted({k for _, k, _ in violations})))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
