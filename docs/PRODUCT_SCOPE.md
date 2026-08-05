# HVAC XPERT Product Scope

## Product definition

HVAC XPERT is a single-owner, local-first HVAC/R field copilot and personal training simulator. It converts facts manually recorded from legitimately accessed private sources and applicable field observations into searchable equipment knowledge, deterministic diagnostic behavior, interactive two-dimensional references, guided service calls, and personal training.

The field experience helps the owner decide what to inspect or measure next. The training experience lets the owner practice the same reasoning against clearly labeled simulated equipment behavior. Neither experience may present unsupported AI output as manufacturer fact. `PERSONAL_USE_PIVOT.md` is the active product-direction amendment.

## Personal product wedge

The product is a private diagnostic memory and one-next-test copilot for equipment the owner actually services. The approved model- and revision-specific E24 case remains the deterministic baseline, but new breadth is driven by real jobs and a ten-minute manual-entry target rather than a public content-acquisition program. Training remains in scope and reuses supported diagnostic paths.

## Product outcomes

HVAC XPERT must help users:

- identify the exact equipment model, family, and applicable revision;
- understand components, connectors, wiring, operating sequences, and fault definitions;
- collect a complaint, observations, fault codes, and technician-entered measurements;
- choose the next safe, discriminating diagnostic test;
- compare an actual or simulated result with an approved expectation;
- narrow possible causes without converting hypotheses into facts;
- inspect the source, page, validation level, and review state behind technical guidance;
- document findings, unresolved questions, escalation, and service disposition; and
- practice troubleshooting through reviewed scenarios, hints, scoring, and remediation.

## Primary users

- Primary owner and user: `Debynyhan-Banks`
- Future technicians, instructors, contractors, reviewers, and administrators are deferred until a separate shared-use or commercial scope decision

## Product capability pillars

### 1. Personal equipment knowledge

- Manual private upload and manual fact entry
- Immutable source identity, hashing, applicability, revision, and provenance
- Structured equipment, component, connector, fault, sequence, measurement, and procedure records
- Explicit unknowns and conflicts
- Simple owner-facing confidence labels backed by the existing validation metadata
- A fail-closed export gate that remains separate from personal use

### 2. Field diagnostic support

- Equipment and revision confirmation
- Complaint, observation, fault-code, and prior-work intake
- Safety screening before diagnostic instructions
- Evidence-backed next-test recommendations
- One-next-test-at-a-time field presentation
- Manual entry of real measurements and observations
- Deterministic comparison with approved expectations
- Ranked hypotheses labeled by supporting and contradicting evidence
- Stop, escalate, and manufacturer-support boundaries
- Case timeline and service-summary generation

### 3. Interactive equipment reference

- Original semantic SVG schematics and bounded topology views
- Components, connectors, terminals, conductors, and measurement points
- Approved sequence-of-operation visualization
- Source and validation traceability from every inspectable fact
- Component-location photographs or original locator illustrations when authorized and useful

Two-dimensional semantic diagrams are the default because they directly support electrical diagnosis. General photorealistic three-dimensional equipment rendering is not required for the pilot. A targeted 3D teaching aid may be considered later only when it demonstrates a spatial concept that 2D diagrams and photographs cannot explain adequately.

### 4. Deterministic simulation and virtual instruments

- Reviewed electrical state and fault behavior
- Explicit operating-state machines
- Fault injection
- Virtual multimeter behavior
- Additional virtual instruments only when approved source data supports their behavior
- Clear separation between simulated readings and real technician-entered readings

The deterministic engine, not AI, establishes simulated operational truth.

### 5. Personal training and optional AI

- Reviewed service-call scenarios
- Personal workflow, hints, scoring, remediation, and progress
- AI explanations grounded in approved knowledge and simulator state
- Owner-authored scenarios confirmed before they influence scoring or guidance
- Additional difficulty paths only when personal use demonstrates a need

### 6. Owner knowledge operations

- Fast manual creation and correction
- Owner source comparison and field confirmation
- Conflict and revision handling
- Scenario and procedure authoring
- Versioned private knowledge and backup/restore
- Audit history sufficient to understand where a fact came from and why it changed

Multi-role review, publication operations, organization administration, and customer content workflows are deferred.

## Operational modes

### Field mode

Field mode works with actual technician observations. HVAC XPERT does not claim to connect to, control, or automatically read the equipment. A value is an actual field reading only when the technician explicitly records it as such. The application may compare that value with an approved reference but must preserve the distinction between manufacturer fact, technician observation, deterministic evaluation, and AI hypothesis.

The default field view presents one primary next test with its reason, safety boundary, points, meter mode, expected result, and result-entry control. Detailed provenance and reviewer metadata remain directly available without dominating the field workflow.

### Training mode

Training mode uses clearly labeled simulated faults, states, and readings produced by the deterministic engine. Simulated outcomes must never appear in field case records or be described as live equipment readings.

### Owner mode

Owner mode manages manual entries, sources, field confirmations, conflicts, procedures, diagrams, scenarios, and backups. Existing reviewer and decision metadata remains auditable, but separate organizational roles are not required for daily personal use.

