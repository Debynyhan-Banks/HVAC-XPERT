# ST-003 Training Replay Technical Review Guide

## Decision status

The deterministic training replay is an implementation candidate. Instructor and assigned HVAC/R technical reviewer acceptance remain required before `ST-003` is complete. Publication remains unauthorized, and the approved private package stays under legal hold.

## Evidence boundary

The replay adds no new manufacturer-derived diagnostic assertion. It reuses the technically approved Package 4 E24 path, Package 2 high-pressure-switch continuity definition, and their accepted source references. The new acceptance decision concerns training behavior, scoring clarity, safety gating, and whether the displayed remediation accurately preserves the approved branch boundary.

No source PDF, rendered page, or extracted private record is included in this repository guide.

## Review exercise

1. Load the approved E24 deterministic replay.
2. Confirm the simulated observation and answer controls remain hidden before de-energized safety acknowledgement.
3. Acknowledge safety and confirm the observation is visibly labeled `SIMULATED` and “not a live field measurement.”
4. Confirm the approved expected result remains continuity while the deterministic training observation is no continuity.
5. Submit `Does not match expected` and `Escalate`; confirm a score of `100/100`, a passing outcome, and no remediation.
6. Repeat with the deterministic hint; confirm the hint is disclosed before use and the score is `90/100`.
7. Submit an incorrect interpretation or disposition; confirm only the affected 50-point criterion fails and targeted remediation appears.
8. Confirm supported answers and approved branch guidance are not exposed before submission but are traceable afterward.

## Proposed behavior assertions

1. Safety gating prevents premature exposure of the synthetic observation, hint, and answer controls.
2. Synthetic evidence remains visibly and structurally distinct from field and reference evidence.
3. The replay never changes the approved test, expected result, or deterministic branch disposition.
4. Interpretation and disposition each contribute exactly 50 points.
5. Hint use subtracts exactly 10 points and remains visible in the scoring breakdown.
6. The passing threshold is exactly 80 of 100.
7. Incorrect choices produce criterion-specific remediation without inventing another test or repair action.
8. Equal attempt requests produce equal snapshots and no AI or randomness affects scoring.

## Bounded exclusions

- The rubric is an HVAC XPERT application decision, not manufacturer guidance, certification, or a psychometrically validated examination.
- The interface is not secure testing software and does not prevent a learner from viewing approved path definitions elsewhere in the local application.
- Attempts are not persisted, synchronized, or reported to an instructor portal.
- No live reading, connected instrument, equipment control, automatic diagnosis, repair authorization, or replacement decision is performed.
- No AI explanation, adaptive scenario generation, randomization, or unsupported next test is included.
- No public source redistribution or publication permission is granted.

## Acceptance statement

After completing the review exercise, the assigned reviewer may record acceptance with:

> I technically approve the eight ST-003 deterministic training behavior assertions and bounded exclusions. The scoring rubric is accepted for pilot practice use. Publication remains unauthorized.
