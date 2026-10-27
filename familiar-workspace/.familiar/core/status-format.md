# status-format — Project Memory Format & Update Rules

> Defines the format and the update discipline for the memory files, all under
> `5-System/`. Memory is the source of truth (see `state-schema.md`).
> **Config** = how familiar runs this project, **context** = stable facts, **snapshot** = current
> state, **log** = history.

## Sections — use when

**Read the section you were pointed at. Do not read this file end to end to file one update.**

| Section | Use when |
|---|---|
| The memory files | You need the file map — what each memory file holds, when it changes, when it loads. |
| Read order & update protocol | Starting a session, or deciding what to read before answering. |
| Update rules (non-negotiable) | Writing any memory update — the snapshot ceiling lives here. |
| Tracks | Tagging state to a parallel line of work, or reading a track table. Lifecycle changes belong to `/system-settings` → Tracks. |
| Reading history without loading it | You need past context — the two-stage scan for `status-log.md` and `Decisions/`. |
| What to log | Deciding whether something is worth a log entry at all. |
| Decision records | A decision met the three-part gate and needs its own file. |
| Handoffs / Save Progress | Cross-referencing how those two surfaces relate to memory; the formats themselves are `handoff-format.md` and the `save` skill. |
| Template — `Memory/status-snapshot.md` | Writing or re-cutting a snapshot. |
| Template — `Memory/status-log.md` | Writing a log entry. |

## The memory files

| File | Holds | Changes | Loaded |
|------|-------|---------|--------|
| `project-config.md` | How familiar runs this project (extensions, language, tracks) | Rarely | Setup, status, or maintenance routes |
| `project-context.md` | Stable facts set at check-in | Rarely | When background is needed |
| `Memory/status-snapshot.md` | Current state, and the map of current work and files | Every material state update | Status, continuation, memory, or contradiction-sensitive routes — ceiling 60 lines of at most 250 characters |
| `Memory/status-log.md` | Dated history, append-only | Add entries only | Only when history is needed |
| `Decisions/<slug>.md` | Reasoning behind a gated decision | New file; updated if revisited | Only when a decision is questioned |
| `Handoffs/<date>_<slug>.md` | In-flight work across a session break | New file per thread | **Never spontaneously** — only via `handoff` |
| `Memory/save-progress.md` | What the user is coming back to, per track | Overwritten in place | Only via `ongoing-work`, and only if it exists |
| `4-Trackers/tasks.md` | Open items and actions, each declaring what it is `Blocked by` | Every time an item opens, moves, or closes | When the snapshot's summary is not enough — and by `triage` |
| `4-Trackers/timeline.md` | Milestones and dates | Whenever a date moves (`calendar-rules.md`) | When dates are in question |

## Read order & update protocol

