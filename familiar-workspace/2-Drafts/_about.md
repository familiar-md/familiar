# Drafts

Deliverable drafts awaiting user review: external and internal presentations, document drafts, marked-up
copies. The user reviews and **copies finished items out** into the normal project folders
(promotion is the user's action — familiar never writes outside the workspace).

`_draft-index.md` lists each deliverable's current file and status, so a person can navigate this
folder without an AI assistant. A deliverable is one flat file at v1. From v2 it gets its own
subfolder: `<deliverable>/` holds the current version, `<deliverable>/_superseded/` the earlier ones,
and `<deliverable>/_versions.md` one line per version. familiar does this when it saves; nothing is
deleted.

A deliverable that was scoped before drafting also has a `_brief.md` in its folder: its main
message, audience, key points and outline, settled with `/deliverable-brief` before the first draft.

If you edit a draft outside familiar, drop the edited file here (in the deliverable's folder or at
the root) and say which deliverable it belongs to; familiar registers it as the next version. It does
not belong in `1-Inputs/`.

If drafts pile up or untracked files appear, run `/system-settings` and pick Workspace tidy — it
proposes a cleanup and only acts on what you approve. Anything cleared out lands in a `_del/`
holding folder here, never deleted outright.
