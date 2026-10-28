# familiar core — technical manual

**Baseline:** core `1.0.0` · state schema `1.0` · extension contract `1.1` · install record schema `1.1`
**Verified against:** the maintainer's source repository at release time — its gate suite passes in
full (135 of 135) before every release. The suite is not in this download; see "How this document stays
true" and §13.
**Scope:** familiar **core** only — the `familiar-workspace/` tree as it ships. The extension contract
appears here as the interface core defines and enforces; no extension is described.

> This document is the consolidated technical description of familiar core: every mechanism, where
> it lives, what enforces it, and where it stops. `README.md` is the product overview and user guide,
> `INSTALL.md` the operator procedures. Where either disagrees with the
> executable behavior, the executable behavior wins and the prose is the defect.

## How this document stays true

A manual is prose, and prose rots quietly — exactly the way the extension manifest schema rotted for
a full release cycle because no code ever parsed it. So this one is not trusted on its authorship
date. familiar's maintainer keeps an executable gate suite in the source repository (`tests/` there).
It is not included in this download, and it runs before every release. One of its tests,
`test_core_manual_still_describes_this_tree`, reads this file and fails the suite when it stops
matching the shipped tree, so a release does not go out with a manual that disagrees with the files
beside it. You can check any of these claims yourself against the `familiar-workspace/` folder. The
test checks:

- the four declared versions in the **Baseline** line, against `VERSION`, `state-schema.md`, the
  manifest schema's own `contract` const, and the prebuilt install record;
- every gate count stated here, against the number of test methods that actually exist;
- the bootstrap's word and character counts, against the file;
- the set of `CORE-*` rule IDs — in **both** directions, so a rule added to the bootstrap and left
  undocumented here fails just as loudly as a rule documented here and since deleted;
- the core skill count, the model-invocable/user-only split computed from real frontmatter, and the
  presence of every individual skill name;
- every agent filename, every route ID in `routes.md`, and every capability name and state in
  `capabilities.json`.

What it deliberately does **not** check is the prose: an explanation can become wrong while every
number stays right. Treat a passing gate as "the inventory and the versions are current", not as
"every sentence is still accurate". The **Known limits** section (§14), and anything describing
intent or rationale, are the parts to re-read with suspicion after a design change.

If you find a statement here that disagrees with the files in your copy, the files are right and this
document is the defect; please report it.

---

## 1. What core is

familiar core is a host-portable, workspace-siloed memory and routing foundation for coding agents.
It is a set of plain files — Markdown protocol, Markdown skills, two JSON schemas, and prebuilt
per-host entry files — that ships complete inside one folder, `familiar-workspace/`, and gives that
folder a durable, authoritative memory and a deterministic way to load only the instructions a
request actually needs.

Three claims define it, and each is mechanically defended somewhere in the tree:

1. **One authoritative home per fact.** Project state lives in named files with declared update
   behavior (§6). Everything else — reports, dashboards, briefings — is a derived view that
   never overrides its source.
2. **Load after routing, not before.** The bootstrap permits bounded startup reads for preferences
   and binding (§4.1). A route is then selected, and exactly one skill body and its declared context load (§4, §5).
3. **Never claim a capability that has not been proven.** Capability state is a five-value
   vocabulary with no implied fallback; `active` means a released fixture passed (§9).

**Core is neutral by construction.** It ships nothing domain-specific and hard-codes no extension
ID. A gate asserts the bootstrap contains no domain vocabulary, and the maintainer's router audit rejects a core
file that names a specific specialty. Domain behavior arrives only through the extension contract
(§11), which core discovers generically.

### What core is not

- **Not a resident runtime.** Core routing and memory are files the host reads. There is no install
  step — `familiar-workspace/` is copied in and used as-is. Python or equivalent tooling is still
  required for document and PDF features (deck and document building, PDF extraction); a host
  without it has a real, disclosed gap in those features rather than a silent fallback.
- **Not an enforcement layer.** Core states rules; it does not police them. Mechanical enforcement
  is an optional, separately-maintained capability and the bootstrap explicitly disclaims implying
  it. Guard hooks are excluded from the core release payload.
- **Not multi-writer.** The documented operating model is one active writer at a time. The
  stale-write protocol (§6.3) detects a conflict; it does not merge one.

---

## 2. Repository shape (core only)

`familiar-workspace/` is the whole product: a single self-contained folder a user downloads and
pastes into any project, with no installation step and no separate compiler. It ships pre-baked —
scaffolded content folders, every host's native skill and worker files, and the protocol already in
place.

```text
familiar-workspace/
├── AGENTS.md / CLAUDE.md / GEMINI.md   host entry files (CLAUDE.md, GEMINI.md reference AGENTS.md);
│                                       release text sits inside <!-- familiar:start/end -->, user notes below
├── .familiar/
│   ├── routes.md, state-schema.md, extension-contract.md,
│   │   capabilities.json, extension-manifest.schema.json    protocol
│   ├── core/                           20 protocol .md files, including bootstrap.md
│   ├── scripts/                        stdlib helpers: project_check.py, doctor.py, ...
│   ├── installed.json                  core version, per-adapter capability states
│   └── release-manifests/              built releases only: fingerprints of release-owned files
├── .claude/skills/                     10 skills, one folder each; .claude/agents/ holds the native workers
├── .agents/skills/                     Codex and Gemini native skills — byte-identical to .claude/skills/
├── .codex/agents/, .gemini/agents/     native workers for Codex and Gemini
├── 1-Inputs/                           Sources/, Admin/, Templates/ — read-only
├── 2-Drafts/                           generated outputs plus _draft-index.md
├── 3-Knowledge/                        grounded understanding derived from 1-Inputs/
├── 4-Trackers/                         tasks.md, timeline.md, meetings.md
└── 5-System/                           config, context, Memory/, Decisions/, Handoffs/, preferences
```

`.familiar-project` ships inside the folder by default, with `created: not-yet-set` — every download
is bound from the moment it's renamed and opened. `checkin` stamps `created` with a real date the
first time it runs in the project (§4.1, §12). It replaces `project-config.md` only while that file
is still the shipped stub (`revision: 0`); a filled-in configuration beside an unset marker — a
migrated project — is reconciled in place, never reset to defaults.

