# familiar core — technical manual

**Baseline:** core `1.0.2` · state schema `1.0` · extension contract `1.1` · install record schema `1.1`
**Scope:** familiar **core** only, the `familiar-workspace/` folder as it ships. The extension contract
appears here as the interface that core defines. No extension is described.

This manual describes how familiar core works: each mechanism, where it lives, what enforces it, and
where it stops. [`docs/using-familiar.md`](docs/using-familiar.md) is the user guide, and
[`INSTALL.md`](INSTALL.md) has the install and update steps. If this manual disagrees with the files
in your copy, the files are right. Please report the difference.

## 1. What core is

familiar core is a memory and routing layer for coding agents. It works on several agents, and it
stays inside one project folder. It is a set of plain files:

- Markdown rules and skills
- two JSON schemas
- a ready-made entry file for each agent

All of it ships inside one folder, `familiar-workspace/`. It gives that folder a lasting memory that
is the one source of truth. It also gives the agent a fixed way to load only the instructions that
a request needs.

Three claims define core. Each one has a mechanism in the files:

1. **One home per fact.** Project state lives in named files, each with a stated update rule (§6).
   Everything else, such as reports, dashboards and briefings, is a view. A view never overrides its
   source.
2. **Load after routing, not before.** The bootstrap allows a few bounded reads at startup, for
   preferences and binding (§4.1). The agent then selects one route and loads exactly one skill and
   the context it declares (§4, §5).
3. **Never claim a capability that has not been proven.** Capability state uses five fixed values,
   and none of them implies a fallback. `active` means that a released check passed (§10).

**Core is neutral.** It ships nothing for a specific field and names no extension. The bootstrap
contains no field-specific words, and the release checks confirm this. A specialty arrives only
through the extension contract (§11), which core discovers without knowing any extension in advance.

### What core is not

- **Not a program that runs.** Core routing and memory are files that the agent reads. There is no
  install step: you copy `familiar-workspace/` and use it as it is. Document and PDF features (deck
  and document builds, PDF extraction) still need Python. Without Python, the agent tells you that
  those features do not work. It does not pretend to fall back.
- **Not an enforcement layer.** Core states rules, and the model follows them. The optional guards
  in familiar-hooks add a mechanical check that helps enforce some rules, but they are not a
  guarantee. The guards are not part of the core download.
- **Not for several writers at once.** familiar supports one active writer at a time. The
  stale-write protocol (§6.3) detects a conflict. It does not merge one.

---

## 2. Repository shape (core only)

`familiar-workspace/` is the whole product. It is one self-contained folder that you download and
use, with no install step and no build step. It ships complete: the content folders, each agent's
own skill and subagent files, and the rules, all in place.

```text
familiar-workspace/
├── AGENTS.md / CLAUDE.md / GEMINI.md   agent entry files (CLAUDE.md, GEMINI.md reference AGENTS.md);
│                                       release text sits inside <!-- familiar:start/end -->, user notes below
├── .familiar/
│   ├── routes.md, state-schema.md, extension-contract.md,
│   │   capabilities.json, extension-manifest.schema.json    protocol
│   ├── core/                           20 protocol .md files, including bootstrap.md
│   ├── scripts/                        standard-library helpers: project_check.py, doctor.py, ...
│   ├── installed.json                  core version, capability states for each agent
│   └── release-manifests/              built releases only: fingerprints of release-owned files
├── .claude/skills/                     8 skills, one folder each; .claude/agents/ holds the subagents
├── .agents/skills/                     Codex and Gemini skills, identical to .claude/skills/
├── .codex/agents/, .gemini/agents/     subagents for Codex and Gemini
├── 1-Inputs/                           Sources/, Admin/, Templates/ (read-only)
├── 2-Drafts/                           generated outputs plus _draft-index.md
├── 3-Knowledge/                        knowledge pages built from 1-Inputs/
├── 4-Trackers/                         tasks.md, timeline.md, meetings.md
└── 5-System/                           config, context, Memory/, Decisions/, Handoffs/, preferences
```

`.familiar-project` is already in the folder, with `created: not-yet-set`. Every download is
therefore a bound project as soon as you rename it and open it. The first `project-status` →
Check-in writes the real date into `created` (§4.1, §12). Check-in replaces `project-config.md` only
while that file is still the shipped stub (`revision: 0`). A project with a filled-in configuration
and an unset marker is a migrated project. Check-in brings that configuration up to date in place
and never resets it to defaults.

---

## 3. The runtime model

```text
agent entry file           AGENTS.md / CLAUDE.md / GEMINI.md
  → bootstrap              the only protocol file that is always loaded
    → startup reads        project preferences and title; optional global preferences, always
    → route registry       .familiar/routes.md, one route selected
      → one skill body     .claude/skills/<name>/SKILL.md (or .agents/skills/…)
        → required context declared by that skill, nothing else
          → conditional    loaded only when its named condition is present
```

Each arrow limits what context loads. It is a rule, not a suggestion. This chain is what makes the
agent load context step by step instead of all at once. The bootstrap has a fixed size. The registry
is a table, not a body of instructions. Each skill declares its context in a contract that the
release checks test.

**Cost.** The protocol that is always loaded is `bootstrap.md` at 500 words / 3,529 characters. That
is its ceiling. Startup also reads the bounded preference and title context (§4.1).
The route registry adds 967 words when the agent reads it, and its ceiling is 1,000 words. Everything else
loads on demand. The entry files, the registry and one skill come to a few thousand tokens. The
agent's own instructions and tools are usually several times that. Some agents show every skill
description to the model at the start. On those agents, add the description lines of the skills
that the agent shows (§10.3).

---

## 4. The bootstrap

`.familiar/core/bootstrap.md` is 500 words. Its full text is copied into `AGENTS.md`. `CLAUDE.md`
and `GEMINI.md` only reference `AGENTS.md`. The bootstrap is the only file that is always in
context, so every word in it costs tokens on every turn of every session. That is why its size has a
hard limit.

It holds exactly four things.

### 4.1 Identity and the preference read

The bootstrap opens with one paragraph on what familiar is. Then come the required startup reads,
which are bounded:

1. Find the `.familiar-project` marker before reading project state. Resolve project paths from the
   marker's folder, also when the session opens in a subfolder.
2. Before routing or project work, read `5-System/user-preferences.md`, the title of
   `5-System/project-config.md`, and the optional `~/.familiar/user-preferences.md`.

The agent reads the global file every time, not only to find a default signature. Its standing
preferences therefore apply in every project. This read is the one startup exception to
`CORE-WORKSPACE-SILO`. Project preferences win over global ones on any conflict. The global
signature applies unless the project file sets its own.

The agent then shows the signature once, as `*(<signature>) familiar bound*`. If the project title is
set, it adds `: <name>`. The line must be visible in the reply text, not only in reasoning or in a
collapsed section. If the agent cannot get a signature, it uses one of two substitutes:

- `n/a` when the signature read failed
- `not set` when both files were read but neither holds a signature

A read that the agent did not try never justifies either substitute.

The startup reads are a stated exception in `CORE-PROGRESSIVE-DISCLOSURE`. They set preferences and
binding before routing, without a required first tool call that could get in the way of finding the
marker. They do not allow reading tasks, knowledge or project history before routing. The reads are
required.

The signature **confirms that the bootstrap loaded**, and the bootstrap says so. It does not claim
that mechanical enforcement is present. The signature is only useful as a check if it is a key that
the user chose and recognizes. That is why the user sets it with `/ili-system-settings preferences`.
Check-in asks for it on the first run, and the shipped `5-System/user-preferences.md` has no
signature. A signature built into the template would make every project show the same key, and the
check would prove nothing.

