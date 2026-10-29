# `/draft-document` → Review

> Branch of the `draft-document` router. Reached only from `/draft-document`; the user
> starts it, never a route match. Load this file after the branch is selected, then follow the
> context contract below and load nothing from the other branches.

For a Word file the team already owns: tracked changes, comment threads and, often, reference-manager
fields are in it. This branch edits that file in review passes. It does not rebuild it. Building a
new document, or revising your own draft, is the Document branch.

## Context contract

- **Required context:** `.familiar/core/docx-rules.md`, `.familiar/core/file-handling.md`, `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, project configuration, and the live team copy of the document.
- **Conditional context:** the deliverable's `2-Drafts/<slug>/_brief.md` when it exists, and every file its `Standards` line names (an extension's drafting standards, for example); the `Referencing method` line in `5-System/user-preferences.md`, for how existing citation fields are treated; `4-Trackers/` or project sources only when a requested edit needs a fact from them.
- **Excluded context:** the Document and Deck branches, other projects, and undeclared extension content.
- **Updates:** one new version under `2-Drafts/` per pass, saved with `.familiar/scripts/draft_save.py` (`adopt` first when the team returned an edited file); its `_trace.md` sidecar when the pass adds or changes a cited statement.
- **Capabilities:** file-read, file-write, and `document-tools`, confirmed live with `scripts/build_docx.py`'s health check. A renderer is optional.
- **Completion:** the pass is saved as a new version, `scripts/tracked_edit.py --check` reports no problems, and the report lists what was edited, what was refused and why, and every comment still waiting on a person.

## Rules

1. **Every edit is a tracked change** by the author "AI Review", or a comment by that author. A
   reply goes inside the existing thread.
2. **Never accept, reject or delete** another person's tracked change or comment. Never edit or resolve
   a comment addressed to the client (`Note to <client>:`); the script will not reply to one.
3. **Never edit an existing reference-manager field.** For a new citation, clone an existing field of
   the same kind (EndNote: `ADDIN EN.CITE`). With no field to clone, write a placeholder such as
   `[N: Author Year]` and add a comment carrying the full reference. The script treats a field and
   its result text as opaque and refuses an anchor inside one.
4. **One canonical file per round.** Before the pass, confirm with the user which file is the live
   team copy and that it is saved and closed in Word. Edit that file's latest version, not a copy
   that has since been edited. If two sessions will edit different sections, plan the merge before
   either starts; this branch does not merge.
5. **The source is never edited** (`CORE-COPY-ON-EDIT`). The pass writes a new version.

## Procedure

1. Confirm the live team copy per rule 4. If the user hands over a file edited outside familiar, run
   `draft_save.py adopt` on it first so it enters the version history under its author marker.
   Read the deliverable's `_brief.md` if it exists: its argument is what every edit must keep, and
   the files on its `Standards` line apply to this pass as if they were listed above. An edit that
   would change the brief's argument is a comment to the user, not an edit.
2. Read the document and list its comments: `python scripts/tracked_edit.py --list-comments <file>`.
   Sort the comments into: addressed to the AI, addressed to the team, addressed to the client
   (`Note to ...`). Act only on the first group unless asked.
3. Write an `edits.json` (shape in the script's docstring): `replace`, `delete`, `insert_after`,
   `comment`, `reply`. Anchors are exact text from one paragraph. Cite per `docx-rules.md` → Editor
   notes → Dual citation, and use rule 3 for any new reference-manager citation. Attach a `comment`
   to a change when the reason is not obvious to the next reader.
4. Run `draft_save.py next --slug <slug> --ext docx --ai`. It moves earlier versions, so take
   `<source>` from its `source now at:` line and `<new-path>` from its `write:` line, then run
   `python scripts/tracked_edit.py --apply <source> edits.json <new-path>`. It is all-or-nothing: any
   refused edit is listed and nothing is written. Fix the anchor or drop the edit, and rerun.
5. Verify, in order:
   - `python scripts/tracked_edit.py --check <source> <new>`: rejecting the AI Review changes reproduces the
     source text, every tracked change, comment and field in the source is byte-identical, and all new
     markup is by "AI Review".
   - `python scripts/tracked_edit.py --accept-copy <new> <scratch-copy>` then
     `python scripts/build_docx.py --validate <scratch-copy> --source <source>`. Run the formatting
     checks on the accepted copy, because tracked insertions skew the font-share check. Delete the
     scratch copy afterwards; it is not a draft.
   - When a renderer is available, render `<new>` and read the pages for the changed passages.
6. Register the version with `draft_save.py register`. If the pass added or changed cited statements,
   update the `_trace.md` sidecar and rerun the claims check (`docx-rules.md` → Editor notes → Claims
   check).
7. Report: edits applied, edits refused with the reason, comments left for people, and the saved path.

## Known traps

- **LibreOffice does not render a deletion nested inside an insertion.** The script never nests one.
  If a render of a team-edited file looks wrong there, that is a render artefact; check the XML.
- **Tracked paragraph splits make `validate.py --original` report false differences.** Treat differences
  at tracked paragraph boundaries as expected, and trust `--check` for the safety question.
- **Text inside another author's insertion is not editable.** Changing a colleague's new wording means
  a comment suggesting the change, not an edit.
- **Hyperlinks and fields are opaque.** An edit that needs to change linked text is a comment.
- **A comment with no paragraph id cannot be threaded** without editing it. Add a new comment instead.

Never report a pass complete from a successful write alone; `--check` is the evidence.
