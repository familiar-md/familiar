# `/save progress` → Save progress

> Branch of the `save` router. Reached only from `/save progress`; the user
> starts it, never a route match. Load this file after the branch is selected, then follow the
> context contract below and load nothing from the other branch.

Fires at a **break boundary, not a clock boundary** — it can run several times in one day. It does
not produce a new state surface; it reconciles the ones that already exist.

## Context contract

- **Required context:** `.familiar/core/file-handling.md` → Integrity and delivery, `.familiar/core/status-format.md` → Save Progress, `5-System/Memory/status-snapshot.md`, `5-System/Memory/status-log.md` headlines, `4-Trackers/tasks.md` + `timeline.md`, `5-System/Handoffs/`
- **Conditional context:** `.familiar/core/voice.md` and `.familiar/core/plain-language.md` only when step 2 files a durable insight as a knowledge page.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** `5-System/Memory/save-progress.md` (overwritten in place, never appended, never logged); the
  snapshot's **Current work** lines, when step 2 finds them out of date; plus, only for
  items step 2 actually routes: `5-System/Memory/status-snapshot.md` + an appended `5-System/Memory/status-log.md` entry
  (decision/date), `4-Trackers/tasks.md` (action), a `3-Knowledge/` page (insight), or
  `5-System/user-preferences.md` (preference) — the To memory branch's own routing table decides which.
  **No new state file beyond these.**
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** Current state, tasks, and per-track loose ends are reconciled in their existing authoritative files, with no invented action or new state surface.


## Procedure

1. **Read current state** across every track (or the flat project, if none declared):
   `5-System/Memory/status-snapshot.md`, recent `5-System/Memory/status-log.md` entries (**headlines first** —
   `status-format.md` → Reading history without loading it — then open only what you selected),
   `4-Trackers/tasks.md`,
   `4-Trackers/timeline.md`, open `5-System/Handoffs/`.
2. **File anything loose.** Route each unfiled item this session produced using the
   `/save to-memory` table — decision/date → snapshot + log, action → `tasks.md`,
   insight → a knowledge page, preference → `5-System/user-preferences.md`. Apply the same **material-event
   test**: most firings append nothing to `5-System/Memory/status-log.md`.
   **Then refresh the map.** Check the snapshot's **Current work** lines against this session: a piece
   of work started, a new current file, a changed next step, or a piece finished. Fix those lines in
   place, in plain words with the file's path (`state-schema.md` → Template — `Memory/status-snapshot.md` (current, keep small)).
   This is a state update, not a log entry.
3. **Capture intent — the one thing state does not hold.** Ask, or infer from the conversation,
   what the user is coming back to. One line per track plus a carry line for anything cross-cutting.
4. **Read `5-System/Memory/save-progress.md` before writing it.** Keep any other track's existing line
   as-is and replace only this session's track line (`status-format.md` → Save Progress). Never
   appended, never logged.
5. **If something is genuinely mid-flight** — a draft stopped mid-edit, no clean state to file it
   under — do not write a handoff yourself. Tell the user to run **`/handoff`** → Session
   handoff; it is the branch that owns that file.

## Guardrails

- **Never lint, never re-interview.** Those belong to `checkin`; running them here turns every
  break into ceremony.
- **`5-System/Memory/save-progress.md` is derived and disposable, not authoritative.** If it ever contradicts
  `5-System/Memory/status-snapshot.md`, the snapshot wins.
- **This skill sees only its own session.** Three tracks worked in three parallel sessions need
  three separate `/save progress` runs — one per session, each merging into the shared file per
  step 4. Running it in only one session leaves the other tracks' progress unfiled.
- **Task provenance.** A user-stated action gets filed per the To memory branch's precedent. A model-inferred
  action is only **offered**, never written — an inferred task with no stated blocker would enter
  the frontier looking workable when it may not be.
- Apply `bootstrap.md`, `file-handling.md`, and `status-format.md` to state written here.
