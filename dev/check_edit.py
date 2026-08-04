#!/usr/bin/env python3
"""Editing a concept changes what you edited, and nothing else.

    python dev/check_edit.py

## Why this exists

`concept_edit.py` is the only thing in this project that writes into a person's own prose.
Everything else writes machine fields into files a machine generated. That difference is the
whole reason this check is here: a build that formats its own output badly is a nuisance, and
an editor that reformats a paragraph you did not open is a thing you stop trusting with your
writing — permanently, and correctly.

The property is one sentence. **A save that changes nothing must change nothing, byte for
byte.** Everything below is that sentence applied to a different shape of input.

It was proved once by hand, over the 74 concepts that happened to be in this repository, and
then written into [DR-0020](../docs/decisions/0020-the-console-edits-concepts.md) as an
established fact. It was not established; it was measured on a Tuesday. Three defects were
sitting inside the same module while that sentence was in the documentation:

  * A `#` line inside a fenced block was read as a heading. The section boundary then landed
    **between a code fence's two halves**, so editing the section above handed somebody text
    ending in an unclosed fence. This was live, on the worst possible file:
    `guide/first-concept.md` teaches a new author how to write a concept by embedding an
    example one in a ```` ```markdown ```` block, and that example's `# Decision`, `# Why` and
    `# What would change this` headings were read as real. Nine sections where there are six —
    on the page a first-time user is likeliest to open.
  * A heading with no blank line after it gained one. So did every body that ended without a
    trailing newline, and every run of two blank lines lost one.
  * `write()` found a frontmatter key by searching the block for its text, so with
        description: "status: draft is the default"
        status: draft
    a request to set `status: stable` rewrote **the description** and left `status` alone.
    Silently, with no error, and with the requested field untouched.

The corpus pass would have caught none of the first two, because the corpus did not contain
those shapes, and would have caught the third only by coincidence. So this check runs both: the
real corpus, and a table of shapes chosen because they are awkward rather than because they are
present. The second table is the one that will still be earning its keep in a year.

Project-local, like the other checks here: it tests this repository's implementation, not an
adopter's mesh. `needs: []`.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT / "dropin"))

import concept_edit as ce  # noqa: E402
from okfm_core import frontmatter, is_concept  # noqa: E402

SKIP_DIRS = {".git", "__pycache__", ".okfm-cache", "node_modules"}

FM = "---\ntype: Document\ntitle: T\nstatus: draft\n---\n"

# Bodies that are awkward on purpose. Each one is a way the old rebuilder guessed wrong, or a
# way the next one might. A shape is in this table because it is hard, not because a file in
# this repository happens to have it — which is the difference between a property and a
# measurement.
SHAPES = {
    "a hash comment inside a fenced block": FM + "\n# A\n\n```bash\n# install it\necho hi\n```\n",
    "a fence nested in a longer fence":     FM + "\n# A\n\n````md\n```\n### x\n```\n````\n",
    "a tilde fence":                        FM + "\n# A\n\n~~~bash\n# install it\n~~~\n",
    "a fence that is never closed":         FM + "\n# A\n\n```bash\n# install it\n",
    "a fence indented inside a list":       FM + "\n# A\n\n- item\n\n  ```bash\n  # x\n  ```\n",
    "a heading with no blank line after":   FM + "\n# A\nText.\n\n# B\nMore.\n",
    "two blank lines before a heading":     FM + "\n# A\n\ntext\n\n\n# B\n\nmore\n",
    "a whitespace-only line as a gap":      FM + "\n# A\n\ntext\n   \n# B\n\nmore\n",
    "no trailing newline":                  FM + "\n# A\n\ntext",
    "two trailing newlines":                FM + "\n# A\n\ntext\n\n",
    "a heading indented four spaces":       FM + "\n# A\n\n    # not a heading\n\ntext\n",
    "an empty body":                        FM + "\n",
    "a body with no headings at all":       FM + "\njust text, no headings\n",
    "a body that starts at the fence":      "---\ntype: Document\ntitle: T\n---\n# Only\n\ntext.\n",
    "a table":                              FM + "\n# A\n\n| a | b |\n|---|---|\n| 1 | 2 |\n",
    "an html comment and a list":           FM + "\n# A\n\n<!-- note -->\n\n- one\n- two\n",
}

# (frontmatter, key to set, new value) where the key's text also appears somewhere else in the
# block. Both orderings, because the old substring search happened to be right when the real
# key came first and this must not pass by luck.
TARGETS = [
    ('type: Document\ndescription: "status: draft is the default"\nstatus: draft',
     "status", "status: stable", "description"),
    ('type: Document\nstatus: draft\ndescription: "status: draft is the default"',
     "status", "status: stable", "description"),
    ('type: Document\ntitle: T\nokfm_relations:\n  - { predicate: part_of, target: /x.md }\n'
     'description: "part_of, target: /x.md is the edge"',
     "okfm_relations", "okfm_relations:\n  - { predicate: part_of, target: /y.md }",
     "description"),
]


def concepts() -> list[Path]:
    """Every concept in the repository, wherever it lives.

    Deliberately wider than the console's reach. The console edits configured bundles, but the
    property under test belongs to the module, and `docs/`, `packs/`, `examples/` and
    `templates/` hold concepts written by hand rather than generated — which is exactly where
    the unusual whitespace lives.
    """
    out = []
    for p in sorted(PROJECT.rglob("*.md")):
        if SKIP_DIRS & set(p.relative_to(PROJECT).parts):
            continue
        try:
            if is_concept(p):
                out.append(p)
        except (OSError, UnicodeDecodeError):
            continue
    return out


def resave(path: Path) -> tuple[bytes, bytes]:
    """Save a concept without changing anything, exactly as the console's Save does.

    The browser posts **every** unlocked field and **every** section on every save — it has no
    idea which one you typed in — so a no-op save is not a hypothetical. It is what happens
    when somebody edits one paragraph and presses the button.
    """
    before = path.read_bytes()
    parsed = ce.parse(path)
    fields = {f["key"]: f["raw"] for f in parsed["fields"] if not f["locked"]}
    ce.write(path, fields=fields, sections=parsed["sections"])
    return before, path.read_bytes()


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "c.md"

        # --- the corpus ---------------------------------------------------
        # On copies. A check that edits the repository to prove it does not edit the
        # repository has already lost the argument.
        found = concepts()
        if not found:
            print("no concepts found — this check examined nothing", file=sys.stderr)
            return 2
        changed = []
        for p in found:
            scratch.write_bytes(p.read_bytes())
            try:
                before, after = resave(scratch)
            except (ValueError, OSError) as e:
                changed.append(f"{p.relative_to(PROJECT).as_posix()} — {type(e).__name__}: {e}")
                continue
            if before != after:
                changed.append(p.relative_to(PROJECT).as_posix())
        if changed:
            problems.append(f"{len(changed)} of {len(found)} concepts do not survive a save "
                            f"that changed nothing: {', '.join(changed[:6])}"
                            + (" …" if len(changed) > 6 else ""))
        else:
            print(f"  ok  all {len(found)} concepts survive a no-op save byte-identical")

        # --- shapes the corpus does not have -------------------------------
        broke = []
        for name, text in SHAPES.items():
            scratch.write_bytes(text.encode("utf-8"))
            try:
                before, after = resave(scratch)
            except (ValueError, OSError) as e:
                broke.append(f"{name} ({type(e).__name__})")
                continue
            if before != after:
                broke.append(name)
        if broke:
            problems.append(f"{len(broke)} of {len(SHAPES)} awkward shapes are reformatted by a "
                            f"save that changed nothing: {'; '.join(broke)}")
        else:
            print(f"  ok  all {len(SHAPES)} awkward shapes survive a no-op save byte-identical")

        # --- a fence is not a heading --------------------------------------
        # Stated separately from the round-trip because it can be broken without breaking it:
        # a splitter that finds a phantom heading and a rebuilder that puts the bytes back
        # unchanged still shows a person two half-sections with a code fence torn between them.
        secs = ce.split_sections("\n# Real\n\n```bash\n# not a heading\necho hi\n```\n\n## Also\n")
        got = [s["heading"] for s in secs if s["level"]]
        if got != ["Real", "Also"]:
            problems.append(f"a `#` line inside a fenced block was read as a heading: {got} "
                            f"— the fence's two halves land in different sections")
        else:
            print("  ok  a `#` line inside a fenced block is code, not a heading")

        # --- and no real concept is split inside a fence ---------------------
        # The property behind the previous assertion, stated so it cannot be satisfied by the
        # one input that was thought of. A section that ends while a fence is still open is a
        # section whose text a person would be handed with no closing ``` — and whose other
        # half is a separate editable box.
        #
        # This was not hypothetical, and it was not in an obscure file. `guide/first-concept.md`
        # — the page that teaches somebody how to write their first concept — embeds an example
        # concept in a ```markdown block, and that example's own `# Decision`, `# Why` and
        # `# What would change this` headings were read as real ones: nine sections where there
        # are six.
        # The probe line is what makes this correct. `_fenced` marks a block's *closing*
        # delimiter as inside it — right for deciding whether a line can be a heading, and the
        # wrong question here. Asking about one more line past the end asks the question this
        # actually cares about: with the section exhausted, is a fence still open? Same single
        # implementation, rather than a second fence reader in a check that would drift from
        # the first one.
        torn = []
        for p in found:
            _, body = frontmatter(p)
            for s in ce.split_sections(body or ""):
                lines = (s["text"] or "").splitlines()
                if lines and ce._fenced(lines + [""])[-1]:
                    torn.append(f"{p.relative_to(PROJECT).as_posix()} → "
                                f"{s['heading'] or '(preamble)'}")
                    break
        if torn:
            problems.append(f"{len(torn)} concept section(s) end with a code fence still open, "
                            f"so the boundary fell inside one: {', '.join(torn[:5])}")
        else:
            print(f"  ok  no section in {len(found)} concepts is split inside a code fence")

        # --- the right key is the one that changes -------------------------
        mistargeted = []
        for block, key, new, bystander in TARGETS:
            scratch.write_bytes(f"---\n{block}\n---\n\n# A\n\ntext\n".encode("utf-8"))
            was = {f["key"]: f["raw"] for f in ce.parse(scratch)["fields"]}
            ce.write(scratch, fields={key: new})
            now = {f["key"]: f["raw"] for f in ce.parse(scratch)["fields"]}
            if now.get(key) != new:
                mistargeted.append(f"setting `{key}` did not change it — still "
                                   f"{now.get(key)!r}")
            if now.get(bystander) != was.get(bystander):
                mistargeted.append(f"setting `{key}` rewrote `{bystander}` instead: "
                                   f"{was.get(bystander)!r} became {now.get(bystander)!r}")
        problems += mistargeted
        if not mistargeted:
            print(f"  ok  a key is replaced where it is, not where its text first appears "
                  f"({len(TARGETS)} cases)")

        # --- an edit lands, and its neighbours do not move -------------------
        scratch.write_bytes((FM + "\n# A\n\nfirst\n\n# B\n\nsecond\n\n# C\n\nthird\n")
                            .encode("utf-8"))
        secs = ce.parse(scratch)["sections"]
        secs[1] = {**secs[1], "text": "rewritten"}
        ce.write(scratch, sections=secs)
        after = ce.parse(scratch)["sections"]
        texts = [s["text"] for s in after]
        if texts != ["first", "rewritten", "third"]:
            problems.append(f"editing one section disturbed its neighbours: {texts}")
        else:
            print("  ok  editing one section leaves the others exactly as they were")

        # --- machine keys refuse -------------------------------------------
        # The refusal is the rule DR-0020 kept from DR-0011. If it ever became a silent
        # no-op, the console would appear to accept an edit it discarded.
        accepted = []
        for key in ce.MACHINE_KEYS:
            scratch.write_bytes((FM + "\n# A\n\ntext\n").encode("utf-8"))
            try:
                ce.write(scratch, fields={key: f"{key}: tampered"})
            except ValueError:
                continue
            accepted.append(key)
        if accepted:
            problems.append(f"{', '.join(accepted)} accepted a hand edit — they record when a "
                            f"machine did something, and only a command may write them")
        else:
            print(f"  ok  {', '.join(ce.MACHINE_KEYS)} refuse a hand edit")

        # --- the wire format stays narrow ------------------------------------
        # `_split_body` carries each section's byte span. It must not reach the browser: the
        # page would post the whole body back a second time inside the sections it was given,
        # and a field nothing shows is a field nothing maintains.
        leaked = sorted(set(ce.split_sections("\n# A\n\ntext\n")[0]) - {"heading", "level", "text"})
        if leaked:
            problems.append(f"split_sections leaks {leaked} to callers — the byte spans stay "
                            f"inside the module")
        else:
            print("  ok  split_sections hands out heading/level/text and nothing else")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — a save changes what you edited and nothing else"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
