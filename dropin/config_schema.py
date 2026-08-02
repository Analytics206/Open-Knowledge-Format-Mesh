#!/usr/bin/env python3
"""The rules `okfm.json` must satisfy, written once as data.

Two things validate a config: `check_config.py` in the terminal, and the config panel in
the web UI. Writing the rules twice would mean two lists of keys that agree until somebody
adds a key to one of them, and the disagreement would be silent — the UI would accept a
config the build rejects, which is worse than no UI. So the rules are a table here, and
`bake_web_ui.py` bakes this same table into the page.

The split between the two is honest and worth stating: **the browser checks everything that
does not need a filesystem** — types, enums, ranges, unknown keys, credential handles — and
the terminal checks those *plus* whether the paths exist. A page opened from `file://` cannot
see your disk, so it says so rather than guessing.

`needs: []` — no network, no secrets, no model.
"""
import difflib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SPEC_VERSION = "0.2.1"

# Where "on my own machine" stops. DR-0008 rejected a `network` rung on the exposure ladder
# because nothing needed the open internet without a credential; an endpoint outside this
# set is the first thing that could, so it is worth a line of output rather than silence.
LOOPBACK = ("localhost", "127.0.0.1", "::1", "0.0.0.0")

# A credential in a config file is a credential in git history. Values name a handle that
# something else resolves; the prefixes are a closed list so a pack cannot quietly widen it.
HANDLE_PREFIXES = ("env", "file", "keyring", "op", "vault", "aws-sm", "gcp-sm", "azure-kv")
_HANDLE = re.compile(r"^(" + "|".join(HANDLE_PREFIXES) + r"):\S+$")