**When the selected route requires current project state, read in this order** (skip files that don't exist yet):
1. `5-System/project-config.md`
2. `5-System/project-context.md`
3. `5-System/Memory/status-snapshot.md`
4. recent entries in `5-System/Memory/status-log.md` — **headlines first**, per
   "Reading history without loading it" below; never the whole file.

If `project-config.md` does not exist, report that setup is incomplete and suggest running `checkin`,
which establishes it on its first real run.

**Update trigger.** Whenever information changes, when the user says "update memory," or at a
check-in: refresh `status-snapshot.md` in place, append a dated entry to `status-log.md` when the
change is material (see "What to log"; never overwrite history), and propagate per
`calendar-rules.md`. Detailed open items / actions
live in `4-Trackers/tasks.md` (a markdown checklist; each open item declares what it is `Blocked by`);
the snapshot summarizes them. Milestones and dates live in `4-Trackers/timeline.md`.

## Reading history without loading it

`status-log.md` is append-only and never shrinks; `Decisions/` grows a file at a time. Loading
either whole is how a long-running project starts spending most of a turn on history it did not
need — and burying the relevant entry in the middle of a large read is how it gets missed anyway.

**Both are already structured for a two-stage read. Use it — never open the file first.**

1. **Abstract.** Scan headlines only.
   - Log: `grep "^## \[" status-log.md` returns one line per entry — date, type, headline, and the
     track code where tracks are declared. Narrow with the type or track before going further
     (`grep "^## \[.*\] decision |"`, `grep "^## \[.*\] model |"`).
   - Decisions: list `Decisions/`, then read the first five lines of each candidate — title, date,
     track, status, and the one-line `**Summary:**`. That is the whole abstract.
2. **Open only what the abstract selected.** Read those entries or those records, not the file.

If the abstract genuinely does not narrow it — a broad "what happened on this project" — say that,
read the most recent entries, and tell the user what window you covered. That is honest; a silent
full-file read that answers from the middle of it is not.

**No separate index file.** The headline prefix and the record header *are* the index; a second file
listing them would be one more thing to keep in sync and would drift the first time an entry was
appended without it.

## Update rules (non-negotiable)

1. When anything changes: **update the snapshot in place**, **append a log entry when the change is
   material** ("What to log" below), and propagate to `4-Trackers/timeline.md` and the calendar
   where relevant (`calendar-rules.md`).
2. **Never overwrite or delete log entries.** The log is append-only.
3. Keep the snapshot **lean** — status and continuation routes load it frequently. Detail and history belong in the
   log, not the snapshot. **Ceiling: one line per bullet, 60 lines total, and no line over 250
   characters** — a run-on bullet beats the line count without making the file any shorter, and
   `project_check.py` reports both. A bullet that needs a second line is a log entry, not a
   snapshot bullet. When the ceiling is reached, move the oldest
   detail to the log and tell the user. A snapshot that grows into a second log costs every turn.
4. If a *stable fact* changes (rare — e.g. a scope change), update `project-context.md` and log
   the change.
5. Status indicator (use consistently in the snapshot and the health tracker):
   **On track / At risk / Off track / Unknown**, always with the date the user last confirmed it
   (`state-schema.md` → Template — `Memory/status-snapshot.md` (current, keep small)). Never raise a status to On track
   without the user's confirmation; health and freshness are separate facts.

## Tracks — parallel lines of work in one project

A **track** is a parallel line of work inside one project: the financial model, the market
scan, the report. Every state surface carries a track tag and can be filtered by it, and
tracks are optional — a project with no `## Tracks` table in `project-config.md` writes no tags
anywhere. Full concept, the naming authority, where each tag goes, and the discover/reshape
lifecycle: `/system-settings` → Tracks → Format and tagging discipline. That branch owns this content; this
file only needs the one non-negotiable a memory write must hold: **never mint a track code while
filing a routine update** — tag with an existing code, `shared`, or escalate to the user per that
section, then let `/system-settings` → Tracks write any new code.

## What to log (essential only — avoid bloat)

Log a `status-log.md` entry only for **material** events. The log should let someone reconstruct
how the project evolved — not transcribe the conversation.

- **Log:** decisions; scope/deliverable changes; deadline or milestone changes; new, changed, or
  resolved risks/issues; phase changes and major progress; meeting outcomes (one or two lines).
- **Don't log:** routine Q&A, minor wording tweaks, restating unchanged status, or every small
  action.

One concise entry per material event. The snapshot holds current state; the log holds the
meaningful deltas; `tasks.md` holds the open items.

## Decision records

The log records **that** a decision was made. A decision record holds **why** — the alternatives,
what was weighed, what would have to change to revisit it. That reasoning is what cannot be
reconstructed at an audit, a renegotiation, or a handover.

**The gate — write one only when all three hold:**

1. **Hard to reverse** — changing course later carries real cost.
2. **Surprising without context** — a reader months from now asks "why did they do it that way?"
3. **A genuine trade-off** — real alternatives existed and one was chosen for stated reasons.

Miss any one and the log line is enough. Offer the record; do not write it unasked. Expect three to
eight on a full submission — the gate is what stops this becoming paperwork.

Write to `5-System/Decisions/<short-slug>.md` and **link it from the `status-log.md`
entry** for the same decision, so the log stays the timeline and the record holds the reasoning.
Update a record in place if the decision is revisited; never delete one (`CORE-NO-DELETE`).

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Decision — <short title>

**Date:** YYYY-MM-DD
**Track:** <code from `project-config.md`, or `shared`. Omit the line if no tracks are declared.>
**Status:** active | revisited YYYY-MM-DD | superseded by <link>
**Decided by:** <who actually made the call — user, decision owner, review group>
**Summary:** <one line: what was decided. This is the abstract a reader sees when scanning
`Decisions/` without opening the records — see "Reading history without loading it". Make it say
what was chosen, not what the topic was.>

## Context
<the situation forcing a choice, and any hard constraint — a deadline, a data gap, a guideline
requirement. Cite the source section where one applies.>

## Options considered
<each real alternative and why it was or was not taken. An option list of one means this did not
meet the gate.>

## Decision
<what was chosen.>

## Consequences
<what this commits the project to, and what it forecloses.>

## What would reopen this
<the specific change — new data, an agency question, a scope change — that would make this worth
revisiting. This is what makes the record useful later rather than merely historical.>
```

## Handoffs

In-flight work carried across a session break, written and read **only** via `handoff` — the
user typing it, or familiar invoking it after the user confirms a turn-expensive-entry-point offer. Never
loaded before routing: several threads may be open, so a recent handoff is not automatically relevant.
Full rules: `handoff-format.md`.

## Save Progress

`Memory/save-progress.md` holds **intent** — what the user is coming back to — the one thing not
derivable from the other files. Written and overwritten **only** via `/save progress`, fired
at a break boundary rather than a clock or a session limit, and read back **only** via
`ongoing-work`. Not loaded before routing and never logged: it is disposable, not
history. **Non-authoritative** — where it conflicts with `status-snapshot.md`, the snapshot wins.

**Parallel sessions on separate tracks each fire their own `/save progress` at their own break
boundary.** Each run reads the file before writing it, keeps every other track's line unchanged, and
replaces only its own track's line. A run that skips the read and writes fresh erases intent a
sibling session already filed for a track it never saw.

---

## Templates

Every template for the surfaces this file governs — `status-snapshot.md`, `status-log.md`,
`save-progress.md`, plus `project-config.md` and `project-context.md` — lives in one place:
`state-schema.md` → Templates. This file states the rules; that file states the shape.

## Beyond these files — other memory surfaces

The files above hold project **state**. Two other surfaces hold different things; keep them
distinct:

- **`3-Knowledge/`** — compiled **knowledge** from the project's own sources
  (by-source synthesis pages + `_knowledge-index.md`), maintained by `ingest.md`. Updated in
  place; consulted on a relevant query or ingest, not loaded every interaction.
- **`5-System/user-preferences.md`** — behavioural preferences for this project.

**Capture routing.** When the user says "add this to memory" outside a check-in, route by type
and confirm where it landed — full routing table in `/save to-memory`.
