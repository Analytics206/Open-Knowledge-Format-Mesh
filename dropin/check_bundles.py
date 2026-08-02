#!/usr/bin/env python3
"""Validate every bundle in the mesh -- the seed of `okfm validate`.

Runs three passes over each bundle named in okfm.json:

  conformance   parseable frontmatter, non-empty `type`, reserved-file structure (official 11)
  profile       `okfm_` prefix rule, controlled predicates, NO STORED VERDICTS (spec 3.4)
  strip test    remove every `okfm_` key and re-run conformance (spec 7.1 rule 4)

plus link and footnote resolution. Deliberately stdlib-only and regex-based -- no PyYAML --
which is the evidence behind decisions/0001's zero-dependency validator argument.

`needs: []` -- no network, no secrets, no model. Exits non-zero on any failure.
"""
import re
import sys
from pathlib import Path

from okfm_core import (ACTOR_KINDS, PROJECT, actor_kind, actor_of, configured_bundles,
                       load_or_create_config, parse_relations, vocab_terms)

_FM = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
_OKFM_KEY = re.compile(r"^(okfm_[\w]+):", re.M)
_STORED_VERDICT = re.compile(r"^okfm_(stale|drifted|drift|trust|tier|fresh)\s*:", re.M)
# One source entry: what it points at, and the hash it pinned.
_SOURCE_PIN = re.compile(r'resource:\s*(\S+)[\s\S]*?okfm_captured:\s*\{\s*hash:\s*"?'
                         r'sha256:([0-9a-f]+)')

_REASON_CODES = re.compile(r"^okfm_reason_codes:\s*(\[.*?\]|\n(?:[ \t]*-.*\n?)+)", re.M)


def scalar(block, key):
    m = re.search(rf"^{key}:[ \t]*(.*(?:\n[ \t]+\S.*)*)$", block, re.M)
    if not m:
        return None
    v = " ".join(p.strip() for p in m.group(1).splitlines()).strip()
    return (v[1:-1] if v[:1] in "\"'" and v[-1:] in "\"'" else v) or None


