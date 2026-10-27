# _page-template — Knowledge Page Format

> Copy this structure for each new by-source page. Filename encodes the source, e.g.
> `2024_Smith-Report.md`. Update the page in place as understanding grows (it's internal living
> content, not a deliverable). Rules: `.familiar/core/ingest.md` at the project root.

```markdown
---
source: <exact source filename in 1-Inputs/Sources>
source_id: <the source's `Source ID` in `3-Knowledge/_source-register.md`>
source_title: <human title>
type: <technical report | published article | internal/confidential report | prior specialist review |
  transcript | scope record | other>
source_date: <the date on the DOCUMENT — when it was written or published; "unknown" if it carries
  none. Never today's date. This is the field the recency check reads (ingest.md).>
version: <the document's own version/edition label, e.g. "v1.2" (as in "Market Review v1.2, Oct 2025") — for
  versioned internal/confidential reports. Omit where the source carries none. The recency check
  (ingest.md) reads this as a tiebreaker when source_date is equal or unknown on both sides.>
authors: <first author et al. — published articles only. Omit otherwise.>
journal: <journal name — published articles only. Omit otherwise.>
volume_issue: <e.g. "42(3)" — published articles only. Omit otherwise.>
doi: <DOI — published articles only. Omit otherwise.>
date_ingested: YYYY-MM-DD
last_verified: YYYY-MM-DD
values_checked: <set by ingest.md → Check pass: "YYYY-MM-DD (<N> values, <M> corrected, <K> left for a
  person)", or "not yet">
review_by: <YYYY-MM-DD for volatile facts, or "not scheduled">
volatility: <low | medium | high — how quickly external facts in this source can change>
track: <code from project-config.md, or shared; omit where the project declares no tracks>
supersedes: <page this one replaces, or "none">
superseded_by: <page that replaces this one, or "none">
generated_by: <the fully qualified skill that wrote this page, e.g. extension-id:skill-id>
skill_version: <the familiar version that skill shipped in, from .familiar/installed.json>
generated_by_model: <the model ID that actually wrote this page's synthesis, e.g. claude-sonnet-5 —
  read from the environment/system context at write time, never guessed or left stale from a
  template copy>
reasoning_effort: <the exact runtime effort setting, e.g. medium; use "not exposed" when the host
  does not provide it, never infer it>
contributors: <optional list of {role, model, reasoning_effort} for independent model workers whose
  judgment materially shaped this page; omit for retrieval-only workers or when none were used>
generated_at: <YYYY-MM-DD, the date this page's content was last (re)synthesized by a model — distinct
  from date_ingested's source-intake date if the page is later regenerated without a new source>
ref_carry_through: <"<N> claims tagged, <M> carried a source-native marker" for a source that cites
  its own claims in any style — numbered reference, footnote, superscript, or inline (Author, Year)
  citation (ingest.md step 4) — or "n/a — source carries no citation markers of its own" otherwise>
tags: [<topic>, <topic>]
---

# <Source title>

## Summary
<2–4 sentences: what this source is and why it matters to the project.>

## Key findings
- <finding> [<source>, p.<n>, <table/section>]
- <finding> [<source>, p.<n> [PDF p.<m>]]
- <finding attributed to a source-native numbered reference> [<source>, p.<n>, ref <k>]
- <finding attributed to a source-native inline citation> [<source>, p.<n>, citing <Author Year>]
- <finding whose source-native citation marker is illegible or ambiguous> [<source>, p.<n>, ref: ambiguous]

## Relevance to this project
<how it bears on deliverables, decisions, risks.>

## Related pages
- `<other page filename>.md` — <why it relates>

## Open questions / contradictions
- <anything unresolved, or where this source conflicts with another page>
```
