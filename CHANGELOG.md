# Changelog

All notable changes to familiar core are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org). This file covers familiar core; familiar-hub,
familiar-hooks and familiar-template were first released alongside it at `1.0.0` and are versioned on
their own from there. From `1.0.0`, a change that would break
your project's files or an extension's contract only comes with a new major version, and
`INSTALL.md` describes how to update.

Earlier pre-release history was private and is not reproduced here. Version `0.3.0` is the baseline
for this repository.

## [Unreleased]

## [1.0.0] - 2026-10-27

First public release. familiar is a project-memory and workflow layer for LLM agents: a plain folder you
rename to your project and open Claude Code, Codex or Gemini CLI inside, with project state, sources,
drafts and history kept as Markdown files beside your work, so nothing has to be explained twice. Ten
skills ship in core (`GUIDE.md`, `CHEATSHEET.md`). Released alongside it, each in its own repository:
`familiar-hub` (one view across all your projects), `familiar-hooks` (optional session titles and
guards) and `familiar-template` (a starter for writing your own extension). The changes below are
against `0.8.2`.

### Added

- `/system-settings` → Hooks: lists the optional hooks a hooks package offers (session titles, guards) and installs or removes the ones the user picks in this project's host hook file, after a preview and a yes. Core ships no hooks; the branch does nothing until that package is added to the project.
- `routes.md` → Running familiar's scripts: which Python to use (3.10 or newer, or the one in `~/.familiar/venv`),
  and offering to install a missing package, run only on the user's yes.
- `doctor.py` prints the fix commands for this operating system, including a per-user `~/.familiar/venv` where the
  system Python refuses `pip` installs (PEP 668).
- `CHEATSHEET.md`: every command on one page, for core, the fleet hub and the optional hooks.
- `routes.md` → Files outside the project: a file you name outside the project can still be read, and the
  assistant now says once that it is outside the project and nothing from it is kept.
- On Claude Code, questions to you (check-in, setup, choices) come as the host's question pop-ups, one per item
  with likely answers to pick, instead of a numbered list.

### Changed

- On Claude Code every skill's command is `/ili-<skill>` (`/ili-checkin`, `/ili-save`), so typing `/ili` lists them
  all. The bare `/checkin` form still works. Codex and Gemini are unchanged.
- "familiar" is written in lowercase throughout. The "familiar signature" preference is matched in any case, so a
  project that wrote "Familiar Signature" still works.
- `ingest` started by its command always builds the knowledge page; it no longer asks whether the source is
  worth keeping. Read mode (answer only, write nothing) is for when the assistant starts it from a question.
- The demo project carries the source register, abbreviations list and citation-count stamps a real project has.
- Every shipped script stops with a plain message on a Python older than 3.10 instead of failing with a traceback.
- `doctor.ps1` is retired: `doctor.py` is the one preflight on every OS, including Windows.
- `INSTALL.md` links the extension starter (`familiar-template`) and the fleet hub (`familiar-hub`) instead of
  saying they will be published separately.

## [0.8.2] - 2026-10-26

### Fixed

- `routes.md` → Resolution rule 1: a `/save` or `/handoff` command written anywhere in a message counts the same
  as one typed first.
- The Claude Code entry file says the host's own memory folder is not the project's record, so a request to save,
  remember or hand off project work writes inside the project.

## [0.8.1] - 2026-10-24

### Added

- `draft_save.py migrate` brings a project that kept `2-Drafts/` flat onto the folder layout: one folder per
  deliverable with two or more versions, older versions into `_superseded/`, `_versions.md` back-filled from
  the filenames and the old index rows, and the retired "keep files flat" rule dropped from the index preamble.
  `--dry-run` shows the plan, a backup of the index and the move list lands in `.familiar/backups/`, a file
  open in Office is skipped, and project files that still name a moved file are listed, not edited.
- `voice.md` → Naming the user: the user is "you" or "the user", never a role label such as "PM" that
  was guessed or copied from an imported brief.

### Changed

- `project_check.py` raises a flat multi-version `2-Drafts/` to `attention` with the migrate command, flags an
  index that still states the retired rule, and reads index rows written as markdown links.
