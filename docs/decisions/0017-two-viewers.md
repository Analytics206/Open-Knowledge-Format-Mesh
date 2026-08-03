---
type: Decision
title: DR-0017 — Two viewers, because one file was doing two opposite jobs
description: "The viewer an adopter copied had this project's mesh and steward baked into it — sixty-eight of somebody else's concepts in a file they had just added to their repository. The drop-in now ships a blank one and the build seeds it, which also makes Level 2 a single copy."
status: draft
tags: [distribution, web-ui, phase-2]
generated: { by: "agent:claude-opus-5", at: 2026-08-03T00:00:00Z }
okfm_scope: project
okfm_relations:
  - { predicate: part_of, target: /decisions/index.md }
  - { predicate: depends_on, target: /decisions/0015-the-install-has-an-upgrade.md }
---

# Context

`okfm-web-ui.html` at the download's root is Level 1. Open it and OKFM's own mesh is
there — the guide, the decision records, the graph, the health panel. It works with no
server and no build **because the data is baked into the file**. That is the whole design.

The README then told an adopter to copy that same file into their project.

# What was wrong

Measured, not reasoned about: the shipped viewer carries **68 concepts and
`human:analytics206` as the owner of four bundles.**

An adopter who copies it and opens it before running a build — the obvious thing to do after
copying a folder — sees another project's decision records and another person's name, in a
file they have just added to their own repository, looking exactly like it worked. If they
commit before building, that ships with their code.

One file was serving two purposes that want opposite things. At Level 1 the baked data is the
feature. At Level 2 it is somebody else's data sitting where theirs should be.

# Decision

**Two files, one generated from the other.**

| | Holds | For |
|---|---|---|
| `okfm-web-ui.html` at the download root | this project's mesh, baked | Level 1 — open it and read |
| `dropin/okfm-web-ui.html` | the same page with the three data blocks emptied | Level 2 — the build fills it |

**The build seeds it.** On a first run, if the configured viewer path holds no file and the
drop-in has a blank one, it is copied there and then filled with the adopter's mesh. So
Level 2 is now **one folder and one command** — which is what it always claimed to be, while
actually requiring two copies and a paragraph explaining why the second file lived somewhere
else.

**The template is generated, not maintained.** Two HTML files would be two copies of the
viewer's markup, and this project has had to reunify a rule split across two implementations
four times. `dev/check_viewer_template.py` blanks the shipped viewer and compares; editing
the page and forgetting the template fails there rather than shipping an adopter a page whose
markup is a version behind its data.

It also asserts the property directly rather than inferring it from the regeneration passing:
no concept, no bundle, and above all no person's name from this project appears in the blank
one. A template that merely looked right would still carry a name.

# What this is not

Not a privacy control. The data in question is a public repository's own documentation, and
the steward's handle is in every commit. The problem is that it is **wrong**, in a file whose
entire job is to show the reader their own mesh — and wrong in the way that looks like
working, which is the expensive kind.

# Consequences

`dev/check_readme.py` and `dev/check_pack_example.py` no longer copy the viewer into their
temporary projects. Both did, which pre-seeded the exact artefact under test — a fixture that
supplies the thing being checked reports success either way.

The skip path stays for the case where neither viewer is present: the mesh is built and valid
without a viewer, and taking the pipeline down for a missing reader would end an adopter's
first run in an error about a file they had never heard of.
