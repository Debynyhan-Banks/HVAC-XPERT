# Data Governance Policy

## Purpose

This policy defines how HVAC XPERT acquires, stores, transforms, validates, publishes, corrects, and removes manufacturer-derived knowledge.

## Governing principles

1. Source authority and traceability outrank convenience.
2. Unknown values remain `null`; missing values are not guessed.
3. Conflicting assertions remain separate until an authorized reviewer resolves them.
4. Source binaries, extracted assertions, normalized records, and public presentation are distinct data layers.
5. Every transformation is reproducible from versioned inputs, code, prompts, and schemas.
6. Publication is a controlled state transition, not the default result of extraction.

## Data layers

| Layer | Contents | Default access |
| --- | --- | --- |
| Source metadata | URLs, titles, ownership, access and license decisions | Internal |
| Source binary | Original PDFs, images, videos, or exports | Restricted |
| Raw extraction | Native text, OCR, page images, tables, regions | Restricted |
| Sourced assertions | Individual facts with provenance and validation level | Internal review |
| Canonical knowledge | Normalized, reviewed, versioned equipment records | Application services |
| Public presentation | Original drawings, explanations, and approved facts | Public or customer |

## Required provenance

Every extracted assertion must record:

- Stable fact and entity identifiers
- Property path and value
- Unit when applicable
- Source document identifier, revision, page, and section when available
- Source URL or controlled source reference
- Extraction method and timestamp
- AI provider, model, and prompt version when applicable
- Confidence as an extraction signal, never as validation proof
- Validation level, reviewer, timestamp, and notes

The canonical contract is `schemas/provenance.schema.json`.

## Validation states

Use the ladder defined in `VALIDATION_POLICY.md`. A record may advance only when evidence for the next level is recorded. Downgrades are allowed when a conflict, revised source, or review error is discovered.

## Identity and revision rules

- Stable IDs do not encode mutable display names.
- A model record represents one explicit revision.
- Document applicability to brand, family, model, serial range, and revision is recorded rather than inferred.
- Duplicate files share a SHA-256 fingerprint but retain source-discovery events.
- Superseded records remain auditable and link to their replacement.

## Roles

| Role | Responsibility |
| --- | --- |
| Data governance owner | Policy, access, retention, removal, and audit decisions |
| Source reviewer | Terms, robots, license, access, and rate-limit approval |
| Extraction operator | Reproducible extraction runs and quality flags |
| Technical reviewer | HVAC/R correctness and source comparison |
| Instructor validator | Training suitability and instructional clarity |
| Publisher | Final publication gate and release record |

One person may hold multiple roles during the pilot, but the review action and identity must still be recorded.

## Change control

- Schema changes require a recorded decision and migration impact review.
- Extraction runs log code, schema, prompt, and model versions.
- Published knowledge packages are immutable; corrections create a new version.
- Manual edits require the same provenance and review fields as automated extraction.

## Retention and removal

- Retention follows the source's license, contractual terms, and operational need.
- A source owner request triggers an immediate publication review and dependency trace.
- Removal must address source binaries, rendered derivatives, caches, search indexes, and public artifacts as required.
- Audit records retain non-content metadata when legally permitted.

## Quality metrics

Track provenance coverage, schema pass rate, conflict rate, reviewer rejection rate, revision coverage, time-to-review, publication rollback rate, and golden-document regression rate.