`tests/quality_gates.py` (in the maintainer's source repository; not part of this download) holds the 135 executable contracts.

---

## 3. The runtime model

```text
host entry file            AGENTS.md / CLAUDE.md / GEMINI.md
  → bootstrap              the only always-loaded protocol file
    → startup reads        project preferences and title; optional global preferences, always
    → route registry       .familiar/routes.md — one route selected
      → one skill body     .claude/skills/<name>/SKILL.md (or .agents/skills/…)
        → required context declared by that skill, nothing else
          → conditional    loaded only when its named condition is actually present
```

Each arrow is a gate on context, not a suggestion. The chain is the mechanism that makes progressive
disclosure real rather than aspirational: the bootstrap is bounded and audited, the registry is a
table not a body of instructions, and the skill's context contract is validated by three separate
gates.

**Cost profile.** The always-loaded protocol floor is `bootstrap.md` at 500 words / 3,529 characters — at the
declared ceiling. Startup also reads the bounded preference and title context (§4.1).
The route registry adds 941 words when read, held under a 1,000-word ceiling. Other context is on
demand. The entry files, the registry and one skill together come to a few thousand tokens; the host's
own instructions and tools are usually several times that.
On a host that eagerly surfaces skill descriptions, add the description lines of
whichever skills that host exposes (§10.3).

---

## 4. The bootstrap

`.familiar/core/bootstrap.md` — 500 words, and inlined verbatim into `AGENTS.md`, the one entry file
that carries the full text (`CLAUDE.md` and `GEMINI.md` simply reference `AGENTS.md`). It is the only file guaranteed to be in
context. Everything it contains is therefore paid for on every turn of every session, which is why
its size is a gate, not a guideline.

It carries exactly four things.

### 4.1 Identity and the preference read

A one-paragraph statement of what familiar is, then mandatory, bounded startup reads. Locate the
`.familiar-project` marker before reading project state. Resolve project paths from its directory,
including when the session opens in a project subfolder. Before routing or project work, read
`5-System/user-preferences.md`, the title of `5-System/project-config.md`, and the optional
`~/.familiar/user-preferences.md`. The global file is read every time, not only as a signature
fallback, so its standing preferences apply on every project. That read is the sole startup exception
to `CORE-WORKSPACE-SILO`. Project preferences win on any conflict; the global signature applies unless
the project file sets its own.

Emit the retrieved signature once as `*(<signature>) familiar bound*`, appending `: <name>` from
the project title when set. Keep this visible in reply text, not only reasoning or collapsible
commentary. If no signature can be retrieved, use `n/a` for a failed signature read, or `not set`
when the files were read successfully but neither contains a signature. An unattempted read never
justifies either substitute.

The startup reads are an explicit exception in `CORE-PROGRESSIVE-DISCLOSURE`. They establish
preferences and binding before routing without requiring a particular first tool call, which could
otherwise conflict with locating the marker itself. They do not authorize reading tasks, knowledge,
or project history before routing. The reads are mandatory.

The signature is a **confirmation that the bootstrap is active**, and the file says so explicitly:
it does not claim mechanical enforcement is available. This distinction was deliberate — the marker
is evidence the protocol loaded, nothing more. Its detection value depends on the key being one the
user chose and recognises, which is why the user sets it through `/system-settings` → Preferences,
`checkin` only points there, and the shipped `5-System/user-preferences.md` carries no signature at
all. A signature baked into the template would make every project emit the same key and the canary
would confirm nothing.

The two halves of the line prove two different reads: the name proves `project-config.md` was read,
the signature proves the preferences were. Each project has **its own** signature,
in its `5-System/user-preferences.md`; the global file holds only a default, shown by a project that
has none of its own. A per-project key is the stronger canary — it can only come from reading this
project's file, not from a key the agent has seen in every other project — and it is the project's
identity outside the session: the fleet hub labels each project's rows with it and reports two
projects sharing one.

The project file is read again later, at `voice.md` → Pre-delivery check, immediately before
delivering output, where it overrides the global file on any preference they disagree on.

### 4.2 The active boundary

The directory containing `.familiar-project` is the active project, and that whole folder is the
two-way boundary — see `CORE-WORKSPACE-SILO`. A file enters via `1-Inputs/` or an explicit task
mention and leaves only when asked; familiar infrastructure inside the folder may be read when a
route requires it; nothing outside the folder is in scope, and there is no cross-project exception.
A file the user names outside the folder may be read for that task, and `routes.md` → Files outside
the project has the assistant say so once: the file is outside the project, nothing from it is kept,
and copying it into `1-Inputs/` makes it part of the project. Added 2026-10-27, after a demo run read
a named outside file without remark.

Note the marker names the workspace rather than the workspace being assumed by folder name —
`file-handling.md` restates this as a rule, because a project may rename its workspace root.

### 4.3 The eleven non-negotiable rules

Each carries a stable `CORE-*` ID. Stability matters: `test_stable_rule_references` scans every
shipped `.md`, `.py`, `.ps1`, and `.json` file and fails on a citation to a rule ID that no longer
exists, so a rule can be reworded but not silently renumbered. Legacy numeric-rule citations are
forbidden by the repository's own working rules.

`CORE-WORKSPACE-SILO` is one rule for both directions: the project folder *is* the project, read and
write are both scoped to it, symmetrically, and "another project" simply means a different folder.

| Rule | States | Failure mode it prevents |
|---|---|---|
| `CORE-GROUND` | Ground project claims in retrieved material, external claims in attributable sources. A failed or blocked read is a retrieval gap. Report it; never turn it into an inferred fact. | The agent reconstructs a file it could not read from its filename, or answers from parametric memory and presents it as project fact. |
| `CORE-NO-DELETE` | Do not delete project files; identify obsolete material and let the user decide what to remove or archive. | Irreversible loss during cleanup. |
| `CORE-WORKSPACE-SILO` | The marker's directory is the active project and the boundary in both directions: read and write inside it. A file enters via `1-Inputs/` or an explicit task mention, and leaves only when asked. Never reach into a sibling folder unasked. | Writes leaking outside the workspace, or context and confidentiality bleeding in from an unrelated folder — in either direction, not just out. |
| `CORE-COPY-ON-EDIT` | Do not overwrite a source in `1-Inputs/` or an in-workspace draft — create a dated copy instead. Update authoritative state only when the route declares it under `Updates`. | A source document or a delivered draft destroyed by an edit. |
| `CORE-PLAIN-NAMES` | Talk to the user in plain words. Name each thing; show an ID, code or version label only beside that name. | Replies the user cannot follow: chains of task IDs, gap codes and version labels that only the session holds (launch audit 2026-10-23: "I'm a bit lost", "Explain simply"). |
| `CORE-NO-FABRICATION` | Do not invent facts, dates, amounts, decisions, citations, paths, capabilities, or completion. Say what must be confirmed. | Confident invention — including inventing that a capability works, or that work is done. |
| `CORE-SCOPE` | Change only what the task requires. Do not reorganize adjacent files or load unrelated history. | Drive-by refactors and context bloat. |
| `CORE-INSTRUCTIONS-READONLY` | Treat installed protocol and route files as read-only during project work; change the system only through an explicit maintenance route. | The agent editing its own rules mid-session. |
| `CORE-PROGRESSIVE-DISCLOSURE` | Before routing load only this bootstrap and its bounded startup reads. Then read one skill, its required context, and context whose named condition is present. | Reading the whole project "to be safe". |
| `CORE-HUMAN-APPROVAL` | Ask before overwriting, publishing, sending, installing, changing status, or another consequential action the route does not authorize. | Unattended consequential action. |
| `CORE-STALE-WRITE` | Read a living state file's revision before editing. If it changed since, stop, reread, and reconcile instead of overwriting newer work. | Silently overwriting newer work from a concurrent session. |

These are **instructions to a model, not code.** Their reliability is the model's compliance, plus
whatever the optional enforcement capability adds on a host that has it. Core never states or
implies otherwise.

### 4.4 Route selection

A four-sentence instruction: read `.familiar/routes.md` (or the installed core copy when the
project-local one is absent), select one route *before* loading detailed instructions, read that
skill's body plus required and conditionally-triggered context, respect its excluded context and
declared update surfaces, and **ask rather than browse the system** when no route fits.

That last clause is the anti-pattern this whole design exists to prevent: an agent that, faced with
an unmatched request, starts reading files to find out what it can do.

### 4.5 The budget

500 words is a hard ceiling asserted by `test_bootstrap_size_rules_and_neutrality`, which also
checks that every `CORE-*` rule is present and that no domain vocabulary appears. The file currently
sits at 498, two words under. `AGENTS.md` embeds the text verbatim and is **hand-synced — there is no
regeneration script**; `test_entry_file_bootstrap_matches_core` compares it against the source.
`CLAUDE.md` and `GEMINI.md` carry no copy of their own — each is a thin file that resolves to
`AGENTS.md` — so a bootstrap edit is a two-file edit (`bootstrap.md` and `AGENTS.md`) plus a gate run.

---

## 5. Routing

### 5.1 The registry

`.familiar/core/routes.md`, also copied to `.familiar/routes.md` for the project-local read the
bootstrap performs. It is a table plus seven resolution rules — deliberately not instructions, so
reading it is cheap.

Seven routes:

| Route ID | Select when | Canonical skill |
|---|---|---|
| `project.status` | Resume work, inspect current state, establish a fresh project, or check in | `ongoing-work` or `checkin` (user-only) |
| `project.memory` | Record progress, decisions, tasks, or durable context | `save` (user-only) |
| `project.handoff` | Pause or resume unfinished work across focused sessions, or hand a scoped piece of work to someone outside this project | `handoff` (user-only) |
| `project.research` | Retrieve project or external evidence | `ingest`, or `online-research` (user-only) |
| `project.output` | Create or revise a presentation, written document, or workbook | `draft-document` (user-only) |
| `project.output` | Scope a deliverable before drafting it | `deliverable-brief` (user-only) |
| `project.schedule` | Maintain tasks or milestones | `triage` (user-only) |
| `system.maintenance` | Maintain familiar or the project shell: update, workspace tidy, tracks, closeout | `system-settings` (user-only) |

There is no fleet-scope route. `triage` is project-scope only, like every other skill; the
cross-project view is the separate fleet hub (§6.4).

A route ID appearing on more than one row would be **one route with several distinct triggers**, not
a duplicate — rule 6 says so explicitly. `project.output` repeats: drafting a deliverable and
scoping one before drafting are distinct triggers.

### 5.2 Resolution rules

1. Explicit skill invocation wins when that skill is installed and available. The user invokes a
   skill explicitly with the host's command. `save` and `handoff` alone may also be invoked in the
   user's own words ("save progress", "hand this off"); any other request, including one that names
   another skill, is a route match, and rule 3 applies. Added 2026-10-24, after two weeks of real use
   typed `/save` and `/handoff` dozens of times mid-sentence; every other user-only skill still
   starts only from its command.
2. Otherwise select the single narrowest matching route.
3. **A route whose matching skill is `(user-only)` is never opened or run by the agent.** Identify
   the fit, tell the user how to start it on this host — the host's own form where it has one (a
   slash command, a `$`-prefixed mention, or a skill picker), or a plain request by skill name where it
   has none — and stop. The wording is host-neutral on purpose; see the per-host note in §5.3.
