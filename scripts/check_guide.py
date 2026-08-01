"""Phase 0 consistency check: does okfm-guide/ match the viewer's baked BOOTSTRAP?

A dry run of what `okfm validate` will eventually do. Deliberately stdlib-only and
regex-based -- no PyYAML -- to prove the zero-dependency core is viable.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / "okfm-guide"
VIEWER = ROOT / "okfm-viewer.html"

# ---- pull BOOTSTRAP out of the viewer -------------------------------------
html = VIEWER.read_text(encoding="utf-8")
m = re.search(r"const BOOTSTRAP = (\{.*?\n\});", html, re.S)
if not m:
    sys.exit("FATAL: could not find BOOTSTRAP in viewer")
boot = json.loads(m.group(1))
baked = {c["p"]: c for c in boot["concepts"]}

# ---- minimal frontmatter reader -------------------------------------------
FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def scalar(block: str, key: str):
    """Top-level `key: value` -- handles quotes and folded continuation lines."""
    m = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    v = " ".join(p.strip() for p in m.group(1).splitlines()).strip()
    if v.startswith(('"', "'")) and v.endswith(('"', "'")):
        v = v[1:-1]
    return v or None


def relations(block: str):
    m = re.search(r"^okfm_relations:\s*\n((?:[ \t]*-.*\n?)+)", block, re.M)
    if not m:
        return []
    return sorted(
        (p, t) for p, t in re.findall(
            r"predicate:\s*([\w_]+),\s*target:\s*([^\s}]+)", m.group(1)
        )
    )


errors, warnings = [], []
seen = set()

for f in sorted(GUIDE.glob("*.md")):
    mesh_path = f"/okfm-guide/{f.name}"
    seen.add(mesh_path)
    text = f.read_text(encoding="utf-8")

    fm = FM.match(text)
    if not fm:
        errors.append(f"{f.name}: no parseable frontmatter")
        continue
    block = fm.group(1)

    # --- OKF v0.2 conformance: non-empty `type` is the only hard requirement
    ctype = scalar(block, "type")
    if not ctype:
        errors.append(f"{f.name}: missing or empty `type` (conformance failure)")

    b = baked.get(mesh_path)
    if b is None:
        errors.append(f"{f.name}: file exists but is absent from viewer BOOTSTRAP")
        continue

    for key, got, want in (
        ("type", ctype, b["t"]),
        ("title", scalar(block, "title"), b["title"]),
        ("description", scalar(block, "description"), b["d"]),
    ):
        if got != want:
            errors.append(f"{f.name}: {key}\n      file:   {got!r}\n      viewer: {want!r}")

    # --- trust tier is DERIVED, never stored (spec 3.4)
    derived = "human" if re.search(r'^verified:.*human:', block, re.M) else (
        "machine" if re.search(r"^verified:", block, re.M) else None
    )
    if derived != b["v"]:
        errors.append(f"{f.name}: derived trust {derived!r} but viewer baked {b['v']!r}")

    if re.search(r"^okfm_stale:|^okfm_drift(ed)?:|^okfm_trust:", block, re.M):
        errors.append(f"{f.name}: stores a derived verdict (spec 3.4 forbids)")

    n_src = len(re.findall(r"^\s+- id:", block, re.M))
    if n_src != b["src"]:
        errors.append(f"{f.name}: {n_src} sources but viewer baked src={b['src']}")

    # --- relations: files are bundle-relative, viewer is mesh-relative
    got_rel = relations(block)
    want_rel = sorted((p, t.replace("/okfm-guide/", "/")) for p, t in map(tuple, b["r"]))
    if got_rel != want_rel:
        errors.append(f"{f.name}: relations\n      file:   {got_rel}\n      viewer: {want_rel}")

    if scalar(block, "okfm_scope") != "guide":
        errors.append(f"{f.name}: missing `okfm_scope: guide` -- would pollute an adopter's mesh")

    # --- every body link must resolve
    body = text[fm.end():]
    for label, target in re.findall(r"\[([^\]]+)\]\(([^)#]+?)(?:#[^)]*)?\)", body):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (GUIDE / target).resolve().exists():
            errors.append(f"{f.name}: broken link [{label}]({target})")

    # --- footnote refs must have definitions
    for ref in set(re.findall(r"\[\^([\w-]+)\](?!:)", body)):
        if not re.search(rf"^\[\^{re.escape(ref)}\]:", body, re.M):
            errors.append(f"{f.name}: footnote [^{ref}] referenced but never defined")

for missing in sorted(set(baked) - seen):
    errors.append(f"{missing}: viewer BOOTSTRAP expects it but no file exists")

print(f"guide files : {len(list(GUIDE.glob('*.md')))}")
print(f"baked in viewer : {len(baked)}")
print()
for w in warnings:
    print(f"  WARN  {w}")
for e in errors:
    print(f"  FAIL  {e}")
print()
print("OK -- guide bundle and viewer agree" if not errors else f"{len(errors)} problem(s)")
sys.exit(1 if errors else 0)
