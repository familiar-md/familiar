# familiar cheat sheet

One page of commands for familiar core, the fleet hub and the optional hooks. The commands are
shown in their Claude Code form. On Codex use `$checkin` instead of `/ili-checkin`. On Gemini CLI,
ask for a skill by name ("run the checkin skill"). [`GUIDE.md`](GUIDE.md) explains each skill.

## In a project

| Command | Use it to | Branches |
|---|---|---|
| `/ili-checkin` | Reconcile project state and report health. The first run sets up a fresh project. | — |
| `/ili-ongoing-work` | See what is open and in progress. Writes nothing. | — |
| `/ili-ingest` | Turn a source document into cited notes in `3-Knowledge/`, or answer from it in chat. | — |
| `/ili-deliverable-brief` | Settle a deliverable's message, audience and outline before drafting. | — |
| `/ili-draft-document` | Build a deck, a document or a workbook, or review a team-owned Word file. | Deck, Document, Review, Workbook |
| `/ili-save` | Reconcile state before a break, or file a note or task change. | Save progress, To memory |
| `/ili-handoff` | Park work for a later session, or write a brief for someone outside the project. | Session handoff, Assignment brief |
| `/ili-triage` | Sort the work you can start today by effort or urgency. Writes nothing. | — |
| `/ili-online-research` | Research a question against outside sources, with citations. | — |
| `/ili-system-settings` | Housekeeping for the installation and the project shell. | Update, Workspace tidy, Tracks, Project closeout, Preferences, Fleet, Hooks |

Type `/ili` to list them all. Name a branch to skip the menu: `/ili-save progress`,
`/ili-draft-document deck`. Only `ingest` and `ongoing-work` may start without the command; the
assistant must wait for you to ask for every other skill. "Save progress" and "hand this off" in
plain words also work.

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
| First-run walkthrough | setup | runs by itself the first time |

| Script, run in the hub folder | Does |
|---|---|
| `python scripts/fleet_overview.py --discover <folder> --apply` | Find projects and register them in `~/.familiar/fleet.md` |
| `python scripts/brief.py` | Write today's brief now |
| `python scripts/weekly.py` | Write the week-ahead brief now |
| `python scripts/schedule.py enable --time 08:00 --days weekdays --print` | Preview a daily schedule; rerun with `--yes` to apply |
| `python scripts/schedule.py status` | Show what is scheduled |

To keep a project out, set its `included` cell to `no` in `~/.familiar/fleet.md`, or run
`/ili-system-settings` → Fleet inside the project.

## Optional hooks

From [familiar-hooks](https://github.com/familiar-md/familiar-hooks). Copy its `.familiar/hooks/`
folder into the project first. Then run `/ili-system-settings` → Hooks, or use the tool directly:

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
