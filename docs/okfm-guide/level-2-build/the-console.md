# Approving used to be four edits

```bash
python okfm/okfm.py console --by human:you
```

Everything the build writes is `status: draft`. Approving one by hand meant opening the file
and changing four things: `status` to `stable`, a `verified` entry with your handle and the
time, and a repin of every `okfm_captured` in `sources`.

The last is the one that matters and the one nobody remembers. Skip it and the drift you just
reviewed is back on the next `refresh`, with nothing to say the review was incomplete.

`revalidate --by human:you --stable` already did all four in one command. What was missing was
a way to reach it from the page where you had just decided the concept was fine — so it is a
button now, on a **Review** page listing every draft and on any concept's detail panel.

# The same file, opened from disk, has none of this

The console serves `okfm-web-ui.html`, the same page level 1 opens. The edit surface appears
only when something answers `/api/ping`, which nothing does on `file://`.

That is not a convention. `EDIT.on` is assigned in exactly one place — inside the probe — and
`dev/check_viewer_template.py` fails if it is assigned anywhere else in either viewer. A
"force edit" query parameter would be one line and invisible in review; it fails there.

Delete `console.py` and a fully working viewer remains.

# It edits sections, not files

A concept is two documents in one file: frontmatter a validator reads by key, and a body a
person reads by heading. `concept_edit.py` splits it into both, and writes back only what
changed — so an edit to one section cannot disturb the half you were not looking at.

```bash
python okfm/okfm.py edit .okfm/level-2-build/the-pipeline.md
```

Top-level keys are edited as **raw text**, because there is no YAML parser here and adding one
would be a second parser disagreeing with the first at the margins. A key you do not touch is
returned byte for byte, and it is replaced by line number rather than by searching for its
text — which matters more than it sounds, because the search version once took a request to
set `status` and rewrote a `description` that happened to quote it.

**A save changes what you edited and nothing else.** Not a blank line, not a trailing newline,
not the spacing inside a code block. `dev/check_edit.py` holds that over every concept here
and over a table of shapes chosen because they are awkward — an unclosed fence, a heading with
no blank line under it, a body that ends without a newline.

**Sections never split a code fence.** A `#` line inside a fenced block is code, not a
heading. That sounds pedantic until you open the guide's own `first-concept.md`, which teaches
you to write a concept by showing you one inside a ```` ```markdown ```` block: its example's
`# Decision` and `# Why` were being offered as editable sections of the *outer* document, with
the fence's opening in one box and its close in another. Nine sections where there are six.

`generated` and `sources` are shown and not editable. They record *when a machine did
something*; editing them is not an edit but a claim about history. The refusal lives in the
module, not in the page — the server rejects the edit even if the browser offers it.

# What it will not do

**Write a concept field itself.** Approve shells out to `revalidate.py`, saving goes through
`concept_edit.py`, the pipeline button runs `okfm.py`. Every one is what the command line
runs, so a change cannot behave one way in a browser and another in a terminal.

**Run without knowing who you are.** `--by` is required and must be `human:<id>` — the same
refusal `revalidate` makes, because a web page does not turn a machine's edit into a person's.
The handle sits in the masthead the whole time it runs.

**Accept a filename from the browser.** The page addresses concepts by mesh path —
`/level-2-build/the-pipeline.md` — and the server resolves it against a map built from the
same function the bake stamps into the page. Nothing the client sends is ever joined to a
directory, so there is nothing to escape from. Mutations also need an `X-OKFM` header, which
a cross-origin page cannot set, and it binds the loopback only.

# One steward, one keyboard

No authentication, no locking, and undo is one step deep and lives in the server's memory.
That is honest for a tool a person runs on their own machine against their own repository. A
second steward, or a hosted instance, is where it stops being enough.
