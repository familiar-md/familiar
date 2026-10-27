# Presentation rules

## Template precedence

1. Use the template the user explicitly selects.
2. Otherwise use a project-specific template in `1-Inputs/Templates/` when project configuration
   designates one.
3. If no template is available or selected, ask the user to supply one, or to accept the builder's
   plain default master, named as such in the completion report. Never invent a brand master.
4. Never alter a supplied template source. Build a new presentation.

Project templates are for a client, project, or niche use case — assets the user has deliberately
placed in `1-Inputs/Templates/`. Do not inspect arbitrary company folders or search outside this
location.

If a template has no validated layout profile, profile it first: `build_pptx.py --profile-template
TPL.pptx` reports every layout's index, name, and placeholder shape. Use that to choose `layout`/
`title_layout` in the build spec — do not guess layout indices from visual similarity.

## Using the template

Inventory the selected template before you plan any slide:

1. Profile its layouts with `build_pptx.py --profile-template TPL.pptx`.
2. Render the template with `build_pptx.py --render TPL.pptx DIR` and look at every slide, including
   its guideline, palette and example slides. These show the brand's own visual vocabulary. If the
   guideline or palette pages are layouts rather than slides, build a scratch deck with one slide on
   each of those layouts and render that.
3. Write down the brand rules the template states: palette and chart colours, fonts and sizes,
   bullet style, punctuation, and the fixed elements (logo, slide number, confidentiality line,
   footer).

The brand rules bind every element on every slide, from a template layout or custom-built:

- Reference theme colours. Do not hard-code RGB values, except the editor-note colours below.
- Use the theme fonts and the template's own bullet style.
- Never move or cover a fixed element.
- If two brand chart colours are too close to tell apart in one chart, take the second series
  colour from elsewhere in the template palette, and name the choice in the completion report.

Template layouts are the default arrangement, not a requirement. Use a layout when it shows the
slide's message as well as a custom arrangement does. If a layout loses something the message
needs, such as colour assigned by role or a before-and-after shift, build that element as a custom
shape inside the brand rules. The order is: the slide's message, then the brand rules, then layout
reuse.

## Headline test

Every content slide has one headline: a full sentence that states the slide's point. It is the
title, or the line under the title when the title is a topic label such as "Issue 1: Unmet Need".

To run the test, read only the headlines, in order. Together they must state the deck's governing
thought (the one message the audience must accept or act on) and every key point that supports it. Name each slide whose headline does not, and say what it is missing.
This is the same test `/deliverable-brief` runs at its Outline stage.

## Visual design

A presented deck is visual by default. A read-ahead or leave-behind deck, which the audience reads
without a presenter, can carry denser text and tables. Confirm which one at `deck.md` step 1, or take
it from the brief's format.

For a presented deck, plan each slide in this order:

1. Write the headline sentence. It carries the slide's argument.
2. Choose the form that shows the evidence for it, from the table below.
3. Cut the text to fit the form. Move the detail to speaker notes.

| The slide shows | Use |
|---|---|
| One to four headline numbers | Stat tiles |
| Two or three positions side by side | Cards, with header colour assigned by role |
| A change from one state to another | A from-to strip with an arrow |
| A comparison of values | A native, editable chart |
| A sequence, a course of treatment, or a plan | A process bar or timeline |
| A specific request to the audience | An action bar |
| A key quotation | A quote panel |
| Many attributes across several options | A table, only when the reader must read across rows |

- Assign one colour to each role, such as "our position", "their position" and "the gap", and keep
  it the same across the deck. Colour carries meaning, not decoration.
- Write card and tile text as fragments: at most four bullets in a card, or one short sentence.
- Size each box to its content. Do not stretch a box to fill empty space.
- Keep every citation superscript and editor note with its text when that text moves into a visual
  or into the speaker notes.

## Content

- One purpose per slide.
- Put the conclusion or question in the title when the evidence supports it.
- Prefer a visual form over prose and over a table, per Visual design above.
- Keep source locators near claims that need verification.
- Separate confirmed fact, interpretation, recommendation, and open question.
- State every figure or claim's actual source — the client, a named report, a public filing —
  never an internal label. "Figures were familiar-derived" is not client language; write
  the real source, or mark it `[verify]` if there is none yet (`voice.md` → Uncertainty marker).
  Flag a task the drafter still owes — confirming a value, finalizing a set — with `[action: ...]`
  instead; it is an instruction, not an uncertain claim.
- List every abbreviation used on the slides on a glossary slide, expanded in full. Check each one
  against `3-Knowledge/_abbreviations.md` first; add a missing abbreviation there
  (`ingest.md` → Ingest procedure, step 7) before using it on a slide.
- Remove unused placeholders, speaker-note residue, and template sections (PowerPoint's
  Slides-pane section grouping) left over from a template build -- `build_pptx.py --build`
  does this automatically when it clears a template's slides; `--validate` flags any section,
  or any section entry, still pointing at a slide the build removed.

Common structures are starting points, not mandatory templates:

- project start: purpose, scope, roles, plan, milestones, risks, next actions;
- status update: progress, current state, decisions needed, risks, next actions;
- recommendation: question, evidence, options, tradeoffs, recommendation, implementation; and
- review: criteria, findings, severity, response, owners, dates.

## Editor notes

Same convention and the same colors as `docx-rules.md` → Editor notes, for a citation/locator or
a `[verify]`/`[action: ...]` flag on a slide: a bullet in SPEC.json can carry `"runs": [{"text":
"..."}, {"text": "[verify]", "note": "certainty"}]` instead of a plain string, colored and
italicized — `reference` (teal), `primary-reference` (purple, the source-native marker a
`reference` claim traces back to per ingest.md's `ref_carry_through`) or `certainty` (amber,
covering both `[verify]` and `[action: ...]`) — so the note reads the same way in a deck as in a
Word document. `docx-rules.md` → Editor notes → Dual citation governs when both `reference` and
`primary-reference` runs are required for one claim. An unrecognized note type is refused, and the
marker text itself never changes.

## Validation and delivery

Follow `deck-build.md`. A deck is complete when structural validation passes, every slide has been
rendered and looked at, every slide has been read once for internal-referencing language and
unexpanded abbreviations per the Content rules above, **and** the built deck has passed the Headline
test, or its failures are reported. The render that counts is PowerPoint's where PowerPoint is
installed (`office_render.ps1`); a LibreOffice render is a working view and is reported as
LibreOffice-only. With no renderer at all, deliver only with that limitation stated plainly in the
completion report.

A deck that leaves the project and states numbers, quotes or what a source says gets the same trace
sidecar and claims check as a Word draft (`docx-rules.md` → Editor notes → Trace sidecar and Claims
check), with the slide number in the Section column. It is the answer to "where does this number
come from?" before anyone has to ask. It also gets the stranger read in `docx-rules.md` → Build and
validation, step 8, with the slides read in order. Save a new dated version in `2-Drafts/`, include
skill/date/version provenance, and never publish or send it without user approval.