4. Otherwise load the skill body before any project content.
5. Follow the skill's Required, Conditional, Excluded, Updates, Capabilities, and Completion
   declarations.
6. A genuine collision — two routes whose triggers both plausibly match with no narrower rule — is
   an **installation error**, not something to resolve by load order.
7. When no route fits, ask, without opening unrelated files.

### 5.3 `(user-only)` and why it lives in the registry

Eight of the 10 core skills carry `disable-model-invocation: true` in their frontmatter. Claude
Code honors that frontmatter. Each `(user-only)` skill also ships a pre-baked
`agents/openai.yaml` with `allow_implicit_invocation: false`, so both adapters report
`user-invocation-control: active`. Gemini CLI remains instruction-level: all skill descriptions may
reach the model there.

**Starting a skill differs by host.** On Claude Code a skill is a slash command: `/ili-triage`. Each
`.claude/skills/<skill>/SKILL.md` sets `name: ili-<skill>`, so the `/` menu lists every familiar skill
under `/ili`; the folder name still invokes it (`/triage`), and the `.agents/` copy keeps
`name: <skill>` (the one sanctioned difference between the two copies). On Codex
it is a `$` mention (`$triage`) or the `/skills` picker. Gemini CLI has no per-skill command: the model
activates a skill after the user confirms, so ask for it by name ("run triage"). The same registry rule 3
sentence therefore resolves to a different gesture on each host, and on a host with no explicit gesture
the user's plain request is the start signal. Use the form your host documents; the skill content is
identical on all three.

> **Recommended: put the command first** (`/online-research <question>`, `$triage`). That is the form
> every host documents. A command written at the end or mid-sentence often works, but it is not
> guaranteed: if the host does not expand it, it arrives as plain text, and because a `(user-only)`
> skill is hidden from the model, the assistant can only report that it found no such skill and fall
> back to unrouted behavior. If a skill did not run, resend with the command first. `save` and
> `handoff` are the designed exception (§5.2 rule 1).

Rule 3 is the host-neutral guarantee. It lives in the registry text itself rather than depending on
any host recognizing per-skill frontmatter, so the promise holds identically everywhere. Two gates
back it: `test_route_targets_match_invocation_marker` keeps the registry's `(user-only)` annotations
consistent with the actual frontmatter, and `test_all_core_skills_are_routed_or_listed_as_exceptions`
proves every skill is reachable.

### 5.4 Explicit-only, unrouted

Empty: every core skill is reachable from the table above. The section stays because the category
is real: a skill too consequential or too narrow to reach by route match is
listed here and named only by the user, and `test_all_core_skills_are_routed_or_listed_as_exceptions`
accepts either placement.

### 5.4a Router skills and branches

Four skills in core are **routers**: `system-settings`, `draft-document`, `handoff`, and
`save`. Each one's body is a menu; each operation it offers lives in a reference file under
its own `skills/<router>/references/`, and the router loads exactly one after the user picks. From
that point the branch's own context contract governs — its Required, Conditional, Excluded, Updates,
Capabilities and Completion declarations replace the router's, which covered only the menu. A run
therefore loads the menu plus one procedure, the same budget as invoking one skill directly.

| Router | Branches |
|---|---|
| `system-settings` | `update`, `tidy-workspace`, `tracks`, `project-closeout`, `preferences`, `fleet`, `hooks` |
| `draft-document` | `deck`, `document`, `review`, `workbook` |
| `handoff` | `session-handoff`, `assignment` |
| `save` | `progress`, `to-memory` |

Two branches write outside the project, each to one file under `~/.familiar/` and only on an explicit
request, declared in the branch's own contract as the exception to `CORE-WORKSPACE-SILO`: `preferences`
writes `user-preferences.md`, and `fleet` writes this project's own row of `fleet.md` (register,
unregister by setting `included` to `no`); lifecycle is the hub's, in its registry. The cross-project overview
that reads `fleet.md` is a separate fleet hub, distributed on its own. The hub
alone creates `fleet.md` (`fleet_overview.py --discover <dir> --apply`, a script, so it works the same
on every host); the branch edits an existing file and, when there is none, says to set up the hub.

Consolidating them removed entries from the command list for operations that share an occasion —
housekeeping, producing a deliverable, moving work off the user's plate, filing durable state — but
share no procedure, without merging their procedures into one contract that would have had to union
every Required set and gut the Excluded discipline.

Two properties make this safe rather than a hole in the routing model:

- **Rule 3 still covers every branch.** Each router carries `disable-model-invocation: true`, so a
  route match never opens it and never reaches anything beneath it. That made `machine-setup`,
  `project-closeout`, `deck`, `document`, `assignment`, and `to-memory` user-started, which they were
  not all before — the deliberate price of each consolidation. The setup skill stayed a top-level
  model-invocable one at the time, as the first command a new user ran — until it retired entirely
  2026-09-04 (§12), when `checkin` absorbed the one piece of its first-run work a human still needs
  to do.
- **Branches stay under gate coverage.** `CONTRACTS` in the maintainer's gate suite is `SKILLS` plus
  every `references/*.md` carrying a context contract, so contract completeness, disjointness,
  capability vocabulary, the read-only/file-write rule, and the writing-layer declaration are all
  checked on branches exactly as on skills. Without that, demoting a skill would have silently
  dropped it out of coverage.

A branch is not a skill: it has no frontmatter, no route, and no slash command, and it is never
opened without a selection in the menu.

### 5.5 Extension routes

There is no separate extension registry to consult. An extension route exists exactly when its skill
folder is present on disk in this host's native skill location — checked directly against the
extension's own `familiar-extension.json` manifest — and that presence check happens **before**
finalizing a match against the core table. A narrower installed extension route wins; its skill body
is not opened until it is selected. Extension routes add entries and never replace core routes. Each
carries its own `select_when` trigger string — the same role the core table's "Select when" column
plays — required by the manifest schema since contract `1.1`. An extension route's skill is
`(user-only)` exactly when its own `SKILL.md` carries the frontmatter marker, and rule 3 applies to
it identically.

---

## 6. The state model

`.familiar/core/state-schema.md` defines schema version `1.0`. A generated report is a view,
never another source of truth.

### 6.1 Authoritative surfaces

| Surface | Authoritative contents | Update behavior |
|---|---|---|
| `5-System/project-config.md` | Stable settings, workspace path, schema version, installed extensions, capability record | In place; explicit setup/maintenance only |
| `5-System/project-context.md` | Background, objectives, stakeholders, durable constraints | In place; material durable changes only |
| `5-System/Memory/status-snapshot.md` | Current phase, blockers, immediate next actions, latest revision | Atomic in-place replacement |
| `5-System/Memory/status-log.md` | Meaningful chronological events | Append only |
| `4-Trackers/tasks.md` | Action, owner, status, due information, blockers | In place, by task routes |
| `4-Trackers/timeline.md` | Milestones and dates | In place when a date moves |
| `4-Trackers/meetings.md` | Planned internal and client meetings: series rules, one-offs, per-date moves and cancellations, and each meeting's agenda (optional) | In place; rows are never deleted |
| `5-System/Decisions/*.md` | Approved decision, rationale, date, consequences | New record; amendments retain history |
| `5-System/Handoffs/*.md` | Temporary in-flight instructions for the next focused session | New record; status may change in place |
| `5-System/user-preferences.md` | Project-specific statement of how the user wants familiar to work here | In place; the referencing method once on the first Word draft that cites, otherwise via `save` → To memory only (a project-only signature is a hand edit; the shared signature lives in `~/.familiar/user-preferences.md`, written by `system-settings` → Preferences) |
| `5-System/notes.md` | Loose notes fitting no other surface | Append or in place, via `save` → To memory |

