# familiar route registry

Read this registry after the bootstrap. Select one route, then load only the named skill and its
declared context contract. An extension route exists exactly when its skill folder is present on
disk in this host's native skill location — no separate registry lists it. A route whose skill
folder is absent is unavailable and must not be selected. Check an installed extension's own manifest —
`.familiar/extensions/<id>/package/familiar-extension.json` — for its route's `select_when` trigger text — the same role the
"Select when" column plays for the core table below — before finalizing a match: a narrower
installed extension route wins. Extension routes add entries and never replace the routes below. An
extension route's skill is `(user-only)` exactly when that skill's own `SKILL.md` frontmatter
carries `disable-model-invocation: true` — check the file directly; Resolution rule 3 applies to it
the same way it applies to a core route.

**`(user-only)`** marks a skill that only the user may start. It is never opened or run as the
result of a route match — see Resolution rule 3.

| Route ID | Select when | Canonical skill |
|---|---|---|
| `project.status` | Resume work, inspect current state, establish a fresh project, or check in | `ongoing-work` or `checkin` (user-only) |
| `project.memory` | Record progress, decisions, tasks, or durable context | `save` (user-only) |
| `project.handoff` | Pause or resume unfinished work across focused sessions, or hand a scoped piece of work to someone outside this project | `handoff` (user-only) |
| `project.research` | Retrieve project or external evidence for a task | `ingest`, or `online-research` (user-only) |
| `project.output` | Create or revise a presentation, written document, or workbook | `draft-document` (user-only) |
| `project.output` | Scope a deliverable before drafting it: its message, audience, objective, sources, or outline | `deliverable-brief` (user-only) |
| `project.schedule` | Add, edit, complete, or reschedule a task or milestone | `save` (user-only) |
| `project.schedule` | Prioritize or sort existing open work by effort or urgency | `triage` (user-only) |
| `system.maintenance` | Maintain familiar or the project shell: update, workspace tidy, tracks, closeout, preferences, fleet registration, optional hooks | `system-settings` (user-only) |

## Resolution rules

1. Explicit skill invocation wins when that skill is installed and available. The user invokes a
   skill explicitly with the host's command. `save` and `handoff` alone may also be invoked in the
   user's own words, by naming the skill or one of its branches as the thing to do now ("save
   progress", "hand this off"). A command written anywhere in the message ("…then /save progress")
   counts the same as one typed first. Any other request, including one that names another skill, is
   a route match, not an invocation, and rule 3 applies to it.
2. Otherwise select the single narrowest matching route.
3. **A route whose matching skill is `(user-only)` is never opened or run by the agent.** Identify
   which skill fits and tell the user how to start it on this host (e.g. "that's
   `triage` — start it whenever you'd like"). Name the host's own invocation form where it has one (a
   slash command such as `/triage`, a `$`-prefixed mention, or a skill picker). Where it has none, say
   the user can ask for the skill by name. Then stop. This rule lives here, in the
   host-neutral registry, rather than depending on a host recognizing any per-skill invocation-control
   frontmatter — it holds the same way on every host.
4. Otherwise, load the selected skill body before project content.
5. Follow the skill's Required, Conditional, Excluded, Updates, Capabilities, and Completion declarations.
6. A route collision — two routes, core or extension, whose "Select when" both plausibly match one
   request with no narrower rule to prefer one — is an installation error. Do not pick a winner by
   load order. This does not cover a route ID appearing more than once in the table above with
   mutually exclusive "Select when" text: those are one route with several distinct triggers, not a
   collision, and rule 2 already resolves them.
7. When no route fits, ask for direction without opening unrelated files.

## Files outside the project

A file the user names outside the project may be read for that task (`CORE-WORKSPACE-SILO`). Say once,
in the answer, that it is outside the project and nothing from it is kept here, and that copying it into
`1-Inputs/` makes it part of the project. Never write to it or copy it in unasked.

## Running familiar's scripts

`python` in any familiar instruction means Python 3.10 or newer. Use the Python in `~/.familiar/venv`
(`bin/python`, or `Scripts\python.exe` on Windows) when that folder exists; otherwise the first of
`python3`, `python`, `py` whose `--version` reports 3.10 or newer. Find it once and keep using it for
the session.

A script that cannot run is never worked around silently: when no Python qualifies, or a script stops
with "familiar needs Python" or a missing package, follow `.familiar/core/running-scripts.md`.

## Explicit-only, not routed

No skill currently sits outside the table above. When one does, list it here: it is `(user-only)`
and exists only for the user to name directly, and the agent should not propose it as the answer to
an unprompted request.

## Router skills

Four skills are **routers**: each one's body is a menu, and the procedure the user picks lives in a
reference file under that skill's own `references/` folder. Load the menu, select one branch, then
load that one file — from there the branch's own context contract governs, not the router's. A
branch is not a skill: it is never separately invocable and never opened without a selection. Because
each router carries the `(user-only)` marker, Resolution rule 3 covers every branch beneath it.

- `system-settings` holds `update`, `tidy-workspace`, `tracks`, `project-closeout`, `preferences`, `fleet`, and `hooks`.
- `draft-document` holds `deck`, `document`, `review`, and `workbook`.
- `handoff` holds `session-handoff` and `assignment`.
- `save` holds `progress` and `to-memory`.