The two halves of the bound line prove two different reads. The name proves that the agent read
`project-config.md`. The signature proves that it read the preferences. Each project has **its own**
signature, in its `5-System/user-preferences.md`. The global file holds only a default, which a
project shows when it has no signature of its own. A key for each project is the stronger check,
because it can only come from this project's file. It is also the project's identity outside the
session: the fleet hub labels each project's rows with it, and reports two projects that share one.

The agent reads the project file again at `voice.md` → Pre-delivery check, just before it delivers
output. There, the project file overrides the global file on any preference where they disagree.

### 4.2 The active boundary

The folder that holds `.familiar-project` is the active project. That whole folder is the boundary,
in both directions (see `CORE-WORKSPACE-SILO`).

- A file comes in through `1-Inputs/` or because the task names it. It leaves only when you ask.
- The agent can read familiar's own files inside the folder when a route needs them.
- Nothing outside the folder is in scope, and there is no exception for other projects.

You can name a file outside the folder, and the agent can read it for that task. `routes.md` → Files
outside the project then has the agent say so once. The file is outside the project, and nothing from
it is kept. If you copy it into `1-Inputs/`, it becomes part of the project.

The marker names the workspace. The agent does not assume the workspace from the folder name.
`file-handling.md` repeats this as a rule, because a project can rename its workspace folder.

### 4.3 The eleven non-negotiable rules

Each rule has a stable `CORE-*` ID. A rule can be reworded, but its ID does not change, so citations
to it stay valid.

`CORE-WORKSPACE-SILO` is one rule for both directions. The project folder *is* the project. Reads and
writes are both limited to it, and "another project" means a different folder.

| Rule | States | Failure it prevents |
|---|---|---|
| `CORE-GROUND` | Base project claims on material that was read, and outside claims on sources that can be named. A failed or blocked read is a gap. Report it, and never turn it into an inferred fact. | The agent rebuilds a file it could not read from the file name, or answers from its own memory and presents that as project fact. |
| `CORE-NO-DELETE` | Do not delete project files. Point out old material and let the user decide what to remove or archive. | Loss that cannot be undone during a cleanup. |
| `CORE-WORKSPACE-SILO` | The marker's folder is the active project and the boundary in both directions. Read and write inside it. A file comes in through `1-Inputs/` or because the task names it, and leaves only when asked. Never reach into another folder unasked. | Writes that leak outside the workspace, or context and confidential material that come in from an unrelated folder. |
| `CORE-COPY-ON-EDIT` | Do not overwrite a source in `1-Inputs/` or a draft in the workspace. Make a dated copy instead. Update the state files only when the route declares them under `Updates`. | An edit destroys a source document or a delivered draft. |
| `CORE-PLAIN-NAMES` | Talk to the user in plain words. Name each thing. Show an ID, code or version label only beside that name. | Replies the user cannot follow: chains of task IDs, gap codes and version labels that only the session knows. |
| `CORE-NO-FABRICATION` | Do not invent facts, dates, amounts, decisions, citations, paths, capabilities or completion. Say what must be confirmed. | Confident invention, including a claim that a capability works or that work is done. |
| `CORE-SCOPE` | Change only what the task needs. Do not reorganize nearby files or load unrelated history. | Unrequested cleanups and too much context. |
| `CORE-INSTRUCTIONS-READONLY` | During project work, treat familiar's installed rule and route files as read-only. Change the system only through a maintenance route that the user starts. | The agent edits its own rules in the middle of a session. |
| `CORE-PROGRESSIVE-DISCLOSURE` | Before routing, load only this bootstrap and its bounded startup reads. Then read one skill, its required context, and any context whose named condition is present. | Reading the whole project "to be safe". |
| `CORE-HUMAN-APPROVAL` | Ask before you overwrite, publish, send, install, change a status, or take another important action that the route does not allow. | Important actions with nobody watching. |
| `CORE-STALE-WRITE` | Read a state file's revision before you edit it. If the revision changed, stop, read again, and reconcile. Do not overwrite newer work. | Newer work from another session overwritten without notice. |

These rules are **instructions to a model, not code.** They are as reliable as the model's
compliance, plus whatever the optional guards add on an agent that supports hooks. Core never claims
more.

### 4.4 Route selection

This part of the bootstrap is four sentences:

1. Read `.familiar/routes.md`, or the installed core copy if the project copy is missing.
2. Select one route *before* loading detailed instructions.
3. Read that skill's body and its required and conditional context. Respect its excluded context and
   the state files it declares.
4. If no route fits, **ask the user. Do not search the system.**

The last sentence prevents the failure this design exists to avoid: an agent that gets a request it
cannot match and starts to read files to find out what it can do.

### 4.5 The budget

The bootstrap has a hard ceiling of 500 words, and it is at the ceiling. Any addition needs a cut
somewhere else. `AGENTS.md` contains the same text, copied by hand. `CLAUDE.md` and `GEMINI.md` have
no copy of their own. If you change the bootstrap, change `bootstrap.md` and `AGENTS.md` together.

---

## 5. Routing

### 5.1 The registry

The registry is `.familiar/core/routes.md`. The bootstrap reads its project copy at
`.familiar/routes.md`. The registry is a table plus seven resolution rules. It is not a set of
instructions, so it is cheap to read.

There are seven routes. `project.output` has two rows:

| Route ID | Select when | Skill |
|---|---|---|
| `project.status` | Resume work, look at the current state, set up a new project, check in, or sort open work by effort or urgency | `project-status` (user-only) |
| `project.memory` | Record progress, decisions, tasks or lasting context | `save` (user-only) |
| `project.handoff` | Pause or resume unfinished work across sessions, or hand a piece of work to someone outside this project | `handoff` (user-only) |
| `project.research` | Find project or outside evidence | `ingest` (user-only) or `online-research` (user-only) |
| `project.output` | Create or revise a presentation, written document or workbook | `draft-document` (user-only) |
| `project.output` | Scope a deliverable before drafting it | `deliverable-brief` (user-only) |
| `project.schedule` | Add, edit, complete or reschedule a task or milestone | `save` (user-only) |
| `system.maintenance` | Maintain familiar or the project folders: update, workspace tidy, tracks, closeout, preferences, optional hooks | `system-settings` (user-only) |

There is no route for all projects together. `project-status` → Triage covers one project, like
every other skill. The view across projects is the separate fleet hub (§6.4).

A route ID on more than one row is **one route with several triggers**, not a duplicate. Rule 6 says
so. `project.output` has two rows because drafting a deliverable and scoping one first are different
triggers.

### 5.2 Resolution rules

1. An explicit skill command wins when that skill is installed and available. The user starts a skill
   with the agent's command, anywhere in the message. Only `save` can also start from the user's own
   words ("save progress", "remember this"). Any other request is a route match, also when it names
   another skill, and rule 3 applies. Every other skill starts only from its command.
2. Otherwise, select the single narrowest route that matches.
3. **The agent never opens or runs a route whose skill is `(user-only)`.** It names the skill that
   fits and tells the user how to start it on this agent. That is the agent's own form where there
   is one: a slash command, a `$` mention, or a skill picker. Where there is none, it is a plain
   request by skill name. Then the agent stops. §5.3 has the details for each agent.
4. Otherwise, load the skill body before any project content.
5. Follow the skill's Required, Conditional, Excluded, Updates, Capabilities and Completion
   declarations.
6. A real collision is two routes whose triggers both match, with no narrower rule between them. It
   is an **installation error**. Load order does not settle it.
7. If no route fits, ask, and do not open unrelated files.

### 5.3 `(user-only)` and why it lives in the registry

