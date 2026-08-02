# a8df4ee284cf

## Answer

### The misunderstanding in one line

`build.exclude` controls what the build **reads**. It does not control what the mesh **is**, and it does not delete anything a previous run already wrote. The web UI is fed by the second and third of those, not the first — so excluding a folder correctly stops new concepts being generated from it and changes nothing a reader can see.

The repo says this out loud in `docs/okfm-guide/level-2-build/config-validation.md` ("The two keys that look like the same key"): *"`exclude` says what gets **read**. `bundles` says what the mesh **is**. Nothing connects them, and the failure that follows is the most confusing kind available: you exclude a folder, re-run, and nothing changes — so the tool looks broken rather than misconfigured."*

### Where `build.exclude` actually takes effect

It has exactly one consumer. `okfm_core.normalize()` lifts `build.{root,root_files,exclude,include}` into a flat `discover` dict (`okfm_core.py:105-107`). `discover_sources()` then reads `d.get("exclude", [])` into `excluded` and applies it in the nested `skipped()` helper (`okfm_core.py:213-222`), which matches an entry either relative to its scan root (`archive`) or relative to the project (`docs/archive`) — "when a list called `exclude` is ambiguous, excluding is the safe reading."

`discover_sources()` is reached only via `resolve_sources()` (`okfm_core.py:258-268`), whose only real callers are the source loop in `build.py:284-322` and `check_config.orphaned_bundles()`. Nothing on the read/render path calls it. Spec §13.5 frames the same thing as **reach**: `build.exclude` "drops a folder **inside** a root".

Two things will silently make even that no-op:

- **An explicit `sources` list beats discovery outright.** `resolve_sources()` returns `cfg["sources"]` verbatim when present and never calls `discover_sources()`, so `build.exclude` is dead config. `config_schema.py:82-85` states it: *"Its presence turns discovery off entirely."*
- **A misspelled key is ignored by every consumer.** That is the entire reason `check_config.py` exists (`"a misspelled `exlude` does not fail. It builds the wrong thing, quietly"`).

### Why the concepts are still on disk

`build.py` writes concepts through `mirror()` and `write_index()` into `<project>/.okfm/<bundle>/`. It has exactly one delete path: `prune_members()` (`build.py:151-185`), and its docstring is explicit — *"This is the only place the build deletes anything, and it is deliberately narrow: `.md` files, in the mesh's own `members/` folder, that this process wrote."*

So an excluded folder simply stops being visited. `.okfm/<name>/` and every concept in it survive untouched. Worse, `prune_members()` computes `known = set(configured_bundles(cfg)) | {built names} | {mesh_dir.name}`, so while the stale directory still holds concepts (or is still named in `bundles`) it counts as known and even `.okfm/mesh/members/<name>.md` is not pruned.

### Why the web UI still lists them

`bake_web_ui.collect()` (`bake_web_ui.py:115-164`) enumerates bundles with `configured_bundles(cfg)` — never `resolve_sources()`. And `okfm_core.configured_bundles()` (`okfm_core.py:366-380`) has two modes, neither of which knows `exclude` exists:

1. If `"bundles" in cfg`, it returns that map resolved against the project, period.
2. Otherwise it lists every subdirectory of `bundle_root(cfg)` (`build.out`, default `.okfm`) containing at least one file with a non-empty `type:` — i.e. exactly the stale output folder you just left behind.

Your `okfm.json` is in case 1: it carries `build.exclude: ["decisions"]` *and* a six-entry `bundles` map (`mesh`, `level-1-view`, `level-2-build`, `level-3-enrich`, `docs`, `guide`). Anything named there is shown regardless of `exclude`. The same is true of `check_bundles.py:41`, which validates `configured_bundles(cfg)`.

### A third reason, if you ran the build alone

The viewer carries a **baked** snapshot. `bake_web_ui.py` rewrites three constants in `okfm-web-ui.html` — `BOOTSTRAP`, `CONFIG_SCHEMA`, `CONFIG` (the `_BLOCKS` table, `bake_web_ui.py:37-41`). `build.py` never invokes it. Only the full pipeline does, in order: `config` → `build` → `refresh` → `view` (`bake_web_ui.py`) → `check` (`okfm.py:44-50`). If you ran `python okfm/build.py --apply` or `okfm.py build`, the committed HTML still holds the previous index verbatim. `docs/okfm-guide/level-2-build/the-web-ui-bake.md` also explains why `view` must run *after* `refresh` (drift comes from the observation cache).

### What you actually have to change

