# Current State

## Current phase

Phase 0 — Governance and foundation

## Current objective

Complete instructor and HVAC acceptance of the first deterministic training replay while preserving the source-rights, safety, and publication gates.

## Completed

- Product mission and MVP boundaries recorded
- Governance and continuity documents created
- Canonical manufacturer knowledge schemas created
- Provenance and validation ladder defined
- Pilot manufacturer source registry created
- Repository responsibility boundaries established
- Official Daikin, Goodman, Amana, and Daikin City source entry points identified
- North American terms and robots policies reviewed
- Crawler prohibition and manual-ingestion fallback documented
- Manufacturer permission-request draft created
- Four pilot PDFs manually imported into the private document vault
- SHA-256 fingerprints, page counts, stable document IDs, and canonical manifests created
- Product specification and installation documents matched to official Daikin CDN URLs
- Service and repair-parts documents recorded as distributor-hosted copies pending official-source matching
- Completion protocol now requires validation, a focused commit, and a GitHub push after every completed work unit
- `Debynyhan-Banks` assigned as the pilot HVAC/R technical reviewer
- First controlled extraction run created as private package `RUN-ASXS6-20260802-001`
- Model identity, nomenclature, ratings, and dimensions mapped with page-level provenance
- Sixteen major component records mapped to the exact M6 parts-catalog applicability code
- Fifty-one outdoor fault-code index records mapped from service-manual pages 45-48
- Three applicable wiring-diagram source locations inventoried without copying diagrams into Git
- Private review package passed referential, page-range, privacy-boundary, and canonical schema validation
- `Debynyhan-Banks` accepted all 74 page-cited assertions in `RUN-ASXS6-20260802-001`
- Accepted assertions advanced to `LEVEL_4_TECHNICIAN_REVIEWED`
- Three wiring pages accepted as equivalent applicable renderings of the 3.5-5.0 ton outdoor AC drawing
- Technical approval audit recorded while retaining the package under legal hold
- Private approved-package loader implemented with model, revision, count, provenance, decision, and private-path validation
- Fail-closed publication gate implemented with separate technical, legal-hold, and publication-approval requirements
- Seven synthetic gate tests pass for valid loading, status, provenance, revision, path, legal hold, and explicit publication approval
- Approved pilot package loads successfully for internal use while public mode is rejected as required
- Deterministic simulator core implemented with immutable model, revision, component, fault, and effect definitions
- Explicit power and operation-requested inputs produce stable engine-level statuses without inferring manufacturer behavior
- Manual fault activation accepts only exact approved fault codes and applies only declared simulator effects
- Matching effects combine deterministically while conflicting active effects fail closed
- Ten synthetic simulator tests pass for input validation, unknown-state preservation, fault activation, clearing, effects, definition validation, conflicts, and replay determinism
- Deterministic simulator pull request #5 merged and the simulator foundation review was confirmed by `Debynyhan-Banks`
- Immutable `KNOWLEDGE_EXTENSION` packages implemented so new facts cannot inherit a base package's prior approval
- Extension validation enforces base-package identity, model revision, record counts, provenance, and component/state/measurement references
- Approval tooling now applies explicit decisions to operating-state and measurement records
- Private extension `RUN-ASXS6-20260802-002` created with six cooling-flow phases and six diagnostic measurements supported by fifteen page-cited assertions
- Candidate pages 5, 6, 10, 15, 16, 17, 21, and 72 visually reviewed during extraction
- `Debynyhan-Banks` accepted all fifteen assertions in `RUN-ASXS6-20260802-002` at `2026-08-02T23:00:09Z`
- Extension assertions advanced to `LEVEL_4_TECHNICIAN_REVIEWED` while retaining the legal and publication hold
- Approved base and extension compose successfully at runtime as 16 components, 51 faults, 6 operating states, and 6 measurements
- Deterministic simulator now exposes immutable approved operating-state and diagnostic-measurement definitions
- Exact manual phase selection applies only approved component commands and never advances automatically
- State/fault conflicts on the same component property fail closed
- Local simulator runner lists approved phases and diagnostics or emits a deterministic JSON snapshot
- Real-package smoke test selects steady cooling and applies the two approved compressor and outdoor-fan commands
- Ten package-gate tests, three extension-review tests, seventeen simulator tests, and two runner tests pass together
- Private local browser application implemented over deterministic simulator snapshots
- Local server binds only to `127.0.0.1`, validates local host headers, disables cross-origin access, and sends restrictive browser security headers
- Browser interface provides model counts, exact manual phase selection, explicit power/request controls, searchable fault activation, component commands/effects, and applicable diagnostic definitions
- Every snapshot request creates a fresh simulator instance, preserving deterministic replay and preventing hidden phase persistence
- Static browser assets contain no pilot model identifier or private package path; approved records load only through the ignored private vault at runtime
- Eight private-application tests cover definitions, deterministic snapshots, exact identifiers, strict input validation, loopback binding, host filtering, and static-asset privacy
- Private local application pull request #9 merged as commit `5516eb8`
- Simulator source references now preserve validation level, outcome, reviewer, and review timestamp
- Reference-only virtual diagnostic meter implemented with approved meter mode, lead points, expected value or range, interpretation, procedure, safety category, and source pages
- Meter interface exposes human-readable technician validation and explicit manufacturer-verification-pending status
- The meter fails closed if the server does not declare reference-definition-only measurement behavior and never generates a live or simulated reading
- Real approved-package browser test verified the `197–253 VAC` L1/L2 supply-voltage definition, energized-line-voltage category, approved procedure, technician reviewer, and service-manual page 15 traceability
- Reference-only diagnostic meter pull request #10 merged as commit `ea2ba67`
- Assigned HVAC technical reviewer confirmed the private interface and diagnostic meter were fully reviewed and approved
- Topology review tooling now validates canonical connector, pin, node, and connection fields, IDs, enums, counts, component references, bidirectional connector/pin and pin/node membership, node endpoints, and approval metadata
- Canonical pin signal types now distinguish inverter-generated three-phase motor output from incoming line-voltage AC
- Private pending extension `RUN-ASXS6-20260804-003` created with 6 connectors, 17 pins, 17 nodes, and 8 explicit connections for the X1M supply, M1C compressor, and M1F fan paths
- Package 3 uses product-specification page 50 as primary provenance and visually cross-checks the accepted equivalent diagrams on service page 76 and installation page 36
- Unlabeled X108A and M1F terminals remain positional `LEFT`, `CENTER`, and `RIGHT` identifiers; wire colors remain `null` where the diagram does not label them
- Topology extraction and review tooling pull request #11 merged as commit `8b79be3`
- Private simulator command cards now translate approved enum values into technician-readable behavior while preserving the raw source definition and explicitly identifying unspecified exact settings
- Diagnostic meter now provides a direct applicable-test selector, and diagnostic table rows expose visible inspect actions instead of relying on text that only appears clickable
- Private simulator UI improvement pull request #12 merged as commit `90d2de3`
- AI-assisted Package 3 pre-review visually compared product-specification page 50, service page 76, and installation page 36 and found no discrepancy in the bounded supply, compressor, fan, protective-earth, or exclusion assertions
- Package 3 reviewer guide now records the 48-assertion decision boundary without copying private PDFs, rendered pages, or private records into the repository
- Approval tooling now replaces Package 3's pending review actions with a complete accepted decision summary instead of leaving stale reviewer instructions after approval
- Assigned HVAC/R technical reviewer `Debynyhan-Banks` explicitly accepted all 48 Package 3 topology assertions and the documented bounded exclusions at `2026-08-04T14:29:12Z`
- All Package 3 assertions advanced to `LEVEL_4_TECHNICIAN_REVIEWED` with outcome `ACCEPTED`; the private package now has status `TECHNICALLY_APPROVED_LEGAL_HOLD`
- Package 3 retains `publication_allowed: false`, and the approval does not authorize source redistribution, automated collection, or public publication
- Package 3 technical-review pull request #13 merged as commit `019fc02`
- Private package gate now composes approved operating-state, measurement, connector, pin, node, and connection records across both extensions with duplicate, enum, component, endpoint, and bidirectional membership validation
- Real three-package composition loads 16 components, 51 faults, 6 operating states, 6 measurements, 6 connectors, 17 pins, 17 nodes, and 8 explicit connections
- Private browser definitions expose topology only as `REFERENCE_DEFINITION_ONLY`
- Reference-only SVG topology map renders all eight explicit wires using documented conductor colors, preserves unknown fan-wire colors, identifies the standalone X1M PE bounded node, and displays reviewer and source-page traceability
- Real-package browser verification found eight rendered connection rows, one standalone bounded node, correct Package 3 counts, and no browser warnings or errors
- Combined product scope now preserves the original training and simulation mission while adding an evidence-grounded lead-technician field workflow
- Product priorities now favor reviewed two-dimensional diagnostic diagrams, manual field observations, deterministic evaluation, and traceable case summaries over general 3D rendering or autonomous equipment control
- AI grounding is defined as retrieval from applicable approved knowledge packages; foundation-model training on manufacturer PDFs is not required and cannot replace provenance or review
- Field, training, deterministic, reference, and AI evidence classes are explicitly separated
- Bounded diagnostic case states, next-test requirements, result evaluation, hypothesis handling, escalation, case summary, and pilot acceptance criteria are documented
- Existing pilot documents do not require duplicate upload; additional private documents are required only to close identified evidence gaps
- Combined product scope and diagnostic workflow merged through pull request #15 as commit `07d2a02`
- Competitive review positions the pilot around one complete model- and revision-specific diagnostic case rather than document breadth, connected hardware, general 3D content, or a large course catalog
- Field experience priorities now require one primary next test at a time while keeping detailed evidence directly available
- Nameplate OCR, offline access, read-only instrument import, remote lead-technician review, historical comparison, and approved bulletin or parts alerts are explicitly deferred until after pilot proof
- Competitive positioning and priority amendment merged through pull request #16 as commit `2ca4a10`
- Roadmap execution now uses steel threads while preserving the existing phases as governance and maturity gates
- Before-thread access checklists now identify required documents, user decisions, credentials, external services, legal approvals, reviewer actions, expected costs, and blockers without requesting secrets in chat
- `ST-001` records the completed bounded model-to-reference-simulator workflow; `ST-002` implements the first bounded field diagnostic case loop without an external API
- Canonical diagnostic-path and diagnostic-case schemas now separate approved path definitions from field or training case records
- Private-package and review gates now validate diagnostic-path dependencies, exact fault and measurement references, safety acknowledgements, ordered steps, complete deterministic branches, provenance, and independent approval status
- Stateless diagnostic case engine now requires exact fault-code entry, required safety acknowledgement, one approved test at a time, chronological technician-entered field results, and deterministic fail-closed branch evaluation
- Field and training result sources remain separated; connected or imported instrument readings stay deferred
- Private browser interface now provides complaint context, safety screening, next-test rationale and procedure, technician result entry, deterministic outcome, and traceability without implying equipment measurement or repair authority
- Synthetic engine and application fixtures validate the complete software loop while pending manufacturer-derived paths remain excluded from runtime composition
- Private Package 4 `RUN-ASXS6-20260804-004` defines one bounded `E24` high-pressure-switch-continuity path with four page-cited assertions, one test, and three stop-or-escalate branches
- Assigned HVAC/R technical reviewer `Debynyhan-Banks` accepted all four Package 4 assertions and bounded exclusions at `2026-08-05T00:24:19Z`
- All Package 4 assertions advanced to `LEVEL_4_TECHNICIAN_REVIEWED`; the package status is `TECHNICALLY_APPROVED_LEGAL_HOLD` and `publication_allowed` remains false
- Real four-package composition loads 16 components, 51 faults, 6 operating states, 6 measurements, 6 connectors, 17 pins, 17 nodes, 8 explicit connections, and 1 diagnostic path
- Real-package browser acceptance verified the E24 complaint, de-energized safety gate, PCB-side continuity test, continuity/no-continuity/unknown choices, deterministic no-continuity escalation, visible actual-versus-expected evidence, technician identity, package lineage, deduplicated source-page traceability, and a clean browser console
- `ST-002` is complete for the bounded E24 pilot path; unsupported diagnosis, repair authorization, connected instruments, persistence, and publication remain excluded
- `ST-003` deterministic training contracts define answer-redacted replay definitions and safety-gated attempt snapshots separately from field diagnostic cases
- Training replay reuses the approved diagnostic case engine in `TRAINING` mode and always labels generated observations as `SIMULATED`
- The first eligible replay deterministically creates a divergent observation from the approved expected result without AI or randomness
- Safety acknowledgement is required before the observation, hint, or learner controls are exposed
- Target interpretation, target disposition, approved branch guidance, score, and remediation remain hidden until both learner answers are submitted
- The transparent pilot rubric awards 50 points for interpretation, 50 for disposition, subtracts 10 for hint use, and passes at 80 points
- Focused synthetic tests cover answer redaction, safety gating, qualitative and numeric simulation, full/partial/incorrect scoring, hint penalty, remediation, request validation, and equal-input determinism
- Private browser interface now presents the training replay, clearly distinguishes simulation from live or technician-entered evidence, and exposes post-submission scoring, remediation, package lineage, and source traceability
- `ST-003` remains an implementation candidate until the assigned reviewer accepts the documented training behavior assertions and bounded exclusions

