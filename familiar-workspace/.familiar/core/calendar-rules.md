# calendar-rules — Deadlines & the user's Calendar

> How familiar keeps deadlines consistent across the project and reflected on the user's calendar.
> The **timeline (`4-Trackers/timeline.md`) plus memory is the single source of truth**; the calendar is a
> *rendering* of it, never an independent source. Rules and update discipline: `bootstrap.md`,
> `status-format.md`.

## The user's calendar

familiar has no calendar capability and never claims to have written one — there is no calendar
capability declared in `installed.json` and no calendar automation anywhere in this system. The
user's calendar is external to the workspace: familiar tells the user what belongs on it and leaves
the writing to them.

- **Milestones**, **hard deadlines**, **internal meetings**, **external stakeholder meetings**, and
  **review reminders** (e.g. "draft due before Thursday's stakeholder meeting") belong on it.
- familiar derives *what* should be on the calendar from the timeline and the meeting cadence in
  `project-context.md`, and states it to the user in plain language. The user puts it on their own
  calendar; familiar never writes to it.

## When a deadline changes (propagation order)

A date change must flow to **all** of these, in order:
1. **`4-Trackers/timeline.md`** — the milestone row, and every milestone downstream of it via its
   `Depends on` chain. A slipped date rarely moves only one row, but a `hard external` date does
   not move because a predecessor slipped: report the lost slack and ask what gives. Then run
   `python .familiar/scripts/timeline_views.py`. Its dependency section lists what the change put
   at risk, and it regenerates `4-Trackers/_views/`.
2. **`status-snapshot.md`** (next milestone / open items).
3. **`status-log.md`** — append an entry noting the old date, new date, reason, and that it was
   propagated.
4. **Tell the user** which calendar events are now stale and what to change them to.
Never change a date in one place only.

## Recurring check

- During the recurring check-in (`check-in.md`), confirm whether any dates moved. If yes,
  run the propagation above. If no, tell the user the calendar should still match the timeline —
  familiar cannot read their calendar to confirm it.

## Guardrails

- Never claim to have created, moved, or deleted a calendar event — familiar has no calendar surface.
- If something is cancelled, mark it and log it in the timeline, per the no-delete rule, and tell the
  user to reflect the cancellation on their own calendar.
