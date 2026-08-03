# Private Simulator Interface

This application serves the deterministic simulator through a local browser UI.
It binds only to `127.0.0.1`, validates the `Host` header, sends no cross-origin
headers, and loads approved packages at runtime from the ignored private vault.

Run the approved pilot package and extension:

```bash
python3 scripts/run_local_app.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --open
```

The interface supports:

- model and approved-definition counts
- exact manual operating-phase selection
- explicit power-available and operation-requested inputs
- exact approved fault-code activation
- explicit component commands and fault effects
- applicable diagnostic definitions with source-page references
- reference-only virtual meter display with approved mode, points, values, procedures, and safety category
- technician-validation labels and explicit manufacturer-verification status

The server creates a fresh deterministic simulator for every snapshot request.
It does not infer or persist equipment state, automate phase transitions, publish
private records, generate live or simulated meter readings, or serve on a
network-accessible interface.
