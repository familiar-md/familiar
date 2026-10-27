<!-- familiar-state-schema: 1.0 -->
<!-- revision: 1 -->
<!-- last-updated: 2026-07-22 -->
# Decision — Model both single-site and two-site consolidation scenarios

**Date:** 2026-07-22
**Track:** shared
**Status:** active
**Decided by:** Client (Marcus Ilunga, Northgate VP Operations), overriding Meridian's original
proposal

## Context
Meridian's original proposal scoped a single-site (Hartsdale) consolidation scenario only, on the
assumption that Hartsdale could absorb full consolidated volume. At kickoff, Marcus was firm that a
two-site fallback needed to stay on the table in case Hartsdale's capacity assumption did not hold
[`2026-07-22_Kickoff-Notes.md`, §2 Decisions Made]. This directly overrode Meridian's proposed scope.

## Options considered
- **Single-site only (Meridian's original proposal).** Simpler model, faster to build, but no
  fallback if the base-case site's capacity assumption fails during or after implementation.
- **Two-site fallback in parallel (client-directed, chosen).** More modeling work up front — a
  second full scenario, not a variant — but avoids committing to a single site before capacity is
  proven.

## Decision
Model both scenarios in parallel throughout the engagement, not sequentially and not single-site
only.

## Consequences
Commits `RESEARCH` to building and maintaining two full cost/savings scenarios (see `4-Trackers/tasks.md`)
rather than one, extending the modeling workload but not the SOW's stated deliverable count or
timeline. Forecloses presenting a single-site-only recommendation without also showing the two-site
comparison.

## What would reopen this
If Hartsdale's confirmed expansion capacity (`status-log.md`, 2026-08-08) is later found to be
overstated, or if the client explicitly de-scopes the two-site scenario to save modeling time.
