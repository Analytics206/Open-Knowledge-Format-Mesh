# The half that already shipped

Federation splits cleanly in two, and the cheap half is done: a registry bundle, `OKF Member`
concepts, cross-bundle references, commit pinning, and a viewer that renders more than one
bundle. [`okfm-mesh/`](../../../.okfm/mesh/index.md) is that half, running, with six members.

# The half that has not

An agent interface on a bundle, cross-bundle routing from the registry to member agents, an
addressed feedback inbox and outbox, and the agent as the access-control point.

# Why co-located bundles cannot prove it

Six directories under one steward resolve in-process. That is explicitly permitted — the
specification's own advice is not to make bundles converse through chat completions for
theatre — but it means the local mesh proves **addressing** and nothing about **negotiation**.

What is missing is a bundle that can refuse. Access control, transport failure, version skew,
and a pin that breaks because another owner deprecated your target are all invisible when
every member is a folder you control.

# A remote member is what closes it

One hosted bundle: lives somewhere else, is reached through its own agent, is pinned by
commit, and decides for itself what to share. That single addition turns six directories into
a mesh with a real network boundary, and it exercises `okf://` resolution, pinning, and the
access-control property against something with the ability to say no.

# Why it is scheduled last

It is the least-evidenced part of the design — nothing in the surrounding ecosystem covers
federation of knowledge bundles, so there is no prior art to borrow and every mistake will be
made here first. Unproven work standing between the project and its measurable payoff belongs
after that payoff, not before it.
