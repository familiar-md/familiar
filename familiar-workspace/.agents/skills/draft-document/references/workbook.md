# `/draft-document` → Workbook

> Branch of the `draft-document` router. Reached only from `/draft-document`, or when the user asks
> for this branch in words; never from a route match alone. Load this file after the branch is
> selected, then follow the context contract below and load nothing from the other branches.

For an Excel deliverable: a tracker, a screening or extraction tool, a register, a summary workbook.
Workbooks were the most common thing built in real use, and the two ways they went wrong were
silent loss (a saved version without the drop-downs, shapes or images its source had) and a sheet
only its builder could read.

## Context contract

- **Required context:** `.familiar/core/file-handling.md`, `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, project configuration, and the project sources the workbook draws on.
- **Conditional context:** the deliverable's `2-Drafts/<slug>/_brief.md` only when it exists; the existing workbook only when revising one or starting from a template, per `CORE-COPY-ON-EDIT`.
- **Excluded context:** the Document, Deck and Review branches, other projects, and undeclared extension content.
- **Updates:** one new version under `2-Drafts/` (saved with `.familiar/scripts/draft_save.py --ai`), and its build script at `2-Drafts/<slug>/_build/` when a script built it.
- **Capabilities:** file-read, file-write, and `document-tools` for workbooks (openpyxl, or Excel on this machine), confirmed live before relying on either; `scripts/xlsx_check.py` needs only Python.
- **Completion:** the new version is saved and registered, `scripts/xlsx_check.py --compare` reports nothing lost against its source (or every loss was agreed with the user first), and the report names the sheets, what each is for, and anything the workbook still needs from a person.

## Procedure

0. **Brief.** As in the Document branch step 0: use a locked `_brief.md` for audience, purpose and
   structure; with a working brief or none, say so in one line and continue.
1. **Schema first.** Before building, show the user the plan in a few lines: each sheet's name and
   purpose, and on each data sheet the columns and what one row is. Ask before building when the
   workbook is new or its structure changes. Reuse the user's existing workbook structure when one
   exists; do not invent a parallel one.
2. **Check the source.** When revising a workbook or starting from a template, run
   `python -X utf8 scripts/xlsx_check.py <source>` (the skill's own `scripts/` folder: `.claude/skills/draft-document/scripts/`
   on Claude Code, `.agents/` in place of `.claude/` on Codex and Gemini).
   - **Open in Excel** (a `~$` lock file): ask the user to save and close it. Do not read a file
     mid-edit or write beside it.
   - **Anything openpyxl would remove** (newer-format drop-downs, shapes, form controls, slicers):
     do not round-trip the file through openpyxl. Where Excel is installed, make the change through
     Excel itself (a short PowerShell COM script that opens a copy, edits cells and saves), which
     keeps every feature. Otherwise tell the user what would be lost and get their yes, or build the
     new content as a separate sheet or workbook the user pastes in.
   - **Macros** (`.xlsm`): load with `keep_vba=True` and save as `.xlsm`.
3. **Build** to the path `draft_save.py next --slug <slug> --ext xlsx|xlsm --ai` printed, never to a
   path of the script's own choosing. Save the build script as
   `2-Drafts/<slug>/_build/<the version's filename stem>.py` (`file-handling.md` → Boundaries).
4. **Readable by someone who did not build it.**
   - A first sheet named `About` says what the workbook is for, what each sheet holds, the sources
     and their dates, and what is still open.
   - Column headers in plain words. Every ID column sits next to a column that names the thing
     (`CORE-PLAIN-NAMES`): a study ID beside the author and year, a gap ID beside the gap.
   - One table per sheet, starting at the top left, with the header row frozen and filters on. No
     merged cells inside a data table.
   - Colour only with a legend on the same sheet saying what each colour means. A colour nobody
     can explain is noise.
   - Totals and counts as formulas, not typed numbers, so they stay right when rows change.
   - A summary sheet stays short: the few columns a reader needs, with detail on its own sheet.
5. **Verify.**
   - `python -X utf8 scripts/xlsx_check.py --compare <source> <new>`: anything listed as lost is a
     defect unless the user agreed to it in step 2.
   - Reopen the new file with the library to confirm it loads. Where Excel is installed, open it in
     Excel through COM, recalculate, and confirm it opens without a repair prompt; a file saved by
     openpyxl has no calculated values until then.
6. **Save and report.** Register the version with `draft_save.py register`. Report the path, each
   sheet and its purpose in one line, the `--compare` result, and anything left for a person.

## Guardrails

- Never edit the user's own copy in place (`CORE-COPY-ON-EDIT`); every pass writes a new version.
- Never let a workbook be the only record of a project decision. A decision goes to memory through
  `/save`; the workbook can repeat it.
- When the user asks for a "simple" or "summary" version, cut columns and sheets rather than adding
  explanation. Ask which three questions the sheet must answer if that is unclear.
