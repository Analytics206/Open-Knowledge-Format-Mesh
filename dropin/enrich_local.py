#!/usr/bin/env python3
"""Draft descriptions with a model running on your own machine — level 3, local variant.

    python okfm/okfm.py enrich-local             # what it would write
    python okfm/okfm.py enrich-local --apply     # write it
    python okfm/okfm.py enrich-local --limit 1   # try one first

`needs: [model]` — the only component in this folder that is not `needs: []`, and the
reason it is absent from `okfm.py`'s pipeline. A workflow's needs set is the union of
everything it invokes (DR-0008), so putting this in the default run would take the whole
pipeline out of CI on a fork's pull request.

## Why this is level 3, not "level 2 and a half"

The level 2/3 line is the `model` line, exactly, and `dev/check_levels.py` enforces it. A
component that calls a model is level 3 whether the model runs in a data centre or on the
laptop it is called from.

What makes this feel lighter is that it holds no key — and that distinction is already on
the ladder, one rung further up: this is `needs-model` **without** `needs-secrets`. Level 3
has three variants, and only the third holds a credential:

    your agent   your agent drives OKFM   OKFM calls nothing        `enrich.py`
    local        OKFM drives a model      on this machine, no key   this file
    credentialed OKFM drives a provider   a hosted API, with a key  not built

See [DR-0013](../docs/decisions/0013-the-local-model-variant.md).

## What it may write, and what it may not

`description` and `tags`, and it must restamp `generated.by` as itself. Everything else in
DR-0008's ownership table belongs to a person or to the build, and `okfm.py guard` checks
the diff afterwards rather than trusting this file to have behaved.

Two rules on top of the shared contract, because a small local model is not your agent:

- **The model replaces the tag set, except for `needs-*`.** Those are the level ladder — a
  project-local claim about exposure that `dev/check_levels.py` reads as fact — so existing
  ones are carried over verbatim and any the model proposes are dropped. Everything else is
  a `[model]` field under DR-0008, and owning a field means replacing it.
- **It is never asked whether a concept should be deleted.** `enrich.py`'s brief asks your
  agent that, because your agent can read the whole mesh and weigh it. This sees one
  document and cannot.

## What it will not touch

A concept carrying `verified:`, or one whose `generated.by` names a person. The work list
already excludes anything drafted, so neither should arrive here — but the check is cheap
and the failure it prevents is silently overwriting a review.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

from enrich import FORBIDDEN, work_list
from okfm_core import PROJECT, find_config, frontmatter, scalar, utf8_stdout

utf8_stdout()

DEFAULTS = {"base_url": "http://localhost:11434", "model": None,
            "num_ctx": 8192, "timeout_s": 120}

MAX_DESC = 400        # characters, not tokens — this is a YAML line, not a budget
MAX_TAGS = 6

SYSTEM = """\
You write one-sentence descriptions for an index of technical documents.

Return ONLY a JSON object, nothing else:
  {"description": "...", "tags": ["...", "..."]}

description: state the document's main point in its own voice, as its author would if
  asked to put it in one line. Under 300 characters. No markdown, no line breaks, no
  surrounding quotes.

  Never write ABOUT the document. "This document explains...", "The document claims...",
  "A guide to...", "Covers..." all describe the container instead of the content, and the
  reader can already see the container.

    RIGHT  Drift is observed at build time and never at read time.
    WRONG  This document explains how drift is observed.

    RIGHT  Two adapters cover the field, because nearly every provider speaks one of them.
    WRONG  A discussion of provider adapter design.

  If the document argues for something, the description is the argument's conclusion.

tags: zero to six lowercase topics, single words or hyphenated. Omit rather than guess.

Every word must be supported by the document. Do not invent, and do not describe what the
document ought to say.
"""

USER = """\
Title: {title}
Current description: {desc}

Document:
---
{text}
---
"""


def settings() -> dict:
    _, cfg = find_config()
    out = dict(DEFAULTS) | {k: v for k, v in (cfg.get("enrich") or {}).items()
                            if v is not None}
    return out


# ── talking to the model ───────────────────────────────────────────────────────

def ask(cfg: dict, title: str, desc: str, text: str) -> str:
    """One request, one answer. Ollama's native chat API — no key, no SDK, no dependency."""
    payload = {
        "model": cfg["model"],
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": USER.format(title=title, desc=desc,
                                                             text=text)}],
        "stream": False,
        "format": "json",
        # Off for the same reason temperature is 0: the answer is in the document, and a
        # reasoning trace re-derives what one read already gives you. Measured on a reasoning
        # model over a trivial prompt: 2.8k characters of thinking on a 4B and 6k on a 9B,
        # taking 15s and 89s against 1-2s with this set. On a real work list that is the
        # difference between a queue that drains and one that times out.
        "think": False,
        # Extraction-shaped work has one right answer sitting in the source. Sampling for
        # variety would only make a second run disagree with the first, which turns a queue
        # that should drain into one that regenerates its own work.
        "options": {"temperature": 0, "num_ctx": cfg["num_ctx"]},
    }
    req = urllib.request.Request(
        cfg["base_url"].rstrip("/") + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=cfg["timeout_s"]) as r:
        return json.loads(r.read().decode("utf-8"))["message"]["content"]


