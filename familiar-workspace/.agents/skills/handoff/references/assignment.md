# `/handoff` → Assignment brief

> Branch of the `handoff` router. Reached only from `/handoff`; the user starts it, never
> a route match. Load this file after the branch is selected, then follow the context contract
> below and load nothing from the other branch.

Produce a single self-contained `.md` file that hands a scoped piece of work to someone with no
access to this project's memory or Knowledge — a coworker, or an AI tool they
run themselves (Copilot Chat, ChatGPT, another Claude session). Everything the recipient needs must
be **in the file**; they cannot come back and ask familiar a follow-up question.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md`, `3-Knowledge/_knowledge-index.md`, `4-Trackers/tasks.md`, and the source the brief is drawn from
- **Conditional context:** knowledge pages the index identifies as relevant to the task, and acceptance criteria and handoff constraints only when the brief needs them.
- **Excluded context:** Other projects, undeclared extension content, and project areas not required or conditionally triggered here.
- **Updates:** one brief in `2-Drafts/` (saved with `.familiar/scripts/draft_save.py`)
- **Capabilities:** file-read, file-write. Optional capabilities must degrade as the procedure states.
- **Completion:** A standalone brief names the owner, scope, inputs, required output, constraints, and acceptance check without relying on unstated project context.


## Procedure

1. **Ask who receives it.** The brief's opening framing depends on the answer:
   - **Coworker** — opens with a plain task statement a person reads first. If they will also feed
     it to their own AI tool, keep every fact explicit and self-contained anyway; do not assume they
     will supply project context themselves.
   - **AI agent / tool directly** — opens with role and instruction framing ("You are assisting
     with...") so the file works pasted straight in as the first message of a chat.
2. **Gather the minimum inputs.** Ask for whatever the user has not already given. Halt and ask rather
   than draft past a gap:
   - The task or deliverable — if this is still vague ("look into X"), ask what "done" looks like
     before drafting. Never invent a scope.
   - Why it matters / where it fits — one to three sentences, not the project history.
   - Deadline, or state plainly that none exists.
   - Definition of done — format, length, must-haves.
   - Who to go back to with questions (default: the user).
3. **Pull supporting facts from the project; do not invent them.** Check `_knowledge-index.md` and
   `4-Trackers/tasks.md`, then open only the knowledge pages the index shows as relevant to the task.
   Carry over only what the recipient needs to start, not the whole project history.
4. **Flag confidentiality before drafting.** If the task touches confidential project specifics —
   identifiers, unreleased figures, named individuals — say so and ask the user whether those belong
   in a file meant to leave the workspace. A local familiar folder does not establish a model host's,
   collaborator's, or recipient's confidentiality terms. Redact or generalize only on the user's
   instruction; never decide unasked.
5. **Draft** using the template below and save it with `draft_save.py` (slug `assignment-<slug>`, `.md`, `--ai`; `file-handling.md` → Saving under `2-Drafts/`).
   Record the producing skill/version and exact model/effort in `_draft-index.md` per
   `file-handling.md` → AI runtime provenance.
6. **Tell the user the path.** Promotion — copying it out to actually hand off — is their action, same
   as every other `Drafts` item.

## Template

```markdown
# Assignment: <short title>

**For:** <coworker name/role, or "AI agent">
**From:** <user name>
**Date:** YYYY-MM-DD
**Due:** <date, or "no fixed deadline">

## Task
<1-3 sentences: what to produce or investigate>

## Context
<why this matters, where it fits — only what the recipient needs>

## What you have to work with
<source material, links, files, constraints>

## Definition of done
<what "finished" looks like>

## Out of scope
<explicit boundaries; note anything redacted or generalized for confidentiality>

## Questions
Go back to: <user name / contact>
```

For the AI-agent framing, add a role line above `## Task`:
`You are assisting <user/org> with the task below. Read the whole brief before starting.`

## Guardrails

- Never invent a deadline, source, or scope detail the user did not give you. Missing input is a
  question, not a placeholder.
- This file is written to leave familiar's controlled environment. Run the confidentiality check in
  step 4 every time, not only when the task looks sensitive.
- Nothing here routes automatically. If the assignment creates something worth tracking ("waiting on
  Sarah's brief"), offer to log it in `4-Trackers/tasks.md` per `/save to-memory` —
  do not file it unasked.