All 8 core skills have `disable-model-invocation: true` in their frontmatter, so 0 of them are
model-invocable. The agent can name the skill that fits, but only the user starts one. Claude Code
respects this frontmatter. Each `(user-only)` skill also ships an `agents/openai.yaml` with
`allow_implicit_invocation: false`. Claude Code and Codex therefore both report
`user-invocation-control: active`. On Gemini CLI, the control is an instruction only: every skill
description can reach the model there.

**Starting a skill differs by agent.**

- **Claude Code:** a skill is a slash command, such as `/ili-project-status`. Each
  `.claude/skills/<skill>/SKILL.md` sets `name: ili-<skill>`, so the `/` menu lists every familiar
  skill under `/ili`. The folder name also starts it (`/project-status`). The `.agents/` copy keeps
  `name: <skill>`. This is the one planned difference between the two copies.
- **Codex:** a `$` mention (`$project-status`) or the `/skills` picker.
- **Gemini CLI:** there is no command for each skill. The model starts a skill after the user
  confirms, so ask for it by name ("run project-status").

Rule 3 is therefore one sentence that means a different action on each agent. On an agent with no
command, the user's plain request starts the skill. Use the form that your agent documents. The
skill content is the same on all three.

> **Put the command first** (`/ili-online-research <question>`, `$project-status`). Every agent
> documents this form. A command at the end or in the middle of a sentence often works, but not
> always. If the agent does not expand it, it arrives as plain text. A `(user-only)` skill is hidden
> from the model, so the agent can then only report that it found no such skill, and it answers
> without a route. If a skill did not start, send the message again with the command first. `save`
> in plain words is the planned exception (§5.2 rule 1).

Rule 3 lives in the registry text itself. It does not depend on an agent that reads skill
frontmatter, so the promise is the same on every agent. The release checks confirm that the
registry's `(user-only)` labels match the real frontmatter, and that every skill can be reached.

### 5.4 Explicit-only, unrouted

This list is empty: the table above reaches every core skill. The category exists for a skill that
is too important or too narrow to start from a route match. Such a skill would be listed here and
started only by the user.

### 5.4a Router skills and branches

Five core skills are **routers**: `project-status`, `system-settings`, `draft-document`, `handoff`
and `save`. Each router's body is a menu. Each option on the menu is a procedure file under the
router's own `skills/<router>/references/`. The router loads exactly one of them after the user
picks.

From that point, the branch's own context contract applies. Its Required, Conditional, Excluded,
Updates, Capabilities and Completion declarations replace the router's, which covered only the menu.
A run therefore loads the menu plus one procedure. That is the same budget as one skill started
directly.

| Router | Branches |
|---|---|
| `project-status` | `check-in`, `ongoing`, `triage` |
| `system-settings` | `update`, `tidy-workspace`, `tracks`, `project-closeout`, `preferences`, `hooks` |
| `draft-document` | `deck`, `document`, `review`, `workbook` |
| `handoff` | `session-handoff`, `assignment` |
| `save` | `progress`, `to-memory` |

One branch writes outside the project. `preferences` writes `~/.familiar/user-preferences.md`, and
only when the user asks. Its contract declares this as the exception to `CORE-WORKSPACE-SILO`. No
project skill touches `~/.familiar/fleet.md`. The fleet hub, which ships on its own, creates and keeps
that list. `fleet_overview.py --discover <dir> --apply` adds projects. `--set-included`,
`--set-category` and `--set-lifecycle` each change one row. These are scripts, so they work the same
on every agent.

Two properties keep routers safe within the routing model:

- **Rule 3 covers every branch.** Each router has `disable-model-invocation: true`. A route match
  therefore never opens a router, and never reaches a branch under it.
- **The release checks cover branches.** Each branch with a context contract gets the same checks as
  a skill.

A branch is not a skill. It has no frontmatter, no route and no slash command. The agent opens a
branch only after the user picks it from the menu.

### 5.5 Extension routes

There is no separate list of extensions. An extension route exists exactly when its skill folder is
on disk, in this agent's skill folder, with the extension's own `familiar-extension.json` manifest.
The agent checks for it **before** it settles on a match from the core table. A narrower installed
extension route wins. The agent opens its skill body only after it selects the route.

Extension routes add entries and never replace core routes. Each one has its own `select_when`
trigger, which plays the same role as the core table's "Select when" column. The manifest schema
requires it from contract `1.1`. An extension skill is `(user-only)` exactly when its own `SKILL.md`
has the frontmatter marker. Rule 3 then applies to it in the same way.

---

## 6. The state model

`.familiar/core/state-schema.md` defines schema version `1.0`. A generated report is a view. It is
never another source of truth.

### 6.1 Authoritative surfaces

| Surface | What it holds | How it changes |
|---|---|---|
| `5-System/project-config.md` | Stable settings, workspace path, schema version, installed extensions, capability record | In place, through setup or maintenance only |
| `5-System/project-context.md` | Background, objectives, stakeholders, lasting constraints | In place, for important lasting changes only |
| `5-System/Memory/status-snapshot.md` | Current phase, blockers, next actions, latest revision | Replaced whole, in one step |
| `5-System/Memory/status-log.md` | Important events in date order | Append only |
| `4-Trackers/tasks.md` | Action, owner, status, due information, blockers | In place, by task routes |
| `4-Trackers/timeline.md` | Milestones and dates | In place when a date moves |
| `4-Trackers/meetings.md` | Planned internal and client meetings: series rules, single meetings, moves and cancellations by date, and each meeting's agenda (optional) | In place. Rows are never deleted. |
| `5-System/Decisions/*.md` | Approved decision, reasons, date, consequences | A new record. Changes keep the history. |
| `5-System/Handoffs/*.md` | Temporary instructions for the next session on unfinished work | A new record. Its status can change in place. |
| `5-System/user-preferences.md` | How the user wants familiar to work in this project | In place. The referencing method is set once, on the first Word draft that cites. Everything else changes through `save` → To memory only. A signature for this project only is a hand edit. The shared signature is in `~/.familiar/user-preferences.md`, written by `system-settings` → Preferences. |
| `5-System/notes.md` | Loose notes that fit no other file | Append or in place, through `save` → To memory |

`5-System/Memory/save-progress.md`, overview reports, briefings and dashboards are **views that can
be rebuilt**. They never override the files above.

### Freshness and session provenance

Knowledge pages record `last_verified` and `review_by`, and the index shows both. The check-in
health check reports pages past their `review_by` date. It does not rewrite project knowledge on its
own. An agent's own built-in memory is not a source of truth and never overrides these files.

Core does not keep a log of every model session. The model name and effort setting are operating
details, not project facts. Record them only as provenance for important research, decisions or
deliverables.

### 6.2 Required metadata

Every state file that changes opens with:

```text
<!-- familiar-state-schema: 1.0 -->
<!-- revision: <non-negative integer; 0 is an unwritten scaffold> -->
<!-- last-updated: <ISO-8601 timestamp or date> -->
```

The activity log is append-only and uses no revisions. Entries go from oldest to newest. Each entry
has its own date and the task or decision IDs it affects.

### 6.3 The stale-write protocol

Before a route writes, it records the revision it read. The new version adds one to the revision. If
the revision on disk is no longer the one the route read, `CORE-STALE-WRITE` applies: **stop, read
again, reconcile, and report the conflict.** Do not overwrite. Where the agent supports it, write to
a temporary file beside the original and then replace the original in one step.

This protocol *detects* conflicts, and only some of them. It catches a second writer that also
follows the protocol. It does not lock, merge, or stop a writer that ignores it. familiar supports
one active writer at a time.

It also does not work across a synced folder, which is the case you are most likely to hit. The
revision check reads the local disk. OneDrive, SharePoint, Dropbox, iCloud Drive and similar apps
sync *after* a write. Two computers can both read revision 3 and both write revision 4, and neither
check stops them. The sync app then keeps the last write, or makes a conflict copy.

