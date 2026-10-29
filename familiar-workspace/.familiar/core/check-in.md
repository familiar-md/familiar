# Recurring project check-in

Use this procedure only through `/project-status` → Check-in. Pre-draft from current state and ask only for
changes the project files cannot answer.

## 0. Establish a fresh project

Run this step only when `.familiar-project`'s `created` line still reads `not-yet-set` — once step 0
completes it always reads a real date, so the step cannot fire twice. Otherwise skip straight to step 1.

An unset marker alone does not prove the project is new: projects migrated from an older layout can
carry one beside a configuration someone already filled in. Before asking anything, read
`5-System/project-config.md`. It is **untouched** only while it is still the shipped stub —
`revision: 0` and the title `# Project Config — NOT YET WRITTEN`. Anything else is **populated**, and
step 3 below reconciles it instead of replacing it. Never reset a populated configuration to template
defaults.

1. Have one conversation, not a form: ask for and confirm a **Project Name** — offer the folder name
   as a reasonable default, never assume it — plus what this project is for, the next concrete
   outcome to work toward, and any known deadline. First read the configuration, the project context, and the
   status snapshot — a project can hold real work before its configuration is written — and ask
   only for what none of them already answers.
2. For each installed extension whose manifest declares `contributions.checkin_fragments`, read that
   fragment and fold its questions into the same conversation, immediately after the base questions
   in step 1. Skip an extension not present under `.claude/skills/` (or `.agents/skills/`) even if a
   stale manifest still names it.
3. Write the configuration, according to what the file was:
   - **Untouched:** replace `5-System/project-config.md` in full with `state-schema.md`'s
     `project-config.md` template: the title line (`# Project Config — <Project Name>`),
     `Setup status: complete`, `revision: 1`, `last-updated:` today's date, `Organization`/`Domain`
     from the conversation or "not set" if not raised, `Extensions` mirrored from what is actually
     present under `.claude/skills/` (or `.agents/skills/`), and every other field at its template
     default. Append each fragment's "Output — specialty-specific fields" under its own
     `## Extension — <extension-id>` heading, per `state-schema.md`. Stamp `.familiar-project`'s
     `created` line with today's date in the same pass.
   - **Populated:** edit it in place. Keep every existing value and `## Extension —` section, fill
     only fields still at a template default or "not set" from the conversation, set
     `Setup status: complete`, mirror `Extensions` from what is present on disk (report, do not
     delete, a section for an extension no longer present), increment `revision` from its current
     value (add `revision: 1` if an older layout has none), and set `last-updated:` to today. Stamp `created` with the earliest date the project's
     own records show — the oldest activity-log entry, or failing that the configuration's previous
     `last-updated` — and say which you used.
4. If this project's `5-System/user-preferences.md` has no familiar signature of its own, say once
   "This project has no signature of its own (it shows <the default, or `not set`>); run
   `/system-settings` → Preferences to give it one" and continue. Do not ask for it here. "No
   signature of its own" requires having read the file; if the read failed or was blocked, report
   that read as a retrieval gap rather than claiming none exists. Do not cite project state as already recording
   the gap unless you read it there.
5. Carry the purpose, next outcome, and any deadline from step 1 above into "2. Pre-draft the delta"
   below as this project's first pre-draft input, so the first real check-in seeds status, tasks, and
   timeline instead of opening on an empty state the user must populate unprompted.
6. Continue into the normal reconciliation pass below unchanged.

## 1. Read current state

Read project configuration, the status snapshot, open tasks, timeline milestones, open handoffs,
and the recent activity-log headlines. Open an older activity entry only to resolve a contradiction.
Do not load source documents or synthesized knowledge during a routine check-in.

## 2. Pre-draft the delta

Summarize:

- progress since the last logged material event;
- current blockers and at-risk milestones;
- frontier tasks with no open blocker (`python .familiar/scripts/task_frontier.py`; if it cannot run,
  apply `state-schema.md` → Tracker conventions by reading `tasks.md`);
- decisions or dates that appear unresolved;
- open tasks missing an owner, or missing a due date, follow-up date, or no-date reason
  (`state-schema.md` → Tracker conventions); and
- missing state required for the next milestone.

Ask the user to correct the draft and supply only new progress, decisions, actions, risks, dates, or
constraints. Never re-run first-run questions whose answers remain in project context.

## 3. Reconcile

Apply the user's confirmed changes to their authoritative surfaces:

- current phase, blockers, risks, and next actions → status snapshot; set its `Status` and
  `confirmed` date only from what the user confirmed in this check-in (lifecycle is the fleet hub's,
  not the snapshot's);
- actions, owners, status, due information, and blockers → tasks;
- milestones and dependencies → timeline, then run `python .familiar/scripts/timeline_views.py` so
  the generated views match (if it cannot run, say the views are stale);
- material events → append-only activity log;
- approved decisions with meaningful alternatives or consequences → decision records; and
- durable background or constraints → project context.

Increment each living file's revision after verifying it has not changed since read. Do not update a
derived view as though it were authoritative.

## 4. Health check

First run `python .familiar/scripts/project_check.py`. It is read-only and prints only exceptions:
- setup-marker and configuration mismatches;
- snapshot age and a log newer than the snapshot;
- open tasks with no owner or date, or past due;
- open milestones past their date;
- schedule files older than `timeline.md`;
- index gaps, byte-identical inputs, sync conflict copies, and retired `/familiar:` names.

Use its findings as evidence, and confirm any you act on. If it cannot run, say so in one line and
make the same checks by reading the files; never skip them silently.

Timeline rows in an older layout (no `ID`, or a `Due` that is not a full date, a window, or
`No date: <reason>`) are converted one row at a time, never in bulk: propose the converted row,
and write it only after the user confirms its date and dependencies (`state-schema.md` → Tracker
conventions).

Report, and fix only with approval:

- tasks referenced as blockers but missing from the task tracker;
- a due date that differs between tasks, timeline, and snapshot;
- a completed item still shown as a current blocker;
- a milestone with no owner or dependency where one is required;
- a configuration extension ID that differs from what is actually present under `.claude/skills/` (or `.agents/skills/`);
- a stale revision or last-updated marker; and
- an open handoff whose next step contradicts newer state.

## 5. Close

Return the current status, the next milestone, the frontier, and the single most useful next route.
Do not invent a priority when the user has not stated one. If nothing material changed, do not append
an empty activity-log entry.
