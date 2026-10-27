# `/save to-memory` → To memory

> Branch of the `save` router. Reached only from `/save to-memory`; the user
> starts it, never a route match. Load this file after the branch is selected, then follow the
> context contract below and load nothing from the other branch.

# familiar — Memory Capture & Routing

**This branch owns capture routing** — the table below is the single source of truth for it.

## Context contract

- **Required context:** `.familiar/core/file-handling.md` → Integrity and delivery, `5-System/project-config.md` for the tracks table, and the target memory surface only
- **Conditional context:** the one authoritative destination and its current revision; related state only when propagation is required; `.familiar/core/status-format.md` → Decision records only for a decision record; `.familiar/core/state-schema.md` → Templates only when creating status state from scratch; `.familiar/core/voice.md` and `.familiar/core/plain-language.md` only when filing a knowledge page or decision record.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** one of `5-System/Memory/status-log.md` + `5-System/Memory/status-snapshot.md`, `4-Trackers/tasks.md`, a
  `3-Knowledge/` page, `5-System/user-preferences.md`, `5-System/project-context.md`, `5-System/notes.md`, or
  `5-System/Decisions/` — the one the routing table picked — plus `4-Trackers/timeline.md`, but only when the
  fact being filed is a date change requiring propagation
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** The confirmed fact is written once to its authoritative surface, required propagation is reconciled, and the user is told exactly where it landed.


**Do not load `status-format.md` or `state-schema.md` to file a routine note.** Everything the
common path needs is inline below. Load `status-format.md` only to write a **decision record**
(→ Decision records); load `state-schema.md` only to create a `5-System/Memory/status-snapshot.md` /
`5-System/Memory/status-log.md` **from scratch** (→ Templates).

## Route it — pick the right surface

| What the user gave you | Goes to |
|---|---|
| Decision made, or a date change | `5-System/Memory/status-snapshot.md` **and** an appended `5-System/Memory/status-log.md` entry |
| Action item / to-do — new, edited, completed, or rescheduled | `4-Trackers/tasks.md` — for an existing task, find its row and update it in place (status, owner, due date); append only for a genuinely new task |
| Durable insight about a source | A `Knowledge` page (consider `ingest`); use `_page-template.md` and apply `file-handling.md` -> AI runtime provenance |
| Behavioural preference / feedback on how familiar should work | `5-System/user-preferences.md` |
| Stable project fact (scope, team, stakeholder) | `5-System/project-context.md` |
| A loose note that fits nowhere above | `5-System/notes.md` (create if needed) |

When you produce something analytically useful in chat — a comparison, a finding — **offer** to file
it to `Knowledge` rather than letting it disappear. Offer; do not auto-file.

If the decision meets the three-part gate in `status-format.md` → Decision records — hard to reverse, surprising
without context, a genuine trade-off — **offer** a record in `5-System/Decisions/` as well,
linked from the log entry. Offer it; do not write it unasked, and do not offer when the gate is not met.

**Then tell the user where you filed it.** Always. Silent filing is a failure.

## Append a log entry — the format

> **Maintainer note — deliberate mirror.** This block duplicates `state-schema.md` → Template — `Memory/status-log.md` (append-only; oldest entry on top, newest appended at bottom), so that filing one note does not load a larger file. `state-schema.md`
> stays canonical; both must change together. It carries the reciprocal note.

Append the newest entry at the bottom. Keep the header prefix exact; the log is grepped by it.

```markdown
## [YYYY-MM-DD] <type> | <one-line headline>
<1-3 lines: what changed and why; old -> new where relevant; what was propagated.>
```

`type` is one of: `kickoff` `decision` `scope` `deadline` `risk` `meeting` `ingest` `progress`.

**Tracks.** If `5-System/project-config.md` carries a `## Tracks` table, the track code goes first in the
header, and the same code tags the task or snapshot bullet you write:

```markdown
## [YYYY-MM-DD] <code> | <type> | <one-line headline>
```

Use only a code from that table. Never invent one, and never carry in an identifier from a source
document. Anything touching more than one track is tagged `shared`, not tagged to the track that
raised it. If the table is absent, write no tag anywhere. Full rules: `/system-settings` → Tracks → Format and tagging discipline.

**Log material events only** — decisions, scope or deliverable changes, deadline or milestone
changes, new/changed/resolved risks, phase changes, meeting outcomes. Do not log routine Q&A,
wording tweaks, or restatements of unchanged status. The log must let someone reconstruct how the
project evolved, not transcribe the conversation.

## Non-negotiables

- `5-System/Memory/status-log.md` is **append-only**. Add entries; never edit or remove past ones.
- `5-System/Memory/status-snapshot.md` is updated **in place** and must stay **small** — it is current state, not
  history. Ceiling: one line per bullet, 60 lines total. A note needing two lines is a log entry.
- Log **material** items only. Bloat defeats the purpose.
- A date change must also propagate. Do the memory and timeline sides yourself per
  `calendar-rules.md` → When a deadline changes (propagation order), then **tell the user what to put
  on their own calendar** — familiar has no calendar surface and never claims to have written one.

## Scope boundary

Behavioural feedback goes to `5-System/user-preferences.md` for **this project only**. If the user's feedback is a
**systemic** change to how familiar works, say so plainly: it needs the system maintainer to update the central
installed familiar files. **Never edit the central files yourself** (`CORE-INSTRUCTIONS-READONLY`).
