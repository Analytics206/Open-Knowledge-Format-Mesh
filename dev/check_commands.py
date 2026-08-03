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

# Where an adopter is told what to type. The viewer is included because it gives
# instructions too — and gave a wrong one for months precisely because this list was
# markdown-only. See FLAGS below.
SOURCES = ["README.md", "spec/*.md", "docs/**/*.md", "templates/*.md", ".okfm/**/*.md",
           "okfm-web-ui.html"]

# The viewer's three baked data blocks are a COPY of the corpus, already scanned above as
# markdown. Scanning them again would report every command quoted inside a historical
# decision record as a live instruction.
_BAKED = re.compile(r"const (?:BOOTSTRAP|CONFIG_SCHEMA|CONFIG) = \{.*?\n\};", re.S)

# `okfm view --serve` was recommended in the viewer and in two specification sections. It
# was never a flag: running it printed `unknown option: --serve` and exited 2. The command
# check passed it every time, because `view` is a real command and the phantom was the FLAG.
#
# So flags are checked too, statically, against the allow-lists the scripts declare. Running
# them to find out would be the direct test and is not worth it — half the documented
# commands write files.
FLAGS = re.compile(r"okfm(?:\.py)?[ \t]+([a-z][a-z-]{2,})[ \t]+(--[a-z][a-z-]*)")
_ALLOWED = re.compile(r"reject_unknown\([^,]+,\s*\(([^)]*)\)")

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
            if f.suffix == ".html":
                text = _BAKED.sub("", text)
            for cmd in set(_CMD.findall(text)):
                if cmd in NOT_COMMANDS:
                    continue
                found.setdefault(cmd, []).append(f.relative_to(PROJECT).as_posix())
    return found


def documented_flags() -> dict[tuple[str, str], list[str]]:
    """(command, flag) -> the files that tell someone to type it."""
    found: dict[tuple[str, str], list[str]] = {}
    for pattern in SOURCES:
        for f in sorted(PROJECT.glob(pattern)):
            if not f.is_file():
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if f.suffix == ".html":
                text = _BAKED.sub("", text)
            for cmd, flag in set(FLAGS.findall(text)):
                if cmd in NOT_COMMANDS:
                    continue
                found.setdefault((cmd, flag), []).append(f.relative_to(PROJECT).as_posix())
    return found


def allowed_flags(script: str) -> set[str] | None:
    """What a script's `reject_unknown` permits, or None when it declares no list.

    None is not "everything allowed" — it means this check cannot speak for that script, and
    saying nothing is better than inventing a verdict from an absent declaration.
    """
    path = DROPIN / script
    if not path.is_file():
        return None
    m = _ALLOWED.search(path.read_text(encoding="utf-8"))
    if not m:
        return None
    return set(re.findall(r'"(--?[a-z-]+)"', m.group(1)))


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

    # --- flags -------------------------------------------------------------
    scripts = {}
    src = (DROPIN / "okfm.py").read_text(encoding="utf-8")
    for name, script in re.findall(r'[("]([a-z-]+)",\s*"([\w.]+\.py)"', src):
        scripts[name] = script

    checked = 0
    for (cmd, flag), files in sorted(documented_flags().items()):
        if cmd not in known or cmd not in scripts:
            continue
        allowed = allowed_flags(scripts[cmd])
        if allowed is None:
            continue                       # that script declares no list — say nothing
        checked += 1
        if flag not in allowed:
            problems.append(f"`okfm {cmd} {flag}` is documented in "
                            f"{', '.join(sorted(set(files))[:2])} and `{scripts[cmd]}` "
                            f"rejects it — it accepts {', '.join(sorted(allowed)) or '(none)'}")
    if checked:
        print(f"  ok  {checked} documented flag(s) match what the script accepts")

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
