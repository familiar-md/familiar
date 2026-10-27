# `/system-settings` → Tracks

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

Owns the whole track lifecycle: the format, the tagging discipline, and the flow that changes it.

## Context contract

- **Required context:** `.familiar/core/file-handling.md` → Integrity and delivery, `.familiar/core/status-format.md` → Update rules (non-negotiable), `.familiar/core/state-schema.md` → Template — project-config.md, `5-System/project-config.md`, `5-System/Memory/status-snapshot.md` + `5-System/Memory/status-log.md`, and `4-Trackers/`
- **Conditional context:** an installed extension's `track-presets.md` only when its manifest contributes one to the active project
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** `5-System/project-config.md`'s `## Tracks` table; the re-cut `5-System/Memory/status-snapshot.md`;
  retagged `4-Trackers/tasks.md`, `4-Trackers/timeline.md`, and `3-Knowledge/_knowledge-index.md`; and one
  `5-System/Memory/status-log.md` entry
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** The user-confirmed track table, affected state tags, and snapshot grouping agree, with one material-change log entry when state changed.

## Format and tagging discipline

A **track** is a parallel line of work inside one project: the financial model, the market
scan, the report. Tracks share one project, one set of constraints and one timeline, so they
stay in one workspace. They differ day to day, so every state surface carries a track tag and can
be filtered. Tracks are labels on one set of files, never separate folders. The `## Tracks` table
in `5-System/project-config.md` (`state-schema.md` → Template — `project-config.md`) is the **naming
authority** — every track tag written anywhere in the workspace uses a code from it.

**Tracks are discovered, not declared.** A user rarely knows the shape of the work at kickoff, and the
shape changes as the project changes. This skill exists so that adopting or reshaping tracks costs
one command at any point in the project, rather than a decision at the moment of least information.

**The gate — tracks are optional.** If `5-System/project-config.md` has no `## Tracks` table, write no tags
anywhere. A single-thread project pays nothing for this, and most projects start without one.

**`5-System/project-config.md` is the naming authority.** Each track has one canonical name and one short
code, declared there. Never invent a track name at write time, and never carry an identifier scheme
in from a source document — a brief's own phase numbers, section numbers or letters. Where a source
uses its own names, map them to the declared codes and say so once.

**When work fits no declared code, tag it and escalate — never mint a code.** Tag the item with the
closest declared code, or `shared` where it spans more than one, name the mismatch to the user once in
the reply, and tell them to run `/system-settings` and pick Tracks. A new code exists only after this flow writes it
into `5-System/project-config.md`. Minting one mid-write puts a tag on three surfaces that the naming
authority does not recognise.

**Where the tag goes:**

| Surface | Form |
|---|---|
| `5-System/Memory/status-snapshot.md` | One `### <Track>` heading per track; the standard bullets under it |
| `5-System/Memory/status-log.md` | In the header: `## [YYYY-MM-DD] <code> \| <type> \| <headline>` |
| `4-Trackers/tasks.md` | One `### <Track>` heading per track under `## Open` |
| `4-Trackers/timeline.md` | A `Track` column |
| `3-Knowledge/_knowledge-index.md` | A `Track` column |
| `5-System/Decisions/<slug>.md` and `5-System/Handoffs/<file>.md` | A `**Track:**` line under the title |

**Cross-cutting work is tagged `shared`.** Anything touching more than one track — a shared
credential, a schedule move, a decision that constrains two tracks — takes the code `shared`, never
the code of the track that happened to raise it. `shared` is what makes a cross-track change
findable later. A cross-cutting item filed under one track is the failure this dimension exists to
stop.

**Tag, do not partition.** Tracks are labels on one set of files — never separate folders, never a
second snapshot, never a register file holding per-track status. Filter at read time instead: to
work one track, read the whole snapshot, then the log entries whose header carries that code or
`shared`. Partitioned state drifts apart; a filtered view cannot.

**Convergence stays in the existing machinery.** Where tracks converge on one deliverable, the
dependency lives in `4-Trackers/tasks.md` (`Blocked by:`) and `4-Trackers/timeline.md` (`Depends on`).
A track labels work; it does not order it. Never restate a dependency as a track relationship.

### Tracks are discovered, and they change

**No track is ever created here, or during a check-in.** Setting up, adding, splitting,
merging, retiring and reviving tracks is one user-invoked flow: **`/system-settings` → Tracks**. Tell the user to
run it; familiar cannot call it (it is User-only).

Three consequences to hold while writing memory:

1. **A project with no `## Tracks` table is normal, not unfinished.** The first check-in deliberately
   writes none. Write no tags, and never propose a table outside the check-in lint's one-time
   detection.
2. **A retired track's existing tags stay valid and are never rewritten.** A code keeps meaning what
   it meant; only its status in `5-System/project-config.md` changes. Never reuse a retired code.
3. **Tagging goes forward only.** When tracks change, `5-System/Memory/status-log.md` keeps whatever tags its entries
   already carry — append-only (`CORE-NO-DELETE`). Only the present-tense surfaces are retagged.

## Step 1 — Read the current state

Always, before proposing anything:

1. `5-System/project-config.md` — the `## Tracks` table, if one exists, and the
   installed **Extensions** entry.
