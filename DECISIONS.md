# Architecture Decision Records

This file records accepted cross-project decisions. Revisions must preserve prior text, add a superseding decision, and explain migration impact.

## ADR-001: Deterministic simulator is the source of truth

- Status: Accepted
- Date: 2026-08-02
- Decision: The simulation engine determines electrical state, readings, fault behavior, and transitions. AI may explain those results but does not determine them.
- Reason: LLM output is probabilistic and cannot establish safe circuit behavior.

## ADR-002: PostgreSQL is the primary operational database

- Status: Deferred for shared or commercial use by ADR-021
- Date: 2026-08-02
- Decision: Store normalized operational records in PostgreSQL. Store source binaries in controlled object storage and reference them by immutable hash.
- Reason: Relational constraints, transactions, and auditability suit the knowledge graph's core records.

## ADR-003: JSON Schema defines canonical data contracts

- Status: Accepted
- Date: 2026-08-02
- Decision: Use JSON Schema Draft 2020-12 for persisted and exchanged knowledge records. Application-specific validators may be generated from or mapped to these schemas.
- Reason: Language-neutral contracts support TypeScript, Python, database, and review tooling.

## ADR-004: SVG is the canonical interactive schematic format

- Status: Accepted
- Date: 2026-08-02
- Decision: Use original SVG redraws linked to canonical component and node identifiers.
- Reason: SVG supports semantic identifiers, animation, accessibility, hit targets, and responsive rendering.

## ADR-005: Provenance is mandatory for extracted facts

- Status: Accepted
- Date: 2026-08-02
- Decision: Every extracted fact must identify its source document, source location, extraction method, and validation level.
- Reason: Untraceable technical data cannot be safely reviewed, corrected, or trusted.

## ADR-006: Human review precedes publication

- Status: Accepted
- Date: 2026-08-02
- Decision: AI- or OCR-extracted records cannot enter the public knowledge base until they pass the publication gate in `VALIDATION_POLICY.md`.
- Reason: Extraction confidence is not evidence of technical correctness.

## ADR-007: Model revisions remain separate

- Status: Accepted
- Date: 2026-08-02
- Decision: An equipment record represents one explicit model revision. Records from different revisions may be linked but not silently merged.
- Reason: Connector assignments, boards, sequence logic, and service values may change between revisions.

## ADR-008: Manufacturer acquisition adapters are pluggable

- Status: Accepted
- Date: 2026-08-02
- Decision: Discovery, metadata normalization, and access behavior are implemented behind small source and manufacturer interfaces.
- Reason: Adding a manufacturer must not require rewriting existing adapters or core ingestion logic.

## ADR-009: Original redraws replace public diagram redistribution

- Status: Accepted
- Date: 2026-08-02
- Decision: Public experiences use original interactive drawings derived from validated facts. Source diagrams remain access-controlled unless redistribution is expressly permitted.
- Reason: This supports interactivity while reducing copyright and licensing risk.

## ADR-010: Unknown and conflicting facts stay explicit

- Status: Accepted
- Date: 2026-08-02
- Decision: Unknown values are represented as `null`; conflicts are stored as distinct sourced assertions and are never resolved by silent inference.
- Reason: Apparent completeness must not replace factual integrity.

## ADR-011: Completed work is synchronized to GitHub

- Status: Accepted
- Date: 2026-08-02
- Decision: Each validated work unit is committed and pushed to `https://github.com/Debynyhan-Banks/HVAC-XPERT.git` before it is reported complete. Normal changes use a focused branch and pull request when supported; the initial publication may establish `main` directly.
- Reason: Frequent remote synchronization preserves continuity, reviewability, and recovery while the project is developed across human and AI work sessions.

## ADR-012: Technical approval and publication authorization are separate gates

- Status: Accepted
- Date: 2026-08-02
- Decision: Technically approved private packages may support internal development, but public export requires a separate explicit publication approval and a cleared legal hold. All missing or contradictory gate values block export.
- Reason: HVAC/R correctness review does not establish source licensing, redistribution rights, or permission to publish manufacturer-derived records.

## ADR-013: Missing simulator behavior remains unknown

- Status: Accepted
- Date: 2026-08-02
- Decision: The deterministic simulator applies only explicit operating-state commands and fault effects from approved model-revision records. Missing component behavior remains `UNKNOWN`, and conflicting active effects fail closed rather than being resolved by precedence or inference.
- Reason: A plausible sequence is not evidence of the manufacturer's actual sequence and could create unsafe troubleshooting guidance.