The conflict-copy check knows these name patterns:

- a computer name added to the file name
- "conflicted copy"
- iCloud Drive's `name 2.md` form (a space and a number before the extension)

A conflict copy lands inside the project folder. `CORE-NO-DELETE` forbids the agent to remove it,
and a later read could mistake it for the real state. `file-handling.md` therefore requires a check
for a conflict copy before each write, and a stop and report when the agent finds one. That check is
the only part of this that familiar can enforce. The rest is a limit on how you work, described in
`INSTALL.md` → *Synced folders and concurrent use*.

### 6.4 No cross-project exception

`CORE-WORKSPACE-SILO` has no exception for other projects. The workspace folder is a hard boundary
in both directions. The agent never reads anything in another project, and never writes outside the
active workspace.

A project never reads another project. The view across projects is the fleet hub. It is a separate
folder, outside every project, that reads each registered project as data and keeps its own list
(§5.4a). Nothing inside a project can name another project to read from.

### 6.5 Extension state surfaces

An extension declares its own state files. Each one is an object with four fields:

- `path`: relative to the workspace, never a plugin-cache path
- `schema_version`: the extension's own version, separate from core's `1.0`
- `update_behavior`: plain text, in the style of the table above
- `scaffold`: whether the extension's folder already includes the file

A scaffolded file ships at revision `0` with the extension's schema version. Adding the same
extension again later never replaces it. Package files are replaced. State files are not.

---

## 7. The workspace

The folder ships already set up. Nothing copies a template into a new project. The workspace,
including `.familiar-project`, ships filled in as far as it can be without project facts. On its first
real run, `project-status` → Check-in writes the project's own facts into the remaining stub files
(§4.1, §12).

```text
familiar-workspace/
├── .familiar-project                   ships with created: not-yet-set; check-in stamps it on the first run
├── .familiar/
│   ├── routes.md, state-schema.md, extension-contract.md,
│   │   capabilities.json, extension-manifest.schema.json    protocol
│   ├── core/                           every core .md
│   ├── installed.json                  core version, capability states for each agent
│   ├── extensions/<id>/package/        each installed extension's package, if there are any
├── 1-Inputs/                           Sources/, Admin/, Templates/ (read-only)
├── 2-Drafts/                           generated outputs plus _draft-index.md
├── 3-Knowledge/                        index with review dates, knowledge pages
├── 4-Trackers/                         tasks.md, timeline.md, meetings.md
└── 5-System/                           config, context, Memory/, Decisions/, Handoffs/, preferences
```

`file-handling.md` sets what each folder owns:

- `1-Inputs/` is source material, and it is read-only.
- `3-Knowledge/` holds the knowledge built from those sources.
- `2-Drafts/` holds outputs that wait for review.
- `4-Trackers/` and `5-System/` hold the project state.

A project can rename the workspace folder. The agent finds it from the marker and never assumes it
from the folder name. A project cannot quietly change what these folders mean.

Every folder ships an `_about.md` that says what the folder owns. An agent that lands in the folder
without the rules loaded can still understand the layout.

---

## 8. Skills

### 8.1 The context contract

Every `SKILL.md` declares six fields:

| Field | Meaning |
|---|---|
| **Required context** | What the skill must read to work at all. |
| **Conditional context** | What it loads only when a *named condition* is present. |
| **Excluded context** | What the skill must not open. |
| **Updates** | Which state files the skill can write in place. |
| **Capabilities** | Which capabilities it needs, from the fixed vocabulary. |
| **Completion** | The outcome that means the skill is done. |

The release checks confirm these points for every skill and every branch:

- All six fields are present, once each, with real content. Each skill has its own Completion text,
  stated as an outcome.
- No file is both required and conditional, or both required and excluded. A file in both lists
  would make the contract say nothing.
- The capability names come from `capabilities.json`.
- A skill whose Updates field says "nothing" does not declare `file-write`. In core, the one recorded
  exception is `online-research`, which saves a file only when the user asks.

### 8.2 The 8 core skills

**Model-invocable (0)**: none. A route match names the skill that fits and stops (§5.2 rule 3).

**User-only (8)**: a route can name them, but the agent never starts them:

