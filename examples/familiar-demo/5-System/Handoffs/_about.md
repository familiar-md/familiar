# Handoffs

Handoffs carry genuinely in-flight work across a focused-session boundary. They are not project
state: durable dates, decisions, risks, actions, and current status belong in their authoritative
surfaces first.

Handoffs are inspected only after a status, continuation, or handoff route is selected. List open
files by `Covers:` and let the user choose; the newest file is not necessarily relevant.

## One file per thread

Use `YYYY-MM-DD_<short-slug>.md` and the template in `handoff-format.md`. Each file carries revision
metadata, a plain-language `Covers:` line, optional track, status, last completed point, next concrete
step, decisions already filed elsewhere, open questions, and artifact paths.

Never delete a handoff (`CORE-NO-DELETE`). With user confirmation, change status to `resumed`,
`closed`, or `superseded`. Current project state wins over an older handoff; stop on a contradiction
and ask the user to reconcile it.
