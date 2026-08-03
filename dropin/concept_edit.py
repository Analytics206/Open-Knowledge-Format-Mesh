#!/usr/bin/env python3
"""Split a concept into the pieces a person edits, and put it back together.

    python okfm/okfm.py edit <path>              # show the pieces
    python okfm/okfm.py edit <path> --json       # the same, for a program

## Why this is not a text editor

The ask was: *"I don't want an editor that just opens files, it should parse sections to
edit."* Right, and for a reason beyond convenience. A concept is two documents in one file —
frontmatter that a validator reads by key, and a body that a person reads by heading. Opening
the whole thing as text means every edit risks the half you were not editing, and the half
most easily broken by accident is the one nothing warns you about until the next build.

So this splits a concept into **top-level frontmatter keys** and **body sections**, and
writes back only the pieces that changed. Everything untouched is preserved byte for byte,
including comments, quoting style and key order.

## Why the frontmatter is edited as text

There is no YAML parser here. `dropin/` is standard library only, and adding PyYAML to read a
file the rest of the toolchain already reads with `re` would be a second parser that
disagrees with the first one at the margins — which is the failure this project has had to
undo four times.

A top-level key is a line matching `^key:` plus every indented line under it. Replacing one
means replacing that span. It is lossless because nothing is re-serialized: a key you did not
touch is the same bytes it was.

The cost is that you can write invalid YAML, and this module cannot tell you so. What it can
do is refuse to leave you there: the console validates after every write and hands back the
previous text, so a bad edit is one click from gone. `okfm validate` is the authority on
whether a concept is legal, and it stays the authority.

## What is not editable, and why that is only two things

`generated` and `okfm_captured` are written by machines and mean *when a machine did
something*. Editing them by hand is not an edit, it is a claim about history. Everything
else — including `status`, `verified` and `okfm_relations` — is editable, which is a
deliberate widening of [DR-0011](../docs/decisions/0011-viewer-and-console.md)'s line. See
[DR-0020](../docs/decisions/0020-the-console-edits-concepts.md).

`needs: []`.
"""
import json
import re
import sys
from pathlib import Path

from okfm_core import PROJECT, frontmatter, reject_unknown, utf8_stdout

utf8_stdout()

# A top-level key line, and the start of the next one. Continuation is "anything indented, or
# blank" — which is what YAML block structure means at this level and all this needs to know.
_KEY = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")

# Written by a machine, about a machine. `generated.at` is the build's stamp and
# `okfm_captured` is the observation drift is measured against; hand-editing either does not
# change a fact, it changes the record of one. Commands write these — `build`, `revalidate`.
MACHINE_KEYS = {
    "generated": "the build stamps this — editing it backdates a machine's work",
    "sources": "holds `okfm_captured`, which `revalidate` observes; edit it there",
}


def split_frontmatter(block: str) -> list[dict]:
    """Top-level keys in file order, each with the exact text that belongs to it."""
    lines = block.splitlines()
    starts = [i for i, ln in enumerate(lines) if _KEY.match(ln)]
    out = []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        key = _KEY.match(lines[i]).group(1)
        raw = "\n".join(lines[i:end]).rstrip()
        out.append({
            "key": key,
            "raw": raw,
            "value": _KEY.match(lines[i]).group(2).strip(),
            "multiline": end - i > 1,
            "locked": MACHINE_KEYS.get(key),
        })
    return out


def split_sections(body: str) -> list[dict]:
    """Body split on markdown headings, in file order.

    Text before the first heading is a section with an empty heading rather than a special
    case. A concept whose body is three paragraphs and no headings is one editable section,
    which is the honest answer — not an error and not zero sections.
    """
    lines = body.splitlines()
    heads = [i for i, ln in enumerate(lines) if re.match(r"^#{1,6}\s+\S", ln)]
    out, first = [], heads[0] if heads else len(lines)
    if "".join(lines[:first]).strip():
        out.append({"heading": "", "level": 0, "text": "\n".join(lines[:first]).strip("\n")})
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        hashes, title = re.match(r"^(#{1,6})\s+(.*)$", lines[i]).groups()
        out.append({"heading": title.strip(), "level": len(hashes),
                    "text": "\n".join(lines[i + 1:end]).strip("\n")})
    return out


