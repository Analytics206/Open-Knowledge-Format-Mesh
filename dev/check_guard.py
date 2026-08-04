#!/usr/bin/env python3
"""The tier guard enforces the table it documents, and refuses to pass when it checked nothing.

    python dev/check_guard.py

## Why this exists

`guard.py` is the only thing standing between an enrichment pass and the fields DR-0008 says
a model may not write. [DR-0020](../docs/decisions/0020-the-console-edits-concepts.md) leaned
on it explicitly when the console's edit surface was widened to include `status` and
`okfm_relations`: *"the guard's purpose is intact — it distinguishes an agent writing
`verified` from a person doing it."*

Nothing checked that. `dev/check_commands.py` asserted `guard` is a command that answers
`--help`, and `dev/check_levels.py` asserted it declares `needs: []`. Neither ran it against a
single edit. The one component whose entire job is enforcement was the one nothing enforced.

Four defects were live, three of them from reading `git diff` text as though a line starting
`+status:` meant a field had changed:

  * **`guard --allow verified` exited 0 having examined nothing.** The space-separated
    spelling — which is how `revalidate --by human:you` works, so it is the one people
    reach for — parsed `verified` as a *path*, scoped the diff to a file that does not
    exist, and printed "No markdown changes to check" while an agent-written `verified`
    sat in the tree. A reassuring message over a check that did not run.
  * **A protected key inside a fenced code block in a body was flagged.** Every document
    here that shows an example concept in a ```` ```yaml ```` block tripped it, so writing
    documentation taught people to reach for `--allow` — the exact habit this guard cannot
    survive.
  * **A deleted file's fields were blamed on another file.** git writes `+++ /dev/null` for a
    deletion, which never matches `+++ b/`, so lines kept being attributed to the previous
    file. Deleting one concept reported four violations against an innocent neighbour.
  * **`sources` was named as protected in DR-0008 and in `guard.py`'s own docstring, and was
    absent from the table.** A pass could repoint a concept at a different document and
    nothing said anything.

Every case below is run against a real git repository in a temporary directory, because a
guard is a thing you can only test by giving it a diff. `needs: []`.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

CONCEPT = """---
type: Document
title: {title}
description: "A concept that exists to be edited badly."
status: draft
tags: [needs-nothing]
generated: {{ by: "{by}", at: 2026-08-01T00:00:00Z }}
sources:
  - id: subject
    resource: ./source.txt
    okfm_role: subject
    okfm_captured: {{ hash: "sha256:{h}", at: 2026-08-01 }}
okfm_scope: project
---

# Body

