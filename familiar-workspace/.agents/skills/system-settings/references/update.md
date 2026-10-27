# `/system-settings` → Update

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

> **Maintainer note — why this branch only reports.** An earlier version of this procedure performed
> the update in place: it deleted `.familiar/` and every host skill/worker directory inside the current
> project, copied the new release's versions in, and restamped the marker — the six steps below in
> outline (establish versions, diff the release, replace release-owned paths wholesale, leave content
> folders alone, restamp the version, verify). Two defects settled this against continuing that way
> (`B-F08`, `_dev/reviews/2026-09-05/IMPLEMENTATION-PLAN.md` D3): `.familiar/` also holds every
> installed extension's package, so a wholesale replace silently deleted those
> installs along with the code being updated; and the schema-migration check ran only after the
> replacement and the version stamp were both already done, so by the time an incompatible schema was
> noticed there was nothing left to preflight — only a restore from the user's own backup copy. D3
> settled on a fresh folder with the content moved by hand. Since 2026-10-24 the in-place path is
> `.familiar/scripts/update.py`, which avoids both defects: it replaces only manifest-listed files,
> one owner at a time, and checks the schema before writing. It runs from a terminal, not from this
> branch, because it reads the new release outside the project. This branch never deletes or
> replaces anything; it reports and hands off.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, this project's `.familiar/installed.json` and `.familiar-project`, and the downloaded release the user is checking against.
- **Conditional context:** none.
- **Excluded context:** Project source documents, synthesized knowledge, other projects, and every content folder — this branch does not open or touch them.
- **Updates:** `nothing`. This branch only reads and reports.
- **Capabilities:** file-read.
- **Completion:** The installed and new-release versions are reported, schema compatibility is checked, and the user has the exact updater command (or the hand procedure when the project has no release manifest) from `INSTALL.md` → Updating.

## What this branch does

**There is no installer.** The update itself — `update.py` run from the new release against this
project, or the hand procedure — reaches outside the project this session is open in. That is out of scope for anything familiar does from inside a session
(`CORE-WORKSPACE-SILO`): a session cannot read or write a folder it isn't open in, and the new release
lives in one until the user has created it. This branch's job is narrower: tell the user whether an
update is warranted and safe, then give them the command or the procedure.

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

### 3. Note what else the release changed

The downloadable release carries no changelog beyond `VERSION`. If the user has network access,
suggest checking the release notes at `https://github.com/familiar-md/familiar/releases` for anything
beyond a version bump — in particular any format change to a file that mixes release prose with the
project's own data: `4-Trackers/tasks.md` and `timeline.md`, `3-Knowledge/_knowledge-index.md`,
`3-Knowledge/_abbreviations.md`, or `2-Drafts/_draft-index.md`. Those carry across unchanged when the five folders move in step 4 of the
documented procedure, so a format change there needs a manual look afterward, not before. `_about.md`
(every folder) and `3-Knowledge/_page-template.md` carry no per-project data, so the documented
procedure already has the user take the release's fresh copy of those instead — no format-drift risk
to flag for them.

### 4. Hand off

If this project has `.familiar/release-manifests/familiar.json`, give the user the updater command
with both absolute paths filled in, to run from a terminal with the session closed:

```text
python "<new release>/familiar-workspace/.familiar/scripts/update.py" --project "<this project's folder>"
```

Tell them it only reports, that the same command with `--apply` writes, and that each installed
extension needs `--extension "<its new drop-in folder>"` to be updated too (list the extensions under
`.familiar/extensions/`). Point to `INSTALL.md` → Updating → With the updater for the steps.

If the project has no release manifest, the updater will stop. Send the user to `INSTALL.md` →
Updating → Updating by hand instead: a new folder from the new release, extensions re-dropped, the
five content folders moved across, and `.familiar-project`'s `created` line carried forward.

Do not run the updater or attempt any part of the move yourself.

## Guardrails

- Apply `CORE-INSTRUCTIONS-READONLY` and `CORE-WORKSPACE-SILO`.
- Never delete, replace, or write to any path in this project as part of this branch — it reports
  only.
- Never claim a capability became active because this branch ran. Capability state is
  `.familiar/installed.json`'s to report, and it changes only when a health check passes.
- If the user asks this branch to run the update itself, say plainly that it can't — the update
  reads a folder outside the current project — and repeat the command and the `INSTALL.md` steps.
