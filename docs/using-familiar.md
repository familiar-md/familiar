# Using familiar

This is the full user guide: download, your first session, everyday work, the skills and
troubleshooting. The same guide is on the web, with search, at
<https://familiar-md.github.io/familiar/>. The [README](../README.md) has the short version.

## Download

Get these files from the [Releases page](https://github.com/familiar-md/familiar/releases):

| File | What it is |
|---|---|
| `familiar-workspace-<version>.zip` | The workspace. Unzip it. The folder inside is your first project. Give it a name you will recognize. |
| `familiar-demo-<version>.zip` (optional) | A fictional project after a few weeks of use. It unzips to `Cauldron-Roasters/`. |

The workspace is a separate folder for the agent. It does not replace your project folder. See
[How the workspace fits your project](#how-the-workspace-fits-your-project). You need nothing else:
this guide and the pages it links to are the documentation.

> **Already have a project folder?** Put the workspace inside it, one level down, beside your other
> files. Open the agent in the workspace folder, not the outer one. The agent works only inside the
> workspace. You move files in and out yourself. [Where things live](#where-things-live) shows both
> layouts.

## Works with

You need a coding agent that opens a folder and reads and writes the files in it.

| Agent | Status |
|---|---|
| [Claude Code](https://code.claude.com/docs/en/overview), in a terminal, VS Code or JetBrains, or the Code tab of the Claude desktop app | Built and tested. In daily use. |
| [Codex](https://developers.openai.com/codex) | Tested |
| [Gemini CLI](https://geminicli.com/docs/) | Tested |
| Other agents that read `AGENTS.md` and agent skills | Not tested. They are expected to work. |
| Claude.ai chat, Claude Cowork | Not supported. Neither works inside a project folder. |

Each agent needs its own account or subscription. The workspace adds no install steps.

**Python 3.10 or newer** is recommended. Word and PowerPoint builds and PDF text extraction need it.
You do not need a terminal to install it. If a step needs Python or a missing package, the agent
tells you what will not work and offers to install it. It installs nothing until you say yes. To
check everything at once, ask the agent to "run the preflight".

**Which model to use.** On Claude Code, Sonnet does most sessions well, drafting included. Use Opus
for deliverable briefs, content reviews, planning, and demanding drafts.

## Your first session

1. **Rename the folder.** Rename `familiar-workspace/` to your project's name and move it where you
   want it. This folder is the agent's workspace.
2. **Add your sources** (now or later). Copy in what you want the agent to know.

   | Folder | Suggested use |
   |---|---|
   | `1-Inputs/Sources/` | Documents to ingest: reports, minutes, articles |
   | `1-Inputs/Admin/` | Scope, SOWs, contracts, timelines, correspondence |
   | `1-Inputs/Templates/` | Files to build from: a branded PowerPoint template, a Word report template, a standard workbook. **Keep this name.** The deck builder looks here. |
   | `1-Inputs/Examples/` | Past deliverables to learn a style from |

   The other subfolders are suggestions. Add, rename or nest your own. Keep the five numbered
   top-level folders as they are.
3. **Open your agent in that folder.** The agent finds its instructions in the folder it opens in.
   - Terminal: `cd` into the folder and start the agent (`claude`, for example).
   - VS Code: **File → Open Folder**, then open Claude Code.
   - Claude desktop app: the **Code** tab, with this folder chosen.
4. **Run the check-in:** `/ili-project-status check-in`. It reads what is already in the folder.
   Then it asks only what the files cannot answer:
   - the project name and what it is for
   - the next concrete outcome, and any deadline
   - a signature: three characters that stand for this project, such as `v_v` or `o.o`

   When it finishes, the project has a configuration, a status snapshot and a first set of tasks.
5. **Start working.** From the next session on, the first reply opens with the bound line:
   `*(v_v) familiar bound*: Project Name`.

### The bound line

The bound line shows that the instructions loaded. With several projects open in different windows,
it also shows which project is answering. The fleet hub labels each project with its signature too.

| You see | It means | Do this |
|---|---|---|
| Your project's signature and name | Loaded, right project | Nothing |
| Another project's signature | The agent opened in another project's folder | Reopen it in the right one |
| Your default signature | This project has no signature of its own | Set one: `/ili-system-settings preferences` |
| `not set` | No signature anywhere yet | Set one: `/ili-system-settings preferences` |
| `n/a` | The agent could not read the signature | Ask it to try again. See [Troubleshooting](#troubleshooting). |
| No line at all | The instructions did not load | See [Troubleshooting](#troubleshooting) |

The bound line is a check, not a lock. The rules are instructions that the model follows.

## Working in sessions

Each skill loads only the files its task needs. Short, focused sessions work best.

- **Do one task, or a few related ones, per session.** A focused session stays fast and cheap.
- **Start a fresh session for a new task.** Every turn sends the whole conversation again. An old
  task's history adds cost to the next one. In Claude Code, `/clear` starts fresh in the same window.
- **Watch the context window.** If a task outgrows it, run `/ili-handoff` and continue in a new
  session. The handoff carries the work over. Some agents summarize a long conversation on their own.
  A handoff is different: it is saved in the project, works on every agent, and stays after you
  close the window.
- **Mind the cache.** Agents cache the conversation for a while. In Claude Code, that is an hour on a
  subscription and five minutes on an API key. After a break, a long session reads all of it again
  at full price. A fresh session that starts with `/ili-project-status ongoing` often costs less.

## How the workspace fits your project

![Reference files are copied into the workspace's 1-Inputs, ingested into 3-Knowledge and drafted into 2-Drafts; approved files are renamed and copied back out to your project folder. 4-Trackers and 5-System hold what the project remembers: tasks, timeline, meetings, status, decisions and handoffs](assets/familiar-workspace-flow.svg)

- **Bring in only what the agent needs to know.** Leave out any file that is not worth keeping in the
  agent's memory.
- **Work on drafts in `2-Drafts/`.** Every build or edit makes a new version. The previous version
  moves to `_superseded/`. `_draft-index.md` records which version is current.
- **Copy out what is approved.** When a draft is ready to share, rename it and copy it to your own
  project folder. The agent publishes and sends nothing for you.
- **Use one workspace per project.** Each workspace keeps its own memory and tasks. Facts from one
  project never appear in another. Confidential material stays inside its own project.

## An example day

You run a competitor study for a client. The kickoff was last week. The minutes arrived this morning,
and a findings deck is due Friday. This is how the day can go, and which skill does each part.

| Moment | Skill | What happens |
|---|---|---|
| Morning: "Where are we?" | `/ili-project-status ongoing` | Current work, what you can start today, open handoffs. Writes nothing. |
| You have news, or want a full status | `/ili-project-status check-in` | Give it your update, or ask where things stand. It brings tasks, timeline and status up to date and flags drift. |
| The minutes arrive | `/ili-ingest` | One knowledge page, with a locator on every claim. |
| A decision comes up: "Remember this" | `save` → To memory | Filed where that kind of fact lives. |
| The deck is big and the story is not settled (optional) | `/ili-deliverable-brief` | Message, audience, key points and outline, agreed and locked before anything is built. |
| Build the deck | `/ili-draft-document deck` | Built from the brief if there is one, or from what you tell it. Checked and saved as a new version. |
| The team returns a Word file with comments | `/ili-draft-document review` | Tracked changes and comment replies. |
| Too much to do | `/ili-project-status triage` | Work you can start, sorted by effort or urgency. Writes nothing. In the fleet hub, `/ili-fleet tasks` does the same across all your projects. |
| You need an outside fact | `/ili-online-research` | An answer with citations. Saves nothing unless you ask. |
| You stop in the middle of a task | `/ili-handoff` | A handoff that a later session continues from. |
| End of day: "Save progress" | `save` → Save progress | Brings every open thread up to date before you stop. |

## The skills

![The project lifecycle. Set up: download, unzip, rename, then the first check-in. The repeatable middle: check-in, ongoing, triage and save, repeated for as long as the project runs. Close out: the project closeout. Alongside, the skills used as the work needs them: ingest and online research, deliverable brief and draft document, handoff, and system settings.](assets/familiar-lifecycle.svg)

In Claude Code, type `/ili` to list every familiar skill. A skill starts only from its command. The
agent can tell you which skill fits, but it never starts one on its own. The one exception is
`save`, which also starts from plain words ("save progress", "remember this").

| Skill | What it does | Branches |
|---|---|---|
| `project-status` | Checks in and brings the project state up to date, shows where things stand, or sorts what you can start today. The first run sets up a new project. | Check-in, Ongoing, Triage |
| `ingest` | Turns a source document into a knowledge page with citations. Later sessions read the page instead of the original. | — |
| `deliverable-brief` | Agrees a deliverable's message, audience, key points and outline before drafting, then locks them. Learns a kind of deliverable from your own examples. | — |
| `draft-document` | Builds a deck, a Word or Markdown document, or an Excel workbook. Reviews a Word file that your team owns. | Deck, Document, Review, Workbook |
| `save` | Files one note or task change, or brings the project state up to date before a break. | Save progress, To memory |
| `handoff` | Parks work for a later session, or writes a standalone brief for someone outside the project. | Session handoff, Assignment brief |
| `online-research` | Answers a question from outside sources, with citations and the gaps it found. | — |
| `system-settings` | Housekeeping for the installation and the project folders. | Update, Workspace tidy, Tracks, Project closeout, Preferences, Hooks |

Name a branch to skip the menu: `/ili-save progress`, `/ili-draft-document deck`. The
[skills quick reference](../QUICK-REFERENCE.md) puts every command on one page.

**Your own skills work too.** Add them to the agent's skills folder as usual. familiar's rules still
apply while they run. Outputs go to `2-Drafts/` and claims carry sources. If a skill's own
instructions disagree with familiar's rules, familiar's rules win.

### `project-status` branches

| Branch | What it is for |
|---|---|
| Check-in | Give it your news, or ask for a full status. It brings tasks, timeline and status up to date, reports drift such as overdue tasks, and sets up a new project on its first run. |
| Ongoing | A quick "where are we": what is open, in progress and startable now, from the saved state. Writes nothing. |
| Triage | Sorts the work you can start today by effort or urgency. Writes nothing. |

### `draft-document` branches

| Branch | What it is for |
|---|---|
| Deck | A PowerPoint deck, built on your template from `1-Inputs/Templates/` when there is one, and checked visually. |
| Document | A memo or report, as a Word file or as Markdown. |
| Review | Edits a Word file your team already owns, as tracked changes and comment replies under the name **AI Review**. It never rebuilds the file. |
| Workbook | An Excel file such as a tracker, register or summary, planned sheet by sheet and checked so nothing from its sources is lost. |

Each build is saved as a new version in `2-Drafts/`. Nothing is overwritten.

### `save` branches

| Branch | What it is for |
|---|---|
| Save progress | Brings the whole project state up to date before a break: status, tasks, timeline and open handoffs. |
| To memory | Files one thing: a decision, a risk, a preference, or one task added, changed, done or moved. |

### `handoff` branches

| Branch | What it is for |
|---|---|
| Session handoff | Parks work mid-task so a later session picks it up where you stopped. Also resumes an open handoff. |
| Assignment brief | A standalone brief for a colleague or another AI agent to pick up work outside familiar. |

### `system-settings` branches

| Branch | What it is for |
|---|---|
| Update | Brings the project and its extensions up to a newer release. Put the new zips in the project's `_update/` folder and run `/ili-system-settings update`. It shows what will change and applies the changes when you say yes. It keeps your own edits and backs up every file it replaces ([`INSTALL.md`](../INSTALL.md#updating)). |
| Workspace tidy | Finds old drafts and loose knowledge files and proposes a cleanup. It acts only on what you approve. |
| Tracks | Optional labels for parallel strands of work in one project, such as a financial model, a market scan and a report. Tasks, timeline, knowledge index and status are then grouped by track. A project with one strand does not need tracks. |
| Project closeout | Brings the final state up to date and writes a closeout summary. Deletes nothing. |
| Preferences | Sets this project's signature, your default signature, and standing preferences for every project. |
| Hooks | Turns optional hooks on or off, such as session titles and guards. First copy the [familiar-hooks](https://github.com/familiar-md/familiar-hooks) package into the project. Copying only adds the files. This branch turns each hook on or off. |

You register a project with the optional fleet hub in the hub itself, not here.

### Starting a skill on each agent

| Agent | How |
|---|---|
| Claude Code | `/ili-project-status`, `/ili-ingest` and so on. A branch goes after the name: `/ili-save progress`. |
| Codex | `$project-status`, `$ingest` and so on, or the `/skills` picker. |
| Gemini CLI | Ask for the skill by name ("run the project-status skill") and confirm when asked. `/skills list` shows the skills it found. |
| Others | Ask for the skill by name. An agent that reads both skill folders can list each skill twice. It is the same skill. |

Put the command first in the message. A command in the middle of a sentence often works too. If a
skill did not start, send the message again with the command first.

## Common questions

### Do I need a deliverable brief?

No. A brief is optional. It is worth it only before a large or complex deck or report. It agrees the
main message, audience, key points and outline before anything is built. The draft then needs fewer
rounds and fewer tokens. `draft-document` builds from the brief if there is one, and works without
one.

### What is ingest for?

- **Not every source needs it.** Ingest what you want the agent to keep and refer back to. Examples
  are meeting minutes that track progress, or an article that you plan to quote in a report.
- **It writes one knowledge page** in `3-Knowledge/`. Every claim on the page has a locator: a page,
  section or table. It also adds a row to the knowledge index and the source register.
- **Later sessions read the page, not the original.** This saves time and tokens. When exact wording
  matters, the locators take the agent back to the original.

### Which save do I use?

- **To memory** files one thing: a decision, a risk or a task change. It reads only the file that
  holds that kind of fact.
- **Save progress** brings the whole project up to date before a break: the status snapshot, tasks,
  timeline and open handoffs.
- **If you are not sure, use Save progress.** It reads more, so it costs a few more tokens, but it
  misses nothing.

### What happens to old drafts?

- A new draft never overwrites an old one. Earlier versions move to `_superseded/`.
- The Review branch edits a Word file that your team already owns. It does not rebuild the file.
  Every edit is a tracked change. Every reply goes in the existing comment thread, under the author
  name **AI Review**. It never accepts or rejects other people's changes. It never touches a
  reference-manager field.
- If someone edits a file outside the workspace, it comes back in as the next version, under that
  editor's initials.

### Where do answers come from?

Answers come from the project's own record, with the exact reference. If the record has no answer,
the agent reports a gap. It does not guess. If you want an outside source, `online-research` finds
it and cites each source with the date it was read.

## Where things live

The demo project, Cauldron Roasters, shows the layout. In it, a consultancy writes a competitor brief
for a coffee roaster.

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

Name the workspace after the project, with `-familiar` at the end. Many editors and agents show the
folder name when a session starts. With several projects open, you can then tell them apart before
the first reply.

| Folder | What is in it | Who writes it |
|---|---|---|
| `1-Inputs/` | `Sources/`, `Admin/`, `Templates/`, `Examples/`. Add or rename subfolders as you like. Keep the name `Templates/`. | You. The agent only reads it. |
| `2-Drafts/` | Generated documents and decks, in versions. `_draft-index.md` lists the current ones. | The agent. You copy finished work out. |
| `3-Knowledge/` | One page per ingested source, an index, a source register, and saved full-text extractions. | The agent. |
| `4-Trackers/` | `tasks.md` (open items and what blocks them) and `timeline.md` (milestones and dates). | The agent, when you ask. You can edit them too. |
| `5-System/` | Configuration and context, `Memory/` (status snapshot and activity log), `Handoffs/`, `Decisions/`, `user-preferences.md`. | The agent. |
| `.familiar/` | The rules, route table and helper scripts. Do not edit them. | The release. |

Every fact has one home. Files that change often carry a revision marker. Before a later session
writes to one, it compares the marker, so it does not overwrite newer work.

## What the agent will not do

These are instructions that the agent follows in every session. They are not locks. The guards in
[familiar-hooks](https://github.com/familiar-md/familiar-hooks) add a mechanical check. The guards
catch the common cases, but they are not a guarantee.

- **Delete your files.** It flags old material and leaves the removal to you.
- **Write outside the project folder.** The one exception is your global preferences file,
  `~/.familiar/user-preferences.md`, and only when you ask.
- **Overwrite a source or a draft.** It makes a dated copy or a new version instead.
- **Invent facts.** Each project claim comes from a source, with a locator. If a read fails, it
  reports a gap.
- **Do anything important without asking.** It needs your yes to overwrite, publish, send, install or
  change a status.
- **Change more than the task needs.** It does not tidy nearby files unless you ask.
- **Write over newer work.** Before it updates a state file, it reads the file's revision again. If the
  revision changed, it stops.

## Working with synced folders

> **Not tested.** A workspace in OneDrive, SharePoint, Dropbox or iCloud Drive is not a tested setup.
> It can cause problems. Keep a backup if you try it.

- **Run one session on a project at a time.** Two sessions, or two computers that sync the same
  folder, can overwrite each other's changes. The agent cannot see this happen.
- **Watch for duplicates.** Your sync app can make a copy such as `tasks 2.md` or
  `tasks (conflicted copy).md`. If it does, the agent stops and tells you. Pick the right file and
  delete the other one yourself.

[`INSTALL.md`](../INSTALL.md#synced-folders-and-concurrent-use) has the details.

## Troubleshooting

**No bound line in the first reply.** The instructions did not load, or the model skipped the step.
Check these two things:

1. The agent started inside the project folder (the one that holds `.familiar-project`), not its
   parent.
2. You started a new session after you renamed the folder.

If both are true, ask "are you bound to a familiar project?". The model usually shows the line then.
Do not trust the session until you see the line. If the problem continues, open an issue with the
information that [`CONTRIBUTING.md`](../CONTRIBUTING.md) lists.

**Skill not found or not listed.** Check that you are in the project folder and that you started a
new session. The agent reads skills when a session starts.

**`python` is not found, or a script says it needs Python 3.10 or newer.** Python is missing or too
old. On a Mac this is normal: the built-in `python3` is an older copy from Apple. Ask the agent to
fix it. It runs the preflight and offers to install Python. To install it yourself on Windows, use
the Microsoft Store. On macOS, use the installer from python.org.

**Documents or decks will not build.** Ask the agent to run the preflight. It reports each problem
and offers the fix. The usual causes are a missing `python-docx` (version 1.2.0 or later),
`python-pptx`, or LibreOffice. Without LibreOffice, a Word file still builds but nobody checks how
it looks, and a deck is not delivered.

**The agent reports a conflict copy.** Your sync app made a second copy of a state file, for example
`tasks 2.md` or `timeline (conflicted copy ...).md`. Decide which copy is right. Merge them by hand if
you need to. Then delete the extra copy yourself. The agent does not delete it.

**An older project looks wrong after an update.** Look in the updater's report for `diverged` files.
These are your own edits, and the updater kept them. To roll back, use the backups in
`5-System/_update-backups/`. See [`INSTALL.md`](../INSTALL.md#updating).

## Going further

![How extensions layer onto familiar core. Core is the base: its rules, routes and everyday skills. Extensions are folders dropped onto the project that add their own skills and routes; the template starts your own. Separately and optionally, familiar-hub gives one view across all your projects and familiar-hooks adds enforcement guards.](assets/familiar-extensions.svg)

| | |
|---|---|
| [familiar-hub](https://github.com/familiar-md/familiar-hub) | One view and a daily brief across all your projects. It is a separate folder beside your projects, and it keeps the list of projects it reads. |
| [familiar-hooks](https://github.com/familiar-md/familiar-hooks) | Optional hooks for each project: session titles, and guards that block most reads and writes outside the project before they run. An extra layer, not a guarantee. |
| [familiar-template](https://github.com/familiar-md/familiar-template) | Build your own specialty extension with an AI agent, for example for marketing, consulting or proposal writing. Tag its repo with the [`familiar-extension`](https://github.com/topics/familiar-extension) topic so that others can find it. |
| [`INSTALL.md`](../INSTALL.md) | Updating, differences between agents, the document tools, synced folders. |
| [`MANUAL.md`](../MANUAL.md) | The technical reference for how the core works. |
| [`CHANGELOG.md`](../CHANGELOG.md) | What changed in each release. |
