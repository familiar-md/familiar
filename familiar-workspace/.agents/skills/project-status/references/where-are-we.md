# `/project-status` → Where are we

> Branch of the `project-status` router. Reached only from `/project-status`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

A **stateless query**: the return leg of `save`, and clock-independent by design:
answerable at 9am, mid-afternoon after an interruption, or on a project untouched for a fortnight.

## Context contract

- **Required context:** `5-System/Memory/status-snapshot.md`
- **Conditional context:** `5-System/Memory/save-progress.md` only when it exists and the user is resuming interrupted work, plus status-log headlines then the needed newest entry to check its freshness; `4-Trackers/tasks.md` only when the snapshot does not identify the next actionable item; `4-Trackers/timeline.md` only when timing or milestones are requested or contradictory; the `Covers:` and `Status:` lines of `open` and `resumed` `5-System/Handoffs/` only when the user asks to resume or hand off work, or asks where things stand; `2-Drafts/_draft-index.md` only when the snapshot has no Current work lines.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** `nothing`. This skill is a read of current state and writes no file, ever
- **Capabilities:** file-read. Optional capabilities must degrade as the procedure states.
- **Completion:** The reply identifies active work, blockers, and the next useful route from current state without changing any file.


## Procedure

1. **Read only — write nothing.** Start with `5-System/Memory/status-snapshot.md`.
2. **Open conditional context only as needed**, per the context contract above: `4-Trackers/tasks.md`
   (the **frontier** — items with no open blocker; `python .familiar/scripts/task_frontier.py` lists it,
   or apply the rule by reading the file if it cannot run) when the snapshot does not already name the next
   actionable item; `4-Trackers/timeline.md` (next milestones, anything `at risk`) when timing or
   milestones are requested or contradict the snapshot; the `Covers:` and `Status:` lines of `open` and
   `resumed` handoffs when the user asks to resume or hand off work, or asks where things stand; `5-System/Memory/save-progress.md` when it exists and the user is
   resuming interrupted work, followed by status-log headlines and only the newest entry needed for
   the freshness comparison.
3. **Lead with status and how fresh it is:** the snapshot's `Status` with its `confirmed` date. If
   that date is missing or more than 14 days old, call the status unconfirmed rather than repeating
   it. For a project whose `Lifecycle` is not `active`, say so first.
   **Then report per track** where `5-System/project-config.md` declares them, otherwise flat: current phase,
   the snapshot's **Current work** lines (each piece of work named in plain words, with a link to its
   current file and its next step), and whichever of frontier tasks, next milestone(s), open handoffs,
   or the `5-System/Memory/save-progress.md` carry line you opened above. When the user asks where things
   stand, that map is the answer: lead with it, keep it short, and never answer with a list of IDs or
   version labels (`CORE-PLAIN-NAMES`). If the snapshot has no Current work lines, say so and name the
   files the draft index lists as current instead.
   **Name stale threads.** An `open` or `resumed` handoff whose date is more than 7 days old is
   probably finished or replaced. List those by `Covers:` line and say the user can close them with
   `/handoff`; never close one from here.
4. **If `5-System/Memory/save-progress.md` is older than the newest `5-System/Memory/status-log.md` entry**, say so — it may describe
   intent that has since been overtaken. State wins; `5-System/Memory/save-progress.md` never overrides it.
5. **If no memory exists yet**, say so plainly and suggest `/project-status` → Check-in, which establishes a
   fresh project on its first run, rather than guessing at project state. "No memory" is a claim
   about the file, so make it only after reading `5-System/Memory/status-snapshot.md` at that exact
   path, relative to the `.familiar-project` marker, and finding it absent or still the unwritten
   template. A read that failed, was blocked, or used any other path is a retrieval gap under
   `CORE-GROUND`: report it as a gap, never as an empty project.

## Guardrails

- Never lints, never edits, never files anything — that is Check-in's and `save`'s job.
- Never invents a status for a track or item state does not cover; report the gap instead.