# ── the table ──────────────────────────────────────────────────────────────────
# path      dotted location in the config
# kind      string | bool | int | enum | path | paths | strings | pathmap | stores | any
# base      what a relative path is relative to: "project" or "root" (build.root)
# exists    "dir" | "file" — what the path should be; absent means do not look
# soft      a missing path is a warning, not an error (it may not exist yet)
# nullable  null is a legal value
# required  the KEY must be present, even if its value is null
# label     what the web UI calls it
# help      one line, shown in the form and quoted in errors — written once, read in both
FIELDS = [
    {"path": "okfm", "kind": "string", "default": SPEC_VERSION, "required": True,
     "label": "Profile version",
     "help": "Which OKFM profile this config is written against."},
    {"path": "pack", "kind": "string", "default": None, "required": True, "nullable": True,
     "label": "Domain pack",
     "help": "A domain vocabulary overlay, or null for none. The key must be present even "
             "when empty — a mesh with no domain is a normal mesh, not a missing answer."},

    {"path": "build.root", "kind": "path", "base": "project", "exists": "dir",
     "default": "docs", "label": "Documents root",
     "help": "The folder to read. Every subfolder of documents under it becomes a bundle."},
    {"path": "build.root_files", "kind": "bool", "default": True,
     "label": "Bundle the loose files",
     "help": "Turn the documents sitting directly in the root into their own bundle. Set "
             "false when they are a landing page and two stubs rather than knowledge."},
    {"path": "build.exclude", "kind": "paths", "base": "root", "exists": "dir", "soft": True,
     "default": [], "label": "Exclude — folders inside the root",
     "help": "Subtrees to skip, relative to the root. An archive of superseded documents "
             "is the usual first entry."},
    {"path": "build.include", "kind": "paths", "base": "project", "exists": "dir",
     "soft": True, "default": [], "label": "Include — trees outside the root",
     "help": "Folders outside the root to read as well, relative to the project. This is "
             "the only way to reach one; nothing scans your project on its own."},
    {"path": "build.out", "kind": "path", "base": "project", "default": ".okfm",
     "label": "Output folder",
     "help": "Where bundles are written. Your documents are never written to."},
    {"path": "build.mesh", "kind": "string", "default": "mesh",
     "label": "Mesh bundle name",
     "help": "The generated OKF whose concepts are the other OKFs — the one to read first."},
    {"path": "build.mode", "kind": "enum", "choices": ["mirror", "in-place"],
     "default": "mirror", "label": "Mode",
     "help": "mirror writes concepts beside your files and never touches them; in-place "
             "adds frontmatter to the files themselves."},
    {"path": "build.vocab_overlays", "kind": "paths", "base": "project", "exists": "file",
     "default": [], "label": "Vocabulary overlays",
     "help": "Extra predicate, type and reason-code files, merged by family."},
    {"path": "build.sources", "kind": "any", "default": None, "nullable": True,
     "label": "Explicit source list",
     "help": "An explicit list of folders. Its presence turns discovery off entirely — "
             "somebody who wrote one meant it."},

    {"path": "bundles", "kind": "pathmap", "base": "project", "exists": "dir", "default": {},
     "label": "Bundles",
     "help": "id → path. Its presence turns discovery off. The id should be the folder "
             "name: two names for one bundle means the second one exists to be got wrong."},

    {"path": "read.web_ui.path", "kind": "path", "base": "project", "exists": "file",
     "soft": True, "default": "./okfm-web-ui.html", "label": "Web UI file",
     "help": "The single-file viewer. Opens from disk; there is no server."},
    {"path": "read.web_ui.index", "kind": "path", "base": "project", "soft": True,
     "default": None, "nullable": True, "label": "Index file",
     "help": "Where the generated index is written, if you want it as a separate file."},
    {"path": "read.web_ui.serve_port", "kind": "int", "min": 1, "max": 65535,
     "default": None, "nullable": True, "label": "Serve port",
     "help": "Port for the optional local preview. Not needed to open the file."},
    {"path": "read.index.max_concepts", "kind": "int", "min": 1, "max": 10000,
     "default": 60, "label": "Index budget",
     "help": "How many concepts an injected index may carry before it costs more than it "
             "buys."},
    {"path": "read.index.priority_types", "kind": "strings", "default": [],
     "label": "Priority types",
     "help": "Types that survive the budget first, most important first."},
    {"path": "read.exclude_scopes", "kind": "strings", "default": [],
     "label": "Excluded scopes",
     "help": "Scopes kept out of health statistics and out of any context assembled for an "
             "agent — the bundled guide is the usual entry."},

    {"path": "enrich.enabled", "kind": "bool", "default": False,
     "label": "Use a local model (Ollama)",
     "help": "Turn on Level 2+ — OKFM drafts descriptions itself, using a model on hardware "
             "you control. Off by default: nothing should start calling a model because a "
             "config file mentioned one."},
    {"path": "enrich.base_url", "kind": "string", "default": "http://localhost:11434",
     "label": "Ollama address",
     "help": "Where Ollama answers. http://localhost:11434 when it runs on this machine; "
             "http://<host>:11434 for a box on your network — that host needs "
             "OLLAMA_HOST=0.0.0.0 to accept anything but its own loopback."},
    {"path": "enrich.model", "kind": "string", "default": None, "nullable": True,
     "label": "Model",
     "help": "The model tag to draft with. It must ALREADY be pulled on that Ollama "
             "instance — nothing here downloads it. Avoid reasoning models: thinking is "
             "disabled, and one that ignores that spends minutes per concept."},
    {"path": "enrich.num_ctx", "kind": "int", "min": 512, "max": 1000000, "default": 8192,
     "label": "Context window",
     "help": "Tokens the model may hold. Ollama defaults to 2048, which silently truncates "
             "a long document and describes only the half it saw."},
    {"path": "enrich.timeout_s", "kind": "int", "min": 5, "max": 3600, "default": 120,
     "label": "Timeout (seconds)",
     "help": "How long to wait for one answer. A small model on a CPU is slow, not stuck."},

    {"path": "stores", "kind": "stores", "default": {}, "label": "Stores",
     "help": "External data stores. Credentials are named by handle and never written "
             "here: a config file is committed, a credential is not."},

    {"path": "federation.registry", "kind": "path", "base": "project", "exists": "dir",
     "soft": True, "default": None, "nullable": True, "label": "Registry",
     "help": "The bundle that registers the others. null is a valid mesh — a registry "
             "appears when a second owner does."},
]

BY_PATH = {f["path"]: f for f in FIELDS}
# Containers whose keys are the adopter's to choose. The unknown-key check stops here.
OPEN_KINDS = {"pathmap", "stores", "any"}
OPEN_PATHS = {f["path"] for f in FIELDS if f["kind"] in OPEN_KINDS}

