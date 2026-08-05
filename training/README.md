# Deterministic Training Replay

The training module reuses eligible approved diagnostic paths without changing their manufacturer-derived facts. It creates one answer-redacted replay definition for the first supported divergent-result branch in each path.

## Contract

- Safety acknowledgement is required before the synthetic observation, hint, or learner controls become available.
- Every generated observation has source type `SIMULATED` and is not a live or technician-entered measurement.
- Target interpretation, target disposition, approved branch guidance, score, and remediation remain hidden until both learner answers are submitted.
- Equal requests produce equal snapshots; the engine uses no randomness or AI.
- The underlying diagnostic case engine performs the deterministic comparison and branch selection in `TRAINING` mode.

## Scoring

- Interpretation: 50 points
- Supported disposition: 50 points
- Hint used: minus 10 points
- Passing score: 80 of 100

This is a transparent HVAC XPERT practice rubric. It is not a manufacturer score, certification, repair authorization, or secure examination system. Attempts are returned to the caller but are not persisted.

## Boundaries

Training replay does not connect to equipment, control equipment, read an instrument, infer an unsupported test, publish private records, or replace instructor and HVAC technical acceptance.