def main() -> int:
    _, cfg, _ = load_or_create_config(write=False)
    bundles = configured_bundles(cfg)
    errors, warnings = [], []
    total = 0

    # Overlays let a pack add domain terms without forking core (spec 10.2). Core alone
    # carries no domain words, which is what keeps the tooling portable (13.3).
    overlays = [(PROJECT / p) for p in cfg.get("vocab_overlays", [])]
    predicates = vocab_terms("predicates", overlays)
    reason_codes = vocab_terms("reason_codes", overlays)
    known_types = vocab_terms("types", overlays)
    if not predicates:
        errors.append("vocab/predicates.yaml is missing or empty — cannot check relations")

    if not bundles:
        print("No bundles found. Run build.py first, or point `bundles` at one.")
        return 0

    # Which bundles the registry claims as members. Collected during the walk and checked
    # at the end -- see `registered` below for why this is an error rather than a nicety.
    registered: set[str] = set()
    registry = None
    reg_path = (cfg.get("federation") or {}).get("registry") or cfg.get("mesh")
    if reg_path:
        want = (PROJECT / str(reg_path).removeprefix("./")).resolve()
        registry = next((b for b, p in bundles.items()
                         if p.resolve() == want or b == reg_path), None)

    # Every concept path in the mesh, so relation targets resolve across bundles.
    mesh_paths = set()
    for bid, src in bundles.items():
        if src.is_dir():
            root = f"/{bid}"
            for f in src.rglob("*.md"):
                if _FM.match(f.read_text(encoding="utf-8")):
                    mesh_paths.add(f"{root}/{f.relative_to(src).as_posix()}")

    for bid, src in sorted(bundles.items()):
        if not src.is_dir():
            errors.append(f"{bid}: configured path does not exist ({src})")
            continue
        if not (src / "index.md").is_file():
            # Said plainly, because the symptom otherwise surfaces somewhere else entirely:
            # the mesh's member concept points at `/<bid>/index.md` and the failure reads as
            # a dangling relation in a different bundle, which is two steps from the cause.
            errors.append(f"{bid}: no index.md — a bundle's index is its directory map "
                          f"(spec 6.1), and the mesh points every member at one")
            continue
        root = f"/{bid}"
        n = 0

        for f in sorted(src.rglob("*.md")):
            text = f.read_text(encoding="utf-8")
            fm = _FM.match(text)
            rid = f"{bid}/{f.relative_to(src).as_posix()}"
            if not fm:
                warnings.append(f"{rid}: no frontmatter — not a concept, ignored")
                continue
            block, body = fm.group(1), text[fm.end():]
            n += 1
            total += 1

            # --- conformance -------------------------------------------------
            ctype = scalar(block, "type")
            if not ctype:
                errors.append(f"{rid}: missing or empty `type` (conformance failure)")
            elif known_types and ctype not in known_types:
                # A WARNING, never an error. Official OKF §6.2: `type` is not centrally
                # registered and consumers must tolerate unknown values. This catches
                # typos, it does not police vocabulary.
                warnings.append(f"{rid}: type `{ctype}` is not a known type — typo, "
                                f"or add it to a pack overlay")

            # --- strip test: type is official, so it must survive the strip ---
            stripped = _OKFM_KEY.sub("__stripped__:", block)
            if not scalar(stripped, "type"):
                errors.append(f"{rid}: fails the strip test — `type` depends on an okfm_ key")

            # --- profile: derived, never stored (spec 3.4) --------------------
            if _STORED_VERDICT.search(block):
                bad = _STORED_VERDICT.search(block).group(0).strip()
                errors.append(f"{rid}: stores a derived verdict `{bad}` (spec 3.4 forbids)")

            # --- profile: one hash per source, and it must be that source's ---
            # Two different files cannot share a sha256. When two of a concept's sources
            # carry the same captured hash, at most one of them is real and the other
            # reports drift forever while carrying no signal — the exact failure a pinned
            # hash exists to prevent, wearing its clothes. `revalidate.py` wrote this state
            # for a while by stamping one hash across every source it found.
            pins = {}
            for res, digest in _SOURCE_PIN.findall(block):
                if digest in pins and pins[digest] != res:
                    errors.append(f"{rid}: `{res}` and `{pins[digest]}` pin the same hash — "
                                  f"two different files cannot, so at least one pointer is "
                                  f"wrong and will report drift forever")
                pins[digest] = res

            # --- profile: the actor vocabulary (spec 6.3) ---------------------
            # `generated.by` and `verified.by` are read by the ownership model, not just
            # displayed: the build decides what it may overwrite from one, and the trust tier
            # a reader sees is derived from the other. An actor with an unrecognised prefix is
            # classified as nothing in particular, which quietly means "machine" — so a
            # mistyped `humna:alex` silently downgrades a real review rather than failing.
            #
            # A warning, not an error, and deliberately: official OKF does not constrain this
            # field, and rejecting an adopter's existing convention would be OKFM policing a
            # value it merely reads. The trust model degrades safely — it never awards a tier
            # it cannot justify — so saying so is enough.
            for key in ("generated", "verified"):
                who = actor_of(block, key)
                if who and not actor_kind(who):
                    warnings.append(f"{rid}: {key}.by `{who}` — unknown actor kind. "
                                    f"One of {', '.join(k + ':' for k in ACTOR_KINDS)}, "
                                    f"or the trust tier reads it as a machine")

            # --- profile: controlled predicates (spec 7.3) --------------------
            # Both YAML forms, via the one parser in `okfm_core`. This had its own copy that
            # required the comma between the keys, so block form was silently skipped here —
            # and the viewer's bake had a second copy with the same flaw, so those edges were
            # neither checked nor drawn. Spec 7.3's own primary example was block form.
            for pred, tgt in parse_relations(block):
                if pred not in predicates:
                    errors.append(f"{rid}: predicate `{pred}` not in the vocabulary")
                # An absolute target whose first segment names a bundle is mesh-absolute;
                # anything else absolute is relative to its own bundle root. Without this
                # a concept cannot address another bundle at all, which would make a
                # mesh of six bundles unable to say how they relate.
                mesh_tgt = tgt
                if tgt.startswith("/"):
                    head = tgt.lstrip("/").split("/", 1)[0]
                    mesh_tgt = tgt if head in bundles else f"{root}{tgt}"
                    if pred == "registers" and bid == registry:
                        registered.add(head)
                if mesh_tgt not in mesh_paths:
                    errors.append(f"{rid}: relation target {tgt} resolves to nothing")

            # --- profile: controlled reason codes (spec 10.2) ------------------
            # A WARNING, not an error, until domain packs exist. Core carries only the
            # four codes every domain shares, so failing on an unknown one would reject
            # every legitimate domain code before there is any way to declare it.
            rc = _REASON_CODES.search(block)
            if rc:
                raw = rc.group(1)
                codes = (re.findall(r"[\w_]+", raw) if raw.strip().startswith("[")
                         else re.findall(r"^\s*-\s*([\w_]+)", raw, re.M))
                for code in codes:
                    if code not in reason_codes:
                        warnings.append(
                            f"{rid}: reason code `{code}` is not in core vocabulary — "
                            f"declare it in a pack overlay")

            # --- body links ---------------------------------------------------
            fence = False
            for line in body.splitlines():
                if re.match(r"^\s{0,3}(```|~~~)", line):
                    fence = not fence
                    continue
                if fence:
                    continue
                for label, tgt in re.findall(r"\[([^\]]+)\]\(([^)#]+?)(?:#[^)]*)?\)", line):
                    if tgt.startswith(("http", "mailto:", "okf://", "sys://", "store://")):
                        continue
                    if not (f.parent / tgt).resolve().exists():
                        errors.append(f"{rid}: broken link [{label}]({tgt})")

            # --- footnotes ----------------------------------------------------
            for ref in set(re.findall(r"\[\^([\w-]+)\](?!:)", body)):
                if not re.search(rf"^\[\^{re.escape(ref)}\]:", body, re.M):
                    errors.append(f"{rid}: footnote [^{ref}] referenced but never defined")

        print(f"  {n:>3} concepts  {bid}")

    # --- the mesh must name every bundle (spec 12.2) --------------------------
    # An unregistered bundle is the mesh lying about itself in the one place it cannot
    # afford to: a reader asks the registry what exists and gets an incomplete answer, with
    # nothing anywhere to say so. Checking it here is what keeps membership from depending
    # on somebody remembering to add an edge.
    if registry:
        for bid in sorted(bundles):
            if bid == registry or not (bundles[bid] / "index.md").is_file():
                continue
            if bid not in registered:
                errors.append(f"{bid}: not registered — `{registry}` has no concept with "
                              f"`registers` -> /{bid}/index.md, so the mesh does not know "
                              f"this bundle exists")

    print(f"\n{total} concepts across {len(bundles)} bundles")
    for w in warnings:
        print(f"  warn  {w}")
    for e in errors:
        print(f"  FAIL  {e}")
    print()
    print("OK — mesh is valid" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
