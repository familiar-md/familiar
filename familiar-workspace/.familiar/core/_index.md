# Core index

Read `bootstrap.md` first. It is the only always-loaded core protocol.

| File | Purpose | Load |
|---|---|---|
| `bootstrap.md` | Identity, project boundary, stable safety rules, and route selection | always |
| `routes.md` | Seven coarse routes and deterministic selection rules | after bootstrap |
| `state-schema.md` | Authoritative project-memory surfaces and stale-write protocol | when reading or updating state |
| `extension-contract.md` | Generic extension composition contract | setup or maintenance only |
| `capabilities.json` | Machine-readable capability vocabulary (at `.familiar/`, not here) | validation only |
| `extension-manifest.schema.json` | Machine-readable extension manifest schema (at `.familiar/`, not here) | validation only |
| `familiar-behavior.md` | Neutral lifecycle behavior shared by focused project routes | when a selected route needs lifecycle guidance beyond its skill body |
| `voice.md` | Writing voice, the avoid-list, and the pre-delivery check | whenever output is written, including a chat reply |
| `plain-language.md` | Which shape the writing takes and the sentence rules that bind under it | when producing or editing anything longer than a chat reply |
| `familiar-voice.md` | Optional conversational companion voice | only when project configuration enables familiar voice |
| `running-scripts.md` | What to do when Python or a package a script needs is missing | only when a script cannot run |
| `retrieval-fallback.md` | Inline retrieval/review behavior without named workers | loaded by `bootstrap.md` before worker dispatch when the active adapter's `named-subagents` capability is anything other than `active` |

`routes.md`, `state-schema.md` and `extension-contract.md` each exist twice: canonically here, and
copied to `.familiar/` for the project-local read the bootstrap addresses. The copies are held
byte-identical by `test_core_registry_copies_stay_identical`; edit the copy here, never the other.

Detailed procedure files are selected through `routes.md` or an installed skill. Open only the
section named by the selected skill. Project knowledge is reached through the project's own index.
Extension routes come from whichever extension skill folders are present on disk; core does not
infer or enumerate them.
