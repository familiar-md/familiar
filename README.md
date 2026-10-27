# familiar

![familiar: bound to your work](docs/assets/familiar-hearth-banner.jpg)

**familiar is a project-memory and workflow layer for LLM agents, where nothing has to be explained
twice.**

familiar is a folder. Download the release, rename its `familiar-workspace` folder to your project's
name, and open Claude Code, Codex, or Gemini CLI inside it. There is nothing to set up and nothing
running in the background. The folder holds what the project is, what has been decided, what is
open, and where the source for each claim lives, so every session starts from that record instead
of from nothing, and answers trace back to your own sources rather than the model's memory. On top
of it sit the everyday workflows: check-ins, ingesting documents, drafting decks and documents,
research, and tracking. The record starts thin and grows as you work, the way a colleague learns a
project by being there for it.

## Yours, on your disk

familiar core is free and open source: plain markdown and a few small scripts that you own, with no
account, no server, and nothing to sign up for. Every rule, skill, and template is a file you can
read and change. familiar stores nothing outside the folder; the AI assistant you open in it sends
what it reads to its own provider, under that provider's terms.

## One folder per project

familiar works best one project to a folder. Open your assistant in the project you want to work on
and it becomes familiar with that project, its details, decisions, and history, and with nothing
else. Keeping projects apart keeps each one's memory and tasks its own, stops one project's facts
turning up in another, and keeps confidential material inside the project it belongs to.

