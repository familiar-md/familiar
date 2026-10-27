# familiar installation

There is no installer. `familiar-workspace/` is the release — a folder you download, rename, and
open your coding assistant inside. Nothing runs on your machine to set it up.

## Prerequisites

- One of Claude Code, Codex, or Gemini CLI, installed and signed in. Install each from its vendor's
  own page: [Claude Code](https://code.claude.com/docs/en/overview),
  [Codex](https://developers.openai.com/codex), [Gemini CLI](https://geminicli.com/docs/). Codex and
  Gemini CLI are installed through Node.js tooling, and each needs its own account or subscription.
- Python 3.10 or newer, recommended. The assistant offers to install it, and any missing package, the
  first time a step needs one (see [Optional document toolchain](#optional-document-toolchain)).
  Without it, tracking a project, check-ins, and text ingest still work, with the assistant doing
  the bookkeeping checks by hand and saying so. Document builds and PDF extraction need it.

[`GUIDE.md`](GUIDE.md) walks through the first session and the everyday workflow.

## Getting started

1. Download the latest release from
   [github.com/familiar-md/familiar/releases](https://github.com/familiar-md/familiar/releases) and
   unpack it. It contains a `familiar-workspace/` folder plus this
   file, `README.md`, `GUIDE.md`, `MANUAL.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
   `LICENSE`, `VERSION`, and an `examples/` folder. **`familiar-workspace/` is the
   product**; the rest is documentation you can keep wherever you like.
2. Rename `familiar-workspace/` to whatever you want to call this project, and move it where you
   want it. That folder *is* the project — see
   [`README.md`](README.md#what-a-project-looks-like) for its layout. familiar reads and writes only
   inside it (`CORE-WORKSPACE-SILO`); nothing outside the folder is in scope.
3. If you already have source material to start from, put it under `1-Inputs/Sources/`, `1-Inputs/Admin/`,
   or `1-Inputs/Templates/` before your first session.
4. Open Claude Code, Codex, or Gemini CLI with that folder as the working directory. Each host's entry
   file (`CLAUDE.md`, `AGENTS.md`, or `GEMINI.md`) is already present and self-contained — there is
   nothing else to point the host at.

The renamed folder does not have to be the top level of what you'd otherwise call "the project." It's
equally supported to paste it as a subfolder one level inside an existing project directory that
already holds other, non-familiar material — the coding host's working directory is that subfolder
either way, `CORE-WORKSPACE-SILO` still bounds familiar to it, and you move files across that boundary
by hand (source material in, finished drafts out to the surrounding project folder) whenever you
choose.

## First run

There is no setup step to invoke. The project marker (`.familiar-project`) ships already in place,
so familiar binds and loads project state from the first message in the folder.

The first time you run `checkin`, it establishes the project: it asks for and confirms a Project
Name and stamps `.familiar-project`'s `created` date. If this project has no familiar signature of
its own yet, it says so once and points you to `/system-settings` → Preferences, which writes the
project's signature to its `5-System/user-preferences.md`, and a default signature and any standing
preferences to the global file for every project. Every later `checkin` just reconciles state as usual.

## Host support

Every host reads the same content, from different native locations:

| Host | Skills | Subagents | Notes |
|---|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/agents/*.md` | |
| Codex | `.agents/skills/` | `.codex/agents/*.toml` | Start a skill with `$skill-name` or the `/skills` picker. `agents/openai.yaml` per skill sets `interface.display_name` and whether Codex may pick the skill from your request: it may for `ingest` and `ongoing-work`, and may not for the other seven. |
| Gemini CLI | `.agents/skills/` | `.gemini/agents/*.md` | No per-skill command: ask for a skill by name ("run the triage skill") and confirm when asked. Skill names show with no namespace prefix — a spec limit, not a bug. |

**Other hosts.** Cursor, GitHub Copilot (VS Code), and OpenCode read `AGENTS.md` and both skill
folders, so familiar's bootstrap should load, but none has been tested with familiar. Skills may
appear twice because both folders are read. These hosts have no row in `.familiar/installed.json`,
so familiar treats every capability as `unknown`, performs worker steps inline, and reports an
extension route as unverified and asks before running it.

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
  its default install folder (macOS app bundle, Windows Program Files, common Linux locations); only
  the Windows location has been tested. Without it, the build still succeeds and validates
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

This is a genuine gap on a host with no Python, or a non-Claude model with no equivalent
document-authoring skill loaded — do not assume it works everywhere because it works on one machine.

## Updating

Updating means bringing a project you already have up to a newer release. Use the updater script
when your project has a release manifest — the file `.familiar/release-manifests/familiar.json`,
which every project started from release `0.6.4` or later carries. Use the [manual
procedure](#updating-by-hand) below when it does not, or when you would rather move your content by hand.

### With the updater

The updater, `update.py`, ships in every release. You run the **new** release's copy, from a
terminal, against your existing project. It replaces only the release's own files, one by one, and
only when your copy is still exactly what your old release shipped. Your content folders, your own
notes below the `<!-- familiar:end -->` marker in `CLAUDE.md`, `AGENTS.md` and `GEMINI.md`, and any
release file you edited are left as they are. It deletes nothing.

1. Download the new release and unpack it as its own new folder. Do not unpack it into, or over,
   your project. Close any coding-host session that is open in the project.
2. See what would change. Nothing is written:

   ```text
   python "<new release>/familiar-workspace/.familiar/scripts/update.py" --project "<your project folder>"
   ```

   → verify: the report lists each release file as `same`, `update` (replaced, safely),
   `add` (new in this release), `diverged` (you or someone edited it; left alone) or `retired`
   (no longer shipped; left in place), and ends with `report only`.
3. If the report starts with `STOP`, nothing was written. The reason says what to do: a different
   `state-schema` is a migration that needs the release notes in [`CHANGELOG.md`](CHANGELOG.md)
   first, and a missing manifest means [updating by hand](#updating-by-hand).
4. Look at any `diverged` file. The updater keeps your version. If you want the release's version
   instead, compare the two by hand and copy the release's over yours.
5. If the project has extensions, add `--extension "<new extension drop-in folder>"` once for each
   extension you have a newer download of. An extension you name no copy for is left unchanged, and
   the report warns if the new core version is outside the range the extension declares.
6. Apply it — the same command with `--apply` added:

   → verify: the output ends with `applied; familiar-version -> <new version>` and a
   `project_check` line, and a rerun of step 2 shows `update 0, add 0`.
7. Open your coding host in the project and start a new session. Skills, agents and entry files are
   read at session start, so nothing from the new release is live until then.

Every file the updater replaced, and the old `.familiar-project`, is copied first into
`5-System/_update-backups/<old version>-to-<new version>_<date>/`. To roll back, copy that folder's
contents back over the project. Running the updater again is safe: it finds everything `same` and
keeps the first backup.

`/system-settings` → Update checks your version against a downloaded release from inside a session
and gives you the exact command. It does not run the updater itself, because the updater reads a
folder outside the current project, which is out of scope for anything familiar does from inside a
session (`CORE-WORKSPACE-SILO`).

A few files under `4-Trackers/` and `3-Knowledge/` carry release prose mixed with your actual data —
the format notes at the top of `tasks.md`, `timeline.md`, `_knowledge-index.md`, `_abbreviations.md`,
and `2-Drafts/_draft-index.md`. Because they hold real content too, neither the updater nor the
hand procedure replaces them the way it replaces `_about.md` and `_page-template.md`. The format notes
stay as they are with your data, so format changes in a new release do not reach an existing project
automatically. Compare them by hand afterward if a release's notes say one of those formats changed,
and hand-merge only what you want. Each of those files now carries only a short pointer to its
rules; the rules themselves live in `.familiar/core/state-schema.md`, which every update
already brings. In practice, what can drift is a table's columns.

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

**Why the updater can work in place.** An earlier design replaced release-owned folders inside the
project wholesale. That silently deleted any installed extension's package (`.familiar/extensions/`
lives under one of those folders), and it checked for a schema migration only after the
replacement. The updater avoids both: it touches only the files a release manifest lists, one owner
at a time, so an extension's files are never part of core's update, and it checks the schema and the
release's own integrity before it writes anything.

## The fleet hub

The fleet hub is a separate folder (`familiar-hub/`) that answers questions across all your
registered projects. It is not part of this download: get it from
[familiar-hub](https://github.com/familiar-md/familiar-hub), whose `INSTALL-HUB.md` covers setup and what the
hub reads. Setting up the hub creates `~/.familiar/fleet.md`, the list of your projects; after that,
`/system-settings` → Fleet adds, removes or updates a project's own row. Without a hub, the Fleet
branch registers nothing. Whether a project is active, paused or closed is recorded in the hub, not in the project.

## Extensions

An extension adds skills, agents, and knowledge for a specialty, in the same no-installer shape as
this release: not a plugin, and not wired through an installer. To add one to an existing
`familiar-workspace/` project, copy its `.claude/`, `.agents/`, `.codex/`, `.gemini/`, and
`.familiar/` top-level folders into the project root, merging with what is already there. Nothing in
a drop-in overwrites core files; it only adds skill, agent, and extension-package paths. No install
step and no restart beyond opening a new session — skills and agents are discovered by file presence,
same as core. No extension is part of this release. To write your own, start from
[familiar-template](https://github.com/familiar-md/familiar-template) ("Use this template"), which
follows `.familiar/core/extension-contract.md`; see each extension's own
`_about.md` for what it adds and its exact drop-in instructions.
