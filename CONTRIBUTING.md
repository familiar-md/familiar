# Contributing

familiar has a single maintainer, so response times vary. Issues are welcome and are the most useful
contribution, especially reports from assistants and operating systems other than Claude Code on Windows.

Questions, ideas and "how do I…" threads go in this repository's
[Discussions](https://github.com/familiar-md/familiar/discussions) tab; keep Issues for something broken
or a specific change you'd like made.

## Reporting an issue

A useful issue lets the maintainer reproduce what you saw. Please include:

- The assistant and its version (for example, run `claude --version`), and the model it was using if you know it.
- Your operating system and, if the problem involves documents or PDFs, the output of `python .familiar/scripts/doctor.py` (`python3` on macOS).
- Your familiar version (`familiar-version:` in the project's `.familiar-project` file).
- The `familiar bound` line from the start of the session, or a note that there was none.
- What you asked, as exactly as you remember it, and which skill ran.
- What you expected, and what happened instead. Quote error messages in full.

Do not attach project documents you would not want public. Describe the content instead.

If you believe an instruction could cause the assistant to write outside the project folder, delete
files, or send data somewhere, follow [`SECURITY.md`](SECURITY.md) instead of opening a public issue.

## Pull requests

Keep them small, and open an issue first so the change can be discussed before you spend time on it.
Core is deliberately small and host-neutral; changes that add domain-specific content, or behavior
that only one host supports, are unlikely to be accepted into core.

The repository's own gate suite (`tests/quality_gates.py`) is maintainer-only and is not part of this
download, so the maintainer runs it on your change. Documentation fixes and corrections to host
behavior, with a link to the vendor's documentation, are the easiest to accept.

## Extensions

Specialty add-ons do not belong in this repository. Build them in their own repository against
`.familiar/core/extension-contract.md`. Start from
[familiar-template](https://github.com/familiar-md/familiar-template) ("Use this template"), which
carries the contract checklist and a validator, and tag your repo with the `familiar-extension`
topic so others can find it. An extension that works against the extension contract does not need
any change to core.

## License

By contributing you agree that your contribution is licensed under the Apache License 2.0, as is the
rest of the project (see [`LICENSE`](LICENSE)).