| Skill | Purpose |
|---|---|
| `project-status` | Status menu. Routes to `check-in`, `ongoing` or `triage` (§5.4a). |
| `ingest` | Turn one approved source into a page in `3-Knowledge/`. |
| `online-research` | Research from outside sources, without the check of the project's own library first. |
| `system-settings` | Housekeeping menu. Routes to one of six branches (§5.4a). |
| `deliverable-brief` | Scope a deliverable in `2-Drafts/<slug>/_brief.md` (core message, argument, headline outline), then lock it for `draft-document`. It starts from a matching profile (global, in `~/.familiar/brief-profiles/`, or an extension's `brief-profiles/`). A profile is built on request from the user's own examples. It also reads project state and knowledge, without changing them. |
| `draft-document` | Deliverable menu. Routes to `deck`, `document`, `review` or `workbook` (§5.4a). |
| `handoff` | Handoff menu. Routes to `session-handoff` or `assignment` (§5.4a). |
| `save` | Memory menu. Routes to `progress` or `to-memory` (§5.4a). |

**Branches (17)**: these are procedures, not skills. They have no frontmatter, no route and no slash
command. You reach them only through their router's menu.

| Router | Branch | Purpose |
|---|---|---|
| `project-status` | `check-in` | The regular check-in: a first draft from state, then reconcile and health check. Sets up a new project on its first real run (§4.1, §12). |
| `project-status` | `ongoing` | A read-only query: what is open right now. |
| `project-status` | `triage` | Sort this project's open work by effort or urgency. Read-only. |
| `system-settings` | `update` | Update core or chosen extensions without touching other components' files. |
| `system-settings` | `tidy-workspace` | Survey old workspace files, propose a cleanup, and move files after approval. |
| `system-settings` | `tracks` | The whole life of a track: propose, add, split, merge, retire. |
| `system-settings` | `project-closeout` | Reconcile the final state and write a closeout summary. |
| `system-settings` | `preferences` | Set this project's signature (in `5-System/user-preferences.md`), the default signature, and standing preferences (in the global `~/.familiar/user-preferences.md`). |
| `system-settings` | `hooks` | Turn the optional familiar-hooks on or off. |
| `draft-document` | `deck` | Build or revise a presentation. |
| `draft-document` | `document` | Create or revise a written document (`.docx`, or Markdown when Word builds are not possible). |
| `draft-document` | `review` | Tracked changes and comment replies on a Word file that the team owns (`tracked_edit.py`). |
| `draft-document` | `workbook` | Plan, build and check an Excel deliverable. `xlsx_check.py` names what a round trip through openpyxl would drop, and what a new version lost. |
| `handoff` | `session-handoff` | Park or resume unfinished work across sessions. |
| `handoff` | `assignment` | Write a self-contained brief for someone with no access to this project. |
| `save` | `progress` | Reconcile every track before a break. Writes no new file. |
| `save` | `to-memory` | Send a note to the right memory file. |

### 8.3 Procedure files

Long procedures live in `.familiar/core/`. They load only when a skill names them, so skill bodies
stay short:

| File | Loaded by | Contents |
|---|---|---|
| `check-in.md` | `project-status` → Check-in | Read state → draft the changes → reconcile → health check → close |
| `ingest.md` | `ingest` | Read mode and ingest mode, the size check and bulk ingest, the ingest procedure, source dates and conflicts, privacy and failure |
| `status-format.md` | memory and track skills | Memory file formats, read order, update rules, decision records |
| `handoff-format.md` | `handoff` → Session handoff | What a handoff is for, one file per thread, the four status values, the template, writing and reading one |
| `deck-rules.md` / `deck-build.md` | `draft-document` → Deck | Template order, template inventory and brand rules, the headline test, visual design, content and bullet rules, checks and delivery; the build procedure |
| `docx-rules.md` | `draft-document` → Document, when it applies | Word document content, copies, build and checks |
| `calendar-rules.md` | `save` → To memory, `project-status` → Check-in | Timeline and memory as the only source of truth, the order of updates, safeguards |
| `familiar-behavior.md` | any route that needs project-lifecycle guidance | Neutral project-lifecycle behavior. It is *not* a startup checklist. |
| `voice.md` | a skill that writes prose, and on its own for a routed chat reply | §9 |
| `plain-language.md` | written output longer than a chat reply | §9 |
| `familiar-voice.md` | only when the project configuration turns it on | Optional companion voice |
| `retrieval-fallback.md` | when `named-subagents` is not `active` | §10.2 |
| `running-scripts.md` | only when a script cannot run | What to do when Python or a package is missing |

`_index.md` maps which file loads when.

---

## 9. The writing and output layer

### 9.1 Two files: judgment and spec

**`voice.md`** is the part that a script cannot check. A skill loads it when it writes prose, and it
governs a routed chat reply on its own. It asks for clear, direct language at the user's level.
familiar has *no* fixed industry, profession or formal register. The main points are:

- Lead with the outcome.
- Use concrete nouns and active verbs.
- Keep confirmed fact, interpretation from a source, open question and recommendation apart.
- Keep uncertainty where the evidence is uncertain.

Its avoid-list bans generic scene-setting, inflated claims, fake quotations, rhetorical questions as
decoration, and claims that work is done before the checks ran.

Its **Audience** section decides who a deliverable's body text speaks to. The writer confirms the
reader before writing (`document.md`/`deck.md` step 1). For an outside reader, the text may not:

- name the project files or the retrieval system as the evidence
- credit a finding to generic "sources" instead of the study or guideline
- report the document's own drafting or confirmation status in the text
- explain an editing choice to the reader
- cite the project's own unfinished draft

The test is who the sentence speaks to, not a list of banned phrases. An internal working draft is
exempt.

Its **Uncertainty marker** section defines two bracket markers:

- `[verify]` for a claim that has no source yet or is not confirmed
- `[action: ...]` for an instruction to the drafter, a task rather than a claim in question

Both counts must reach zero before an outside delivery. In a `.docx` or `.pptx` built with
`document-tools`, each marker gets its own colored, italic run (`docx-rules.md`/`deck-rules.md` →
Editor notes). It does not stay as plain bracket text in the body font.

**`plain-language.md`** is the part that can be counted. A skill loads it only when it writes
something longer than a chat reply. It first picks the **shape** from the type of content, not from
the audience:

| Shape | Rules |
|---|---|
| Operational | Commands, one instruction per sentence, 20 words |
| Full-prose deliverable | Paragraphs, structure rules only, 25 words |
| Deck | Fragments, length and word rules only |
| Chat reply | `voice.md` only |
| Persuasive text | Exempt |

The shape decides which sentence rules apply. Then come the rules: verb tenses, modal verbs, one
word per meaning, filler to delete, a self-check, and a section that states the rules' own limits.

**Why the split is where it is.** You apply `voice.md` by thinking, and `plain-language.md` by
searching the draft. Only the second can be checked, so only the second is worth its load cost at
the moment of writing. The shape choice lives in `plain-language.md`, beside the rules it selects.

**Why an aerospace standard.** "Write clearly" is an opinion, and models do not act on opinions. "No
sentence over 20 words" is a spec, and models do act on specs. ASD-STE100 was written so that a tired
reader who is not a native English speaker cannot misread an instruction. The same rules remove the
signs of AI-written prose: long sentences, rotating synonyms, hedging, decorative clauses. The spec
and `voice.md`'s banned list therefore support each other without repeating each other.

### 9.2 The pre-delivery check

Before output governed by `voice.md` goes out, the agent checks six things:

1. The requested outcome is present and easy to find.
2. Claims have the grounding that the task needs.
3. Unknowns and assumptions are visible.
4. No dates, names, amounts, citations or paths were invented.
5. The shape matches the project configuration, the project's `user-preferences.md`, and the
   audience.
6. The remaining `[verify]` and `[action: ...]` tags are counted and reported. Output that leaves the
   project needs zero.

Paths, versions and provenance are covered by `file-handling.md` (§9.3), not by this check. What a
skill must not read is in each skill's **Excluded context** field.

### 9.2.1 How the rules reach each write

Every skill that declares `file-write` requires `file-handling.md`. Source protection, naming,
versions and provenance therefore apply to every write. Skills that write a deliverable, knowledge
page, review, brief or other prose also declare `voice.md` and `plain-language.md`. They declare
them as required context, or behind the exact branch that writes prose. Skills that only maintain
state load the state rule that applies instead, such as `status-format.md`, `state-schema.md` or
`check-in.md`.

This keeps a tracker or metadata edit from loading the full prose spec, and file safety and state
formats stay required. The release checks confirm that every skill that writes files loads
`file-handling.md`, plus either the writing rules or a state format. The six-field contract stays the
one statement of what a route can load.

The project's `user-preferences.md` is read at startup (§4.1). It is read again through `voice.md`
just before written output, where its content can change the result.

### 9.3 File handling, naming, provenance

- New output for you to review is named `YYYY-MM-DD_<short-description>_<status>_vN.<ext>`, with
  status `DRAFT`, `REVIEW` or `FINAL`. Each revision adds one to the version. `final-final`, `new` and
  overwriting the source file name are not version control.
- State files keep stable names and use revisions instead. Activity logs are append-only.
- An output based on project sources cites the source path and a useful locator. An output based on
  outside sources carries the original URL, the date it was read, and the narrowest locator
  available. A gap in retrieval is recorded as a gap.
- Generated knowledge and review outputs record the skill that made them, the date, and the installed
  component version. For an extension, that is its full namespaced ID.
- Office documents are ZIP packages. Before the agent reads or delivers a `.docx`, `.pptx` or
  `.xlsx`, it checks for a readable central directory and `[Content_Types].xml`. A renamed or cut-off
  archive is not a valid Office document.
- Nothing is published, sent or moved outside the workspace without your approval.

### 9.4 The optional companion voice

`familiar-voice.md` is flavor only. familiar works the same with it off, and **no rule or guard
depends on it**. It acts only on something the agent notices without being asked: a date that moved,
a logged decision about to be contradicted, a track gone quiet, or a relevant memory nobody asked
for. It shows as an italic line that starts with the signature key. It never applies to a guard
message, a system message or anything inside a deliverable. It uses italics only when the agent
reports that it can show Markdown formatting.

### 9.5 Document building, and its limits

`deck` and `document` ship real build scripts that work on any agent:
`skills/draft-document/scripts/build_pptx.py` and `skills/draft-document/scripts/build_docx.py`. They
use `python-pptx` and `python-docx`, which are ordinary open-source libraries. They are not a copy of
any vendor's document skill. Each script supports `--health-check`, `--build`, `--validate` and
`--render`.

Two more scripts sit beside them in `skills/draft-document/scripts/`:

- `xlsx_check.py` (standard library only) lists what a workbook holds and compares two versions.
- `office_render.ps1` (Windows PowerShell 5.1) opens a deck, document or workbook in the real Office
  application, read-only and with a time limit, for the final check. For a deck, it makes slide PNGs
  and a PDF. For a document, it opens the file and counts pages, tracked changes and comments. For a
  workbook, it recalculates and counts formula errors.

Where Office is installed, its render is the one that counts. A LibreOffice render is labeled as
LibreOffice only.

Both build scripts look for LibreOffice's `soffice` on `PATH` first. Then they look in the default
install folders, which are not on `PATH` by default:

- the macOS app bundle (`/Applications/LibreOffice.app/Contents/MacOS/soffice`)
- `Program Files` on Windows
- the common Linux paths (`/usr/lib/libreoffice`, `/opt/libreoffice*`)

A default install is therefore found with no setup.

**Preflight.** `.familiar/scripts/doctor.py` is a preflight for this toolchain. It uses only the
standard library and runs on Windows, macOS and Linux (with `python3`, `python` or `py`). It checks
the Python version, the `python-docx` and `python-pptx` packages, LibreOffice (with the same search
as the build scripts), pandoc, and the optional extraction tools. For each gap, it prints what is
missing, what breaks without it, and the command that fixes it on that computer. Where the system
Python blocks `pip` (PEP 668), that command uses a virtual environment at `~/.familiar/venv`. The
preflight exits `0` when every required check passes. It avoids newer syntax so that it can still
run on an older Python and report it. It changes nothing.

Every other shipped script starts with a check that stops on a Python older than 3.10, with a plain
message instead of a traceback. `routes.md` → Running familiar's scripts tells the agent how to pick
the interpreter. `running-scripts.md` tells it when to offer an install.

**`document-tools` is recorded as `available`, never `active`, on every agent.** Nothing checks the
toolchain at install time, and the capability table is written by hand. Both procedure files
therefore run the script's own `--health-check` at the start of every build and report the real
result. A visual check needs LibreOffice's `soffice` (found as above). Without it, the build reports
`"visual_validation": false` and does not skip the check without telling you. `deck` has no fallback
without the visual check, and it must say so. `document` falls back to Markdown. On an agent with no
Python, this is a real gap, and familiar does not hide it.

**Citations and Word files that the team owns.** A Word draft cites in two colored layers, back to
back (`docx-rules.md` → Editor notes → Dual citation):

- teal `reference` for the compiled document that a statement came from
- purple `primary-reference` for the underlying study

Only the purple layer ever becomes a reference-manager field, and only through an installed citation
extension. Core drafts the tags and never writes those fields. A draft with citations that leaves the
project gets a Markdown `_trace.md` file beside it, with one row per cited statement. Before each
handoff, the claims check grades each row *primary verified*, *compiled source* or *unsupported*.
The project's `Referencing method` (`none | manual | extension`) is in
`5-System/user-preferences.md`. The Document branch asks for it once. It changes only how the final
version is made, and how a tracked review treats existing fields.

When a deliverable becomes a file that the team edits, the `review` branch takes over from
`document`. `build_docx.py --revise` cannot write tracked changes, and it rebuilds the text it
touches. `scripts/tracked_edit.py` is therefore the only editor for such a file. It only adds:

- Every edit is a `w:ins`/`w:del` or a comment by "AI Review".
- Replies go under the parent comment.
- It leaves fields, hyperlinks and other authors' tracked text untouched.
- It refuses to reply to comments addressed to the client (`Note to ...`).
- `--apply` applies all edits or none.

`--check` proves that a pass was safe. If you reject every AI change, you get the source back, and
everything from the source is identical byte for byte. This has been tested on a hand-built test
file, not yet on a file written in Word.

`deck` ships **no** brand or neutral presentation master, and there is no shared template library on
the computer. `deck-rules.md` uses this order: the template that you choose, then a template for this
project that you placed in `1-Inputs/Templates/`. If neither exists, `deck` reports that it is
unavailable. It does not invent a brand or a neutral master.

---

## 10. Capabilities, hosts, and delegation

### 10.1 The vocabulary

`.familiar/capabilities.json` defines thirteen capability names and five states. Both lists are
fixed:

```text
project-instructions   explicit-skills      implicit-skills     user-invocation-control
named-subagents        mechanical-enforcement                   file-read
file-write             document-tools       background-work     authenticated-knowledge
external-retrieval     hosted-publication
```

| State | Meaning |
|---|---|
| `active` | The released version exists and its health check passed. |
| `available` | Possible, but it still needs separate setup or a live check. |
| `unsupported` | The agent cannot do this. |
| `unavailable` | Possible in principle, but not present here. |
| `unknown` | Not determined. |

**No state implies a fallback.** This vocabulary exists to prevent two failures: reporting
`available` as if it were `active`, and describing a fallback that does not exist. The release checks
confirm that the table uses only these names and states, and that `document-tools` is never
`active`.

### 10.2 Delegation and its fallback

Core ships two subagents:

- `lookup` finds material in `3-Knowledge/`. It returns exact quotes with citation anchors and a
  coverage report, never conclusions.
- `web-lookup` does the same on the open web, from primary sources. It returns the URL and the date
  read, and one of three results for each item.

An optional extension can ship more subagents under its own namespace. This manual covers core only.

The split is the point. Retrieval subagents return quotes and gaps, and the calling skill does the
reasoning. A subagent cannot slip an inference into the answer, because it does not produce answers.

Before it hands work to a subagent, `bootstrap.md` checks the agent's `named-subagents` state. If the
state is not `active`, the agent loads `retrieval-fallback.md` and does the subagent's work itself.
An agent with no row in `installed.json` always falls into this case (see "Agents not listed"
below). Retrieval then uses the main context. A review from several perspectives becomes a series of
personas in one context, so **the perspectives are not independent, and the delivery must say so.**

### 10.3 The three adapters

| Capability | claude | codex | gemini |
|---|---|---|---|
| `project-instructions` | active | active | active |
| `file-read` / `file-write` | active | active | active |
| `explicit-skills` | active | active | active |
| `implicit-skills` | active | active | active |
| `user-invocation-control` | **active** | **active** | unsupported |
| `named-subagents` | **active** | **active** | **active** |
| `mechanical-enforcement` | available | available | available |
| `document-tools` | available | available | available |
| `background-work` | available | available | unknown |
| `authenticated-knowledge` | unknown | unknown | unknown |
| `external-retrieval` | available | unknown | unknown |
| `hosted-publication` | available | unsupported | unsupported |

**Entry files.** `CLAUDE.md` is for Claude Code, `GEMINI.md` for Gemini CLI, and `AGENTS.md` for
Codex. `AGENTS.md` is also written for Claude Code and Gemini CLI. `CLAUDE.md` and `GEMINI.md` only
reference `AGENTS.md` and add no rules of their own, so the bootstrap text has one home.

**Skills and subagents.** Skills go in `.claude/skills/<name>/` for Claude Code and in
`.agents/skills/<name>/` for Codex and Gemini CLI. Subagents ship as `.claude/agents/*.md`,
`.codex/agents/*.toml` and `.gemini/agents/*.md`, each in that agent's own format. On Codex and
Gemini CLI, subagents use the current model and name no Claude model. Skills call a subagent by its
project-level name. For an extension, that name is `<namespace>-<agent>` (§11.3).

`INSTALL.md` → Host support compares the three agents for users. `docs/using-familiar.md` covers how
to start skills on each one.

**Agents not listed.** Other coding agents read `AGENTS.md`, for example Cursor, GitHub Copilot in VS
Code and OpenCode. The bootstrap loads there, but `installed.json` has no row for them. The rule in
`extension-contract.md` is that an agent with no row treats every capability as `unknown`. It does
subagent work itself, through `retrieval-fallback.md`. Before it runs an extension route, it says
that the route is not tested on this agent and asks the user. Some of these agents read both
`.claude/skills/` and `.agents/skills/`, so each skill can appear twice in their pickers. The two
copies are the same.

---

## 11. The extension contract, as core defines it

Core discovers extension manifests without knowing any extension in advance, and contains no
extension ID. The contract is version `1.1`. Each extension has a UTF-8 JSON manifest named
`familiar-extension.json` at the root of its package. `extension-manifest.schema.json` is the
authority for machine checks, and `extension-contract.md` is its prose companion.

### 11.1 Manifest shape

Required fields: `contract` (always `1.1`), `id`, `display_name`, `version` (semver), `core` (a
compatible version range), `type` (`workflow` | `specialty` | `enforcement` | `integration`),
`namespace`, `contributions`, `capabilities`, `unavailable_behavior`, `package`. Optional fields:
`compatible_with`, `conflicts`.

`contributions` requires four arrays: `routes`, `skills`, `agents` and `state_surfaces`. It allows two
more arrays for project-lifecycle pieces, `checkin_fragments` and `track_presets`. Each is a list of
file paths relative to the package. A route is an object with `id`, `skill` and `select_when`. A state
surface is the four-field object in §6.5.

`capabilities` requires `required` and `optional` arrays. `unavailable_behavior` is `hide`, `degrade`
or `report-unavailable`. It applies when an *optional* capability is missing. `package` requires
`update_source`.

There is no separate list of extensions. An extension exists exactly when its skill folder is on disk
in an agent's skill folder, with its own `familiar-extension.json` manifest. A route's `host_status`
is therefore worked out when it is read. The agent compares the manifest's required and optional
capabilities with the table in `.familiar/installed.json`. The result is not stored anywhere.

### 11.2 What validation enforces

**Nothing checks an extension when you add it.** There is no installer or validator at run time
(§12). Adding an extension is a plain folder merge.

If you build an extension from familiar-template, work through the template's
`CONTRACT-CHECKLIST.md`, and run its `check_extension.py` where the template includes it. Core runs
no check on it.

The agent evaluates capabilities for each agent and records the result under `host_status`. If a
required capability is missing, the extension is unavailable on that agent. If an optional
capability is missing, `hide`, `degrade` or `report-unavailable` applies. The bootstrap checks this
status before it selects an extension route.

Core route IDs are reserved. The order in the registry decides only the display order. It never lets
one route override another.

### 11.3 Namespacing and materialization

A plugin-scoped subagent `<namespace>:<agent>` appears in a project as `<namespace>-<agent>`. No tool
renames it when you add the extension. Each extension's folder ships with the names already in this
form:

- Subagent files are named `<namespace>-<agent>` in every agent's subagent folder.
- Their frontmatter `name:` matches.
- The skills call them by that name.

### 11.4 Layout and removal

An extension's folder holds its package at `.familiar/extensions/<id>/package/`. Its skills and
subagents are already in each agent's own folders. To add it, merge that folder onto the project
root. No list records this. The files on disk and the package's own manifest are the record.
`.familiar/installed.json` still records the capability state for each agent.

To remove an extension, delete the paths that its `_about.md` lists. Nothing checks whether you
edited one of those files, so look before you delete.

---

## 12. Update and extension lifecycle

A new project has no install step. `familiar-workspace/` ships complete:

- the rules
- each agent's own skills and subagents
- the empty content folders
- a filled-in `.familiar-project` (`created: not-yet-set`)

You get a working project when you rename the folder and open an agent inside it. The first time
`project-status` → Check-in runs, it writes the real date into `created` and asks for a
`Project Name` (§4.1, §8.2). It also asks for a signature if the project has none, which
`/ili-system-settings preferences` can also set. No script sets up a project, and nothing is
compiled.

One script updates a project: `.familiar/scripts/update.py`. `system-settings` → Update runs it from
a session, so most users never open a terminal. You can also run it from a terminal (§12.1).
`system-settings` → Update (§5.4a) is the only route for updates. You start it yourself. It never
starts from a route match, because the whole `system-settings` menu is `(user-only)`.

### 12.1 What Update does

**Update runs the updater after your yes.** `references/update.md` reads the project's version from
`.familiar/installed.json` → `core.version` and from the marker. It reads the new release's version
from its `VERSION` file. It also reads `core.build` from both `installed.json` files. A release
build writes into `core.build` the commit it came from, with `-dirty` if that commit had
uncommitted changes. The comparison works like this:

- A newer version is an update.
- The same version with a different build is also an update.
- If the build is missing, Update cannot decide. It reports that, and you choose.

Update then compares the `state-schema` lines, because a difference means a migration, which no
procedure performs. Then it runs the new release's `update.py` against the project in report mode,
and explains the report. After your yes, it runs the updater with `--apply` and reads the result
back.

The release folder is one that you named, read for this task only (`routes.md` → Files outside the
project). The updater makes every write, and only inside the project. If the agent cannot run the
command, the branch gives it to you with both paths filled in. A project without
`.familiar/release-manifests/familiar.json` goes to the hand procedure in `INSTALL.md` → Updating. That
procedure starts a fresh folder, adds the extensions again, and moves the five content folders
across.

**The updater.** `update.py` runs from the new release's copy against the project. It reads the
release and writes only to the project. It decides file by file against the project's own release
manifests. There is one manifest per owner: `familiar` for core, and each extension under its own
ID. A release build writes each manifest with a fingerprint of every file it ships. Each file gets
one of these results:

- `same`: the project's copy matches the new release.
- `update`: the project's copy still matches what the old release shipped, so replacing it loses
  nothing.
- `diverged`: the copy matches neither, so someone edited it. The updater leaves it alone and reports
  it.
- `add`: the file is new in this release.
- `retired`: the release no longer ships the file. An unedited copy moves into the update's backup
  folder, with any folder that it leaves empty. A retired skill therefore stops loading, and nothing
  is lost (`CORE-NO-DELETE`). An edited copy stays in place, and stays in the manifest so that later
  runs keep reporting it.

The updater compares and replaces entry files only inside their `familiar:start`/`familiar:end`
block. It stops before any write in three cases:

- the schemas differ
- the project has no core manifest
- a release file does not match its own manifest

It updates an extension only from a folder named with `--extension`. It checks each installed
extension's declared `core` range either way. Before `--apply` writes, it copies every file it will
replace, and the old marker, into `5-System/_update-backups/<old>-to-<new>_<date>/`. Then it sets
only the `familiar-version:` line and runs `project_check.py`. Separate manifests for each owner, and
the check before each write, make an in-place update safe. A core update never touches an
extension's package.

One hazard remains. Some files under `4-Trackers/`, `3-Knowledge/` and `2-Drafts/` hold release text
beside project data, and the update does not change them. If a new release changes a format, those
files do not get the change until you look at them yourself. Update tells you to do this.

To remove an extension, delete the paths that its folder added, listed in its own `_about.md`. There
is no list to update as well. The files on disk are the record.

### 12.2 No Python at runtime

Routing, skills and state are files that an agent reads directly, and setup needs no Python. The
updater (§12.1) is a standard-library Python script. The hand procedure needs no Python. Otherwise,
only the optional document and extraction scripts and the small read-only helpers under
`.familiar/scripts/` use Python. The document scripts check their own dependencies with
`--health-check` and fall back as their skills describe. `doctor.py` (§9.5) reports on the whole
toolchain at once.

---

## 13. Checks you can run

Two scripts in your copy check your setup. Neither changes anything.

- `.familiar/scripts/doctor.py` checks the document toolchain (§9.5).
- `.familiar/scripts/project_check.py` checks the project's health. Check-in runs it for you.

Before each release, the maintainer runs a separate set of checks against this manual and the
shipped files. Those checks are not part of the download. They cover the versions in the Baseline
line, the counts and names in this manual, and the skill contracts. They do not check the prose. An
explanation can become wrong while every count stays right.

---

## 14. Known limits, stated plainly

1. **Rules are instructions, not enforcement.** Every `CORE-*` rule depends on the model following
   it. `mechanical-enforcement` is `available` on Claude Code, Codex and Gemini CLI, and the guards
   are not part of the core download. The guards help enforce some rules, but they are not a
   guarantee. They match command text, so a short script run through an interpreter gets past them.
   The true claim is therefore "the guards catch the common cases where the agent supports hooks",
   never "familiar prevents X".
2. **Nothing verifies `document-tools` in advance.** No capability has an install-time check, and the
   capability table is written by hand. The truth is whatever the live `--health-check` reports on
   the computer that runs the session. On an agent with no Python, deck and document builds do not
   work, and familiar says so.
3. **`deck` ships no template and no shared library.** The only source is a template for this project
   that you place in `1-Inputs/Templates/`. Without one, `deck` reports that it is unavailable. It does
   not invent a brand or a neutral master (§9.5).
4. **There is no calendar link.** Date changes go to `4-Trackers/timeline.md` and memory, as
   `calendar-rules.md` describes. familiar then tells you what to put on your own calendar.
5. **Concurrency is detection, not control.** `CORE-STALE-WRITE` catches a second writer that follows
   the protocol. familiar supports one active writer at a time.
6. **`user-invocation-control` is an instruction only on Gemini CLI.** Claude Code frontmatter and
   Codex settings enforce it. Gemini CLI relies on registry rule 3.
7. **The bootstrap has no room left.** It is at its 500-word ceiling, and `AGENTS.md` holds a copy
   made by hand. Any addition needs a cut.
8. **Agent features change on their own schedule.** A change in an agent's file formats can require
   updates to the shipped subagent files and the documentation. Agents other than these three have no
   capability record (§10.3).

---

## Appendix A — core file inventory

**Protocol (`.familiar/core/`):** `bootstrap.md`, `_index.md`, `routes.md`, `state-schema.md`,
`extension-contract.md`, `familiar-behavior.md`, `file-handling.md`, `voice.md`,
`plain-language.md`, `familiar-voice.md`, `retrieval-fallback.md`, `running-scripts.md`,
`status-format.md`, `handoff-format.md`, `check-in.md`, `ingest.md`, `deck-rules.md`,
`deck-build.md`, `docx-rules.md`, `calendar-rules.md`. `capabilities.json` and
`extension-manifest.schema.json` are one level up, in `.familiar/` beside the `core/` folder.

**Agents:** `lookup.md`, `web-lookup.md`.

**Entry files:** `AGENTS.md` (holds the bootstrap text), `CLAUDE.md`, `GEMINI.md` (both only reference
`AGENTS.md`).

**Skill scripts.** Each is under both `.claude/skills/` and `.agents/skills/`.

| Script | What it does |
|---|---|
| `draft-document/scripts/build_pptx.py` | Builds and checks a deck (§9.5). |
| `draft-document/scripts/build_docx.py` | Builds and checks a Word document (§9.5). |
| `draft-document/scripts/tracked_edit.py` | Tracked changes and comment replies on a Word file that the team owns (§9.5). |
| `draft-document/scripts/xlsx_check.py` | Lists what a workbook holds and compares two versions. |
| `draft-document/scripts/office_render.ps1` | The final check in real Office, on Windows (§9.5). |
| `ingest/scripts/extract_pdf.py` | Extracts the text of a PDF. |
| `ingest/scripts/extract_encite.py` | Extracts EndNote citation fields from a Word source. |
| `ingest/scripts/source_register.py` | Keeps the list of ingested inputs, `3-Knowledge/_source-register.md`. Ingest checks it before and records after. |

**Project scripts (`.familiar/scripts/`).** All use only the standard library. Each script that
reports has a fallback: if it cannot run, the agent does the step by reading the files, and says so.

| Script | What it does |
|---|---|
| `project_check.py` | The read-only project health check that check-in runs (`check-in.md` → 4. Health check). |
| `timeline_views.py` | Writes `4-Trackers/_views/next-two-weeks.md` and `gantt.md` from `timeline.md`, stamped with its revision. Lists dependency problems without moving any date. `--json` prints the overdue, upcoming and problem lists as data and writes nothing. The fleet hub reads that. `--json --window N` widens "upcoming" to N days for that reader. The views stay at 14 days. |
| `meetings_view.py` | Does the same for `4-Trackers/meetings.md` (optional). It expands each series rule, applies moves, cancellations and extra meetings, and writes `_views/meetings-next-weeks.md`. `--json --window N` prints the meetings and problems as data, each meeting with its agenda from the file's `## Agendas` section. |
| `ref_count.py` | Counts claim tags and citation markers on a page, against its `ref_carry_through` stamp (ingest step 5). |
| `index_check.py` | Compares index rows with each page's front matter (ingest step 6). `--sync` is its one write: it copies each page's dates into its existing index row. |
| `task_frontier.py` | Lists open tasks whose blockers are cleared (Triage, Ongoing, check-in). |
| `tracker_edit.py` | The one script that writes a single milestone, task or meeting change. See below. |
| `draft_save.py` | The save path for `2-Drafts/`. See below. |
| `doctor.py` | The preflight for the document toolchain (§9.5). |
| `update.py` | The updater (§12.1). |

**`tracker_edit.py`** writes one change, for example `milestone --id M-04 --due ... --reason ...` or
`task --id T-12 --done`. `--dry-run` previews the change. For each change, it:

- checks the revision and adds one to it
- replaces the file in one step
- adds the status-log entry
- writes the views again
- lists the places (snapshot, tasks, later milestones) that still name the old date

It never deletes a row and never moves another date. The fleet hub uses it for edits across projects.
`--title "..." --reason ...` renames a milestone or task in place. IDs never change. If a blocker
names the old title in words, the script lists it and does not rewrite it.

`tracker_edit.py meeting <add-series|add-oneoff|move|cancel|edit-series|rename|agenda>` does the same
for `meetings.md`:

- A move or cancel changes one date of a series through an exception row, or a single meeting in
  place. A moved date takes its agenda with it.
- `edit-series` changes the series row itself.
- `agenda --id S-01 --date YYYY-MM-DD|standing --items "A; B"` sets the topic list for one date or
  the standing list for a series. `--none "reason"` records that there is no agenda.

It refuses a change that would leave the file with a problem that it did not have before, and it
reports a new overlap.

**`draft_save.py`** has four commands: `next`, `register`, `adopt` and `migrate`. It plans every
move, refuses if a target already exists, and never deletes.

- `next` prints `source now at:` for the current version after its moves.
- `adopt` checks every input before it moves anything.
- `migrate` folds an old flat `2-Drafts/` into one folder per deliverable, after you see a
  `--dry-run`.

`file-handling.md` → Saving under `2-Drafts/` has the same steps for doing it by hand.

No skill ships a `scaffold.py`, because the workspace is already set up and filled in as far as it can
be.

## Appendix B — record shapes

`.familiar/installed.json`

```json
{
  "schema": "1.1",
  "core": { "id": "familiar", "version": "1.0.2" },
  "adapters": { "claude": { "project-instructions": "active", "...": "..." } }
}
```

A release build adds `"build": "<commit>"` inside `core` (§12.1). The source files never carry it.

There is no separate list of extensions. The agent finds an installed extension from its package
under `.familiar/extensions/<id>/package/` and its own `familiar-extension.json` manifest (§11.4).
`installed.json` has no entry for it.

There is no `.familiar/backups/` and no transaction record, because there is no installer that needs
them. The updater's own backups go to `5-System/_update-backups/` (§12.1).