2. `5-System/Memory/status-snapshot.md`, `4-Trackers/tasks.md`, `4-Trackers/timeline.md`,
   `3-Knowledge/_knowledge-index.md`.
3. Recent `5-System/Memory/status-log.md` entries.

Then say which mode applies and confirm it with the user before acting:

| The project has | Mode |
|---|---|
| No `## Tracks` table | **Adopt** — step 2, then step 3 |
| A table, and the user wants a change | **Reshape** — step 4 |
| A table, and the user asked for a review | **Review** — step 5 |

## Step 2 — Propose the track list

**Do not ask the user to name tracks from memory.** Read the state and propose; the user edits. A blank
prompt gets the tracks the user happens to recall, which is the flat list's own bias repeated.

**For each installed extension**, check its manifest for a declared track-preset contribution.
Where a preset matches the project's work type,
type, offer it as the starting point and say where it came from. A preset is a **starting point the
user edits freely** — never a fixed structure. Where no preset file exists, or none matches, derive
from state as below and say so.

**Deriving from state.** Group the open items, timeline rows, knowledge pages and recent log entries
by what they serve. One track per group. Then:

- **Name every item you cannot place.** Never force an item into a track to make the list tidy — an
  unplaceable item is usually either a `shared` item or a missing track.
- Propose a short lowercase code per track — `model`, `landscape`, `report`. One word where one
  word works.
- Three to six tracks is the usual range. **Above about eight, say so**: that is normally several
  projects sharing a folder, and splitting the project is the better fix. State it once, then do
  what the user decides.
- **Where the work is genuinely one line start to finish, say that and stop.** Tagging a
  single-thread project is pure overhead. Recommending no tracks is a valid outcome of this skill.

Present the proposal as a table — code, track, scope in one line — followed by the items you cannot
place. That table is the judgment surface; the user confirms, renames, merges or drops before
anything is written.

## Step 3 — Apply

On approval, in this order:

1. Write the `## Tracks` table to `5-System/project-config.md` (`state-schema.md` → Template — `project-config.md`).
2. **Tag forward, not backward.** Tag `5-System/Memory/status-snapshot.md`, `tasks.md`, `timeline.md` and
   `_knowledge-index.md` — the surfaces that describe the present. Leave existing `5-System/Memory/status-log.md`
   entries untagged: the log is append-only, and relabelling history breaks that rule for no
   retrieval gain. New entries carry a code from that day on.
3. **Retire any imported identifier scheme.** Where past entries carry phase numbers, section
   numbers or letters from a source brief, record the mapping to the new codes once under the table
   in `5-System/project-config.md`, then use the codes only. Competing identifier schemes are what this table
   exists to prevent.
4. Re-cut the snapshot to its ceiling while regrouping it (`status-format.md` → Update rules (non-negotiable)).
5. Append a `5-System/Memory/status-log.md` entry, and tell the user what changed on each surface.

## Step 4 — Reshape

Projects reshape. Each operation below is a config change: update the table, then append a
`5-System/Memory/status-log.md` entry saying what moved and why.

**Add.** A new line of work appears. Add the row, tag forward from today. Nothing retrospective.

**Split.** One track grew two independent halves — no shared blockers, no shared deliverable. Ask
the user which existing items go to which side. Retire the original code and add both new ones. Record
the old code in the mapping note so a reader of past entries can follow it.

**Merge.** Two tracks turned out to be one. Keep the clearer code, retire the other, record the
mapping. Retag the present-tense surfaces; leave the log.

**Retire.** The work is finished or dropped. Set `closed YYYY-MM-DD` in the table. **A retired
track's existing tags stay valid and are never rewritten** — the code keeps meaning what it meant.
Only its status changes. Do not reuse a retired code for different work.

**Revive.** Set the status back to `active`. Nothing else changes.

**Pause.** Set `paused`. A paused track is skipped by the check-in's dormant-track lint, which is
what stops a deliberate pause reading as neglect.

## Step 5 — Review

A health pass over the tracks themselves, reported to the user as findings — change nothing here:

- **Unplaceable items** — open items, pages or milestones with no track tag, or a tag that is not a
  code in the table.
- **Imported identifiers** — any phase number, section number or letter from a source document being
  used as a track name.
- **Dormant** — a track marked `active` with no log entry in the last two check-in periods. Ask
  whether to pause it.
- **Overweight** — a track holding most of the project's open items. Ask whether it wants splitting.
- **Under-used `shared`** — cross-cutting items tagged to one track. This is the most common tagging
  error, because the natural pull is to tag an item with whatever was being worked on when it
  surfaced. Test each: *if this track were cancelled tomorrow, would this item disappear with it?*
  If it would survive, it is `shared`.

## Guardrails

- **Propose, then act on approval.** Never write the table, retag a surface, or retire a track the
  user did not confirm.
- **Never rewrite `5-System/Memory/status-log.md`.** Append-only (`CORE-NO-DELETE`). Tags go forward only.
- **Never invent a code at write time.** If an item needs a track that does not exist, say so and
  ask; do not add a row silently.
- **A dependency is not a track relationship.** Where tracks converge, the edge lives in
  `tasks.md` (`Blocked by:`) and `timeline.md` (`Depends on`). Never restate one as the other.
- Where the user asks for something this skill cannot resolve from state, ask. Never proceed on an
  assumed track list.
