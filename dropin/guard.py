#!/usr/bin/env python3
"""Check that an edit pass wrote only what it owns — Level 3's enforcement.

    python okfm/okfm.py guard                    # check the working tree against HEAD
    python okfm/okfm.py guard --staged           # check what is staged
    python okfm/okfm.py guard .okfm/level-3/     # check only what the pass touched

DR-0008 says a `[model]` component may write `description`, `tags`, prose, and reason
codes — and may not write `verified`, `okfm_relations`, `status`, `type`, `title`,
`sources`, or `okfm_captured`. Until now that was a rule in a document.

This enforces it, which is what makes the human gate real rather than trusted. An agent that
adds a `verified` entry it did not earn fails here, and the failure names the field.

`needs: []` — it reads git and frontmatter. No model, no network, no secrets.

## It compares frontmatter, not diff text

For each changed file it takes the concept's frontmatter **before** and **after** and compares
them key by key, using `concept_edit.split_frontmatter` — the same function the console edits
through, so the guard and the editor cannot disagree about what a top-level key is.

That is a rewrite, and each of the three bugs it fixes came from reading `git diff` output as
though a line beginning `+status:` meant a field had changed.

**A protected key inside a fenced code block in a *body* was flagged.** The old parser tracked
whether it was inside frontmatter and then never consulted the answer — and it could not have,
because `--unified=0` emits no context lines, so the `---` boundaries are almost never in the
diff to be seen. Every document in this repository that shows an example concept in a
```` ```yaml ```` block tripped it. A guard that fires on writing documentation is a guard
people learn to pass with `--allow`, which is the one failure this file cannot afford.

**A deleted file's fields were blamed on another file.** git writes `+++ /dev/null` for a
deletion, which does not match `+++ b/`, so the parser kept attributing lines to whichever
file came before it. Deleting one concept reported four violations against an innocent
neighbour, and the summary line miscounted the files.

**A deleted concept is not checked at all, and says so.** There is no trust to be gained by a
file that no longer exists, and pretending to check it would be the same lie in the other
direction.

## What it cannot do

Tell an agent's edit from a person's. Git records that a line changed, not who decided to
change it. So `guard` is a check you run **after an enrichment pass**, and a person editing
their own concept will trip it — correctly, because the tool cannot know they are allowed
to. `--allow` names fields to permit for a run where a human is the author.

A **new** file is judged on whether it arrives already trusted, not on the full protected
list — see `CREATED_PROTECTED`.

**Build output is not an edit pass.** A concept the deterministic build regenerated because
its source changed carries a fresh `okfm_captured`, and flagging that made every routine
rebuild look like a violation — which teaches people to pass `--allow=okfm_captured` as a
matter of routine, and a guard people learn to pass is worse than no guard.

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

from concept_edit import split_frontmatter
from okfm_core import FM, PROJECT, reject_unknown, scalar, utf8_stdout

utf8_stdout()

BUILD = "process:okfm-build"

# Frontmatter keys a [model] pass must not touch (DR-0008's ownership table).
PROTECTED = {
    "verified": "trust is a human act — the backfill honesty rule (§16)",
    "okfm_relations": "typed edges are never inferred; traversal reads them as fact",
    "status": "promotion out of draft is a human decision",
    "type": "drives everything downstream",
    "title": "drives everything downstream",
    # Named in DR-0008 and in this file's own docstring for a long time, and absent from this
    # table the whole time — so a pass could repoint a concept at a different document and
    # nothing said anything. Compared with the captures inside it blinded, because those have
    # their own rule and their own exemption directly below.
    "sources": "what a concept is about — repointing it rewrites what the concept means",
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

_CAPTURE = re.compile(r"okfm_captured:\s*\{[^}]*\}")


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=PROJECT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def changed(staged: bool, paths: list[str]) -> list[tuple[str, str]]:
    """`(status, path)` per changed markdown file. `--no-renames` so a move reads as D then A,
    which is what it is for this purpose: one concept stops existing and another starts.

    **Untracked files count as created.** `git diff` compares the index against the working
    tree, and a file that has never been added is in neither — so in the default mode a
    brand-new concept was invisible, and `CREATED_PROTECTED` only ever ran under `--staged`.
    That is the whole case it exists for: a pass that *authors* a concept already carrying
    `verified` has claimed a review that did not happen, and it sailed through unless somebody
    happened to stage it first.
    """
    args = ["diff", "--name-status", "--no-renames"] + (["--cached"] if staged else [])
    out = _git(*args, "--", *(paths or ["*.md"])).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[-1].endswith(".md"):
            rows.append((parts[0][:1], parts[-1]))
    if not staged:
        others = _git("ls-files", "--others", "--exclude-standard", "--",
                      *(paths or ["*.md"])).stdout
        rows += [("A", f) for f in others.splitlines() if f.endswith(".md")]
    return rows


def tracks_anything(paths: list[str]) -> bool:
    """Whether the named paths match any file git knows about, tracked or merely present.

    Without this, `guard --allow verified` — the space-separated spelling, which is how
    `revalidate --by human:you` works and therefore the one people reach for — parsed
    `verified` as a **path**, scoped the diff to a file that does not exist, printed
    "No markdown changes to check" and exited 0 while an agent-written `verified` sat in the
    tree. A guard that examines nothing must not report success.
    """
    return not paths or bool(
        _git("ls-files", "--cached", "--others", "--exclude-standard", "--", *paths).stdout.strip())


def side(path: str, new: bool, staged: bool) -> str | None:
    """The file's text on one side of the comparison, or None when it is not there."""
    if not new:
        r = _git("show", f"HEAD:{path}")
        return r.stdout if r.returncode == 0 else None
    if staged:
        r = _git("show", f":{path}")
        return r.stdout if r.returncode == 0 else None
    f = PROJECT / path
    return f.read_text(encoding="utf-8") if f.is_file() else None


