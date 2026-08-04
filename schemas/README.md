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
  -> Training Scenario
```

`common.schema.json` contains shared primitives. `provenance.schema.json` is embedded by every knowledge record so each extracted assertion remains source-visible and reviewable.

`source-registry.schema.json` validates the acquisition allowlist and enforces the fail-closed approval gate.

`diagnostic-path.schema.json` stores reviewed manufacturer-derived complaint, test, expected-result, and branch relationships. `diagnostic-case.schema.json` stores technician observations and deterministic evaluations separately from published equipment knowledge.

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
- `scenario.schema.json`
- `provenance.schema.json`
- `source-registry.schema.json`
