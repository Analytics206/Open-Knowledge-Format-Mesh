# What it prints

```bash
python okfm/okfm.py enrich          # the work, with the reason for each item
python okfm/okfm.py enrich --brief  # just the paths
```

Each item says which concept, what is wrong with it — drifted, extracted description, no
description at all — and what would make it right.

# Why the reason ships with the item

A list of paths tells an agent *where* to work and nothing about *what done looks like*. The
difference shows up immediately in output quality: given "this description is a quotation of
the first paragraph and does not say what the document is for," an agent writes a purpose.
Given a bare path, it writes a summary — which is the thing the admission test exists to
reject.

# It needs nothing, and it is still level 3

Mechanically this is arithmetic over frontmatter: `needs: []`, no network, no model.

It sits at level 3 because a work list exists only to be worked. Every item on it is a
request for prose that does not exist yet, which is the one thing level 2 cannot produce. A
component's level is the level of the thing it serves when it has no other reason to exist.

# Why it is not in the pipeline

Nothing here changes a file. Running it inside the default build would print work into the
middle of a CI log where nobody reads it, on every run, forever.

It is a report. Reports are asked for.