def block_of(text: str | None) -> str:
    m = FM.match(text or "")
    return m.group(1) if m else ""


def keys(text: str | None) -> dict[str, str]:
    """Top-level frontmatter keys to their exact text.

    `split_frontmatter` is `concept_edit`'s on purpose. The guard and the editor disagreeing
    about what counts as a top-level key would mean a field the console can write and the
    guard cannot see, which is the shape every hole in this file has had.
    """
    return {e["key"]: e["raw"] for e in split_frontmatter(block_of(text))}


def captures(text: str | None) -> list[str]:
    """Every `okfm_captured` mapping, in file order.

    Compared separately from `sources` because it is nested inside it and is the only
    protected field that is not top-level — and because it is the one field with an exemption.
    """
    return _CAPTURE.findall(block_of(text))


def is_build_output(text: str | None) -> bool:
    """Does the file, as it now stands, say the deterministic build wrote it?

    `verified` disqualifies it regardless of the stamp, matching `build._owned()` exactly. The
    build refuses to overwrite a verified concept, so one carrying both a `verified` entry and
    a build stamp is not the build's any more — and two functions answering the same question
    differently is how an exemption becomes a hole.
    """
    block = block_of(text)
    if not block or re.search(r"^verified:", block, re.M):
        return False
    return BUILD in (scalar(block, "generated") or "")


