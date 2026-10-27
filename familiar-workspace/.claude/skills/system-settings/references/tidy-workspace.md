# `/system-settings` → Workspace tidy

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

A housekeeping pass over the workspace, for a user running several projects who does not always
pull finished drafts out or delete what is done with. **Propose, then act on approval — never move
or rename a file that was not in the approved table** (`CORE-NO-DELETE`: familiar never deletes;
this skill never even moves unasked).

## Context contract

- **Required context:** `.familiar/core/file-handling.md` → Workspace map, `.familiar/core/status-format.md` → Templates, `2-Drafts/`, `3-Knowledge/`, and `5-System/` for what is still live
- **Conditional context:** `2-Drafts/_draft-index.md` for every drafts decision, and `2-Drafts/<deliverable>/_versions.md` when a deliverable has a folder; `_knowledge-index.md` for knowledge-page checks; the `Tidy standing approval` line of `5-System/user-preferences.md` when present; project tracks only when grouping suggests a workstream split.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** only the moves the user approved (individually, or through a standing approval that covers them), into `_del/` holding folders, each recorded in that folder's `_moves.md`, plus one `5-System/Memory/status-log.md` entry. Never deletes
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** Every candidate has an explicit KEEP/MOVE/REORGANIZE/RENAME/ASK disposition, and only individually approved filesystem changes and required index updates are applied.


**Scope:** `2-Drafts/`, `3-Knowledge/`, `.scratch/`, and stray files anywhere else in
the workspace outside the two folders below. `1-Inputs/` is out of scope — read-only, never
touched. `5-System/` is out of scope — its files are living state with their own update
discipline in `status-format.md` → Update rules (non-negotiable), not clutter.

## Step 1 — Survey

**`2-Drafts/`** — `_draft-index.md` is the authority on what is current, and each deliverable's
`_versions.md` on its history; judge every file against them, never against its version number. A
higher version is not evidence of approval or of being current: drafting lineages fork (a newer
`v2` can follow an older `v4`), and a later version can be built from an unverified one. The save
procedure in `file-handling.md` → Saving under `2-Drafts/` already moves superseded versions into
`<deliverable>/_superseded/`, so this pass only looks for what that procedure did not cover.

- **Current** in the index: never a candidate. KEEP, and do not list it.
- **Already in `<deliverable>/_superseded/`:** filed correctly. KEEP, and do not list it.
- **A deliverable's `_brief.md`:** its scoping record from `/deliverable-brief`, also before any
  draft exists. KEEP, and do not list it.
- **Legacy superseded, still flat:** a file the index lists as superseded that sits outside a
  `_superseded/` folder: a **supersede-candidate**.
- **Legacy flat lineage:** a deliverable with two or more versions still in the `2-Drafts/` root.
  Propose REORGANIZE: the folder, `_superseded/` and `_versions.md` steps from `file-handling.md`,
  one `_versions.md` line per known version with `—` for a rationale that is not recorded. Never
  invent one.
- **Not in the index at all:** it may be an external edit or an untracked current copy. Ask which
  deliverable it belongs to ("adopt as the next version of `<slug>`?"); never infer from its number.
- A lone `FINAL`-status file: **do not assume it was already promoted out.** Promotion is a copy
  the user makes; the file can legitimately still sit here afterward. Ask.
- Audit sidecars (`*findings.json`, document-build specs) stay beside the output they document.
  A render or export that shares its stem with a superseded draft (the PDF of a superseded
  `.docx`) is superseded with it.
- A file that does not match the naming convention at all: flag it, do not guess a disposition.
- Scripts, `__pycache__`, an unzipped package, or a folder `file-handling.md` → Workspace map does not list, in
  `2-Drafts/` or the workspace root: scratch that landed in the wrong place. Low band, ASK, with `.scratch/` or
  `_del` as the proposed home.
- An index row whose current file is missing, or a `_versions.md` line naming a file that is not
  there: report it as an index finding. Fix the index only with approval.

**`.scratch/`** — report its size and the age of its newest file. If it holds anything, propose
MOVE TO `_del` for the contents; scratch is disposable, but this skill still only moves, never
deletes. It is never an index finding.

**`3-Knowledge/`** — cross-check pages against `_knowledge-index.md`:

