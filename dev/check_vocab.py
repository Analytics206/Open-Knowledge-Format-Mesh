#!/usr/bin/env python3
"""A pack may add domain terms. It may not widen a family it did not name.

    python dev/check_vocab.py

## Why this exists

The overlay mechanism is how a domain pack contributes vocabulary without forking core
(§10.2, §13.3). For most of this project's life it took a flat list of **file paths** and
appended every one of them to every family's read. So a pack file declaring a single
reason code registered that term as a valid reason code, a valid type, a valid role — and
a valid **predicate**.

The predicate is the damage. `check_bundles` warns on an unknown type and warns on an
unknown reason code, because official OKF says `type` is not centrally registered and
because core carries only the codes every domain shares. It *rejects* an unknown
predicate, alone among the four, because `okfm_relations` feeds traversal and drift
propagation, which read a typed edge as fact. "A wrong edge is worse than a missing one"
is the rule the authoring contract states, and this quietly handed every pack author the
ability to mint one.

The fix was not to reorder the read. An overlay is now a **directory**, and the filename
inside it names the family, so `reason_codes.yaml` is the only file the reason-code load
will open. The bug is unreachable rather than corrected. This file is what keeps it that
way, because "unreachable" is a claim about code that somebody will refactor.

Two properties, both regression tests for a defect that shipped:

  isolation   a term declared in one family appears in that family and no other
  resolution  a pack path that is not a directory is REPORTED, never skipped

The second is not cosmetic. Skipping an unresolvable pack validates the mesh against core
vocabulary alone, so every domain term in the bundle fails at once — a hundred errors
whose single cause is one wrong path.

Project-local, like the other checks here: it tests this repository's implementation, not
an adopter's mesh. `needs: []`.
"""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(PROJECT / "dropin"))

from okfm_core import VOCAB, load_vocab, pack_dirs, vocab_terms  # noqa: E402

# Every family core ships. Read from disk rather than listed here, so adding a fifth
# vocabulary file puts it under this guard without anyone remembering to.
FAMILIES = sorted(p.stem for p in VOCAB.glob("*.yaml"))

CANARY = "zzz-canary-term"


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    if not FAMILIES:
        print(f"no vocabulary files in {VOCAB}", file=sys.stderr)
        return 2

    problems = []
    print(f"families: {', '.join(FAMILIES)}")

    with tempfile.TemporaryDirectory() as tmp:
        pack = Path(tmp) / "pack"
        pack.mkdir()

        # --- isolation ----------------------------------------------------
        # One family at a time: declare the canary only in that family's file, then
        # assert every OTHER family is unchanged by it.
        for declared in FAMILIES:
            for f in pack.glob("*.yaml"):
                f.unlink()
            (pack / f"{declared}.yaml").write_text(
                f"canary:\n  - {CANARY}\n", encoding="utf-8", newline="\n")

            for family in FAMILIES:
                has = CANARY in vocab_terms(family, [pack])
                if family == declared and not has:
                    problems.append(f"{declared}.yaml did not reach the {family} vocabulary "
                                    f"— the overlay is not being read at all")
                elif family != declared and has:
                    problems.append(f"a term declared in {declared}.yaml leaked into "
                                    f"`{family}` — an overlay must only reach the family "
                                    f"its filename names")
            print(f"  ok  {declared}.yaml reaches {declared} and nothing else"
                  if not problems else f"  FAIL  {declared}.yaml")

        # --- core survives an overlay -------------------------------------
        # An overlay ADDS. A pack that shadowed core would let a domain silently drop a
        # predicate the profile relies on, which is a fork wearing a config key's clothes.
        (pack / "predicates.yaml").write_text(
            "canary:\n  - " + CANARY + "\n", encoding="utf-8", newline="\n")
        core_only = vocab_terms("predicates", [])
        with_pack = vocab_terms("predicates", [pack])
        lost = core_only - with_pack
        if lost:
            problems.append(f"an overlay removed core predicate(s): {', '.join(sorted(lost))}")
        else:
            print(f"  ok  overlay adds without shadowing ({len(core_only)} core predicates kept)")

        # --- families stay separate in the merged map ----------------------
        # `load_vocab` returns family -> terms. The canary must appear under the pack's own
        # family heading, not smeared across core's.
        fams = load_vocab("predicates", [pack])
        if "canary" not in fams or CANARY not in fams.get("canary", []):
            problems.append("the overlay's family heading was lost in the merge")
        else:
            print(f"  ok  family headings survive the merge ({len(fams)} families)")

        # --- resolution: a bad path is reported, not skipped ---------------
        dirs, missing = pack_dirs({"pack": "no/such/pack"})
        if not missing or dirs:
            problems.append("pack_dirs skipped an unresolvable pack instead of reporting it "
                            "— every domain term would then fail against core alone")
        else:
            print("  ok  an unresolvable pack is reported, not skipped")

        # A file where a directory belongs is the exact mistake the old flat-list config
        # invited, so it is named rather than left to the `is_dir()` fallthrough.
        probe = Path(tmp) / "not-a-dir.yaml"
        probe.write_text("core:\n  - x\n", encoding="utf-8", newline="\n")
        try:
            rel = probe.relative_to(PROJECT)
        except ValueError:
            rel = probe
        _, missing_file = pack_dirs({"pack": str(rel)})
        if not missing_file:
            problems.append("a FILE passed as a pack was accepted — overlays are directories, "
                            "and the filename inside names the family")
        else:
            print("  ok  a file passed as a pack is rejected")

    print()
    for p in problems:
        print(f"  FAIL  {p}")
    print("OK — a pack adds to the family it names, and to no other"
          if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
