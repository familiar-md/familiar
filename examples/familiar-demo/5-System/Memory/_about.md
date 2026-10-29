# Memory

- `status-snapshot.md` — the **current** state. Small; read by status, continuation, memory, and
  contradiction-sensitive routes; updated in place with revision checks.
- `status-log.md` — **append-only** dated history; never overwritten.
- `save-progress.md` — what the user is coming back to. Disposable; overwritten by
  `/save progress`, read by `/project-status` → Where are we; never loaded at session start, never logged.

Formats and rules: `.familiar/core/status-format.md` at the project root.