`5-System/Memory/save-progress.md`, overview reports, briefings and dashboards are **derived and
disposable**. They never override the surfaces above.

### Freshness and session provenance

Knowledge pages record `last_verified`, `review_by`, and `volatility`; the index exposes the first
two. A scheduled freshness task may report overdue pages and contradictions, but it does not
silently rewrite project knowledge. Native host memory is non-authoritative and never overrides
these files.

Core does not keep a transcript-like log of every model session. Model name and effort are
operational telemetry, not project truth. Record them only as provenance for consequential research,
decisions, or deliverables, or in an optional operations extension that is not loaded as project
memory.

### 6.2 Required metadata

Every living state surface opens with:

```text
<!-- familiar-state-schema: 1.0 -->
<!-- revision: <non-negative integer; 0 is an unwritten scaffold> -->
<!-- last-updated: <ISO-8601 timestamp or date> -->
```

The append-only activity log does not use replacement revisions; entries are appended oldest to
newest and each carries its own date plus affected task or decision IDs.

### 6.3 The stale-write protocol

Before writing, a route records the revision it read. The replacement increments it by one. If the
on-disk revision is no longer the value read, `CORE-STALE-WRITE` applies: **stop, reread, reconcile,
and report the conflict** — do not overwrite. Where the host supports it, write to a temporary
sibling and atomically replace.

This is conflict *detection*, honestly scoped. It catches a second writer that also followed the
protocol. It does not lock, merge, or defend against a writer that ignored it. The documented model
remains one active writer at a time.

It also does not survive a synced folder, and that is the case most likely to be hit in practice.
The revision comparison reads local disk; OneDrive, SharePoint, Dropbox, iCloud Drive and their equivalents
reconcile *after* a write lands. Two machines can therefore both read revision 3, both write
revision 4, and neither check fires — the sync client resolves it as last-writer-wins or by dropping
a conflict copy. The conflict-copy check recognizes the machine-suffix and "conflicted copy" patterns
and iCloud Drive's `name 2.md` form (a space and a number before the extension). Since a conflict copy lands inside the silo, where `CORE-NO-DELETE` forbids cleanup
and a later route read could mistake it for real state, `file-handling.md` requires a pre-write check
for one and a stop-and-report when found. That check is the only part of this the system can
actually enforce; the rest is a constraint on how the user works, stated in `INSTALL.md` →
*Synced folders and concurrent use*.

### 6.4 No cross-project exception

`CORE-WORKSPACE-SILO` has no cross-project exception at all: the workspace folder is a hard boundary
in both directions, full stop. Nothing in a sibling project is ever read, and nothing is written
outside the active workspace.

A project never reads another project. The cross-project view is the fleet hub, a separate folder
outside every project that reads each registered project as data (§5.4a → `fleet`); nothing inside a
project can name another project to read from.

### 6.5 Extension state surfaces

