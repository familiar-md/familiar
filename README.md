# familiar

![familiar: bound to your work](docs/assets/familiar-hearth-banner.jpg)

**familiar is a project-memory and workflow layer for LLM agents, where nothing has to be explained
twice.**

familiar is a folder. Download it, rename it to your project's name, and open your AI coding assistant
inside it. There is nothing to set up and nothing running in the background. The folder holds what the
project is, what has been decided, what is open, and where the source for each claim lives, so every
session starts from that record instead of from nothing, and answers trace back to your own sources
rather than the model's memory. On top of it sit the everyday workflows: check-ins, ingesting
documents, drafting decks and documents, research, and tracking. The record starts thin and grows as
you work, the way a colleague learns a project by being there for it.

## Download

From the [Releases page](https://github.com/familiar-md/familiar/releases), download:

- **`familiar-workspace-<version>.zip`**: the workspace. Unzip it and the `familiar-workspace` folder
  inside is your first project.
- **`familiar-demo-<version>.zip`** (optional): a fictional project after a few weeks of use. Open
  your assistant in it and ask "where are we?" to see familiar working before you start your own.

That is all you need. This page and the documents linked from it are the documentation; none of them
has to be downloaded.

## Works with

familiar runs inside an agent harness: an AI coding assistant that reads instructions from the folder
it is opened in and can read and write files there. It is built and tested with
[Claude Code](https://code.claude.com/docs/en/overview), and follows the open `AGENTS.md` and agent
skills conventions, so other assistants that read them should work too. The workspace already carries
the files [Codex](https://developers.openai.com/codex) and [Gemini CLI](https://geminicli.com/docs/)
look for. Install your assistant from its own page; familiar adds no steps to it, and each assistant
needs its own account or subscription.

familiar works best with Python 3.10 or newer. You do not have to set it up yourself: when a step
needs Python or a Python package that is missing, the assistant says what will not work and offers to
install it, and installs nothing until you say yes. Without Python you can still track a project,
ingest text sources, and run check-ins, but the assistant does the bookkeeping checks by hand, which is
slower and less reliable, and it tells you when it does. Building Word and PowerPoint files and
extracting text from PDFs need Python. To check everything at once, ask the assistant to run the
preflight, or run `python3 .familiar/scripts/doctor.py` yourself from the project folder (`python` or
`py` if `python3` is not found). Every problem it finds comes with the command that fixes it.

## Your first session

1. **Rename the folder.** Rename `familiar-workspace/` to your project's name and move it where you
   want it. That folder is the project.
2. **Add your sources.** Copy the documents you want familiar to work from into
   `1-Inputs/Sources/`. Scope documents, timelines, and correspondence go in `1-Inputs/Admin/`;
   your own blank templates go in `1-Inputs/Templates/`. You can also do this later.
3. **Open the assistant in that folder.** In a terminal, `cd` into the project folder and start your
   assistant (`claude`, for example). The folder must be the working directory; the assistant finds
   its instructions there.
4. **Look for the bound line.** Your first reply should begin with a line like
   `*(your signature) familiar bound*: Project Name`. That line is the sign that familiar's
   instructions loaded. If the signature is not set yet it reads `not set`, which is expected on a
   fresh project. If there is no such line at all, see [Troubleshooting](#troubleshooting).
5. **Run the check-in.** Start the `checkin` skill (`/ili-checkin` in Claude Code; see
   [Starting a skill](#starting-a-skill)). On a fresh project it asks for a project name, what the
   project is for, the next concrete outcome, and any known deadline. It reads whatever is already in
   the folder first and only asks what the files cannot answer. When it finishes, the project has a
   configuration, a status snapshot, and a first set of tasks.
6. **Give the project its signature.** Run `system-settings` and choose **Preferences**. The
   signature is a three-character glyph, such as `ili` or `v_v`, that stands for this project's
   familiar: the bound line shows it, and the fleet hub labels the project with it. The same branch
   also sets a default signature and standing preferences for every project; those go to
   `~/.familiar/user-preferences.md` in your home folder, one of two places familiar writes outside
   the project folder, and it asks first.

## The everyday loop

A working day has a shape, and familiar's skills follow it.

You begin with a **check-in**. It reads the project's saved state, looks for things that have
drifted (a task that is overdue, a status that has not been confirmed in a while, a conflict copy
left by a sync client) and reports what is healthy and what is not. It tells you what is startable
today, meaning tasks with nothing blocking them, rather than a flat list of everything open. If you
only want the answer to "where are we?" without any housekeeping, `ongoing-work` does that: it reads
the state and writes nothing.

Then you work. When a new source arrives, such as a report, a protocol, a set of meeting notes, or a
presentation, you ask familiar to **ingest** it. Ingest reads the document and writes one page into
`3-Knowledge/` that summarizes it, with a locator (page, section, or table) on every claim, and adds
it to an index so later sessions can find it without opening every page. Asked a question about a
document instead, it answers in chat and writes nothing.

When you need something produced, you **draft a document** or a deck. familiar builds the Word file
or presentation from your sources, validates it, and saves it as a new version under `2-Drafts/`.
It never overwrites an earlier version; the old one moves to a `_superseded` folder and the draft
index records which version is current. Another branch edits a Word file your team already owns as
tracked changes and comment replies, without rebuilding it. Finished drafts stay in `2-Drafts/`
until you copy them out; familiar does not publish or send anything.

Decisions, risks, and task changes come up mid-conversation. **Save** captures them: `save
to-memory` files a single note or edits a single task, and `save progress` reconciles the whole
project's state before you step away. Neither creates a new kind of file; both update the files
that already hold that kind of fact.

When you stop mid-task, a **handoff** parks the work so a later session can resume it, or writes a
standalone brief for a coworker or another AI tool that has no access to your project. The next day,
the check-in or `ongoing-work` picks the state back up.

Between those, two read-only skills help you decide what to do: `triage` sorts open work by effort
or urgency, and `online-research` answers a question from external sources with citations, saving
nothing unless you say so.

## The skills

Ten skills ship in core. "User-only" means the assistant is told never to start the skill on its
own; you must ask for it. Skills marked "no" can be started by the assistant when your request
matches. The [cheat sheet](CHEATSHEET.md) puts every command on one page.

| Skill | What it does | User-only | Branches |
|---|---|---|---|
| `checkin` | Reconciles project state, reports health, and sets up a fresh project on its first run. | Yes | None |
| `ongoing-work` | Answers "what is open and in progress right now" from saved state. Writes nothing. | No | None |
| `ingest` | Digests a source document into `3-Knowledge/` with locator-level citations. Started by its command, it always builds the page; started by the assistant from a question about a document, it answers in chat and writes nothing. | No | None |
| `deliverable-brief` | Settles a deliverable's main message, audience, key points, sources and headline outline before drafting, then locks it as the plan the draft follows. Learns a kind of deliverable from your own examples and pre-fills from what the project already knows. | Yes | None |
| `draft-document` | Builds a deck, a Word/Markdown document or an Excel workbook, or edits a team-owned Word file as tracked changes. | Yes | Deck, Document, Review, Workbook |
| `save` | Captures a note or task change, or reconciles state before a break. | Yes | Save progress, To memory |
| `handoff` | Parks work for a later session, or writes a standalone brief for someone outside the project. | Yes | Session handoff, Assignment brief |
| `triage` | Sorts the open work you can start today by effort or urgency. Writes nothing. | Yes | None |
| `online-research` | Researches a question against outside sources, with citations and stated gaps. | Yes | None |
| `system-settings` | Housekeeping for the installation and the project shell. | Yes | Update, Workspace tidy, Tracks, Project closeout, Preferences, Fleet, Hooks |

A skill with branches is a menu: you can name the branch when you start it ("`draft-document` deck")
or it will ask. It runs exactly one. For `save` and `handoff` only, asking in plain words works too:
"save progress" or "hand this off" starts the same thing as the command. Every other skill in this
table starts only from its command.

Notes on three `system-settings` branches. **Update** compares your version with a newer release
and gives you the updater command to run from a terminal ([`INSTALL.md`](INSTALL.md#updating)); it
does not run the update itself. **Tracks** manages named strands of work inside one project.
**Fleet** registers the project with the [fleet hub](#going-further); you can ignore it without one.

### Starting a skill

Skills are plain files, so the content is the same everywhere; only the way you ask differs.

| Assistant | How to start a skill |
|---|---|
| Claude Code | Type `/ili-checkin`, `/ili-ingest`, `/ili-draft-document`, and so on. Type `/ili` to list every familiar skill. Pass a branch as an argument: `/ili-save progress`. |
| Codex | Type `$checkin`, `$ingest`, and so on, or open the `/skills` picker. |
| Gemini CLI | Ask for it by name: "run the checkin skill", then confirm when asked. |
| Others | Ask for the skill by name. An assistant that reads both skill folders may list each skill twice; it is the same skill. |

The most reliable way to start a skill is to make the command the first thing in the prompt. A
command in the middle of a sentence often works too, but if the skill didn't run, resend with the
command first. `/save` and `/handoff` work mid-message by design.

## Where things live

```text
<project>/                      (your renamed familiar-workspace folder)
├── .familiar-project           marks the project boundary
├── .familiar/                  rules, route table, helper scripts
├── CLAUDE.md  AGENTS.md  GEMINI.md
├── .claude/  .agents/  .codex/  .gemini/    skills and subagents, per assistant
├── 1-Inputs/                   source documents, templates, admin
├── 2-Drafts/                   generated outputs pending approval
├── 3-Knowledge/                digested source material
├── 4-Trackers/                 tasks, timeline
└── 5-System/                   config, context, status, decisions, handoffs
```

| Folder | What is in it | Who writes it |
|---|---|---|
| `1-Inputs/` | `Sources/` (documents to ingest), `Admin/` (scope, timelines, correspondence), `Templates/` (your blank decks and documents), `Examples/` (style references). | You. familiar only reads it. |
| `2-Drafts/` | Generated documents and decks, versioned, with `_draft-index.md` listing what is current. | familiar. You copy finished work out. |
| `3-Knowledge/` | One page per ingested source, an index, a source register, and cached full-text extractions. | familiar. |
| `4-Trackers/` | `tasks.md` (open items and what blocks them) and `timeline.md` (milestones and dates). | familiar, on request. You can also edit them by hand. |
| `5-System/` | Project configuration and context, `Memory/` (status snapshot and activity log), `Handoffs/`, `Decisions/`, `user-preferences.md`. | familiar. |
| `.familiar/` | The rules, route table, and helper scripts. Treat as read-only. | The release. |

Every fact has one authoritative home, and living state files carry revision markers so a later
session can detect a stale write before overwriting newer work.

## One folder per project

familiar works best one project to a folder. Open your assistant in the project you want to work on
and it becomes familiar with that project, its details, decisions, and history, and with nothing
else. Keeping projects apart keeps each one's memory and tasks its own, stops one project's facts
turning up in another, and keeps confidential material inside the project it belongs to.

familiar core is free and open source: plain Markdown and a few small scripts that you own, with no
account, no server, and nothing to sign up for. Every rule, skill, and template is a file you can read
and change. familiar stores nothing outside the folder; the AI assistant you open in it sends what it
reads to its own provider, under that provider's terms.

## What familiar will not do

These are rules the assistant is instructed to follow in every session. They are written
instructions, not locks, so they are only as reliable as the model following them; the bound line at
the start of a session is a check that the instructions loaded, and is not enforcement. For a
mechanical check, add the guards from [familiar-hooks](https://github.com/familiar-md/familiar-hooks).

- **Delete your files.** It flags obsolete material and leaves removal to you.
- **Write outside the project folder.** The two exceptions are your global preferences file and, if
  you choose to register, one row in the fleet registry, both under `~/.familiar/`, and both only on
  your explicit request.
- **Overwrite a source or a draft.** It makes a dated copy or a new version instead.
- **Invent facts.** Claims about the project are tied to a retrieved source with a locator. If a
  read fails or a document cannot be fetched, it reports a gap instead of guessing.
- **Act without asking on anything consequential.** Overwriting, publishing, sending, installing, or
  changing a status needs your approval.
- **Change more than the task requires.** It does not tidy adjacent files unasked.
- **Write over newer work.** Before updating a state file it rereads the file's revision and stops if
  it changed.

## Working with synced folders

A project may live in OneDrive, SharePoint, Dropbox, or iCloud Drive, and you may move between
machines. familiar supports one writer at a time. Do not run two sessions against the same project
at once, on synced storage or off it: a sync client reconciles after the write, so the stale-write
check cannot see the collision. If a sync conflict copy appears beside a state file, familiar stops
and reports it rather than writing. [`INSTALL.md`](INSTALL.md#synced-folders-and-concurrent-use)
has the details.

## Troubleshooting

**No "familiar bound" line in the first reply.** The instructions did not load, or the model skipped
the step. Check that the assistant was started inside the project folder (the folder that contains
`.familiar-project`), not its parent, and that you started a new session after renaming. If both are
true, ask "are you bound to a familiar project?"; the model will usually emit the line. Do not trust
the session until you see it. If it keeps happening, open an issue with the information listed in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

**Skill not found or not listed.** Confirm you are in the project folder and started a fresh
session; skills are read at session start.

**`python` is not found, or a script says "familiar needs Python 3.10 or newer".** Python is
missing or too old. On a Mac this is normal: the built-in `python3` is Apple's own older copy. Ask the
assistant to fix it; it runs the preflight and offers the install. By hand: on Windows,
`winget install 9NQ7512CXL7T -e` installs the Python install manager; on macOS, use the installer
from python.org. Then open a new terminal.

**Documents or decks will not build.** Run `python3 .familiar/scripts/doctor.py` (or `python`, or
`py`) and read what it reports as `FAIL`; each FAIL line ends with the command that fixes it. The usual
causes are a missing `python-docx` (version 1.2.0 or later), `python-pptx`, or LibreOffice. Without
LibreOffice a Word file still builds but is not visually checked, and a deck is not delivered.

**The assistant reports a conflict copy.** Your sync client created a second copy of a state file
(for example `tasks 2.md` or `timeline (conflicted copy ...).md`). Decide which is right, merge by
hand if needed, and delete the extra yourself. familiar will not.

**An older project looks wrong after an update.** Look at the updater's report for `diverged` files
(your edits, kept) and roll back from `5-System/_update-backups/` if needed; see
[`INSTALL.md`](INSTALL.md#updating).

## Going further

- **[familiar-hub](https://github.com/familiar-md/familiar-hub):** one view and a daily brief across
  all your projects, from a separate folder kept next to them.
- **[familiar-hooks](https://github.com/familiar-md/familiar-hooks):** optional per-project hooks:
  session titles, and guards that block reads and writes outside the project before they run.
- **[familiar-template](https://github.com/familiar-md/familiar-template):** build your own specialty
  extension (marketing, consulting, proposal writing, and more) with an AI assistant. Tag your
  extension's repo with the [`familiar-extension`](https://github.com/topics/familiar-extension) topic
  so others can find it.
- **[`INSTALL.md`](INSTALL.md):** updating, assistant differences, the document toolchain, synced
  folders.
- **[`MANUAL.md`](MANUAL.md):** the technical reference for how the core mechanism works.
- **[`CHANGELOG.md`](CHANGELOG.md):** what changed in each release.

## Versioning

familiar core, familiar-hub, familiar-hooks and familiar-template each have their own version.
Versions follow [Semantic Versioning](https://semver.org): a release that would break your project's
files or an extension written against the contract bumps the first number; new features bump the
second; fixes bump the third.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
