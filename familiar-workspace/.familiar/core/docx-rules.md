# Word-processing document rules

`document-tools` is `available`, not `active`, for a `.docx` deliverable: whether it actually works
depends on this host having Python plus `python-docx` installed, and optionally a LibreOffice
`soffice` binary for a rendered PDF to visually inspect. Run
the `draft-document` skill's `scripts/build_docx.py` with `--health-check` before relying on either.

## Three ways to start

| Mode | Meaning | Body of the source |
|---|---|---|
| `--build` | Create from nothing | n/a — no source document |
| `--from-template ... --mode shell` | "Use this document's look for a new report" | Cleared; page setup, headers/footers, and styles kept |
| `--from-template ... --mode extend` | "Use this document as a starting point" | Kept; new content appended after it |
| `--revise` | "Change this document" | Kept; only targeted plain-text paragraphs change |

**There is no default mode for `--from-template`.** The caller must say `shell` or `extend` — a
silent guess is how a report ships with the previous project's table still in it. `--revise` locates
each edit by the exact text of a whole paragraph (not a substring); an anchor that matches zero or
more than one location is refused rather than guessed at. Whole-cell replacement is not supported
because it can remove a table's internal structure. A `replace` on a paragraph carrying non-text
content (an image) is also refused rather than silently destroying it — narrow the edit or accept the
limitation and say so.

A `--revise` replacement keeps the character formatting of the runs it replaces — a rebuilt run
inherits the anchor's font, size and weight, and a note run adds only its own color and italic on
top. Formatting the task did not ask to change is not a free variable: a template that mandates a
font is not satisfied by a paragraph that silently fell back to the style default.

**Tracked changes do not survive `--revise` or `--from-template extend`.** python-docx has no API to
create, read, or reliably preserve `w:ins`/`w:del` markup through run-level surgery — if the task
requires an edit that should show as a tracked change, or the source carries tracked changes that
must remain, do not use either. Use the Review branch of `/draft-document` (`scripts/tracked_edit.py`),
which only adds tracked changes and comments and leaves the team's markup byte-identical.

## Content and copies

- Apply `CORE-COPY-ON-EDIT` to an existing document.
- Preserve styles, comments, fields, hyperlinks, headers, footers, and embedded objects unless the
  task explicitly changes them.
- Keep source facts traceable with useful locators.
- Place the new version in `2-Drafts/` and follow `file-handling.md`.

## Editor notes

An inline note that talks to the editor rather than being part of the document's own content — a
source citation/locator, or a `voice.md` → Uncertainty marker `[verify]` or `[action: ...]` flag —
is never left as plain text in the body font. Give it its own run instead of folding it into the
paragraph string: a SPEC.json paragraph (`--build`/`--from-template`) or an EDITS.json edit
(`--revise`) can carry `"runs": [{"text": "..."}, {"text": "[verify]", "note": "certainty"}]` in
place of a plain string — see `build_docx.py`'s module docstring for the exact shape. Three note
types are supported, each a fixed color plus italic so an editor scanning the page sees which is
which without reading it: `reference` (teal) for a citation or locator, `primary-reference`
(purple) for the source-native citation marker a `reference` claim traces back to (ingest.md's
`ref_carry_through` — the underlying study, not the compiled document citing it), and `certainty`
(amber) for a `voice.md`
uncertainty marker — both `[verify]` and `[action: ...]` share this one color; they differ in
wording, not formatting, because both are the same kind of thing to an editor scanning the page:
something to resolve before filing. Deliberately colored text, not a highlight: a background fill
reads as "look here right now," while a note that will sit on the page through several editing
passes before it's resolved reads better as a quieter, still-unmistakable combination. An
unrecognized note type is refused, not guessed at. The marker text itself is unchanged — only its
formatting is — so `[verify]` and `[action: ...]` still mean what `voice.md` says they mean; this
only stops them from disappearing into the body font while editing.

**Dual citation.** A claim pulled from a knowledge page carries two provenance layers whenever the
page's own `ref_carry_through` field shows it kept its source-native marker: the compiled document
it came from (a compiled report, review or similar — `reference`, teal) and the primary source that document
itself cited for the claim (`primary-reference`, purple). Both runs are written, back to back,
never merged into one: `{"runs": [{"text": "Revenue grew faster than costs "}, {"text": "[Market Review v8.0,
§4.2]", "note": "reference"}, {"text": " "}, {"text": "[Lee, 2025]", "note":
"primary-reference"}]}`. Citing only the compiled document when its own knowledge page shows a
carried source-native marker for that claim is the exact failure this convention exists to catch
— see ingest.md → Ingest procedure step 4. The other cases:

- A claim drafted from the primary paper itself, read by the team, gets only the purple run, with
  its locator inside it (`[Lee, 2025, p.4]`).
- A claim from a compiled document that names no primary for it (an `n/a` page, or a claim tagged
  `[ref: ambiguous]`) gets only the teal run. Add `[verify]` when the document will carry a
  public reference list, because that claim has no citation to give it yet.
- A claim from a source that is not literature (meeting notes, a client email) gets only the teal
  run.

The teal run records where the text came from, for the editor. The purple run is the citation the
reader will see. A confidential compiled document is never cited in a document that leaves the
project. A published review is cited in its own right only for its own synthesis, never in place of
the primary data it reports.

**What a citation claims.** A citation tells the reader that the source states this sentence. Being
about the same topic is not enough.

- Cite each sentence. A citation block at the end of a paragraph implies that every figure in the
  paragraph is supported.
- A teal tag on a figure that its compiled document does not contain is as wrong as a fabricated
  citation. Check the source's text, not its topic.
- Take each purple tag from the compiled document's own numbered reference list, as carried on the
  knowledge page. Never take it from memory or a search.
