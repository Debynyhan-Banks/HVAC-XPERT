# Data Governance Policy

## Purpose

This policy defines how HVAC XPERT privately records, stores, confirms, uses, corrects, backs up, exports, and removes manufacturer-derived facts and owner field observations.

## Governing principles

1. Source authority and traceability outrank convenience.
2. Unknown values remain `null`; missing values are not guessed.
3. Conflicting assertions remain separate until the owner resolves them with applicable evidence.
4. Source binaries, manual entries, field observations, normalized records, and any export are distinct data layers.
5. Every transformation is reproducible from versioned inputs, code, prompts, and schemas.
6. Export or publication is a controlled state transition, not the default result of personal entry.

## Data layers

| Layer | Contents | Default access |
| --- | --- | --- |
| Source metadata | Titles, hashes, applicability, revisions, and private references | Owner only |
| Source binary | Original PDFs, images, videos, or exports | Restricted local storage |
| Manual entry | Concise facts in original owner wording with source or field context | Owner only |
| Field observation | Actual service-call observations and measurements | Owner only |
| Canonical knowledge | Normalized, confirmed, versioned equipment records | Local application |
| Export presentation | Explicitly selected owner data without restricted source content | Disabled by default |

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

## Personal confidence states

Daily personal use exposes the status vocabulary defined in `docs/PERSONAL_USE_PIVOT.md`: `UNVERIFIED`, `MANUAL_CONFIRMED`, `FIELD_CONFIRMED`, and `CONFLICTED`.

`UNVERIFIED` and `CONFLICTED` records cannot drive deterministic guidance. `MANUAL_CONFIRMED` requires direct owner comparison with an applicable private source. `FIELD_CONFIRMED` requires an applicable real service-call observation and does not override a conflicting manufacturer reference without explicit resolution.

## Canonical validation states

Use the ladder defined in `VALIDATION_POLICY.md`. A record may advance only when evidence for the next level is recorded. Downgrades are allowed when a conflict, revised source, or review error is discovered.

## Identity and revision rules

- Stable IDs do not encode mutable display names.
- A model record represents one explicit revision.
- Document applicability to brand, family, model, serial range, and revision is recorded rather than inferred.
- Duplicate files share a SHA-256 fingerprint but retain source-discovery events.
- Superseded records remain auditable and link to their replacement.

## Active role

| Role | Responsibility |
| --- | --- |
| Personal knowledge owner | Entry, source comparison, field confirmation, conflicts, safety, retention, backup, removal, and export decisions |

Separate source reviewer, extraction operator, instructor validator, publisher, administrator, and customer roles are deferred. Existing records retain their historical role and decision metadata.

## Current role assignments

| Role | Assignee | Scope | Status | Assigned |
| --- | --- | --- | --- | --- |
| Personal knowledge owner | `Debynyhan-Banks` | Private sources, personal field cases, applicability, technical confirmation, and export decisions | Active | 2026-08-04 |

Ownership does not automatically confirm an entry. Every actionable entry must still record identity, date, applicability, source or field context, outcome, and personal confidence state.

## Change control

- Schema changes require a recorded decision and migration impact review.
- Automated extraction remains deferred; any future run must log code, schema, prompt, and model versions.
- Confirmed personal knowledge remains versioned; corrections create a new version or explicit supersession record.
- Manual edits require source or field context and personal confidence fields.

## Retention and removal

- Retention follows the source's license, contractual terms, and operational need.
- A source owner request or access change triggers an immediate dependency and export review.
- Removal must address source binaries, rendered derivatives, caches, local indexes, backups, and exported artifacts as required.
- Audit records retain non-content metadata when legally permitted.

## Quality metrics

Track applicability and context coverage, schema pass rate, conflict rate, time-to-entry, time-to-confirmation, revision coverage, unsupported stops, field reuse, correction rate, and backup-restore success.
