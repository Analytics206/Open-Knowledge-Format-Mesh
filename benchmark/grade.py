#!/usr/bin/env python3
"""Score a benchmark run — the arithmetic half of grading.

    python benchmark/grade.py --run <dir> --packets   # blind packets for a grader
    python benchmark/grade.py --run <dir>             # score the verdicts, write the report

## The split, and why it is here

Deciding whether an answer contains a claim is judgement, and this file does none of it. It
prepares **packets** — one answer, one claim list, no arm label, no question id — and then,
once somebody has filled in verdicts, it does the counting. Counting is arithmetic and belongs
in code; judging is not and does not.

Keeping them apart is what makes the blinding real rather than declared. A grader who can see
which arm an answer came from will find the claim they expect to find, and no amount of good
faith fixes that — which is why the packet carries an opaque id and the key is not read until
after the verdicts are in.

`needs: []` — reads files, counts, prints.

## What gets counted, and why separately

**Claims hit** is the headline: did the answer contain the thing a correct answer contains.

**False statements** are counted apart from misses, because they are not the same failure. A
miss is a gap — the answer did not say something it could have. A false statement is a defect,
and a defect traceable to a concept is the most valuable output this whole apparatus produces:
it means curated knowledge actively misled somebody, which is worse than having none.

A run where the bundle arm hits more claims *and* states more falsehoods is not a win, and a
single score would hide that. So there is no single score.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def utf8_stdout() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


def load(run: Path):
    key = json.loads((run / "key.json").read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in
                 json.loads((HERE / "questions.json").read_text(encoding="utf-8"))["questions"]}
    answers = {f.stem: f.read_text(encoding="utf-8")
               for f in sorted((run / "answers").glob("*.md"))}
    return key, questions, answers


def packets(run: Path, key: dict, questions: dict, answers: dict) -> int:
    """One file per answer: the text, and the claims to mark. No arm, no question id.

    Deliberately not sorted by anything meaningful — `answers` comes back in hash order, so
    the two arms of one question do not sit next to each other. Adjacency is a tell.
    """
    out = run / "packets"
    out.mkdir(exist_ok=True)
    written = 0
    for oid, text in answers.items():
        meta = key.get(oid)
        if not meta:
            print(f"  skip  {oid} — not in key.json", file=sys.stderr)
            continue
        q = questions[meta["question"]]
        body = text.split("## Answer", 1)[-1].split("## Files used")[0].strip()
        cited = text.split("## Files used", 1)[1].strip() if "## Files used" in text else "(none)"
        (out / f"{oid}.md").write_text(
            f"# {oid}\n\n"
            f"## The answer to grade\n\n{body}\n\n"
            f"## Files it says it used\n\n{cited}\n\n"
            f"## Mark each claim present or absent\n\n"
            + "\n".join(f"{i}. {c}" for i, c in enumerate(q["claims"]))
            + "\n\nA claim counts as present when the answer states it in substance. Different\n"
              "wording is fine; a weaker or hedged version of the claim is not.\n\n"
            f"## Then list any statement in the answer that is FALSE\n\n"
            f"Not merely missing — actually wrong about how this system works.\n",
            encoding="utf-8", newline="\n")
        written += 1
    print(f"wrote {written} packet(s) to {out}")
    print("Grade each one WITHOUT looking at key.json, then write verdicts.json:")
    print('  { "<oid>": { "hit": [0, 2], "false": ["..."] }, ... }')
    return 0


def verdicts_of(run: Path) -> dict:
    """`verdicts.json`, or every `verdicts-N.json` merged.

    Grading gets split across several graders on purpose — no one of them may see both arms
    of the same question, because a matched pair is the one comparison that gives the arm
    away. So the normal case is several files, and merging them is this function's whole job.

    A duplicate id across two files is an error rather than a last-write-wins: it means the
    split was built wrong and somebody graded the same answer twice, which is exactly the
    situation the split exists to prevent.
    """
    single = run / "verdicts.json"
    files = [single] if single.is_file() else sorted(run.glob("verdicts-*.json"))
    merged, seen = {}, {}
    for f in files:
        for oid, v in json.loads(f.read_text(encoding="utf-8")).items():
            if oid in merged:
                raise SystemExit(f"{oid} graded twice: {seen[oid].name} and {f.name}")
            merged[oid], seen[oid] = v, f
    return merged


def score(run: Path, key: dict, questions: dict, answers: dict) -> int:
    verdicts = verdicts_of(run)
    if not verdicts:
        print(f"no verdicts in {run} — run with --packets first", file=sys.stderr)
        return 2

    # Scoring a partial set silently would report a gap computed from whichever answers
    # happened to be graded, and an arm short a few answers scores lower for a reason that
    # has nothing to do with the bundle.
    ungraded = sorted(set(answers) - set(verdicts))
    if ungraded:
        print(f"{len(ungraded)} answer(s) have no verdict: {', '.join(ungraded)}",
              file=sys.stderr)
        return 2

    rows, arms = [], {"treatment": [0, 0, 0], "control": [0, 0, 0]}  # hit, total, false
    for oid, v in sorted(verdicts.items()):
        meta = key[oid]
        q = questions[meta["question"]]
        hit, total = len(set(v.get("hit", []))), len(q["claims"])
        false_n = len(v.get("false", []))
        arms[meta["arm"]][0] += hit
        arms[meta["arm"]][1] += total
        arms[meta["arm"]][2] += false_n
        rows.append((meta["question"], meta["arm"], hit, total, false_n, v.get("false", [])))

    width = max(len(r[0]) for r in rows)
    print(f"{'question':<{width}}  {'arm':<9}  claims  false")
    for qid, arm, hit, total, fn, _ in sorted(rows):
        print(f"{qid:<{width}}  {arm:<9}  {hit}/{total:<4}  {fn}")

    print()
    for arm in ("treatment", "control"):
        hit, total, fn = arms[arm]
        pct = 100 * hit / total if total else 0
        print(f"{arm:<10} {hit}/{total} claims ({pct:.0f}%), {fn} false statement(s)")

    t, c = arms["treatment"], arms["control"]
    gap = (100 * t[0] / t[1] if t[1] else 0) - (100 * c[0] / c[1] if c[1] else 0)
    print(f"\ngap        {gap:+.0f} percentage points, "
          f"{t[2] - c[2]:+d} false statement(s), bundle minus no-bundle")

    # Said plainly rather than left to the reader: a gap this small on this few questions is
    # a direction, not a measurement. Overclaiming here would be the same failure the harness
    # exists to catch, committed by the person reading it.
    if abs(gap) < 10:
        print("\nToo small to call on 8 questions. A direction, not a result.")

    falses = [(qid, arm, f) for qid, arm, _, _, _, fs in rows for f in fs]
    if falses:
        print(f"\n{len(falses)} false statement(s) — each one traces to a source that misled:")
        for qid, arm, f in falses:
            print(f"  [{arm}] {qid}: {f}")

    report = {"arms": {a: {"claims_hit": v[0], "claims_total": v[1], "false": v[2]}
                       for a, v in arms.items()},
              "questions": [{"question": r[0], "arm": r[1], "hit": r[2], "total": r[3],
                             "false": r[5]} for r in rows]}
    (run / "report.json").write_text(json.dumps(report, indent=2) + "\n",
                                     encoding="utf-8", newline="\n")
    print(f"\nwrote {(run / 'report.json').name}")
    return 0


def main() -> int:
    utf8_stdout()
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--run", required=True)
    ap.add_argument("--packets", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    args = ap.parse_args()
    if args.help:
        print(__doc__)
        return 0

    run = Path(args.run).resolve()
    if not (run / "key.json").is_file():
        print(f"not a benchmark run: {run}", file=sys.stderr)
        return 2
    key, questions, answers = load(run)
    if not answers:
        print(f"no answers in {run / 'answers'}", file=sys.stderr)
        return 2
    return packets(run, key, questions, answers) if args.packets \
        else score(run, key, questions, answers)


if __name__ == "__main__":
    raise SystemExit(main())
