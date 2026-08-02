# Deterministic Simulator

The simulator consumes a `PrivateKnowledgePackage` that has already passed
`scripts/private_package_gate.py`. It copies approved model, revision, component,
fault, and simulator-effect definitions into immutable runtime structures.

## Current contract

- `OperatingInputs` accepts only explicit power availability and operation-requested booleans.
- Faults are manually activated by an exact code present in the approved package.
- Active faults apply only their declared `simulator_effects` values.
- Matching effects are combined; conflicting effects for the same target property fail closed.
- Components without an explicit approved effect remain `UNKNOWN`.
- Snapshots contain no wall-clock time, random values, or AI-generated state.

The engine-level status reports the simulator envelope, not a manufacturer
sequence of operation. Status precedence is active fault, unavailable power,
operation requested, then idle.

## Deliberate limit

The approved pilot extension contains six cooling-phase records and six diagnostic
measurements, but no reviewed automatic transition logic or transition timing. The
current engine does not yet consume those records. Integration may expose manual
phase selection and explicit component commands only; it must not infer contactor,
valve, inverter, timing, or lockout behavior.
