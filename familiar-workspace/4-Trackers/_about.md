# Trackers

Living tools familiar maintains and the user uses regularly. These stay here — they are not drafts to be
pulled out.

**Ships with the template, and familiar keeps both current:**

- `timeline.md` — milestones and hard dates. With memory, the source of truth for dates.
- `tasks.md` — the detailed open-item checklist, with blocked-by edges.
- `meetings.md` — planned internal and client meetings (series rules, one-offs, moves and cancellations). Optional; a project without it is valid.

**Generated, never edited:** `_views/next-two-weeks.md` and `_views/gantt.md` are rendered from
`timeline.md` by `.familiar/scripts/timeline_views.py`, stamped with the timeline revision they came
from. `_views/meetings-next-weeks.md` is rendered from `meetings.md` by
`.familiar/scripts/meetings_view.py` the same way. Change dates in `timeline.md` and regenerate; an edit made in a view is lost on the next run.

**The user may add** a project health tracker, accrual calculator, or roles & responsibilities
matrix. familiar will read and update anything it finds here, but only the two files above are
assumed to exist. Keep no second schedule here: a hand-kept gantt drifts from `timeline.md`.
