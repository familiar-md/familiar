# Inputs

What the user supplies. **Immutable raw inputs** — familiar reads from these but never edits, rewrites,
or moves them.

- `Sources/` — source documents and new project information: scope records,
  study reports, datasets, and other inputs familiar uses to produce deliverables. Notes and
  minutes of past meetings go in `Sources/Meetings/`.
- `Admin/` — internal user material: the company Roles & Responsibilities form, governance
  and internal process notes.
- `Templates/` — project-specific blank templates for this project.
- `Examples/` — reference material showing what good output looks like; not necessarily
  project-related. The user points to a specific one when it's relevant.

Compiled understanding drawn from `Sources/` lives in `3-Knowledge/`
(built via `.familiar/core/ingest.md` at the project root), not back in here.
