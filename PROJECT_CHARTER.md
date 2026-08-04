# HVAC XPERT Project Charter

## Mission

Build a highly accurate interactive HVAC/R schematic, troubleshooting, and technician-training platform grounded in validated manufacturer documentation.

## Product outcome

HVAC XPERT transforms source documents into structured equipment knowledge, animated schematics, deterministic diagnostic simulations, evidence-grounded field diagnostic cases, guided service calls, and instructor-managed training content. `docs/PRODUCT_SCOPE.md` is the canonical capability and product-boundary specification.

## Primary users

- HVAC apprentices
- Residential technicians
- Commercial technicians
- Refrigeration technicians
- Instructors
- Contractors
- Service managers

## Core differentiator

Manufacturer documentation is transformed into traceable, validated, interactive equipment models rather than presented only as static PDFs. Users can inspect the source and validation level behind a technical claim.

## Initial scope

- Electrical schematic training
- Animated voltage and signal paths
- Virtual multimeter behavior
- Service-call simulations
- AI-guided troubleshooting explanations
- Evidence-grounded field diagnostic case workflow
- Instructor review workflows
- One manufacturer-family pilot

## MVP pilot

- Organization: Daikin Comfort Technologies
- Brands: Amana and Goodman
- Family: S-Series inverter outdoor units
- First model: `ASXS6S4810AA`

## Out of scope for MVP

- Broad multi-manufacturer ingestion
- A full thermodynamic physics engine
- AR equipment recognition
- Live technician dispatching
- Automatic repair authorization
- Unreviewed AI publication
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
6. Human review is required before public publication.
7. Legal, licensing, security, and source controls are product requirements.
8. Field observations, simulated readings, deterministic evaluations, and AI hypotheses remain distinct.
9. Two-dimensional semantic diagrams take priority over 3D presentation unless a validated learning need requires 3D.

## Success criteria for the pilot

- A reviewed source registry exists for the pilot family.
- Ten to twenty-five authoritative documents are fingerprinted and classified.
- Model and revision mappings are explicit.
- Extracted equipment, component, connector, fault, sensor, and sequence data pass schema validation.
- Every extracted fact has provenance and a validation level.
- Conflicts and unknowns are visible to reviewers and users.
- A qualified HVAC reviewer signs the pilot acceptance report.
