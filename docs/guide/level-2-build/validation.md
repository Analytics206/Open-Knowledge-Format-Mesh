# Three passes

**Conformance** — parseable frontmatter, a non-empty `type`, the reserved file structure.
This is official OKF v0.2, and OKFM has no opinions about it.

**Profile** — the `okfm_` prefix rule, controlled predicates, resolvable relation targets,
and no stored verdicts. A frontmatter key like `okfm_stale` or `okfm_trust` is rejected
outright: those are derived at read time by definition, and storing one is storing an opinion
that will be wrong later.

**The strip test** — remove every `okfm_` key and re-run conformance. This is the rule that
keeps OKFM a profile instead of a fork. If a bundle stops being legal OKF when the profile is
stripped, the profile has started carrying weight the format was supposed to carry.

# Reject versus warn, and why they differ

**Predicates reject.** Typed relations are what make the graph mean anything, and impact
analysis, drift propagation, and neighbour surfacing all read them as fact. An edge asserted
by a producer that guessed is worse than no edge at all.

**Types warn.** Official OKF is explicit that `type` is not centrally registered and consumers
must tolerate unknown values. Rejecting one would break conformance *and* stop an adopter
inventing the type their domain needs. The list catches typos; it does not police vocabulary.

**Reason codes warn**, for now. Core carries only the codes every domain shares, so failing on
an unknown one would reject every legitimate domain code before packs exist to declare them.

# No dependencies, on purpose

Regex and the standard library, no YAML parser. That is not minimalism for its own sake — it
is the evidence behind the zero-dependency claim. A validator that needs `pip install` makes
level 2 a level 2 with an install step, and the first thing a stranger hits is a dependency
resolution problem in a language they may not use.
