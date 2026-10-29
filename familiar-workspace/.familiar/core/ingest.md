# Source ingest

Ingest turns one user-approved project source into navigable project knowledge. It does not make an
external source authoritative merely because it was retrieved.

## Read mode or ingest mode

- **Read mode:** answer the immediate question from the source without creating project knowledge.
  It writes nothing, not even the source register; offer to record the file as `read` if the user
  wants the read to stay visible later.
- **Ingest mode:** create or update one knowledge page and its index entry.

Ingest is user-only: it runs only from its command, and the assistant never starts it from a
question about a source. A user who starts it wants ingest mode: do not ask whether the source is
worth keeping. Read mode is for a user who starts it but asks only what a source says. If neither
fits and writing would result, ask which mode they want.

## Size check

Synthesis quality and locator and marker carry-through fall as the context fills with earlier
sources, and reading extracts is most of an ingest's cost. So after step 2 has produced the
extracts (local, nothing read into context), and before step 3 reads any of them, check sizes with a
directory listing. If the request covers **two or more sources to synthesize** (new or incomplete,
per the step 1 receipt), or **any one extract over about 300 KB**, say so in one line and ask once:

> *N sources, ~X KB extracted (~Y k tokens; bytes ÷ 4). Results are most reliable with one source
> per fresh context. Go one at a time, or run them all now?*

Do not warn on a single source under the cutoff. If the user chooses one at a time, finish one
source through step 9, then name the next and suggest a fresh session (or `/clear`) and "ingest the
rest"; the source register resumes it. If the user chooses all, proceed without asking again. For
one oversized source, also offer `extract_pdf.py --pages` scoping before synthesizing the whole.

## Bulk ingest

When the user chooses all and this host's `named-subagents` state is `active`, give each source its
own fresh context by dispatching one worker per source, in waves. Otherwise use one at a time.

Ask once, in the same reply as the size check: *How many workers per wave, and should I pause for
your go-ahead between waves?* The host does not report how much of the user's usage window remains,
so the user sets the pace; never pick a wave size larger than the user's. Suggest 5 when they have
no preference. A wave never exceeds the host's own concurrency limit.

- **Before any dispatch:** run steps 1–2 for every source. Steps 1, 2 and 6–9 stay with this session.
- **Each wave:** first record every source in it as `partial` with `--note "bulk wave <N> dispatched"`,
  so a cutoff mid-wave leaves them `incomplete` on the next scan, not `new`. Each worker gets one
  extract and runs steps 3–5 only, with step 4's marker rule and step 5's `ref_count.py` stamp
  quoted in its prompt. It writes only its own page and returns the page path, a one-line summary,
  its track, and its source date. It never edits the index, register, abbreviations, or log.
- **After each wave, serially:** rerun `ref_count.py` on each page and redispatch any page whose
  `ref_carry_through` is missing or a placeholder. Then run steps 6, 7 and 9 for that wave, marking
  each source `ingested`, before starting the next. A cutoff loses only the wave in flight; "ingest
  the rest" resumes from the register.
- **Report:** say once that `ref_count.py` checks marker counts, not whether a page's figures match
  its source, and offer the check pass below.

## Check pass

A page's figures are checked against its own extract before a deliverable relies on them. Offer the
check after a bulk ingest, and before a deliverable that leaves the project cites pages that were
never checked. Run it only on the user's yes.

