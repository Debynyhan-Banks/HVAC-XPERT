# Canonical Schemas

These JSON Schema Draft 2020-12 contracts define the normalized manufacturer knowledge model. They are the source of truth for persisted and exchanged records; framework-specific types must remain compatible with them.

## Relationship chain

```text
Manufacturer
  -> Brand
  -> Equipment Family
  -> Model Revision
  -> Document
  -> Component
  -> Connector
  -> Pin
  -> Electrical Node
  -> Connection
  -> Operating State
  -> Measurement
  -> Fault
  -> Approved Diagnostic Path
     -> Operational Diagnostic Case
     -> Deterministic Training Replay
        -> Training Attempt
  -> Instructor-authored Training Scenario
```

`common.schema.json` contains shared primitives. `provenance.schema.json` is embedded by every knowledge record so each extracted assertion remains source-visible and reviewable.

`source-registry.schema.json` validates the acquisition allowlist and enforces the fail-closed approval gate.

`diagnostic-path.schema.json` stores reviewed manufacturer-derived complaint, test, expected-result, and branch relationships. `diagnostic-case.schema.json` stores technician observations and deterministic evaluations separately from published equipment knowledge. `training-replay.schema.json` stores the answer-redacted replay definition; `training-attempt.schema.json` stores safety state, clearly labeled synthetic observation, learner response, transparent scoring, and post-submission remediation. `personal-knowledge-entry.schema.json` stores one private owner-entered equipment, fault, measurement, or diagnostic-branch record with exact applicability, source or field context, confidence, safety, and fail-closed guidance status.

## Contract rules

- One equipment-model record represents one revision.
- Required unknown values are represented as `null`, not fabricated defaults.
- Domain records require at least one provenance assertion.
- References use stable IDs and require a separate referential-integrity validation pass.
- Schema conformance is necessary but does not establish technical correctness.

## Files

- `manufacturer.schema.json`
- `brand.schema.json`
- `equipment-family.schema.json`
- `equipment-model.schema.json`
- `document.schema.json`
- `document-source.schema.json`
- `component.schema.json`
- `connector.schema.json`
- `pin.schema.json`
- `node.schema.json`
- `connection.schema.json`
- `operating-state.schema.json`
- `measurement.schema.json`
- `fault.schema.json`
- `diagnostic-path.schema.json`
- `diagnostic-case.schema.json`
- `training-replay.schema.json`
- `training-attempt.schema.json`
- `personal-knowledge-entry.schema.json`
- `scenario.schema.json`
- `provenance.schema.json`
- `source-registry.schema.json`
