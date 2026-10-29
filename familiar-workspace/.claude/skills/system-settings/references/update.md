# `/system-settings` → Update

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

> **Maintainer note — why the updater, never a hand copy.** An earlier version of this procedure
> performed the update in place by hand: it deleted `.familiar/` and every host skill/worker
> directory, copied the new release's versions in, and restamped the marker. Two defects settled
> against that (`B-F08`): `.familiar/` also holds every installed extension's package, so a wholesale
> replace deleted those installs, and the schema check ran only after the replacement. The in-place
> path is `.familiar/scripts/update.py`, which replaces only manifest-listed files, one owner at a
> time, and checks the schema before writing. This branch runs it for the user, so updating needs no
> terminal: the new release is a folder the user names, read for this task only
> (`routes.md` → Files outside the project), and every write lands in this project.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, this project's `.familiar/installed.json` and `.familiar-project`, and the downloaded release folder the user names.
- **Conditional context:** an extension's new drop-in folder, only when the user names one.
- **Excluded context:** Project source documents, synthesized knowledge, other projects, and every content folder — this branch does not open or touch them.
- **Updates:** release-owned files only, written by `.familiar/scripts/update.py --apply` after the user's yes: replaced and added files, untouched retired files moved into `5-System/_update-backups/`, `.familiar-project`'s `familiar-version` line, and `.familiar/release-manifests/`. This branch's declared exception to `CORE-INSTRUCTIONS-READONLY`.
- **Capabilities:** file-read, and running a Python script, which does the writing; this branch edits no file itself. Where the host cannot run one, step 6 says what to do.
- **Completion:** The versions and schema are reported, the updater's report is shown in plain words, and either the update is applied and read back or the user has declined — or, where the updater cannot run here, the user has the exact command or the hand procedure from `INSTALL.md` → Updating (https://github.com/familiar-md/familiar/blob/main/INSTALL.md#updating).

## What this branch does

**There is no installer.** The user downloads the new release and unzips it as its own folder,
anywhere but inside this project. This branch checks that the update is warranted and safe, runs the
updater in report mode, explains what it would change, and applies it on a yes. Most users never
open a terminal for this.

## Procedure

### 1. Establish both versions

Read this project's installed version from `.familiar/installed.json` → `core.version`, and the
version it was set up at from `.familiar-project`'s `familiar-version` line. Read the new release's
`VERSION` file. Report all three.

If the two project values disagree, say so: it means a previous manual update moved the content
folders across without correcting the marker, and the marker is the one that is wrong.

Also read `core.build` from both `installed.json` files: this project's and the new release's.
A release build stamps it with the commit it was built from. A copy taken straight from source has
none.

- **The new version is newer:** an update is available. Continue.
- **The versions are equal and both builds are present but different:** the release is a
  different build of the same version, usually one carrying later fixes. Report both builds, say
  an update is available, and continue.
- **The versions are equal and either build is missing:** say that the version alone cannot show
  whether anything changed, and ask the user whether to continue.
- **Otherwise** (older, or the same version and the same build): say so and stop — there is
  nothing to update to.

### 2. Check schema compatibility

Compare this project's `.familiar-project` → `state-schema` line against the new release's own
`.familiar-project`. If they differ, tell the user plainly: this is a schema migration, not a routine
update, and neither this branch, the updater nor the hand procedure performs one. Point them at the
release notes or ask them to get help before doing anything else.

If they match, say so and move to step 3.


### 3. Ask for the release folder

If the user has not named it, ask where they unzipped the new release: the folder holding its own
`.familiar-project` and `.familiar/`. A folder inside this project is refused (`update.py` stops on
it); ask them to move it out. Ask the same for any extension they also downloaded (list the ones under
`.familiar/extensions/`). Suggest a look at the release notes at
`https://github.com/familiar-md/familiar/releases` when they have network access.

### 4. Run the report

With the project's root and the release folder as absolute paths, run the release's own copy:

```text
python "<release folder>/.familiar/scripts/update.py" --project "<this project's folder>"
```

adding `--extension "<folder>"` once per extension named in step 3. It writes nothing. Explain the
report in plain words: how many familiar files would be replaced, added and left alone; each
`diverged` file by name (someone edited it, so it is kept and the release's version is not used);
each `retired` file and whether it moves to the backup or stays because it was edited. If it begins
with `STOP`, say why in plain words and stop; a missing manifest means the hand procedure (step 6).

### 5. Apply on a yes

Ask once (`CORE-HUMAN-APPROVAL`). On a yes, run the same command with `--apply`. Read the output
back: it ends with `applied; familiar-version -> <version>`, the backup folder and a `project_check`
line. Run the report once more; `update 0, add 0` confirms it. Then tell the user to close this
session and start a new one: skills, agents and entry files are read at session start, so nothing
new is live until then.

### 6. When the updater cannot run here

If no Python 3.10+ is available, follow `.familiar/core/running-scripts.md` first. If the host cannot
run a command or read the named folder (a hook guard, a sandbox, a host without a shell), say so
plainly and give the exact command with both paths filled in, to run from a terminal; offer to walk
through it. If the project has no release manifest, send the user to `INSTALL.md` → Updating →
Updating by hand.

## Guardrails

- Apply `CORE-WORKSPACE-SILO`: the release folder is read, never written; every write is the
  updater's, inside this project.
- Write nothing by hand. Every change is `update.py`'s, and only after the user's yes; never edit,
  copy or delete a release file yourself.
- Never claim a capability became active because this branch ran. Capability state is
  `.familiar/installed.json`'s to report, and it changes only when a health check passes.
