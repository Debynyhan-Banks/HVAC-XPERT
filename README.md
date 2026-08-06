# HVAC XPERT

HVAC XPERT is a single-owner, local-first HVAC/R field copilot and personal training tool. It turns the owner's private source facts and field observations into searchable equipment knowledge, interactive references, deterministic diagnostic cases, and training replays. See `docs/PERSONAL_USE_PIVOT.md` and `docs/PRODUCT_SCOPE.md` for the active boundaries.

## Current status

- Phase: Personal alpha — local field copilot
- Primary owner: `Debynyhan-Banks`
- Deterministic baseline: `ASXS6S4810AA` revision `AA`
- Active thread: `P-002` searchable private memory; owner acceptance pending
- Repository visibility: Public; private records and source files remain excluded
- Automated collection: Not authorized or needed for the personal workflow

No crawler may download source material until the applicable source record has completed terms, robots, licensing, and access review.

## Start here

Every contributor and AI agent must read these files in order:

1. `PROJECT_CHARTER.md`
2. `docs/PERSONAL_USE_PIVOT.md`
3. `CURRENT_STATE.md`
4. `DECISIONS.md`
5. `DATA_GOVERNANCE.md`
6. `SOURCE_POLICY.md`
7. `VALIDATION_POLICY.md`
8. `AI_HANDOFF.md`
9. The schemas relevant to the task

## Non-negotiable rules

- Never invent manufacturer data.
- Preserve unknown values as `null`.
- Attach provenance and validation status to every extracted fact.
- Keep model revisions separate.
- Treat OCR and AI output as unvalidated until reviewed.
- Keep source binaries, copied expression, field history, and private knowledge outside Git.
- Export or publish only through an explicit fail-closed decision.
- Create original interactive redraws instead of redistributing manufacturer diagrams without permission.

## Repository map

| Path | Responsibility |
| --- | --- |
| `docs/` | Supporting project documentation and future ADR files |
| `schemas/` | Canonical JSON Schema data contracts |
| `sources/` | Source registry and source-review records |
| `ingestion/` | Discovery and controlled acquisition adapters |
| `extraction/` | Text, OCR, visual, table, and structured extraction |
| `validation/` | Automated and human-review workflows |
| `knowledge-base/` | Versioned, approved knowledge packages |
| `simulator/` | Deterministic electrical and refrigeration simulation |
| `apps/` | User, administration, API, and worker applications |
| `tests/` | Unit, integration, golden-document, and acceptance tests |
| `scripts/` | Auditable maintenance and validation commands |

## Active direction

The approved private baseline and completed `ST-001` through `ST-003` workflows remain available: manual phase/reference simulation, SVG topology, virtual reference meter, bounded E24 field case, and deterministic training replay. Public export remains disabled. The active product work now prioritizes fast manual entry, personal confidence states, searchable local case history, phone-first offline access, and job-driven equipment breadth. The interface must continue to distinguish private references, actual field observations, deterministic evaluations, simulations, and optional AI explanations. It never fabricates live readings, authorizes repair, or invents unsupported tests.

P-001 provides a private localhost form that saves one model, fault, measurement, or diagnostic branch as a local JSON record while preventing unverified, conflicted, revision-unknown, or safety-unknown entries from driving guidance. P-002 adds local search across those records, immutable correction lineage, and server-evaluated private field-case history without activating personal entries as deterministic rules.

## Private local interface

```bash
python3 scripts/run_local_app.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --extension sources/private/review/RUN-ASXS6-20260804-003/package \
  --extension sources/private/review/RUN-ASXS6-20260804-004/package \
  --open
```

The local interface reads the ignored, approved packages at runtime. It does not
copy private records into tracked application assets or expose a network listener.

## Completion protocol

Every validated work unit must be committed and pushed to `https://github.com/Debynyhan-Banks/HVAC-XPERT.git`. Before committing, inspect the staged files and exclude private source documents, secrets, local environment files, and temporary output. See `AI_HANDOFF.md` for the full synchronization and handoff protocol.
