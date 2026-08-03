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

# ---- named ordinal series (Phase 3, Level 2) ------------------------------
# `### Phase 3 — The credentialed half` vanished from the roadmap in a rewrite whose
# replacement block ended one line short: the last line of the text being replaced was the
# NEXT section's heading. Nothing noticed for two commits. Phase 3 is referenced twelve
# times across the corpus, §15's own map says the roadmap is where phases live, and a reader
# falling out of Phase 2's exit criteria straight into `Scope: sys:// resolvers` reads Phase
# 3's requirements as Phase 2's -- which makes Phase 2 permanently unfinishable.
#
# The numbered spine above (`## 15.`, `### 7.3`) has been guarded since the split. The
# corpus's OTHER heading system, a name plus an ordinal, was guarded by nothing.
#
# **The rule is scoped to the document that DEFINES a series, and that scoping is the whole
# design.** `Level 4` is referenced twenty-two times and has no heading in the README or the
# roadmap, because DR-0009 defined it and then folded it into Level 3 as the credentialed
# variant. A history of superseded ordinals is precisely what a decision record is for. A
# corpus-wide "every ordinal mentioned must have a heading" rule would report those
# twenty-two, be correct about none of them, and be switched off within a week. Contiguity
# inside the defining document reports one failure, and it is the real one.
#
# Series names are discovered from the headings rather than listed here, for the reason
# `dev/check_commands.py` gives: a list here would be a second place to keep the same set in
# sync, which is the failure this file exists to catch.
GENERATED = {".okfm", "packs", "examples", "benchmark", ".git"}
# `\d{1,2}` on purpose -- `## Amendment 2026-08-01` is a date, not an ordinal.
SERIES_H = re.compile(r"^#{1,6}\s+([A-Z][a-z]+)\s+(\d{1,2})\b")

corpus = {}
for p in sorted(ROOT.rglob("*.md")):
    if GENERATED & set(p.relative_to(ROOT).parts):
        continue
    corpus[p.relative_to(ROOT).as_posix()] = p.read_text(encoding="utf-8").splitlines()

series = 0
for rel, lines in corpus.items():
    defined = defaultdict(set)
    for line in lines:
        m = SERIES_H.match(line)
        if m:
            defined[m.group(1)].add(int(m.group(2)))

    for name, nums in sorted(defined.items()):
        if len(nums) < 2:
            continue                      # one heading is a mention, not a series
        series += 1
        missing = sorted(set(range(min(nums), max(nums) + 1)) - nums)
        if missing:
            errors.append(f"{rel} defines {name} {sorted(nums)} and has no heading for "
                          + ", ".join(f"{name} {n}" for n in missing))

        # ...and a mention inside the defining document must land on one of its headings.
        ref = re.compile(rf"\b{name}\s+(\d{{1,2}})\b")
        in_fence = False
        for i, line in enumerate(lines, 1):
            if re.match(r"^\s{0,3}(```|~~~)", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for n in {int(x) for x in ref.findall(line)} - nums:
                errors.append(f"{rel}:{i} refers to {name} {n}, which it gives no heading")

print(f"files          : {len(FILES)}")
print(f"sections       : {len(real_homes)} with content, {len(subsections)} subsections")
print(f"references     : {sum(len(v) for v in refs.values())} to {len(refs)} targets")
print(f"ordinal series : {series} across {len(corpus)} corpus files")
print(f"total lines    : {sum(len(f.read_text(encoding='utf-8').splitlines()) for f in FILES)}")
print()
for e in errors:
    print(f"  FAIL  {e}")
print()
print("OK -- corpus is internally consistent" if not errors else f"{len(errors)} problem(s)")
sys.exit(1 if errors else 0)
