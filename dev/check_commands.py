#!/usr/bin/env python3
"""Every `okfm <command>` the documentation tells someone to run must exist.

    python dev/check_commands.py

## Why

Two did not. `okfm validate` appeared six times across the specification, the README and the
guide; `okfm index` four times, including in `first-concept.md`, which is the page a
first-time author reads before writing anything. Both printed `unknown command` and exited 2.

The dispatcher answered to `check`, and nothing anywhere told a reader that. One command
with two names is a coin toss decided by which document you happened to open, and the name
the documentation gave you was the losing side of it.

`index` was worse than a naming mismatch — it did not exist in any form, while
`read.index.max_concepts`, `read.index.priority_types` and `read.exclude_scopes` were
synthesized into every adopter's config on their first build and read by nothing. A knob
that adjusts nothing is worse than a missing feature: the adopter turns it, sees no change,
and concludes the tool is broken somewhere they cannot see.

## What this checks, and the direction it does not

**Documented → dispatchable.** Every command named in prose must be one the dispatcher
knows. The reverse is deliberately *not* an error: a command that exists and is undocumented
is a gap in the writing, reported as a note, and there are legitimate ones — `okfm config`
is a pipeline stage nobody needs to invoke by name.

Names are read out of the docs rather than listed here. A list here would be a third place
to keep the same set in sync, which is the failure this file exists to catch.

`needs: []`.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DROPIN = PROJECT / "dropin"

# Where an adopter is told what to type.
SOURCES = ["README.md", "spec/*.md", "docs/**/*.md", "templates/*.md", ".okfm/**/*.md"]

# `okfm view`, `okfm.py enrich-local`, `python okfm/okfm.py revalidate` — one pattern, since
# the docs write it all three ways.
#
# `[ \t]+`, not `\s+`. `\s` matches newlines, so a fence whose first line ended in `okfm`
# and whose next began `python` reported a command called `python`.
_CMD = re.compile(r"okfm(?:\.py)?[ \t]+([a-z][a-z-]{2,})\b")

# Words that follow "okfm" in prose without being commands. Kept short on purpose: anything
# longer is this file quietly excusing a real miss.
NOT_COMMANDS = {"concepts", "bundles", "holds", "reads", "writes", "itself", "profile",
                "keys", "mesh", "own", "and", "the", "web", "json", "core", "does",
                "self", "never", "still", "drives", "installs", "holding", "runs"}


def documented() -> dict[str, list[str]]:
    """command -> the files that name it, fenced or inline.

    Both, and the rule behind that is worth stating: **the documentation must not name a
    command that does not exist, in any form.** Not in a fence, not in inline code, not in a
    sentence about what is coming later. A reader scanning for something to type does not
    distinguish an instruction from a roadmap entry, and neither can this check.

    Restricting to fences was tried and was worse. It let a real instruction through — `okfm
    view` is told to readers seven times and almost always inline, in the middle of a
    sentence — while the thing it was meant to excuse, a page describing a command that does
    not exist yet, is better fixed by describing the *capability* instead of its invocation.
    A phantom command name in prose is a promise the corpus cannot keep.
    """
    found: dict[str, list[str]] = {}
    for pattern in SOURCES:
        for f in sorted(PROJECT.glob(pattern)):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for cmd in set(_CMD.findall(text)):
                if cmd in NOT_COMMANDS:
                    continue
                found.setdefault(cmd, []).append(f.relative_to(PROJECT).as_posix())
    return found


def dispatchable() -> set[str]:
    """What `okfm.py` answers to, read from the dispatcher rather than restated."""
    src = (DROPIN / "okfm.py").read_text(encoding="utf-8")
    steps = re.findall(r'^\s*\("([a-z-]+)",\s*"[\w.]+\.py"', src, re.M)
    extra = re.findall(r'"([a-z-]+)":\s*"[\w.]+\.py"', src)
    return set(steps) | set(extra)


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    known = dispatchable()
    if not known:
        print("could not read any commands out of dropin/okfm.py", file=sys.stderr)
        return 2
    print(f"dispatcher knows: {', '.join(sorted(known))}")

    docs = documented()
    problems, notes = [], []

    for cmd, files in sorted(docs.items()):
        if cmd in known:
            continue
        problems.append(f"`okfm {cmd}` is documented in {', '.join(sorted(set(files))[:3])}"
                        + (f" (+{len(set(files)) - 3} more)" if len(set(files)) > 3 else "")
                        + " and the dispatcher does not know it")

    # Documented AND dispatchable is not yet proof it runs — a name in the table can point at
    # a script that raises on import. Cheap to rule out, so ruled out.
    for cmd in sorted(docs):
        if cmd not in known:
            continue
        r = subprocess.run([sys.executable, str(DROPIN / "okfm.py"), cmd, "--help"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=PROJECT)
        if r.returncode not in (0, 2):
            problems.append(f"`okfm {cmd} --help` exited {r.returncode} — documented, "
                            f"dispatched, and broken")
        elif "Traceback" in r.stderr:
            problems.append(f"`okfm {cmd} --help` raised on import")
        else:
            print(f"  ok  okfm {cmd}"
                  + (f"  ({len(set(docs[cmd]))} doc(s))" if docs.get(cmd) else ""))

    for cmd in sorted(known - set(docs)):
        notes.append(f"`okfm {cmd}` exists and no document mentions it")

    print()
    for n in notes:
        print(f"  note  {n}")
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — every documented command exists and runs"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
