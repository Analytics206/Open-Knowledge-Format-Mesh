# examples/minimal

What an *adopter's* configuration looks like, as opposed to the one at the repository
root — which is OKFM self-hosting its own mesh.

Three differences worth noticing:

| | Root `okfm.json` | This one |
|---|---|---|
| `pack` | `null` — OKFM itself has no domain | `"warehouse"` — schema/query/metric shaped |
| `build.exclude` | the in-place decision records | an archive and a vendored tree |
| `build.include` | nothing outside `docs/` | `adr/`, which lives at the project top |
| `stores` | none | a SQL store, credentials **by reference** |

The credential line is the one to copy:

```json
"profile": "env:WAREHOUSE_DSN"
```

A config file gets committed. A credential does not. Stores name an environment variable or
a secret-manager handle and never the secret itself.

## You do not have to write any of this

Running the build with no configuration produces the same result and writes this file for
you. `docs/` is found, every folder of documents under it becomes its own OKF in `.okfm/`,
the loose files at the top become one more, and a mesh OKF is written over all of them.

The config has four groups — `build`, `bundles`, `read`, and the two pointer-resolution
keys. Four keys inside `build` are the ones worth knowing:

- **`build.root`** — read somewhere other than `docs/`.
- **`build.exclude`** — drop a folder **inside** the root. An `archive/` of superseded
  documents is the usual first entry.
- **`build.include`** — add a tree **outside** the root. This is the only way to reach one:
  no exclusion gets you to a directory the scan never entered, and nothing sweeps the project
  looking for concepts on its own.
- **`build.root_files`** — set to `false` when the loose documents at the top of `docs/` are a
  landing page and two stubs rather than knowledge.

Discovery runs on every build, not just the first, so a folder added next month gets an OKF
without anyone remembering to declare it. Naming bundles explicitly under `bundles` turns
discovery off entirely — someone who wrote that list meant it.

`read.exclude_scopes: ["guide"]` keeps the bundled guide out of your health statistics, your
injected index, and any context assembled for an agent. Leave it in place unless you have
deleted the guide.
