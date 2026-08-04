# Diagnostic Case Workflow

## Purpose

This specification defines the bounded workflow that turns HVAC XPERT from a reference interface into an evidence-grounded lead-technician assistant. It does not authorize new manufacturer facts, autonomous diagnosis, live equipment control, or simulated field readings.

## Evidence classes

Every diagnostic statement belongs to one of these classes and must remain visibly distinguishable:

| Class | Meaning | Example handling |
| --- | --- | --- |
| Approved manufacturer fact | Reviewed record applicable to the exact model and revision | Display provenance, validation level, and review state |
| Technician observation | Symptom, condition, code, or measurement entered by the user | Record author, time, unit, conditions, and original value |
| Deterministic evaluation | Reproducible comparison or simulator result produced by approved rules | Record inputs, rule or definition ID, and outcome |
| AI hypothesis or explanation | Evidence-organizing assistance that may be incomplete | Label as a hypothesis and show supporting, contradicting, and missing evidence |
| Unknown or conflict | Required evidence is absent, ambiguous, or inconsistent | Preserve explicitly; do not fill it with inference |

## Case states

1. `CASE_CREATED`
2. `EQUIPMENT_IDENTIFIED`
3. `COMPLAINT_CAPTURED`
4. `SAFETY_SCREENED`
5. `EVIDENCE_REVIEWED`
6. `TEST_SELECTED`
7. `RESULT_RECORDED`
8. `RESULT_EVALUATED`
9. `NEXT_ACTION_SELECTED`
10. `ESCALATED` or `CASE_CLOSED`

The workflow may loop from `NEXT_ACTION_SELECTED` to `TEST_SELECTED`. It must not advance when required equipment identity, safety, applicability, or test-definition evidence is missing.

## Required case information

### Equipment identity

- Manufacturer and brand
- Exact model
- Serial or other available revision evidence
- Equipment role and configuration
- Applicable knowledge-package ID and revision
- Identity confidence based on recorded evidence, not AI confidence alone

### Service context

- Customer complaint in the technician's words
- Observed operating condition
- Environmental and load conditions when relevant
- Active and historical fault codes
- Work already performed
- Photographs or notes when authorized

### Safety state

- Energized or de-energized test requirement
- Required technician qualification
- PPE and instrument category when specified
- Stored-energy, pressure, refrigerant, rotating-equipment, and other applicable warnings
- Stop conditions and escalation requirement

## Next-test selection

A recommended test must:

- exist as an approved definition applicable to the selected model and revision;
- state why it discriminates among current hypotheses;
- identify the instrument mode and exact approved test points;
- state energized or de-energized status and approved safety category;
- show the expected value, range, state, or explicit unknown;
- cite the source page and review status;
- identify prerequisites and stop conditions; and
- avoid implying that selecting a test performs a real measurement.

AI may rank approved candidate tests based on case evidence. It may not invent a test, point, expected value, safety instruction, or applicability relationship. Deterministic rules perform comparisons and branch selection where approved rules exist.

## Result entry and evaluation

Field mode requires explicit technician entry of the observed result. The record must preserve:

- original value and unit;
- measurement definition and test-point IDs;
- timestamp and author;
- operating state and relevant conditions;
- optional technician note; and
- whether the result was actual, imported from an authorized instrument, or simulated.

Evaluation must be reproducible. The system may classify a value as inside, outside, above, below, matching, not matching, or unknown only when the approved definition supports that operation. It must not silently convert units, apply tolerances, or infer pass/fail criteria without an approved rule.

## Hypothesis handling

Each hypothesis must show:

- current status: `POSSIBLE`, `SUPPORTED`, `CONTRADICTED`, `CONFIRMED`, or `UNRESOLVED`;
- supporting observations and deterministic outcomes;
- contradicting evidence;
- missing evidence;
- applicable approved procedure or fault relationship; and
- the next approved test that would best distinguish it, when one exists.

AI-generated hypotheses remain hypotheses. `CONFIRMED` requires an approved confirmation rule or explicit qualified-reviewer decision. Absence of evidence is not evidence that a component is good.

## Stop and escalation behavior

The application must stop or escalate when:

- equipment identity or revision applicability is unresolved;
- required safety information is missing;
- the proposed test is outside the technician's stated qualification;
- approved evidence conflicts;
- no approved diagnostic branch exists;
- an observation indicates a hazardous condition;
- manufacturer support, engineering review, or a licensed specialist is required; or
- the technician requests escalation.

Escalation output should contain the equipment identity, complaint, fault codes, completed tests, actual readings, source-backed evaluations, unresolved conflicts, and the precise question requiring assistance.

## Case summary

A closed or escalated case should include:

- equipment and knowledge revision;
- complaint and initial conditions;
- safety acknowledgements;
- chronological tests and observations;
- actual versus expected results;
- deterministic evaluations;
- confirmed findings and unresolved hypotheses;
- actions taken or recommended;
- escalation details; and
- citations for every manufacturer-derived statement.

The summary must not claim that HVAC XPERT performed physical work, observed equipment directly, or authorized a repair.

## Minimum pilot user interface

- Case header with exact equipment identity and revision
- Complaint, fault-code, and observation intake
- Safety boundary panel
- Evidence panel with source and review status
- Hypothesis list with supporting, contradicting, and missing evidence
- One next-test card with rationale and procedure
- Technician result-entry form
- Deterministic result evaluation
- Case timeline
- Stop, escalate, and close actions
- Traceable case-summary export

## Acceptance boundary

The first workflow increment is complete when one reviewed pilot complaint can traverse the full case loop using only approved equipment records, diagnostic definitions, and deterministic comparisons. Training mode may traverse the same loop with clearly labeled simulator results. Unsupported branches must fail closed and explain what evidence is missing.
