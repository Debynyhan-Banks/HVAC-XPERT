# Private Simulator Interface

This application serves the deterministic simulator through a local browser UI.
It binds only to `127.0.0.1`, validates the `Host` header, sends no cross-origin
headers, and loads approved packages at runtime from the ignored private vault.

Run the approved pilot package and both extensions:

```bash
python3 scripts/run_local_app.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --extension sources/private/review/RUN-ASXS6-20260804-003/package \
  --open
```

The interface supports:

- model and approved-definition counts
- a bounded field diagnostic case panel with exact complaint and fault-code entry conditions
- required safety acknowledgement before the next approved test is shown
- technician-entered actual results with deterministic comparison and fail-closed completion, stop, or escalation outcomes
- traceable case state, package IDs, reviewer status, and source pages without implying that the application measured the equipment
- exact manual operating-phase selection
- explicit power-available and operation-requested inputs
- exact approved fault-code activation
- technician-readable component commands and fault effects that preserve raw approved values without inventing exact setpoints
- reference-only SVG topology generated from approved connectors, terminals, nodes, and explicit wires
- explicit display of standalone bounded nodes, unknown wire colors, reviewer status, and source-page traceability
- a direct diagnostic-test selector plus visibly actionable test rows
- applicable diagnostic definitions with source-page references
- reference-only virtual meter display with approved mode, points, values, procedures, and safety category
- technician-validation labels and explicit manufacturer-verification status

The first real `E24` diagnostic path is held in private Package 4 pending HVAC
technical review. Until that review is explicitly accepted, the approved-package
command above correctly shows no real diagnostic path. Synthetic fixtures validate
the interface and deterministic behavior without promoting the pending assertion.

The server creates a fresh deterministic simulator for every snapshot request.
It does not infer or persist equipment state, automate phase transitions, publish
private records, generate live or simulated meter readings, propagate voltage,
infer current flow or switching, or serve on a network-accessible interface.
Field mode currently accepts only explicit technician entry. Connected or imported
instrument results remain deferred.
