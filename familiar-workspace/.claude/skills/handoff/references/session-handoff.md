# `/handoff` → Session handoff

> Branch of the `handoff` router. Reached only from `/handoff`; the user starts it, never
> a route match. Load this file after the branch is selected, then follow the context contract
> below and load nothing from the other branch.

Carry half-finished work across a session boundary. **Format and templates:
`.familiar/core/handoff-format.md` — read it before writing or reading a handoff.**

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, `5-System/Memory/` in normal read order, `4-Trackers/tasks.md` + `timeline.md`, and an existing handoff when resuming
- **Conditional context:** the selected existing handoff only when resuming or closing it, and related authoritative state only for reconciliation.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** one `5-System/Handoffs/YYYY-MM-DD_<slug>.md`, or a `**Status:**` change on an existing one
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** In-flight state is filed in a new handoff or an explicitly selected handoff is read back and marked consistently.


Project state is not this. Dates, decisions, risks, and open actions live in `5-System/Memory/`,
`4-Trackers/timeline.md`, and `4-Trackers/tasks.md`; routes load them when required. A handoff carries
only what has no other home: a draft partway through markup or a deck stopped at slide six.

## Two modes — ask which if it is not obvious

A trailing instruction that names a new task rather than a handoff action ("extract these files into
the tracker") is neither mode by itself. Treat it as a candidate match for **Reading back** and run
that mode's steps in order — a text match against a `Covers:` line, even an exact-looking one, is not
user confirmation.

### Writing

0. **Is a handoff the right tool?** A handoff is for stopping: a later day, another person's
   session, or a context that is genuinely full. If the user only wants the next step done now and it
   is self-contained, and this host's `named-subagents` is `active`, offer once to run it as a worker
   and report back here instead. Write the handoff if the user still wants it.
1. File the durable parts first. Any decision, date change, or new action from this session goes to
   its normal surface per `/save to-memory`. Only what is left over belongs in the handoff.
2. Write `5-System/Handoffs/YYYY-MM-DD_<short-slug>.md` using the template in `handoff-format.md` → Template. **Never
   overwrite an existing handoff** — another thread may still be live in it.
3. Fill `Covers:` so the thread is identifiable at a glance, and `Status: open`. Where
   `5-System/project-config.md` declares tracks, fill `Track:` with a code from that table, or `shared`.
4. **Collapse the chain.** If this session resumed a handoff (`Status: resumed`) and the new one carries
   the same thread forward, set the resumed one to `Status: superseded YYYY-MM-DD by <new path>` in the
   same step. The user's request for a new handoff on that thread is the confirmation; a resumed
   handoff on a different thread stays untouched.
5. Tell the user the path, and name the handoff it superseded, if any.

### Reading back

1. List the `open` handoffs with their `Covers:` lines. **Let the user choose** — the most recent is
   not necessarily the relevant one, and a single apparent match still needs the user's yes before
   step 3.
2. Load memory in the normal read order (`status-format.md` → Read order & update protocol) first. The handoff supplements project
   state; it never replaces it.
3. Mark the chosen one `Status: resumed YYYY-MM-DD` only after the user confirms the match.
4. If its `Next concrete step` contradicts the current snapshot, **say so and stop.** The handoff is
   older than memory — the user decides which is right.

### Closing one

Ask before setting a terminal status; never infer one from a handoff's age. When the user confirms the
thread is over, set `Status: closed YYYY-MM-DD` (work finished or abandoned) or
`Status: superseded YYYY-MM-DD by <path>` (a later handoff or decision replaced it). Only `open`
handoffs are listed by their `Covers:` line once a status, continuation, or handoff route is
selected, so this is what stops a dead thread surfacing in that list forever.

**Finishing a resumed thread from any skill.** When this session resumed the handoff (`Status: resumed`)
and has completed its `Next concrete step`, the working agent does not send the user to `/handoff`.
It asks once — "that finishes the thread; close the handoff?" — and on a yes sets
`Status: closed YYYY-MM-DD` in place, plus one line saying what finished. This is the only handoff
write permitted outside `/handoff`, and the user's yes is still required; a handoff this session did not
resume stays untouched.

## Guardrails

- Never delete a handoff, resumed or stale (`CORE-NO-DELETE`).
- Never restate what memory already holds. Point at it.
- Do not act on a handoff the user did not choose.
