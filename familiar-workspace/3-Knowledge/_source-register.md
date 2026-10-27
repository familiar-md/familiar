<!-- familiar-state-schema: 1.0 -->
<!-- revision: 0 -->
<!-- last-updated: not-yet-written -->
# Source Register

Every input file and what ingest did with it. Maintained by
the ingest skill's `scripts/source_register.py` (`.familiar/core/ingest.md` → Ingest procedure); edit a
row by hand only to correct it. One row per version: `Version` is the first 12 hex digits of the
file's SHA-256. `Status` is read, ingested, partial, failed, skipped, or superseded. `Roles` is any
of source, template, example, admin.

| Source ID | Version | Path | Aliases | Roles | Status | Knowledge page | Supersedes | Last processed | Note |
|---|---|---|---|---|---|---|---|---|---|
