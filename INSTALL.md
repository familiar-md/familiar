# familiar installation

There is no installer. The release is a folder you download, rename, and open your AI coding
assistant inside. Nothing runs on your machine to set it up.

## Prerequisites

- An AI coding assistant that reads instructions from the folder it is opened in, installed and
  signed in. familiar is built and tested with [Claude Code](https://code.claude.com/docs/en/overview)
  and follows the open `AGENTS.md` and agent skills conventions; the workspace also carries the files
  [Codex](https://developers.openai.com/codex) and [Gemini CLI](https://geminicli.com/docs/) look for.
  Each assistant needs its own account or subscription.
- Python 3.10 or newer, recommended. The assistant offers to install it, and any missing package, the
  first time a step needs one (see [Optional document toolchain](#optional-document-toolchain)).
  Without it, tracking a project, check-ins, and text ingest still work, with the assistant doing
  the bookkeeping checks by hand and saying so. Document builds and PDF extraction need it.

[`docs/using-familiar.md`](docs/using-familiar.md#your-first-session) walks through the first session and the everyday workflow.

## Getting started

1. Download `familiar-workspace-<version>.zip` from
   [github.com/familiar-md/familiar/releases](https://github.com/familiar-md/familiar/releases) and
   unzip it. It holds one folder, `familiar-workspace/`, and the licence.
2. Rename `familiar-workspace/` to whatever you want to call this project, and move it where you
   want it. That folder *is* the project — see
   [`docs/using-familiar.md`](docs/using-familiar.md#where-things-live) for its layout. familiar reads and writes only
   inside it (`CORE-WORKSPACE-SILO`); nothing outside the folder is in scope.
3. If you already have source material to start from, put it under `1-Inputs/Sources/`, `1-Inputs/Admin/`,
   or `1-Inputs/Templates/` before your first session.
4. Open your assistant with that folder as the working directory. Its entry file (`CLAUDE.md`,
   `AGENTS.md`, or `GEMINI.md`) is already present and self-contained — there is nothing else to point
   it at.

> **Already have a project folder?** The workspace can sit inside it, one level down, beside your
> other files. Open the agent in the workspace folder, not the outer one. familiar works only inside
> the workspace; you move files across by hand: sources in, finished drafts out.
> [Where things live](docs/using-familiar.md#where-things-live) shows both layouts.

## First run

There is no setup step to invoke. The project marker (`.familiar-project`) ships already in place,
so familiar binds and loads project state from the first message in the folder.

The first time you run `/project-status` → Check-in, it establishes the project: it asks for and confirms a Project
Name, stamps `.familiar-project`'s `created` date, and asks for the project's signature, written to
its `5-System/user-preferences.md`. Skip that question and `/system-settings` → Preferences sets it
later; Preferences also sets a default signature and standing preferences for every project. Every
later check-in just reconciles state as usual.

## Host support

Every host reads the same content, from different native locations:

| Host | Skills | Subagents | Notes |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/agents/*.md` | |
| Codex | `.agents/skills/` | `.codex/agents/*.toml` | Start a skill with `$skill-name` or the `/skills` picker. `agents/openai.yaml` per skill sets `interface.display_name` and whether Codex may pick the skill from your request: it may not, for any of the eight. |
| Gemini CLI | `.agents/skills/` | `.gemini/agents/*.md` | No per-skill command: ask for a skill by name ("run the project-status skill") and confirm when asked. Skill names show with no namespace prefix — a spec limit, not a bug. |

**Other assistants.** An assistant that reads `AGENTS.md` and the skill folders (Cursor, GitHub
Copilot in VS Code and OpenCode among them) should load familiar's bootstrap. Skills may appear twice
because both folders are read. Such an assistant has no row in `.familiar/installed.json`, so familiar
treats every capability as `unknown`, performs worker steps inline, and asks before running an
extension route.

`python` below means Python 3.10 or newer under whichever command this machine has: `python3`,
`python`, or `py`. The assistant picks it the same way (`routes.md` → Running familiar's scripts).
On macOS the built-in `/usr/bin/python3` is Apple's own older copy; install current Python from
python.org.

`.claude/skills/` and `.agents/skills/` hold byte-identical copies of every shared skill file (a
quality gate enforces this): host skill-discovery paths differ, and Windows symlinks aren't reliable
enough to point one at the other. The one deliberate difference is the `agents/openai.yaml` inside
each skill under `.agents/skills/`, which carries the Codex invocation policy that Claude Code
expresses through `SKILL.md` frontmatter instead — so the two trees are not identical file-for-file.

A capability is `active` only once its released implementation and a live health check both pass;
otherwise it is reported `available`, `unsupported`, `unavailable`, or `unknown` — never a claimed
fallback. Current state per host is recorded in `.familiar/installed.json`.

## Synced folders and concurrent use

familiar supports **one writer at a time**. Keeping a project in OneDrive, SharePoint, Dropbox, iCloud Drive, or a
similar synced folder is fine, and so is one person moving between machines — what is not supported
is two sessions writing the same project at once, on synced storage or off it.

The rule that normally prevents a session overwriting newer work is `CORE-STALE-WRITE`: reread a
living state file's revision before replacing it, and stop if it moved. That check reads local disk.
A sync client reconciles *after* a write has already landed, so two machines can both read revision
3, both write revision 4, and neither check fires. The sync client then either picks a winner or
writes a conflict copy beside the original. familiar cannot see that collision happen, and a prose
rule is not a lock — treat this as a real constraint on how you work, not a warning it can enforce.

What it does do is refuse to write past the evidence. Before updating a living state file it looks
for a conflict copy alongside it (`tasks-DESKTOP-A1B2.md`, `timeline (conflicted copy
2026-09-11).md`, or iCloud Drive's `tasks 2.md`) and stops and reports rather than writing. Clearing one is yours to do —
`CORE-NO-DELETE` means familiar will not remove it for you, and it must never merge one silently or
read one as real state.

Two smaller effects of the same setup are worth knowing. A file left as an online-only placeholder
(OneDrive Files On-Demand) reads as an error rather than an absence, so a report may say
"unreadable" where "not downloaded" is the truth. And a synced SharePoint root adds a long prefix to
every path beneath it, which on Windows can push a deep project against the `MAX_PATH` limit.

## Optional document toolchain

`document-tools` (used by the `draft-document` skill for `.pptx`/`.docx` output) is recorded
`available`, not `active` — there is no install-time verification. Each build runs its own script's
`--health-check` first and reports honestly from that:

- Python 3.10 or newer (`python3` on macOS), plus `python-pptx` (deck) or `python-docx >= 1.2.0` (document) — without these the health
  check reports `"build": false` and the skill degrades (plain text/Markdown for `document`; explicit
  `unavailable` for `deck`, which has no plain-text fallback).
- LibreOffice, optionally, for visual rendering. The build scripts look for `soffice` on `PATH` and in
  its default install folder (macOS app bundle, Windows Program Files, common Linux locations). Without it, the build still succeeds and validates
  structurally, but reports `"visual_validation": false`.

The project ships a cross-platform preflight that checks all of this at once and explains what
breaks without each piece. Run it from the project folder:

```text
python .familiar/scripts/doctor.py
```

(`python3` on macOS and most Linux.) It uses only the standard library, runs even on a Python too old
for familiar so it can say so, checks the Windows-only items only on Windows, and exits `0` when every
required check passes. Each FAIL line ends with the command that fixes it on that machine. Where the
system Python refuses `pip` installs (Debian, Ubuntu, Homebrew; PEP 668), it puts the packages in a
familiar-only virtual environment at `~/.familiar/venv`, which the assistant then uses for every
script. It reports your machine, not
familiar — a failure there never means the installation is broken, only that a document or deck
build would be. On Windows, run it the same way (`py -3` if `python` is not found).

Document builds need Python on the machine: an assistant that cannot run it cannot build a deck.

## Updating

Updating brings a project you already have up to a newer release. Core, extensions and the hooks
package update together.

1. Download the new `familiar-workspace-<version>.zip` from the
   [Releases page](https://github.com/familiar-md/familiar/releases), plus the newer zip of any
   extension or of the hooks package you use.
2. Put the zips in your project's `_update/` folder. There is no need to unzip them.
3. Open your agent in the project and run `/ili-system-settings update` (`$system-settings` on
   Codex).
   → verify: it lists what would change for each package, and anything it will leave alone.
4. Answer yes to apply it.
   → verify: it reports `applied` and a backup folder under `5-System/_update-backups/`.
5. Start a new session; nothing from the new release is live until then. Delete the zips from
   `_update/` when you like.

**What it keeps.** Your content folders, your own notes below the `<!-- familiar:end -->` marker in
`CLAUDE.md`, `AGENTS.md` and `GEMINI.md`, and any familiar file you edited (reported as
`diverged`). Files a release no longer ships move into the backup, so nothing is deleted. To roll
back, copy the backup folder's contents over the project.

**Extensions.** Each extension with a zip in `_update/` updates in the same run. One without is
left as it is, and the report warns if the new core version is outside the range it declares. An
extension built from [familiar-template](https://github.com/familiar-md/familiar-template) carries a
release manifest once its author runs `check_extension.py --release`; one without a manifest is
updated by copying its folders onto the project again.

**If the report starts with `STOP`,** nothing was written. A different `state-schema` is a
migration: read the release notes in [`CHANGELOG.md`](CHANGELOG.md) first. A missing manifest means
[updating by hand](#updating-by-hand).

### From a terminal

```text
python .familiar/scripts/update.py --project . --from _update            # report only
python .familiar/scripts/update.py --project . --from _update --apply    # back up, then write
```

A project set up from `1.0.0` has an updater without `--from`. For that one update, unzip the new
release outside the project and run its copy instead:
`python "<new familiar-workspace folder>/.familiar/scripts/update.py" --project "<your project>"`,
adding `--extension "<folder>"` per extension and `--apply` to write.

### Format notes in tracker files

The format notes at the top of `tasks.md`, `timeline.md`, `_knowledge-index.md`, `_abbreviations.md`
and `2-Drafts/_draft-index.md` sit beside your data, so no update replaces them. The rules
themselves live in `.familiar/core/state-schema.md`, which every update brings. If a release's notes
say a table's columns changed, compare by hand.

### Updating by hand

This path starts a new folder from the release and moves your own content across, instead of
replacing files inside the project you already have. Because nothing is deleted until you choose to,
it cannot half-succeed: stop at any point and the old folder is exactly as it was.

1. Download the new release and unpack it as its own new folder, same as [Getting
   started](#getting-started) — do not unpack it into, or over, your existing project folder.
2. Open both `.familiar-project` files (old project, new folder) and compare their `state-schema:`
   lines. **If they differ, stop here** — that is a schema migration, not a routine update, and this
   procedure does not perform one. Check [`CHANGELOG.md`](CHANGELOG.md) and the release notes on the
   GitHub Releases page, or ask for help before going further.
3. If your project has any installed extensions, re-drop each one from its own download onto the new folder, the
   same way you dropped it on originally.
4. **Copy** these five folders from your old project folder into the new one, overwriting the fresh
   copies the release shipped: **`1-Inputs/`, `3-Knowledge/`, `2-Drafts/`, `4-Trackers/`, `5-System/`.** Do not
   move them yet: the old folder remains your rollback until you have tested the new one. These are
   the standard data folders; separately carry forward any user-created host settings, custom skills,
   or optional guard configuration you deliberately want to keep.
   **Then restore the new release's own copy of every `_about.md`** (one per folder, including the
   root one) **and `3-Knowledge/_page-template.md`** over whatever step 4 just brought in from the old
   folder. Both carry zero per-project data — nothing you write ever lands in them — so there is
   nothing to lose by taking the release's fresh copy, and doing so is how their wording keeps up with
   the product instead of freezing at whatever release the project started on.
   If you added your own instructions to `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`, they sit below
   that file's `<!-- familiar:end -->` marker: copy those lines to the same place in the new
   folder's file. Everything above the marker is the release's and comes fresh with it.
5. In the new folder's `.familiar-project`, replace only the `created:` line with the value from
   your old project's `.familiar-project`. Leave its `familiar-version:` and `state-schema:` lines
   exactly as the new release set them.
6. Open your coding host in the new folder and start a new session — skills, agents, and entry files
   are read at session start, so nothing from the new release is live until then.

Keep the old folder unchanged until you've confirmed the new one works; it's your entire rollback.
Once you're satisfied, archive or delete it yourself — familiar does not do this step for you and
does not need to.

## The fleet hub

The fleet hub is a separate folder that answers questions across all your registered projects. It
is not part of this download: get it from
[familiar-hub](https://github.com/familiar-md/familiar-hub), whose `INSTALL-HUB.md` covers setup and what the
hub reads. Setting up the hub creates `~/.familiar/fleet.md`, the list of your projects, and the hub keeps it:
ask `/fleet` to add, exclude or recategorise a project. Nothing inside a project writes the list.
Whether a project is active, paused or closed is recorded in the hub, not in the project.

## Extensions

An extension adds skills, agents and knowledge for a specialty. Like the workspace, it has no
installer. To add one, copy its top-level folders (`.claude/`, `.agents/`, `.codex/`, `.gemini/`,
`.familiar/`) into the project root, merging with what is already there. Nothing in an extension
overwrites core files. Start a new session and its skills appear. No extension is part of this
release; to write your own, start from
[familiar-template](https://github.com/familiar-md/familiar-template) ("Use this template"), which
follows `.familiar/core/extension-contract.md`. Each extension's own `_about.md` says what it adds.

### Adding several at once

Say you want the fleet hub, the hooks package and two extensions of your own:

1. **The hub** is not added to a project. Unzip it as its own folder beside your projects; its
   `INSTALL-HUB.md` covers the rest.
2. **The hooks:** copy the `.familiar/` folder from the hooks zip onto the project, then run
   `/ili-system-settings hooks` to switch on the ones you want. Copying alone turns nothing on.
3. **Each extension:** copy its top-level folders onto the project root, one after the other. Order
   does not matter.
4. Start a new session.
   → verify: typing `/ili` lists each extension's skills, and `/ili-system-settings hooks` lists the
   hooks as installed.
