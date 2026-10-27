# System

familiar-managed system files for this project. The user rarely needs to touch these.

- `project-config.md` — how familiar runs this project: installed extensions,
  and language overrides. Run-settings only — facts about the project live
  in `project-context.md`.
- `project-context.md` — stable facts captured at check-in: background, objective, scope,
  constraints, stakeholders, and timeline.
- `Memory/` — `status-snapshot.md` (current state) and `status-log.md` (append-only history).
- `Decisions/` — the reasoning behind gated decisions; the log says *that*, these say *why*.
- `Handoffs/` — in-flight work carried across a session break. Never read automatically; written
  and read via `/handoff` (user-invoked only).
- `user-preferences.md` — behavioural preferences/feedback for this project (created when the user
  gives feedback).
- `notes.md` — loose notes that fit nowhere else (created if needed).

familiar creates/updates these during kickoff and ongoing work, per `status-format.md`.
