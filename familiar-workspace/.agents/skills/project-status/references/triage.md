# `/project-status` → Triage

> Branch of the `project-status` router. Reached only from `/project-status`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

A **stateless query**, read-only like Where are we — it never edits a tracker. Answers one
question: *of what is actually workable right now, what should I run given the constraint I am
under* — a big budget window with no time pressure, or the reverse.

## Context contract

- **Required context:** `4-Trackers/tasks.md` + `4-Trackers/timeline.md`
- **Conditional context:** `5-System/Memory/status-snapshot.md` only when the project tracker does not exist yet.
- **Excluded context:** `Knowledge`, `Inputs`, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** `nothing`. The sort is delivered in chat; re-ordering a tracker belongs to other skills
- **Capabilities:** file-read. Optional capabilities must degrade as the procedure states.
- **Completion:** Every frontier item appears once with both axes visible, excluded and unreadable items are counted or identified, and no tracker is changed.


## Calibration

Work shape: **bounded transactional** — reading and classifying state that already exists, not
generating a recommendation. On missing or unreadable state familiar says so rather than guessing at
what is open.

## Step 1 — Ask the perspective, unless given

If the user invoked this with a stated perspective, skip the question.

- **Token-heavy** — "I have budget headroom right now (or am about to lose it) — what's the biggest
  task I could run?"
- **Time-sensitive** — "What's actually about to slip?"

## Step 2 — Read state

`4-Trackers/tasks.md` (`## Open`), `4-Trackers/timeline.md` (milestone dates, `Depends on`). Read
`5-System/Memory/status-snapshot.md` only if `tasks.md` does not exist yet.

**Frontier only.** Run `python .familiar/scripts/task_frontier.py`, which applies the blocker rule
below mechanically and lists the frontier and what blocks everything else; if it cannot run, say so
and apply the rule by reading `tasks.md`. A task blocked by an open item or an external dependency cannot be started today
regardless of its effort or urgency — exclude it from triage, same frontier definition as
Where are we. Count excluded blocked items and report the count once; do not list them
individually unless the user asks.

## Step 3 — Classify every frontier item on both dimensions

Classify every item on **both** axes regardless of which perspective was asked for — the perspective
picks sort order, not what gets shown. An item that looks light under one lens and urgent under the
other is exactly the case the user needs to see, not one axis hiding the other.

**Effort — light / moderate / heavy.** Judge from what the task actually requires, not its one-line
label: a single edit or confirmation is light; a bounded build with a few sources is moderate; a
multi-source synthesis, a full document build, or anything that would dispatch several agents
(deck, vendor review, draft-report markup, a financial model pass) is heavy.

**Urgency — due-soon / normal / unscheduled.** Due-soon: an explicit due date in `tasks.md` within
the user's stated or default horizon (7 days), or a `timeline.md` milestone it feeds with no slack
before that date. Normal: a due date beyond the horizon. **Unscheduled: no due date and no milestone
link — state this plainly rather than guessing at urgency from the item's wording.**

**Confidence.** High — an explicit due date or an unambiguous heavy-effort task type: classify and
move on. Medium — effort or urgency depends on scope not stated in the task line: classify, but say
what assumption was made. Low — the task line gives neither a date nor enough detail to judge effort:
mark that axis unscheduled / effort unclear rather than assigning a tier.

## Step 4 — Report, sorted by the chosen perspective

Present every frontier item once, both axes visible, sorted by the perspective's primary axis
(heaviest-first for token-heavy, most-urgent-first for time-sensitive) with the other axis as a
visible tag — never drop it.

```
[heavy | due-soon] Draft submission section 4 — due 2026-08-22
[heavy | unscheduled] Build the base-case model
[light | due-soon] Confirm input list with stakeholder — due 2026-08-19
```

Close with the count of excluded blocked items and — for the token-heavy perspective specifically —
a flag on any `heavy | due-soon` item: that is the one case where running the big task now is not
actually optional. Frame it as a flag, not a pick; the user decides what to run.

## Guardrails

- Never edits `tasks.md`, `timeline.md`, or the snapshot — read and report only.
- Never opens a project's `Knowledge` or `Inputs` — status fields only.
- Never infers urgency from an item's wording when no date exists. Unscheduled stays unscheduled.
- Never silently drops the non-primary axis to keep the list short.
