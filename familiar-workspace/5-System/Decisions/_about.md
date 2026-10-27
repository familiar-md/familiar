# Decisions

Decision **records** — the reasoning behind a decision, not the fact of it. `Memory/status-log.md`
already records that a decision was made and when. This folder holds why: what the alternatives
were, what was weighed, and what would have to change to revisit it.

That reasoning is what nobody can reconstruct later. At a client review, an audit, a
renegotiation, or a handover to another user, "we chose vendor X" is not enough — you need to
know whether it was clinician advice, data availability, or a stakeholder instruction, because the answer
changes how you defend it.

## Most decisions do not get one

A record is written only when **all three** are true:

1. **Hard to reverse** — changing course later carries real cost.
2. **Surprising without context** — a reader months from now would ask "why did they do it that way?"
3. **A genuine trade-off** — there were real alternatives and one was chosen for stated reasons.

Miss any one and the `status-log.md` line is sufficient. Expect roughly three to eight records on a
full submission, not one per meeting. The gate is what keeps this from becoming paperwork.

Every record is linked from its `status-log.md` entry, so the log stays the timeline and this stays
the reasoning. Records are updated in place if a decision is later revisited — never deleted
(`CORE-NO-DELETE`).

Format and the close-out reconciliation: `.familiar/core/status-format.md` → Decision records.
