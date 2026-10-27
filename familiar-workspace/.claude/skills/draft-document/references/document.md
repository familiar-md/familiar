# `/draft-document` → Document

> Branch of the `draft-document` router. Reached only from `/draft-document`; the user
> starts it, never a route match. Load this file after the branch is selected, then follow the
> context contract below and load nothing from the other branch.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, project configuration, and the project sources explicitly required by the document.
- **Conditional context:** the deliverable's `2-Drafts/<slug>/_brief.md` only when it exists, with every file its `Standards` line names, and the `authority` file or template its profile names only when the brief is locked; `.familiar/core/docx-rules.md` only when the requested artifact is a Word document (`.docx`); the existing document only when revising one, per `CORE-COPY-ON-EDIT`.
- **Excluded context:** Other projects, unrelated project history, and undeclared extension content.
- **Updates:** one new version under `2-Drafts/` (saved with `.familiar/scripts/draft_save.py`); its `_trace.md` sidecar when the claims check runs; the `Referencing method` line in `5-System/user-preferences.md` the first time it is asked.
- **Capabilities:** file-read, file-write, and `document-tools` for a Word document, confirmed live with `scripts/build_docx.py`'s health check; a plain Markdown or text document needs only file-read and file-write.
- **Completion:** The document is written and, when `document-tools` produced it, passes structural validation, plus visual validation when a renderer was available — or the missing capability is explicitly reported before an invalid artifact is produced.

## Procedure

0. **Brief.** Find the deliverable's slug from the request or `_draft-index.md`, and ask if it is
   unclear. Then look for `2-Drafts/<slug>/_brief.md`.
   - **Locked:** take the audience, format, mandatories, key points and outline from it, and do not
     ask again what it settles. Draft to its headlines, in order. Mark its accepted evidence gaps
     `[verify]`. If its profile names an `authority` form or a fillable template, propose it as the starting template.
   - **Working (not locked):** say in one line that the brief is not locked, then continue and use it.
     Treat its `proposed` fields as open.
   - **None:** say in one line that `/deliverable-brief` can scope the deliverable first, then continue.
   Never write to the brief. If drafting shows that the argument must change, finish the draft to the
   brief and tell the user to amend it with `/deliverable-brief`.
1. Confirm the format the user wants and who reads the output (`voice.md` → Audience). Not the
   file's DRAFT/REVIEW/FINAL status — a document that will eventually leave the project (a
   submission, a client deliverable) is written for that external reader from the first drafted
   word. The internal-audience exemption is only for a document that never leaves the project at
   all (a review record, a tracker). If the request doesn't make the audience obvious, ask; it
   changes every sentence. A `.docx` deliverable needs `document-tools`; a Markdown or plain-text
   document does not.
2. **Format is `.docx`:** run `scripts/build_docx.py` with `--health-check`.
   - **`"build": true`** — read `docx-rules.md` and follow it through structural (and, when
     `"visual_validation": true`, visual) validation before reporting completion. Give a source
     citation/locator and a `[verify]` or `[action: ...]` flag their own colored, italicized run per
     `docx-rules.md` → Editor notes, instead of leaving them as plain bracket text in the body font.
     Cite per `docx-rules.md` → Editor notes → Dual citation. When the draft writes its first
     citation and `5-System/user-preferences.md` has no `Referencing method` line, ask once and
     record the answer there (`docx-rules.md` → Editor notes → Referencing method).
   - **`"build": false`** — say plainly that Word output is unavailable here (Python or
     `python-docx` missing on this host), and offer the same content as Markdown instead. Do not
     attempt an unvalidated conversion.
3. **Format is Markdown or plain text:** ground every factual claim in the selected project or
   retrieved sources, and write it directly — no capability check needed.
   - When the request names a numbered section of a specialty/extension reference document (e.g.
     "Section 1"), do not treat the first file whose title matches as the whole section. Open that
     library's own `_index.md` router first — or dispatch the extension's dedicated lookup agent, if
     it has one — to confirm how many files the named section actually spans, then ground the draft
     in all of them.
4. Starting from an existing document is three different operations — decide which one was actually
   asked for; never default. `docx-rules.md` → Three ways to start lists them: `--from-template
   --mode shell` to reuse its look for a new report, `--from-template --mode extend` to build on top
   of it, or `--revise` to change specific content in place. All three follow `CORE-COPY-ON-EDIT`:
   the source is never edited, only read from — the result is always a new dated copy.
   - **`--revise` against a document that predates the editor-note convention:** `--revise` only
     reformats the paragraphs it touches, so an older document can come out half-converted — some
     citations and flags teal or amber, the rest still plain body text. Either bring the whole file
     up to the convention or say plainly in the completion report that only the touched passages
     carry note formatting; do not hand over a half-converted document as if it were finished. Run
     `--validate` (see `docx-rules.md` → Build and validation) before reporting completion — it
     checks this on every run.
5. Save under `2-Drafts/` with `draft_save.py next --ai` (`file-handling.md` → Saving under `2-Drafts/`); when revising,
   read the source from its `source now at:` line, because `next` may have moved it. Record the producing
   skill/version and exact model/effort in `_draft-index.md` per `file-handling.md` → AI runtime
   provenance, and report the path.
   If a brief was used, the report also names each section that maps to no key point and each key point
   with no section.
6. **A Word draft that leaves the project and carries citations:** before reporting completion,
   run the claims check and write the trace sidecar beside the draft, per `docx-rules.md` → Editor notes →
   Trace sidecar and Claims check. Report the grade counts and name every *unsupported* statement.

Never claim a `.docx` deliverable is complete from a successful file write alone when
`document-tools` was used — render and inspect it first.
