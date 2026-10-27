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
| 2026-07-20-Northgate-SOW | b2dd48f50858 | 1-Inputs/Sources/2026-07-20_Northgate-SOW.md |  | source | ingested | 3-Knowledge/2026-07-20_Northgate-SOW.md |  | 2026-08-24 |  |
| 2026-07-22-Kickoff-Notes | bcf3778024a7 | 1-Inputs/Sources/Meetings/2026-07-22_Kickoff-Notes.md |  | source | ingested | 3-Knowledge/2026-07-22_Kickoff-Notes.md |  | 2026-08-24 |  |
| 2026-06-region-logistics-market-note | 2ad5b75c8070 | 1-Inputs/Sources/2026-06-region-logistics-market-note.md |  | source | ingested | 3-Knowledge/2026-06_Regional-Logistics-Market-Note.md |  | 2026-08-24 |  |
