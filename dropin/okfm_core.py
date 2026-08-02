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


def normalize(cfg: dict) -> dict:
    """Grouped for a person to read; flat for the code that reads it.

    The config file has four groups — `build`, `read`, `stores`, `federation` — because a
    dozen sibling keys at the top level stops being a file you can take in at a glance and
    starts being one you search. The tooling wants them flat, so the lifting happens once,
    here, instead of every reader learning the grouping.

    Flat keys still win when present. Nobody is running an old config yet, but a normalizer
    that silently overrides what someone wrote is a worse failure than one that does not.
    """
    out = dict(cfg)
    b = cfg.get("build") or {}
    r = cfg.get("read") or {}
    for key, src, name, default in (
        ("bundle", b, "out", ".okfm"),
        ("mesh", b, "mesh", "mesh"),
        ("mode", b, "mode", "mirror"),
        ("sources", b, "sources", None),
        ("vocab_overlays", b, "vocab_overlays", None),
        ("web_ui", r, "web_ui", None),
        ("index", r, "index", None),
        ("exclude_scopes", r, "exclude_scopes", None),
    ):
        if key not in out and (name in src or default is not None):
            out[key] = src.get(name, default)
    if "discover" not in out and b:
        keys = ("root", "root_files", "exclude", "include")
        out["discover"] = {k: b[k] for k in keys if k in b}
    return out


def find_config() -> tuple[Path | None, dict]:
    for candidate in (PROJECT / CONFIG_NAME, HERE / CONFIG_NAME):
        if candidate.is_file():
            return candidate, normalize(json.loads(candidate.read_text(encoding="utf-8")))
    return None, {}


MAX_DEPTH = 4


def docs_root(cfg: dict, root: Path) -> Path:
    """The directory to scan. `docs/` when it exists, otherwise the project itself.

    Nearly every project keeps its documentation in `docs/`, and a first run that produces
    concepts for the documentation is obviously right where one that also sweeps up `src/`,
    a vendored SDK and three lockfiles is obviously wrong and takes ten minutes to undo.
    Scanning the whole tree is the fallback, not the default -- and `discover.root` overrides
    both.
    """
    named = (cfg.get("discover") or {}).get("root")
    if named:
        return (root / named).resolve()
    return root / "docs" if (root / "docs").is_dir() else root


def scan_roots(cfg: dict, root: Path) -> list[Path]:
    """Every tree this build reads: the docs root, then whatever `include` names.

    Two keys, because an adopter has exactly two things to say about where knowledge lives
    and neither can be said with the other:

        "build": { "root": "docs", "exclude": ["archive"], "include": ["adr", "rfcs"] }

    `exclude` drops a folder **inside** a scan root. `include` adds a tree **outside** one --
    you cannot exclude your way to a directory the scan never reached. An `include` path that
    turns out to be inside a root already being scanned is dropped rather than scanned twice;
    it is inside, so it is `exclude`'s business.
    """
    roots = [docs_root(cfg, root)]
    for rel in (cfg.get("discover") or {}).get("include", []):
        p = (root / rel).resolve()
        if p.is_dir() and not any(p == r or r in p.parents for r in roots):
            roots.append(p)
    return roots


def _project_parts(directory: Path, root: Path) -> tuple[str, ...]:
    """Path parts relative to the project, minus any `..` an included path walked up through."""
    rel = directory.relative_to(root, walk_up=True)
    return tuple(p for p in rel.parts if p != "..")


def _name_bundles(found: list[tuple[Path, Path]], root: Path) -> list[dict]:
    """Bundle ids: the folder's own name, so `docs/guides/` is `guides` and not `docs-guides`.

    A collision renames **every** folder holding that name, not just the second one reached.
    Otherwise which folder keeps the short id depends on scan order, and adding a directory
    next month silently renames somebody else's bundle -- which, since the id appears in every
    cross-bundle relation target, breaks edges in bundles nobody touched.
    """
    holders: dict[str, list[tuple[Path, Path]]] = {}
    for pair in found:
        holders.setdefault(pair[0].name, []).append(pair)

    def dashed(directory: Path, base: Path) -> str:
        return "-".join(directory.relative_to(base).parts) or base.name

    out = []
    for directory, base in found:
        group = holders[directory.name]
        name = directory.name
        if len(group) > 1:
            # Relative to its own scan root first; if two roots produce the same path,
            # fall back to the project-relative one, which cannot collide.
            name = dashed(directory, base)
            if sum(1 for d, b in group if dashed(d, b) == name) > 1:
                name = "-".join(_project_parts(directory, root))
        out.append({"path": directory.relative_to(root, walk_up=True).as_posix(),
                    "bundle": name, "type": "Document"})
    return out