_FENCE = re.compile(r"\A\s*```(?:json)?\s*(.*?)\s*```\s*\Z", re.S)


def parse(raw: str, keep: list[str]) -> tuple[dict | None, str]:
    """The model's answer, or the reason it is being refused.

    Everything a model returns is a proposal. A description that arrived malformed is not a
    smaller version of a good one — it is a sentence nobody wrote — so this rejects rather
    than repairs, and says which rule it broke.
    """
    m = _FENCE.match(raw)
    if m:
        raw = m.group(1)                      # instructed not to, and they do it anyway
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, "did not return JSON"
    if not isinstance(data, dict):
        return None, "returned JSON that is not an object"

    desc = data.get("description")
    if not isinstance(desc, str):
        return None, "no `description` in the answer"
    desc = " ".join(desc.split())             # a folded YAML scalar is not worth the risk
    if not desc:
        return None, "returned an empty description"
    if len(desc) > MAX_DESC:
        return None, f"description is {len(desc)} characters, over the {MAX_DESC} cap"

    proposed = [t.strip().lower() for t in (data.get("tags") or [])
                if isinstance(t, str) and t.strip()]
    # The level ladder is not the model's to write. `dev/check_levels.py` reads these tags
    # as a claim about exposure, so one invented here would forge the check that exists to
    # stop a component drifting out of its level. Carried over verbatim, never proposed.
    ladder = [t for t in keep if t.startswith("needs-")]
    topics = []
    for t in proposed:
        if t.startswith("needs-") or t in ladder or t in topics:
            continue
        topics.append(t)
        if len(topics) == MAX_TAGS:
            break
    return {"description": desc, "tags": ladder + topics}, ""


# ── writing it back ────────────────────────────────────────────────────────────

_FOLDED = r"(?:\n[ \t]+\S.*)*"


def _set(block: str, key: str, value: str, before: str = "generated") -> str:
    """Replace one top-level key, or insert it before `before`.

    Continuation lines go with it. A folded `description` whose first line was replaced
    would leave the rest of the old sentence behind as stray YAML — valid enough to parse
    and wrong enough to be read as part of the new one.
    """
    line = f"{key}: {value}"
    pattern = re.compile(rf"^{key}:[ \t]*.*{_FOLDED}$", re.M)
    if pattern.search(block):
        return pattern.sub(lambda _: line, block, count=1)
    anchor = re.search(rf"^{before}:", block, re.M)
    return (block[:anchor.start()] + line + "\n" + block[anchor.start():]) if anchor \
        else f"{block}\n{line}"


def _quoted(s: str) -> str:
    """A double-quoted YAML scalar. `okfm_core.scalar` unescapes `\\"`, so this round-trips."""
    return '"' + s.replace('"', '\\"') + '"'


def refuse(block: str) -> str:
    """Why this concept is not ours to rewrite, or empty."""
    if re.search(r"^verified:", block, re.M):
        return ("carries `verified` — somebody signed this off, and rewriting it would "
                "invalidate a review nobody withdrew")
    by = re.search(r'by:\s*"?([^",}]+)', scalar(block, "generated") or "")
    actor = by.group(1).strip() if by else ""
    if actor.startswith("human:"):
        return f"written by {actor} — a person's prose, not a slot to fill"
    return ""


def read_source(concept, uri: str, budget: int) -> tuple[str, bool]:
    """The text the description should describe, capped. Returns (text, truncated)."""
    target = (concept.parent / uri).resolve()
    if target == concept.resolve():
        # In-place: the file IS the concept, so its frontmatter is not part of what it says.
        _, body = frontmatter(target)
        text = body or ""
    else:
        text = target.read_text(encoding="utf-8")
    return (text[:budget], True) if len(text) > budget else (text, False)


# ── the run ────────────────────────────────────────────────────────────────────

