# familiar project state schema

This file defines the authoritative state surfaces for schema version `1.0`. A generated report is a view, not another source of truth.

Every path in the table below is relative to the workspace root, which is the working directory a
session launches in. A resolved short label (`bootstrap.md`'s "Route selection") still needs this
table's hop from label to path before it is a real path on disk.

| Surface | Authoritative contents | Update behavior |
|---|---|---|
| `5-System/project-config.md` | Stable settings, workspace path, schema version, installed extensions, and capability record | In place; explicit setup or maintenance only |
| `5-System/project-context.md` | Background, objectives, stakeholders, and durable constraints | In place; material durable changes only |
| `5-System/Memory/status-snapshot.md` | Current phase, blockers, immediate next actions, and latest revision | Atomic in-place replacement |
| `5-System/Memory/status-log.md` | Meaningful chronological events | Append only |
| `3-Knowledge/_source-register.md` | Every input file version, its roles, and what ingest did with it | In place, by `source_register.py record` during ingest |
| `4-Trackers/tasks.md` | Action, owner, status, due information, and blockers | In place by task routes |
| `4-Trackers/timeline.md` | Milestones and dates | In place when a date moves |
| `4-Trackers/meetings.md` | Planned internal and client meetings: series rules, one-offs, per-date moves and cancellations | In place; rows are never deleted |
| `5-System/Decisions/*.md` | Approved decision, rationale, date, and consequences | New record; later amendments retain history |
| `5-System/Handoffs/*.md` | Temporary in-flight instructions for the next focused session | New record; status may change in place |
| `5-System/_update-backups/<old>-to-<new>_<date>/` | Copies of the release files `update.py` replaced in one update, for rollback | Written only by `update.py --apply`; never edited |
| `5-System/user-preferences.md` | Project-specific statement of how the user wants familiar to work here, this project's familiar signature, and the referencing method | In place; the signature by `/system-settings` → Preferences on the user's yes, or by the first `/project-status` → Check-in when the user gives one (the default signature, shown by a project with none of its own, is in `~/.familiar/user-preferences.md`), the referencing method once on the first Word draft that cites (`docx-rules.md` → Editor notes → Referencing method), then explicit feedback via `/save to-memory` only |
| `5-System/notes.md` | Loose notes that fit no other surface | Append or in place, via `/save to-memory` |

## Tracker conventions

**`4-Trackers/timeline.md`:**
- Columns: `| ID | Milestone | Track | Due | Confirmed | Type | Status | Depends on | Owner |`.
  `Track` holds a code from `project-config.md`, or `shared`; leave it blank when the project
  declares no tracks.
- `ID` — `M-01`, `M-02`, … Assigned once and never reused, so other rows, tasks, and views can
  point at a milestone even after it is renamed.
- `Due` — a full date `YYYY-MM-DD`, a window `YYYY-MM-DD to YYYY-MM-DD` (the second date is the
  deadline), or `No date: <reason>`. Nothing else: a month, a relative phrase ("2 weeks after
  M-04"), or a start date is not a deadline. Put a relative deadline in `Depends on` with its own
  best current date, and a recurring meeting's cadence in `meetings.md`, not here.
- `Confirmed` — the date the date was agreed with whoever controls it, or `tentative`.
- `Type` — `deliverable` (promised output) · `internal` (project gate) · `hard external` (a date the
  project does not control) · `client meeting` (one dated meeting with the client) · `internal meeting`
  (one dated team meeting). A recurring meeting's cadence lives in `4-Trackers/meetings.md`; give a
  timeline row only to a meeting that is itself a milestone (the evidence presentation, not the weekly check-in).
- `Status` — `not started` · `in progress` · `on track` · `at risk` · `slipped` · `done` ·
  `not applicable`.
- `Depends on` — milestone IDs, comma-separated, or `—`.
- **Views are generated, never edited.** `.familiar/scripts/timeline_views.py` renders
  `4-Trackers/_views/next-two-weeks.md` and `4-Trackers/_views/gantt.md` from this file, stamped
  with its revision, and lists dependency problems without moving any date. Regenerate after every
  change to this file; `project_check.py` flags a view whose stamp is behind.
- Every dated deliverable in `project-context.md` needs a matching row; a deliverable with no
  milestone is a gap the check-in lint should catch.
- This file shows the current plan only — do not keep superseded rows. Date history (old date, new
  date, reason) lives in `status-log.md`.
- A hand-kept gantt or granular schedule beside this file drifts (2026-09-23 audit). Replace it with
  the generated view, or mark it superseded; never maintain a second editable plan.

**`4-Trackers/meetings.md`** (optional; a project without it is valid):
- Two tables under `## Series` and `## One-offs and exceptions`. Planned meetings, not minutes and not
  a calendar: update your own calendar to match.
- Series columns: `| ID | Meeting | Kind | Rule | Time | Start | End | Attendees | Milestone | Status |`.
  `ID` is `S-01`, `S-02`, … assigned once and never reused. `Kind` is `internal` or `client`. `Rule` is
  `weekly:<day>` or `every-2-weeks:<day>` (`mon` … `sun`); the first occurrence is the first named day on
  or after `Start` and a bi-weekly series counts from it. `Time` is local `HH:MM-HH:MM` (no timezone).
  `End` is inclusive, or `—`. `Attendees` are comma-separated, or semicolon-separated when a name
  contains a comma. `Milestone` is a timeline ID or `—`. `Status` is `active`, `paused` (no
  occurrences) or `ended` (the `End` date governs).
- One-off and exception columns: `| ID | Meeting | Kind | Date | Time | Attendees | Milestone | Series | Replaces | Status | Note |`.
  `ID` is `X-01`, … A one-off has `Series` `—`, `Status` `planned`, `done` or `cancelled`, and every other
  column filled. An exception names its `Series`, inherits blank columns from it, and has `Status`
  `moved` (`Replaces` is the original date; `Date`/`Time` are the new ones), `cancelled` (`Replaces` only)
  or `extra` (an added `Date`). A date moved or cancelled must be one of the series' occurrences.
- Never delete a row. A series ends with `End` or `Status`; an occurrence is `cancelled`.
- `## Agendas` (optional, after the tables): one `### <ID> <YYYY-MM-DD>` heading per meeting date, named by the
  series ID (or the one-off's own ID) and the date as it now stands, with `- topic` bullets or one
  `None needed: <reason>` line. `### <S-ID> standing` is a series' standing list, used by any of its dates
  without one of its own. Set with `tracker_edit.py meeting agenda`, which carries a dated agenda to the
  new date when a meeting moves; a replaced list is kept in the status log. Past agendas stay.
- **The view is generated, never edited.** `.familiar/scripts/meetings_view.py` expands the rules and
  exceptions into dated occurrences (`4-Trackers/_views/meetings-next-weeks.md`, stamped with this
  file's revision; `--json` for other tools) and lists what it cannot read. `project_check.py` flags a
  stale stamp, an unreadable row, and a milestone ID that is not in the timeline.

**`4-Trackers/tasks.md`:**
- Every open task carries `Owner: <person>` and exactly one of `Due: YYYY-MM-DD` (a commitment),
  `Follow up: YYYY-MM-DD` (waiting on someone; the date to chase), or `No date: <reason>`. Write
  dates as full ISO dates so `.familiar/scripts/project_check.py` can compare them; when only a
  month is known, write `No date: expected October 2026` rather than a partial date.
- Name a blocker by the blocking task's own ID when it is one. A blocker does not have to be a task
  itself — name it in plain words when it isn't. An external blocker still counts as a blocker; do
  not exclude a task from the frontier just because its blocker has no row of its own.

## Extension state surfaces

An extension declares its own state surfaces in `familiar-extension.json` under
`contributions.state_surfaces`, one object per surface:

| Field | Meaning |
|---|---|
| `path` | Workspace-relative path (e.g. `4-Trackers/<extension>.md`) — never a plugin-cache path. |
| `schema_version` | The extension's own version for that surface's shape, independent of this file's `1.0`. |
| `update_behavior` | Plain-text update rule, matching the style of this file's Update behavior column (e.g. "Atomic in-place replacement", "Append only"). |
| `scaffold` | Whether the extension's drop-in folder carries the file already created (with the Required metadata block below); `false` when a skill creates it on first use instead. |

An extension surface with `scaffold: true` still starts with the Required metadata block below,
stamped with the extension's own `schema_version`, not this file's.

## Templates

These are the only templates for the surfaces in the table above. `/project-status` → Check-in writes the first two
once, on its first real run in a fresh project; the rest are written and updated by the routes named
in the surface table.

### Template — `project-config.md`

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Project Config — <Project Name>

- **Setup status:** complete
- **Organization:** <organization or "not set">
- **Domain:** <working domain or "not set">
- **Extensions:** <ordered extension IDs and versions, or "none">
- **Capabilities:** see `.familiar/installed.json`
- **Language / register overrides:** <overrides or "none">
- **familiar voice:** <on/off and optional name>
- **Tracks:** <not set, or "see table">
```

The `Extensions` entry mirrors what is actually present in this host's native skill location —
presence on disk is authoritative, not a registry. Extension-owned check-in fields — written from
that extension's `checkin_fragments`, when declared — use a heading named
`## Extension — <extension-id>` and keys namespaced by that ID.

#### Tracks

Tracks are optional and created only by the tracks branch (`/system-settings` → Tracks →
Format and tagging discipline). Codes in the table are the naming authority for task, status,
event, and handoff tags.

```markdown
## Tracks

| Code | Track | Scope in one line | Status |
|---|---|---|---|
| `workstream-a` | <name> | <scope> | active |
| `shared` | — | Reserved for cross-track work | — |

_Status is active, paused, not started, or closed YYYY-MM-DD._
```

`shared` is reserved and must not be redefined.

### Template — `project-context.md`

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Project Context — <Project Name>

- **Background:** <why the project exists>
- **Objective:** <one or two sentences>
- **In scope:** <outcomes or work included>
- **Out of scope:** <explicit exclusions>
- **Stakeholders / roles:** <people or groups and their roles>
- **Constraints:** <durable time, policy, resource, or quality constraints>
- **Baseline timeline:** <start and hard milestones>
- **Standing references:** <important project-source paths>
```

An installed workflow extension may add a namespaced subsection. Core does not prescribe its fields.

### Template — `Memory/status-snapshot.md` (current, keep small)

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Status Snapshot — <Project Name>
_As of: YYYY-MM-DD_   |   **Lifecycle:** active   |   **Status: On track / At risk / Off track / Unknown** — confirmed YYYY-MM-DD

- **Current phase:** <…>
- **Current work:** one indented line per piece of work in progress:
  - <piece of work, in plain words> — current file: <path> — next: <step>
- **Next milestone(s):** <milestone — date>
- **Open items / actions:** <item — owner — due>
- **Risks / issues:** <risk — severity — mitigation>
- **Blockers:** <blocker — what's needed>
- **Recent changes (this period):** <1–3 bullets; full detail in the log>
```

- **`Lifecycle`** is `active`, `paused`, `reference`, or `closed`. Only an `active` project's
  missed dates and missing owners are raised as problems; the rest are reported as information, so
  a paused personal project does not generate overdue noise. The fleet hub does not read this value:
  it keeps lifecycle for registered projects in its own registry, and reports a snapshot that disagrees.
- **`confirmed`** is the date the user last confirmed the status at a check-in. `As of` changes on
  every write; `confirmed` changes only when the user confirms. A status not confirmed in the last
  14 days is reported as unconfirmed, whatever it says, and `Unknown` is the honest value when
  nobody has confirmed one yet.
- **`Current work`** is the project's map: the answer to "where are we, and which file is the
  latest?". One line per piece of work, named in plain words, with the path of its current file
  and its next step. When a new version becomes the current one, or a piece of work finishes,
  update its line in the same write; a finished piece leaves the list.

**If `project-config.md` declares tracks**, keep the project-level header and status line, then
repeat the bullets under one `### <Track>` heading per track, plus a `### shared` heading for
cross-cutting items. The ceiling still binds: one line per bullet, 60 lines total, no line over 250
characters.

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Status Snapshot — <Project Name>
_As of: YYYY-MM-DD_   |   **Lifecycle:** active   |   **Status: On track / At risk / Off track / Unknown** — confirmed YYYY-MM-DD

- **Current phase (project):** <…>
- **Next milestone(s):** <milestone — date — track>

### <Track name> (`<code>`) — On track / At risk / Off track
- **Current work:**
  - <piece of work> — current file: <path> — next: <step>
- **Open items / actions:** <item — owner — due>
- **Risks / blockers:** <risk or blocker — what's needed>

### shared
- **Open items / actions:** <item touching more than one track — owner — due>
```

### Template — `Memory/status-log.md` (append-only; oldest entry on top, newest appended at bottom)

> **Maintainer note — deliberate mirror.** `/save to-memory` carries a copy of
> this template and the material-event test, so that filing one note does not load this file. This
> section stays canonical; both must change together.

Append a dated entry per **material** event only (see `status-format.md`, section "What to log");
never edit or remove past entries. A consistent header prefix keeps the log greppable
(`grep "^## \[" status-log.md | tail -5`).

```markdown
# Status Log — <Project Name>

## [YYYY-MM-DD] <type> | <one-line headline>
<1–3 lines: what changed and why; old → new where relevant; what was propagated.>
(type ∈ kickoff | decision | scope | deadline | risk | meeting | ingest | progress)

## [YYYY-MM-DD] kickoff | First check-in completed
Captured context, timeline, and first snapshot from the first check-in.
```

**If `project-config.md` declares tracks**, the track code goes first in the header, so one grep
returns one track's history: `grep "^## \[.*\] model |" status-log.md`.

```markdown
## [YYYY-MM-DD] <code> | <type> | <one-line headline>
```

### Template — `Memory/save-progress.md` (overwritten in place, never logged)

```markdown
# Save Progress — <Project Name>
_As of: YYYY-MM-DD HH:MM_

- **<Track or project>:** <what the user is coming back to, one line>
- **shared:** <cross-cutting carry line, if any>
```

## Required metadata

Every living state surface starts with these comment fields:

```text
<!-- familiar-state-schema: 1.0 -->
<!-- revision: <non-negative integer; 0 is an unwritten scaffold> -->
<!-- last-updated: <ISO-8601 timestamp or date> -->
```

Before writing, a route records the revision it read. The replacement increments that revision by one. If the on-disk revision is no longer the value read, apply `CORE-STALE-WRITE`: reread, reconcile, and report the conflict. Write to a temporary sibling and atomically replace the destination where the host supports it.

The activity log is append-only and does not use replacement revisions. Each entry carries its own date and references affected task or decision IDs where applicable.

`save-progress.md`, briefings, and dashboards are derived and disposable. They never override the surfaces above.