An extension declares its own surfaces as objects with `path` (workspace-relative, never a
plugin-cache path), `schema_version` (its own, independent of core's `1.0`), `update_behavior`
(plain text matching the column above), and `scaffold` (whether the extension's drop-in folder
carries the file already created). A scaffolded surface ships at revision `0` with the extension's
schema version, and a later drop-in of the same extension never replaces it — package paths are
replaced, living state is not.

---

## 7. The workspace

The folder ships already scaffolded — nothing copies a template into a new project. The workspace,
including `.familiar-project`, ships filled in as far as it truthfully can; `checkin` writes the
project's own facts into the remaining stub surfaces on its first real run (§4.1, §12).

```text
familiar-workspace/
├── .familiar-project                   ships with created: not-yet-set; checkin stamps it first-run
├── .familiar/
│   ├── routes.md, state-schema.md, extension-contract.md,
│   │   capabilities.json, extension-manifest.schema.json    protocol
│   ├── core/                           every core .md
│   ├── installed.json                  core version, per-adapter capability states
│   ├── extensions/<id>/package/        each installed extension's package, when any is installed
├── 1-Inputs/                           Sources/, Admin/, Templates/ — read-only
├── 2-Drafts/                           generated outputs plus _draft-index.md
├── 3-Knowledge/                        freshness-aware index, digested pages
├── 4-Trackers/                         tasks.md, timeline.md, meetings.md
└── 5-System/                           config, context, Memory/, Decisions/, Handoffs/, preferences
```

`file-handling.md` fixes the ownership boundaries: `1-Inputs/` is source, read-only; `3-Knowledge/` is
grounded understanding derived from it; `2-Drafts/` holds outputs awaiting review; `4-Trackers/` and
`5-System/` are authoritative state. A project may rename the workspace root — resolved from the
marker, never assumed from the folder name — but may not silently reinterpret these boundaries.

Every folder ships an `_about.md` stating what it owns, so the structure is self-describing to an
agent that lands in it without the protocol loaded.

---

## 8. Skills

### 8.1 The context contract

Every `SKILL.md` declares six fields, and three gates enforce them:

| Field | Meaning |
|---|---|
| **Required context** | What must be read for this skill to work at all. |
| **Conditional context** | Loaded only when a *named condition* is actually present. |
| **Excluded context** | What this skill must not open, stated positively. |
| **Updates** | Which authoritative state surfaces this skill may write in place. |
| **Capabilities** | Which capabilities it needs, from the canonical vocabulary. |
| **Completion** | The outcome-based condition for being done. |

Enforcement:

- `test_every_skill_has_context_contract` — all six present, once each, non-boilerplate, with
  distinct outcome-based Completion text.
- `test_context_contract_required_and_conditional_are_disjoint` — required ∩ conditional and
  required ∩ excluded must both be empty. A file in both lists is a contract that says nothing. A
  non-blocking companion report flags a conditional entry with no trigger phrase.
- `test_skill_capabilities_use_canonical_vocabulary` — the primary capability list must use names
  from `capabilities.json`; a clause after `;` is treated as elaboration.
- `test_read_only_skills_do_not_declare_file_write` — a skill whose Updates line says "nothing" may
  not declare `file-write`, with one recorded exception in core (`online-research`) that documents a
  specific user-requested write. The gate also tolerates a second such exception that lives in an
  optional extension rather than in core.

### 8.2 The 10 core skills

**Model-invocable (2)** — a route may select and run these:

| Skill | Purpose |
|---|---|
| `ongoing-work` | Stateless read-only query: what is open right now |
| `ingest` | Digest one approved source into `3-Knowledge/` |

**User-only (8)** — identified by a route but never started by the agent:

| Skill | Purpose |
|---|---|
| `checkin` | Recurring check-in: pre-draft from state, reconcile, health-check; establishes a fresh project on its first real run (§4.1, §12) |
| `triage` | Sort this project's open work by effort or urgency; read-only |
| `online-research` | External research, bypassing the local-library check |
| `system-settings` | Housekeeping menu; routes to one of seven branch procedures (§5.4a) |
| `deliverable-brief` | Scope a deliverable in `2-Drafts/<slug>/_brief.md` (core, argument, headline outline), then lock it for `draft-document`. Starts from a matching profile (global `~/.familiar/brief-profiles/`, or an extension's `brief-profiles/`), built on request from the user's own examples, and a read-only harvest of project state and knowledge |
| `draft-document` | Deliverable menu; routes to `deck`, `document` or `review` (§5.4a) |
| `handoff` | Handoff menu; routes to `session-handoff` or `assignment` (§5.4a) |
| `save` | Memory menu; routes to `progress` or `to-memory` (§5.4a) |

**Branches (12)** — procedures, not skills: no frontmatter, no route, no slash command, reachable
only through their router's menu. They are covered by the contract gates via `CONTRACTS`:

| Router | Branch | Purpose |
|---|---|---|
| `system-settings` | `update` | Update core or selected extensions without touching other components' files |
| `system-settings` | `tidy-workspace` | Survey, propose, and on approval move stale workspace files |
| `system-settings` | `tracks` | Own the whole track lifecycle: propose, add, split, merge, retire |
| `system-settings` | `project-closeout` | Reconcile final state and produce a derived closeout summary |
| `system-settings` | `preferences` | Set this project's familiar signature (in `5-System/user-preferences.md`), the default signature, and standing preferences (in the global `~/.familiar/user-preferences.md`) |
| `system-settings` | `fleet` | Register or unregister this project in `~/.familiar/fleet.md`; the hub owns lifecycle; the hub that reads it is distributed separately |
| `draft-document` | `deck` | Build or revise a presentation |
| `draft-document` | `document` | Create or revise a written document (`.docx` or degraded Markdown) |
| `draft-document` | `review` | Tracked-change and comment-reply passes on a team-owned Word file (`tracked_edit.py`) |
| `draft-document` | `workbook` | Plan, build and check an Excel deliverable; `xlsx_check.py` names what an openpyxl round-trip would drop and what a new version lost |
| `handoff` | `session-handoff` | Park or resume in-flight work across sessions |
| `handoff` | `assignment` | Draft a self-contained brief for someone with no access to this project |
| `save` | `progress` | Reconcile every track at a break boundary; writes no new surface |
| `save` | `to-memory` | Route an out-of-band note to the right memory surface; owns capture routing |


### 8.3 Procedure files

Long procedures live in `.familiar/core/` and load only when a skill names them, keeping skill
bodies short:

| File | Loaded by | Contents |
|---|---|---|
| `check-in.md` | `checkin` | Read state → pre-draft the delta → reconcile → health check → close |
| `ingest.md` | `ingest` | Read mode vs. ingest mode, size check and bulk ingest, the ingest procedure, source dates and conflicts, privacy and failure |
| `status-format.md` | memory/track skills | Memory file formats, read order, update rules, decision records |
| `handoff-format.md` | `handoff` → Session handoff | What a handoff is for, one file per thread, the four status values, template, writing and reading one |
| `deck-rules.md` / `deck-build.md` | `draft-document` → Deck | Template precedence, template inventory and brand rules, the headline test, visual design for presented decks, content and bullet discipline, validation and delivery; the build procedure |
| `docx-rules.md` | `draft-document` → Document, conditionally | Word-document content, copies, build and validation |
| `calendar-rules.md` | `save` → To memory, `checkin` | Timeline-plus-memory as sole source of truth; propagation order; guardrails |
| `familiar-behavior.md` | any route needing lifecycle guidance | Neutral project-lifecycle behavior; explicitly *not* a startup checklist |
| `voice.md` | a skill that authors prose; on its own for a routed chat response | §9 |
| `plain-language.md` | authored output longer than a chat reply | §9 |
| `familiar-voice.md` | only when project config enables it | Optional companion voice |
| `retrieval-fallback.md` | when `named-subagents` ≠ `active` | §10.2 |
| `running-scripts.md` | only when a script cannot run | What to do when Python or a package is missing |

`_index.md` is the map of which file loads when.

---

## 9. The writing and output layer

### 9.1 Two files, split by judgment versus spec

- **`voice.md`** — the half that cannot be checked mechanically, loaded when a skill authors prose
  and sufficient on its own for a routed chat response. Clear, direct language at the user's level;
  familiar has *no* universal industry, profession, or formal register. Lead with the outcome;
  concrete nouns and active verbs; distinguish confirmed fact, source-backed interpretation, open
  question, and recommendation; preserve uncertainty where the evidence is uncertain. The avoid-list
  bans generic scene-setting, inflated claims, fake quotations, decorative rhetorical questions, and
  claiming completion before validation ran.
  Its **Audience** section governs who a deliverable's body prose is addressed to: confirmed before
  writing (`document.md`/`deck.md` step 1), and, for an external reader, prose may not name the
  project corpus or retrieval system as an evidence base, attribute a finding to generic "sources"
  instead of the study or guideline, report the document's own drafting/confirmation status inline,
  explain an editorial choice to the reader, or cite the project's own in-progress draft. Judged by
  who the sentence addresses, not a banned-phrase list — an internal working draft is exempt outright.
  Its **Uncertainty marker** section defines two bracket markers, not one: `[verify]` for an
  ungrounded or unconfirmed claim, `[action: ...]` for an instruction to the drafter (a task, not a
  claim in question) — both must reach zero before external delivery, and in a `.docx`/`.pptx` built
  with `document-tools` both get their own colored, italic run (`docx-rules.md`/`deck-rules.md` →
  Editor notes) rather than surviving as plain bracket text in the body font.
- **`plain-language.md`** — the half that is countable, loaded only when writing something longer
  than a chat reply. It opens by picking the **shape** from content type rather than audience —
  operational (imperative, one instruction per sentence, 20 words), full-prose deliverable
  (paragraphs, structural rules only, 25 words), deck (fragments, limits and vocabulary only), chat
  reply (`voice.md` alone), persuasive text (exempt) — and that choice decides which sentence rules
  bind. Then the rules themselves: tense, modal, one word per meaning, filler to delete, a
  self-check, and a section stating its own limits honestly.

**Why the split is where it is.** `voice.md` is applied by thinking and `plain-language.md` is
applied by searching the draft, so only the second can be verified and only the second is worth its
load cost at the moment of writing rather than always. Shape selection lives in `plain-language.md`
and not in `voice.md` because the shape exists to decide which sentence rules bind; separating the
choice from its consequence is what let the previous three-file layer drift.

**Why a 1983 aerospace standard.** "Write clearly" is an opinion and models do not act on opinions.
"No sentence over 20 words" is a spec and models do act on specs. ASD-STE100's rules were written so
that a tired reader who is not a native English speaker cannot misread an instruction. Removing the
tells of AI-generated prose — long sentences, synonym rotation, hedging, decorative clauses — is a
side effect, which is why the spec and `voice.md`'s banned list reinforce rather than duplicate each
other.

### 9.2 The pre-delivery check

Before delivering output governed by `voice.md`, it requires verifying six things: the requested outcome
is present and findable; claims are grounded at the level the task requires; unknowns and
assumptions are visible; dates, names, amounts, citations and paths were not invented; the shape
matches project configuration, the project's `user-preferences.md`, and the audience; and remaining
`[verify]`/`[action: ...]` tags are counted and reported — zero required for output leaving the
project.

Two former items were removed rather than lost. Path, version and provenance are `file-handling.md`'s
subject, and every skill declaring `file-write` now names that file in its required context, so the
rule loads whether or not the writing layer does. Context leakage is what the **Excluded context**
field of every skill contract already states, one skill at a time and more precisely than a general
reminder could.

### 9.2.1 How the rules reach each write

Every skill declaring `file-write` requires `file-handling.md`; source protection, naming, versions,
and provenance apply to every write. Skills that author a deliverable, knowledge page, review,
brief, or other prose also declare `voice.md` and `plain-language.md`, either as required context or
behind the exact branch that produces prose. State-maintenance skills instead load the applicable
state rule such as `status-format.md`, `state-schema.md`, or `check-in.md`.

This distinction keeps a tracker or metadata edit from loading the full prose specification while
leaving file safety and state formats mandatory. `test_file_write_skills_load_relevant_write_rules`
derives the file-writing set from each capability line, checks that every writer requires
`file-handling.md`, and checks that the contract exposes either authored-output guidance or a state
format. The six-field contract remains the single statement of what a route can load.

The project-local `user-preferences.md` is read during bounded startup (§4.1) and again through
`voice.md` immediately before authored output, where its content can affect the result.

### 9.3 File handling, naming, provenance

- New user-reviewable output: `YYYY-MM-DD_<short-description>_<status>_vN.<ext>`, status `DRAFT`,
  `REVIEW`, or `FINAL`. Increment on revision. `final-final`, `new`, and overwriting the source
  filename are explicitly not version control.
- Living state uses stable filenames and revisions instead; activity logs are append-only.
- An output based on project sources cites the source path and a useful locator; one based on
  external retrieval carries the original URL, access date, and the narrowest available locator. A
  retrieval gap is recorded as a gap.
- Generated knowledge and review outputs record the producing skill ID, date, and installed
  component version — the fully qualified namespaced ID for an extension contribution.
- Office documents are ZIP packages: before reading or delivering a `.docx`, `.pptx`, or `.xlsx`,
  verify a readable central directory and `[Content_Types].xml`. A renamed or truncated archive is
  not a valid Office document.
- Nothing is published, sent, or moved outside the workspace without explicit approval.

### 9.4 The optional companion voice

`familiar-voice.md` is pure flavour — familiar works identically with it off, and **no rule or guard
depends on it**. It fires only for something noticed unprompted (a date that moved, a logged
decision about to be contradicted, a track gone quiet, a directly relevant memory not asked for),
renders as an italic line prefixed with the signature key, and never applies to a guard message, a
system message, or anything inside a deliverable. Italics are used only when the adapter reports
Markdown rendering as available.

### 9.5 Document building — the honest gap

`deck` and `document` ship real, host-neutral build scripts (`skills/draft-document/scripts/build_pptx.py`,
`skills/draft-document/scripts/build_docx.py`) using `python-pptx` and `python-docx` — ordinary
open-source libraries, deliberately not a redistribution of any vendor's packaged document skill.
Each supports `--health-check`, `--build`, `--validate`, `--render`. Beside them,
`scripts/xlsx_check.py` (standard library only) inventories a workbook and compares two versions, and
`scripts/office_render.ps1` (Windows PowerShell 5.1) opens a deck, document or workbook in the real
Office application, read-only and under a time limit, for the Office-native final check: slide PNGs
and a PDF for a deck, an open check with page, tracked-change and comment counts for a document, a
recalculation and formula-error count for a workbook. Where Office is installed, its render is the
one that counts; a LibreOffice render is labelled LibreOffice-only.

Both scripts look for LibreOffice's `soffice` on `PATH` first and then in the default install
locations, which are not on `PATH` by default: the macOS app bundle
(`/Applications/LibreOffice.app/Contents/MacOS/soffice`), `Program Files` on Windows, and the common
Linux paths (`/usr/lib/libreoffice`, `/opt/libreoffice*`). A default install is therefore found without
any configuration.

**Preflight.** `.familiar/scripts/doctor.py` is a cross-platform, standard-library preflight for this
toolchain (Windows, macOS, Linux; run it with `python3`, `python` or `py`, whichever exists). It
checks the Python version, the `python-docx` and `python-pptx` packages, LibreOffice (using the same
lookup as the build scripts), pandoc, and the optional extraction tools; it prints what is missing,
what breaks without it, and the command that fixes it on that machine (a `~/.familiar/venv` where the
system Python refuses `pip`, per PEP 668), and exits `0` when every required check passes. It avoids
3.10 syntax so it can diagnose an older Python. Every other shipped script starts with a guard that
stops on Python older than 3.10 with a plain message instead of a traceback, and `routes.md` →
Running familiar's scripts tells the assistant how to pick the interpreter, and `running-scripts.md`
when to offer an install. It is read-only. A PowerShell `doctor.ps1` shipped beside it until 1.0.0 and was retired once
`doctor.py` covered Windows.

**`document-tools` is recorded `available`, never `active`, on every adapter.** There is no
install-time verification mechanism anywhere in this codebase — the capability matrix is
hand-asserted — so rather than invent one, both procedure files instruct running the script's own
`--health-check` at the start of every build and reporting the real result. Visual validation needs
a LibreOffice `soffice` binary (found as above); its absence is reported as `"visual_validation": false`, not
silently skipped. `deck` has no non-visual fallback and must say so; `document` degrades to
Markdown. On a host with no Python, this is a real gap, and the design refuses to hide it.

**Citations and team-owned Word files.** A Word draft cites in two colored layers: teal `reference`
for the compiled document a statement came from, purple `primary-reference` for the underlying study,
back to back (`docx-rules.md` → Editor notes → Dual citation). Only purple is ever converted to a
reference-manager field, and only by an installed citation extension; core drafts tags and never
writes those fields. A draft that leaves the project and carries citations gets a Markdown
`_trace.md` sidecar beside it, one row per cited statement, graded *primary verified*, *compiled
source* or *unsupported* by the claims check before each handoff. The project's `Referencing
method` (`none | manual | extension`) lives in `5-System/user-preferences.md`, is asked once by the
Document branch, and changes only how finalization works and how tracked review treats existing
fields.

Once a deliverable is a file the team edits, the `review` branch takes over from `document`.
`build_docx.py --revise` cannot write tracked changes and rebuilds the runs it touches, so
`scripts/tracked_edit.py` is the only editor on such a file. It is additive by construction: every
edit is a `w:ins`/`w:del` or comment by "Claude (AI)", replies thread under the parent comment,
and fields, hyperlinks and other authors' tracked text are opaque. Replies to client-addressed
comments (`Note to ...`) are refused, and `--apply` is all-or-nothing. `--check` is the evidence a
pass was safe: rejecting Claude's changes reproduces the source, and everything from the source is
byte-identical. It has been exercised on a hand-built fixture, not yet on a Word-authored file.

`deck` additionally ships **no** brand or neutral presentation master, and there is no global,
machine-wide template library to fall back to — the `machine-setup` branch that once created one was
retired with the fleet model it belonged to (§5.4a). `deck-rules.md`'s precedence is the user's
explicit selection, then a project-specific template the user has placed in `1-Inputs/Templates/`; if
neither is available, `deck` reports itself unavailable rather than inventing a brand or neutral
master.

---

## 10. Capabilities, hosts, and delegation

### 10.1 The vocabulary

`.familiar/capabilities.json` — thirteen capability names and five states, both closed
sets:

```text
project-instructions   explicit-skills      implicit-skills     user-invocation-control
named-subagents        mechanical-enforcement                   file-read
file-write             document-tools       background-work     authenticated-knowledge
external-retrieval     hosted-publication
```

| State | Meaning |
|---|---|
| `active` | The released implementation exists and its health check passed. |
| `available` | Present in principle; separate setup or a live check is still required. |
| `unsupported` | The host cannot do this. |
| `unavailable` | Supported in principle, not present here. |
| `unknown` | Not determined. |

**No state implies a fallback.** Reporting `available` as though it were `active`, or narrating a
graceful degradation that does not exist, is the specific failure this vocabulary was built to
prevent. `test_adapter_capabilities_are_explicit_and_truthful` asserts the matrix uses only these
names and states and holds the specific truthfulness assertions (including `document-tools` never
being `active`).

### 10.2 Delegation and its fallback

Core ships two subagents: `lookup` (retrieval from `3-Knowledge/` — verbatim quotes
with citation anchors and a coverage report, never conclusions) and `web-lookup` (the same discipline
against primary sources on the open web, with URL and access date and a three-state result per
item). An optional extension may ship further workers under its own namespace; this manual covers core
only.

The separation is the point: retrieval workers return quotes and gaps; synthesis happens in the
caller. A worker cannot smuggle an inference into the answer because it does not produce answers.

Before any dispatch, `bootstrap.md` checks the current adapter's `named-subagents` state. Anything
other than `active` loads `retrieval-fallback.md` and the installed worker contract is performed
inline. A host with no row in `installed.json` falls in that case by construction (see "Hosts not
listed" below). Retrieval then costs main-context budget, and a multi-perspective review becomes sequential
personas in one context, so **the perspectives are not independent and the delivery must say so.**

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

Entry files: `CLAUDE.md` (claude), `AGENTS.md` (codex — and also written for claude and gemini),
`GEMINI.md` (gemini). `CLAUDE.md` and `GEMINI.md` are thin: they reference
`AGENTS.md` and add no protocol rules of their own, so the bootstrap text has one home.

Skill placement: `.claude/skills/<name>/` for claude, `.agents/skills/<name>/` for codex and gemini.
Workers ship as `.claude/agents/*.md`, `.codex/agents/*.toml`, and
`.gemini/agents/*.md`, already written in each host's native format. Codex and Gemini inherit the
current model rather than embedding Claude model names. Skills invoke a worker by its project-level
name (for an extension, `<namespace>-<agent>`, §11.3).

`INSTALL.md` → Host support is the user-facing comparison of all three, and `README.md` covers invoking
skills on each. Both are hand-written from this matrix. Host APIs change independently, so a change to
the matrix should land together with matching documentation updates.

**Hosts not listed.** Other coding hosts read `AGENTS.md` (Cursor, GitHub Copilot in VS Code, and
OpenCode do, for example), so the bootstrap loads there, but `installed.json` has no row for them. The rule in `extension-contract.md` is: a host with no row treats
every capability as `unknown`. It performs worker contracts inline through `retrieval-fallback.md`,
and it reports an extension route as unverified on this host and asks the user before running it,
rather than refusing silently or running silently. Some of these hosts read both `.claude/skills/` and
`.agents/skills/`, so each skill may appear twice in their pickers; the two copies are identical.

---

## 11. The extension contract, as core defines it

Core discovers extension manifests generically and contains no extension ID. Contract version `1.1`,
a UTF-8 JSON manifest named `familiar-extension.json` at the package root, with
`extension-manifest.schema.json` authoritative for machine validation and `extension-contract.md`
as its prose companion.

### 11.1 Manifest shape

Required: `contract` (const `1.1`), `id`, `display_name`, `version` (semver), `core` (a compatibility
range), `type` (`workflow` | `specialty` | `enforcement` | `integration`), `namespace`,
`contributions`, `capabilities`, `unavailable_behavior`, `package`. Optional: `compatible_with`,
`conflicts`.

`contributions` requires four arrays — `routes`, `skills`, `agents`, `state_surfaces` — and permits
two lifecycle-fragment arrays: `checkin_fragments`, `track_presets`, each a list of package-relative
file paths. A route is an object with `id`, `skill`, and `select_when`. A state surface is the
four-field object of §6.5.

`capabilities` requires `required` and `optional` arrays. `unavailable_behavior` is one of `hide`,
`degrade`, `report-unavailable`, applied when an *optional* capability is missing. `package`
requires `update_source`.

There is no separate extension registry file. An extension exists exactly when its skill folder is
present on disk in a host's native skill location, discovered by checking that folder's own
`familiar-extension.json` manifest directly. A route's `host_status` is therefore computed at read
time — comparing the manifest's required and optional capabilities against `.familiar/installed.json`'s
adapter table — rather than stored anywhere.

### 11.2 What validation actually enforces

**Nothing validates an extension when a user drops it in.** There is no installer or validator at
runtime (§12), and a drop-in is a plain folder merge. Validation happens only on the maintainer side,
for the maintainer's own extensions, through the gate suite in the source repository:
- `test_extension_manifest_schema_matches_declared_contract`: every manifest declares the
  contract version the shipped schema defines.
- `test_extension_manifests_resolve_and_do_not_collide`:
  - required fields are present, contract is `1.1`, and `id` equals `namespace`;
  - the `core` range floor is at least the first supported core version;
  - the manifest version matches the package's `VERSION`;
  - every declared skill exists;
  - skill and materialized agent names do not collide with core or with each other.

A third-party extension built from the extension template gets no such check from core; its author
works through the template's `CONTRACT-CHECKLIST.md` and, where the template includes it, its
standalone `check_extension.py`.

Capability evaluation is per adapter and recorded under `host_status`. Missing required capabilities
make the extension unavailable on that host. Missing optional capabilities apply `hide`, `degrade`,
or `report-unavailable`; the bootstrap checks that status before selecting an extension route.

Core route IDs are reserved. Registry order controls display order only — it never grants override
precedence.

### 11.3 Namespacing and materialization

A plugin-scoped agent `<namespace>:<agent>` appears in a project as `<namespace>-<agent>`. No
tool does that rename at drop-in time. Each extension's drop-in folder ships already materialized:
agent files are named `<namespace>-<agent>` in every host's agent directory, their frontmatter
`name:` matches, and the skills invoke them by that name. The maintainer-side collision check (§11.2) verifies
the materialized names against core and each other.

### 11.4 Layout and removal

An extension's drop-in folder carries its package at `.familiar/extensions/<id>/package/` and its
skills and workers already in each host's native directories. Installing it is merging that folder
onto the project root. There is no registry recording this — presence on disk plus the package's
own manifest is the record, and `.familiar/installed.json` still tracks per-adapter capability
state. Removing an extension is deleting the paths its `_about.md` lists. Nothing checks whether
the user edited one of those files first, so the user should look before deleting.

---

## 12. Update and extension lifecycle

There is no install step for a new project. `familiar-workspace/` ships pre-baked and complete —
protocol, every host's native skills and workers, scaffolded empty content folders, and a filled-in
`.familiar-project` (`created: not-yet-set`) — so a user gets a working project just by renaming the
folder and opening a coding host inside it. `checkin` stamps `created` with a real date, and asks for
a `Project Name` (pointing to `/system-settings` → Preferences if the project has no familiar
Signature of its own) the first time it runs in the project (§4.1, §8.2) — the setup skill retired 2026-09-04 and is no
longer invoked for this. No script scaffolds a project, nothing is compiled at that point, and there is
no `SessionStart` prose injection or separate rule compiler.

One script updates a project, `.familiar/scripts/update.py`, and the user runs it from a terminal, never
a session (§12.1). `system-settings` → Update (§5.4a) is the only route that concerns updates; a user
reaches it deliberately, never as a route match, since the whole `system-settings` menu is `(user-only)`.

### 12.1 What Update does

**Update only reports; it changes nothing.** `references/update.md` reads the project's version from
`.familiar/installed.json` → `core.version` and the marker, and the new release's `VERSION`. It also
reads `core.build` from both `installed.json` files. A release build
stamps `core.build` with the commit it came from (with `-dirty` if the tree had uncommitted
changes); a copy taken straight from the maintainer's source tree has none.
- A newer version is an update.
- The same version with a different build is also an update.
- The same version with a missing build is reported as undecidable, and the user chooses.

Update then checks the `state-schema` lines, since a mismatch is a migration no procedure performs.
Finally it hands off: when the project carries `.familiar/release-manifests/familiar.json` it gives
the user the updater command with both paths filled in, and otherwise it points to the hand
procedure in `INSTALL.md` → Updating (a fresh folder, extensions re-dropped, the five content folders
moved across).

**The updater.** `update.py` runs from the new release's copy against the project, because it reads
one folder and writes another, which no session bound to either can do (`CORE-WORKSPACE-SILO`). It
decides file by file against the project's own release manifests, one per owner (`familiar` for core,
each extension its own id), which a release build writes with a fingerprint of every file it ships:
- `same`: the project's copy matches the new release.
- `update`: it still matches what the old release shipped, so replacing it loses nothing.
- `diverged`: it matches neither, so someone edited it. It is left alone and reported.
- `add`: new in this release.
- `retired`: no longer shipped. It is left in place (`CORE-NO-DELETE`) and stays listed in the
  manifest so later runs keep reporting it.

Entry files are compared and replaced only inside their `familiar:start`/`familiar:end` block. The
updater stops before any write when the schemas differ, when the project has no core manifest, or
when a release file does not match its own manifest. Extensions are updated only from a drop-in
named with `--extension`; each installed extension's declared `core` range is checked either way.
`--apply` copies every file it replaces, and the old marker, into
`5-System/_update-backups/<old>-to-<new>_<date>/` first, then sets only the `familiar-version:` line and
runs `project_check.py`. Listing files per owner and checking before writing is what makes an
in-place update safe: an extension's package is never part of core's update.

One hazard remains. Several files under `4-Trackers/`, `3-Knowledge/` and `2-Drafts/` carry release
prose alongside project data, and they move across unchanged. A format change in a new release does
not reach them without a manual look, which Update tells the user to take.

Removing an extension is deleting the paths its drop-in folder added, listed in that extension's own
`_about.md`. There is no registry to update alongside it — presence on disk is the record.

### 12.2 No Python at runtime

Routing, skills, and state are files a host reads directly, and setup needs no Python. The
updater (§12.1) is a standard-library Python script; the hand procedure needs none. Python is used only by the optional document and extraction scripts and the small read-only helpers
under `.familiar/scripts/`. The document scripts check their own dependencies with `--health-check`
and degrade as their skills describe, and `doctor.py` (§9.5) reports the whole toolchain at once.

---

## 13. Quality gates

The gate suite lives in the maintainer's source repository, not in this download, and runs before
every release. It is run as `python tests/quality_gates.py` — 135 tests, all passing at this release;
its final line reads `Ran 135 tests …
OK`. This section describes what it covers so you know which claims in this manual are mechanically
defended and which are prose.

**Bootstrap and routing (6)** — bootstrap size, rule presence and neutrality; the registry's size and
resolution rules; `AGENTS.md`'s embedded bootstrap matching `.familiar/core/bootstrap.md`;
route/frontmatter `(user-only)` consistency; every skill routed or listed as an exception; worker
fallback owned by bootstrap.

**Skill contracts (5)** — six-field contract present and non-boilerplate; required/conditional and
required/excluded disjoint; canonical capability vocabulary; read-only skills declare no
`file-write`; every skill declaring `file-write` loads file-handling plus the relevant prose or
state rules.

**References (3)** — stable `CORE-*` rule citations resolve; `file.md → Heading` section references
resolve; named-procedure references resolve (**printed, not asserted** — a heuristic kept
non-blocking on purpose, ~17 residual prints, none real).

**JSON and schema integrity (3)** — every shipped JSON parses; the extension manifest schema's
`contract` const agrees with the contract document; extension manifests resolve and do not collide.

**Truthfulness and payload (4)** — adapter capabilities explicit and truthful; document-tools
scripts genuinely health-check and round-trip (this one actually builds a `.pptx` and a `.docx`);
router audit accepts only explicitly quarantined partial libraries; **this document still describes
this tree** (see “How this document stays true” above).

**Environment (4)** — core and its extensions share one release version; the shipped demo uses the
current state schema; Markdown links resolve with exact Git-tracked case (compared against Git's own
spelling, so a case defect is caught even on a case-insensitive filesystem); **`.claude/skills/` and
`.agents/skills/` are byte-identical** — the new gate. The two trees hold the same skill content
twice because host discovery paths differ and Windows symlinks are unreliable; each skill's own
`agents/` subfolder (per-host invocation-policy metadata such as `openai.yaml`) is excluded since it
has no shared counterpart, but nothing else catches drift between the two copies, so this gate is the
whole enforcement.

Two further maintainer-side checks sit outside the suite: a router audit that inspects skill and
route structure, and a release build that assembles this download from an allowlist and refuses
anything private or unlicensed. Neither is part of the download. What you can run yourself, on your own
copy, is `.familiar/scripts/doctor.py` (§9.5) for the document toolchain and
`.familiar/scripts/project_check.py` for project health.

---

## 14. Known limits, stated plainly

1. **Rules are instructions, not enforcement.** Every `CORE-*` rule depends on model compliance.
   Mechanical enforcement is `available` on Claude, Codex, and Gemini, and the
   guard layer is excluded from the core payload. A pattern-matching guard also has a confirmed
   structural ceiling — an interpreter one-liner is invisible to any verb-matching regex — so the
   honest claim is "the common-case boundary is enforced where the host supports it", never
   "familiar prevents X".
2. **`document-tools` is unverified by construction.** No install-time verification mechanism exists
   for any capability; the matrix is hand-asserted. The truth is whatever the live `--health-check`
   reports on the machine running the session. On a Python-less host, deck and document building do
   not work, and the design says so rather than degrading silently.
3. **`deck` ships no template and no global library.** The only source is a project-specific
   template the user places in `1-Inputs/Templates/`; without one, `deck` reports itself unavailable
   rather than inventing a brand or neutral master (§9.5).
4. **There is no calendar surface.** Date changes propagate to `4-Trackers/timeline.md` and memory
   per `calendar-rules.md`, and familiar tells the user what to put on their own calendar. The
   half-built `calendar` skill was withdrawn from core rather than left implying an integration
   exists.
5. **Concurrency is detection, not control.** `CORE-STALE-WRITE` catches a cooperating second
   writer. One active writer at a time remains the documented model.
6. **`user-invocation-control` is instruction-level on Gemini.** Claude frontmatter and
   Codex policy metadata enforce it natively; Gemini relies on registry rule 3.
7. **The bootstrap has no headroom.** 500/500 words, hand-synced into `AGENTS.md` with no
   regeneration script. Any material addition requires a subtraction.
8. **Host features evolve independently.** Active native workers are backed by the
   maintainer's native-install fixtures, but host-format changes can still require updates to the
   shipped worker files and documentation. Hosts other than these three have no capability record
   (§10.3).

---

## Appendix A — core file inventory

**Protocol (`.familiar/core/`):** `bootstrap.md`, `_index.md`, `routes.md`, `state-schema.md`,
`extension-contract.md`, `familiar-behavior.md`,
`file-handling.md`, `voice.md`, `plain-language.md`, `familiar-voice.md`,
`retrieval-fallback.md`, `running-scripts.md`, `status-format.md`, `handoff-format.md`,
`check-in.md`, `ingest.md`, `deck-rules.md`, `deck-build.md`, `docx-rules.md`,
`calendar-rules.md`. `capabilities.json`
and `extension-manifest.schema.json` sit one level up, at `.familiar/` alongside the `core/` folder.

**Agents:** `lookup.md`, `web-lookup.md`.

**Entry files:** `AGENTS.md` (carries the bootstrap verbatim), `CLAUDE.md`, `GEMINI.md` (both thin,
resolving to `AGENTS.md`).

**Scripts shipped in `familiar-workspace/`:** `skills/draft-document/scripts/build_pptx.py`,
`skills/draft-document/scripts/build_docx.py`, `skills/ingest/scripts/extract_pdf.py`,
`skills/ingest/scripts/extract_encite.py`, `skills/ingest/scripts/source_register.py` (the input
ledger ingest scans before and records after, `3-Knowledge/_source-register.md`) (each under both `.claude/skills/` and `.agents/skills/`, per
`test_claude_and_agents_skill_trees_are_byte_identical`), and `.familiar/scripts/project_check.py`,
the read-only project health check `checkin` runs at `check-in.md` → 4. Health check (stdlib only;
if it cannot run, check-in makes the same checks by reading files). Beside it, `.familiar/scripts/timeline_views.py`
renders `4-Trackers/_views/next-two-weeks.md` and `gantt.md` from `timeline.md`, stamped with
its revision, and lists dependency problems without moving any date; `--json` prints the same
overdue/upcoming/problem lists as data and writes nothing (the separately distributed fleet hub reads that); `--json --window N` widens "upcoming" to N days for that reader, while the views stay at 14. `.familiar/scripts/meetings_view.py` does the same for `4-Trackers/meetings.md` (optional): it expands each series rule, applies moves, cancellations and extras, and writes `_views/meetings-next-weeks.md`; `--json --window N` prints the occurrences and problems as data, each occurrence with its agenda from the file's `## Agendas` section. Three more read-only helpers count what the model
used to estimate: `ref_count.py` (claim tags and citation markers on a page, against its
`ref_carry_through` stamp; ingest step 5), `index_check.py` (index rows against page front matter;
ingest step 6), and `task_frontier.py` (open tasks whose blockers are cleared; triage, ongoing-work,
check-in). Each has a fallback: if it cannot run, the step is done by reading and says so.
`.familiar/scripts/tracker_edit.py` is the one script that writes a single milestone or task change (`milestone --id M-04 --due ... --reason ...`, `task --id T-12 --done`; `--dry-run` previews): it checks and bumps the revision, replaces the file atomically, appends the status-log entry, regenerates the views, and lists the places (snapshot, tasks, downstream milestones) that still name the old date. It never deletes a row and never moves another date. The fleet hub calls it for cross-project edits. `--title "..." --reason ...` renames a milestone or task in place (IDs never change; a blocker that names the old title in words is listed, not rewritten). `tracker_edit.py meeting <add-series|add-oneoff|move|cancel|edit-series|rename|agenda>` does the same for `meetings.md` (a move or cancel changes one date of a series through an exception row, or a single meeting in place, and a moved date takes its agenda with it; `edit-series` changes the series row itself; `agenda --id S-01 --date YYYY-MM-DD|standing --items "A; B"` or `--none "reason"` sets one date's topic list or a series' standing list), refuses a change that would leave the file with a problem it did not have, and reports a new overlap.
`.familiar/scripts/draft_save.py` is the save path for `2-Drafts/` (`next`, `register`, `adopt`, `migrate`; it plans every
move, refuses on any existing target, never deletes; `migrate` folds a flat legacy `2-Drafts/` into per-deliverable folders after a `--dry-run` the user has seen; `next` prints `source now at:` for the current
version after its moves, and `adopt` validates every input before it moves anything);
`index_check.py --sync` is its one write, copying each page's dates into its existing index row; `file-handling.md` → Saving under `2-Drafts/` holds the
equivalent manual steps.
No skill ships a `scaffold.py` — the workspace is already scaffolded, filled in as far as it
truthfully can be. The router audit and `profile_deck_template.py` are maintainer tooling and are not shipped. The
preflight **does** ship: `.familiar/scripts/doctor.py` (Windows, macOS and Linux, standard library
only). It checks the optional document toolchain (§9.5), and `INSTALL.md` names it.

## Appendix B — record shapes

`.familiar/installed.json`

```json
{
  "schema": "1.1",
  "core": { "id": "familiar", "version": "1.0.0" },
  "adapters": { "claude": { "project-instructions": "active", "...": "..." } }
}
```

A release build adds `"build": "<commit>"` inside `core` (§12.1). The source tree never carries it.

There is no separate extensions registry file: an installed extension is discovered by its package's
presence under `.familiar/extensions/<id>/package/` plus its own `familiar-extension.json` manifest
(§11.4), not by an entry here.

There is no `.familiar/backups/` and no transaction record; there is no installer to need them. The
updater's own backups go to `5-System/_update-backups/` (§12.1).
