# familiar operating behavior

The bootstrap owns session boundaries and routing. This file defines neutral project-lifecycle
behavior for a selected project route; it is never an additional startup checklist.

## Start or configure

When the workspace or authoritative configuration is absent, name `/checkin` (under `project.status`)
as the command that establishes it and let the user start it — per Resolution rule 3, never run it.
A quick setup may defer context. A full setup records only confirmed facts and installed extension
contributions.

## Continue work

Use `project.status` when the user asks what is open, returns after a break, or needs current
blockers. Read the snapshot first, then tasks, timeline, open handoffs, and only the recent activity
entries required to resolve a contradiction. Do not load project history for an unrelated request.

## Execute a focused task

Select one route and one skill. Read its context contract before project files. Complete the
smallest useful result, record only declared updates, and report missing capability or context
instead of silently widening scope.

## Capture durable change

Use `project.memory` for a confirmed decision, action, risk, preference, or material state change.
Each fact has one authoritative home under `state-schema.md`. Derived summaries may point to that
home but do not become another source of truth.

## Pause or switch agents

Use `project.handoff` for genuinely in-flight work that has no other state surface. Reconcile
durable facts first. The next focused session reads current state before the handoff and stops on a
revision conflict. The documented operating model is one active writer at a time.

## Close work

Close tasks, tracks, handoffs, or the project only with explicit user confirmation. Preserve history
under `CORE-NO-DELETE`. A closeout produces a derived summary and final state updates; it does not
rewrite the activity log or remove source material.

## Extension behavior

Extensions add namespaced routes and state contributions through their manifests. Load one only
when its route is selected. Missing or removed extensions do not alter core behavior. Collision,
compatibility, and unavailable-capability behavior follow `extension-contract.md`.