def parse(path: Path) -> dict:
    """A concept as its editable pieces. Raises ValueError when it is not a concept."""
    block, body = frontmatter(path)
    if not block:
        raise ValueError(f"{path} has no frontmatter — not a concept")
    return {"fields": split_frontmatter(block), "sections": split_sections(body)}


def _rebuild_body(sections: list[dict], lead: str = "\n") -> str:
    """Sections back to a body, in the shape `split_sections` reads.

    `lead` is carried from the original rather than chosen here. Most concepts have a blank
    line after the closing `---` and thirteen do not, and a rebuilder that picks one puts a
    one-line diff into every file of the other kind on a save that changed nothing. Round-trip
    fidelity is the whole basis for trusting this module with somebody's writing: reformatting
    what you were not asked to touch is how an editor loses an argument about whether it also
    lost something else.
    """
    parts = []
    for s in sections:
        if s.get("level"):
            parts.append("#" * int(s["level"]) + " " + s["heading"])
        parts.append((s.get("text") or "").strip("\n"))
    return lead + "\n\n".join(p for p in parts if p).strip("\n") + "\n"


def write(path: Path, fields: dict[str, str] | None = None,
          sections: list[dict] | None = None) -> str:
    """Apply changed keys and/or a new section list. Returns the previous file text.

    Returning the old text rather than writing a `.bak` is deliberate: a backup file beside a
    concept is a file the next build has to be taught to ignore, and this project has already
    shipped one directory of things the build had to learn about. The caller holds it in
    memory for exactly as long as an undo is useful.
    """
    before = path.read_text(encoding="utf-8")
    block, body = frontmatter(path)
    if not block:
        raise ValueError(f"{path} has no frontmatter — not a concept")

    if fields:
        entries = split_frontmatter(block)
        known = {e["key"]: e for e in entries}
        for key, raw in fields.items():
            if key in MACHINE_KEYS:
                raise ValueError(f"`{key}` is not hand-editable — {MACHINE_KEYS[key]}")
            new = (raw or "").rstrip()
            if key in known:
                if new:
                    block = block.replace(known[key]["raw"], new, 1)
                else:
                    # Deleting a key removes its line rather than leaving `key:` with nothing
                    # after it, which is a null the validator reads as a present-but-empty
                    # value — a different statement from "this concept does not say".
                    block = block.replace(known[key]["raw"] + "\n", "", 1).replace(
                        known[key]["raw"], "", 1)
            elif new:
                block = block.rstrip() + "\n" + new
        # A deletion can leave a blank line where the key was. Collapse runs, keep none at
        # the edges — the frontmatter block is written back between two `---` lines.
        block = re.sub(r"\n{2,}", "\n", block).strip("\n")

    if sections is not None:
        body = _rebuild_body(sections, "\n" if body.startswith("\n") else "")

    # Exactly `revalidate.py`'s reconstruction. Two spellings of "write a concept back"
    # would differ by a newline on some file nobody looked at, and the diff would be blamed
    # on whichever command ran second.
    path.write_text(f"---\n{block}\n---\n{body}", encoding="utf-8", newline="\n")
    return before


def restore(path: Path, text: str) -> None:
    """Put back exactly what was there. The undo behind every console write."""
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    argv = sys.argv[1:]
    reject_unknown(argv, ("--json",), __doc__)
    paths = [a for a in argv if not a.startswith("-")]
    if not paths:
        print("usage: okfm edit <path> [--json]", file=sys.stderr)
        return 2

    p = (PROJECT / paths[0]).resolve()
    if not p.is_file():
        print(f"not found: {paths[0]}", file=sys.stderr)
        return 2
    try:
        parsed = parse(p)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if "--json" in argv:
        print(json.dumps(parsed, indent=1))
        return 0

    print(f"{paths[0]}\n")
    print("  frontmatter")
    for f in parsed["fields"]:
        mark = "  (command-only)" if f["locked"] else ""
        shown = f["value"] if not f["multiline"] else f"<{len(f['raw'].splitlines())} lines>"
        print(f"    {f['key']:<18} {shown[:52]}{mark}")
    print("\n  body sections")
    for s in parsed["sections"]:
        name = s["heading"] or "(preamble)"
        print(f"    {'#' * s['level'] + ' ' if s['level'] else '':<4}{name:<34} "
              f"{len(s['text'].split())} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
