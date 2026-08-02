# f31c0ace5e2d

## Answer

It is deliberate, and the reason is stated identically in three places: the code, the guide,
and the drop-in README. The rationale is **diagnostic quality, not correctness** — running the
remaining steps would produce a *second, misleading* error, and that second error is the one
people chase.

### Where the behaviour lives

`dropin/okfm.py`, in the full-pipeline loop over `STEPS`:

```python
        rc = run(script, args)
        rec.step(name, script, args, rc, time.monotonic() - t0)
        if rc != 0:
            # Stop on the first failure. A later step reading what an earlier one failed
            # to write reports a second, misleading problem.
            failed = (name, rc)
            break
```

`docs/okfm-guide/level-2-build/the-pipeline.md` has a section headed "It stops at the first
failure" whose entire body is: "Deliberately. A later step reading what an earlier one failed to
write reports a second, misleading problem, and the second problem is the one people chase."
`dropin/README.md` repeats the first sentence verbatim. The guide's trailing clause — *the second
problem is the one people chase* — is the part that names the actual failure mode being avoided.

### Why a later step's error would be misleading: the steps are a write-then-read chain

`STEPS` in `dropin/okfm.py` is ordered `config → build → refresh → view → check`, and each stage
consumes what the previous one wrote:

- `check_config.py` validates `okfm.json` before anything reads it.
- `build.py` writes concepts into the bundle, each with `sources[].okfm_captured: { hash: "sha256:…" }`.
- `refresh.py` reads those `okfm_captured` pins, observes the pointers, and writes the observation
  cache at `HERE / ".okfm-cache" / "observations.json"`.
- `bake_web_ui.py` reads both the bundles and that same `CACHE` path to bake `okfm-web-ui.html`.
- `check_bundles.py` validates every bundle — links, footnotes, and mesh registration.

So a `build` that dies partway leaves a partial bundle tree, and `check_bundles.py` would then
emit errors describing the *absence of the crashed step's output* rather than its cause: entries
like `broken link [...](...)` and `not registered — \`<mesh>\` has no concept with \`registers\` ->
/<bid>/index.md, so the mesh does not know this bundle exists`. Those read like a mesh-integrity
problem. They are an artifact of a build that never finished.

### The `config` step is the sharpest case, and it is why `config` is first

The comment above `STEPS` singles it out: "`config` runs first and stops the pipeline on an error.
A build that reads a config with a misspelled key does not fail — it quietly does something else,
and the adopter is left comparing what they wrote against what they got." `check_config.py`'s
docstring gives the mechanism — "every consumer of a config ignores keys it does not recognise, so
a misspelled `exlude` does not fail. It builds the wrong thing, quietly" — and states the contract
the pipeline relies on: "Exit 1 on an error, 0 otherwise, so the pipeline stops before building the
wrong thing." Here continuing past the failure would be worse than noisy: the downstream steps
would *succeed*, over the wrong inputs.

### The rule is per-step, not per-error — you still get the full error list

This is the nuance that keeps the design from being user-hostile. Stopping applies at the step
boundary; *within* a step, everything is accumulated and reported at once. `check_bundles.py`
builds `errors, warnings` lists across all three passes (conformance, profile, strip test) plus
link/footnote resolution, prints every entry, then `return 1 if errors else 0`. So the failing step
tells you all of its problems; what is suppressed is only the downstream steps whose inputs are
already known-bad.

### Stopping is cheap because the pipeline is designed to be re-run

`docs/decisions/0008-build-pipeline.md` makes idempotence an explicit acceptance criterion for
`okfm build`: "running it twice produces an empty diff." `build.py`'s `_owned()` docstring names
safe re-running as a hard requirement — "This is the rule that makes the build safe to re-run,
which it has to be: an adopter runs it after every documentation change, and a tool that eats your
edits on the second run gets deleted after the second run." Re-running after the fix therefore
redoes the already-successful steps at near-zero cost, so little is lost by not pushing through.
(The files state the idempotence and the stop rule separately; the connection between them is my
inference, not a claim either file makes.)

### The stop is loud, and it does not cost you the run record

`rec.write()` is called *before* the failure branch, so the telemetry record is written either way.
`telemetry.py`'s `Run.write()` derives `outcome: success | failed` from `all(s['exit'] == 0 for s in
self.steps)`, and each step's `exit` code is recorded — so the record shows exactly which step
failed and that the later ones never ran. The CLI then prints `"{name} failed (exit {rc}) —
stopping"` to stderr plus the run-record path, and returns `rc` as the process exit code. Telemetry
itself can never be the cause of a failure: `Run.write()` catches `OSError` and warns, because "a
record is a nice-to-have about a run; the run itself is the point."

### Consistency with the surrounding design

The same "a wrong signal is worse than no signal" principle recurs across the codebase, which is
why this choice fits rather than being an isolated preference:

- `dropin/guard.py` judges new files by a different rule to avoid "four misleading failures every
  time somebody authors a decision record… A guard that cries wolf on the normal case is worse than
  no guard."
- `okfm_relations` is never inferred, because "an edge asserted by a producer that guessed is worse
  than no edge, because traversal treats it as fact" (DR-0008).
- `refresh.py` reports `unknown` rather than defaulting to `match`, since a defaulted verdict would
  be "a stored opinion wearing a computed one's clothes."

Note also that the same stop rule governs `--check` (CI) mode, which runs the identical five steps
with different per-step arguments (`build` dry-runs with `[]`; `refresh` and `view` get `--check`
and fail on mismatch instead of writing).

## Files used

- dropin/okfm.py
- dropin/build.py
- dropin/check_config.py
- dropin/check_bundles.py
- dropin/refresh.py
- dropin/bake_web_ui.py
- dropin/telemetry.py
- dropin/guard.py
- dropin/README.md
- docs/okfm-guide/level-2-build/the-pipeline.md
- docs/okfm-guide/level-2-build/validation.md
- docs/decisions/0008-build-pipeline.md
