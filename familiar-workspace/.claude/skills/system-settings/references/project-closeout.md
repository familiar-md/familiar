# `/system-settings` → Project closeout

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md` → Naming and copies, `.familiar/core/status-format.md` → Update rules (non-negotiable), project configuration and context, status snapshot, activity log, tasks, timeline, decisions, handoffs, and outputs under review.
- **Conditional context:** Source or extension state only when needed to verify a specific open obligation.
- **Excluded context:** Other projects, unrelated source content, and undeclared extension content.
- **Updates:** confirmed task/milestone/handoff terminal states, final snapshot and activity entry, and one derived closeout summary.
- **Capabilities:** file-read and file-write.
- **Completion:** Every known obligation has a confirmed disposition, authoritative state reflects the user's closeout decision, and history remains intact.

## Procedure

1. List every open task, milestone, blocker, handoff, decision consequence, and promised output.
2. Ask the user to confirm each disposition: complete, transferred, cancelled, or still open. Do not
   infer a terminal state from age or apparent completeness.
3. Reconcile confirmed dispositions across their authoritative surfaces using revision checks.
4. Append one material closeout event and update the final snapshot.
5. Write a derived closeout summary covering outcomes, remaining obligations, important decisions,
   and reusable de-identified lessons.
6. Ask before marking the project itself closed. If the user agrees, set the snapshot's `Lifecycle` to `closed` with a revision check (`status-format.md` → Update rules (non-negotiable)). If the project is on the fleet registry, tell the user the hub records lifecycle in its own registry, so they should run `python scripts/fleet_overview.py --set-lifecycle "<name>" closed` in the hub (until then the hub reports the mismatch and keeps treating the project as active), and that dropping the project from the registry is `/system-settings` → Fleet.

Apply `CORE-NO-DELETE`. Archiving or removing files remains the user's action.
