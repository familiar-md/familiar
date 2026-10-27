# familiar user guide

This guide covers what you need before you start, what happens in your first session, the loop you
will repeat every day, and what each skill does. For installation and updating, see
[`INSTALL.md`](INSTALL.md). For the underlying mechanism, see [`MANUAL.md`](MANUAL.md).

## What familiar is

familiar is a folder. You rename it, put your project's source documents in it, and open an AI
coding assistant (Claude Code, Codex, or Gemini CLI) with that folder as the working directory. The
assistant reads a short set of instructions from the folder, loads the project's saved state (what
the project is, what is open, what happened last time), and works from that instead of starting
cold. Everything it learns is written back to plain Markdown files in the same folder, so the next
session, on any of the three assistants, picks up where this one stopped.

Nothing is installed and nothing runs in the background. If you delete the folder, familiar is gone.

## Before you start

You need one of these installed and signed in. Follow the vendor's own install page; familiar adds
no steps to it.

| Assistant | Install and sign-in |
|---|---|
| Claude Code | [code.claude.com/docs](https://code.claude.com/docs/en/overview) |
| Codex | [developers.openai.com/codex](https://developers.openai.com/codex) |
| Gemini CLI | [geminicli.com/docs](https://geminicli.com/docs/) |

Codex and Gemini CLI are installed through Node.js tooling, so you may need that first. Each
assistant needs its own account or subscription.

familiar works best with Python 3.10 or newer. You do not have to set it up yourself: when a step
needs Python or a Python package that is missing, the assistant says what will not work and offers to
install it, and installs nothing until you say yes. Without Python you can still track a project,
ingest text sources, and run check-ins, but the assistant does the bookkeeping checks by hand, which
is slower and less reliable, and it tells you when it does. Building Word and PowerPoint files and
extracting text from PDFs need Python. To check everything at once, ask the assistant to run the
preflight, or run it yourself from the project folder:

```text
python3 .familiar/scripts/doctor.py
```

Use `python` or `py` if `python3` is not found. Every problem it finds comes with the command that
fixes it on your machine, and it exits `0` when everything required is present. It reports on your
machine, not on familiar. Details are in [`INSTALL.md`](INSTALL.md#optional-document-toolchain).

## Your first session

1. **Rename the folder.** Unpack the release, rename `familiar-workspace/` to your project's name,
   and move it where you want it. That folder is the project.
2. **Add your sources.** Copy the documents you want familiar to work from into
   `1-Inputs/Sources/`. Scope documents, timelines, and correspondence go in `1-Inputs/Admin/`;
   your own blank templates go in `1-Inputs/Templates/`. You can also do this later.
3. **Open the assistant in that folder.** In a terminal, `cd` into the project folder and start
   `claude`, `codex`, or `gemini`. The folder must be the working directory; the assistant finds
   its instructions there.
4. **Look for the bound line.** Your first reply should begin with a line like
   `*(your signature) familiar bound*: Project Name`. That line is the sign that familiar's
   instructions loaded. If the signature is not set yet it reads `not set`, which is expected on a
   fresh project. If there is no such line at all, see [Troubleshooting](#troubleshooting).
5. **Run the check-in.** Start the `checkin` skill (the exact keystrokes depend on your assistant;
   see [Starting a skill](#starting-a-skill-on-each-host)). On a fresh project it asks for a project
   name, what the project is for, the next concrete outcome, and any known deadline. It reads
   whatever is already in the folder first and only asks what the files cannot answer. When it
   finishes, the project has a configuration, a status snapshot, and a first set of tasks.
6. **Give the project its signature.** Run `system-settings` and choose **Preferences**. The
   signature is a three-character glyph, such as `ili` or `v_v`, that stands for this project's familiar:
   the bound line shows it, and the fleet hub labels the project with it. It is written to this
   project's `5-System/user-preferences.md`. The same branch also sets a default signature, shown by
   any project without its own, and standing preferences you want on every project; those go to
   `~/.familiar/user-preferences.md` in your home folder. That is one of two places familiar writes
   outside the project folder, and it asks first.

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
it to an index so later sessions can find it without opening every page. Ingest also has a lighter
mode that answers a question about a document in chat and writes nothing; it defaults to that and
only writes a page when the source is worth keeping.

When you need something produced, you **draft a document** or a deck. familiar builds the Word file
or presentation from your sources, validates it, and saves it as a new version under `2-Drafts/`.
It never overwrites an earlier version; the old one moves to a `_superseded` folder and the draft
index records which version is current. A third branch edits a Word file your team already owns as
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
matches.

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
does not run the update itself. **Tracks** manages named strands of work inside one project. **Fleet** registers
the project in `~/.familiar/fleet.md`, which a cross-project overview tool that is not part of this
download creates (see [`INSTALL.md`](INSTALL.md#the-fleet-hub)); you can ignore it.

## Starting a skill on each host

The three assistants start skills differently. Skills are plain files, so the content is the same
everywhere; only the way you ask differs.

| Host | How to start a skill | Notes |
|---|---|---|
| Claude Code | Type `/ili-checkin`, `/ili-ingest`, `/ili-draft-document`, and so on. | Type `/ili` to list every familiar skill in the `/` menu. The bare form (`/checkin`) also works but is not listed. Pass a branch as an argument: `/ili-save progress`. |
| Codex | Type `$checkin`, `$ingest`, and so on, or open the `/skills` picker. | Codex can also pick a skill from your request. For `ingest` and `ongoing-work` that is allowed by configuration; the other seven are explicit-only. |
| Gemini CLI | Ask for it by name: "run the checkin skill". | Gemini has no per-skill command. It activates a skill when your request matches and asks you to confirm. `/skills` lists what it found. |
| Cursor, GitHub Copilot, OpenCode | Untested. | They read `AGENTS.md` and both skill folders, so skills may appear twice. See the note below. |

> **Tip: lead with the command.** The most reliable way to start a skill is to make the command the
> first thing in the prompt (`/online-research` or `$online-research`, then your question). A command
> placed at the end or in the middle of a sentence ("summarize the Q3 report, please /ingest") often
> works too, but it depends on the host and the assistant recognizing it, so if the skill didn't run,
> resend with the command first. `/save` and `/handoff` also work mid-message by design.

On Claude Code and Codex, a user-only skill is blocked from model invocation by host configuration
(on Codex this has not yet been checked in a live session). On Gemini CLI, the user-only rule is a
written instruction that the assistant follows; it is not enforced by the host. If the assistant ever starts a user-only skill on its own, say so and stop it.

Other hosts are untested. Cursor, GitHub Copilot in VS Code, and OpenCode read `AGENTS.md`, so the
bootstrap should load, and they read the same skill folders. familiar has no capability record for
them, so it treats every capability as unknown, does worker steps inline, and asks before running
an extension route. Expect to adjust. Reports from these hosts are welcome (see
[`CONTRIBUTING.md`](CONTRIBUTING.md)).

## Where things live

| Folder | What is in it | Who writes it |
|---|---|---|
| `1-Inputs/` | `Sources/` (documents to ingest), `Admin/` (scope, timelines, correspondence), `Templates/` (your blank decks and documents), `Examples/` (style references). | You. familiar only reads it. |
| `2-Drafts/` | Generated documents and decks, versioned, with `_draft-index.md` listing what is current. | familiar. You copy finished work out. |
| `3-Knowledge/` | One page per ingested source, an index, a source register, and cached full-text extractions. | familiar. |
| `4-Trackers/` | `tasks.md` (open items and what blocks them) and `timeline.md` (milestones and dates). | familiar, on request. You can also edit them by hand. |
| `5-System/` | Project configuration and context, `Memory/` (status snapshot and activity log), `Handoffs/`, `Decisions/`, `user-preferences.md`. | familiar. |
| `.familiar/` | The rules, route table, and helper scripts. Treat as read-only. | The release. |

The folder `examples/familiar-demo/` in the download is a fictional, populated project you can read
to see what these files look like after a few weeks of use. It is a reading sample, not something to
run. Start with [its `_about.md`](examples/familiar-demo/_about.md).

## What familiar will not do

These are rules the assistant is instructed to follow in every session. They are written
instructions, not locks, so they are only as reliable as the model following them; the bound line at
the start of a session is a check that the instructions loaded, and is not enforcement.

- **Delete your files.** It flags obsolete material and leaves removal to you.
- **Write outside the project folder.** Everything stays inside the renamed folder. The two
  exceptions are your global preferences file and, if you choose to register, one row in the fleet
  registry, both under `~/.familiar/`, and both only on your explicit request. It reads that
  preferences file at the start of each session.
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
true, ask "are you bound to a familiar project?"; the model will usually emit the line. A missing
line is a known weakness of instruction-following, so do not trust the session until you see it. If
it keeps happening, open an issue with the information listed in
[`CONTRIBUTING.md`](CONTRIBUTING.md).

**Skill not found or not listed (Codex, Gemini CLI).** Confirm you are in the project folder and
started a fresh session; skills are read at session start. On Codex, use `$skill-name` or `/skills`.
On Gemini CLI there is no `/skill-name` command; type "run the triage skill", then confirm when
asked. A skill that appears twice on another host is the same skill read from two folders.

**`python` is not found, or a script says "familiar needs Python 3.10 or newer".** Python is
missing or too old. On a Mac this is normal: the built-in `python3` is Apple's own older copy. Ask the
assistant to fix it; it runs the preflight and offers the install. By hand: on Windows,
`winget install 9NQ7512CXL7T -e` installs the Python install manager; on macOS, use the installer
from python.org. Then open a new terminal.

**Documents or decks will not build.** Run `python3 .familiar/scripts/doctor.py` (or `python`, or
`py`) and read what it reports as `FAIL`; each FAIL line ends with the command that fixes it. The usual causes are a missing `python-docx` (version 1.2.0 or
later), `python-pptx`, or LibreOffice. Without LibreOffice a Word file still builds but is not
visually checked, and a deck is not delivered.

**The assistant reports a conflict copy.** Your sync client created a second copy of a state file
(for example `tasks 2.md` or `timeline (conflicted copy ...).md`). Decide which is right, merge by
hand if needed, and delete the extra yourself. familiar will not.

**An older project looks wrong after an update.** Look at the updater's report for `diverged` files
(your edits, kept) and roll back from `5-System/_update-backups/` if needed; see
[`INSTALL.md`](INSTALL.md#updating). After an update by hand, check that `state-schema:` in
`.familiar-project` matches in both folders.