1. **Compare, do not rewrite.** One worker per page when `named-subagents` is `active` (in the
   user's wave size, as above), otherwise one page at a time. Each gets the page and its
   `_extract-<stable-source-ID>.md` and lists, per value or method statement on the page: confirmed,
   wrong (page says X, source says Y, with the locator), missing context (context the
   number-context rule in step 4 asks for, which the source states and the page dropped), no context
   applies (a number none of those kinds fits, which is not a fault), or cannot check (the
   value sits in a figure or table the text layer does not carry — a person checks the page image).
   A worker writes nothing.
2. **Report** the counts per page and every wrong value first, then the missing context. Values that
   need a page-image check are listed for the user and stay out of deliverables until a person has
   looked.
3. **Fix on the user's yes.** Apply the agreed corrections to each page, then stamp it in its front
   matter: `values_checked: YYYY-MM-DD (<N> values, <M> corrected, <K> left for a person)`, and set
   `last_verified` to the same date. Run `index_check.py --sync` once at the end.

## Ingest procedure

1. Run the ingest skill's `scripts/source_register.py scan` (the skill names the full path for this host) and show the user its receipt, which
   lists files that are new, unchanged, incomplete, renamed or copied, possibly revised, or missing.
   It writes nothing. Act on it before synthesizing:
   - **unchanged** or **renamed/copied:** the same bytes were already processed. Do not synthesize
     again unless the user asks. A copy is recorded as an alias in step 9.
   - **incomplete:** a partial or failed run. Resume it rather than starting a second page.
   - **possible revision:** confirm with the user that it is a new version of the same document.
     A byte difference alone does not prove a meaningful revision, and a newer file is not
     automatically the authority.
   Then identify the source, its owner or publisher, date/version, original location, stable
   source ID (the register's `Source ID` when it already has one), volatility, last verification
   date, and a review-by date for facts likely to change.
2. Use the active extraction capability for its format. The adapter owns tool and platform details.
   For a PDF this is the ingest skill's `scripts/extract_pdf.py` — write its markdown output to
   `3-Knowledge/_extract-<stable-source-ID>.md`, preserving the `<!-- PDF page N
   -->` locators it emits. This is the full-text cache `lookup`'s third routing tier reads; a format
   with no local extraction step (a source read directly, not converted) has no extract to write.
   The PDF cache header records the source fingerprint, page count, and per-page OCR mode. A later
   `--pages` refresh may merge only with a cache for that exact source; changed or legacy sources
   start a new cache. For a Word (`.docx`) source, also run
   the ingest skill's `scripts/extract_encite.py SOURCE -o 3-Knowledge/_extract-<stable-source-ID>-encite.json`.
   It reads the EndNote citation fields behind the source's numbered markers and records, per
   marker, the reference it points to (authors, year, title, journal, DOI). When it finds citation
   groups, use those records in step 4 to name the study behind each carried marker instead of
   inferring it from the rendered number. Report any `malformed` or `unsupported` count as an
   extraction limit. Zero fields means the source has no EndNote citations; carry its markers from
   the text as usual. If the script cannot run, say so once and carry markers from the text — never
   skip step 4 because the extractor was unavailable.
3. Preserve page, section, table, slide, sheet, or record locators where available.
4. Synthesize only what the source supports. Separate quotations, source claims, interpretation,
   uncertainty, and gaps. **Mandatory:** when the source attributes a claim to one of its own
   source-native citation markers — a numbered reference, footnote, or superscript (numeral or
   letter), or an inline citation such as `(Lee, 2025)` or `(Smith et al.)` — you MUST carry
   that marker with the claim exactly as the source expresses it, wherever it is legible (e.g.
   `[Smith 2023, p.4, ref 3]` for a numbered/superscript source, or `[Market Review v8.0, §4.2, citing
   Lee 2025]` for an inline-citation source). You MUST NOT launder an inline or lettered citation down
   to the container document's own name or version — the compiled report (or review, or briefing pack) is the vehicle,
   not the source of the underlying claim, and citing only the vehicle where the source itself named
   a more specific origin is a factual error in the page, not a stylistic simplification. Where OCR
   or extraction has made the marker ambiguous — mangled superscripts, unclear which of several
   references on a page it points to — mark it `[ref: ambiguous]` rather than guessing which one it
   is; never silently drop it instead. A source that cites its own claims, in whatever style, is
   expected to produce a page where most claims carry that marker — paraphrasing it away is a
   synthesis failure, not a stylistic choice, and it is the specific failure mode this rule exists to
   stop (a heavily cited source can yield a page where almost no claim kept its marker, found only
   later when a drafting skill goes looking for the primary sources and finds nothing to point to). **Before writing the page** — not after, not on a
   later pass — count claims tagged against claims that carried a source-native marker. If the
   carried share looks low against how densely the source itself cites (a handful carried out of
   dozens of claims from a heavily-cited source), you MUST go back and re-attach markers to the
   dropped claims. Do not write the page with a known shortfall and plan to note it afterward — fix
   it first; reporting is for what remains genuinely unresolvable (illegible or absent in the
   source), not for what was simply not carried through yet.
   **Every number carries the context that makes it mean something**, as far as the source states
   it, by kind of number: a rate, proportion or count — the population or subgroup, denominator or
   N, time frame, and how it was measured ("42% (n=118 of 281 surveyed mid-size
   firms, 2024 survey)", not "42%"); a cost or price — currency, price year, unit, list or net; a quantity or rate of use — unit and
   period; a model input or assumption — what it assumes and where it comes from. A number none of
   these fits (a date, a version, a page count) needs only its own unit. Never invent context the
   source does not state. When
   the source reports a combined group, the page says combined; never present it as one subgroup.
   A value the source takes from another study is attributed to that study ("churn 37% in the Lee 2024
   panel, as cited by Smith 2023 ref 12"), not to the source. A number with its context dropped is the
   error a later check most often finds, far more often than a wrong number.
5. Write one page under `3-Knowledge/` using `_page-template.md`. Before stamping `ref_carry_through`,
   run `python .familiar/scripts/ref_count.py 3-Knowledge/<page>.md` and stamp the counts it reports.
   It counts the claim tags and source-native markers actually on the page, which is what the stamp
   claims; a self-estimate is what let a 58-claim page carry 5 markers unnoticed. If it cannot run,
   count by hand and say the count is manual. Then continue, stamping
   `generated_by_model` with the model ID actually running this synthesis and `reasoning_effort`
   with its actual effort setting (from the environment/system context, never guessed), plus
   `generated_at` with today's date. Use `not exposed` for a runtime value the host does not provide.
   Restamp all three on any later resynthesis of the same page, even without a new source. For a
   source that cites its own claims in any style — numbered, superscript, or inline — you MUST also
   stamp `ref_carry_through` with the final claim count from step 4 (`<N> claims tagged, <M> carried
   a source-native marker`); use `n/a — source carries no citation markers of its own` when step 4
   doesn't apply. **A page is not complete without this field** — an ingest that skips it has not
   finished step 4, regardless of what the synthesis prose looks like. This makes a shortfall visible
   at ingest time instead of only when a later skill goes looking for the primary source behind a
   claim and finds nothing to point to. This step does not itself refuse to write the page over a low
   count — it is a completion requirement on the reporting, not a content gate — but Step 3 of the
   ingest skill MUST call out a low carried share to the user before the ingest is presented as done,
   the same way `[ref: ambiguous]` is already surfaced rather than silently accepted. The count's
   accuracy stays this step's responsibility whether or not any mechanical check is installed.
6. Add or update its single entry in `_knowledge-index.md`, then run
   `python .familiar/scripts/index_check.py` and fix any disagreement it reports for this page
   (it prints a ready row, summary aside, for a page with none). Date drift is mechanical:
   `index_check.py --sync` copies each page's `source_date`, `last_verified` and `review_by` into
   its row, so run it rather than retyping dates. If the script cannot run, check the row's dates,
   track, and supersession against the page by eye.
7. If the source uses an abbreviation not already listed in
   `3-Knowledge/_abbreviations.md`, add it there with its expansion and this
   source as first-seen. Do not duplicate an existing entry; if the same abbreviation expands
   differently in this source, add a second entry noting the conflict and both sources.
8. Record a material ingest event in the activity log only when it changes project understanding or
   state.
9. Record the outcome in the source register:
   the ingest skill's `scripts/source_register.py record <path> --status <ingested|partial|failed|skipped>
   --page <3-Knowledge/page.md> --id <Source ID> --role <role>`, adding `--supersedes <version>` for
   a confirmed revision. Record a partial or failed run too, with a `--note` saying what is left; an
   unrecorded failure is how the same work gets redone or silently lost.
   - **Roles** say how a file may be used; a file can carry more than one:
     - `source`: facts, instructions, or commitments that apply to this project.
     - `template`: a structure or required format to follow.
     - `example`: what a good finished output looks like. Its facts and commitments do not
       transfer, so another project's signed SOW is an `example`, not a `source`.
     - `admin`: governance or operational material.
   - The folder a file sits in is only a default for its role. If the script cannot run, say so
     and name the file and outcome in the ingest report, so the gap is visible.

## Meeting notes

A source under `1-Inputs/Sources/Meetings/` (or any meeting notes, minutes, or transcript) is ingested
as a record of one meeting, not as a document summary. The page leads with the date, attendees as
the source names them, and the matching `4-Trackers/meetings.md` ID when one exists (say so when
none does). Then it separates, each with locators where the source has them:

- **Decisions:** what was agreed, and by whom if the source says.
- **Actions:** the task, the owner as named, and the due date as stated. Do not invent an owner or
  a date the source does not give; mark it `unassigned` or `no date`.
- **Open questions:** raised and not resolved.
- **Discussion:** the rest, kept brief.

Ingest writes only the knowledge page. After the ingest report, offer to carry the actions into
`4-Trackers/tasks.md`, dates into `4-Trackers/timeline.md`, and any durable decision into
`5-System/Decisions/` through their normal routes; do not edit those files from the ingest. Transcripts
are lossy: attribute only what the transcript attributes, and report a speaker you cannot resolve.

## Source dates and conflicts

Record the date or version printed on the source, not the ingest date. Use `unknown` when the source
does not state one. When two sources disagree, the source date helps identify sequence but does not
decide authority by itself; preserve the conflict, provenance, and applicable owner or publisher.

`last_verified` records when the cited source was actually checked. `review_by` is required for
high-volatility external facts and may be `not scheduled` for stable internal records. A scheduled
freshness check reports overdue pages for review; it does not silently replace project knowledge.

## Privacy and failure

Do not send a confidential or restricted source to a remote parser unless the user has explicitly
approved that data path. When extraction is unavailable, unreadable, partial, or lossy, report the
limitation and do not fabricate missing text. Source binaries remain in their approved source
location; they are not copied into an extension package.
