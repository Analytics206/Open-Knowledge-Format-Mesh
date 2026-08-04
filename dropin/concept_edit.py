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
means replacing **that span**, by line number. It is lossless because nothing is
re-serialized: a key you did not touch is the same bytes it was.

That emphasis is the correction. This replaced a key by searching the block for its text, so

    description: "status: draft is the default"
    status: draft

took a request to set `status: stable`, rewrote **the description**, and left `status` alone.
No error, and the field you asked for untouched. The line span was already being computed and
was thrown away in favour of the search.

The cost of editing YAML as text is that you can write invalid YAML, and this module cannot
tell you so. What it can do is refuse to leave you there: the console validates after every
write and hands back the previous text, so a bad edit is one click from gone. `okfm validate`
is the authority on whether a concept is legal, and it stays the authority.

## What a save must not do

**Change anything you did not edit.** Not a blank line, not a trailing newline, not the
spacing inside a code block. The rule sounds fussy until you notice what it protects: this is
the only code in the project that writes into somebody's own prose, and an editor that
reformats a paragraph you did not open is one you stop trusting with your writing —
permanently, and correctly.

It is a property here rather than a list of remembered cases. `_split_body` returns spans that
tile the body exactly, so a section that did not change is written back as the bytes it was
read from and the question of which whitespace convention its author used never arises. What
that replaced was a rebuilder that re-joined everything with its own separators and was then
patched, once, for the thirteen concepts that happened to disagree with it.

Fences are part of the same rule. A `#` line inside a fenced block was read as a heading, which
put a section boundary *between a code fence's two halves* — so editing the section above
handed somebody text ending in an unclosed fence, and its other half was a separate editable
box. That was live rather than theoretical, on the file least able to afford it:
`guide/first-concept.md` teaches a first-time author by embedding an example concept in a
```` ```markdown ```` block, and the example's own `# Decision`, `# Why` and `# What would
change this` headings were read as the document's. Nine sections where there are six.

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

# A fenced code block, opening or closing. Up to three spaces of indent and three or more
# backticks or tildes, per CommonMark — and the close must use the same character and be at
# least as long as the open, which is what makes ```` ```` ```` able to contain ``` ``` ```.
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*(.*)$")

# A heading, when it is not inside a fence.
_HEAD = re.compile(r"^(#{1,6})\s+(\S.*)$")


def _fenced(lines: list[str]) -> list[bool]:
    """Which lines are inside a fenced code block.

    Without this, `# install it` inside a ```` ```bash ```` block is a heading. That is not a
    cosmetic misread: the section boundary lands *between the fence's two halves*, so editing
    the section above hands somebody text ending in an unclosed ```` ``` ```` and the section
    below opens with orphaned code. The two halves of one code block become independently
    editable, which is a way to lose a document that no diff makes obvious.
    """
    inside, opened = [False] * len(lines), None
    for i, ln in enumerate(lines):
        m = _FENCE.match(ln)
        if opened is None:
            # A backtick fence's info string may not contain a backtick, so ``` `x` ``` in
            # prose does not open a block.
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                opened, inside[i] = m.group(1), True
            continue
        inside[i] = True
        if m and m.group(1)[0] == opened[0] and len(m.group(1)) >= len(opened) \
                and not m.group(2).strip():
            opened = None
    return inside


def split_frontmatter(block: str) -> list[dict]:
    """Top-level keys in file order, each with the exact text and line span that belongs to it.

    `start`/`end` are the point of this function. They were computed and thrown away, and
    `write` then found a key by searching the block for its text — which edits whichever key
    happens to spell it first. See the note there.
    """
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
            "start": i,
            "end": end,
        })
    return out