- A page with no index row, or an index row with no matching page, is a **broken-link finding**
  regardless of file count.
- If pages have accumulated to where the user says navigation is hard, propose an optional grouping
  scheme (by source type, or by date-bucket) — this touches every path that cites a page (the
  index, other pages, memory), so it is a REORGANIZE proposal, never done silently.
- Where the pages fall into three or more clear subject groups and `5-System/project-config.md` has no
  `## Tracks` table, say so and tell the user to run **`/system-settings` → Tracks** — that is a workstream
  split, not a folder problem, and grouping the folder would not fix retrieval. Mention it once;
  never propose a track table here (this skill does not touch `5-System/`).
- Leave `_extract-*.md` files alone. Flag only an extract with no matching synthesis page — that
  means an ingest was interrupted, not that the extract is clutter.

**Elsewhere** — any file sitting loose in the workspace or `4-Trackers/` that is not one of the
known living files (`file-handling.md` → Workspace map) is a stray-file finding.

## Step 2 — Confidence bands, then the table

- **High** — a legacy flat file the draft index lists as superseded: propose MOVE TO `_del`.
- **Medium** — a lone `FINAL` draft, or a broken-link finding: propose a disposition, name the
  uncertainty, and ask.
- **Low** — anything off-convention or unclear in purpose: no proposed disposition, ASK outright.

Present one row per file or group: path, finding, proposed disposition (**KEEP / MOVE TO `_del` /
REORGANIZE `<target>` / RENAME `<target>` / ASK**). This table is the judgment surface — the user
edits or approves each row. A blanket "yes to all" is valid only if the user says it explicitly; do
not treat silence or a general "looks good" as row-by-row approval.

**Standing approval.** A project can pre-approve one narrow, reversible operation. If
`5-System/user-preferences.md` has a line
`Tidy standing approval: move drafts the draft index lists as superseded to 2-Drafts/_del/`, rows in
exactly that class are marked **pre-approved** in the table and carried out in Step 3 without a
per-row answer. The table is still shown first, and the user can strike any row. Nothing else is
covered: no Medium or Low row, no REORGANIZE or RENAME, nothing outside `2-Drafts/`, and never a
deletion. The user adds or removes the line by saying so; `/save` → to-memory records it there.

## Step 3 — Execute only approved rows

- **MOVE TO `_del`** — create `<folder>/_del/` if it does not exist and move the file there with
  the Bash tool (`Move-Item`, not `rm`/`del` — `CORE-NO-DELETE` rules them out here, and the
  optional guard layer blocks them outright where it is installed). This skill never deletes;
  it relocates to a holding area the user empties themselves.
  Use a folder-scoped `_del/` (`2-Drafts/_del/`, `3-Knowledge/_del/`)
  so context stays with the material; for stray files outside either, use
  `_del/`. Append each move to that folder's `_moves.md` as it happens —
  `| YYYY-MM-DD | <original path> | <new path> | <approved individually / standing approval> |` —
  so any move can be undone by moving the file back. Create `_moves.md` with that table header
  on first use; never rewrite earlier rows.
- **REORGANIZE** — create the approved subfolder(s), move the files, then update
  `_knowledge-index.md`'s paths in the same pass. An index left stale after a move is worse than
  no index.
- **RENAME** — only to fix a naming-convention violation, and only on user confirmation: a straight
  filesystem rename, not a new dated copy (`CORE-COPY-ON-EDIT` governs content changes, not
  fixing a filename).

## Step 4 — Log it

If anything moved, append one `5-System/Memory/status-log.md` entry (`state-schema.md` → Template — `Memory/status-log.md` (append-only; oldest entry on top, newest appended at bottom), type
`progress`): counts moved to `_del` (and how many under a standing approval), counts
reorganized, the date, and where the `_moves.md` record is. Skip this step if the user
approved nothing — a no-op pass is not a loggable event.

## Guardrails

- Never move, rename, or reorganize a file that was not on the approved table. Missing user input on
  a row means that row is untouched, not defaulted to KEEP or to the proposed action.
- `_del` is a holding area, not deletion. Never empty it, on this pass or a later one — clearing it
  out is the user's action, same as promoting a draft out of `Drafts`.
- `1-Inputs/` and `5-System/` are never in scope for this skill, regardless of how
  cluttered they look.