# (prefix, title, blurb) — plus an optional fourth entry, a note the form renders as a
# callout above the fields. For the one group where getting it wrong costs a confusing
# runtime failure rather than a validation message.
GROUPS = [
    ("", "Profile", "What this file is."),
    ("build", "Build", "What gets read, and what gets written."),
    ("bundles", "Bundles", "Name them and discovery stops. Usually leave this empty."),
    ("read", "Read", "Consuming a mesh rather than producing one."),
    ("enrich", "Enrich — Level 2+",
     "A model on hardware you control drafts the descriptions extraction cannot write. "
     "No key, no account, no bill — the same terms as Level 2, plus a model you already have.",
     "The model must already be pulled on that Ollama instance: `ollama pull <model>`. "
     "Nothing here downloads it, and this page cannot check — a page opened from file:// "
     "cannot see your machine, let alone another one on your network. A name that is not "
     "there fails at run time with a 404 naming the model. Nothing in the build reads any of "
     "this; only `okfm.py enrich-local` does."),
    ("stores", "Stores", "External data. Handles only."),
    ("federation", "Federation", "Who registers whom."),
]


# ── walking a config ───────────────────────────────────────────────────────────

def dig(cfg: dict, path: str):
    """Value at a dotted path, and whether the key was present at all.

    Present-but-null and absent are different answers — `pack: null` is a decision and a
    missing `pack` is an omission — so this returns both rather than collapsing them.
    """
    node = cfg
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None, False
        node = node[part]
    return node, True


def _finding(level, path, msg, hint=None):
    return {"level": level, "path": path, "msg": msg, **({"hint": hint} if hint else {})}


def unknown_keys(cfg: dict) -> list[dict]:
    """Keys nobody reads. The whole reason this validator exists: a misspelled key is
    silently ignored by every consumer, so the symptom is a build that does the wrong thing
    quietly rather than one that complains.
    """
    out = []

    def walk(node, prefix):
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            if key.startswith("_"):
                continue                      # `_note`-style comments are the file's own
            path = f"{prefix}{key}"
            if path in OPEN_PATHS:
                continue                      # the adopter names these
            children = [p for p in BY_PATH if p.startswith(path + ".")]
            if path in BY_PATH:
                if children and isinstance(value, dict):
                    walk(value, path + ".")
                continue
            if children:
                walk(value, path + ".")
                continue
            siblings = [p.rsplit(".", 1)[-1] for p in BY_PATH
                        if p.rsplit(".", 1)[0] == prefix.rstrip(".") or "." not in p]
            near = difflib.get_close_matches(key, siblings, n=1, cutoff=0.7)
            out.append(_finding("error", path, "not a key anything reads",
                                f"did you mean `{near[0]}`?" if near else
                                "remove it, or prefix it with `_` to keep it as a note"))

    walk(cfg, "")
    return out


def _check_type(field, value) -> str | None:
    kind = field["kind"]
    if kind == "any":
        return None
    if kind in ("string", "path"):
        return None if isinstance(value, str) else "must be a string"
    if kind == "bool":
        return None if isinstance(value, bool) else "must be true or false"
    if kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            return "must be a whole number"
        lo, hi = field.get("min"), field.get("max")
        if lo is not None and value < lo or hi is not None and value > hi:
            return f"must be between {lo} and {hi}"
        return None
    if kind == "enum":
        return None if value in field["choices"] else \
            "must be one of " + ", ".join(f"`{c}`" for c in field["choices"])
    if kind in ("paths", "strings"):
        if not isinstance(value, list):
            return "must be a list"
        return None if all(isinstance(v, str) for v in value) else "every entry must be a string"
    if kind == "pathmap":
        if not isinstance(value, dict):
            return "must be a map of id to path"
        return None if all(isinstance(v, str) for v in value.values()) else \
            "every value must be a path"
    if kind == "stores":
        return None if isinstance(value, dict) else "must be a map of name to store"
    return None


def _rel(base: str, cfg: dict, project: Path) -> Path:
    if base == "root":
        root, _ = dig(cfg, "build.root")
        return (project / (root or "docs")).resolve()
    return project