## How private documents ground optional AI

Legitimately accessed private documents remain useful. They are not used to create an untraceable model memory. The personal path is:

1. Privately upload a document the owner may legitimately access.
2. Record source, hash, model applicability, and document revision.
3. Manually enter concise facts in original wording with page references.
4. Validate schemas, references, units, and model boundaries.
5. Mark the fact `MANUAL_CONFIRMED` only after direct owner comparison.
6. Keep the resulting knowledge local and private.
7. Retrieve only applicable confirmed facts for the current question or case.
8. Let optional AI organize and explain the evidence with visible citations and uncertainty.

Retrieval from approved records is the default AI grounding method. Foundation-model training on manufacturer PDFs is not required. Future fine-tuning may be considered for licensed workflow examples, classification, or response style, but it cannot replace retrieval, provenance, deterministic evaluation, or human approval.

AI output is never a source. If approved evidence is missing or conflicting, the answer must say so and stop or escalate when safety requires it.

## Personal alpha scope

The approved Daikin Comfort Technologies Amana and Goodman S-Series records beginning with model `ASXS6S4810AA` remain the deterministic baseline. New entries may cover other equipment encountered by the owner, but each entry must retain exact model, revision, source or field context, and confidence status.

The pilot should prove one complete diagnostic loop:

1. Confirm equipment and revision.
2. Capture the complaint, observations, and available fault codes.
3. Present applicable safety boundaries.
4. Select an approved diagnostic test.
5. Show points, meter mode, procedure, expected result, and provenance.
6. Record a technician-entered result or obtain a simulated result in training mode.
7. Evaluate the result deterministically.
8. Update supported, contradicted, and unresolved hypotheses.
9. Recommend the next approved test, stop, or escalation action.
10. Produce a traceable case summary.

The personal alpha retains V1 electrical schematic training, approved voltage and signal-path visualization, virtual multimeter behavior, service-call simulations, and deterministic training replay. AI explanation is optional and deferred until manual search and local case history are useful without it.

## Required pilot document coverage

| Capability | Minimum preferred evidence |
| --- | --- |
| Model identity, ratings, and applicability | Product specification or engineering data |
| Installation, supply, terminals, and field wiring | Installation manual and applicable wiring diagram |
| Fault definitions and diagnostic procedures | Service manual and current service bulletins |
| Components and replacement-part identity | Applicable repair-parts catalog |
| Connector, pin, and signal identity | Connector chart, wiring diagram, or control documentation |
| Operating sequence and commanded behavior | Sequence chart, service manual, or engineering documentation |
| Expected electrical measurements | Manufacturer diagnostic table or approved component data |
| Component-specific behavior | Original component-manufacturer datasheet when manufacturer equipment documentation is insufficient |

The existing product-specification, installation, service, and repair-parts documents do not need to be uploaded again. Additional documents should be added only for equipment or evidence gaps relevant to personal service work and must remain in controlled private storage.

## Explicitly deferred or excluded

The following do not belong in the pilot unless a later approved scope change establishes a demonstrated diagnostic or training need:

- general photorealistic 3D equipment models;
- a complete thermodynamic or refrigerant-cycle physics engine;
- AR equipment recognition;
- live equipment control, unattended sensor collection, or IoT commissioning;
- automatic repair authorization;
- technician dispatching, invoicing, payment, or inventory-management systems;
- broad multi-manufacturer ingestion before the pilot quality gates pass;
- multi-tenant SaaS, organization management, customer billing, or team permissions;
- instructor portals, enterprise analytics, and public content operations;
- unrestricted crawling or collection from unapproved sources;
- publication of complete restricted manuals or copied source diagrams; and
- AI answers based only on model memory, general web content, or unreviewed extraction.

## Personal expansion candidates

After the pilot demonstrates diagnostic accuracy and safe use, candidates include:

- equipment families and models encountered on real service calls;
- offline-capable field access;
- nameplate model and serial OCR with mandatory technician confirmation;
- user-authorized read-only import from compatible meters and probes;
- authorized equipment and component photographs;
- voice-assisted case intake with visible confirmation;
- approved parts applicability and service-bulletin alerts;
- historical case and known-good comparison with exact equipment applicability;
- additional virtual instruments;
- encrypted backup and restore; and
- narrowly targeted 3D or AR teaching aids with a validated learning benefit.

## Personal success measures

- Time to add a useful model, fault, measurement, or branch
- Time to find the next applicable test
- Percentage of technical claims with exact applicability and source or field context
- Rate of promotion from `UNVERIFIED` to `MANUAL_CONFIRMED` or `FIELD_CONFIRMED`
- Safety-stop and escalation correctness
- Time and number of steps required to reach the next discriminating test
- Diagnostic-path agreement with reviewed manufacturer procedures
- Rate of unsupported or misapplied guidance, with a target of zero display as confirmed guidance
- Case-summary completeness and traceability
- Repeat use on actual service calls
- Personal improvement across deterministic training replays
- Knowledge-package freshness and revision coverage
- Successful encrypted backup and restore