1. **Delete the output folder.** `rm -rf .okfm/<name>/`. Nothing in the build will do it for you.
2. **If you have a `bundles` map, remove the `bundles.<name>` line.** This is what makes readers stop showing it; the `exclude` entry alone never could.
3. **Re-run the whole pipeline, not just the build:** `python <dropin>/okfm.py` (this repo's dropin lives at `dropin/`). That re-bakes the viewer via step 4 and lets `prune_members()` drop the now-unknown `.okfm/mesh/members/<name>.md` on the same run. `python <dropin>/okfm.py --check` is the CI form and will fail with `"STALE: committed viewer does not match the project"` until you do.
4. **Keep the `build.exclude` entry** — it is still correct, it is just not sufficient. Removing it would make the next build recreate the folder.

Alternatively, if the folder is an **in-place** bundle (its own markdown carries `type:` frontmatter, like `docs/decisions/` here), excluding it while leaving it in `bundles` is the *intended* configuration and you should change nothing: `build.py:76-81` refuses to mirror a file that is already a concept, so mirroring it would just be a second copy.

### The tooling already diagnoses this — run `okfm config`

Two checks were written for precisely your symptom:

- `check_config.orphaned_bundles()` (`check_config.py:49-83`) warns: *"this build no longer writes it, but it is still listed and still on disk — so every reader still shows it"*, with the hint *"the build stopped producing `<bid>` (check `build.exclude` and `build.root_files`). Remove the `bundles.<bid>` line and delete `<path>`, or put back the setting that built it."* It judges by the `generated.by: process:okfm-build` stamp (`_is_build_output`, matching `build.MINE`) rather than by location, so hand-authored bundles like `.okfm/guide/` are never falsely flagged.
- `config_schema._cross_checks()` (`config_schema.py:405-423`) warns when an excluded path is itself a `bundles` value: *"excluded from the build, but `bundles.<bid>` still names it — every reader still shows it."*

Two caveats about relying on them:

- The second one compares `f"{build.root}/{exclude_entry}"` against each `bundles` value, so it fires only when `bundles.<id>` points at the **source** folder (`docs/decisions`), not at the mirrored output (`./.okfm/decisions`). The mirror case is the `orphaned_bundles()` one.
- `orphaned_bundles()` returns `[]` immediately when `"bundles" not in cfg` (`check_config.py:61`). If you have no `bundles` map, `configured_bundles()` falls back to scanning `.okfm/` subdirectories, the stale folder still renders, and **nothing warns you**. Delete the folder regardless.

### Two things this is *not*

- **`read.exclude_scopes` is a different key entirely.** It filters by the `okfm_scope` frontmatter value (e.g. `guide`), not by folder, and per `config_schema.py:108-111` it governs health statistics and agent context assembly. `.okfm/mesh/log.md:62-64` additionally records that the web UI currently *hardcodes* the excluded scope to `guide` instead of reading `exclude_scopes` — "correct today by coincidence rather than by construction" — so do not expect it to hide a folder either.
- **`build.include` will not help.** Per spec §13.5 and `scan_roots()`, `include` adds a tree *outside* a root; an `include` path inside the root is dropped, and `config_schema._cross_checks()` warns *"inside `<root>`, so it is dropped"*.

### Aside: a latent crash on the diagnostic path

`check_config.orphaned_bundles()` line 64 does `{s["bundle"] for s in resolve_sources(cfg)}`, but `resolve_sources()` (`okfm_core.py:267`) normalizes a bare-string `sources` entry to `{"path": s, "type": "Document"}` with **no `bundle` key**. So a config with an explicit `sources` list of plain strings makes `okfm config` raise `KeyError: 'bundle'`. `build.py:302` handles the same case defensively with `entry.get("bundle")`.

### Verification note

`okfm-web-ui.html` is not present in this snapshot (only `dropin/bake_web_ui.py`, which reads and rewrites it at `PROJECT / "okfm-web-ui.html"`). My description of what the viewer displays is taken from the bake script's `collect()` payload and from `docs/okfm-guide/level-1-view/the-web-ui.md`, not from the HTML itself.

## Files used

- okfm.json
- README.md
- dropin/okfm_core.py
- dropin/build.py
- dropin/bake_web_ui.py
- dropin/config_schema.py
- dropin/check_config.py
- dropin/okfm.py
- dropin/check_bundles.py
- dropin/README.md
- docs/okfm-guide/level-2-build/config-validation.md
- docs/okfm-guide/level-2-build/the-web-ui-bake.md
- docs/okfm-guide/level-2-build/the-pipeline.md
- docs/okfm-guide/level-1-view/the-web-ui.md
- spec/okfm-v0.2.1.md
- .okfm/mesh/log.md
