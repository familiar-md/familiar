# Using familiar

The full user guide: installing, your first session, everyday workflow, the skills and
troubleshooting. It is also published, with search, at <https://familiar-md.github.io/familiar/>. The
short version is in the [README](../README.md).

## Download

From the [Releases page](https://github.com/familiar-md/familiar/releases):

| File | What it is |
|---|---|
| `familiar-workspace-<version>.zip` | The workspace. Unzip it; the folder inside is your first project. Give it a name you will recognise. |
| `familiar-demo-<version>.zip` (optional) | A fictional project after a few weeks of use. It unzips to `Cauldron-Roasters/`, named after its project the way you would name yours. |

The workspace is a dedicated folder for the agent, not a replacement for your project folder; see
[How the workspace fits your project](#how-the-workspace-fits-your-project). Nothing else needs
downloading: this page and the pages it links are the documentation.

> **Already have a project folder?** The workspace can sit inside it, one level down, beside your
> other files. Open the agent in the workspace folder, not the outer one. The agent works only
> inside the workspace; you move files in and out by hand. [Where things live](#where-things-live)
> shows both layouts.

## Works with

It needs a coding agent that opens a folder and reads and writes files in it.

| Agent | Status |
|---|---|
| [Claude Code](https://code.claude.com/docs/en/overview), in a terminal, VS Code or JetBrains, or the Code tab of the Claude desktop app | Built and tested; in daily use |
| [Codex](https://developers.openai.com/codex) | Tested |
| [Gemini CLI](https://geminicli.com/docs/) | Tested |
| Other agents that read `AGENTS.md` and agent skills | Should work; not tested |
| Claude.ai chat, Claude Cowork | Not supported: neither works inside a project folder |

Each agent needs its own account or subscription; the workspace adds no install steps to it.

**Python 3.10 or newer** is recommended. Word and PowerPoint builds and PDF text extraction need it.
You do not need a terminal for it: when a step needs Python or a package that is missing, the agent
says what will not work, offers to install it, and installs nothing without a yes. To check
everything at once, ask the agent to "run the preflight".

**How the maintainer runs it:** Sonnet for most sessions (over three quarters), Opus for the rest:
deliverable briefs, reviewing content, planning sessions, and drafting a demanding deliverable.
Sonnet handles most drafting well.

## Your first session

1. **Rename the folder.** Rename `familiar-workspace/` to your project's name and move it where you
   want it. That folder is the dedicated workspace for the agent.
2. **Add your sources** (now or later). Copy in what you want the agent to know.

   | Folder | Suggested use |
   |---|---|
   | `1-Inputs/Sources/` | Documents to ingest: reports, minutes, articles |
   | `1-Inputs/Admin/` | Scope, SOWs, contracts, timelines, correspondence |
   | `1-Inputs/Templates/` | Files to build from: a branded PowerPoint template, a Word report template, a standard workbook. **Keep this name**: the deck builder looks here. |
   | `1-Inputs/Examples/` | Past deliverables to learn a style from |

   The other subfolders are suggestions: add, rename or nest your own as you like. Keep the five
   numbered top-level folders as they are.
3. **Open your agent in that folder.** The folder must be the working folder, because the agent
   finds its instructions there.
   - Terminal: `cd` into the folder and start the agent (`claude`, for example).
   - VS Code: **File → Open Folder**, then open Claude Code.
   - Claude desktop app: the **Code** tab, with this folder chosen.
4. **Run the check-in:** `/ili-project-status check-in`. It reads what is already in the folder, then
   asks only what the files cannot answer: a project name, what it is for, the next concrete outcome,
   any deadline, and a signature: a three-character glyph, such as `v_v` or `o.o`, that stands for
   this project. It leaves the project with a configuration, a status snapshot and a first set of
   tasks.
5. **Start working.** From the next session on, the first reply opens with the bound line:
   `*(v_v) familiar bound*: Project Name`.

### The bound line

It shows that the instructions loaded, and, with several projects open in different windows, which
one is answering. The fleet hub labels each project with its signature too.

| You see | It means | Do this |
|---|---|---|
| Your project's signature and name | Loaded, right project | Nothing |
| Another project's signature | The agent was opened in another project's folder | Reopen it in the right one |
| Your default signature | This project has none of its own | Set one: `/ili-system-settings preferences` |
| `not set` | No signature anywhere yet | Set one: `/ili-system-settings preferences` |
| `n/a` | Reading the signature failed | Ask it to try again; see [Troubleshooting](#troubleshooting) |
| No line at all | The instructions did not load | See [Troubleshooting](#troubleshooting) |

The bound line is a check, not enforcement: the rules are instructions the model follows.

## Working in sessions

Each skill loads only the files its task needs (progressive disclosure), so short, focused sessions
work best.

- **One task, or a few related ones, per session.** A focused session stays fast and cheap.
- **Start a fresh session for a new task.** Every turn sends the whole conversation again, so an old
  task's history keeps costing you on the next one. In Claude Code, `/clear` starts fresh in the same
  window.
- **Watch the context window.** When a task outgrows it, run `/ili-handoff` and continue in a new
  session; the handoff carries the thread over. Some agents also summarise a long conversation on
  their own, but a handoff is written into the project, works on every agent, and survives closing
  the window.
- **Mind the cache.** Agents cache the conversation for a while (in Claude Code, an hour on a
  subscription, five minutes on an API key). Coming back to a long session after a break re-reads
  all of it at full price; a fresh session that starts with `/ili-project-status ongoing` is often
  cheaper.

## How the workspace fits your project

![Reference files are copied into the workspace's 1-Inputs, ingested into 3-Knowledge and drafted into 2-Drafts; approved files are renamed and copied back out to your project folder](assets/familiar-workspace-flow.svg)

- **Bring in only what the agent should know.** A file not worth keeping in the agent's memory can
  stay out of the workspace entirely.
- **Iterate in `2-Drafts/`.** Every build or edit is a new version; the previous one moves to
  `_superseded/`, and `_draft-index.md` records which version is current.
- **Carry out what is approved.** When a draft is ready to share, rename it and copy it to your own
  project folder. Nothing is published or sent for you.
- **One workspace per project.** Each keeps its own memory and tasks, facts from one never turn up in
  another, and confidential material stays inside the project it belongs to.

## An example day

You run a competitor study for a client. The kickoff was last week, the minutes arrived this
morning, and a findings deck is due Friday. Here is how the day might go, and which skill does each
part.

| Moment | Skill | What happens |
|---|---|---|
| Morning: "Where are we?" | `/ili-project-status ongoing` | Current work, what is startable today, open handoffs. Writes nothing. |
| You have news, or want a proper status | `/ili-project-status check-in` | Give it your update, or ask where things stand; it reconciles tasks, timeline and status and flags drift. |
| The minutes arrive | `/ili-ingest` | One knowledge page with a locator on every claim. |
| A decision comes up: "Remember this" | `save` → To memory | Filed where that kind of fact lives. |
| The deck is big and the story is not settled (optional) | `/ili-deliverable-brief` | Message, audience, key points and outline, agreed and locked before any building. |
| Build the deck | `/ili-draft-document deck` | Built from the brief if there is one, otherwise from what you tell it; checked and saved as a new version. |
| The team returns a Word file with comments | `/ili-draft-document review` | Tracked changes and comment replies. |
| Too much to do | `/ili-project-status triage` | Startable work by effort or urgency. Writes nothing. In the fleet hub, `/ili-fleet tasks` does the same across all your projects. |
| An outside fact is needed | `/ili-online-research` | Cited answer; saves nothing unless asked. |
| Stopping mid-task | `/ili-handoff` | A handoff a later session resumes from. |
| End of day: "Save progress" | `save` → Save progress | Reconciles every open thread before you step away. |

## The skills

In Claude Code, type `/ili` to list every familiar skill. Every skill starts only from its command:
the agent may tell you which one fits, but never starts one on its own. The one exception is `save`,
which also starts from plain words ("save progress", "remember this").

| Skill | What it does | Branches |
|---|---|---|
| `project-status` | Check in and reconcile state (the first run sets up a fresh project), see where things stand, or sort what you can start today. | Check-in, Ongoing, Triage |
| `ingest` | Turns a source document into a cited knowledge page that later sessions read instead of the original. | — |
| `deliverable-brief` | Settles a deliverable's message, audience, key points and outline before drafting, then locks it. Learns a kind of deliverable from your own examples. | — |
| `draft-document` | Builds a deck, a Word or Markdown document, or an Excel workbook, or reviews a team-owned Word file. | Deck, Document, Review, Workbook |
| `save` | Files one note or task change, or reconciles state before a break. | Save progress, To memory |
| `handoff` | Parks work for a later session, or writes a standalone brief for someone outside the project. | Session handoff, Assignment brief |
| `online-research` | Answers a question from outside sources, with citations and stated gaps. | — |
| `system-settings` | Housekeeping for the installation and the project shell. | Update, Workspace tidy, Tracks, Project closeout, Preferences, Hooks |

Name a branch to skip the menu: `/ili-save progress`, `/ili-draft-document deck`. The
[skills quick reference](../QUICK-REFERENCE.md) puts every command on one page.

**Your own skills work too.** Add them to the agent's skills folder as usual. familiar's rules still
apply while they run: outputs go to `2-Drafts/`, claims carry sources, and familiar's rules win where
a skill's own instructions disagree.

### `system-settings` branches

| Branch | What it is for |
|---|---|
| Update | Brings the project, and any extensions, up to a newer release. Put the new zips in the project's `_update/` folder and run `/ili-system-settings update`. It shows what would change and applies it on your yes. Your own edits are kept and every replaced file is backed up ([`INSTALL.md`](../INSTALL.md#updating)). |
| Workspace tidy | Finds stale drafts and loose knowledge files and proposes a cleanup; acts only on what you approve. |
| Tracks | Optional labels for parallel strands of work in one project, such as a financial model, a market scan and a report. Tasks, timeline, knowledge index and status are then grouped by track. A single-strand project never needs it. |
| Project closeout | Reconciles final state and writes a closeout summary. Deletes nothing. |
| Preferences | Sets this project's signature, your default signature, and standing preferences for every project. |
| Hooks | Turns on optional hooks, such as session titles and guards, once the [familiar-hooks](https://github.com/familiar-md/familiar-hooks) package is in the project. Copying the package in only adds the files; this branch switches each hook on or off. |

Registering a project with the optional fleet hub happens in the hub itself, not here.

### Starting a skill on each agent

| Agent | How |
|---|---|
| Claude Code | `/ili-project-status`, `/ili-ingest` and so on; a branch goes after the name: `/ili-save progress`. |
| Codex | `$project-status`, `$ingest` and so on, or the `/skills` picker. |
| Gemini CLI | Ask for it by name ("run the project-status skill") and confirm when asked. `/skills list` shows what it found. |
| Others | Ask for the skill by name. An agent that reads both skill folders may list each skill twice; it is the same skill. |

Put the command first in the message. A command mid-sentence often works too; if a skill did not
run, resend with the command first.

## Common questions

### Do I need a deliverable brief?

No. It is optional, and worth it only before a large or complex deck or report. It settles the main
message, audience, key points and outline before anything is built, so the draft needs fewer rounds
and fewer tokens. `draft-document` builds from the brief when there is one, and without one
otherwise.

### What is ingest for?

- **Not every source needs it.** Ingest what you want the agent to keep and refer back to: meeting
  minutes that track progress, or an article you plan to quote and cite in a report.
- **It writes one knowledge page** in `3-Knowledge/`, with a locator (page, section or table) on
  every claim, plus a row in the knowledge index and the source register.
- **Later sessions read the page, not the original**, which saves time and tokens. The locators let
  the agent go back to the original when exact wording matters.

### Which save?

- **To memory** files one thing: a decision, a risk, a task change. It reads only the file that holds
  that kind of fact.
- **Save progress** reconciles the whole project's state before a break: the status snapshot, tasks,
  timeline and open handoffs.
- **When unsure, use Save progress.** It reads more, so it costs a few more tokens, and misses
  nothing.

### What happens to old drafts?

- A new draft never overwrites an old one; earlier versions move to `_superseded/`.
- The Review branch edits a Word file your team already owns, without rebuilding it. Every edit is a
  tracked change and every reply goes in the existing comment thread, under the author name
  **AI Review**. It never accepts or rejects anyone else's changes and never touches a
  reference-manager field.
- A file edited outside the workspace comes back in as the next version, under the editor's initials.

### Where do answers come from?

From the project's own record, with the exact reference. When the record has no answer, the agent
reports a gap rather than guessing. When you want an outside source, `online-research` looks it up
and cites each source with its access date.

## Where things live

The demo project, Cauldron Roasters, shows the layout: a consultancy writing a competitor brief for
a coffee roaster.

**On its own.** The renamed workspace is the whole project:

```text
Cauldron-Roasters/
├── 1-Inputs/
│   ├── Sources/     market-note.pdf, kickoff-notes.docx
│   ├── Admin/       Cauldron-SOW.pdf, contract.pdf
│   ├── Templates/   branded-deck.potx, report.dotx
│   └── Examples/    last-year-brief.pptx
├── 2-Drafts/        competitor-brief/, versioned
├── 3-Knowledge/     a page per ingested source
├── 4-Trackers/      tasks.md, timeline.md
├── 5-System/        config, status, decisions
├── _update/         new release zips, when updating
└── .familiar/ …     the agent's own files
```

**Inside an existing project folder.** The workspace sits one level down, beside files the agent
never sees. Open the agent in `Cauldron-Roasters-familiar/`, not in `Cauldron-Roasters/`:

```text
Cauldron-Roasters/
├── Finance/                      invoices, budget.xlsx
├── Deliverables/                 final decks you copied out
└── Cauldron-Roasters-familiar/   the workspace, laid out as above
```

Name the workspace after the project, with `-familiar` on the end. Many editors and agents show the
folder name when a session starts, so with several projects open you can tell them apart at a glance,
before the first reply.

| Folder | What is in it | Who writes it |
|---|---|---|
| `1-Inputs/` | `Sources/`, `Admin/`, `Templates/`, `Examples/`. Add or rename subfolders freely; keep `Templates/` as named. | You. The agent only reads it. |
| `2-Drafts/` | Generated documents and decks, versioned, with `_draft-index.md` listing what is current. | The agent. You copy finished work out. |
| `3-Knowledge/` | One page per ingested source, an index, a source register, cached full-text extractions. | The agent. |
| `4-Trackers/` | `tasks.md` (open items and what blocks them) and `timeline.md` (milestones and dates). | The agent, on request; you can edit them too. |
| `5-System/` | Configuration and context, `Memory/` (status snapshot and activity log), `Handoffs/`, `Decisions/`, `user-preferences.md`. | The agent. |
| `.familiar/` | The rules, route table and helper scripts. Treat as read-only. | The release. |

Every fact has one home, and living state files carry revision markers, so a later session notices a
stale write before it overwrites newer work.

## What the agent will not do

These are instructions the agent follows in every session, not locks. The guards in
[familiar-hooks](https://github.com/familiar-md/familiar-hooks) add a mechanical check on top. They
catch the common cases, but they are not a guarantee.

- **Delete your files.** It flags obsolete material and leaves removal to you.
- **Write outside the project folder.** The one exception is your global preferences file,
  `~/.familiar/user-preferences.md`, and only when you ask.
- **Overwrite a source or a draft.** It makes a dated copy or a new version instead.
- **Invent facts.** Project claims are tied to a retrieved source with a locator; a failed read is
  reported as a gap.
- **Act on anything consequential without asking.** Overwriting, publishing, sending, installing or
  changing a status needs your yes.
- **Change more than the task needs.** It does not tidy nearby files unasked.
- **Write over newer work.** It rereads a state file's revision before updating it and stops if it
  changed.

## Working with synced folders

> **Not verified.** Running a workspace from OneDrive, SharePoint, Dropbox or iCloud Drive is not a
> verified setup and may cause problems. Keep a backup if you try it.

- **One session on a project at a time.** Two sessions, or two computers syncing the same folder,
  can overwrite each other's changes, and the agent cannot see it happen.
- **Watch for duplicates.** If your sync app makes a copy such as `tasks 2.md` or
  `tasks (conflicted copy).md`, the agent stops and tells you. Pick the right one and delete the
  other yourself.

[`INSTALL.md`](../INSTALL.md#synced-folders-and-concurrent-use) has the details.

## Troubleshooting

**No bound line in the first reply.** The instructions did not load, or the model skipped the step.
Check that the agent was started inside the project folder (the one holding `.familiar-project`),
not its parent, and that you started a new session after renaming. If both are true, ask "are you
bound to a familiar project?"; the model will usually emit the line. Do not trust the session until
you see it. If it keeps happening, open an issue with the information listed in
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

**Skill not found or not listed.** Confirm you are in the project folder and started a fresh
session; skills are read at session start.

**`python` is not found, or a script says it needs Python 3.10 or newer.** Python is missing or too
old. On a Mac this is normal: the built-in `python3` is Apple's own older copy. Ask the agent to fix
it; it runs the preflight and offers the install. Without the agent: on Windows, install Python from
the Microsoft Store; on macOS, use the installer from python.org.

**Documents or decks will not build.** Ask the agent to run the preflight. It reports each problem
and offers the fix. The usual causes are a missing `python-docx` (version 1.2.0 or later), `python-pptx`, or LibreOffice.
Without LibreOffice a Word file still builds but is not visually checked, and a deck is not
delivered.

**The agent reports a conflict copy.** Your sync client created a second copy of a state file (for
example `tasks 2.md` or `timeline (conflicted copy ...).md`). Decide which is right, merge by hand if
needed, and delete the extra yourself; the agent will not.

**An older project looks wrong after an update.** Look at the updater's report for `diverged` files
(your edits, kept) and roll back from `5-System/_update-backups/` if needed; see
[`INSTALL.md`](../INSTALL.md#updating).

## Going further

| | |
|---|---|
| [familiar-hub](https://github.com/familiar-md/familiar-hub) | One view and a daily brief across all your projects, from a separate folder kept next to them. It also keeps the list of projects it reads. |
| [familiar-hooks](https://github.com/familiar-md/familiar-hooks) | Optional per-project hooks: session titles, and guards that block most reads and writes outside the project before they run. An extra layer, not a guarantee. |
| [familiar-template](https://github.com/familiar-md/familiar-template) | Build your own specialty extension (marketing, consulting, proposal writing and more) with an AI agent. Tag its repo with the [`familiar-extension`](https://github.com/topics/familiar-extension) topic so others can find it. |
| [`INSTALL.md`](../INSTALL.md) | Updating, agent differences, the document toolchain, synced folders. |
| [`MANUAL.md`](../MANUAL.md) | The technical reference for how the core mechanism works. |
| [`CHANGELOG.md`](../CHANGELOG.md) | What changed in each release. |
