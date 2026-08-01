"""Shared plumbing for the drop-in build: locating things, and reading frontmatter.

Nothing here knows where it was installed. The folder is pasted into a stranger's project
and must work from wherever it lands, so every path is derived from this file's own
location — never from a repository root, a working directory, or an environment variable.

Python 3.13, standard library only.
"""
import json
import re
import sys
from pathlib import Path

def utf8_stdout() -> None:
    """Windows consoles default to cp1252 and raise on an em dash or a box-drawing
    character. The bundle is UTF-8 by specification; a terminal's default encoding should
    not be what decides whether the build runs.

    Called at import here, and by every entry point — including the dispatcher, which does
    not otherwise depend on this module. It was reimplemented three times before being
    hoisted, which is a good sign it belongs in one place.
    """
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


utf8_stdout()

# The folder this file lives in, and the project it was dropped into.
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

RESERVED = {"index.md", "log.md", "README.md", "CHANGELOG.md", "CONTRIBUTING.md"}

# Directories never worth scanning. Cheap to list, and the alternative is an adopter's
# first run producing three thousand concepts from node_modules.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
    "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    "dist", "build", "target", ".next", ".nuxt", "vendor",
    ".idea", ".vscode", ".github", "site-packages",
}

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def scalar(block: str, key: str):
    """Read one top-level scalar from a frontmatter block. Handles quotes and folded lines."""
    m = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    v = " ".join(p.strip() for p in m.group(1).splitlines()).strip()
    if v[:1] in "\"'" and v[-1:] in "\"'":
        v = v[1:-1]
    return v.replace('\\"', '"') or None


def frontmatter(path: Path):
    """Return (block, body) for a concept, or (None, None) if the file is not one."""
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    return (m.group(1), text[m.end():]) if m else (None, None)


def is_concept(path: Path) -> bool:
    block, _ = frontmatter(path)
    return bool(block and scalar(block, "type"))


# ── configuration ──────────────────────────────────────────────────────────────
# Looked for in three places, in order, then synthesized. The synthesized config is
# WRITTEN OUT, so the first thing an adopter edits is a file the tool already made for
# them rather than a blank page and a manual.

CONFIG_NAME = "okfm.json"


def find_config() -> tuple[Path | None, dict]:
    for candidate in (PROJECT / CONFIG_NAME, HERE / CONFIG_NAME):
        if candidate.is_file():
            return candidate, json.loads(candidate.read_text(encoding="utf-8"))
    return None, {}


def discover_sources(root: Path, limit: int = 40) -> list[str]:
    """Directories under `root` that hold markdown worth turning into concepts.

    Deliberately shallow and conservative. Most projects have many folders under docs/
    and want concepts for only some, so this is a starting point to prune -- which is why
    the result is written to config rather than recomputed on every run.
    """
    found = []
    for d in sorted(root.rglob("*")):
        if not d.is_dir():
            continue
        rel = d.relative_to(root)
        parts = set(rel.parts)
        if parts & SKIP_DIRS or d.resolve() == HERE:
            continue
        if HERE in d.resolve().parents:          # never scan our own output
            continue
        if len(rel.parts) > 3:                   # depth guard
            continue
        mds = [f for f in d.glob("*.md") if f.name not in RESERVED]
        if len(mds) >= 2:                        # one stray README is not a bundle
            found.append(rel.as_posix())
        if len(found) >= limit:
            break

    # Root-level markdown counts too, if there is enough of it.
    root_mds = [f for f in root.glob("*.md") if f.name not in RESERVED]
    if len(root_mds) >= 2:
        found.insert(0, ".")
    return found


def synthesize_config(root: Path) -> dict:
    sources = discover_sources(root)
    return {
        "okfm": "0.2.1",
        "pack": None,
        "_generated": (
            "Written by the OKFM drop-in build on its first run. `sources` lists what it "
            "found; delete a line to stop building concepts for it. Everything else is a "
            "sensible default you can ignore."
        ),
        "sources": [{"path": s, "type": "Document"} for s in sources],
        "bundle": "./bundle",
        "mode": "mirror",
        "viewer": {"path": "../okfm-viewer.html"},
        "index": {"max_concepts": 60, "priority_types": []},
        "exclude_scopes": ["guide"],
    }


def load_or_create_config(write: bool = True) -> tuple[Path, dict, bool]:
    """Return (path, config, created). Synthesizes and writes one if none exists."""
    path, cfg = find_config()
    if path is not None:
        return path, cfg, False

    cfg = synthesize_config(PROJECT)
    path = HERE / CONFIG_NAME
    if write:
        path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path, cfg, True


# ── vocabularies ───────────────────────────────────────────────────────────────
# Controlled lists live in files, not in code, so a pack can overlay them without a
# fork. The shape is deliberately the smallest useful subset of YAML -- `family:` then
# indented `- term` lines, with `#` comments -- which needs about ten lines to read and
# no dependency. Anything richer would be a reason to reach for a real parser, and a
# controlled vocabulary that needs a real parser has stopped being a controlled list.

VOCAB = HERE / "vocab"


def load_vocab(name: str, overlays: list[Path] | None = None) -> dict[str, list[str]]:
    """Read `vocab/<name>.yaml` plus any overlays, merged by family."""
    out: dict[str, list[str]] = {}
    for path in [VOCAB / f"{name}.yaml", *(overlays or [])]:
        if not path.is_file():
            continue
        family = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip():
                continue
            if not line.startswith((" ", "\t", "-")) and line.rstrip().endswith(":"):
                family = line.rstrip()[:-1].strip()
                out.setdefault(family, [])
            elif family and line.lstrip().startswith("- "):
                term = line.lstrip()[2:].strip()
                if term and term not in out[family]:
                    out[family].append(term)
    return out


def vocab_terms(name: str, overlays: list[Path] | None = None) -> set[str]:
    """Every term across every family — what a validator actually checks against."""
    return {t for terms in load_vocab(name, overlays).values() for t in terms}


def bundle_root(cfg: dict) -> Path:
    """Where concepts are written. Inside the dropped folder by default, so that deleting
    the folder removes everything the tool ever created and leaves the project as it was."""
    return (HERE / cfg.get("bundle", "./bundle")).resolve()


def configured_bundles(cfg: dict) -> dict[str, Path]:
    """Bundles to validate. Supports both config shapes: the drop-in's `bundle` plus
    `sources`, and the fuller `bundles` mapping a hosted mesh uses."""
    if "bundles" in cfg:
        base = PROJECT if (PROJECT / CONFIG_NAME).is_file() else HERE
        return {k: (base / v).resolve() for k, v in cfg["bundles"].items()}
    root = bundle_root(cfg)
    if not root.is_dir():
        return {}
    subs = {d.name: d for d in sorted(root.iterdir()) if d.is_dir()}
    return subs or {"bundle": root}
