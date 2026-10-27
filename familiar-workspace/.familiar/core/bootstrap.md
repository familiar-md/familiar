# familiar bootstrap

If the active folder or its parent chain has no `.familiar-project`, do not bind, emit the signature,
or load project state — only setup or installation guidance may run.

Once found, before routing or project work, read `5-System/user-preferences.md` and
`5-System/project-config.md`'s title, relative to the marker's directory, and optional `~/.familiar/user-preferences.md` (the sole startup
exception to `CORE-WORKSPACE-SILO`). Project preferences win; the global signature applies unless the
project sets one.

Write `*(<signature>) familiar bound*` once, at the top of your first reply, as visible text, never
only in reasoning or collapsible commentary. Append `: <name>` from the project title when set. Use the retrieved
signature; use `n/a` only when a signature read failed, and `not set` when neither file
contains one. Never substitute for an unattempted read.

## Non-negotiable rules

### CORE-GROUND

Ground project claims in retrieved material and external claims in attributable sources.
A failed or blocked read is a retrieval gap. Report it; never infer it.

### CORE-NO-DELETE

Do not delete project files; flag obsolete material for the user to remove.

### CORE-WORKSPACE-SILO

The marker's directory is the active project and the boundary in both directions: read and write inside it. A file enters via
`1-Inputs/` or an explicit task mention, and leaves only when asked. Never reach into a sibling
folder unasked.

### CORE-COPY-ON-EDIT

Do not overwrite a source in `1-Inputs/` or an in-workspace draft — create a dated copy instead.
Update authoritative state only when the route declares it under `Updates`.

### CORE-PLAIN-NAMES

Talk to the user in plain words. Name each thing; show an ID, code or version label only beside that name.

### CORE-NO-FABRICATION

Do not invent facts, dates, amounts, decisions, citations, paths, capabilities, or completion. Say what must be confirmed.

### CORE-SCOPE

Change only what the task requires. Do not reorganize adjacent files or load unrelated history.

### CORE-INSTRUCTIONS-READONLY

Treat installed protocol and route files as read-only; change the system only through a maintenance route.

### CORE-PROGRESSIVE-DISCLOSURE

Before routing load only this bootstrap and the startup reads above. Then read one skill, its required
context, and context whose condition is present.

### CORE-HUMAN-APPROVAL

Ask before overwriting, publishing, sending, installing, changing status, or another consequential action the route does not authorize.

### CORE-STALE-WRITE

Read a living state file's revision before editing. If it changed since, stop, reread, and reconcile instead of overwriting it.

## Route selection

Read `.familiar/routes.md`, or the installed core `routes.md` when absent locally. Select one route, then read its body, required context, and any conditionally triggered context, respecting exclusions and update surfaces. If no route fits, ask rather than browse the system.

A context contract's short labels are shorthand, not literal paths — resolve each against
`state-schema.md` first. A miss on the label is a resolution error, not proof it's absent.

Before dispatching a worker, check this host's `named-subagents` state in `.familiar/installed.json`.
Unless `active`, load `.familiar/core/retrieval-fallback.md` and perform the contract inline —
never call an uninstalled worker. Before an extension route, check its manifest's capabilities
against that table, and follow `unavailable_behavior` when missing.
