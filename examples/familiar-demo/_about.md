# familiar-demo — a worked example

This is what a familiar project looks like after a few weeks of real use. It is a **fictional**
engagement (a competitor research brief for Cauldron Coffee Roasters) with fictional people, numbers, and
documents, kept here so you can read populated state instead of empty templates.

Download it as `familiar-demo-<version>.zip` from the Releases page of the familiar repository on
GitHub. It unzips to a folder named `Cauldron-Roasters`, after the client, the same way you rename the
workspace for your own: a complete project you can open your AI assistant in. Run
`/ili-project-status where` (Claude Code; `$project-status where` on Codex) to see familiar answer
from a project with history. Its dates are moved when each release is built, so it was last checked in
a few days before you downloaded it. Keep it separate from your real projects, and start your own from `familiar-workspace`.

In this repository the folder holds only the project content; the release adds familiar's own files
(`.familiar/`, the skill folders and the entry files) when it builds the zip.

## What to look at

- `5-System/project-config.md` and `project-context.md` — the two files intake writes once, and the
  difference between settings and durable facts.
- `5-System/Memory/status-snapshot.md` and `status-log.md` — the snapshot is replaced in place and
  says where the project stands now; the log only ever appends.
- `4-Trackers/tasks.md` — every open item declares what it is `Blocked by`, which is what lets a
  check-in report what is actually startable today rather than a flat list.
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
stamped for real the first time `/project-status` → Check-in runs in a project, and it records the version the project
was set up at.

Every folder here has its own `_about.md` explaining what belongs in it.
