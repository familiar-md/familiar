# `/system-settings` → Preferences

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md` → Naming and copies, `.familiar/state-schema.md` (the user-preferences row only), `5-System/user-preferences.md`, and `~/.familiar/user-preferences.md` when it exists.
- **Conditional context:** none.
- **Excluded context:** Other projects, `~/.familiar/fleet.md` (owned by the Fleet branch), every other file under `~/.familiar/`, and project content unrelated to preferences.
- **Updates:** `5-System/user-preferences.md` for this project's signature or a project-only entry, and `~/.familiar/user-preferences.md` (created if absent) for the default signature or a global entry. This branch's write to the global file is the declared exception to `CORE-WORKSPACE-SILO`: it is the only out-of-project write the branch makes, and only on an explicit user request.
- **Capabilities:** file-read and file-write. Where a host cannot read or write outside the project folder, say so and stop; do not substitute a project-level write for a global one.
- **Completion:** The user has seen both files and which one wins, and any change they approved is written with its revision header updated — or they are told nothing was changed.

## Procedure

1. Read both files. If `~/.familiar/` or the global preferences file does not exist, say so; it is created
   only if step 3 writes to it.
2. Show what is set, in plain language: this project's signature, or that it has none and borrows the
   default, each global standing preference, each project preference, and where the two disagree,
   which one wins (the project's). Ask what the user wants to do: set or change this project's
   signature, set or change the default signature, add, edit or remove a standing preference, or
   nothing.
3. For a change, state the exact text and the file it goes in, and ask before writing
   (`CORE-HUMAN-APPROVAL`). The default scope of a standing preference is **all familiar projects**
   (the global file).
   - **The signature belongs to the project.** It is this project's familiar: the bind line shows it
     and the fleet hub labels the project with it. Write it to this project's
     `5-System/user-preferences.md` as the line `- **familiar signature:** <key>` under the title.
     A key is three characters, a small glyph rather than initials. When the user has no key in mind,
     show the palette below and let them choose, or take their own. Never offer the default signature,
     which every project without its own already shows. This branch cannot see other projects; the
     fleet hub's brief reports two projects sharing a key.

     | Theme | Keys |
     |---|---|
     | Geometric | `ili` `ivi` `i_i` `[-]` `[o]` `{o}` `-i-` `o-o` `.:.` `+o+` |
     | Animal, subtle | `v_v` `^v^` `ovo` `o.o` `-v-` `u_u` `'v'` `nvn` `q_p` `=w=` |

     A key the user writes themselves is plain ASCII and has no `*`, `` ` ``, `|`, `~`, `<`, `>` or `\`: those
     break the bind line's italics, a table, or the hub's reading of the key, or render as HTML, and a Windows console
     can garble anything non-ASCII.
   - The **default signature** in the global file is shown by every project that has none of its own.
     Set or change it only when the user asks for the default.
   - Global preferences are **behavioural only**: tone, referencing method, tidy approval, the
     default signature. Organisation, domain, and other project facts belong in
     `5-System/project-config.md`; say so and offer nothing further.
   - A project-only preference is written to `5-System/user-preferences.md` under the same rules as
     `/save to-memory`.
4. Before writing the project file, read its `revision:` header, reread it immediately before the
   write, stop if it moved (`CORE-STALE-WRITE`), and increment it after. Before writing the global
   file, read its `revision:` header. If it has none, this is its first
   write: add `<!-- revision: 1 -->` and `<!-- last-updated: <date> -->` above the title
   `# User Preferences (global)`, followed by one line: "Edited by you or by `/system-settings` →
   Preferences. `/save to-memory` never writes here." Otherwise
   reread it immediately before the write, stop if the revision moved (`CORE-STALE-WRITE`), and
   increment it after.
5. Write the approved change and nothing else in that file. Read it back and tell the user the line
   that changed. If the signature changed, say it takes effect at the next session's bind line.

Never write to `~/.familiar/fleet.md`; that is the Fleet branch. Apply `CORE-NO-DELETE`: removing a preference deletes only the
single entry the user named, after they confirm it.
