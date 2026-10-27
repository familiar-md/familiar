# This project's workspace

The walled-off area for this project — familiar reads and writes only inside this folder, in both
directions. Launch your assistant inside this folder; nothing outside it is in scope unless you
place a file in `1-Inputs/` or name it explicitly for a task. Subfolders:

- `1-Inputs/` — what the user supplies: `Sources/` (reports, studies, evidence to ingest),
  `Admin/` (scope, timelines, correspondence), `Templates/` (project-specific blanks). Read-only
  raw inputs; familiar never edits them.
- `3-Knowledge/` — compiled, cited understanding familiar builds from those sources,
  plus `_extract-<stable-source-ID>.md` files (full text cache, consulted only when needed).
- `2-Drafts/` — deliverable drafts; the user copies finished work out into their own folders.
- `4-Trackers/` — living tools: `timeline.md` (milestones, dates) and `tasks.md` (open items with
  blockers); the user may add others.
- `5-System/` — config, context, and `Memory/` (snapshot + log); `user-preferences.md`.

Flow: Inputs -> familiar reads/ingests -> writes Knowledge + Drafts ->
user moves finished drafts out. Trackers is the live task list; System is internal state.

Each subfolder has its own `_about.md`. Installed system rules: `.familiar/core/` at the project root.
