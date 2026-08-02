#!/usr/bin/env python3
"""The benchmark harness — spec §18, deterministic half.

    python benchmark/run.py            # materialise both arms, emit prompts and the key
    python benchmark/run.py --check    # validate the question set and the arms, write nothing
    python benchmark/run.py --seed 7   # a different blinding, same corpus

## What this is, and what it is not

§18 measures the premise the whole project rests on: that a curated bundle makes answers
better. Two arms over one corpus — the project with its bundle, and the same project without
it — a fresh agent per question per arm, and blind grading against a claim list.

Everything up to "ask the model" is arithmetic, and that is what this builds: the two arms,
the blinding, the contamination checks, and the grading sheet. Running the questions needs a
model, which puts that half at level 3 or 4 depending on who holds the key. Grading is a
person's or a model's job and reads the same sheet either way.

So this is a **prototype of the shape**, runnable today with `needs: []`, shipping with a
placeholder question set. Real questions get backfilled — and per §18.3 they must be drawn
from real behaviour and real past confusion, never from a bundle's own table of contents,
which is the surest way to flatter it.

## The trap this is built around

A rendered copy is a copy. Any export of a bundle — a static site, a cached context package,
a visualization carrying prose — contaminates the control arm as thoroughly as the bundle
itself. That mistake is borrowed from a published benchmark rather than learned here, and it
is why the control arm is **materialised** into a real directory and then checked, rather
than described in a manifest and trusted.
"""
import argparse
import hashlib
import json
import random
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
RUNS = HERE / "runs"

_FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
_DESC = re.compile(r"^description:[ \t]*(.+)$", re.M)

# Anything that is a derivation of a bundle rather than a source. Removing the bundle and
# leaving one of these behind is the contamination trap in §18.3.
DERIVATIONS = ["okfm-web-ui.html", "okfm-index.json"]

SKIP_DIRS = {".git", ".github", "node_modules", "__pycache__", ".okfm-cache", "runs"}

# The control arm has to be a project someone could actually work in, not a documentation
# folder. Code and config carry facts the questions may legitimately depend on.
CORPUS_GLOBS = ("*.md", "*.py", "*.yaml", "*.json")


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def corpus() -> list[Path]:
    """Every file a reader could reach, relative to the project root."""
    out = set()
    for glob in CORPUS_GLOBS:
        for f in PROJECT.rglob(glob):
            rel = f.relative_to(PROJECT)
            if SKIP_DIRS & set(rel.parts) or rel.parts[0] == "benchmark":
                continue
            out.add(rel)
    return sorted(out)


def bundle_dirs() -> dict[str, Path]:
    """Bundle roots, project-relative.

    `removeprefix`, not `lstrip`. `lstrip` takes a character SET, so `"./.okfm/mesh"` loses
    its dot-folder as well as its prefix and comes back as `"okfm/mesh"` — a directory that
    does not exist. Every `is_relative_to` against it then answered False, no concept was
    ever dropped, and the control arm was byte-identical to the treatment arm while the run
    printed `0 concepts removed` and exited 0.

    This is the second time this exact mistake has been made in this repository;
    `dev/check_levels.py` carries the same comment. Fixing it twice is not the fix — the
    fix is `arms_differ()` below, which fails whatever the cause.
    """
    cfg = json.loads((PROJECT / "okfm.json").read_text(encoding="utf-8"))
    return {bid: Path(p.removeprefix("./")) for bid, p in cfg.get("bundles", {}).items()}


def is_concept(path: Path) -> bool:
    try:
        return bool(_FM.match(path.read_text(encoding="utf-8")))
    except OSError:
        return False


def split_arms(files: list[Path], bundles: dict[str, Path]) -> tuple[list[Path], list[Path]]:
    """(treatment, control).

    Control is the corpus with every concept **and every derivation** gone. Dropping only
    the concepts is the mistake §18.3 warns about: a rendered view left behind carries the
    same prose and quietly turns the control arm into a second treatment arm.
    """
    roots = list(bundles.values())
    drop = {Path(d) for d in DERIVATIONS}
    control = [rel for rel in files
               if rel not in drop
               and not (any(rel.is_relative_to(r) for r in roots) and is_concept(PROJECT / rel))]
    return files, control


