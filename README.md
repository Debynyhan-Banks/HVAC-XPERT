# HVAC XPERT

HVAC XPERT is a governed HVAC/R lead-technician, knowledge, simulation, and training platform. It converts manufacturer documentation into validated equipment knowledge, interactive schematics, evidence-grounded diagnostic cases, troubleshooting simulations, and AI-guided service workflows. See `docs/PRODUCT_SCOPE.md` for the canonical capability boundaries.

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

The first controlled extraction, its operating-state/measurement extension, and its bounded electrical-topology extension are technically approved in private, ignored packages. Internal development composes approved records through the validated private-package gate; public export remains disabled under the unresolved legal and source-rights hold. The deterministic simulator supports exact manual phase selection, approved component commands, fault injection, approved diagnostic definitions, a reference-only virtual meter, and a reference-only SVG connection map through a private browser interface that binds only to `127.0.0.1`. The meter and topology view display approved definitions but never fabricate live readings, propagate voltage, infer switching or current flow, or add unreviewed connectivity. Automatic transitions remain disabled because reviewed timing and transition conditions do not exist. Automated discovery or downloading begins only after `approved_for_collection` is set to `true` by an authorized reviewer in `sources/source-registry.yaml`.

## Private local interface

```bash
python3 scripts/run_local_app.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --extension sources/private/review/RUN-ASXS6-20260804-003/package \
  --open
```

The local interface reads the ignored, approved packages at runtime. It does not
copy private records into tracked application assets or expose a network listener.

## Completion protocol

Every validated work unit must be committed and pushed to `https://github.com/Debynyhan-Banks/HVAC-XPERT.git`. Before committing, inspect the staged files and exclude private source documents, secrets, local environment files, and temporary output. See `AI_HANDOFF.md` for the full synchronization and handoff protocol.
