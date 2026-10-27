# plain-language — Writing Shape and Sentence Rules

> Load when producing or editing anything longer than a chat reply. `voice.md` carries the voice, the
> avoid-list, and the pre-delivery check, and governs a chat reply on its own. This file picks the
> shape the writing takes and the rules its sentences follow.
>
> Adapted from **ASD-STE100 Simplified Technical English** (Issue 9, 2025) via
> [SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) (MIT). Rule numbers below are that
> standard's. The official dictionary is copyrighted and is not reproduced here; the structural rules
> work without it. Free download: asd-ste100.org.

## Pick the shape first

Classify by content type, not by audience. A deck stays bullet-driven when it is externally facing;
a report stays full prose when it is purely internal. The row you pick decides which rules bind.

| What you are writing | Shape | Sentence rules |
|---|---|---|
| **Operational** — status-log entries, the snapshot, handoffs, task and decision records, memory files, and any flag, warning or blocker raised in chat | Imperative mood. One instruction per sentence (5.2). Condition before the command. | **Full**, at a **20-word** limit (5.1). This is what STE was built for and the strongest case for it. |
| **Full-prose deliverable** — reports, memos, submission and comment-round text, externally facing drafts that are not decks | Full paragraphs, formal and neutral. No bullet-scaffolded reasoning inside the deliverable itself; a bullet-headed "what we found / why it matters" reads as an internal working note. Headings and tables stay fine where the source format calls for them. | **Structural only**, at a **25-word** limit (6.3): tenses, active voice, one word per meaning. Do **not** apply the imperative mood and do not strip subordination. |
| **Deck** — internal or externally facing | Bullets and fragments, per `deck-rules.md`'s bullet discipline and speaker-notes rules. Formality scales with audience; the bullets-not-paragraphs choice does not. | Sentence limits and vocabulary discipline only. One instruction per sentence does not bind a bullet. |
| **Chat reply** | Concise. Bullets where they make retrieval easier. | **None.** `voice.md` governs chat on its own — a 20-word limit makes conversation stilted rather than clear, and the user can ask again. |
| **Persuasive or relationship text** — a rationale arguing a position, a note managing a stakeholder expectation | Prose. | **Do not apply.** STE deletes persuasion by design. Say so if asked to apply it here. |

Switch to a deliverable shape only while producing or editing one, then switch back. Use the
operational shape whenever what you write will be acted on rather than read — including inside a file
that is otherwise concise, so a `tasks.md` entry takes the operational shape. A note inside a
procedure is descriptive: 25 words, no imperative, information only (5.5). One topic per paragraph
(6.5), six sentences at most (6.6).

**Domain vocabulary is always legal** (Rules 1.5, 1.8, 1.12). "Net present value",
"materiality threshold", "service-level agreement", "root-cause analysis" are technical nouns. Never
simplify a term whose precision is the point.

## The rules

**Verbs (Section 3).** Use only the infinitive, imperative, simple present, simple past, simple
future, and the past participle as an adjective ("the cached response"). No present perfect — "has
completed" becomes "completed". No `-ing` form as a verb — ", making it easier to…" becomes a new
sentence. Active voice; passive only in descriptive text when the actor is genuinely unknown.
Describe an action with a verb, not a noun: "compress the file", never "perform compression of the
file" (3.7).

**Modals — factual meaning outranks the style rule.** A modal verb carries one of several distinct
meanings — requirement, recommendation, permission, possibility, prediction, or an author's own
observation — and STE's plain-vocabulary goal is never a license to collapse them into each other.
Converting a source's hedge ("the pilot data **may** indicate a cost benefit") into a flat
assertion ("the pilot data **can** indicate a cost benefit") is not simplification; it is a
factual distortion, and it directly conflicts with `voice.md`'s instruction to preserve uncertainty
when the evidence is uncertain. Keep the six meanings distinct in every shape; only the *phrasing*
changes, never the *force*:

| Meaning | Example | Plain phrasing that keeps the meaning |
|---|---|---|
| Requirement (mandatory) | "the applicant must file by X" | **must** |
| Permission / capability | "the reviewer can request more data" | **can** |
| Possibility (evidentiary hedge) | "the data may indicate an effect" | Keep the hedge: "may indicate", "it is possible that", "one plausible reading is" — never flatten to "can" or "does" |
| Prediction (stated but unconfirmed) | "this would reduce churn if replicated" | Keep the conditional structure: "if X occurs, Y is predicted to occur" — do not state the predicted outcome as settled |
| Recommendation (a judgement call, not a rule) | "the committee should consider X" | Attribute it and keep it a recommendation: "the committee recommends X" or "X is advisable because Y" — never silently promote it to a requirement by writing "must" |
| Author's own observation, stated as fact | "the effect was observed in 80% of respondents" | State it plainly; no modal needed |

