# Presentation build procedure

`document-tools` is `available`, not `active`, for `deck`: whether it actually works depends on
this host having Python plus `python-pptx` installed, and optionally a LibreOffice `soffice`
binary for visual rendering. Confirm both before building — never assume from a matrix entry
alone.

1. Confirm the output purpose, audience, and template precedence from `deck-rules.md`.
2. Run the `draft-document` skill's `scripts/build_pptx.py` with `--health-check`.
   - `"build": false` — report `document-tools` unavailable (Python or `python-pptx` missing on
     this host) and stop. Do not fall back to an untested converter.
   - `"build": true, "visual_validation": false` — building and structural validation can
     proceed, but no renderer (`soffice`/LibreOffice) or `pymupdf` was found. State this
     limitation plainly before delivering: the result has not been visually inspected.
3. Inspect the selected template without modifying it: `build_pptx.py --profile-template TPL.pptx`
   reports its layouts and placeholders — use that to set `layout`/`title_layout` in the spec
   rather than guessing indices. Render it as well, per `deck-rules.md` → Using the template.
4. Build a new version: `build_pptx.py --build SPEC.json OUT.pptx --template TPL.pptx` when a
   template was selected (per `deck-rules.md` → Template precedence), or without `--template` only
   when the user accepted the plain default master. `OUT.pptx` is the path `draft_save.py next`
   printed. Template mode keeps the master, theme,
   dimensions, and layouts, but removes the template's existing slides; use it for a new deck, not
   to extend another project's content.
   SPEC.json expresses titles, bullet text and editor-note runs only. When the slide plan needs
   cards, tiles, charts, tables or other shapes (`deck-rules.md` → Visual design), add them with a
   python-pptx script that edits the spec-built output, never the template or a saved version. Save
   the script and its spec beside the deliverable, at `2-Drafts/<slug>/_build/` (`file-handling.md`
   → Boundaries), and name them in the completion report, so the next revision starts from the
   script rather than from the saved `.pptx`.
5. Validate structure: `build_pptx.py --validate OUT.pptx` — add `--template TPL.pptx` when one was
   used, which also checks the build kept its slide dimensions. Its overflow/density findings are
   heuristics (characters per line, lines per text block), not a substitute for visual inspection —
   treat every finding as something to fix, not something to explain away.
6. Render and inspect every slide. Where PowerPoint is installed, the final render is PowerPoint's:
   run the `draft-document` skill's `scripts/office_render.ps1 -Path OUT.pptx -OutDir .scratch/render`
   through `powershell -NoProfile -ExecutionPolicy Bypass -File` (one PNG per slide plus a PDF;
   `"opened": false` means PowerPoint refused the file, which is a defect). Otherwise, if `visual_validation` was true in step
   2, `build_pptx.py --render OUT.pptx OUT_DIR`, labelled LibreOffice-only. Look at each PNG for
   clipping, text overflowing its box or another, unreadable density, missing fonts, accidental
   placeholders, contrast, and visual hierarchy.
7. Correct the smallest failing surface and repeat validation (and rendering, if available).
8. Register the validated result with `draft_save.py register` and the required provenance, and
   state in the completion report which render was used (PowerPoint, LibreOffice-only, or none).
   For a deck that leaves the project and cites sources, write its trace sidecar and run the claims
   check (`deck-rules.md` → Validation and delivery).
