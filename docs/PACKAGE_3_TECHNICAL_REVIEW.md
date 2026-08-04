# Package 3 Technical Review Guide

## Decision status

Package `RUN-ASXS6-20260804-003` is `TECHNICALLY_APPROVED_LEGAL_HOLD`. Assigned HVAC/R technical reviewer `Debynyhan-Banks` accepted all 48 assertions and the documented bounded exclusions at `2026-08-04T14:29:12Z`. Publication remains unauthorized.

## Evidence checked

- Product specification page 50: applicable `ASXS6S4210/4810/6010A*` wiring diagram
- Service instructions page 76: `Outdoor AC 3.5 - 5.0 ton` equivalent drawing
- Installation reference page 36: applicable drawing `3D142511`
- Private package validation: 6 connectors, 17 pins, 17 nodes, 8 connections, and 48 pending assertions

No source PDF, rendered page, or extracted private record is included in this public guide.

## Technical review findings

- **Model applicability:** The cited drawing family includes the 4810 model represented by the pilot package.
- **Incoming supply:** X1M L1 maps to A1P L1 on the black conductor; X1M L2 maps to A1P L2 on the red conductor. Both remain `LINE_VOLTAGE_AC`.
- **Compressor path:** A1P UO, VO, and WO map directly to M1C U, V, and W using red, yellow, and blue conductors. The IGBT-to-`MS 3~` path supports `INVERTER_3_PHASE_AC` classification.
- **Fan path:** The three X108A positions map directly to the matching three M1F positions. The drawing does not print numeric terminal identifiers or wire colors, so `LEFT`, `CENTER`, `RIGHT`, and `null` colors correctly preserve those unknowns.
- **Protective earth:** X1M protective earth is represented without inventing downstream bonding connectivity outside the bounded slice.
- **Exclusions:** Internal A1P electronics, sensors, switches, protection wiring, propagation, timing, switching, and inferred current flow remain outside this package.

## Technical decision

No discrepancy was found in the bounded topology slice. The assigned reviewer provided this direct decision:

> I technically approve all 48 Package 3 topology assertions and the documented bounded exclusions. Publication remains unauthorized.

The private decision advanced all 48 assertions to `LEVEL_4_TECHNICIAN_REVIEWED` with outcome `ACCEPTED`. The package remains private, and the decision does not authorize source redistribution, automated collection, or public publication.
