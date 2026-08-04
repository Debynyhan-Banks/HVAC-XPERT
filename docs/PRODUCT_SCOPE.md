# HVAC XPERT Product Scope

## Product definition

HVAC XPERT is an evidence-grounded HVAC/R lead-technician assistant and training simulator. It converts authorized manufacturer documentation into reviewed equipment knowledge, deterministic diagnostic behavior, interactive two-dimensional schematics, guided service calls, and instructor-managed training.

The field experience helps a technician decide what to inspect or measure next. The training experience lets a learner practice the same reasoning against clearly labeled simulated equipment behavior. Neither experience may present unsupported AI output as manufacturer fact.

## Pilot product wedge

The pilot is a model- and revision-specific diagnostic copilot for technically complex inverter equipment. It must prove one complete, evidence-backed diagnostic case before prioritizing broad document coverage, hardware integrations, or a large training catalog. Training remains in scope and reuses the same approved diagnostic path after the field workflow is validated. `COMPETITIVE_POSITIONING.md` records the market analysis and priority rationale.

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

- HVAC apprentices and students
- Residential HVAC technicians
- Commercial HVAC technicians
- Refrigeration technicians
- Lead technicians and service managers
- HVAC instructors and training managers
- Contractors
- Source, legal, and HVAC technical reviewers
- Content authors and platform administrators

## Product capability pillars

### 1. Governed equipment knowledge

- Manual upload, authorized acquisition adapters, APIs, partnerships, and licensed feeds
- Immutable source identity, hashing, applicability, revision, and provenance
- Structured equipment, component, connector, fault, sequence, measurement, and procedure records
- Explicit unknowns and conflicts
- Separate technical approval and publication-authorization gates

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

### 5. Training and AI instruction

- Reviewed service-call scenarios
- Learner workflow, hints, scoring, remediation, and progress
- AI explanations grounded in approved knowledge and simulator state
- Instructor-authored scenarios with technical review before release
- Separate apprentice, technician, and advanced diagnostic paths when content supports them

### 6. Review and content operations

- Extraction review with accept, revise, reject, and conflict states
- HVAC technical approval
- Legal and source-rights review
- Scenario and procedure authoring
- Versioned knowledge-package publication and rollback
- Audit history and quality metrics

## Operational modes

### Field mode

Field mode works with actual technician observations. HVAC XPERT does not claim to connect to, control, or automatically read the equipment. A value is an actual field reading only when the technician explicitly records it as such. The application may compare that value with an approved reference but must preserve the distinction between manufacturer fact, technician observation, deterministic evaluation, and AI hypothesis.

The default field view presents one primary next test with its reason, safety boundary, points, meter mode, expected result, and result-entry control. Detailed provenance and reviewer metadata remain directly available without dominating the field workflow.

### Training mode

Training mode uses clearly labeled simulated faults, states, and readings produced by the deterministic engine. Simulated outcomes must never appear in field case records or be described as live equipment readings.

### Review mode

Review mode manages sources, extracted assertions, conflicts, technical decisions, publication rights, procedures, diagrams, and scenarios. Reviewer identity and decision history remain auditable.

## How official documents ground AI

Official and otherwise authorized documents remain required. They are not used to create an untraceable model memory. The controlled path is:

1. Upload or acquire an authorized document.
2. Record source, hash, model applicability, document revision, and access rights.
3. Extract candidate structured facts and bounded supporting text.
4. Validate schemas, references, units, and model boundaries.
5. Obtain HVAC technical review and any required legal approval.
6. Publish an immutable approved knowledge package.
7. Retrieve only applicable approved facts for the current question or case.
8. Let AI organize and explain the evidence with visible citations and uncertainty.

Retrieval from approved records is the default AI grounding method. Foundation-model training on manufacturer PDFs is not required. Future fine-tuning may be considered for licensed workflow examples, classification, or response style, but it cannot replace retrieval, provenance, deterministic evaluation, or human approval.

AI output is never a source. If approved evidence is missing or conflicting, the answer must say so and stop or escalate when safety requires it.

## Pilot scope

The first pilot remains bounded to the Daikin Comfort Technologies Amana and Goodman S-Series inverter outdoor-unit family, beginning with model `ASXS6S4810AA`.

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

The pilot also retains V1 electrical schematic training, approved voltage and signal-path visualization, virtual multimeter behavior, service-call simulations, AI-guided explanations, and instructor review workflows.

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

The existing product-specification, installation, service, and repair-parts documents do not need to be uploaded again. The service and repair-parts copies still require exact official-source confirmation. Additional documents should be added only to close a specific evidence gap and must remain in controlled private storage unless publication rights are recorded.

## Explicitly deferred or excluded

The following do not belong in the pilot unless a later approved scope change establishes a demonstrated diagnostic or training need:

- general photorealistic 3D equipment models;
- a complete thermodynamic or refrigerant-cycle physics engine;
- AR equipment recognition;
- live equipment control, unattended sensor collection, or IoT commissioning;
- automatic repair authorization;
- technician dispatching, invoicing, payment, or inventory-management systems;
- broad multi-manufacturer ingestion before the pilot quality gates pass;
- unrestricted crawling or collection from unapproved sources;
- publication of complete restricted manuals or copied source diagrams; and
- AI answers based only on model memory, general web content, or unreviewed extraction.

## Expansion candidates

After the pilot demonstrates diagnostic accuracy and safe use, candidates include:

- additional equipment families and manufacturers;
- offline-capable field access;
- nameplate model and serial OCR with mandatory technician confirmation;
- user-authorized read-only import from compatible meters and probes;
- authorized equipment and component photographs;
- voice-assisted case intake with visible confirmation;
- approved parts applicability and service-bulletin alerts;
- team escalation and remote lead-technician review;
- historical case and known-good comparison with exact equipment applicability;
- additional virtual instruments;
- instructor analytics and competency reporting; and
- narrowly targeted 3D or AR teaching aids with a validated learning benefit.

## Product success measures

- Percentage of technical claims with exact provenance and approval state
- HVAC reviewer acceptance rate and correction rate
- Safety-stop and escalation correctness
- Time and number of steps required to reach the next discriminating test
- Diagnostic-path agreement with reviewed manufacturer procedures
- Rate of unsupported or misapplied guidance, with a target of zero publication
- Case-summary completeness and traceability
- Learner improvement across reviewed training scenarios
- Knowledge-package freshness and revision coverage