**In operational writing only** (the shape defined above — status-log entries, snapshots, handoffs,
task/decision records, and familiar's own instruction files) — where the sentence gives or follows an
instruction rather than reporting a fact — the ambiguity itself is the hazard, so collapse to the
approved set: **can, will, must**; avoid should/would/may/might/could there specifically because
**a model reads "should" as optional**, which is a fair description of why a correct rule in
`deck-rules.md` failed to stop `draft-document` → Deck doing the wrong thing on 2026-08-01. That
collapse is safe in operational text because the sentence states what familiar itself must or may do,
not what a source claims — there is no evidentiary hedge to lose.

In every other shape — full-prose deliverables, decks, anything reporting what a source, a study, or
a stakeholder said — keep the six meanings distinct per the table above. A quotation's own modal verb
is never altered at all; this section governs familiar's own prose describing or summarizing a
source, not a verbatim quote (see Never touch, below).

**Sentences (Sections 4, 5, 8).** Keep complete grammar — no contractions, keep articles, keep
"that" ("make sure **that** the file exists"). STE is short sentences, not telegraph style; "Ensure
file exists before running" is wrong in both directions. Put the condition **before** the command,
with a comma: "If the variance exceeds the threshold, flag it in the snapshot." No semicolons — write two
sentences. Use a vertical list for more than two items or steps. Numbers with units, quoted text,
identifiers, file paths and parenthetical text each count as **one word** toward the limits (8.5,
8.6), so `2026-04 Procedures for Annual Compliance Reviews` does not blow a sentence budget.

**Words (Sections 1, 2, 9).** One item, one name, for the whole document (1.11, 9.4). Collapse these
rotations to one term each before you draft:

- check / verify / confirm / validate / ensure
- config / configuration / settings / options
- run / execute / invoke / launch
- show / display / present
- error (an error) / failure (a failed operation) — one per meaning, kept consistent

Multi-word nouns of three words or fewer (2.1); break longer chains with a preposition — "the
connection pool timeout configuration value" becomes "the timeout value for the connection pool". No
phrasal verbs (9.3): "set up" becomes "install" or "configure". "e.g." becomes "for example", "i.e."
becomes "that is", and "etc." is deleted — name the items.

**Warnings (Section 7).** Command or condition first, risk second. Never bury the instruction behind
the explanation. "Do not run the migration against production. The command deletes rows that do not
match the source." — not the reverse.

**Never touch** (1.5, 8.6): code, identifiers, CLI commands, file paths, quoted error messages,
product and agency names, and any verbatim quotation from a source. A quotation is evidence; editing
it for style destroys it.

## Filler to delete

`voice.md`'s banned list covers the AI-writing tells. These are the additional ones STE removes.
If the word carries no fact, **delete it rather than replacing it**.

| Filler | Write instead |
|---|---|
| leverage, utilize | use |
| in order to | to |
| prior to | before |
| ensure | make sure that |
| in the event that | if |
| due to the fact that | because |
| enables you to, allows you to | you can |
| is designed to, aims to | (delete — say what it does) |
| functionality | function, feature |
| as needed, as appropriate | (state the condition) |
| and/or | pick one, or write "X, or Y, or both" |
| robust, comprehensive, powerful | (delete, or give the measurable property) |
| simply, just, easily, seamlessly | (delete) |

## Self-check before delivery

Run with `voice.md`'s pre-delivery check, not instead of it. Four passes:

1. Count the words in your three longest sentences. Over 20 (operational) or 25 (descriptive) → split.
   These limits are defaults, not a ceiling that outranks the requested artifact — a mandated
   template or citation format that needs a longer sentence wins; say so rather than mangling it.
2. Search the draft for `'s`/`'re`/`'ll` contractions, `has been`, `have been`, an `-ing` verb after
   a comma, and semicolons. In operational text only, also flag `should`, `may`, and `might` — outside
   it, check instead that every modal still carries the meaning (requirement, permission, possibility,
   prediction, recommendation, observation) the source or the judgement actually intended, per the
   Modals table above.
3. Search every `if` and `when`. Each one starts its sentence, before the command.
4. Search for the synonyms you did **not** pick from the rotation list. Replace every hit.

## Limits, stated honestly

This is an unofficial adaptation. Nothing certifies STE compliance — ASD certifies no tool. Full
vocabulary compliance needs the official dictionary. What is enforceable here is the structural half,
which is where nearly all of the benefit sits.