## ADR-014: New assertions use immutable approval extensions

- Status: Accepted
- Date: 2026-08-02
- Decision: New facts added after a package is technically approved enter a separate pending `KNOWLEDGE_EXTENSION` that references the approved base package. Runtime composition is allowed only after the extension receives its own complete technical decision.
- Reason: Editing an approved package would silently broaden the scope of its prior review and weaken the audit trail.

## ADR-015: Unlabeled terminals use positional identifiers

- Status: Accepted
- Date: 2026-08-04
- Decision: When an applicable source drawing shows terminal positions without manufacturer pin numbers, extraction records may use explicit positional identifiers such as `LEFT`, `CENTER`, and `RIGHT`. The records must state that the identifiers describe drawing position, preserve manufacturer numbering as unknown, and remain pending until technical review.
- Reason: Positional identifiers preserve visible connectivity without inventing manufacturer pin assignments or discarding usable topology evidence.

## ADR-016: AI retrieves approved evidence instead of becoming the evidence store

- Status: Accepted
- Date: 2026-08-04
- Decision: AI troubleshooting and instruction retrieve applicable, approved, versioned knowledge records at request time and expose their provenance. Foundation-model memory and unreviewed extraction cannot establish manufacturer facts. Fine-tuning is not required for the pilot and cannot replace retrieval, deterministic rules, or review gates.
- Reason: Retrieval preserves model and document revisions, supports corrections and citations, reduces unsupported answers, and keeps technical truth outside a probabilistic model.

## ADR-017: Field and training evidence remain separate

- Status: Accepted
- Date: 2026-08-04
- Decision: Field mode accepts explicitly identified technician observations and actual readings. Training mode uses clearly labeled deterministic simulator results. Simulated values cannot enter a field case as actual observations, and AI cannot fabricate either type.
- Reason: A user must always know whether a value came from physical equipment, an approved reference definition, deterministic simulation, or AI explanation.

## ADR-018: Pilot depth precedes market breadth

- Status: Accepted
- Date: 2026-08-04
- Decision: The pilot proves one complete model- and revision-specific diagnostic case before prioritizing broad manufacturer coverage, connected-instrument integrations, general 3D content, or a large training catalog. The primary field interface presents one next test at a time while keeping evidence directly available.
- Reason: A complete, safe, and reviewable diagnostic loop demonstrates the product's intended value more clearly than a wide collection of incomplete reference or visualization features.

## ADR-019: Product implementation uses steel threads

- Status: Superseded by ADR-020 for active delivery
- Date: 2026-08-04
- Decision: Preserve roadmap phases as governance and maturity gates while implementing product capability as thin end-to-end steel threads. Each thread must cross the applicable evidence, schema, deterministic-logic, interface, validation, HVAC-review, and repository-publication layers and must declare its access requirements before implementation.
- Reason: Vertical delivery exposes integration, evidence, safety, and usability risks early and prevents isolated horizontal subsystems from creating an appearance of progress without a complete technician outcome.

## ADR-020: Personal local-first use is the active product direction

- Status: Accepted
- Date: 2026-08-04
- Decision: Develop HVAC XPERT first as a single-owner, local-first field copilot and personal training tool for `Debynyhan-Banks`. Prioritize ten-minute manual entry, searchable local case history, phone-first offline access, and job-driven equipment breadth. Defer multi-tenant SaaS, public manufacturer-content publication, organizational review roles, customer billing, and broad automated ingestion.
- Reason: Personal use can validate whether the deterministic one-next-test workflow provides repeatable field value without requiring public content rights, cloud infrastructure, or commercial operations. Private-data, exact-applicability, safety, provenance, evidence-separation, and fail-closed export controls remain mandatory.

## ADR-021: Personal entries begin as private local JSON records

- Status: Accepted
- Date: 2026-08-05
- Decision: P-001 stores one canonical JSON file per owner-entered equipment, fault, measurement, or diagnostic-branch record under the ignored local knowledge directory. No entry becomes an active deterministic rule automatically. PostgreSQL remains deferred until shared, commercial, scale, or concurrency requirements justify it.
- Reason: Per-record local JSON provides immediate private personal value, schema visibility, simple backup inputs, and a low-complexity path into P-002 search without introducing a cloud service or database before sustained personal use establishes the need.
