<!-- familiar-state-schema: 1.0 -->
<!-- revision: 3 -->
<!-- last-updated: 2026-08-24 -->
# Source Register

Every input file and what ingest did with it. Maintained by
the ingest skill's `scripts/source_register.py` (`.familiar/core/ingest.md` → Ingest procedure); edit a
row by hand only to correct it. One row per version: `Version` is the first 12 hex digits of the
file's SHA-256. `Status` is read, ingested, partial, failed, skipped, or superseded. `Roles` is any
of source, template, example, admin.

| Source ID | Version | Path | Aliases | Roles | Status | Knowledge page | Supersedes | Last processed | Note |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-03-Cauldron-SOW | e741dca30c78 | 1-Inputs/Sources/2026-08-03_Cauldron-SOW.md |  | source | ingested | 3-Knowledge/2026-08-03_Cauldron-SOW.md |  | 2026-08-24 |  |
| 2026-08-10-Kickoff-Notes | 39fd502930e1 | 1-Inputs/Sources/Meetings/2026-08-10_Kickoff-Notes.md |  | source | ingested | 3-Knowledge/2026-08-10_Kickoff-Notes.md |  | 2026-08-24 |  |
| 2026-07-regional-expansion-market-note | 345f4427c728 | 1-Inputs/Sources/2026-07-regional-expansion-market-note.md |  | source | ingested | 3-Knowledge/2026-07_Regional-Expansion-Market-Note.md |  | 2026-08-24 |  |
