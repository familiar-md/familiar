<!-- familiar:start -->
# familiar adapter for Claude

<!-- Host adapter for Claude Code. Adds no protocol rules of its own -- see AGENTS.md. -->

@AGENTS.md

This file adds no protocol rules. Use this host's native skill discovery and the capability state recorded in `.familiar/installed.json`. A capability marked `available` is not active until its separate setup and health check succeed.

On this host each familiar skill's command is `/ili-<skill>` (`/ili-save` is `save`); the bare `/<skill>` also works. Give users the `/ili-` form.

Claude Code's own memory folder is not this project's record. A request to save, remember or hand off project work, including `/ili-save`, `/save`, `/ili-handoff` or `/handoff` written mid-message, starts that skill and writes inside this project, never to the host's memory folder.

When you need answers from the user, such as check-in questions, setup offers or a choice between options, ask with this host's AskUserQuestion tool: one question per item, the likely answers as options (the user can always type their own), at most four per call. Ask in plain text when only the user can write the answer (a date, a name, a reason) or the tool is unavailable.

<!-- Add your own instructions for this project below the end marker. familiar updates replace only this block. -->
<!-- familiar:end -->
