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

    python scripts/bootstrap.py docs/decisions --type Decision [--apply]

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

# A chunk that opens with any of these is structure, not prose: heading, list item,
# table row, bold metadata block, fence, or horizontal rule.
_NOT_PROSE = re.compile(r"^(#|[-*+]\s|\d+\.\s|\||\*\*|```|~~~|---\s*$)")


def _extract_description(text: str, limit: int = 200, prefer_blockquote: bool = False) -> str:
    """Extract a description. Ported from project_template's okf.py `_description_fallback`,
    with two corrections learned from running it on this repository's own decision records:

    1. Skip list and table blocks. Decision records open with a `- **Status:**` list that the
       original would have swallowed whole.
    2. Prefer the first prose paragraph *after the first `##` heading*. A paragraph floating
       before any heading is usually front-matter prose, not a summary.

    `prefer_blockquote` restores the original preference. It was right for the corpus it was
    written against -- those specs open with a `> Layer note` summary -- and wrong here, where
    blockquotes are pull-quotes and examples. Corpus convention, not a universal.
    """
    body = _H1.sub("", text, count=1)
    regions = []
    parts = body.split("\n## ", 1)
    if len(parts) > 1 and "\n" in parts[1]:
        # Drop the remainder of the heading LINE itself -- the split consumed its "## "
        # marker, so without this the heading text reads as the section's first paragraph.
        regions.append(parts[1].split("\n", 1)[1])
    regions.append(body)                      # fall back to the whole body

    for region in regions:
        blockquote = paragraph = None
        for raw in re.split(r"\n\s*\n", region):
            chunk = raw.strip()
            if not chunk:
                continue
            first = chunk.splitlines()[0].strip()
            if first.startswith(">"):
                cleaned = " ".join(re.sub(r"^>\s?", "", chunk, flags=re.M).split())
                if len(cleaned) >= 12 and blockquote is None:
                    blockquote = cleaned
            elif _NOT_PROSE.match(first):
                continue
            else:
                cleaned = " ".join(chunk.split())
                # A paragraph ending in ":" introduces a list, table, or quote -- it is a
                # lead-in, not a summary, and reads as a fragment torn from its context.
                if len(cleaned) >= 12 and not cleaned.endswith(":") and paragraph is None:
                    paragraph = cleaned
        picked = (blockquote or paragraph) if prefer_blockquote else (paragraph or blockquote)
        if picked:
            break
    else:
        picked = None

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
          prefer_bq: bool = False) -> list[tuple[Path, str, str]]:
    """Return (path, action, frontmatter) for every concept in src."""
    out = []
    for f in sorted(src.glob("*.md")):
        if f.name in RESERVED:
            continue
        text = f.read_text(encoding="utf-8")
        if _FM.match(text):
            out.append((f, "skip (already a concept)", ""))
            continue

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
            f'    okfm_captured: {{ hash: "sha256:{sha[:16]}...", at: {stamp[:10]} }}',
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
    a = ap.parse_args()

    if not a.src.is_dir():
        print(f"not a directory: {a.src}", file=sys.stderr)
        return 2

    # No wall-clock in the value itself beyond the date -- a rerun must not churn the diff.
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
    plan = build(a.src, a.type, a.scope, stamp, a.prefer_blockquote)

    wrote = skipped = 0
    for path, action, fm in plan:
        if action.startswith("skip"):
            print(f"  skip   {path.name}")
            skipped += 1
            continue
        desc = re.search(r"^description: (.*)$", fm, re.M).group(1)
        print(f"  {'write ' if a.apply else 'would '} {path.name}")
        print(f"           {desc[:96]}")
        if a.apply:
            path.write_text(fm + path.read_text(encoding="utf-8"), encoding="utf-8")
        wrote += 1

    print(f"\n{wrote} concept(s) {'written' if a.apply else 'planned'}, {skipped} skipped")
    if not a.apply and wrote:
        print("dry run -- pass --apply to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
