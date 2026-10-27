# familiar extension contract

Contract version `1.1` uses a UTF-8 JSON manifest named `familiar-extension.json` at an extension package root. JSON is the initial format because it is machine-checkable without an additional parser.

## Identity and compatibility

Each manifest declares a stable lowercase `id`, `display_name`, semantic `version`, compatible `core` range, and one `type`: `workflow`, `specialty`, `enforcement`, or `integration`. The extension ID is its namespace.

## Contributions

An extension may declare routes, skills, agents, state surfaces, required and optional capabilities, compatibility constraints, conflicts, package contents, and update metadata. Every contribution name is unique within the extension. A declared route carries a `select_when` trigger string, the same role the core route registry's "Select when" column plays. A declared state surface is an object with `path`, `schema_version`, `update_behavior`, and `scaffold`, as described in `state-schema.md` → Extension state surfaces.

Core discovers manifests generically and does not contain extension IDs. An extension is present exactly when its skill folder exists in this host's native skill location and its package exists at `.familiar/extensions/<id>/package/` — no separate manifest registry; adapter capability state is recorded in `.familiar/installed.json`.

## Composition and collisions

- Core route IDs are reserved.
- Extension route IDs begin with the extension namespace followed by a dot.
- Skill, agent, and state-surface IDs are namespaced in the installed registry.
- A plugin-scoped agent `<namespace>:<agent>` is materialized as project-native
  `<namespace>-<agent>` definitions for every active host adapter. Its filename, declared name,
  copied skill references, and installed registry mapping must agree.
- Any duplicate fully qualified ID, materialized native invocation collision, or declared conflict
  is an installation error. Nothing validates this at drop-in time — there is no installer — so it
  is the extension author's contract to keep. This repository's own maintainer-only gate suite
  checks it for the extensions maintained here; that tooling is not included in a drop-in copy, so a
  third-party extension author keeps the contract by inspection.
- Registry order controls display order only. It never grants override precedence.
- Removing an extension means deleting exactly the paths its drop-in folder added: its skill
  folders under each host's skill location, its `<namespace>-<agent>` worker files, and
  `.familiar/extensions/<id>/`. No ownership record exists to derive that set from, so each
  extension states it in its own `_about.md`.

## Capability behavior

Capabilities are evaluated per installed adapter at read time, by comparing the manifest's required
and optional capabilities against that adapter's state in `.familiar/installed.json` — `host_status`
is derived, never stored. At least one adapter must have all required capabilities active for the
extension to be usable; a host missing a required capability cannot select the route. A host with no row in `.familiar/installed.json` (for example Cursor, GitHub Copilot, or OpenCode) has every capability treated as `unknown`: it performs worker contracts inline per `retrieval-fallback.md`, and because it cannot confirm an extension route's required capabilities it reports the route as unverified on this host and asks the user before running it, rather than refusing silently or running silently. Missing optional capabilities use the
manifest's explicit `unavailable_behavior`: `hide`, `degrade`, or `report-unavailable`. An
enforcement extension must report inactive unless its mechanism passed that host's fixture.

`package.update_source` is recorded for an update route but does not authorize a network fetch. A state surface with `scaffold: true` ships already created at
revision `0`, and is never replaced by a later drop-in of the same extension — user state survives
an extension update because the update replaces package paths only.

The versioned JSON Schema at `.familiar/extension-manifest.schema.json` is authoritative for machine validation.
