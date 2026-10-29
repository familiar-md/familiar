# familiar skills quick reference

One page of commands for familiar core, the fleet hub and the optional hooks. A printable version,
with a switch for your agent, is `docs/quick-reference.html`. This page shows the commands in their
Claude Code form. On Codex, use `$project-status` instead of `/ili-project-status`. On Gemini CLI, ask
for a skill by name ("run the project-status skill").
[`docs/using-familiar.md`](docs/using-familiar.md#the-skills) explains each skill.

## In a project

| Command | Use it to | Branches |
|---|---|---|
| `/ili-project-status` | Check in and bring the project up to date, see where things stand, or sort what you can start today. The first run sets up a new project. | Check-in, Ongoing, Triage |
| `/ili-ingest` | Turn a source document into a knowledge page with citations, in `3-Knowledge/`. Later sessions read the page instead of the original. | — |
| `/ili-deliverable-brief` | Optional, for a large or complex deliverable. Agree its message, audience, key points and outline before building. The draft then needs fewer rounds. | — |
| `/ili-draft-document` | Build a deck, a document or a workbook, or review a Word file that your team owns. | Deck, Document, Review, Workbook |
| `/ili-save` | Bring the project up to date before a break, or file one note or task change. | Save progress, To memory |
| `/ili-handoff` | Park work for a later session, or write a brief for someone outside the project. | Session handoff, Assignment brief |
| `/ili-online-research` | Answer a question from outside sources, with citations. | — |
| `/ili-system-settings` | Housekeeping for the installation and the project folders. | Update, Workspace tidy, Tracks, Project closeout, Preferences, Hooks |

Type `/ili` to list them all. Name a branch to skip the menu: `/ili-save progress`,
`/ili-draft-document deck`. A skill starts only from its command. The agent can tell you which skill
fits, but it never starts one. The one exception is `save`: "save progress" or "remember this" in
plain words starts it.

**Where things go:** sources in `1-Inputs/` (the agent only reads them), drafts in `2-Drafts/`,
knowledge pages in `3-Knowledge/`, tasks, dates and meetings in `4-Trackers/`, state and memory in
`5-System/`.

## In the fleet hub

Open your agent in the hub folder, then run `/ili-fleet` and ask in plain words. See
[familiar-hub](https://github.com/familiar-md/familiar-hub).

| Ask about | Branch | |
|---|---|---|
| What is active, overdue and next | overview | the default |
| What you can start now | tasks | |
| The next two weeks, and weeks where projects collide | timelines | |
| Stale or unreadable projects | health | |
| Today's brief | brief | `_overview/brief-latest.html` |
| The week ahead | weekly | `_overview/weekly-latest.html` |
| Moving a date, finishing a task, moving a meeting | update | previews first, writes nothing until you say yes |
| Your time off | time off | `~/.familiar/time-off.md` |
| Pausing or closing a project | lifecycle | hub-owned |
| Adding, excluding or recategorizing a project | registry | hub-owned |
| First-run walkthrough | setup | runs by itself the first time |

`/ili-fleet` runs these for you when you ask in plain words. From a terminal in the hub folder:

| Script | Does |
|---|---|
| `python scripts/fleet_overview.py --discover <folder> --apply` | Find projects and register them in `~/.familiar/fleet.md` |
| `python scripts/brief.py` | Write today's brief now |
| `python scripts/weekly.py` | Write the week-ahead brief now |
| `python scripts/schedule.py enable --time 08:00 --days weekdays --print` | Preview a daily schedule; rerun with `--yes` to apply |
| `python scripts/schedule.py status` | Show what is scheduled |
| `python scripts/fleet_overview.py --set-included "<name>" no` | Keep a project out (its row stays) |

The hub keeps the registry. Nothing inside a project writes to it.

## Optional hooks

From [familiar-hooks](https://github.com/familiar-md/familiar-hooks). Hooks are set for each project.
First copy the `.familiar` folder from the hooks download onto the project. Then run
`/ili-system-settings hooks`. It lists, previews and installs the hooks for you. To do it from a
terminal instead:

| Command | Does |
|---|---|
| `python .familiar/hooks/install_hooks.py list` | List the hooks and which are on |
| `python .familiar/hooks/install_hooks.py preview <id>` | Show exactly what would change |
| `python .familiar/hooks/install_hooks.py apply <id> --yes` | Turn hooks on (`--group guards`, `--all`) |
| `python .familiar/hooks/install_hooks.py remove <id> --yes` | Turn them off again |

| Hook | Does |
|---|---|
| `session-title` | Names each Claude Code session `(<signature>) <project name>` |
| `session-title-hub` | Names a hub session `familiar hub` |
| `guard-writes` | Denies writes outside the project, into `1-Inputs/` or into `.familiar/` |
| `guard-delete` | Denies shell deletes outside the host's scratch folder |
| `guard-reads` | Denies reads outside the project |
| `guard-boundary` | Keeps maintainer tooling and project markers apart |
| `check-office` | Flags a truncated `.docx`, `.pptx` or `.xlsx` |
| `check-naming` | Flags a misnamed file in `2-Drafts/` |
| `check-citation` | Flags a knowledge page missing its citation field |

Start a new session after you turn hooks on. The guards add a mechanical check, but they are not a
guarantee or a security boundary. They run Python around every tool call. On a work computer that
your employer manages, check the rules before you install them.