That boundary is a rule the agent follows, not a lock: the assistant can still reach any file your
account can. For stricter setups, use your assistant's own permission and sandbox settings, or add
the guards from [familiar-hooks](https://github.com/familiar-md/familiar-hooks), optional hooks that
block reads and writes outside the project before they run (a deterrent, not a security boundary). To keep
track of all your projects at once, add [familiar-hub](https://github.com/familiar-md/familiar-hub),
a separate folder kept next to your projects that gives you one view and a daily brief across them.

## Built for Claude, open to others

familiar is built and used daily on Claude Code, and maintained to work on Codex and Gemini CLI too.
The first reply in a session is meant to open with a short "familiar bound" line naming the project
and its signature, so on any assistant you can see at a glance whether it loaded the project; if the
line is missing, it probably did not. In Claude
Code, type `/ili` to list every familiar skill.

## Start here

- [`GUIDE.md`](GUIDE.md) — the user guide: prerequisites, your first session, the everyday loop, and
  what each of the ten skills does.
- [`INSTALL.md`](INSTALL.md) — download, host support, the document toolchain, synced folders,
  updating.
- [`CHEATSHEET.md`](CHEATSHEET.md) — every command on one page: core skills, the fleet hub, the hooks.
- [`MANUAL.md`](MANUAL.md) — the technical reference for how the core mechanism works.
- [`CHANGELOG.md`](CHANGELOG.md) — what changed in each release.

## Why

Agent sessions are stateless by default. Without a place for project memory to live, every new
session either re-reads everything (expensive, and still misses what didn't make it into a file) or
trusts the model's running context (which resets, gets summarized, or is simply wrong). familiar
gives a project one authoritative home per fact — configuration, current status, tasks, decisions,
history — so a session picks up where the last one left off, on any supported host, without a
person manually re-briefing it every time.

## Runtime model

```text
host entry file
→ small neutral bootstrap
→ project-local route registry
→ one selected skill
→ that skill's required project context
→ conditionally triggered context
```

A session reads the bootstrap once, picks exactly one route for the request, then loads only that
route's declared context — not the whole project, not every skill, not other projects. Core owns
the bootstrap, the project boundary, the state schema, routing, deterministic adapters, and a fixed
set of safety rules (no silent deletion, no writes outside the project, no invented facts, ask
before anything consequential).

The core is intentionally neutral: it ships nothing domain-specific. It defines an open contract for
optional add-ons to contribute their own routes, skills, and knowledge — without core ever
hard-coding what those add-ons are.

## Install

There is no installer. Download the `familiar-workspace/` release from
[github.com/familiar-md/familiar/releases](https://github.com/familiar-md/familiar/releases), rename
it to your project's name, and open Claude Code, Codex, or Gemini CLI with that folder as the working
directory — its entry file
(`CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`) is already there. The project is usable immediately; the
first real `checkin` establishes the project name, and `/system-settings` → Preferences sets your
signature. Other hosts that read `AGENTS.md` (Cursor, GitHub Copilot, OpenCode) are untested.

Core routing and memory have no always-on Python dependency; only the optional document/PDF tools do.
See [`INSTALL.md`](INSTALL.md) for host support, the document toolchain, the one-writer-at-a-time model on synced
folders, and current update/extension limits.

The pieces that define the system are readable in place, inside the release: the authority model and
safety rules in `.familiar/core/bootstrap.md`, routing in `.familiar/routes.md`, memory layout in
`.familiar/state-schema.md`, and the add-on contract in `.familiar/extension-contract.md`. Host
differences, the document toolchain, and the current update and extension limits are in `INSTALL.md`.

## What a project looks like

```text
<project>/            (this is a renamed familiar-workspace/ release)
├── .familiar-project           marks the project boundary
├── .familiar/                   routing, state schema, capability records
├── CLAUDE.md  AGENTS.md  GEMINI.md
├── .claude/  .agents/  .codex/  .gemini/    per-host skills and subagents
├── 1-Inputs/                   source documents, templates, admin
├── 2-Drafts/                   generated outputs pending approval
├── 3-Knowledge/                digested source material
├── 4-Trackers/                 tasks, timeline
└── 5-System/                   config, context, status, decisions, handoffs
```

Every fact has one authoritative home. Living state files carry revision markers so a later session
can detect a stale write before overwriting newer work.

## Capability truthfulness

The machine-readable table is `.familiar/installed.json`. `active` means the released fixture passed;
`available` means separate setup is still required; `unsupported`, `unavailable`, and `unknown` are
reported without fallback claims. Mechanical enforcement is optional and never implied by the core
bootstrap.

## Extending it

Core defines an open manifest contract (`familiar-extension.json`) that lets an add-on contribute
namespaced routes, skills, background workers, or knowledge sources without core knowing its name in
advance. None are included in the public core release.

To build your own specialty (marketing, consulting, proposal writing, and more), start from
[familiar-template](https://github.com/familiar-md/familiar-template): click "Use this template",
open an AI coding assistant in your copy, and build your skills with it. The template carries the
contract checklist and `check_extension.py`, a standard-library validator that checks a package
against the manifest schema, namespace rules, and file parity. It does not contain a copy of core;
you merge your extension onto a project made from this release. The contract itself is
`.familiar/core/extension-contract.md`.

**Find or share extensions:** tag your extension's repo with the
[`familiar-extension`](https://github.com/topics/familiar-extension) topic, and browse that topic to
see what others have built.

## Quality gates

The source repository carries an executable gate suite (`tests/quality_gates.py`). It is
maintainer-only: it is not included in the downloadable release, and you do not need it to use
familiar. It validates bootstrap size and neutrality, stable rule
IDs, skill context contracts, extension manifests and collisions, markdown link resolution, canonical
capability vocabulary, relevant write rules being wired to every file-writing skill, the router audit,
version parity across active packages, and that every shared skill file under `.claude/skills/` and
`.agents/skills/` stays byte-identical apart from the Claude copy's `ili-` command name.

## Versioning

familiar core, [familiar-hub](https://github.com/familiar-md/familiar-hub),
[familiar-hooks](https://github.com/familiar-md/familiar-hooks) and
[familiar-template](https://github.com/familiar-md/familiar-template) were first released together at
`1.0.0`; from there each has its own version. Versions follow [Semantic Versioning](https://semver.org): a
release that would break your project's files or an extension written against the contract bumps the
first number; new features bump the second; fixes bump the third.

## License

Apache License 2.0. See `LICENSE`.