Some prose that a model may rewrite.
"""


def git(project: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=project, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def guard(project: Path, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(project / "dropin" / "guard.py"), *args],
                       cwd=project, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=120)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def sandbox(root: Path) -> Path:
    root.mkdir(parents=True)
    shutil.copytree(PROJECT / "dropin", root / "dropin",
                    ignore=shutil.ignore_patterns("__pycache__", ".okfm-cache"))
    (root / "okfm.json").write_text('{"okfm":"0.2.1","bundles":{"notes":"./notes"}}',
                                    encoding="utf-8", newline="\n")
    notes = root / "notes"
    notes.mkdir()
    (notes / "source.txt").write_text("source\n", encoding="utf-8", newline="\n")
    (notes / "other.txt").write_text("another\n", encoding="utf-8", newline="\n")
    for name in ("alpha", "beta", "gamma"):
        (notes / f"{name}.md").write_text(
            CONCEPT.format(title=name.title(), by="agent:someone", h="0" * 64),
            encoding="utf-8", newline="\n")
    # One concept the deterministic build owns, for the exemption cases.
    (notes / "built.md").write_text(
        CONCEPT.format(title="Built", by="process:okfm-build", h="1" * 64),
        encoding="utf-8", newline="\n")
    git(root, "init", "-q")
    git(root, "config", "user.email", "check@okfm.local")
    git(root, "config", "user.name", "check")
    git(root, "config", "commit.gpgsign", "false")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "base")
    return root


def edit(p: Path, *pairs: tuple[str, str]) -> None:
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in t:
            raise AssertionError(f"fixture anchor missing in {p.name}: {old!r}")
        t = t.replace(old, new, 1)
    p.write_text(t, encoding="utf-8", newline="\n")


STAMP = ("at: 2026-08-01T00:00:00Z", "at: 2026-08-09T00:00:00Z")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        p = sandbox(Path(tmp) / "proj")
        n = p / "notes"

        # Each case: a mutation, then what the guard must do about it. `flagged` is whether it
        # must fail; `needle` is a word the message has to contain, so a case cannot pass by
        # failing for an unrelated reason.
        cases = [
            ("an agent writes `verified` on an existing concept",
             lambda: edit(n / "alpha.md", ("status: draft",
                                           'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }')),
             (), True, "verified"),
            ("an agent promotes a concept out of draft",
             lambda: edit(n / "alpha.md", ("status: draft", "status: stable")),
             (), True, "status"),
            ("an agent invents a typed edge",
             lambda: edit(n / "alpha.md", ("okfm_scope: project",
                                           "okfm_scope: project\nokfm_relations:\n"
                                           "  - { predicate: part_of, target: /notes/beta.md }")),
             (), True, "okfm_relations"),
            ("an agent repoints `sources` at a different document",
             lambda: edit(n / "alpha.md", ("resource: ./source.txt", "resource: ./other.txt")),
             (), True, "sources"),
            ("an agent refreshes a capture on a concept the build does not own",
             lambda: edit(n / "alpha.md", ('hash: "sha256:' + "0" * 64,
                                           'hash: "sha256:' + "a" * 64)),
             (), True, "okfm_captured"),
            ("a model rewrites `description` and forgets to restamp `generated`",
             lambda: edit(n / "alpha.md", ('description: "A concept that exists to be edited badly."',
                                           'description: "Reworded."')),
             (), True, "generated"),
            ("a model rewrites `description` and restamps `generated`",
             lambda: edit(n / "alpha.md",
                          ('description: "A concept that exists to be edited badly."',
                           'description: "Reworded."'), STAMP),
             (), False, "OK"),
            ("a model rewrites prose and tags only",
             lambda: edit(n / "alpha.md", ("Some prose that a model may rewrite.", "New prose."),
                          ("tags: [needs-nothing]", "tags: [needs-nothing, reviewed]"), STAMP),
             (), False, "OK"),
            # --- the false positives that teach people to reach for --allow ---
            ("a protected key inside a ```yaml block in a BODY",
             lambda: (n / "beta.md").write_text(
                 (n / "beta.md").read_text(encoding="utf-8")
                 + '\n# Example\n\n```yaml\nstatus: stable\nverified: { by: "human:x", '
                   'at: 2026-01-01T00:00:00Z }\nsources:\n  - id: x\n```\n',
                 encoding="utf-8", newline="\n"),
             (), False, "OK"),
            ("deleting one concept while another has a legitimate edit",
             lambda: ((n / "gamma.md").unlink(),
                      edit(n / "alpha.md",
                           ('description: "A concept that exists to be edited badly."',
                            'description: "Reworded."'), STAMP)),
             (), False, "deleted, not checked"),
            # --- the build exemption, and its limit ---
            ("the build repins a capture on a concept it owns",
             lambda: edit(n / "built.md", ('hash: "sha256:' + "1" * 64,
                                           'hash: "sha256:' + "b" * 64)),
             (), False, "re-pinned by the build"),
            ("`verified` added to a build-stamped concept — the exemption must not cover it",
             lambda: edit(n / "built.md", ("status: draft",
                                           'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }')),
             (), True, "verified"),
            # --- new files ---
            ("a new concept born carrying `verified`",
             lambda: (n / "born.md").write_text(
                 CONCEPT.format(title="Born", by="agent:x", h="2" * 64)
                 .replace("status: draft",
                          'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }'),
                 encoding="utf-8", newline="\n"),
             (), True, "verified"),
            ("a new concept that starts as a draft",
             lambda: (n / "born.md").write_text(
                 CONCEPT.format(title="Born", by="agent:x", h="2" * 64),
                 encoding="utf-8", newline="\n"),
             (), False, "OK"),
            # --- the flags ---
            ("a real violation, waived with --allow=verified",
             lambda: edit(n / "alpha.md", ("status: draft",
                                           'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }')),
             ("--allow=verified",), False, "allowed by flag"),
            ("a real violation, waived with `--allow verified` (space, not =)",
             lambda: edit(n / "alpha.md", ("status: draft",
                                           'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }')),
             ("--allow", "verified"), False, "allowed by flag"),
        ]

        for label, mutate, args, must_flag, needle in cases:
            git(p, "checkout", "--", ".")
            for stray in ("born.md",):
                (n / stray).unlink(missing_ok=True)
            mutate()
            code, out = guard(p, *args)
            flagged = code != 0
            if flagged != must_flag:
                problems.append(f"{label} → guard {'FLAGGED' if flagged else 'passed'}, "
                                f"expected {'a failure' if must_flag else 'a pass'}"
                                f"  [{out.strip()[-220:]}]")
            elif needle not in out:
                problems.append(f"{label} → right verdict, but the message never says "
                                f"{needle!r}: {out.strip()[-220:]}")
        git(p, "checkout", "--", ".")
        (n / "born.md").unlink(missing_ok=True)
        if not problems:
            print(f"  ok  {len(cases)} edits each get the verdict DR-0008's table calls for")

        # --- a check that examined nothing must not report success ------------
        # The worst of the four, because it is silent and the message is reassuring. Kept
        # separate from the table: what is asserted is not a verdict but a REFUSAL to reach
        # one, and conflating those is how the bug survived in the first place.
        edit(n / "alpha.md", ("status: draft",
                              'status: draft\nverified: { by: "agent:x", at: 2026-08-09T00:00:00Z }'))
        vacuous = []
        for args in (("notes/does-not-exist.md",), ("no/such/dir/",), ("verified",)):
            code, out = guard(p, *args)
            if code == 0:
                vacuous.append(f"{' '.join(args)} → exit 0: {out.strip()[:110]}")
        git(p, "checkout", "--", ".")
        if vacuous:
            problems.append(f"the guard reported success for paths matching nothing tracked, "
                            f"with a real violation in the tree: {'; '.join(vacuous)}")
        else:
            print("  ok  a path matching nothing tracked is an error, not a clean pass")

        # --- and --allow cannot name a field nothing protects -----------------
        code, out = guard(p, "--allow=verifed")
        if code == 0:
            problems.append("--allow accepted `verifed` — a misspelling silently waives "
                            "nothing while looking like it waived something")
        else:
            print("  ok  --allow refuses a field this guard does not protect")

    print()
    for x in problems:
        print(f"  FAIL  {x}")
    print("OK — the guard enforces the table it documents"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