- Keep the source's exact wording for negatives and qualifiers. "Does not recommend" and "has no
  formal recommendation" are different claims. Do not add a qualifier the source does not state.
- Cite each source at its first citable statement. When the text moves on to another source, name
  that source's study type or setting.

Retrieving the primary paper is not the default. Retrieve it only when:

- the compiled document does not state the claim (for example, one number taken from a range);
- the wording, number or population differs from the compiled document;
- the claim is used outside that document's context (another population, setting or scope);
- a reviewer or the client questions the claim; or
- the source is a review article or slide deck that the client did not verify.

**Referencing method.** A project records how its citations become final as one line in
`5-System/user-preferences.md`: `Referencing method: none | manual | extension`. `none` means the
colored tags are the final form. `manual` means someone types the reference list by hand.
`extension` means an installed citation extension converts the purple tags into reference-manager
fields; core only drafts the tags and never writes those fields itself. The first time a
Word draft writes a citation and the line is absent, ask once and record the answer there. Never
ask at project setup. The tag format above never changes with the method. The method changes only
how tracked review treats existing reference-manager fields and what finalization does. Only the
Document branch of `draft-document` reads it; decks do not.

**Provenance when tags become fields.** When a purple tag becomes a reference-manager field, its teal
provenance moves to a comment on that citation (for example, "Text from Market Review §4.2, ref 19.
Primary not reviewed.") and into the trace sidecar. It is never deleted silently.

**Trace sidecar.** A Word draft or deck that leaves the project and carries citations gets a trace sidecar:
a Markdown file beside the draft, named with the draft's filename stem plus `_trace.md`. It is
internal lineage, never a Word appendix and never part of the deliverable. It starts with
frontmatter carrying the same producing skill, version, model and effort as the draft's
`_draft-index.md` row. It then has one row per cited statement:

| Section | Statement (short form) | Teal source and locator | Purple primary | Grade |
|---|---|---|---|---|

Write `—` in a column that has no tag for that statement.

**Claims check.** Before each handoff of such a draft, grade every cited statement and record the
grade in the sidecar:

- *primary verified*: the purple tag was checked against the primary paper's own text;
- *compiled source*: the teal tag was checked against the compiled document's text, and its purple
  tag came from that document's reference list, but the primary was not reviewed. This is
  acceptable;
- *unsupported*: the source does not state the claim, or a `[verify]` is still open. This needs
  action before filing.

Report the count of each grade in the completion report, and name every *unsupported* statement.

**Revising a document that predates this convention.** `document.md` step 2 governs only the
content a run writes itself; it does not retroactively fix paragraphs a `--revise` pass did not
touch. A revise pass over a document that does not already follow this convention throughout must
do one of two things — never neither: bring the whole file up to it, or say plainly in the
completion report that only the touched passages carry note formatting and the rest predates the
convention. A half-converted document — some citations teal, others plain body text — must never
be handed over as if it were finished; the reader cannot tell "not yet checked" from "this note
convention doesn't apply here." The `--validate` note-formatting check (see Build and validation)
makes this mechanically checkable — run it before claiming a revised document is done.

## Build and validation

1. Inspect document structure before editing. For `--from-template` or `--revise`, decide the mode
   from what was actually asked (see the table above) — never default to one.
2. `"build": false` from the health check — report `document-tools` unavailable (Python or
   `python-docx` missing on this host) and stop. Do not switch to an unvalidated conversion path.
3. Make the smallest requested change in a new copy, using the mode the task calls for:
   `build_docx.py --build SPEC.json OUT.docx`, `--from-template TPL.docx SPEC.json OUT.docx --mode
   shell|extend`, or `--revise SOURCE.docx EDITS.json OUT.docx`.
4. Run the structural validator: `build_docx.py --validate OUT.docx`. It always checks editor-note
   formatting — a bracketed citation or `[verify]`/`[action: ...]` flag left in an uncoloured,
   non-italic run is reported — regardless of `--source`, since that check is meaningful on a
   single file. For `extend` or `revise` — where nothing should have been lost — add `--source`
   (the template or source file) so it also checks headers, footers, table count, embedded-image
   count, and character formatting against it. Counting objects alone is not enough: a revision can
   keep every table and image and still drop the font the document is required to be written in, so
   the font/size mix is compared as a share of total text. Skip `--source` for `shell`, which
   intentionally clears the body; a preservation check against the source would flag the very thing
   the mode is asked to do.
5. `"visual_validation": true` from the health check — render to PDF
   (`build_docx.py --render OUT.docx OUT_DIR`) and inspect every page for overflow, clipping,
   broken tables, missing glyphs, and unexpected pagination. `"visual_validation": false` — state
   this limitation plainly before delivering: only structural validation ran.
6. Re-run structural (and visual, if available) validation after the final change.
7. **Open it in Word** where Word is installed: run the `draft-document` skill's
   `scripts/office_render.ps1 -Path OUT.docx` through `powershell -NoProfile -ExecutionPolicy Bypass
   -File`. `"opened": false` means Word refuses the file or must repair it, which no Python check
   or LibreOffice render catches; that is a defect to fix before delivery. Report its page,
   tracked-change and comment counts. Where Word is absent, say the Word check did not run.
8. **Read it as a stranger** when it leaves the project. After the last edit, the whole document goes
   to a reader with no project context: a worker given only the file when `named-subagents` is
   `active`, otherwise a full re-read from the first page to the last. It lists every reference the
   reader cannot resolve ("the second question", "the cohort"), every list with no stated
   consequence, every section that ends without a conclusion, and every claim about a source that
   has no citation. Fix each one, or name it in the completion report. A rewrite pass is not finished
   until this read has been done on the rewritten file.

Never claim integrity from a successful file write alone — structural validation is the minimum,
not the finish line.
