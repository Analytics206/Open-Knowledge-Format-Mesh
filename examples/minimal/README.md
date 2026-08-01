# examples/minimal

What an *adopter's* configuration looks like, as opposed to the one at the repository
root — which is OKFM self-hosting its own guide.

Three differences worth noticing:

| | Root `okfm.json` | This one |
|---|---|---|
| `pack` | `null` — OKFM itself has no domain | `"warehouse"` — schema/query/metric shaped |
| `bundles` | the bundled guide | the adopter's own `./okf` |
| `stores` | none | a SQL store, credentials **by reference** |

The credential line is the one to copy:

```json
"profile": "env:SP3D_DSN"
```

A config file gets committed. A credential does not. Stores name an environment
variable or a secret-manager handle and never the secret itself.

`exclude_scopes: ["guide"]` keeps the bundled guide out of your health statistics,
your injected index, and any context assembled for an agent. Leave it in place unless
you have deleted the guide.

Everything except `pack` is optional. Omit `bundles` and discovery falls back to
convention — any `.md` file with a non-empty `type:` in its frontmatter, anywhere in
the project.
