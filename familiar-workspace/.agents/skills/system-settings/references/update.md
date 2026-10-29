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
> time, and checks the schema before writing. The downloads go in the project's own `_update/`
> folder, so the session never reads outside the project and a reads guard never blocks it.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, this project's `.familiar/installed.json` and `.familiar-project`, and the file list of `_update/`.
- **Conditional context:** a release folder outside the project, only when the user names one instead of the drop zone (step 5).
- **Excluded context:** Project source documents, synthesized knowledge, other projects, every content folder, and the contents of the downloads themselves — the updater reads those, this branch does not.
- **Updates:** release-owned files only, written by `.familiar/scripts/update.py --apply` after the user's yes: replaced and added files, untouched retired files moved into `5-System/_update-backups/`, `.familiar-project`'s `familiar-version` line, and `.familiar/release-manifests/`. This branch's declared exception to `CORE-INSTRUCTIONS-READONLY`. It never deletes the downloads in `_update/`.
- **Capabilities:** file-read, and running a Python script, which does the writing; this branch edits no file itself. Where the host cannot run one, step 5 says what to do.
- **Completion:** The updater's report is shown in plain words, and either the update is applied and read back or the user has declined — or, where the updater cannot run here, the user has the exact command or the hand procedure from `INSTALL.md` → Updating (https://github.com/familiar-md/familiar/blob/main/INSTALL.md#updating).

## What this branch does

**There is no installer.** The user downloads the new zips — core, and any extension or hooks
package they use — and puts them in the project's `_update/` folder, zipped or not. This branch runs
the updater in report mode, explains what it would change, and applies it on a yes. Core and every
extension found there update together; an extension with no new download is left as it is. Most
users never open a terminal for this.

## Procedure

### 1. Check the drop zone

List `_update/`. If it is missing or holds no `.zip` file or folder besides `_about.md`, tell the
user what to do and stop: download `familiar-workspace-<version>.zip` from
`https://github.com/familiar-md/familiar/releases`, plus the newer zip of each extension listed under
`.familiar/extensions/` or of the hooks package if they want those updated too, put them all in
`_update/`, and run this branch again. Read this project's version from `.familiar/installed.json` →
`core.version` and say it.

### 2. Run the report

```text
python .familiar/scripts/update.py --project . --from _update
```

It writes nothing. Explain the report in plain words:

- the version line (`<project>: familiar <old> -> <new>`) and, when present, the build line;
- per owner (`[familiar]`, then each extension), how many files would be replaced, added and left
  alone;
- each `diverged` file by name (someone edited it, so it is kept and the release's version is not
  used);
- each `retired` file and whether it moves to the backup or stays because it was edited;
- each note: an extension with no new copy, an extension whose declared core range the new version
  is outside, a download that is not installed here, several copies of one release (the newest is
  used).

If it begins with `STOP`, say why in plain words and stop. A different state schema is a migration
that needs the release notes first; a missing manifest means the hand procedure (step 5). When every
owner shows `update 0, add 0` and nothing is retired, say there is nothing to update and stop.

### 3. Apply on a yes

Ask once (`CORE-HUMAN-APPROVAL`). On a yes, run the same command with `--apply`. Read the output
back: it ends with `applied; familiar-version -> <version>`, the backup folder and a `project_check`
line. Run the report once more; `update 0, add 0` confirms it.

### 4. Close out

Tell the user three things: close this session and start a new one, because skills, agents and
entry files are read at session start; the downloads in `_update/` can now be deleted, by them; and
the backup folder the update wrote, for a rollback.

### 5. When the updater cannot run here

If no Python 3.10+ is available, follow `.familiar/core/running-scripts.md` first. If the host cannot
run a command (a sandbox, a host without a shell), say so plainly and give the exact command from
step 2, to run from a terminal in the project folder; offer to walk through it. If the user would
rather keep the release outside the project, they may name its unzipped folder: run that release's
own `.familiar/scripts/update.py --project "<this project>"` with `--extension "<folder>"` per
extension, read-only for that folder (`routes.md` → Files outside the project). If the project has
no release manifest, send the user to `INSTALL.md` → Updating → Updating by hand.

## Guardrails

- Apply `CORE-WORKSPACE-SILO`: the downloads are read by the updater, never written; every write is
  the updater's, inside this project.
- Write nothing by hand. Every change is `update.py`'s, and only after the user's yes; never edit,
  copy or delete a release file or a download yourself.
- Never claim a capability became active because this branch ran. Capability state is
  `.familiar/installed.json`'s to report, and it changes only when a health check passes.
