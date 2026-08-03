# Deterministic Simulator

The simulator consumes a `PrivateKnowledgePackage` that has already passed
`scripts/private_package_gate.py`. It copies approved model, revision, component,
fault, and simulator-effect definitions into immutable runtime structures.

## Current contract

- `OperatingInputs` accepts only explicit power availability and operation-requested booleans.
- Operating states are manually selected by exact approved state ID.
- Selected states apply only their explicit approved component commands.
- Diagnostic definitions expose expected values, points, procedures, safety categories, and source pages; they are not simulated readings.
- Source references preserve technician validation level, outcome, reviewer, and review timestamp for display in the private application.
- Faults are manually activated by an exact code present in the approved package.
- Active faults apply only their declared `simulator_effects` values.
- Matching effects are combined; state/fault conflicts for the same target property fail closed.
- Components without an explicit approved command or effect remain `UNKNOWN`.
- Snapshots contain no wall-clock time, random values, or AI-generated state.

The engine-level status reports the simulator envelope, not a manufacturer
sequence of operation. Status precedence is active fault, unavailable power,
operation requested, then idle.

## Local runner

List the approved states and diagnostic definitions:

```bash
python3 scripts/run_simulator.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --list-states \
  --list-measurements
```

Manually select steady cooling and request operation:

```bash
python3 scripts/run_simulator.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --state ASXS6S4810AA:state:cooling-steady-control \
  --power-available \
  --operation-requested
```

The command emits JSON for local internal development. It does not publish private
records or source documents.

## Deliberate limit

The approved pilot extension contains six cooling-phase records and six diagnostic
measurements, but no reviewed automatic transition logic or transition timing. The
engine requires manual phase selection and rejects transition-bearing definitions.
It must not infer contactor, valve, inverter, timing, or lockout behavior.