def check_values(cfg: dict, project: Path | None = None) -> list[dict]:
    """Every rule that applies to one field. `project` unset means skip the disk."""
    out = []
    for field in FIELDS:
        path = field["path"]
        value, present = dig(cfg, path)
        if not present:
            if field.get("required"):
                out.append(_finding("error", path, "required, and missing",
                                    field["help"]))
            continue
        if value is None:
            if not field.get("nullable"):
                out.append(_finding("error", path, "cannot be null"))
            continue

        problem = _check_type(field, value)
        if problem:
            out.append(_finding("error", path, problem, field["help"]))
            continue

        if path == "okfm" and value != SPEC_VERSION:
            out.append(_finding("warn", path,
                                f"this tooling implements {SPEC_VERSION}, the config says {value}"))

        if field["kind"] == "stores":
            out += _check_stores(value)

        malformed = _check_shape(field, value)
        out += malformed
        if project is not None:
            out += _check_paths(field, value, cfg, project,
                                {f["path"] for f in malformed})

    out += _cross_checks(cfg)
    return out


def _check_stores(stores: dict) -> list[dict]:
    out = []
    for name, store in stores.items():
        if not isinstance(store, dict):
            out.append(_finding("error", f"stores.{name}", "must be an object"))
            continue
        profile = store.get("profile")
        if profile is None:
            out.append(_finding("warn", f"stores.{name}.profile",
                                "no credential handle — this store will not resolve"))
        elif not isinstance(profile, str) or not _HANDLE.match(profile):
            looks_like_secret = isinstance(profile, str) and "://" in profile
            out.append(_finding(
                "error", f"stores.{name}.profile",
                "must be a handle, not a credential"
                + (" — this looks like a live connection string" if looks_like_secret else ""),
                "one of " + ", ".join(f"`{p}:`" for p in HANDLE_PREFIXES)
                + ". A config file is committed; a credential is not."))
    return out


def _entries(field, value) -> dict[str, str]:
    """Every individual path a field holds, keyed by where it sits."""
    kind, path = field["kind"], field["path"]
    if kind == "path":
        return {path: value}
    if kind == "paths":
        return {f"{path}[{i}]": v for i, v in enumerate(value)}
    if kind == "pathmap":
        return {f"{path}.{k}": v for k, v in value.items()}
    return {}


def _check_shape(field, value) -> list[dict]:
    """Is the path written the way this field requires? No filesystem needed, so the web UI
    makes this call too — and it is what keeps an absolute path from reaching the disk check
    and getting a second, less useful message about not existing.
    """
    if "base" not in field:
        return []
    where_from = ("the documents root" if field["base"] == "root" else "the project")
    out = []
    for where, rel in _entries(field, value).items():
        if not isinstance(rel, str):
            continue
        if rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel) or \
                ".." in Path(rel).parts:
            out.append(_finding("error", where,
                                f"must sit inside {where_from}, written relative to it"))
    return out


def _check_paths(field, value, cfg, project: Path, skip: set[str]) -> list[dict]:
    """Does what it points at exist? The one class of check a browser cannot make."""
    want = field.get("exists")
    if not want:
        return []
    base = _rel(field.get("base", "project"), cfg, project)
    level = "warn" if field.get("soft") else "error"

    out = []
    for where, rel in _entries(field, value).items():
        if where in skip or not isinstance(rel, str):
            continue                        # already rejected — one problem, one message
        target = (base / rel.removeprefix("./")).resolve()
        ok = target.is_dir() if want == "dir" else target.is_file()
        if not ok:
            shown = target.relative_to(project) if target.is_relative_to(project) else target
            out.append(_finding(level, where, f"no such {want}: {shown}"))
    return out


