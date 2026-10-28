# Security policy

## Reporting a vulnerability

Report privately. Use this repository's Security tab and choose Report a vulnerability, which uses
GitHub's private vulnerability reporting. Please do not open a public issue for anything described
below. Include the familiar version, the assistant and its version, your operating system, and the
smallest set of steps that reproduces the problem.

This is a single-maintainer project with no bounty program. You will get an acknowledgment as soon
as the maintainer can give one, and credit in the fix unless you ask otherwise.

## What is in scope

familiar is a set of instructions and helper scripts that an AI assistant follows; it is not a
service. In scope are defects in what familiar ships that could make an assistant, or a shipped
script, do one of these things when it should not:

- Write, move, or overwrite a file outside the project folder, other than the documented writes
  under `~/.familiar/` (`user-preferences.md`, the hub's `fleet.md`, and `brief-profiles/`), each made only
  on your explicit request.
- Delete a project file, or overwrite a source document or an existing draft.
- Send project content to an outside service without your approval, including through a skill, an
  agent definition, or a bundled script.
- Run a script or command in a way that lets content from a source document control what is
  executed.

## What is out of scope

- The behavior of the assistant products and models themselves. Report those to their vendors.
- A model failing to follow familiar's instructions. The rules are written instructions, not
  mechanical enforcement, so a model can ignore them; the project says so openly. A report that a
  specific wording reliably leads a model to break a rule is welcome as an ordinary issue, unless it
  meets the list above.
- Problems in an extension built by someone else, or on an assistant familiar has no capability record for.
- Anything that needs prior write access to your project folder.

## Supported versions

Only the latest release receives fixes.
