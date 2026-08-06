# Roadmap

## Delivery method

HVAC XPERT now implements personal value through the personal threads defined in `docs/STEEL_THREAD_DELIVERY.md`. Each thread must deliver a thin end-to-end outcome for the owner rather than building unused horizontal infrastructure. The original phase structure remains below as a deferred reference for any future commercial or shared-use decision.

| Personal thread | Product outcome | Status |
| --- | --- | --- |
| `P-000` | Adopt the single-owner local-first product scope | Complete; merged in PR #21 |
| `P-001` | Add a model, fault, measurement, or branch manually in ten minutes | Implementation complete; owner acceptance pending |
| `P-002` | Search private knowledge and persist local case history | Next after P-001 acceptance |
| `P-003` | Use the copilot phone-first and offline without public exposure | Pending |
| `P-004` | Expand knowledge from equipment encountered on real jobs | Pending |
| `P-005` | Add optional retrieval-grounded AI explanation | Deferred until manual workflow proves useful |
| `P-006` | Encrypt, back up, restore, and export owner-controlled data | Pending |
| `P-007` | Evaluate customer-supplied-content platform potential | Deferred until sustained personal use |

## Personal thread sequence

### P-000 — Personal scope

- Make the owner the only active user and decision-maker.
- Preserve private-data, safety, deterministic, provenance, and export boundaries.
- Defer SaaS, public manufacturer content, organizational roles, and customer operations.
- Record that repository visibility remains an explicit owner decision.

### P-001 — Ten-minute manual entry

- Create a fast local form for equipment identity, fault code, measurement, expected result, safety boundary, source or field context, and confidence status.
- Permit draft `UNVERIFIED` entries but prevent them from driving deterministic guidance.
- Promote entries to `MANUAL_CONFIRMED` or `FIELD_CONFIRMED` explicitly.
- Validate exact identifiers, model/revision applicability, and required safety data.

### P-002 — Personal memory

- Add local persistence for knowledge, cases, observations, corrections, and field confirmations.
- Search by model, fault code, symptom, component, and recent case.
- Keep actual, reference, deterministic, simulated, and AI evidence visibly distinct.

### P-003 — Phone and offline use

- Provide an installable phone-first interface with local/offline data access.
- Avoid solving phone access by exposing the current localhost service directly to a public network.
- Complete storage, encryption, backup, and device-loss review before field adoption.

### P-004 — Job-driven breadth

- Add only equipment and problems the owner encounters or expects to service.
- Measure reuse, time saved, corrections, unsupported stops, and conflicts.
- Prefer a useful partial personal memory over a broad public ingestion pipeline.

## Completed technical foundations

| Foundation | Outcome |
| --- | --- |
| `ST-000` | Private evidence, schema, approval, and export gates available |
| `ST-001` | Bounded model-to-reference simulator complete |
| `ST-002` | Bounded E24 field diagnostic case complete |
| `ST-003` | Deterministic training replay implemented; personal acceptance remains available |

## Deferred public-product roadmap

The maturity phases below are not active delivery commitments. They are retained only to prevent a future commercial decision from bypassing source rights, security, validation, or publication controls.

## Phase 0 — Governance and foundation

Deliverables:

- Project charter, handoff, decisions, risks, security, and contribution rules
- Source, data-governance, validation, and license-review policies
- Canonical JSON schemas
- Pilot source registry

Exit gate:

- Governance documents approved
- Schema suite validates successfully
- Named owners assigned for source, legal, and technical review

## Phase 1 — Manufacturer data acquisition and provenance

Deliverables:

- Approved manufacturer source records
- Pluggable Daikin/Goodman/Amana discovery adapter
- Controlled download, hashing, deduplication, and audit logging
- Ten to twenty-five pilot documents
- Document/revision/model mappings

Exit gate:

- Terms, robots, access, and licensing reviews completed
- Collection tests pass against approved fixtures
- Pilot documents are fingerprinted and classified

## Phase 2 — Extraction and validation

Deliverables:

- Native PDF, OCR, image, table, and metadata extraction
- Structured AI extraction with prompt/model version logging
- Automated schema and referential validation
- Reviewer workflow with accept, revise, reject, and conflict states
- Versioned pilot knowledge package

Exit gate:

- Every published fact has source provenance
- Conflicts and unknowns are recorded
- Golden-document tests pass
- HVAC technical review is complete

## Phase 3 — Interactive schematic simulator

Deliverables:

- SVG schematic renderer
- Deterministic electrical state engine
- Operating-state machines
- Virtual multimeter
- Fault injection and measurement-point behavior

Exit gate:

- Simulator output matches the approved pilot knowledge package
- Measurement and fault behavior pass reviewer acceptance tests

## Phase 4 — Training and service-call experience

Deliverables:

- Scenario engine
- AI instructor grounded in approved records
- Technician workflow, scoring, hints, and remediation
- Instructor authoring and review portal
- Field diagnostic case intake and safety screening
- Approved next-test selection and technician result entry
- Field-first presentation of one primary next test with evidence available on demand
- Deterministic result evaluation and hypothesis evidence tracking
- Escalation packet and traceable case summary

Exit gate:

- Training scenarios are technically reviewed
- AI answers expose provenance and validation status
- Safety-sensitive guidance passes acceptance review
- One pilot complaint completes the bounded diagnostic case loop
- Actual, reference, simulated, and AI-generated information remain visibly distinct

## Phase 5 — Controlled expansion

Deliverables:

- Additional equipment families and manufacturer adapters
- Source partnerships or licensed data feeds
- Field troubleshooting experience
- Offline-capable field access after safety and synchronization review
- Nameplate OCR with technician-confirmed model and serial identity
- User-authorized read-only meter and probe import
- Remote lead-technician review and historical case comparison
- Approved service-bulletin and parts-applicability alerts
- Quality, reliability, and content-operations metrics

Exit gate:

- Each new source and family passes the same governance gates as the pilot