def _split_body(body: str) -> tuple[str, list[dict]]:
    """`(lead, sections)`, where the sections' `raw` spans tile the body after `lead`.

    That tiling is the whole design. `lead + "".join(s["raw"] for s in sections) == body`,
    exactly, for any body — so a rebuild that reuses every span reproduces the file byte for
    byte without anything having to know which whitespace conventions the author used.
    Round-trip fidelity stops being a list of shapes that were remembered and becomes a
    property, which matters because the shapes that get forgotten are the ones nobody had in
    the corpus on the day they wrote the rebuilder.
    """
    raw = body.splitlines(keepends=True)
    lines = [ln.rstrip("\r\n") for ln in raw]
    inside = _fenced(lines)
    heads = [i for i, ln in enumerate(lines) if not inside[i] and _HEAD.match(ln)]

    first = heads[0] if heads else len(lines)
    out: list[dict] = []
    lead = "".join(raw[:first])
    if "".join(lines[:first]).strip():
        # Text before the first heading is a section with an empty heading rather than a
        # special case. A body of three paragraphs and no headings is one editable section.
        out.append({"heading": "", "level": 0,
                    "text": "\n".join(lines[:first]).strip("\n"), "raw": lead})
        lead = ""
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        hashes, title = _HEAD.match(lines[i]).groups()
        out.append({"heading": title.strip(), "level": len(hashes),
                    "text": "\n".join(lines[i + 1:end]).strip("\n"),
                    "raw": "".join(raw[i:end])})
    return lead, out


def split_sections(body: str) -> list[dict]:
    """Body split on markdown headings, in file order — the shape a person edits.

    The byte spans `_split_body` carries stay inside this module. The browser sends back what
    it was given, and a field it neither shows nor changes is a field that only makes the
    payload bigger and the contract wider.
    """
    _, out = _split_body(body)
    return [{"heading": s["heading"], "level": s["level"], "text": s["text"]} for s in out]


def parse(path: Path) -> dict:
    """A concept as its editable pieces. Raises ValueError when it is not a concept."""
    block, body = frontmatter(path)
    if not block:
        raise ValueError(f"{path} has no frontmatter — not a concept")
    return {"fields": split_frontmatter(block), "sections": split_sections(body)}


def _same(a: dict, b: dict) -> bool:
    """Whether an incoming section is the one that was read, unchanged."""
    return (int(a.get("level") or 0) == int(b.get("level") or 0)
            and (a.get("heading") or "") == (b.get("heading") or "")
            and (a.get("text") or "").strip("\n") == (b.get("text") or "").strip("\n"))


def _rebuild_body(sections: list[dict], parsed: list[dict], lead: str) -> str:
    """Sections back to a body: exact bytes for what did not change, canonical for what did.

    A section you did not touch is written back as the bytes it was read from, so a save
    normalizes only what you actually edited. Reformatting the rest is how an editor loses an
    argument about whether it also lost something else — and the argument is unwinnable,
    because the diff is real and the explanation is "that part is fine, trust me".
    """
    parts, last = [], len(sections) - 1
    for i, s in enumerate(sections):
        if i < len(parsed) and _same(s, parsed[i]):
            parts.append(parsed[i]["raw"])
            continue
        chunks = []
        if int(s.get("level") or 0):
            chunks.append("#" * int(s["level"]) + " " + (s.get("heading") or ""))
        if (s.get("text") or "").strip("\n"):
            chunks.append(s["text"].strip("\n"))
        parts.append("\n\n".join(chunks) + "\n" + ("\n" if i < last else ""))
    return lead + "".join(parts)


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
        known = {e["key"]: e for e in split_frontmatter(block)}
        for key in fields:
            if key in MACHINE_KEYS:
                raise ValueError(f"`{key}` is not hand-editable — {MACHINE_KEYS[key]}")
        lines = block.splitlines()
        # **A key is replaced where it is, not where its text first appears.** This was
        # `block.replace(raw, new, 1)`, and with
        #     description: "status: draft is the default"
        #     status: draft
        # asking for `status: stable` rewrote the description and left `status` alone —
        # silently, with no error and the requested field untouched. The line span was
        # already computed; searching for the text discarded it.
        #
        # Highest index first, so a splice never moves a span that has not been applied yet.
        for key, raw in sorted(fields.items(),
                               key=lambda kv: -(known[kv[0]]["start"] if kv[0] in known else -1)):
            new, e = (raw or "").rstrip(), known.get(key)
            if e and new == e["raw"]:
                continue                    # unchanged — do not touch its bytes
            if e:
                # An empty value deletes the key outright rather than leaving `key:` with
                # nothing after it, which is a null the validator reads as present-but-empty
                # — a different statement from "this concept does not say".
                lines[e["start"]:e["end"]] = new.splitlines() if new else []
            elif new:
                lines.extend(new.splitlines())
        block = "\n".join(lines).strip("\n")

    if sections is not None:
        lead, parsed = _split_body(body)
        body = _rebuild_body(sections, parsed, lead)

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
