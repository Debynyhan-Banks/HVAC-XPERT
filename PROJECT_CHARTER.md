# HVAC XPERT Project Charter

## Mission

Build a highly accurate, local-first HVAC/R field copilot and personal training tool grounded in the owner's private sources and field-confirmed experience.

## Product outcome

HVAC XPERT helps its owner turn legitimately accessed private documents and real service-call observations into searchable equipment knowledge, deterministic diagnostic cases, interactive references, and personal training replays. `docs/PERSONAL_USE_PIVOT.md` is the active product amendment; `docs/PRODUCT_SCOPE.md` remains the canonical detailed capability boundary.

## Primary users

- Primary owner: `Debynyhan-Banks`
- Future users are deferred until a separate commercial or shared-use scope decision

## Core differentiator

Private source facts and field observations become a traceable, searchable diagnostic memory. The deterministic engine presents one supported next test at a time and stops rather than inventing missing guidance.

## Initial scope

- Electrical schematic training
- Animated voltage and signal paths
- Virtual multimeter behavior
- Service-call simulations
- AI-guided troubleshooting explanations
- Evidence-grounded field diagnostic case workflow
- Personal field log and confidence tracking
- Fast manual entry across equipment encountered in real service work
- One approved reference model and case retained as the deterministic baseline

## Personal alpha baseline

- Organization: Daikin Comfort Technologies
- Brands: Amana and Goodman
- Family: S-Series inverter outdoor units
- First model: `ASXS6S4810AA`
- Initial diagnostic path: bounded `E24` high-pressure-switch continuity case
- Initial training replay: deterministic divergent-result exercise

## Out of scope for MVP

- Automated broad multi-manufacturer ingestion
- A full thermodynamic physics engine
- AR equipment recognition
- Live technician dispatching
- Automatic repair authorization
- Public or customer distribution of private source-derived content
- AI answers based only on model memory or unreviewed extraction
- General photorealistic 3D equipment rendering
- Live equipment control or fabricated field readings
- Redistribution of complete copyrighted manuals without permission

## Product principles

1. Accuracy is more important than content volume.
2. The deterministic simulator is the source of operational truth.
3. AI explains and assists; it does not establish electrical truth.
4. Every technical fact is traceable to its source.
5. Unknown, ambiguous, and conflicting values remain explicit.
6. The owner explicitly confirms a fact before it drives personal deterministic guidance.
7. Legal, licensing, privacy, security, and source controls remain product requirements.
8. Field observations, simulated readings, deterministic evaluations, and AI hypotheses remain distinct.
9. Two-dimensional semantic diagrams take priority over 3D presentation unless a validated learning need requires 3D.

## Success criteria for personal use

- A new model, fault, measurement, or branch can be entered in ten minutes or less.
- Model and revision mappings remain explicit.
- Every actionable fact has source or field context and a personal confidence status.
- Conflicts and unknowns are visible and cannot silently drive guidance.
- Cases record actual observations separately from references and simulations.
- The application is useful repeatedly on the owner's real service calls.
- The private knowledge base can be backed up and restored without entering Git.
