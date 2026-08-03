#!/usr/bin/env python3
"""Run the README's own Level 2 commands against a fresh project.

    python dev/check_readme.py

## What this is, and what it is not

§13.7's distribution test is *a stranger reaches a running mesh in under an hour, with only
the README*. **This is not that test.** Only a stranger can run that one, and the thing it
measures — whether the page is comprehensible to somebody who has never seen the project —
cannot be asserted by the person who wrote it.

What this checks is the half that *is* mechanical: the commands on that page, executed
exactly as written, reach a valid mesh. A README whose instructions do not run fails the
real test too, so this rules out one whole class of failure and leaves the interesting one
open. Saying which is which matters more than the check does.

It was worth writing because the documented path was broken in a way that never showed up
here. `cp -r .../dropin my-project/.okfm` put the tool, the config and the adopter's
concepts in one directory. First run: fine. Second day, upgrading with the same command the
page gives you: a copy nests silently inside, nothing updates, no error — and the only
obvious fix, deleting first, takes every enriched concept with it. This repository never met
that, because it keeps `dropin/` and `.okfm/` apart, which is what the page now says to do.

## Why it interprets commands instead of running a shell

A `subprocess` call to `bash` would be shorter and would skip on any machine without one —
and a check that skips is a check that reports success for the wrong reason, which is the
failure mode this project keeps paying for. So the small command vocabulary the README uses
is interpreted directly, and **a command form this file does not recognise is a failure**,
not a skip. If the page grows a command, this fails until somebody teaches it that command,
which is the correct amount of friction.

`needs: []`.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
README = PROJECT / "README.md"

# The section whose commands are meant to be run verbatim by an adopter.
SECTION = "## Level 2 — paste and run"

# What the README calls the download, and the project it is pasted into.
DOWNLOAD = "Open-Knowledge-Format-Mesh"
ADOPTER = "my-project"


def blocks(text: str, heading: str) -> list[str]:
    """Every ```bash block under one `##` heading, in order."""
    start = text.find(heading)
    if start < 0:
        return []
    rest = text[start + len(heading):]
    end = rest.find("\n## ")
    return re.findall(r"```bash\n(.*?)```", rest[:end if end > 0 else len(rest)], re.S)


