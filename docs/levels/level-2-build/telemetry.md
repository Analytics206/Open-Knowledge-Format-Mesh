# What a record holds

```yaml
telemetry_schema: 1.0
run_id: run_57be468464f04522a324
workflow: "okfm-rebuild@1.0 --check"
trigger: cli
duration_s: 0.31
steps:
  - { id: build, runs: build.py, exit: 0, seconds: 0.09 }
  ...
outcome: success
```

# Why the schema is versioned from the first record

Six months of run records are an asset **only if they are comparable**. Renaming or
repurposing a field silently invalidates every question asked of the history afterwards, and
nobody notices until the answer is already wrong.

Versioning is the cheapest decision in the system: one line, written before there is any
history to protect, and it protects all of it.

# Two documented divergences

**Location.** The specification puts run records inside a bundle. A mesh has six and a run
belongs to none of them, so records live under the drop-in folder — which also keeps
everything OKFM writes inside the directory you pasted.

**Not committed by default.** The specification treats records as durable bundle content. In
practice the build runs many times a day and each run would be a commit's worth of churn.
They are written always and gitignored by default; a team wanting shared history removes one
line, and the records are identical either way.

Both are noted in the module rather than in a decision record. The specification is a working
document and this is the kind of divergence it expects.

# It never fails a build

A telemetry write that cannot happen prints a note and returns. A record is a nice-to-have
about a run; the run is the point, and a build that fails because its logging failed has its
priorities backwards.
