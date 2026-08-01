"""Corpus-wide check across the split OKFM document set.

Verifies: every section has exactly one real home; every cross-reference resolves
somewhere in the corpus; every relative markdown link points at a file that exists.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [
    ROOT / "spec/okfm-v0.2.1.md",
    ROOT / "docs/rationale.md",
    ROOT / "docs/roadmap.md",
    ROOT / "docs/prior-art.md",
]

H2 = re.compile(r"^##\s+(Appendix [A-Z]|\d+)[.\s]")
H3 = re.compile(r"^###\s+(\d+\.\d+)[.\s]")
STUB = re.compile(r"^>\s+Moved to ")

real_homes = defaultdict(list)   # section -> files where it has actual content
subsections = {}                 # "7.3" -> file
refs = defaultdict(list)
errors = []

for f in FILES:
    lines = f.read_text(encoding="utf-8").splitlines()
    rel = f.relative_to(ROOT).as_posix()

    in_fence = False
    for i, line in enumerate(lines):
        # Fenced blocks are EXAMPLES. Linting their links and refs flags illustrative
        # content as broken -- the linter must read them as data, not as document.
        if re.match(r"^\s{0,3}(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        m = H2.match(line)
        if m:
            # a stub is a heading whose next non-blank line is "> Moved to"
            nxt = next((l for l in lines[i + 1:i + 4] if l.strip()), "")
            if not STUB.match(nxt):
                real_homes[m.group(1)].append(rel)
        m3 = H3.match(line)
        if m3:
            subsections[m3.group(1)] = rel

        # "official OKF §5.1" points at the BASELINE spec, not this corpus.
        for r in re.findall(r"(?<!official OKF )§(\d+(?:\.\d+)?)", line):
            refs[r].append((rel, i + 1))

        # relative markdown links
        for label, target in re.findall(r"\[([^\]]+)\]\(([^)#]+?)(?:#[^)]*)?\)", line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (f.parent / target).resolve().exists():
                errors.append(f"{rel}:{i+1} broken link [{label}]({target})")

# ---- one home per section -------------------------------------------------
expected = {str(n) for n in range(0, 23)} | {"Appendix A"}
for s in sorted(expected, key=lambda x: (1, 0) if x[0] == "A" else (0, int(x))):
    homes = real_homes.get(s, [])
    if len(homes) != 1:
        errors.append(f"section {s}: {len(homes)} real homes {homes} (expected exactly 1)")

# ---- list-item refs (§3.4 = design principle 4) ---------------------------
list_counts = {}
for f in FILES:
    lines = f.read_text(encoding="utf-8").splitlines()
    cur, cnt = None, 0
    for line in lines:
        m = H2.match(line)
        if m:
            if cur and cnt:
                list_counts[cur] = max(list_counts.get(cur, 0), cnt)
            cur, cnt = m.group(1), 0
            continue
        if cur and re.match(r"^\d+\.\s+\S", line):
            cnt += 1
    if cur and cnt:
        list_counts[cur] = max(list_counts.get(cur, 0), cnt)

tops = set(real_homes)
dangling = 0
for ref in sorted(refs, key=lambda s: [int(p) for p in s.split(".")]):
    if ref in subsections or ref in tops:
        continue
    if "." in ref:
        top, item = ref.split(".")
        if item.isdigit() and int(item) <= list_counts.get(top, 0):
            continue
    dangling += 1
    where = ", ".join(f"{r}:{n}" for r, n in refs[ref][:4])
    errors.append(f"dangling §{ref} referenced at {where}")

print(f"files          : {len(FILES)}")
print(f"sections       : {len(real_homes)} with content, {len(subsections)} subsections")
print(f"references     : {sum(len(v) for v in refs.values())} to {len(refs)} targets")
print(f"total lines    : {sum(len(f.read_text(encoding='utf-8').splitlines()) for f in FILES)}")
print()
for e in errors:
    print(f"  FAIL  {e}")
print()
print("OK -- corpus is internally consistent" if not errors else f"{len(errors)} problem(s)")
sys.exit(1 if errors else 0)