- Deliverable slugs match filenames case-insensitively, so older mixed-case filenames join their folder.

## [0.8.0] - 2026-10-24

### Added
- `.familiar/scripts/update.py`: updates a project in place from a newer release, keeping edited
  files, project data and your own entry-file text, with a backup under `5-System/_update-backups/`.
  `INSTALL.md` → Updating describes it first, with the hand procedure as the fallback.

### Changed
- `/system-settings` → Update gives the exact updater command instead of only the hand procedure.

### Fixed
- The release's `.familiar-project` now carries the release's own version.

## [0.7.1] - 2026-10-24

### Changed
- Core text is industry-neutral. Examples across the rules, workers and templates use cross-industry
  cases, and `web-lookup` states its rules generically: defining wording quoted verbatim when the caller
  asks, one jurisdiction per lookup, sources in another language quoted in the original.
- The claims-check middle grade is now named *compiled source*. The page template's `type:` list
  offers `technical report` and `prior specialist review`.
- Comments starting `Note to ` are described as client-addressed in the Review branch; behavior is unchanged.
- The docs no longer link to the extension template repository, which is not yet public.

## [0.7.0] - 2026-10-24

### Added
- `CORE-PLAIN-NAMES`: replies name things in plain words, and show an ID, code or version label only
  beside the name it stands for.
- The status snapshot's **Current work** lines: one per piece of work, with its current file and next
  step. `/ongoing-work` answers "where are we?" from them; `/save progress` keeps them current.
- `/draft-document` → **Workbook**: plan the sheets first, build readable workbooks, and check them with
  the new `scripts/xlsx_check.py`, which names what an openpyxl round-trip would drop (newer-format
  drop-down lists, shapes, form controls, macros) and what a new version lost against its source.
- `scripts/office_render.ps1` (Windows, Office installed): opens a deck, document or workbook in the real
  Office application, read-only and under a time limit, as the final check. A deck gets slide images
  and a PDF; a document gets an open check with page, tracked-change and comment counts; a workbook is
  recalculated and its formula errors counted.
- `ingest.md` → **Check pass**: compare a page's figures with its own extract, report wrong values and
  dropped context, fix on a yes, and stamp the page `values_checked`. Every number now carries the
  context its kind needs (a rate its population, N, time frame and method; a price its currency, year
  and unit; a dose its unit and schedule), as far as the source states it.
- `index_check.py --sync` copies each page's dates into its index row.
- `/deliverable-brief`: a `Standards` line (drafting rules every draft and review pass loads) and a
  `Builds on` line (an earlier deliverable whose argument this one must carry). For a deliverable that
  argues a position, each key point records its verbatim quote and the strongest counter with its answer.
- A stranger read before a document or deck leaves the project: a reader with no project context
  lists every reference it cannot resolve, list without a consequence, and section without a conclusion.
- `project_check.py` reports a snapshot over its ceiling (now also no line over 250 characters), a
  snapshot with no Current work lines, and handoffs open or resumed for more than a week.

### Changed
- The familiar signature belongs to each project. `/system-settings` → Preferences writes it to the
  project's `5-System/user-preferences.md`, offering keys from the project's name; the global file keeps
  a default for projects without one. `checkin` points there when a project has no signature of its own.
  The fleet hub's brief reports a signature that labels more than one project, and projects with none.
