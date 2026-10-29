# familiar installation

There is no installer. The release is a folder that you download, rename, and open your AI coding
agent inside. Nothing runs on your computer to set it up.

## Prerequisites

- **An AI coding agent** that reads instructions from the folder it opens in, installed and signed
  in. familiar is built and tested with [Claude Code](https://code.claude.com/docs/en/overview). It
  follows the open `AGENTS.md` and agent skills conventions. The workspace also has the files that
  [Codex](https://developers.openai.com/codex) and [Gemini CLI](https://geminicli.com/docs/) look
  for. Each agent needs its own account or subscription.
- **Python 3.10 or newer** (recommended). The first time a step needs Python or a missing package,
  the agent offers to install it. See [Optional document toolchain](#optional-document-toolchain).
  Without Python, project tracking, check-ins and text ingest still work. The agent then does the
  bookkeeping checks itself and tells you so. Document builds and PDF extraction need Python.

[`docs/using-familiar.md`](docs/using-familiar.md#your-first-session) walks through the first session
and everyday work.

## Getting started

1. Download `familiar-workspace-<version>.zip` from
   [github.com/familiar-md/familiar/releases](https://github.com/familiar-md/familiar/releases) and
   unzip it. It holds one folder, `familiar-workspace/`, and the license.
2. Rename `familiar-workspace/` to your project's name, and move it where you want it. That folder
   *is* the project. [`docs/using-familiar.md`](docs/using-familiar.md#where-things-live) shows its
   layout. familiar reads and writes only inside this folder.
3. If you already have source material, put it in `1-Inputs/Sources/`, `1-Inputs/Admin/` or
   `1-Inputs/Templates/` before your first session.
4. Open your agent with that folder as the working folder. Its entry file (`CLAUDE.md`, `AGENTS.md`
   or `GEMINI.md`) is already in the folder. You do not need to point the agent at anything else.

> **Already have a project folder?** Put the workspace inside it, one level down, beside your other
> files. Open the agent in the workspace folder, not the outer one. familiar works only inside the
> workspace. You move files across yourself: sources in, finished drafts out.
> [Where things live](docs/using-familiar.md#where-things-live) shows both layouts.

## First run

There is no setup step. The project marker (`.familiar-project`) is already in place, so familiar
loads the project from the first message in the folder.

The first `/ili-project-status check-in` sets up the project:

- It asks for the project name and confirms it.
- It writes the `created` date into `.familiar-project`.
- It asks for the project's signature and saves it in `5-System/user-preferences.md`.

If you skip the signature, set it later with `/ili-system-settings preferences`. Preferences also
sets a default signature and standing preferences for every project. Later check-ins only bring the
project state up to date.

## Host support

Every agent reads the same content, from the folders that agent looks in:

| Agent | Skills | Subagents | Notes |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/agents/*.md` | |
| Codex | `.agents/skills/` | `.codex/agents/*.toml` | Start a skill with `$skill-name` or the `/skills` picker. Codex never starts a familiar skill on its own. Each skill's `agents/openai.yaml` sets this. |
| Gemini CLI | `.agents/skills/` | `.gemini/agents/*.md` | No command per skill. Ask for a skill by name ("run the project-status skill") and confirm when asked. Skill names show without a prefix. This is a limit of the skills format, not a bug. |

**Other agents.** An agent that reads `AGENTS.md` and the skill folders is expected to load familiar.
Cursor, GitHub Copilot in VS Code and OpenCode are examples. Skills can appear twice, because the
agent reads both skill folders. familiar has no record of what such an agent supports. It treats
every capability as `unknown`, does subagent steps itself, and asks before it starts an extension
skill.

In this guide, `python` means Python 3.10 or newer under the command your computer uses: `python3`,
`python` or `py`. The agent picks the command the same way. On macOS, the built-in
`/usr/bin/python3` is an older copy from Apple. Install a current Python from python.org.

`.claude/skills/` and `.agents/skills/` hold the same skill files, because agents look in different
folders. The one difference is `agents/openai.yaml` in each skill under `.agents/skills/`. It holds
the Codex settings that Claude Code reads from `SKILL.md` instead. If you edit a skill, edit both
copies.

A capability is `active` only after its released version and a live health check both pass.
Otherwise familiar reports it as `available`, `unsupported`, `unavailable` or `unknown`. It never
claims a fallback. `.familiar/installed.json` records the current state for each agent.

## Synced folders and concurrent use

familiar supports **one writer at a time**. You can keep a project in OneDrive, SharePoint, Dropbox,
iCloud Drive or a similar synced folder. You can move between computers. Do not let two sessions
write the same project at the same time, on synced storage or off it.

Before familiar replaces a state file, it reads the file's revision again. If the revision changed,
it stops. That check reads the local disk. A sync app copies changes *after* the write. Two computers
can both read revision 3 and both write revision 4, and neither check stops them. The sync app then
keeps one version or writes a conflict copy beside the original. familiar cannot see this happen.
The rule is an instruction, not a lock, so the limit is real.

familiar does stop when it sees a conflict copy. Before it updates a state file, it looks for a
conflict copy beside it, such as `tasks-DESKTOP-A1B2.md`, `timeline (conflicted copy 2026-09-11).md`
or iCloud Drive's `tasks 2.md`. If it finds one, it stops and reports it. You remove the copy
yourself. familiar never deletes it, never merges it without telling you, and never reads it as the
real state.

Two smaller effects:

- **Online-only files.** A file that is only a placeholder (OneDrive Files On-Demand) reads as an
  error, not as missing. A report can say "unreadable" when the file is only "not downloaded".
- **Long paths.** A synced SharePoint folder adds a long prefix to every path. On Windows, a deep
  project can then reach the `MAX_PATH` limit.

## Optional document toolchain

The `draft-document` skill builds `.pptx` and `.docx` files with `document-tools`. This capability
is `available`, not `active`, because nothing checks it at install time. Each build runs its
script's `--health-check` first and reports the result:

- **Python 3.10 or newer** (`python3` on macOS), plus `python-pptx` for decks or
  `python-docx >= 1.2.0` for documents. Without these, the health check reports `"build": false`.
  A document then comes out as plain text or Markdown. A deck has no plain-text fallback, so it
  reports `unavailable`.
- **LibreOffice** (optional), for a visual check. The build scripts look for `soffice` on `PATH` and
  in its default install folder on macOS, Windows and Linux. Without LibreOffice, the build still
  succeeds and checks the file structure, but reports `"visual_validation": false`.

The project includes a preflight that checks all of this at once. It tells you what breaks without
each piece. Run it from the project folder:

```text
python .familiar/scripts/doctor.py
```

Use `python3` on macOS and most Linux. On Windows, use `py -3` if `python` is not found.

- It uses only the standard library. It runs on a Python that is too old for familiar, so that it
  can tell you so.
- It checks Windows-only items only on Windows.
- It exits `0` when every required check passes. Each FAIL line ends with the command that fixes it
  on that computer.
- Some systems block `pip` installs into the system Python (Debian, Ubuntu, Homebrew, PEP 668). On
  those, it puts the packages in a virtual environment for familiar at `~/.familiar/venv`. The agent
  then uses it for every script.

The preflight checks your computer, not familiar. A failure does not mean that the installation is
broken. It means that a document or deck build would fail. An agent that cannot run Python cannot
build a deck.

## Updating

An update brings an existing project up to a newer release. Core, extensions and the hooks package
update together.

1. Download the new `familiar-workspace-<version>.zip` from the
   [Releases page](https://github.com/familiar-md/familiar/releases). Also download the newer zip of
   each extension and of the hooks package, if you use them.
2. Put the zips in your project's `_update/` folder. Do not unzip them.
3. Open your agent in the project and run `/ili-system-settings update` (`$system-settings` on
   Codex).

   → verify: it lists what will change for each package, and what it will leave alone.
4. Answer yes to apply the update.

   → verify: it reports `applied` and a backup folder under `5-System/_update-backups/`.
5. Start a new session. Nothing from the new release is live until then. You can then delete the
   zips from `_update/`.

**What it keeps.** The updater keeps:

- your content folders
- your own notes below the `<!-- familiar:end -->` marker in `CLAUDE.md`, `AGENTS.md` and
  `GEMINI.md`
- every familiar file you edited (reported as `diverged`)

Files that a release no longer includes move into the backup, so nothing is deleted. To roll back,
copy the contents of the backup folder over the project.

**Extensions.** Each extension with a zip in `_update/` updates in the same run. An extension without
a zip stays as it is. If the new core version is outside the range that extension declares, the
report warns you. An extension built from
[familiar-template](https://github.com/familiar-md/familiar-template) has a release manifest after its
author runs `check_extension.py --release`. To update an extension without a manifest, copy its
folders onto the project again.

**If the report starts with `STOP`,** nothing was written. A different `state-schema` means a
migration. Read the release notes in [`CHANGELOG.md`](CHANGELOG.md) first. A missing manifest means
that you update [by hand](#updating-by-hand).

### From a terminal

```text
python .familiar/scripts/update.py --project . --from _update            # report only
python .familiar/scripts/update.py --project . --from _update --apply    # back up, then write
```

The updater in a `1.0.0` project has no `--from` option. For that one update, unzip the new release
outside the project and run its copy of the updater:

```text
python "<new familiar-workspace folder>/.familiar/scripts/update.py" --project "<your project>"
```

Add `--extension "<folder>"` for each extension, and `--apply` to write.

### Format notes in tracker files

`tasks.md`, `timeline.md`, `_knowledge-index.md`, `_abbreviations.md` and
`2-Drafts/_draft-index.md` start with format notes. These notes sit beside your data, so no update
replaces them. The rules live in `.familiar/core/state-schema.md`, which every update brings. If a
release's notes say that a table's columns changed, compare the notes by hand.

### Updating by hand

This method starts a new folder from the release and moves your content into it. It does not
replace files inside your existing project. Nothing is deleted until you choose, so it cannot fail
halfway. If you stop at any step, the old folder stays exactly as it was.

1. Download the new release and unzip it as a new folder, as in [Getting started](#getting-started).
   Do not unzip it into or over your existing project folder.
2. Open both `.familiar-project` files (old project and new folder) and compare their
   `state-schema:` lines. **If they differ, stop here.** That is a schema migration, not a routine
   update, and this method does not do one. Read [`CHANGELOG.md`](CHANGELOG.md) and the release
   notes on the GitHub Releases page, or ask for help.
3. If your project has extensions, copy each one from its own download onto the new folder, the same
   way you added it the first time.
4. **Copy** these five folders from the old project into the new one, and replace the new copies:
   **`1-Inputs/`, `2-Drafts/`, `3-Knowledge/`, `4-Trackers/`, `5-System/`.** Copy them, do not move
   them. The old folder is your rollback until you have tested the new one. Also copy any of your
   own agent settings, custom skills or hook settings that you want to keep.
5. Put back the new release's copy of every `_about.md` (one per folder, including the root one) and
   of `3-Knowledge/_page-template.md`. Step 4 replaced them with the old copies. These files hold no
   project data, so you lose nothing, and their wording stays current.
6. If you added your own instructions to `CLAUDE.md`, `AGENTS.md` or `GEMINI.md`, they are below the
   `<!-- familiar:end -->` marker. Copy those lines to the same place in the new folder's file.
   Everything above the marker belongs to the release and comes with it.
7. In the new folder's `.familiar-project`, replace only the `created:` line with the line from your
   old `.familiar-project`. Do not change its `familiar-version:` and `state-schema:` lines.
8. Open your agent in the new folder and start a new session. The agent reads skills, subagents and
   entry files when a session starts, so nothing from the new release is live until then.

Keep the old folder unchanged until you know that the new one works. It is your only rollback. When
you are sure, archive or delete it yourself. familiar does not do this step.

## The fleet hub

The fleet hub is a separate folder that answers questions across all your registered projects. It is
not part of this download. Get it from [familiar-hub](https://github.com/familiar-md/familiar-hub).
Its `INSTALL-HUB.md` covers setup and what the hub reads. Hub setup creates `~/.familiar/fleet.md`,
the list of your projects, and the hub keeps that list. To add, exclude or recategorize a project,
ask `/ili-fleet`. Nothing inside a project writes to the list. The hub, not the project, records
whether a project is active, paused or closed.

## Extensions

An extension adds skills, subagents and knowledge for a specialty. Like the workspace, it has no
installer. To add one, copy its top-level folders (`.claude/`, `.agents/`, `.codex/`, `.gemini/`,
`.familiar/`) into the project root, and merge them with the folders that are already there. An
extension never overwrites core files. Start a new session, and its skills appear.

This release includes no extensions. To write your own, start from
[familiar-template](https://github.com/familiar-md/familiar-template) ("Use this template"). It
follows `.familiar/core/extension-contract.md`. Each extension's own `_about.md` says what it adds.

### Adding several at once

For example, you want the fleet hub, the hooks package and two extensions of your own:

1. **The hub** does not go into a project. Unzip it as its own folder beside your projects. Its
   `INSTALL-HUB.md` covers the rest.
2. **The hooks:** copy the `.familiar/` folder from the hooks zip onto the project. Then run
   `/ili-system-settings hooks` and turn on the hooks you want. Copying alone turns nothing on.
3. **Each extension:** copy its top-level folders onto the project root, one after the other. The
   order does not matter.
4. Start a new session.

   → verify: `/ili` lists each extension's skills, and `/ili-system-settings hooks` shows the hooks
   as installed.
