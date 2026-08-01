#!/usr/bin/env python3
"""Deterministic bundle bootstrap -- the first cut of the Level 2 build.

Turns plain markdown into OKF concepts with NO MODEL ANYWHERE. Every field it writes is
extracted or computed:

    type            from configuration
    title           the first H1, else the filename de-slugged
    description     first blockquote, else first real paragraph (see _extract_description)
    resource        the file path
    okfm_captured   sha256 of the file, as seen right now
    generated       process:okfm-bootstrap

Extraction, not drafting: every value is copied from text that already exists, so the worst
case is an unhelpful description -- never one that is wrong about what the source says. See
decisions/0008 "Extraction is not drafting" and 0009 "Bootstrap from zero, without a model".

`needs: []` -- no network, no secrets, no API key. Runs anywhere.

    python dropin/bootstrap.py docs/decisions --type Decision [--apply]

Without --apply it prints what it would write and changes nothing.
"""
import argparse
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles default to cp1252 and die on an em dash. The bundle is UTF-8 by
# specification; the terminal should not be what decides whether the build runs.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

RESERVED = {"index.md", "log.md", "README.md"}

_H1 = re.compile(r"^#\s+(.+?)\s*$", re.M)
_FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)

# A chunk opening with any of these is structure, not prose: heading, list item, table
# row, fence, or horizontal rule.
#
# `**` is deliberately NOT here. It was, and it silently discarded every paragraph that
# opens with a bold lead-in — which is most of this project's own prose. Bold-led chunks
# are handled by length below, where a short one is a metadata header and a long one is
# a paragraph.
_NOT_PROSE = re.compile(r"^(#|[-*+]\s|\d+\.\s|\||```|~~~|---\s*$)")


def _extract_description(text: str, limit: int = 200, prefer_blockquote: bool = False) -> str:
    """Extract a description. Ported from project_template's okf.py `_description_fallback`,
    with two corrections learned from running it on this repository's own decision records:

    1. Skip list and table blocks. Decision records open with a `- **Status:**` list that the
       original would have swallowed whole.
    2. Prefer the first prose paragraph *after the first `##` heading*. A paragraph floating
       before any heading is usually front-matter prose, not a summary.

    3. A blockquote wins only when it is the FIRST block after the H1. That position is
       conventionally a summary; a blockquote further down is a pull-quote or an example.
       This replaced a `--prefer-blockquote` flag, which pushed a corpus-specific judgement
       onto the adopter for something the document's own structure already answers.

    `prefer_blockquote` forces the old behaviour for corpora where blockquotes summarize
    wherever they appear.
    """
    body = _H1.sub("", text, count=1)

    # A blockquote in the LEAD position — the first block after the H1 — is conventionally
    # a summary, and is the best description a document can offer. Further down it is a
    # pull-quote or an example, so position decides rather than a flag.
    lead = next((c.strip() for c in re.split(r"\n\s*\n", body) if c.strip()), "")
    if lead.startswith(">"):
        cleaned = " ".join(re.sub(r"^>\s?", "", lead, flags=re.M).split())
        if len(cleaned) >= 12:
            return cleaned[:limit].rsplit(" ", 1)[0].rstrip(".,;:—- ") + "…" \
                if len(cleaned) > limit else cleaned

    blockquote = paragraph = None
    for raw in re.split(r"\n\s*\n", body):
        chunk = raw.strip()
        if not chunk:
            continue
        first = chunk.splitlines()[0].strip()

        if first.startswith(">"):
            cleaned = " ".join(re.sub(r"^>\s?", "", chunk, flags=re.M).split())
            if len(cleaned) >= 12 and blockquote is None:
                blockquote = cleaned
            continue

        if _NOT_PROSE.match(first):
            continue

        cleaned = " ".join(chunk.split())
        if first.startswith("**"):
            # A bold-led chunk is a metadata header (`**Status:** draft`) when it is one
            # short line, and ordinary prose when it runs on. Skipping every bold-led
            # chunk discarded real opening paragraphs; length is the honest discriminator.
            if len(cleaned) < 100:
                continue

        # A paragraph ending in ":" introduces a list, table, or quote -- it is a lead-in,
        # not a summary, and reads as a fragment torn from its context.
        if len(cleaned) >= 12 and not cleaned.endswith(":") and paragraph is None:
            paragraph = cleaned

    picked = (blockquote or paragraph) if prefer_blockquote else (paragraph or blockquote)
    out = (picked or "").strip()
    if len(out) > limit:                       # cut on a word boundary, never mid-word
        out = out[:limit].rsplit(" ", 1)[0].rstrip(".,;:—- ") + "…"
    return out


