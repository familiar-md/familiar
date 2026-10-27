# `/system-settings` → Hooks

> Branch of the `system-settings` router. Reached only from `/system-settings`; the user starts it,
> never a route match. Load this file after the branch is selected, then follow the context
> contract below and load nothing from the other branches.

## Context contract

- **Required context:** `.familiar/core/voice.md`, `.familiar/core/plain-language.md`, `.familiar/core/file-handling.md` → Naming and copies, `.familiar/routes.md` → Running familiar's scripts, and `.familiar/hooks/catalog.json`.
- **Conditional context:** none. This branch never opens a host's hook file itself; `install_hooks.py` reads and edits it.
- **Excluded context:** Other projects, `~/.familiar/`, every host settings file other than the one the user chose, and project content.
- **Updates:** The chosen host's hook file only (`.claude/settings.local.json`, or `.codex/hooks.json`), through `python .familiar/hooks/install_hooks.py apply` or `remove` with `--yes`, plus the `.bak` copy the tool leaves beside it. Nothing else, and nothing outside the project.
- **Capabilities:** file-read, and running a Python script, which does the writing; this branch does not edit the hook file itself. Where the host cannot run a script, say so, then give the user the exact command to run themselves; do not edit the hook file by hand.
- **Completion:** The user has seen what is available and what is installed, and any change they approved is written and read back with `list` — or they are told nothing was changed.

## What this is for

Hooks are small programs a host runs at fixed moments: when a session starts, before a tool call, after
one. familiar's optional hooks package offers a few, such as titling each session after its project so
a phone's session list is readable, and guards that deny a tool call which would break one of familiar's
rules. Nothing here is on by default, and none of it is part of core. This branch lets the user see what is
available and install or remove one at a time. The tool does the editing; this branch never writes a hook
file itself.

## Procedure

1. Check for `.familiar/hooks/install_hooks.py` and `.familiar/hooks/catalog.json`. If either is missing,
   say that hooks are an optional separate download that has not been added to this project, that
   its own install file says how to add it, and stop.
2. Find a Python as `routes.md` → Running familiar's scripts says. Do not guess one.
3. Ask which host the hooks are for, defaulting to the one this session is running in: `claude` or
   `codex`. For Gemini CLI, say that no hook file can be written for it and the package's install
   file gives the by-hand route, then stop.
4. Run `python .familiar/hooks/install_hooks.py list --host <host>` and say in plain words what each
   hook does and whether it is installed. Say plainly where a hook's status is not confirmed on a live host,
   and do not describe an unconfirmed guard as protecting anything. Ask what the user wants: install some,
   remove some, or nothing.
5. For a change, run `python .familiar/hooks/install_hooks.py preview <ids> --host <host>` (or `remove`
   without `--yes`), show the user the output, and ask before writing (`CORE-HUMAN-APPROVAL`). Never pass `--yes` on your own judgement or
   for a different set than the one previewed.
6. On a yes, run the same command with `--yes`, then `list` again and tell the user what is now
   installed. A hook loads when a session starts, so say it takes effect in the next session, and that the
   session title in particular shows the next time they open one.
7. If the tool reports an error, or the hook file is not valid JSON, say so, leave the file alone, and
   stop. Do not repair a settings file by hand.

## Guardrails

- One host's hook file per run. A change to a second host is a second run, previewed and approved again.
- A hook that is not confirmed on a live host never makes a capability `active`; report the host's capability state as `.familiar/installed.json` records it.
- This branch does not install the hooks package itself; getting it into the project is the user's step.