def descriptions(files: list[Path], bundles: dict[str, Path]) -> list[tuple[Path, str]]:
    out = []
    roots = list(bundles.values())
    for rel in files:
        if not any(rel.is_relative_to(r) for r in roots):
            continue
        m = _FM.match((PROJECT / rel).read_text(encoding="utf-8"))
        if not m:
            continue
        d = _DESC.search(m.group(1))
        if d:
            out.append((rel, d.group(1).strip().strip('"\'')))
    return out


def opaque(seed: int, qid: str, arm: str) -> str:
    return hashlib.sha256(f"{seed}:{qid}:{arm}".encode()).hexdigest()[:12]


def arm_id(seed: int, arm: str) -> str:
    """The directory name an answering agent actually sees.

    Blinding the grader is not enough. An agent told it is working in `arms/control/` has
    been handed the experiment's independent variable in a path, and it can act on it —
    hedging, noting that documentation seems to be missing, or going looking for what it was
    told it does not have. The arm has to be opaque at answering time too, not just at
    grading time.
    """
    return hashlib.sha256(f"{seed}:arm:{arm}".encode()).hexdigest()[:12]


def main() -> int:
    utf8_stdout()
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    # Materialise outside the repository when the answering agent has a real filesystem.
    # An arm sitting inside the project it was cut from is one `../../..` away from the
    # treatment corpus, and an agent that wanders up finds everything the control arm was
    # built to withhold. Isolation belongs in the path, not in the instructions.
    ap.add_argument("--out", default=None,
                    help="write the run here instead of benchmark/runs/")
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help:
        print(__doc__)
        return 0

    qfile = HERE / "questions.json"
    if not qfile.exists():
        print(f"no question set at {qfile}", file=sys.stderr)
        return 2
    questions = json.loads(qfile.read_text(encoding="utf-8"))["questions"]

    bundles = bundle_dirs()
    files = corpus()
    treatment, control = split_arms(files, bundles)
    control_set = {p.as_posix() for p in control}

    print(f"corpus      {len(files)} files")
    print(f"treatment   {len(treatment)}")
    print(f"control     {len(control)}  ({len(treatment) - len(control)} concepts removed)")

    errors, notes = [], []

    # --- the arms must actually differ ---------------------------------------
    # Everything else here checks whether the comparison is *fair*. This checks whether there
    # is a comparison at all, and it is first because nothing below it means anything if the
    # two directories hold the same files. A benchmark that silently measures a corpus against
    # itself reports a clean run forever and a difference of zero, which reads as "the bundle
    # does not help" rather than "the harness is broken" — the most expensive way to be wrong.
    removed = len(treatment) - len(control)
    if removed == 0:
        errors.append("control arm is identical to the treatment arm — no concept was "
                      "removed, so the two arms measure the same corpus. Check that "
                      "`bundles` in okfm.json names directories that exist.")
    elif removed < len([b for b in bundles]):
        # Fewer concepts dropped than there are bundles means at least one root matched
        # nothing. Not fatal — a bundle can legitimately be empty — but it is the shape the
        # path bug took, so it is said out loud.
        notes.append(f"only {removed} concept(s) removed across {len(bundles)} bundles — "
                     f"verify every `bundles` path resolves")

    # --- §18.1 rule 1: every fact must be present in BOTH arms ---------------
    # The bundle is a shortcut, never the only source. A question whose evidence lives only
    # inside the bundle measures nothing except whether the file was deleted.
    for q in questions:
        src = q.get("answerable_from") or []
        if not src:
            errors.append(f"{q['id']}: no `answerable_from` — cannot be answered in the control arm")
        for s in src:
            if s not in control_set:
                errors.append(f"{q['id']}: `{s}` is not in the control arm — "
                              f"either it is a concept, or it does not exist")

    # --- §18.3 trap 1: derivations are copies --------------------------------
    for d in DERIVATIONS:
        if (PROJECT / d).exists():
            notes.append(f"derivation excluded from the control arm: {d}")

    # --- §18.3, the harder half: does any control file still carry the prose? -
    # A description that survives into the control arm means the concept and its source are
    # the same file, and removing the bundle did not remove the knowledge.
    leaked = []
    for rel, desc in descriptions(files, bundles):
        if len(desc) < 40:
            continue
        for c in control:
            if desc[:60] in (PROJECT / c).read_text(encoding="utf-8"):
                leaked.append((rel.as_posix(), c.as_posix()))
                break

    # --- in-place bundles cannot be benchmarked against themselves ------------
    inplace = sorted(b for b, root in bundles.items()
                     if any(p.is_relative_to(root) and _is_inplace(p) for p in files))
    for b in inplace:
        notes.append(f"bundle `{b}` is in-place: its concepts ARE its sources, so removing "
                     f"them removes the facts. Questions must not draw on it.")

    for n in notes:
        print(f"  note  {n}")
    for a, b in leaked[:10]:
        print(f"  note  prose from {a} still present in {b}")
    for e in errors:
        print(f"  FAIL  {e}")

    if errors:
        print(f"\n{len(errors)} problem(s)")
        return 1

    if args.check:
        print("\nOK — question set and arms are consistent (nothing written)")
        return 0

    # --- materialise ---------------------------------------------------------
    run_id = f"run_seed{args.seed}"
    out = Path(args.out).resolve() / run_id if args.out else RUNS / run_id
    if out.exists():
        shutil.rmtree(out)

    arms = {arm: arm_id(args.seed, arm) for arm in ("treatment", "control")}
    for arm, paths in (("treatment", treatment), ("control", control)):
        for rel in paths:
            dst = out / "arms" / arms[arm] / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(PROJECT / rel, dst)

    key, sheet = {"_arms": arms}, []
    prompts = out / "prompts"
    prompts.mkdir(parents=True, exist_ok=True)
    for q in questions:
        for arm in ("treatment", "control"):
            oid = opaque(args.seed, q["id"], arm)
            key[oid] = {"question": q["id"], "arm": arm, "dir": arms[arm]}
            (prompts / f"{oid}.md").write_text(
                f"# {oid}\n\n"
                f"You have read-only access to a repository at `arms/{arms[arm]}/`.\n"
                f"Answer from those files only. Cite the files you used.\n\n"
                f"## Question\n\n{q['text']}\n",
                encoding="utf-8", newline="\n")
            sheet.append((oid, q))

    random.Random(args.seed).shuffle(sheet)
    lines = ["# Grading sheet", "",
             "Arm labels are deliberately absent. Mark each claim hit or missed, then note any",
             "statement that is false — an omission is a gap, a false statement is a defect and",
             "should be traced to the concept that caused it.", ""]
    for oid, q in sheet:
        lines += [f"## {oid}", "", f"*Shape:* {q.get('shape', 'unspecified')}", "", "Claims:"]
        lines += [f"- [ ] {c}" for c in q["claims"]]
        lines += ["", "False statements:", "", "- ", ""]
    (out / "grading-sheet.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    (out / "key.json").write_text(json.dumps(key, indent=2) + "\n",
                                  encoding="utf-8", newline="\n")

    shown = (out.relative_to(PROJECT).as_posix()
             if out.is_relative_to(PROJECT) else out.as_posix())
    print(f"\nwrote {shown}")
    # Arm directories are named by hash, and so is this line: printing which opaque id is
    # which would put the answer in the same terminal the operator pastes prompts from.
    # `key.json` holds the mapping, and grading reads it after the answers are in.
    print(f"  arms/           2 opaque ids, {len(treatment)} and {len(control)} files")
    print(f"  prompts/        {len(key) - 1} ({len(questions)} questions x 2 arms)")
    print("  grading-sheet.md, key.json")
    print("\nNext: answer each prompt with a fresh agent that can read only its own arm,")
    print("save the answer beside it, then grade blind against the sheet.")
    return 0


def _is_inplace(rel: Path) -> bool:
    """A concept whose body is also the document — frontmatter bolted onto real prose.

    Detected structurally: a `sources` entry pointing at the file's own name. Those bundles
    cannot serve as a benchmark treatment, because there is no version of the corpus that
    keeps the facts and drops the concept.
    """
    try:
        m = _FM.match((PROJECT / rel).read_text(encoding="utf-8"))
    except OSError:
        return False
    return bool(m and re.search(rf"resource:\s*/?{re.escape(rel.name)}\s*$", m.group(1), re.M))


if __name__ == "__main__":
    raise SystemExit(main())
