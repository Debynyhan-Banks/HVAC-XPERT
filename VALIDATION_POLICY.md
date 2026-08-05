# Validation Policy

## Purpose

Validation establishes what evidence supports a technical fact. Extraction confidence measures parser certainty only and does not replace validation.

## Validation ladder

| Level | Name | Minimum evidence |
| --- | --- | --- |
| 0 | `LEVEL_0_UNKNOWN` | Value is unknown, absent, unreadable, or unresolved |
| 1 | `LEVEL_1_AI_EXTRACTED` | AI or automated extraction produced the assertion with source coordinates |
| 2 | `LEVEL_2_SOURCE_VISIBLE` | A reviewer can see the assertion in the cited source location |
| 3 | `LEVEL_3_CROSS_SOURCE_CONFIRMED` | A second authoritative source independently confirms the assertion |
| 4 | `LEVEL_4_TECHNICIAN_REVIEWED` | A qualified HVAC/R technician reviewed technical correctness and applicability |
| 5 | `LEVEL_5_INSTRUCTOR_VALIDATED` | A qualified instructor validated training use and explanation |
| 6 | `LEVEL_6_MANUFACTURER_VERIFIED` | The manufacturer or an authorized representative verified the assertion |

Levels describe evidence, not a simple workflow. A fact must not be advanced when the evidence for that level is missing.

## Personal confidence labels

The local personal interface may present the simpler labels below while preserving the canonical evidence and audit fields:

| Personal label | Minimum personal-use evidence |
| --- | --- |
| `UNVERIFIED` | Draft entry without completed owner comparison |
| `MANUAL_CONFIRMED` | Owner compared the entry with an applicable legitimately accessed private source |
| `FIELD_CONFIRMED` | Owner recorded an applicable real service-call observation |
| `CONFLICTED` | Source, revision, or field evidence disagrees or applicability remains unresolved |

`UNVERIFIED` and `CONFLICTED` entries are visible for correction but cannot drive deterministic guidance. `FIELD_CONFIRMED` records what happened in an applicable case; it does not silently replace a conflicting manufacturer reference.

## Automated validation

At minimum, validation must check:

- JSON Schema conformance
- Stable and unique IDs
- Referential integrity for manufacturer, brand, family, model, document, component, connector, pin, and node references
- Required provenance for every assertion
- Model and document revision compatibility
- Unit and quantity compatibility
- Voltage type and range plausibility rules
- No orphan pins, nodes, or connections
- Duplicate and contradictory assertions
- Explicit `null` values for known unknowns
- Personal confidence and export status consistent with recorded evidence

## Human review outcomes

- `PENDING`: Awaiting review
- `ACCEPTED`: Source and normalized value agree
- `REVISED`: Reviewer corrected the normalized value and recorded why
- `REJECTED`: Extraction is unsupported or inapplicable
- `CONFLICTED`: Authoritative sources disagree or applicability is unresolved

Rejected and conflicted facts remain auditable and are excluded from personal deterministic truth and any export.

## Public or customer export gate

A technical fact may enter any future public or customer knowledge base only when:

- It passes schema and referential validation.
- Its source is visible to the reviewer.
- Its review outcome is `ACCEPTED` or `REVISED`.
- It is at least `LEVEL_2_SOURCE_VISIBLE`.
- Safety-critical, connector, pinout, voltage, sequence, and fault-logic facts are at least `LEVEL_4_TECHNICIAN_REVIEWED`.
- No unresolved revision or applicability conflict exists.

The user interface must show a human-readable validation label and clearly indicate when manufacturer verification is pending.

## Regression controls

Golden-document tests compare approved outputs when extraction code, OCR tooling, schemas, prompts, or AI models change. Any unexplained difference blocks confirmed personal use and export until reviewed.