## In progress

- Written collection and extraction permission request
- Copyright, storage, factual-extraction, and derivative-use determination
- Confirmation of exact official service, parts, and specification asset URLs
- Manual-upload ingestion design using authorized documents or synthetic fixtures
- Instructor and assigned HVAC/R technical review of the `ST-003` deterministic replay and pilot scoring rubric

## Blockers

- No pilot source is approved for automated collection
- Posted terms prohibit automated monitoring or copying of covered sites
- Storage, factual-extraction, and derivative-publication rights remain unresolved
- Exact official URLs for the service manual and parts catalog are unconfirmed
- Technically approved records cannot enter the public repository while the legal hold remains
- Transition timing and automatic transition conditions remain unknown because the cooling-flow chart does not specify them

## Next action

Merge the `ST-003` implementation pull request, run the reviewer exercise in `docs/ST_003_TECHNICAL_REVIEW.md`, and record instructor/HVAC acceptance or requested revisions. No external API, new document upload, cloud service, database, or hardware access is required.

After the work unit passes validation, update this file, commit only the intended non-private files, and push the current branch to `origin`.

## Pilot target

- Organization: Daikin Comfort Technologies
- Brands: Amana and Goodman
- Family: S-Series inverter outdoor units
- Model: `ASXS6S4810AA`

## Last updated

2026-08-04
