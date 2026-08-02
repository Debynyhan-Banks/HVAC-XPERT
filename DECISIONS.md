# Architecture Decision Records

This file records accepted cross-project decisions. Revisions must preserve prior text, add a superseding decision, and explain migration impact.

## ADR-001: Deterministic simulator is the source of truth

- Status: Accepted
- Date: 2026-08-02
- Decision: The simulation engine determines electrical state, readings, fault behavior, and transitions. AI may explain those results but does not determine them.
- Reason: LLM output is probabilistic and cannot establish safe circuit behavior.

## ADR-002: PostgreSQL is the primary operational database

- Status: Accepted
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