def main() -> int:
    argv = sys.argv[1:]
    reject_unknown(argv, ("--staged", "--allow"), __doc__)
    staged = "--staged" in argv
    allowed: set[str] = set()
    paths: list[str] = []
    skip = False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a.startswith("--allow="):
            allowed |= {x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()}
        elif a == "--allow":
            # Both spellings, because the other commands take `--by human:you` with a space
            # and the mismatch turned a field name into a path. See `tracks_anything`.
            if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                allowed |= {x.strip() for x in argv[i + 1].split(",") if x.strip()}
                skip = True
            else:
                print("error: --allow needs field names, e.g. --allow=verified,status",
                      file=sys.stderr)
                return 2
        elif not a.startswith("--"):
            # Naming paths scopes the check to the pass you are actually checking.
            # Without it the diff is "everything uncommitted", which mixes an enrichment
            # pass with whatever structural work happened to be in flight — and a guard
            # that fires on unrelated edits is a guard people learn to pass with --allow.
            paths.append(a)

    unknown = allowed - set(PROTECTED) - set(MUST_UPDATE) - set(CREATED_PROTECTED)
    if unknown:
        # An --allow naming a field nothing protects is either a typo or a belief about this
        # tool that is wrong. Both are worth interrupting for; neither should quietly widen
        # nothing while looking like it widened something.
        print(f"error: --allow names {', '.join(sorted(unknown))}, which this guard does not "
              f"protect", file=sys.stderr)
        print(f"       it protects: {', '.join(sorted(set(PROTECTED) | set(MUST_UPDATE)))}",
              file=sys.stderr)
        return 2

    if not tracks_anything(paths):
        print(f"error: nothing tracked matches {', '.join(paths)}", file=sys.stderr)
        print("       a guard that examined nothing must not report success", file=sys.stderr)
        return 2

    rows = changed(staged, paths)
    where = " (staged)" if staged else " (working tree)"
    if not rows:
        print(f"No markdown changes to check{where}")
        return 0

    created = [p for s, p in rows if s == "A"]
    removed = [p for s, p in rows if s == "D"]
    modified = [p for s, p in rows if s not in ("A", "D")]

    violations: list[tuple[str, str, str, str]] = []
    exempt = 0

    for path in created:
        new = keys(side(path, True, staged))
        for key, why in CREATED_PROTECTED.items():
            if key in allowed or key not in new:
                continue
            value = new[key].split(":", 1)[1].strip().strip("\"'")
            if key == "status" and value == "draft":
                continue
            violations.append((path, key, "written on a new file", why))

    for path in modified:
        old_t, new_t = side(path, False, staged), side(path, True, staged)
        old, new = keys(old_t), keys(new_t)
        if not old and not new:
            continue                        # not a concept on either side
        rebuilt = is_build_output(new_t)

        moved = set()
        for key in set(old) | set(new):
            a, b = old.get(key), new.get(key)
            if key == "sources":
                # The captures inside have their own rule and their own exemption; comparing
                # them here as well would report a routine rebuild as a repointed source.
                a, b = _CAPTURE.sub("<capture>", a or ""), _CAPTURE.sub("<capture>", b or "")
            if a != b:
                moved.add(key)

        for key in sorted(moved & set(PROTECTED)):
            if key not in allowed:
                violations.append((path, key, "changed", PROTECTED[key]))

        if captures(old_t) != captures(new_t) and "okfm_captured" not in allowed:
            if rebuilt:
                exempt += 1
            else:
                violations.append((path, "okfm_captured", "changed",
                                   PROTECTED["okfm_captured"]))

        # A field a [model] pass owns changed and the stamp did not. Skipped on build output,
        # where a rebuilt description and a drafted one are the same bytes and the tool would
        # be guessing — `guard <paths>` is the answer to that, not a heuristic.
        if not rebuilt and moved & set(MODEL_OWNED) and not moved & set(MUST_UPDATE) \
                and not allowed & set(MUST_UPDATE):
            violations.append((path, "generated", "not updated", NO_RESTAMP))

    print(f"{len(modified)} markdown file(s) changed, {len(created)} created, "
          f"{len(removed)} deleted{where}")
    if removed:
        # Named rather than passed over. A deleted concept cannot gain trust, so there is
        # nothing here to enforce — but a check that declines to look at something has to say
        # so, or a silent skip and a clean pass are the same green tick.
        print(f"{len(removed)} deleted, not checked — a concept that no longer exists "
              f"cannot have gained trust")
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
