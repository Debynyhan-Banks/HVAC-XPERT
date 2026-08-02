# HVAC XPERT

HVAC XPERT is a governed HVAC/R knowledge, simulation, and training platform. It converts manufacturer documentation into validated equipment knowledge, interactive schematics, troubleshooting simulations, and AI-guided service workflows.

## Current status

- Phase: Phase 0 — Governance and foundation
- Pilot organization: Daikin Comfort Technologies
- Pilot brands: Amana and Goodman
- Pilot family: S-Series inverter outdoor units
- Pilot model: `ASXS6S4810AA`
- Collection authorization: Not yet approved

No crawler may download source material until the applicable source record has completed terms, robots, licensing, and access review.

## Start here

Every contributor and AI agent must read these files in order:

1. `PROJECT_CHARTER.md`
2. `CURRENT_STATE.md`
3. `DECISIONS.md`
4. `DATA_GOVERNANCE.md`
5. `SOURCE_POLICY.md`
6. `VALIDATION_POLICY.md`
7. `AI_HANDOFF.md`
8. The schemas relevant to the task

## Non-negotiable rules

- Never invent manufacturer data.
- Preserve unknown values as `null`.
- Attach provenance and validation status to every extracted fact.
- Keep model revisions separate.
- Treat OCR and AI output as unvalidated until reviewed.
- Publish only records that pass the required validation gate.
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

## Immediate gate

The first controlled extraction is technically approved in a private, ignored package. Internal development loads it through a validated private-package gate; public export remains disabled under the unresolved legal and source-rights hold. The deterministic simulator foundation preserves unknown behavior and applies only approved fault effects. A separate private operating-state and measurement extension is now pending HVAC/R technical review; it cannot load until explicitly approved. Automated discovery or downloading begins only after `approved_for_collection` is set to `true` by an authorized reviewer in `sources/source-registry.yaml`.

## Completion protocol

Every validated work unit must be committed and pushed to `https://github.com/Debynyhan-Banks/HVAC-XPERT.git`. Before committing, inspect the staged files and exclude private source documents, secrets, local environment files, and temporary output. See `AI_HANDOFF.md` for the full synchronization and handoff protocol.
