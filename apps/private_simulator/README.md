# Private Simulator Interface

This application serves the deterministic simulator through a local browser UI.
It binds only to `127.0.0.1`, validates the `Host` header, sends no cross-origin
headers, and loads approved packages at runtime from the ignored private vault.

Run the approved pilot package and all approved extensions:

```bash
python3 scripts/run_local_app.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --extension sources/private/review/RUN-ASXS6-20260804-003/package \
  --extension sources/private/review/RUN-ASXS6-20260804-004/package \
  --open
```

The interface supports:

- model and approved-definition counts
- a safety-gated deterministic training replay derived from each eligible approved diagnostic path
- clearly labeled simulated observations that cannot be mistaken for live or technician-entered measurements
- answer-redacted setup followed by explicit interpretation and disposition choices
- transparent application scoring: 50 interpretation points, 50 disposition points, a 10-point hint penalty, and an 80-point pass threshold
- post-submission supported answers, approved branch guidance, remediation, package lineage, and source traceability
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

Private Package 4 is technically approved and adds the first real `E24` diagnostic
path. It presents the approved de-energized high-pressure-switch continuity test,
then deterministically stops or escalates for continuity, no-continuity, and unknown
results. Technical approval does not authorize repair or publication.

The server creates a fresh deterministic simulator for every snapshot request.
It does not infer or persist equipment state, automate phase transitions, publish
private records, generate live meter readings, propagate voltage, infer current
flow or switching, or serve on a network-accessible interface. The reference meter
never generates a reading. Training mode generates only clearly labeled synthetic
observations from an approved deterministic branch. Field mode currently accepts
only explicit technician entry. Connected or imported instrument results remain
deferred.
