# handoff-format — In-Flight Session Handoffs

> Format and discipline for `5-System/Handoffs/`. Written and read only
> when `/handoff` → Session handoff runs — user-started only; familiar identifies the fit
> and tells the user the command, never opens it itself. Rules and voice: `bootstrap.md`. Project
> *state* is `status-format.md` — this file is for work in flight, not for state.

## What a handoff is for

The half-finished thing. A draft report three sections into markup, a deck stopped at slide six, a
comment-round argument mid-construction. Project state — dates, decisions, risks, open actions —
already survives in `Memory/`, `4-Trackers/timeline.md`, and `4-Trackers/tasks.md`, and is read through
whichever route needs it, not automatically at session start. **Never duplicate those here.** If a
fact belongs in memory, file it there and let the handoff point at it.

## One file per thread

`Handoffs/YYYY-MM-DD_<short-slug>.md`. Several may be open at once — a user runs more than one thread,
and overwriting a shared file would destroy a live handoff on another. Never overwrite an existing
handoff to start a new one.

A handoff carries one *thread* — a single piece of half-finished work. A **track**
(`/system-settings` → Tracks → Format and tagging discipline) is a whole line of work and can hold several threads over its life.
The `Track:` line says which one this thread sits in.

`CORE-PROGRESSIVE-DISCLOSURE` means handoffs are never scanned before routing — several threads may be
open, and a recent handoff is not automatically the relevant one. Once a status, continuation, or
handoff route is selected, list the `open` handoffs by their `Covers:` lines and let the user choose.
`Covers:` is therefore the one line most likely to be read once that list is shown: write it so the
user can tell at a glance whether this is the thread they want.

## Status — the four values

`open` · `resumed YYYY-MM-DD` · `superseded YYYY-MM-DD by <path>` · `closed YYYY-MM-DD`

Only `open` appears in that route-selected list, so a handoff left `open` after the work is finished or
abandoned keeps appearing there and teaches the user to ignore it. **A handoff is never
deleted** (`CORE-NO-DELETE`) — it is moved to a terminal status instead:

- **`closed`** — the work in the thread is finished, or the user has abandoned it. Add one line saying
  which.
- **`superseded`** — a later handoff, decision or plan replaced this thread. Name the replacement by
  path; a bare `superseded` tells a future reader nothing.

Set a terminal status only when the user says the thread is over. Ask; never infer it from the
handoff's age. One exception needs no extra question: writing a new handoff that carries a resumed
thread forward marks the resumed one `superseded` by the new path, because the user's request for the
new handoff already says the old one is replaced. That keeps a chain of handoffs to one open file.

The agent that resumed a handoff and finished its `Next concrete step` may ask to close it and, on the
user's yes, write `closed` itself from any skill; see `/handoff` → Session handoff → Closing one.

## Template

```markdown
<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: YYYY-MM-DD -->
# Handoff — <thread name>

**Covers:** <the thread, in plain words — enough to know at a glance whether this is the one>
**Track:** <code from `project-config.md`, or `shared`. Omit the line if no tracks are declared.>
**Status:** open
**Written:** YYYY-MM-DD

## Where I stopped
<the last thing actually completed, and the exact point of interruption — file, section, slide>

## Next concrete step
<what the next session does first. One action, not a plan.>

## Do not redo
<work already done that a fresh session would waste time repeating or second-guessing>

## Decided along the way
<choices made in this session that constrain the next. If any is material, it belongs in
`status-log.md` (or a decision record) as well — file it there and link, don't hold it only here.>

## Open questions
<what is genuinely unresolved, and who can resolve it>

## Artifacts
<paths to the files being worked on. Pointers, not restatements.>
```

## Writing one

1. **Point, don't restate.** Reference paths, sections, and log entries. A handoff that reproduces
   the draft is worse than the draft.
2. **Be concrete about the next step.** "Continue the review" is useless; "resume markup at section
   4.2, cost analysis" is the point of the file.
3. **File the durable parts properly first.** A decision, date change, or new action found in this
   session goes to its normal surface per `/save to-memory` — the handoff carries only what has no
   other home.
4. Confirm to the user where it was written.

## Reading one back

1. List the `open` handoffs with their `Covers:` lines and let the user choose. Never assume the most
   recent is the right one.
2. Load memory as normal first (`status-format.md` read order) — the handoff supplements project
   state, it does not replace it.
3. Set `Status: resumed YYYY-MM-DD` on the one picked up. Never delete it (`CORE-NO-DELETE`).
4. If its `Next concrete step` conflicts with what the snapshot now says, **say so and stop**. The
   handoff is older than memory; the user decides which is right.
5. When the user confirms a thread is over, set `closed` or `superseded` per Status above, so it
   leaves the open-handoffs list.
