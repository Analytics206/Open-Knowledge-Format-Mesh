"""Run records — spec §10.1.

One YAML file per run. Not a concept: telemetry does not belong in the concept graph and
would swamp it (§7.1 rule 5), so it lives outside the bundles and is invisible to
conformance, which governs `.md` files.

The point is not observability for its own sake. It is that six months of records are an
asset **only if they are comparable**, which is why `telemetry_schema` is versioned and why
renaming or repurposing a field requires bumping it. That is the cheapest decision in the
system and it protects every question asked of the history later.

## Two deliberate divergences from §10.1

**Location.** §7.2 puts telemetry at `<bundle>/references/telemetry/runs/`. A mesh has
several bundles and a run belongs to none of them, so records go under the drop-in folder
instead — which also keeps everything OKFM writes inside the directory you pasted, so
deleting it leaves the project as it was.

**Committed by default: no.** §10.1 treats records as durable bundle content. In practice
the build runs many times a day during development and each run would be a commit's worth
of churn. They are written always and gitignored by default; a team that wants shared run
history removes the ignore. The records themselves are identical either way.

Both noted here rather than in a decision record — the specification is a working document,
and this is the kind of divergence it expects (see its status note).
"""
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from okfm_core import HERE

SCHEMA = "1.0"
RUNS = HERE / "references" / "telemetry" / "runs"

# Everything a run record needs that is not a step. Kept flat and boring on purpose:
# a field that is hard to write is a field that stops being written.
_SAFE = re.compile(r"[^A-Za-z0-9._-]")


def new_run_id() -> str:
    return "run_" + uuid.uuid4().hex[:20]


def _q(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    return f'"{s}"' if _SAFE.search(s) else s


class Run:
    """Accumulates a record and writes it once, at the end.

    Writing incrementally would be more robust to a crash, but a half-written record that
    looks complete is worse than an absent one — the history has to be trustworthy or it
    is not worth keeping.
    """

    def __init__(self, workflow: str, trigger: str | None = None):
        self.id = new_run_id()
        self.workflow = workflow
        self.trigger = trigger
        self.started = datetime.now(timezone.utc)
        self.steps: list[dict] = []

    def step(self, name: str, script: str, args: list[str], rc: int, seconds: float) -> None:
        self.steps.append({
            "id": name, "runs": script, "args": " ".join(args) or None,
            "exit": rc, "seconds": round(seconds, 2),
        })

    def write(self, produced: list[str] | None = None) -> Path | None:
        finished = datetime.now(timezone.utc)
        lines = [
            f"telemetry_schema: {_q(SCHEMA)}",
            f"run_id: {_q(self.id)}",
            f"workflow: {_q(self.workflow)}",
            f"trigger: {_q(self.trigger)}",
            f"started_at: {_q(self.started.isoformat(timespec='seconds'))}",
            f"finished_at: {_q(finished.isoformat(timespec='seconds'))}",
            f"duration_s: {round((finished - self.started).total_seconds(), 2)}",
            "",
            "# Every step here is `needs: []` under decisions/0008 — no model, no secrets.",
            "# A run that required either would say so, and would not be in CI.",
            "steps:",
        ]
        for s in self.steps:
            lines.append(f"  - id: {_q(s['id'])}")
            lines.append(f"    runs: {_q(s['runs'])}")
            if s["args"]:
                lines.append(f"    args: {_q(s['args'])}")
            lines.append(f"    exit: {s['exit']}")
            lines.append(f"    seconds: {s['seconds']}")
        lines += [
            "",
            f"outcome: {_q('success' if all(s['exit'] == 0 for s in self.steps) else 'failed')}",
            f"produced: {_q(None) if not produced else ''}",
        ]
        if produced:
            lines[-1] = "produced:"
            lines += [f"  - {_q(p)}" for p in produced]
        lines.append("")

        try:
            RUNS.mkdir(parents=True, exist_ok=True)
            out = RUNS / f"{self.id}.yaml"
            out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
            return out
        except OSError as e:
            # Telemetry must never be the reason a build fails. A record is a nice-to-have
            # about a run; the run itself is the point.
            print(f"  (telemetry not written: {e})", file=sys.stderr)
            return None
