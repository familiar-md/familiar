# `/draft-document` → Deck

> Branch of the `draft-document` router. Reached only from `/draft-document`; the user
> starts it, never a route match. Load this file after the branch is selected, then follow the
> context contract below and load nothing from the other branch.

## Context contract

- **Required context:** `.familiar/core/deck-rules.md`, `.familiar/core/deck-build.md`, `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, project configuration, the selected template, and the project sources explicitly required by the presentation.
- **Conditional context:** the deliverable's `2-Drafts/<slug>/_brief.md` only when it exists, with every file its `Standards` line names, and the `authority` file or template its profile names only when the brief is locked; `.familiar/core/docx-rules.md` → Editor notes only when the deck leaves the project and cites sources (its Trace sidecar and Claims check); project status and timeline only for status work; extension style or content contributions only when their route is selected.
- **Excluded context:** Other projects, unselected templates, unrelated project history, and undeclared extension content.
- **Updates:** one new version under `2-Drafts/` (saved with `.familiar/scripts/draft_save.py --ai`), its build script under `2-Drafts/<slug>/_build/` when one was used, and its `_trace.md` sidecar when the claims check runs; project state only when the user separately confirms a material change.
- **Capabilities:** file-read, file-write, and `document-tools`; `available` does not mean working — confirm live with `scripts/build_pptx.py`'s health check before relying on it.
- **Completion:** The new presentation version passes structural validation, plus full visual validation when a renderer was available; or the missing capability is explicitly reported before an invalid artifact is produced. If visual validation was not possible on this host, say so in the completion report rather than implying it happened.

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
1. Confirm purpose, audience, output status, template, and whether the deck is presented or read
   without a presenter (`deck-rules.md` → Visual design). If the request doesn't make the audience
   obvious, ask — see `voice.md` → Audience for what an external reader changes about body prose.
2. Inventory the template per `deck-rules.md` → Using the template. Then read the rest of
   `deck-rules.md` and draft the slide-level argument before building: one headline per slide. With
   a locked brief, its headlines are the slide headlines. Without one, run `deck-rules.md` →
   Headline test on your draft headlines and show them to the user before building. For a
   presented deck, choose each slide's form per `deck-rules.md` → Visual design.
3. Ground every factual claim in the selected project or retrieved sources. Give a source
   citation/locator and a `[verify]` flag their own colored run per `deck-rules.md` → Editor
   notes, instead of leaving them as plain bracket text in the bullet's own color.
4. Follow `deck-build.md` through structural validation and complete visual inspection, using
   `scripts/build_pptx.py`.
5. Read every slide once against `deck-rules.md` → Content: no internal-referencing language
   (`voice.md` → Avoid), and every abbreviation used expanded on a glossary slide and present in
   `3-Knowledge/_abbreviations.md`. Then run `deck-rules.md` → Headline test on the built deck:
   building can shorten or move a headline, so a brief that passed does not prove the deck does.
6. Save the new version under `2-Drafts/` with `draft_save.py next --ai` (`file-handling.md` → Saving under `2-Drafts/`); record the producing skill/version and exact model/effort
   in `_draft-index.md` per `file-handling.md` → AI runtime provenance, and report its path. Keep the
   runtime metadata out of visible slides unless the user asks for it there.
   The report gives the headline test result and names each failing slide, and says which render
   was used (PowerPoint, LibreOffice-only, or none). If a brief was used, the report also names each
   slide that maps to no key point and each key point with no slide.
7. **A deck that leaves the project and states numbers, quotes or what a source says:** write its
   trace sidecar and run the claims check (`deck-rules.md` → Validation and delivery), and report the
   grade counts and every *unsupported* statement.

Never modify a template or an existing presentation in place. Never claim completion from a
successful package write without rendering and inspection.