def _title(text: str, path: Path) -> str:
    m = _H1.search(text)
    if m:
        return m.group(1).strip()
    stem = re.sub(r"^\d{2,4}[-_]", "", path.stem)
    return stem.replace("-", " ").replace("_", " ").strip().title() or path.stem


def _yaml_str(s: str) -> str:
    """Quote only when YAML would otherwise misread it."""
    if not s:
        return '""'
    if re.search(r'^[\s>|@`%*&!\[\]{}#-]|: |:\s*$|["\']|\n', s) or s.strip() != s:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def build(src: Path, ctype: str, scope: str | None, stamp: str,
          prefer_bq: bool = False, refresh: bool = False) -> list[tuple[Path, str, str]]:
    """Return (path, action, frontmatter) for every concept in src."""
    out = []
    for f in sorted(src.glob("*.md")):
        if f.name in RESERVED:
            continue
        text = f.read_text(encoding="utf-8")
        m = _FM.match(text)
        if m:
            # Refresh only what this tool owns. `generated.by` naming this process is the
            # proof that the description was EXTRACTED rather than written by a person or
            # drafted by a model -- and recomputing an extracted field is a tier-`[]`
            # operation. Anything else is somebody's work and is left alone.
            if refresh and "process:okfm-bootstrap" in m.group(1):
                new_desc = _extract_description(text[m.end():], prefer_blockquote=prefer_bq)
                block = re.sub(r"^description: .*(?:\n[ \t]+\S.*)*$",
                               f"description: {_yaml_str(new_desc)}", m.group(1), count=1,
                               flags=re.M)
                if block != m.group(1):
                    out.append((f, "refresh", f"---\n{block}\n---\n" + text[m.end():]))
                    continue
            out.append((f, "skip (already a concept)", ""))
            continue

        # Hash the TEXT, never the raw bytes. `read_text` applies universal-newline
        # translation, so an LF and a CRLF copy of identical content hash the same —
        # which is what keeps `okfm_captured` stable across platforms and stops the
        # mesh reporting drift that did not happen. Switching to read_bytes() here
        # would be a silent correctness regression, not an optimization.
        sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        lines = [
            "---",
            f"type: {ctype}",
            f"title: {_yaml_str(_title(text, f))}",
            f"description: {_yaml_str(_extract_description(text, prefer_blockquote=prefer_bq))}",
            # draft, never stable: an EXTRACTED description is not a reviewed one. With no
            # `verified` entry either, the trust machinery reports this accurately with no
            # special case -- which is the whole reason a no-model bootstrap is honest.
            "status: draft",
            f'generated: {{ by: "process:okfm-bootstrap", at: {stamp} }}',
            "sources:",
            "  - id: self",
            f"    resource: /{f.name}",
            "    okfm_role: subject",
            f'    okfm_captured: {{ hash: "sha256:{sha}", at: {stamp[:10]} }}',
        ]
        if scope:
            lines.append(f"okfm_scope: {scope}")
        lines += ["---", ""]
        out.append((f, "write", "\n".join(lines)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("src", type=Path, help="directory of markdown to bootstrap")
    ap.add_argument("--type", required=True, help="OKF type for every concept found")
    ap.add_argument("--scope", default=None, help="okfm_scope to stamp (optional)")
    ap.add_argument("--apply", action="store_true", help="write; otherwise dry-run")
    ap.add_argument("--prefer-blockquote", action="store_true",
                    help="corpora whose files open with a blockquote summary")
    ap.add_argument("--refresh", action="store_true",
                    help="recompute extracted descriptions on concepts this tool created")
    a = ap.parse_args()

    if not a.src.is_dir():
        print(f"not a directory: {a.src}", file=sys.stderr)
        return 2

    # No wall-clock in the value itself beyond the date -- a rerun must not churn the diff.
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    plan = build(a.src, a.type, a.scope, stamp, a.prefer_blockquote, a.refresh)

    wrote = skipped = 0
    for path, action, fm in plan:
        if action.startswith("skip"):
            print(f"  skip   {path.name}")
            skipped += 1
            continue
        desc = re.search(r"^description: (.*)$", fm, re.M).group(1)
        verb = action if action == "refresh" else ("write " if a.apply else "would ")
        print(f"  {verb:7} {path.name}")
        print(f"           {desc[:96]}")
        if a.apply:
            if action == "refresh":
                # `fm` is the whole rewritten file, not a prefix.
                path.write_text(fm, encoding="utf-8", newline="\n")
            else:
                path.write_text(fm + path.read_text(encoding="utf-8"),
                                encoding="utf-8", newline="\n")
        wrote += 1

    print(f"\n{wrote} concept(s) {'written' if a.apply else 'planned'}, {skipped} skipped")
    if not a.apply and wrote:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