class Shell:
    """Just enough shell to run a quickstart, and no more."""

    def __init__(self, root: Path, download: Path):
        self.cwd = root
        self.root = root
        self.download = download
        self.ran: list[str] = []

    def _resolve(self, token: str) -> Path:
        """Map a README path onto the sandbox. Leading segment only, once.

        Substituting anywhere in the string rewrites the replacement's own text — the
        expansion of `Open-Knowledge-Format-Mesh/dropin` still contains that name, so a
        second pass produced a path with the temp root spliced into the middle of itself.
        """
        head, _, tail = token.partition("/")
        if head == DOWNLOAD:
            base = self.download
        elif head == ADOPTER:
            base = self.root / ADOPTER
        else:
            p = Path(token)
            return p if p.is_absolute() else (self.cwd / token)
        return base / tail if tail else base

    def run(self, line: str) -> str | None:
        """None on success, a message on failure."""
        for part in line.split("&&"):
            problem = self._one(part.strip())
            if problem:
                return problem
        return None

    def _one(self, cmd: str) -> str | None:
        if not cmd or cmd.startswith("#"):
            return None
        self.ran.append(cmd)
        args = cmd.split()

        if args[0] == "cd":
            self.cwd = self._resolve(args[1])
            return None if self.cwd.is_dir() else f"`{cmd}` — no such directory"

        if args[0] == "cp":
            recursive = "-r" in args
            rest = [a for a in args[1:] if not a.startswith("-")]
            if len(rest) != 2:
                return f"`{cmd}` — expected exactly one source and one destination"
            src, dst = self._resolve(rest[0]), self._resolve(rest[1])
            if not src.exists():
                return f"`{cmd}` — source does not exist"
            dst.parent.mkdir(parents=True, exist_ok=True)
            if recursive:
                # Deliberately NOT dirs_exist_ok. `cp -r a b` with b present nests `b/a`
                # rather than replacing, which is exactly the silent non-upgrade the README
                # now warns about — so a README that told you to do it would fail here.
                if dst.exists():
                    return (f"`{cmd}` — destination already exists, so a real `cp -r` would "
                            f"nest a copy inside it and update nothing")
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
            else:
                shutil.copy2(src, dst)
            return None

        if args[0] == "rm" and "-rf" in args:
            for target in (self._resolve(a) for a in args[1:] if not a.startswith("-")):
                if target.is_dir():
                    shutil.rmtree(target)
                elif target.exists():
                    target.unlink()
            return None

        if args[0] == "python":
            r = subprocess.run([sys.executable, *args[1:]], cwd=self.cwd, capture_output=True,
                               text=True, encoding="utf-8", errors="replace")
            self.last = r
            return None if r.returncode == 0 else f"`{cmd}` — exit {r.returncode}\n{r.stdout[-1500:]}"

        # Not a skip. See the module docstring.
        return (f"`{cmd}` — this checker does not know that command. Teach it, or the "
                f"README's quickstart is no longer being verified.")


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    text = README.read_text(encoding="utf-8")
    cmds = [ln.strip() for b in blocks(text, SECTION) for ln in b.splitlines() if ln.strip()]
    if not cmds:
        print(f"no bash blocks under `{SECTION}` — has the heading changed?", file=sys.stderr)
        return 2

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        download = root / DOWNLOAD
        shutil.copytree(PROJECT, download,
                        ignore=shutil.ignore_patterns("__pycache__", ".git", ".okfm-cache"))
        # An adopter's project: their documents, and nothing of OKFM's.
        docs = root / ADOPTER / "docs" / "architecture"
        docs.mkdir(parents=True)
        (docs.parent / "overview.md").write_text(
            "# Overview\n\nThe service accepts webhooks and enqueues work.\n",
            encoding="utf-8", newline="\n")
        (docs / "queue.md").write_text(
            "# The queue\n\nRedis, single consumer group. Chosen over SQS because the "
            "deploy target has no AWS account.\n", encoding="utf-8", newline="\n")

        sh = Shell(root, download)
        for cmd in cmds:
            problem = sh.run(cmd)
            if problem:
                problems.append(problem)
                break
            print(f"  ok  {cmd}")

        proj = root / ADOPTER
        if not problems:
            out = getattr(sh, "last", None)
            if not out or "OK — mesh is valid" not in out.stdout:
                problems.append("the README's commands ran but did not produce a valid mesh")
            else:
                print("  ok  the documented commands reach a valid mesh")

            # The three-directory table on that page, checked against what actually landed.
            # A page that describes a layout the tool does not produce is worse than one that
            # describes nothing, because it is the layout somebody plans around.
            for path, what in ((proj / "okfm.json", "the config, at the project root"),
                               (proj / "okfm" / "okfm.py", "the tool, in okfm/"),
                               (proj / ".okfm" / "mesh", "the mesh, in .okfm/")):
                if path.exists():
                    print(f"  ok  {what}")
                else:
                    problems.append(f"README describes {what}, and it is not there")

            # `.okfm/` must hold bundles and nothing else — that is what makes it deletable
            # and what makes an adopter able to find their own knowledge in it.
            stray = sorted(p.name for p in (proj / ".okfm").glob("*")
                           if p.is_file() or p.name in ("vocab", "references"))
            if stray:
                problems.append(f".okfm/ holds tool files as well as the mesh: "
                                f"{', '.join(stray)}")
            else:
                n = len(list((proj / ".okfm").glob("*")))
                print(f"  ok  .okfm/ holds {n} bundle(s) and nothing else")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — the README's Level 2 commands run, and produce what it says they do"
          if not problems else f"{len(problems)} problem(s)")
    print("\nThis is the mechanical half of §13.7. Whether a stranger UNDERSTANDS the page\n"
          "is not checkable here, and is still unproven.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
