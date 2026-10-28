# familiar-demo — a worked example

This is what a familiar project looks like after a few weeks of real use. It is a **fictional**
engagement (Northgate, a regional logistics consolidation) with fictional people, numbers, and
documents, kept here so you can read populated state instead of empty templates.

Download it as `familiar-demo-<version>.zip` from the Releases page of the familiar repository on
GitHub: unzipped, it is a complete project
you can open your AI assistant in. Ask "where are we?" or run the check-in to see familiar answer from
a project with history. Its dates are from August and September 2026, so expect it to report overdue
work. Keep it separate from your real projects, and start your own from `familiar-workspace`.

In this repository the folder holds only the project content; the release adds familiar's own files
(`.familiar/`, the skill folders and the entry files) when it builds the zip.

## What to look at

- `5-System/project-config.md` and `project-context.md` — the two files intake writes once, and the
  difference between settings and durable facts.
- `5-System/Memory/status-snapshot.md` and `status-log.md` — the snapshot is replaced in place and
  says where the project stands now; the log only ever appends.
- `4-Trackers/tasks.md` — every open item declares what it is `Blocked by`, which is what lets a
  check-in report the three things actually startable today rather than a flat list of eleven.
- `3-Knowledge/` — one page per source, each carrying `last_verified`, `review_by`, and `volatility`,
  and `_knowledge-index.md` cataloguing them so a session finds the right page without opening all
  of them.
- `5-System/Decisions/` and `5-System/Handoffs/` — a decision record with its rationale and
  consequences, and a handoff written to survive a session break.
- `2-Drafts/_draft-index.md` — which deliverable version is current and what superseded what.

## The layout

The project folder *is* the workspace. familiar reads and writes inside it, in both directions, and
nothing outside it is in scope unless you put a file in `1-Inputs/` or name it for a task
(`CORE-WORKSPACE-SILO`). Source material comes in through `1-Inputs/`; finished work leaves when you
copy a draft out of `2-Drafts/` yourself.

The `.familiar-project` marker is what scopes familiar to this folder. Without it familiar stays
inert, which is how you choose which folders it runs in. It ships already in place, with `created`
stamped for real the first time `checkin` runs in a project, and it records the version the project
was set up at.

Every folder here has its own `_about.md` explaining what belongs in it.
