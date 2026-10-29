# familiar cheat sheet

One page of commands for familiar core, the fleet hub and the optional hooks. A printable version
with a switch for your assistant is `docs/cheatsheet.html`. The commands are
shown in their Claude Code form. On Codex use `$project-status` instead of `/ili-project-status`. On Gemini
CLI, ask for a skill by name ("run the project-status skill"). [`docs/using-familiar.md`](docs/using-familiar.md#the-skills) explains each skill.

## In a project

| Command | Use it to | Branches |
|---|---|---|
| `/ili-project-status` | Check in and reconcile state (the first run sets up a fresh project), see where things stand, or sort what you can start today. | Check-in, Ongoing, Triage |
| `/ili-ingest` | Turn a source document into a cited knowledge page in `3-Knowledge/` that later sessions read instead of the original. | — |
| `/ili-deliverable-brief` | Settle a deliverable's message, audience and outline before drafting. | — |
| `/ili-draft-document` | Build a deck, a document or a workbook, or review a team-owned Word file. | Deck, Document, Review, Workbook |
| `/ili-save` | Reconcile state before a break, or file a note or task change. | Save progress, To memory |
| `/ili-handoff` | Park work for a later session, or write a brief for someone outside the project. | Session handoff, Assignment brief |
| `/ili-online-research` | Research a question against outside sources, with citations. | — |
| `/ili-system-settings` | Housekeeping for the installation and the project shell. | Update, Workspace tidy, Tracks, Project closeout, Preferences, Hooks |

Type `/ili` to list them all. Name a branch to skip the menu: `/ili-save progress`,
`/ili-draft-document deck`. Every skill waits for its command; the assistant can tell you which one
fits but never starts it. The one exception: "save progress" or "remember this" in plain words
starts `save`.

**Where things go:** sources in `1-Inputs/` (never edited), drafts in `2-Drafts/`, compiled notes in
`3-Knowledge/`, tasks and dates in `4-Trackers/`, state and memory in `5-System/`.

## In the fleet hub

Open your host in the hub folder, then run `/ili-fleet` and ask in plain words. See
[familiar-hub](https://github.com/familiar-md/familiar-hub).

| Ask about | Branch | |
|---|---|---|
| What is active, overdue and next | overview | the default |
| What you can start now | tasks | |
| The next two weeks, and weeks where projects collide | timelines | |
| Stale or unreadable projects | health | |
| Today's brief | brief | `_overview/brief-latest.html` |
| The week ahead | weekly | `_overview/weekly-latest.html` |
| Moving a date, finishing a task, moving a meeting | update | preview first, nothing written without your yes |
| Your time off | time off | `~/.familiar/time-off.md` |
| Pausing or closing a project | lifecycle | hub-owned |
| Adding, excluding or recategorising a project | registry | hub-owned |
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

The hub keeps the registry; nothing inside a project writes it.

## Optional hooks

From [familiar-hooks](https://github.com/familiar-md/familiar-hooks), per project. Copy the `.familiar`
folder from its download onto the project first. Then run `/ili-system-settings hooks`; it lists, previews and installs them for you. From a terminal instead:

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

Restart the session after applying. The guards are a deterrent, not a security boundary. They run
Python around every tool call, so check before installing them on managed work hardware.
