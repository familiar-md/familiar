# Knowledge

Compiled, durable understanding of **this project's own sources** — what familiar has learned, kept so
it doesn't re-read everything from scratch each time. familiar writes and maintains this folder; the
user reads it.

- One **page per source** you ingest (report, prior review, transcript, scope record), named
  for the source — e.g. `2024_Smith-Report.md`. Pages are updated in place as understanding grows.
- `_knowledge-index.md` — the catalog: every page with a one-line summary and link, plus the
  **source date** (the date on the document, not on the ingest) and which pages supersede which.
  familiar reads this first to find the right page. Because pages are shaped by source and not by
  subject, two sources on one subject can disagree — those two columns are how the disagreement
  stays visible instead of the newest ingest quietly winning.
- `_page-template.md` — the format familiar follows for each page.
- `_source-register.md` — every input file and what ingest did with it: ingested, read, partial,
  failed, skipped, or superseded, with its roles (source, template, example, admin). Ingest shows
  a receipt from it before starting, so a renamed copy is not processed twice and a half-finished
  ingest resumes instead of restarting.
- `_extract-<stable-source-ID>.md` files — full machine-converted PDF->markdown text cache, one per
  ingested source that went through local extraction, written once per source during ingest and
  living directly in this folder (no subfolder) with the `_extract-` prefix. Consulted only as the
  retrieval fallback tier, after `_knowledge-index.md` and the source's own synthesis page fail to
  cover a question — grepped, never read whole. Carries OCR/charmap risk that the synthesis page
  does not.

Raw source files stay in `1-Inputs/Sources/` (read-only). This folder holds the
*installed* version. How ingest works, and the citation/locator rules: `.familiar/core/ingest.md` at the project root.

If pages accumulate to where this folder is hard to navigate, run `/system-settings` and pick Workspace tidy — it
can propose a grouping scheme and will update `_knowledge-index.md` to match, but only on your
approval.