def main() -> int:
    argv = sys.argv[1:]
    apply = "--apply" in argv
    limit = None
    for i, a in enumerate(argv):
        if a == "--limit" and i + 1 < len(argv):
            limit = int(argv[i + 1])
        elif a.startswith("--limit="):
            limit = int(a.split("=", 1)[1])

    cfg = settings()
    if not cfg["model"]:
        print("No model configured. Add one to okfm.json:\n", file=sys.stderr)
        print('  "enrich": { "base_url": "http://localhost:11434", "model": "llama3.2" }\n',
              file=sys.stderr)
        print("Then `ollama pull llama3.2`. Nothing here needs a key — that is the point.",
              file=sys.stderr)
        return 2

    host = urlsplit(cfg["base_url"]).hostname or ""
    obs, items = work_list()
    if obs is None:
        print("No observations yet — run `okfm.py refresh` first.")
        return 0

    todo = [i for i in items if not i["drafted"]]
    if not todo:
        print("Nothing to draft. Every drifted concept already has one.")
        print("Clearing drift is yours:  python okfm/okfm.py revalidate <path> --by human:you")
        return 0
    if limit:
        todo = todo[:limit]

    # Ollama defaults to a 2048-token context and truncates in silence. Three characters per
    # token is pessimistic on purpose; the alternative is describing half a document and not
    # knowing it.
    budget = max(2000, (cfg["num_ctx"] - 800) * 3)

    print(f"model   : {cfg['model']}  @ {cfg['base_url']}")
    if host and host not in ("localhost", "127.0.0.1", "::1"):
        print(f"          note: {host} is not this machine — see `okfm.py config`")
    print(f"drafting: {len(todo)} concept(s)"
          + ("" if apply else "  — preview only, add --apply to write") + "\n")

    written, refused = 0, 0
    for it in todo:
        block, body = frontmatter(it["path"])
        rel = it["path"].relative_to(PROJECT).as_posix()

        why = refuse(block)
        if why:
            print(f"  skip     {it['rid']}\n           {why}")
            refused += 1
            continue

        try:
            text, cut = read_source(it["path"], it["uri"], budget)
        except OSError as e:
            print(f"  skip     {it['rid']}\n           cannot read {it['uri']}: {e}",
                  file=sys.stderr)
            refused += 1
            continue

        try:
            raw = ask(cfg, it["title"], it["desc"], text)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:200]
            print(f"\n{cfg['base_url']} answered {e.code}: {detail}", file=sys.stderr)
            if e.code == 404:
                print(f"`ollama pull {cfg['model']}` first.", file=sys.stderr)
            return 1
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"\nNo answer from {cfg['base_url']} ({e}).", file=sys.stderr)
            print("Start it with `ollama serve`, or point `enrich.base_url` somewhere else.",
                  file=sys.stderr)
            return 1

        proposal, problem = parse(raw, _tags_of(block))
        if problem:
            print(f"  refused  {it['rid']}\n           {problem}")
            refused += 1
            continue

        same = proposal["description"] == it["desc"]
        print(f"  {'draft' if not same else 'same '}    {it['rid']}"
              + ("   (source truncated to fit the context window)" if cut else ""))
        print(f"           was  {it['desc'][:96]}")
        print(f"           now  {proposal['description'][:96]}")
        if proposal["tags"]:
            print(f"           tags {', '.join(proposal['tags'])}")

        if not apply:
            continue

        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        new = _set(block, "description", _quoted(proposal["description"]))
        new = _set(new, "tags", "[" + ", ".join(proposal["tags"]) + "]")
        # Required, not bookkeeping: `bootstrap --refresh` decides what it may recompute by
        # reading this field, so a description improved here that still says
        # `process:okfm-bootstrap` gets silently clobbered on a later run.
        new = _set(new, "generated",
                   f'{{ by: "agent:ollama/{cfg["model"]}", at: {stamp} }}')
        it["path"].write_text(f"---\n{new}\n---\n{body}", encoding="utf-8", newline="\n")
        written += 1

    print()
    if not apply:
        print("Nothing written. Re-run with --apply.")
        return 0

    print(f"{written} concept(s) drafted by agent:ollama/{cfg['model']}"
          + (f", {refused} refused" if refused else ""))
    if written:
        print("\nCheck it stayed in its lane, then review it yourself:")
        print(f"  python okfm/okfm.py guard {_scope(todo)}")
        print("  python okfm/okfm.py revalidate <path> --by human:you")
        print("\nA draft is not a verdict. Drift stands until a person clears it — this wrote")
        print("prose, not trust, and running the model locally changes nothing about who is")
        print("allowed to assert a review.")
    return 0


def _tags_of(block: str) -> list[str]:
    m = re.search(r"^tags:[ \t]*\[(.*?)\][ \t]*$", block, re.M)
    return [t.strip() for t in m.group(1).split(",") if t.strip()] if m else []


def _scope(items) -> str:
    """The paths guard should look at — the pass, not everything uncommitted."""
    return " ".join(sorted({i["path"].relative_to(PROJECT).parent.as_posix()
                            for i in items}))


if __name__ == "__main__":
    raise SystemExit(main())
