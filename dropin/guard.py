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

**Build output is not an edit pass.** A concept the deterministic build regenerated because
its source changed carries a fresh `okfm_captured` in the diff, and flagging that made every
routine rebuild look like a violation — which teaches people to pass `--allow=okfm_captured`
as a matter of routine, and a guard people learn to pass is worse than no guard.

The exemption is deliberately **one key on one kind of file**, not a skip. `okfm_captured` is
the only field a rebuild churns for reasons that have nothing to do with a pass; `verified`,
`status`, `title`, `type` and `okfm_relations` are checked on build output exactly as
anywhere else. A whole-file skip would have meant a `verified` entry added to a build-stamped
concept sailing through, which is the single thing this file exists to catch.

What it cannot do is tell a rebuilt `description` from a drafted one — on a build-owned
concept those are the same bytes. That is what `guard <paths>` is for: scope the check to
what the pass touched, and the ambiguity does not arise.
"""
import re
import subprocess
import sys
from pathlib import Path

from okfm_core import PROJECT, frontmatter, scalar, utf8_stdout

utf8_stdout()

BUILD = "process:okfm-build"

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
#
# So the requirement is checked rather than stated: change a field a [model] pass owns and
# leave `generated` alone, and that is the failure. It was named here for a long time and
# enforced nowhere, which made it a comment about a rule instead of a rule.
MUST_UPDATE = ("generated",)
MODEL_OWNED = ("description", "tags", "okfm_reason_codes")
NO_RESTAMP = ("a field a [model] pass owns changed and `generated` did not — the next "
              "`bootstrap --refresh` decides what it may recompute by reading that field, "
              "and will silently clobber this")

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


def is_build_output(path: str) -> bool:
    """Does the file, as it now stands, say the deterministic build wrote it?

    Read from disk rather than from the diff: the build only restamps `generated.at` when the
    day changes, so a rebuild on the same day rewrites `okfm_captured` and leaves `generated`
    out of the diff entirely. There would be nothing to match on.

    `verified` disqualifies a file regardless of the stamp, matching `build._owned()` exactly.
    The build refuses to overwrite a verified concept, so one carrying both a `verified` entry
    and a build stamp is not the build's any more — and the two functions answering the same
    question differently is how an exemption becomes a hole.
    """
    f = PROJECT / path
    if not f.is_file():
        return False
    block, _ = frontmatter(f)
    if not block or re.search(r"^verified:", block, re.M):
        return False
    return BUILD in (scalar(block, "generated") or "")


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
    changed_keys: dict[str, set[str]] = {}

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
        changed_keys.setdefault(current, set()).add(key)

        if current in created:
            if key in CREATED_PROTECTED and key not in allowed:
                if key != "status" or value.strip("\"'") != "draft":
                    violations.append((current, key, "written on a new file",
                                       CREATED_PROTECTED[key]))
            continue

        # A protected key changed anywhere in a concept's frontmatter region. Indent is
        # allowed to be non-zero: okfm_captured is nested inside a sources entry.
        if key in PROTECTED and key not in allowed:
            violations.append((current, key, "changed", PROTECTED[key]))

    rebuilt = {p for p in files_touched - created if is_build_output(p)}

    # A field a [model] pass owns changed and the stamp did not. Skipped on build output,
    # where a rebuilt description and a drafted one are the same bytes and the tool would be
    # guessing — `guard <paths>` is the answer to that, not a heuristic.
    for path in sorted(files_touched - created - rebuilt):
        keys = changed_keys.get(path, set())
        if keys & set(MODEL_OWNED) and not keys & set(MUST_UPDATE) \
                and not allowed & set(MUST_UPDATE):
            violations.append((path, "generated", "not updated", NO_RESTAMP))

    # The exemption, and all of it: one key, on files the build still owns. Everything else
    # protected is checked on build output exactly as it is anywhere else.
    exempt = sum(1 for path, key, *_ in violations
                 if key == "okfm_captured" and path in rebuilt)
    violations = [v for v in violations
                  if not (v[1] == "okfm_captured" and v[0] in rebuilt)]

    changed = len(files_touched) - len(created)
    print(f"{changed} markdown file(s) changed, {len(created)} created"
          + (" (staged)" if staged else " (working tree)"))
    if exempt:
        # Counted rather than dropped in silence: an exemption nobody can see is one nobody
        # can question, and this one runs on every rebuild.
        print(f"{exempt} re-pinned by the build, not counted")
    if allowed:
        print(f"allowed by flag: {', '.join(sorted(allowed))}")
    print()

    if not violations:
        print("OK — only fields a [model] pass owns were changed")
        return 0

    seen = set()
    for path, key, verb, why in violations:
        if (path, key) in seen:
            continue
        seen.add((path, key))
        print(f"  FAIL  {path}")
        print(f"        `{key}` {verb} — {why}")

    print(f"\n{len(seen)} field(s) flagged.")
    print("If a person made this edit deliberately, re-run with "
          "--allow=" + ",".join(sorted({k for _, k, _, _ in violations})))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
