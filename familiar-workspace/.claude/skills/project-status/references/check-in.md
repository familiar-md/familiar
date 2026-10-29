# `/project-status` → Check-in

> Branch of the `project-status` router. Reached only from `/project-status`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

## Context contract

- **Required context:** `.familiar/core/check-in.md`, `.familiar/core/file-handling.md` → Integrity and delivery, `.familiar/core/status-format.md` → Read order & update protocol, project configuration, status snapshot, open tasks, timeline, open handoffs, and recent activity-log headlines.
- **Conditional context:** `.familiar/core/state-schema.md` → Templates only when establishing a fresh project; older activity entries only to resolve a contradiction; extension state only when its manifest declares a check-in contribution.
- **Excluded context:** Source documents, synthesized knowledge, other projects, and undeclared extension content.
- **Updates:** authoritative state surfaces named by `.familiar/core/check-in.md`; on a fresh project, also `.familiar-project`'s `created` line and `5-System/project-config.md`'s title line; no empty activity entry when nothing material changed.
- **Capabilities:** file-read and file-write.
- **Completion:** Current state is reconciled, detected inconsistencies are reported, and the next useful route is clear.

Read `.familiar/core/check-in.md` and follow it in order. Pre-draft from state before asking
questions. Apply `CORE-STALE-WRITE` to every living file and preserve the activity log as append-only.
