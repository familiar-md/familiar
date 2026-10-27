# `/system-settings` → Fleet

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md` → Naming and copies, `.familiar/core/status-format.md` → Update rules (non-negotiable), `5-System/Memory/status-snapshot.md`, the title of `5-System/project-config.md`, and `~/.familiar/fleet.md` when it exists.
- **Conditional context:** None.
- **Excluded context:** Every other project — their files and, in the registry, every row but this project's own. Every other file under `~/.familiar/`. Project content unrelated to registration.
- **Updates:** `~/.familiar/fleet.md` — this project's own row only, and only when the file already exists; the fleet hub creates it, this branch never does. Nothing inside the project. The write to `fleet.md` is the declared exception to `CORE-WORKSPACE-SILO`: the only out-of-project write this branch makes, and only on an explicit user request.
- **Capabilities:** file-read and file-write. Where a host cannot read or write outside the project folder, say so and stop. Give the user the exact registry row to paste instead; do not substitute a project-level write.
- **Completion:** The user has seen this project's registration, and any change they approved is written and read back — or they are told nothing was changed.

## What this is for

The fleet hub (`familiar-hub/`, a separate folder opened on its own) answers questions across every
registered project. The hub is distributed separately and is not yet published; this core release does
not include it. The hub creates `~/.familiar/fleet.md` when it is set up; until then there is nothing
to register in. The hub reads `~/.familiar/fleet.md` to know which projects exist. This branch is how a
project gets onto that list and comes off it. Whether a project is live (`active`, `paused`,
`reference`, `closed`) is the hub's to record, in the registry's `lifecycle` column, not this
project's: this branch never sets it. The hub never writes into a project, and this branch never reads
another one.

## Procedure

1. Find this project's root (the directory holding `.familiar-project`) as an absolute path. Read the
   registry if it exists and find this project's row by path, ignoring case and trailing separators.
2. Say in plain language: whether this project is registered and `included`, its category, and the
   `lifecycle` cell if the table has one (blank means `active`). Show no other row. Ask what to do:
   register, unregister, or nothing. If they want to pause or close the project, say that the hub
   owns it: run `python scripts/fleet_overview.py --set-lifecycle "<name>" paused|reference|closed|active`
   in the hub folder. Do not set it here.
3. **Register.** State the exact row and ask before writing (`CORE-HUMAN-APPROVAL`):
   `| <name> | <absolute path> | <category> | yes | <today> |`, with a final `active |` cell when the
   table's header has a `lifecycle` column. The name is the title in
   `5-System/project-config.md`, else the folder name. Ask the category (`work`, `personal`, or `unset`).
   - Already registered and `included` is `yes`: say so, change nothing.
   - Registered with `included` `no`: offer to set it to `yes`; do not add a second row.
   - A path containing `|` cannot be stored in the table: stop and say so.
   - No registry yet: do not create it, and write nothing. Say the fleet hub creates
     `~/.familiar/fleet.md`: set up the hub, then run `python scripts/fleet_overview.py --discover
     <folder holding your projects> --apply` inside it, which registers every project it finds.
4. **Unregister.** Set this project's `included` to `no` and keep the row, so the hub stops scanning
   it and the record survives (`CORE-NO-DELETE`). Deleting the row is the user's hand edit.
5. Before writing the registry, reread it immediately beforehand. Change only this project's row, or
   append it; leave every other line byte-for-byte as it was. The file has no revision header and
   gets none.
6. Read the written line back and tell the user what changed. Say the hub shows it the next time its
   overview runs, and that a project not yet registered will not appear there at all.

Never read or edit another project's row or files. Never write to `~/.familiar/user-preferences.md`
from here; that is Preferences.
