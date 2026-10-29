# Changelog

All notable changes to familiar core are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org). This file covers familiar core; familiar-hub,
familiar-hooks and familiar-template keep their own. A change that would break your project's files or
an extension's contract only comes with a new major version, and
[`INSTALL.md`](INSTALL.md#updating) describes how to update.

## [Unreleased]

## [1.0.0] - 2026-10-27

First public release. A project-memory and workflow layer that makes AI agents instantly familiar with your work, progress, and decisions. It is a plain folder
you rename to your project and open your AI coding assistant inside, with project state, sources,
drafts and history kept as Markdown files beside your work.
Built and tested with Claude Code; it follows the open `AGENTS.md` and agent skills conventions and
carries the files Codex and Gemini CLI look for.

- Eight skills: `project-status`, `ingest`, `deliverable-brief`, `draft-document`, `save`,
  `handoff`, `online-research` and `system-settings` (see [the guide](docs/using-familiar.md#the-skills)
  and the [skills quick reference](QUICK-REFERENCE.md)).
- Project memory with one home per fact: configuration, status snapshot and log, tasks, timeline,
  meetings, decisions and handoffs, each with a revision check against stale writes.
- Source ingest with a locator on every claim, a knowledge index and a source register.
- Word, PowerPoint and Excel output, versioned under `2-Drafts/` and never overwritten.
- An updater, `update.py`, that brings a project up to a newer release in place, keeps your edits and
  backs up every file it replaces.
- A preflight, `doctor.py`, that checks Python and the document tools and prints the command that
  fixes each problem.
- An open extension contract for adding a specialty's own skills, agents and knowledge.

Released alongside it, each in its own repository:
[familiar-hub](https://github.com/familiar-md/familiar-hub) (one view across all your projects),
[familiar-hooks](https://github.com/familiar-md/familiar-hooks) (optional session titles and guards)
and [familiar-template](https://github.com/familiar-md/familiar-template) (a starter for writing your
own extension).
