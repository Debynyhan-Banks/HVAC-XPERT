# Roadmap

## Delivery method

HVAC XPERT keeps the phase structure below as governance and maturity gates, but implements product capability through the steel threads defined in `docs/STEEL_THREAD_DELIVERY.md`. A steel thread must produce a thin end-to-end technician outcome instead of completing one horizontal technical layer in isolation.

| Steel thread | Product outcome | Status |
| --- | --- | --- |
| `ST-000` | Governed private evidence and approval foundation | Foundation available; legal work ongoing |
| `ST-001` | Approved model-to-reference-simulator workflow | Complete for bounded pilot records |
| `ST-002` | First field diagnostic case loop | Complete for bounded E24 pilot path |
| `ST-003` | Training replay of the approved case | Pending |
| `ST-004` | Grounded AI explanation of approved evidence | Pending |
| `ST-005` | Reviewer and content-authoring operations | Pending |
| `ST-006` | Additional pilot-family cases and models | Pending |
| `ST-007` | Field persistence, mobile readiness, and escalation | Pending |
| `ST-008` | Confirmed OCR and read-only instrument imports | Deferred until pilot proof |
| `ST-009` | Controlled manufacturer expansion | Deferred until pilot proof |

`ST-002` requires no external API. Its first increment is limited to one exact model and revision, one evidence-supported complaint, one or more approved tests, deterministic result evaluation, and a traceable summary or escalation outcome. The path must stop rather than add tests unsupported by reviewed evidence.

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