- A plain-words request that names `save` or `handoff` or one of their branches ("save progress", "hand
  this off") starts it, the same as its command (`routes.md` → Resolution rules, rule 1). Every other
  user-only skill still starts only from its command.
- Writing a new handoff that carries a resumed thread forward marks the resumed one `superseded`.
- A build script that makes a deliverable version is saved beside it in `2-Drafts/<slug>/_build/`, not in
  `.scratch/`; one-off scripts run from a file with `python -X utf8`.
- Deck rules: with no template, ask whether to use the builder's plain default master; PowerPoint's render
  counts where PowerPoint is installed, and a deck that leaves the project gets a trace sidecar and claims check.
- A log entry is written only for a material change (the update rule said every change).
- `doctor.py` and `doctor.ps1` require Python 3.10, check the same four packages, and recognize Office as a renderer.

### Fixed
- The ingest skill's script paths read as `skills/ingest/scripts/…` from the project root, which does not
  exist; about half of real ingest sessions began with "can't open file". The skill now names the real folder.
- `tracked_edit.py`: a field spanning paragraphs (an EndNote bibliography) is no longer editable in its
  middle paragraphs, and `--check` sees an edit there; `occurrence` counts against the file as written,
  not after earlier edits in the same pass; a run carrying Word's page-break hint is editable; a refusal
  says what blocks the anchor.
- `draft_save.py`: `adopt` validates every input before moving anything, so a long original filename no
  longer leaves a renamed, unregistered file; `next` prints `source now at:`; `register` keeps provenance
  cells it was not given.
- `project_check.py`: v1 beside v2 in a deliverable's folder is not reported unindexed; a milestone named
  "Feedback from…" is reported overdue.
- `task_frontier.py`: a blocker list ends at the next field, so `Owner:` and `Due:` are not read as blockers.
- Example text in `task_frontier.py` and `tracker_edit.py` no longer names real organizations or people.

## [0.6.5] - 2026-10-21

### Changed
- `/handoff` → Closing one: when a session resumed a handoff and has finished its `Next concrete step`, the
  working agent asks once whether to close it and, on a yes, sets `Status: closed` itself from any skill
  instead of sending the user to `/handoff`. A handoff the session did not resume stays untouched.

## [0.6.4] - 2026-10-21

### Added
- `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` wrap their release text in `<!-- familiar:start -->` …
  `<!-- familiar:end -->`. Your own project instructions go below the end marker; updates replace only
  the block. `INSTALL.md` → Updating step 4 says to carry those lines across.
- Every built release (core and each extension) carries `.familiar/release-manifests/<owner>.json`: a
  fingerprint of each release-owned file, and of the entry files' block. It is the baseline the planned
  updater will compare a project against; nothing reads it yet.

## [0.6.3] - 2026-10-20

### Added
- `tracker_edit.py`: `milestone --title` and `task --title` rename in place (IDs never change; a blocker that
  names the old title in words is listed, not rewritten); `meeting rename`; `meeting agenda` sets a dated or
  standing topic list, or records "no agenda needed", in `4-Trackers/meetings.md` → `## Agendas`. `meeting move`
  carries a dated agenda to the new date.
- `meetings_view.py` reads agendas and shows them under each meeting. The `meetings.md` stub and the demo gain an
  `## Agendas` section.

## [0.6.2] - 2026-10-19

### Added
- `ingest.md` → Bulk ingest: when the user runs a multi-source ingest all at once and the host's
  `named-subagents` capability is `active`, one worker per source synthesizes and writes its own page
  (steps 3–5), in waves whose size the user sets, optionally pausing between waves. The main session
  keeps the scan, the extracts, and the index, abbreviation and register writes, and finishes each
  wave's bookkeeping before the next starts, so a cutoff loses only the wave in flight. Otherwise
  ingest falls back to one source at a time.

## [0.6.1] - 2026-10-16

### Added
- `1-Inputs/Sources/Meetings/`: notes, minutes and transcripts of meetings that already happened.
  `ingest.md` → Meeting notes ingests one as a record of the meeting (date, attendees, decisions,
  actions with owners and due dates as stated, open questions) and offers the tracker and decision
  updates instead of making them.
- `/draft-document` → Deck: `deck-rules.md` → Using the template (profile and render the template
  before planning slides; its brand rules bind every element; template layouts are the default, custom
  shapes are allowed when a layout loses meaning), → Visual design (a presented deck is visual by
  default: a form for each kind of content, colour assigned by role, detail in speaker notes; a
  read-ahead deck is exempt) and → Headline test (read only the headlines in order; they must state the
  governing thought and every key point). Deck runs the headline test before building when there is no
  brief, and on every built deck.

### Changed
- `build_pptx.py --validate` judges density per text block instead of per slide, so card and column
  layouts no longer raise false density findings.

### Fixed
- `draft_save.py` adopt resolves the source path before logging it relative to the project root
  (failed on macOS `/private/var` and Windows short temp paths).

## [0.6.0] - 2026-10-16

### Added
- `/deliverable-brief`: scope a deliverable before drafting it. The brief
  (`2-Drafts/<slug>/_brief.md`) moves from core (governing thought, audience, objective) to argument
  (situation, complication, resolution, key points with sources and evidence status) to a headline
  outline. Every field is marked `agreed` or `proposed`. The user locks it, and later changes are
  recorded as amendments. New `project.output` route row. `project_check.py` and Workspace tidy treat
  `_brief.md` as a known file.
- Brief profiles: a profile describes one kind of deliverable (extra fields, outline skeleton, what to
  look for in the project, style). `/deliverable-brief` builds one from the user's own examples, structure
  only, and saves it on a yes to `~/.familiar/brief-profiles/`, offered only in projects of the same
  Organization. Extensions can ship profiles under `brief-profiles/`. A read-only harvest pre-fills the
  brief from project context, the status snapshot, decision records and knowledge pages, as `proposed`
  fields with locators.
- `/draft-document` → Deck and Document read the deliverable's `_brief.md` first. A locked brief
  settles audience, format, key points and outline, and the draft follows its headlines; an unlocked or
  missing brief gets a one-line warning and drafting continues. The completion report names any section
  or slide that maps to no key point, and any key point with no section or slide.

## [0.5.0] - 2026-10-16

### Added
- `4-Trackers/meetings.md`: planned internal and client meetings, as a series rule (`weekly:<day>` or
  `every-2-weeks:<day>`) plus per-date exception rows (moved, cancelled, extra) and single meetings. Notes
  only: nothing syncs with a calendar. A project starts the file on its first meeting; a project without one
  is unaffected. Rules in `state-schema.md` → Tracker conventions.
- `.familiar/scripts/meetings_view.py`: expands the rules into dated occurrences (`--json --window N`) and
  writes `4-Trackers/_views/meetings-next-weeks.md`.
- `tracker_edit.py meeting add-series|add-oneoff|move|cancel|edit-series`: the same revision check, atomic
  write, status-log entry and regenerated view as the milestone and task edits. It refuses a change that would
  leave `meetings.md` with a problem it did not have, and reports a new overlap.
- `project_check.py` flags a stale meetings view, an unreadable meeting row and a meeting naming an unknown
  milestone.

## [0.4.8] - 2026-10-15

### Added
- `.familiar/scripts/tracker_edit.py`: one validated change to `timeline.md` (a milestone's due date, status
  or confirmed date) or `tasks.md` (a task done, reopened, or re-dated). It checks the revision, replaces the
  file atomically, logs old → new and the reason to `status-log.md`, regenerates the timeline views, and
  never deletes a row ("no longer needed" is `not applicable`, with a reason). `--dry-run` shows the exact
  before and after. A tracker with no revision header gets one on its first edit. The fleet hub's
  `/fleet` update uses it.
- Milestone `Type` adds `client meeting` and `internal meeting` (`state-schema.md`).

### Changed
- `timeline_views.py --json` includes each milestone's `type`.

## [0.4.7] - 2026-10-15

### Fixed
- `task_frontier.py` reads a task title that wraps onto indented lines in full (it stopped at the first
  line), keeps the ID of a task written `**T13 — Title.**` (it read the title as "T13"), and skips the old
  template's `(example)` rows.

### Added
- `task_frontier.py --json` returns each task's `owner`, read from its `Owner:` field (empty when not set).

## [0.4.6] - 2026-10-14

### Changed
- Check-in no longer asks for a check-in cadence: the `Check-in cadence` field is gone from the
  `project-config.md` template and stub. Nothing read it. Existing projects keep the line; it is ignored.

## [0.4.5] - 2026-10-14

### Changed
- **Lifecycle is the fleet hub's, not the project's.** `/system-settings` → Fleet no longer sets the
  snapshot's `Lifecycle`; it registers and unregisters only, and adds a blank-safe `lifecycle` cell when the
  registry has that column. The hub records lifecycle in `~/.familiar/fleet.md` (`fleet_overview.py
  --set-lifecycle`), treats blank as `active`, and reports a snapshot value that disagrees. Project-closeout
  tells the user to close the project in the hub. `project_check.py` no longer asks you to add a
  `Lifecycle` field to the snapshot, and check-in no longer writes one.

## [0.4.4] - 2026-10-14

### Changed
- **`/system-settings` → Fleet no longer creates `~/.familiar/fleet.md`.** The fleet hub creates it
  when it is set up, with a script that behaves the same on every host. Fleet still adds, removes or
  updates this project's own row in an existing file and sets the lifecycle; with no file, it says
  to set up the hub and writes nothing.

## [0.4.3] - 2026-10-14

### Added
- **`timeline_views.py --json --window N`** widens the "upcoming" list to `N` days (default 14) for
  tools that look further ahead, such as the fleet hub's daily brief. The generated views and every
  other output are unchanged.

## [0.4.2] - 2026-10-10

### Added
- **A cross-platform preflight check.** `python .familiar/scripts/doctor.py` (`python3` on macOS)
  checks your operating system, Python, `python-docx` (1.2.0 or later), `python-pptx`, PyMuPDF,
  LibreOffice, pandoc, and the optional OCR tools, explains what stops working without each, and
  exits `0` when everything required is present. It uses only the standard library and runs the
  Windows-only checks only on Windows. `doctor.ps1` is still shipped for Windows PowerShell users.
- **A user guide, contributing and security policies, and this changelog** at the repository root:
  `GUIDE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`. The technical reference `MANUAL.md`
  now ships with the release.
- **Prerequisites, a per-host invocation table, and a section for untested hosts** in `INSTALL.md`
  and `GUIDE.md`.

### Changed
- **Document and deck builds find LibreOffice in its default install folder** (macOS app bundle,
  Windows Program Files, common Linux paths) as well as on `PATH`, so visual validation no longer
  reports unavailable on a standard install. Only the Windows location has been tested.
- **Sync conflict detection covers iCloud Drive.** The check that stops a write when a conflict copy
  sits beside a state file now recognizes iCloud's `tasks 2.md` pattern alongside OneDrive and
  Dropbox ones. `INSTALL.md` lists iCloud Drive as a supported synced location, with the
  one-writer-at-a-time limit unchanged.
- **Hosts with no capability record are handled explicitly.** On a host with no row in
  `.familiar/installed.json` (Cursor, GitHub Copilot, OpenCode), every capability is treated as
  `unknown`, worker steps run inline, and an extension route is reported as unverified and
  confirmed with you before it runs.
- **Skill-start instructions are host-neutral.** When a skill is user-only, the assistant now tells
  you how to start it on your host (a slash command, a `$` mention, or asking by name) instead of
  assuming `/skill-name`.
- **`/system-settings` → Fleet says the fleet hub is distributed separately and not yet published.**
  Registering a project is optional and writes only one row to `~/.familiar/fleet.md`.
- On Codex, `checkin` is now explicit-only like every other user-only skill
  (`allow_implicit_invocation: false`); it had been the one exception. `INSTALL.md` no longer says
  Codex is explicit-only across the board: `ingest` and `ongoing-work` still let Codex pick them
  from your request. It also states that the
  signature is set from `/system-settings` → Preferences, not at first check-in.

## [0.4.1] - 2026-10-10

### Changed
- **Every skill that writes under `2-Drafts/` now saves through `.familiar/scripts/draft_save.py`.**
  `draft-document` (document and deck) and `handoff` → assignment brief follow the same versioned
  save path introduced in 0.4.0, instead of leaving it as guidance. A gate fails if a skill that
  writes drafts does not reference the script. The manual fallback stays in `file-handling.md`.

### Added
- **`project_check.py` checks the drafts folder.** Read-only. It reports drafts missing from the
  draft index (possible edits made outside familiar), scripts, caches, and unzipped packages left in
  `2-Drafts/`, stray top-level folders, an oversized index or cell, off-convention names,
  deliverables still flat with two or more versions, and a large or old `.scratch/` folder.

## [0.4.0] - 2026-10-09

### Added
- **Preferences branch in `/system-settings`.** Shows the global (`~/.familiar/user-preferences.md`)
  and project preferences and which one wins, sets your signature, and adds, edits, or removes a
  standing preference, each with approval. The signature is global only; a project-only signature is
  a hand edit. This branch's write to the global file is a declared exception to the project-boundary
  rule.
- **Fleet branch in `/system-settings`.** Registers or unregisters the project in
  `~/.familiar/fleet.md` and sets its `Lifecycle` (for example active or on hold). Writes only this
  project's own row.
- **Versioned drafts save path.** `.familiar/scripts/draft_save.py` saves a new version of a draft
  with automatic subfolders, moves the previous version to `_superseded/`, records it in a versions
  log, and can `adopt` a file you edited outside familiar. `file-handling.md` defines the procedure,
  the log, and a `.scratch/` folder for intermediate files.
- **A Review branch in `draft-document`.** Edits a Word file your team already owns as tracked
  changes and threaded comment replies by "Claude (AI)", without rebuilding it. Includes a byte-level
  check that nothing outside the edits changed and an option to produce an accepted-changes copy.
- **Document rules for sourcing.** A `Referencing method` preference, a `_trace.md` provenance
  sidecar beside a draft, and a three-grade claims check that runs before a document is handed over.
- **A read-only project health check.** `.familiar/scripts/project_check.py`, used by check-in,
  reports problems without changing anything. Check-in also reads a `Lifecycle` field and a
  `confirmed` date on the status snapshot, and an owner and date convention on tasks.
- **A source register.** Ingest records each source's scan receipt and per-version records in
  `3-Knowledge/_source-register.md`.
- **One editable schedule.** `timeline.md` is the single source; generated views are
  revision-stamped. Older timelines with date-named columns such as "Target Date" are read correctly.
- **Counting helpers.** `ref_count.py`, `index_check.py`, and `task_frontier.py` compute what the
  model previously estimated: reference carry-through, index consistency, and the set of tasks with
  nothing blocking them.
- **Ingest guards.** A one-time warning on multi-source or oversized ingests, offering one source per
  fresh context; a page-fidelity check in PDF extraction that recovers pages which lost body text.

### Changed
- **The startup read now always includes `~/.familiar/user-preferences.md`**, not only as a signature
  fallback, so your global standing preferences apply in every project. Project preferences win on
  any conflict.
- **`checkin` no longer asks for the signature.** When none exists it says so once and points to
  `/system-settings` → Preferences.
- **Workspace tidy judges drafts by the draft index, not by version numbers**, and records the moves
  it makes.
- **New top-level folders for generated files are forbidden**, and review records stay out of
  `2-Drafts/`.

## [0.3.1] - 2026-09-26

### Fixed
- The extraction and document tools can no longer overwrite their own source files.
- `--revise` refuses a replacement that would leave hyperlink or tracked-change text behind.
- Check-in reconciles a project configuration that was already filled in instead of resetting it.
- Skills name state files by their full `5-System/` path, and a failed read is reported as a gap
  rather than as an empty project.

### Changed
- Release builds are stamped with a build identifier, and `/system-settings` → Update treats the same
  version with a different build as an update.

## [0.3.0] - 2026-09-11

The baseline for this repository: the drop-in "Design A" shape.

### Changed
- **No installer.** `familiar-workspace/` is the release. You download it, rename it to your project,
  and open Claude Code, Codex, or Gemini CLI inside it. There is no build step, no setup command, and
  nothing runs on your machine to install it.
- **Content folders are numbered and named by role:** `1-Inputs/`, `2-Drafts/`, `3-Knowledge/`,
  `4-Trackers/`, `5-System/`. The `.familiar-project` marker ships in place.
- **Extension routes are discovered by presence on disk.** A route is available exactly when its
  skill folder exists; there is no separate registry file.
- **Nine core skills**, four of them menus with branches: `checkin`, `ongoing-work`, `ingest`,
  `draft-document`, `save`, `handoff`, `triage`, `online-research`, and `system-settings`.

### Removed
- The automated updater. Updating is a manual move of your content into a fresh copy of the release
  (see `INSTALL.md`). A lighter updater is planned but not built.

### Added
- Detection of synced-folder write collisions: before updating a state file, familiar looks for a
  conflict copy beside it and stops rather than writing. One writer at a time remains the supported
  model.
