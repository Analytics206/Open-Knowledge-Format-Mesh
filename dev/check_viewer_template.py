#!/usr/bin/env python3
"""The drop-in's blank viewer must be the shipped viewer with the data removed.

    python dev/check_viewer_template.py          # verify
    python dev/check_viewer_template.py --write  # regenerate from the shipped viewer

## Why there are two viewers

One file was doing two jobs that want opposite things.

`okfm-web-ui.html` at the download root is **Level 1**: open it and OKFM's own mesh is
there — the guide, the decision records, the graph. It is a demonstration, and it is only a
demonstration because the data is baked in.

An adopter copies that same file into their project. Until they run a build it shows
**sixty-eight of OKFM's concepts and `human:analytics206` as the owner of four bundles.**
Somebody else's knowledge and somebody else's name, in a file they just added to their
repository, looking for all the world like it worked. If they open it before building — the
obvious thing to do after copying a folder — that is what they see.

So the drop-in carries a blank one, and the build seeds it into the project on first run.
Level 2 becomes a single copy of one folder, which is what it always claimed to be.

## Why this file exists

Two HTML files is two copies of the viewer's markup, and this project has had to reunify one
rule split across two implementations four times. The template is therefore **generated**:
take the shipped viewer, empty its three data blocks, write that. This check regenerates and
compares, so editing the viewer and forgetting the template fails here rather than shipping
an adopter a page whose markup is a version behind its data.

`needs: []`.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
SHIPPED = PROJECT / "okfm-web-ui.html"
TEMPLATE = PROJECT / "dropin" / "okfm-web-ui.html"

# The same three anchors `bake_web_ui.py` rewrites. Named here rather than imported because
# importing the baker to check the baker's output would hide a divergence in the patterns
# themselves — the one thing that would make both files wrong in the same way.
BLOCKS = [
    re.compile(r"(const BOOTSTRAP = )(\{.*?\n\});", re.S),
    re.compile(r"(const CONFIG_SCHEMA = )(\{.*?\n\});", re.S),
    re.compile(r"(const CONFIG = )(\{.*?\n\});", re.S),
]

# `{\n}` and not `{}`: the bake anchors on a closing brace at column 0, and an empty object
# written flat has none — the next bake would fail to find its own block.
EMPTY = "{\n}"


def blanked() -> str | None:
    """The shipped viewer with its data removed, or None if an anchor is missing."""
    html = SHIPPED.read_text(encoding="utf-8")
    for pattern in BLOCKS:
        m = pattern.search(html)
        if not m:
            return None
        html = html[:m.start(2)] + EMPTY + html[m.end(2):]
    return html


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    if not SHIPPED.is_file():
        print(f"no {SHIPPED.name} at the project root", file=sys.stderr)
        return 2

    fresh = blanked()
    if fresh is None:
        print("could not find all three data blocks in the shipped viewer — the bake and "
              "this check would both be wrong in the same way", file=sys.stderr)
        return 2

    if "--write" in sys.argv:
        TEMPLATE.write_text(fresh, encoding="utf-8", newline="\n")
        kb = len(fresh.encode("utf-8")) // 1024
        print(f"wrote {TEMPLATE.relative_to(PROJECT).as_posix()}  ({kb} KB, no data)")
        return 0

    problems = []
    if not TEMPLATE.is_file():
        problems.append(f"{TEMPLATE.relative_to(PROJECT).as_posix()} does not exist — "
                        f"generate it with `python dev/check_viewer_template.py --write`")
    elif TEMPLATE.read_text(encoding="utf-8") != fresh:
        problems.append(f"{TEMPLATE.relative_to(PROJECT).as_posix()} is not the shipped "
                        f"viewer with its data removed — the markup has diverged. "
                        f"Regenerate with `python dev/check_viewer_template.py --write`")
    else:
        print(f"  ok  {TEMPLATE.relative_to(PROJECT).as_posix()} is the shipped viewer, blanked")

    # The property that actually matters, checked directly rather than inferred from the
    # regeneration passing: no concept, no bundle, no owner from THIS project reaches an
    # adopter's copy. A template that merely looked right would still ship a name.
    if TEMPLATE.is_file():
        text = TEMPLATE.read_text(encoding="utf-8")
        for needle, what in (('"okfm_scope"', "a concept field"),
                             ("human:analytics206", "this project's steward"),
                             ('"/decisions/', "this project's decision records"),
                             ('"/level-2-build/', "this project's bundles")):
            if needle in text:
                problems.append(f"the blank viewer still carries {what} ({needle})")
        if not problems:
            print("  ok  it carries no concept, no bundle and no owner from this project")

    # ---- the edit surface has exactly one switch, and it is the probe ----------
    #
    # DR-0020 put the console's edit surface in the same file as the read-only viewer, on the
    # single condition that it is dark unless `okfm console` answers `/api/ping`. That
    # condition is what keeps Level 1 — a page opened from `file://`, where the probe cannot
    # succeed — read-only, and it is worth exactly as much as it is enforced.
    #
    # Verified live once: from `file://` the page reports `EDIT.on: false`, no Review tab, no
    # badge, zero approve buttons, zero textareas. A browser result is a fact about one
    # afternoon, so the invariant behind it is checked here instead: **`EDIT.on` is assigned
    # true in exactly one place, inside `probeConsole`.** A second assignment — a debug flag,
    # a "force edit" query parameter, a well-meant offline mode — is how a page that must not
    # write acquires the ability to, and it would be one line and invisible in review.
    for path in (SHIPPED, TEMPLATE):
        if not path.is_file():
            continue
        src = path.read_text(encoding="utf-8")
        rel = path.relative_to(PROJECT).as_posix()
        hits = re.findall(r"EDIT\.on\s*=\s*true", src)
        if len(hits) != 1:
            problems.append(f"{rel} switches the edit surface on in {len(hits)} place(s) — "
                            f"it must be exactly one, inside probeConsole()")
            continue
        probe = re.search(r"async function probeConsole\(\)\{.*?\n\}", src, re.S)
        if not probe or "EDIT.on = true" not in probe.group(0):
            problems.append(f"{rel} sets EDIT.on outside probeConsole() — the edit surface "
                            f"must be unlocked by the console answering, and by nothing else")
    if not problems:
        print("  ok  the edit surface is unlocked only by probeConsole(), in both viewers")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — the drop-in ships a viewer with no data in it"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
