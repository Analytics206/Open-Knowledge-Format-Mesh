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

    `line_buffering` matters more than it looks. Python block-buffers stdout when it is not a
    terminal, while a subprocess writes to the same descriptor directly — so `okfm.py`'s stage
    banners were flushed at exit and every one of them landed *after* the output it labelled.
    Piped, redirected, in CI, or read by an agent, a traceback appeared above the banner naming
    the stage that produced it. Fine in a live terminal and actively misleading everywhere
    else, which is the half that gets debugged.
    """
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


utf8_stdout()

# The folder this file lives in, and the project it was dropped into.
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def reject_unknown(argv: list[str], allowed: tuple[str, ...]) -> None:
    """Exit on a flag nothing reads, naming it and what is accepted.

    Several scripts test `"--check" in sys.argv` and ignore the rest, so a mistyped or
    invented flag did nothing and exited 0 — indistinguishable from having worked. The viewer
    recommended `okfm view --serve` in two places; running it printed a success line and
    served nothing, and there was no way to tell whether it had run, failed, or been ignored.

    A flag that is silently swallowed is worse than one that errors, because the user believes
    the thing they asked for happened.
    """
    unknown = [a for a in argv if a.startswith("-") and a.split("=", 1)[0] not in allowed]
    if unknown:
        print(f"unknown option: {' '.join(unknown)}", file=sys.stderr)
        print(f"this command accepts: {', '.join(allowed) or '(no options)'}", file=sys.stderr)
        raise SystemExit(2)

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

# `okfm_relations`, in both legal YAML forms. Lives here because it was written twice —
# once in the validator, once in the viewer bake — and the validator's copy required the
# comma between the two keys, so block form was checked by neither and drawn by neither.
# Two implementations of one rule agree until somebody fixes one of them.
_REL_BLOCK = re.compile(r"^okfm_relations:\s*\n((?:[ \t]*[-{].*\n?|[ \t]+\w+:.*\n?)+)", re.M)
_REL_PAIR = re.compile(r"predicate:\s*([\w_]+)\s*[,\n]\s*(?:[ \t]*)target:\s*([^\s},]+)")


# Who did a thing. Three kinds, and the prefix is load-bearing rather than decorative:
# `_owned()` reads it to decide what the build may overwrite, `enrich.py` reads it to decide
# whose work is already drafted, `revalidate` refuses anything but a human, and the trust
# tier a reader sees is derived from it.
#
# There were four conventions in circulation. Spec 6.3 offered `<producer>/<version>`,
# `human:<id>` and `process:<id>`; AGENTS.md told authors to write `<your-agent>/<model>`;
# and `agent:` — used by 28 of this corpus's 80 actors — appeared in no document at all as a
# legal form. A field the ownership model keys on cannot have an undocumented majority value.
ACTOR_KINDS = ("human", "agent", "process")


def actor_kind(value: str | None) -> str | None:
    """`human`, `agent`, `process`, or None when the prefix is not one of them.

    A real prefix match. `trust()` used to ask whether `human:` appeared anywhere in the
    line, so `nonhuman:bot` was classified as a human verifier — the highest trust tier,
    awarded on a substring.
    """
    if not value:
        return None
    kind = str(value).strip().strip("\"'").split(":", 1)[0]
    return kind if kind in ACTOR_KINDS else None


def actor_of(block: str, key: str) -> str | None:
    """The `by:` inside a `generated:`/`verified:` mapping, unquoted."""
    raw = scalar(block, key) or ""
    m = re.search(r'by:\s*"?([^",}\s]+)', raw)
    return m.group(1) if m else None


def trust(block: str) -> str | None:
    """`human`, `machine`, or None when nothing has verified this. DERIVED, never stored.

    Read from the actor's PREFIX, not from whether `human:` appears somewhere on the line.
    The substring test awarded the top tier to `nonhuman:bot`, which is the worst direction
    for that mistake to run — a false `unverified` is a nuisance, a false `human` is a review
    nobody performed.

    Lives here because a second reader was about to copy it. Every rule this project has had
    to reunify — RESERVED, the config schema, the relation parser — was two implementations
    that agreed until one was fixed.
    """
    if not re.search(r"^verified:", block, re.M):
        return None
    return "human" if actor_kind(actor_of(block, "verified")) == "human" else "machine"


def parse_relations(block: str) -> list[tuple[str, str]]:
    """(predicate, target) for every typed edge in a frontmatter block.

    Accepts the inline flow mapping and the indented block form. Both are legal YAML and
    spec 7.3 shows both; a parser that reads only one silently drops edges, and a dropped
    edge is invisible in exactly the place traversal treats edges as fact.
    """
    m = _REL_BLOCK.search(block)
    return _REL_PAIR.findall(m.group(1)) if m else []


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
        ("bundle_tags", b, "bundle_tags", None),
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


def reserved_only_dirs(root: Path, cfg: dict | None = None) -> list[str]:
    """Folders under a scan root whose only markdown is a reserved filename.

    They hold no documents, so `discover_sources` never makes them bundles — which is right: a
    directory containing one `README.md` is a signpost, not knowledge. But it is dropped a
    level *above* the per-file skip note, so nothing said anything at all, and a folder
    silently absent is indistinguishable from one the scan never reached.

    `docs/api/README.md` is an ordinary shape. Naming it lets an adopter decide whether that
    README is a nav page they are happy to lose or the summary they most wanted indexed.
    """
    cfg = cfg or {}
    d = cfg.get("discover") or {}
    excluded = [x.strip("/") for x in d.get("exclude", [])]
    out = []
    for base in scan_roots(cfg, root):
        for directory in sorted(base.rglob("*")):
            if not directory.is_dir():
                continue
            rel = directory.relative_to(base)
            if set(rel.parts) & SKIP_DIRS or len(rel.parts) > MAX_DEPTH:
                continue
            forms = {rel.as_posix(), "/".join(_project_parts(directory, root))}
            if any(f == x or f.startswith(x + "/") for f in forms for x in excluded):
                continue
            if directory.resolve() == HERE or HERE in directory.resolve().parents:
                continue
            md = list(directory.glob("*.md"))
            if md and all(f.name in RESERVED for f in md):
                out.append(directory.relative_to(root, walk_up=True).as_posix())
    return out


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
            # Relative to the PROJECT, which is what `config_schema` declares for this key.
            # It said `../okfm-web-ui.html` for a long time, which the validator rejects for
            # containing `..` — so the build wrote a config that failed its own check. Not on
            # the first run, when no config exists yet and validation passes trivially, but on
            # the second, after the adopter already believed it worked.
            "web_ui": {"path": "./okfm-web-ui.html"},
            "index": {"max_concepts": 60, "priority_types": []},
            "exclude_scopes": ["guide"],
        },
        "stores": {},
        "federation": {"registry": None},
    }


def load_or_create_config(write: bool = True) -> tuple[Path, dict, bool]:
    """Return (path, config, created). Synthesizes and writes one if none exists.

    Written to the **project**, which is where `find_config` looks first and where every
    path inside it is resolved from. It used to be written to `HERE` — inside the drop-in —
    and that is the adopter's file in the tool's folder:

    * It is the one file the README tells them to edit, and it landed in a dot-folder among
      fourteen Python modules, indistinguishable from the machinery.
    * Replacing the drop-in to upgrade puts their configuration in the blast radius. The
      README's install command *is* the upgrade command, and running it a second time
      silently nests a copy instead of replacing anything — so the adopter is left running
      the old code with the new code sitting inside it, and no error either way.
    * This repository's own config sits at the project root. The tool putting it somewhere
      else than the builder did is the tell.

    A config already at `HERE` still loads, because `find_config` still looks there. Nothing
    an adopter has today moves.
    """
    path, cfg = find_config()
    if path is not None:
        return path, cfg, False

    cfg = synthesize_config(PROJECT)
    path = PROJECT / CONFIG_NAME
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
    """Read core's `vocab/<name>.yaml`, then the same filename in each overlay DIRECTORY.

    An overlay is a directory, and the **filename inside it names the family**. That is the
    whole safety property: `reason_codes.yaml` can contribute to `reason_codes` and to
    nothing else, because that is the only name this function will open for it.

    Overlays used to be a flat list of file paths, appended to every family's read. One
    pack file declaring one reason code therefore registered that term as a valid
    `reason_code`, `type`, `role` **and `predicate`** — measured, not theorised. The last
    one is the damage: predicates are the single vocabulary `check_bundles` rejects on,
    because traversal and drift propagation read a typed edge as fact. So the mechanism for
    adding domain words was also, silently, the mechanism for widening the one list that is
    controlled on purpose.

    Fixing the read order would have fixed this instance. Making the family come from the
    filename makes the next instance unable to happen.
    """
    out: dict[str, list[str]] = {}
    for path in [VOCAB / f"{name}.yaml", *(d / f"{name}.yaml" for d in (overlays or []))]:
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


def pack_dirs(cfg: dict) -> tuple[list[Path], list[str]]:
    """Every vocabulary overlay directory this config asks for, plus what did not resolve.

    Two keys reach the same place, so they are resolved in one function rather than two:
    `pack` names the adopter's domain pack (§13.2 — "a directory of YAML plus at most one
    adapter file"), and `build.vocab_overlays` is the escape hatch for a mesh drawing on
    more than one. A pack is listed first so core loses to the pack and the pack loses to
    an explicit overlay, which is the order an adopter would guess.

    **`pack` is a path, not a bare name.** §13.4's example writes `"pack": "warehouse"`, and
    a bare name needs a search path, a search path needs a resolution order, and a
    resolution order is one more thing that fails silently when it picks the wrong
    directory. A path is checked by the config machinery that already exists. Recorded in
    DR-0014; the spec note in §13.4 says the same.

    A named pack that does not resolve is returned as a problem rather than skipped. Skipping
    it would validate the mesh against core vocabulary alone, so every domain term reports
    "not in core vocabulary" — a hundred confusing errors whose actual cause is one wrong
    path, which is the shape of failure this project has paid for twice already.
    """
    dirs, missing = [], []
    for raw in ([cfg["pack"]] if cfg.get("pack") else []) + list(cfg.get("vocab_overlays") or []):
        root = (PROJECT / str(raw)).resolve()
        if not root.is_dir():
            missing.append(str(raw))
            continue
        # A pack's vocabulary sits at `<pack>/vocab/`, exactly as core's does at
        # `dropin/vocab/`. Same shape in both places, and it leaves the pack root free for
        # the one adapter file §13.2 allows without mixing code in with the word lists.
        # A pack with no `vocab/` is legal — an adapter-only pack adds no vocabulary.
        dirs.append(root / "vocab")
    return dirs, missing


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