def discover_sources(root: Path, cfg: dict | None = None, limit: int = 60) -> list[dict]:
    """One OKF per folder of documents.

    Every directory under a scan root that holds at least one non-reserved markdown file
    becomes its own bundle, and each root's own loose files become one too. That is the
    arrangement people already have -- `docs/guides/`, `docs/architecture/`, `docs/adr/` are
    separate because they are about separate things -- so mirroring it needs no explanation
    and no configuration to get right.

    `root_files: false` drops the loose documents at the top of a root, which in many projects
    are a landing page and two stubs rather than knowledge. `exclude` and `include` are
    described on `scan_roots`.

    Discovery runs on **every** build rather than being frozen into the config on the first
    one. A folder added next month should get an OKF without anyone remembering to declare it;
    that is only true if the scan is live, which is also what makes `exclude` mean something
    more than "delete a line".
    """
    cfg = cfg or {}
    d = cfg.get("discover") or {}
    excluded = [x.strip("/") for x in d.get("exclude", [])]

    def skipped(directory: Path, base: Path) -> bool:
        """An `exclude` entry reads naturally either relative to the root it sits under
        (`archive`) or relative to the project (`docs/archive`), and people write both. Both
        match: when a list called `exclude` is ambiguous, excluding is the safe reading.
        """
        forms = {directory.relative_to(base).as_posix(),
                 "/".join(_project_parts(directory, root))}
        return any(f == x or f.startswith(x + "/") for f in forms for x in excluded)

    def documents(directory: Path) -> bool:
        return any(f.name not in RESERVED for f in directory.glob("*.md"))

    found: list[tuple[Path, Path]] = []          # (directory, the scan root it came from)
    seen: set[Path] = set()

    def add(directory: Path, base: Path) -> None:
        if directory.resolve() not in seen:
            seen.add(directory.resolve())
            found.append((directory, base))

    for base in scan_roots(cfg, root):
        if len(found) >= limit:
            break
        if d.get("root_files", True) and not skipped(base, base) and documents(base):
            add(base, base)
        for directory in sorted(base.rglob("*")):
            if len(found) >= limit:
                break
            if not directory.is_dir():
                continue
            rel = directory.relative_to(base)
            if set(rel.parts) & SKIP_DIRS or len(rel.parts) > MAX_DEPTH:
                continue
            if skipped(directory, base):
                continue
            if directory.resolve() == HERE or HERE in directory.resolve().parents:
                continue                         # never scan our own output
            if documents(directory):
                add(directory, base)

    return _name_bundles(found, root)


def resolve_sources(cfg: dict, root: Path = PROJECT) -> list[dict]:
    """The source folders this build will read.

    An explicit `sources` list wins outright -- someone who wrote one meant it, and silently
    adding to it would be worse than not discovering at all. Otherwise the docs root is
    scanned live.
    """
    explicit = cfg.get("sources")
    if explicit:
        return [s if isinstance(s, dict) else {"path": s, "type": "Document"} for s in explicit]
    return discover_sources(root, cfg)


def synthesize_config(root: Path) -> dict:
    scan = docs_root({}, root)
    return {
        "okfm": "0.2.1",
        "pack": None,
        "_generated": (
            "Written by the OKFM drop-in build on its first run. Every folder of documents "
            "under `build.root` gets its own OKF in `build.out`, plus one for the loose files "
            "at the top and a mesh OKF over all of them. `build.exclude` drops a folder inside "
            "the root; `build.include` adds a tree outside it; `root_files: false` skips the "
            "loose files. Everything else is a sensible default you can ignore."
        ),
        "build": {
            "root": scan.relative_to(root).as_posix() or ".",
            "root_files": True,
            "exclude": [],
            "include": [],
            "out": ".okfm",
            "mesh": "mesh",
            "mode": "mirror",
            "vocab_overlays": [],
        },
        "read": {
            "web_ui": {"path": "../okfm-web-ui.html"},
            "index": {"max_concepts": 60, "priority_types": []},
            "exclude_scopes": ["guide"],
        },
        "stores": {},
        "federation": {"registry": None},
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
    """Where concepts are written: `<project>/.okfm`, one subfolder per bundle.

    One rule covers both arrangements. Paste this folder in as `.okfm/` and the bundles land
    beside the tool, so a single hidden folder holds everything OKFM and `rm -rf .okfm` leaves
    the project exactly as it was. Keep the tool somewhere else — as this repository does —
    and `.okfm/` is still where the mesh lives.

    Either way the adopter's own documents are never written into. That is the property worth
    protecting: `docs/` belongs to them, `.okfm/` belongs to the tool.
    """
    return (PROJECT / cfg.get("bundle", ".okfm")).resolve()


def configured_bundles(cfg: dict) -> dict[str, Path]:
    """Bundles to validate. Supports both config shapes: the drop-in's `bundle` plus
    `sources`, and the fuller `bundles` mapping a hosted mesh uses."""
    if "bundles" in cfg:
        base = PROJECT if (PROJECT / CONFIG_NAME).is_file() else HERE
        return {k: (base / v).resolve() for k, v in cfg["bundles"].items()}
    root = bundle_root(cfg)
    if not root.is_dir():
        return {}
    # A directory holding no concepts is not a bundle. This matters because the tool can be
    # pasted in AS `.okfm/`, which puts `vocab/` and `references/` beside the bundles --
    # listing them as empty bundles is noise in every report the validator produces.
    subs = {d.name: d for d in sorted(root.iterdir())
            if d.is_dir() and any(is_concept(f) for f in d.rglob("*.md"))}
    return subs or {"bundle": root}