def _cross_checks(cfg: dict) -> list[dict]:
    """Rules about how two fields sit together — where the real mistakes live."""
    out = []
    root, _ = dig(cfg, "build.root")
    out_dir, _ = dig(cfg, "build.out")
    include, _ = dig(cfg, "build.include")
    exclude, _ = dig(cfg, "build.exclude")
    bundles, has_bundles = dig(cfg, "bundles")

    def norm(p):
        return str(p).replace("\\", "/").strip("/").removeprefix("./")

    if isinstance(root, str) and isinstance(out_dir, str):
        r, o = norm(root), norm(out_dir)
        if o == r or o.startswith(r + "/"):
            out.append(_finding("error", "build.out",
                                f"writes inside `{root}`, the folder it reads",
                                "the build would read its own output on the next run, and "
                                "your documents would stop being only yours"))

    for i, entry in enumerate(include or []):
        if isinstance(entry, str) and isinstance(root, str):
            e, r = norm(entry), norm(root)
            if e == r or e.startswith(r + "/"):
                out.append(_finding("warn", f"build.include[{i}]",
                                    f"inside `{root}`, so it is dropped",
                                    "include reaches outside the root; use exclude to "
                                    "control what is inside it"))

    # `exclude` says what gets READ. `bundles` says what the mesh IS. Excluding a folder
    # that `bundles` still names changes nothing an adopter can see, which is the most
    # confusing possible outcome: the config now disagrees with itself and the mesh looks
    # broken rather than misconfigured.
    if has_bundles and isinstance(bundles, dict) and isinstance(root, str):
        for i, entry in enumerate(exclude or []):
            if not isinstance(entry, str):
                continue
            excluded_path = f"{norm(root)}/{norm(entry)}".strip("/")
            for bid, rel in bundles.items():
                if isinstance(rel, str) and norm(rel) == excluded_path:
                    out.append(_finding(
                        "warn", f"build.exclude[{i}]",
                        f"excluded from the build, but `bundles.{bid}` still names it — "
                        f"every reader still shows it",
                        f"`exclude` controls what is READ; `bundles` is what the mesh IS. "
                        f"To drop it from the mesh, remove the `bundles.{bid}` line. To keep "
                        f"it as an in-place bundle that the build must not mirror, this is "
                        f"already correct."))

    # What separates level 3's local variant from its credentialed one is not the model, it
    # is where the model runs and whether reaching it costs a secret. The config is the only
    # place that fact is written down, so this is the only place it can be checked.
    enabled, _ = dig(cfg, "enrich.enabled")
    model, _ = dig(cfg, "enrich.model")
    # The switch says intent, the model says which — so the two are not redundant, and this
    # is the only combination that means nothing. The reverse, a model named while switched
    # off, is deliberately silent: that is the normal state of every config nobody has turned
    # this on in yet, and a check that fires on the common case is one people learn to ignore.
    if enabled is True and not (isinstance(model, str) and model.strip()):
        out.append(_finding("error", "enrich.model",
                            "the local model is switched on and no model is named",
                            "name one you have already pulled — `ollama list` on that host "
                            "says which — or set `enrich.enabled` to false"))

    base_url, _ = dig(cfg, "enrich.base_url")
    if isinstance(base_url, str) and base_url.strip():
        host = urlsplit(base_url).hostname
        if not host:
            out.append(_finding("error", "enrich.base_url", "not a URL",
                                "a scheme and a host, like `http://localhost:11434`"))
        elif host not in LOOPBACK:
            out.append(_finding(
                "warn", "enrich.base_url",
                f"`{host}` is not this machine, so this is no longer the local variant",
                "fine if it is your own hardware — nothing here holds a key either way. But "
                "if reaching it needs one, that credential belongs in `stores` as a handle, "
                "and the component becomes `needs-secrets` rather than `needs-model`."))

    if has_bundles and isinstance(bundles, dict) and bundles:
        for bid, rel in bundles.items():
            if isinstance(rel, str) and norm(rel).rsplit("/", 1)[-1] != bid:
                out.append(_finding("warn", f"bundles.{bid}",
                                    f"id does not match the folder name "
                                    f"`{norm(rel).rsplit('/', 1)[-1]}`",
                                    "two names for one bundle, and the second exists only "
                                    "to be got wrong"))
    return out


def validate(cfg: dict, project: Path | None = None) -> list[dict]:
    """Every finding, errors first. `project` unset skips the checks that need a disk."""
    findings = unknown_keys(cfg) + check_values(cfg, project)
    order = {"error": 0, "warn": 1}
    return sorted(findings, key=lambda f: (order[f["level"]], f["path"]))


def as_json() -> str:
    """The table, for the web UI. One source, two consumers."""
    return json.dumps({"version": SPEC_VERSION, "handles": list(HANDLE_PREFIXES),
                       "loopback": list(LOOPBACK), "groups": GROUPS, "fields": FIELDS},
                      indent=1, ensure_ascii=False)


if __name__ == "__main__":
    print(as_json())
