# Current State

## Current phase

Phase 0 — Governance and foundation

## Current objective

Complete source legal/access review and prepare the controlled manufacturer-document acquisition pipeline for the pilot family.

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
- All 48 Package 3 topology assertions remain `LEVEL_1_AI_EXTRACTED` and `PENDING` until a separate HVAC technical decision
- Topology extraction and review tooling pull request #11 merged as commit `8b79be3`
- Private simulator command cards now translate approved enum values into technician-readable behavior while preserving the raw source definition and explicitly identifying unspecified exact settings
- Diagnostic meter now provides a direct applicable-test selector, and diagnostic table rows expose visible inspect actions instead of relying on text that only appears clickable

## In progress

- Written collection and extraction permission request
- Copyright, storage, factual-extraction, and derivative-use determination
- Confirmation of exact official service, parts, and specification asset URLs
- Manual-upload ingestion design using authorized documents or synthetic fixtures
- HVAC technical review of private topology extension `RUN-ASXS6-20260804-003`

## Blockers

- No pilot source is approved for automated collection
- Posted terms prohibit automated monitoring or copying of covered sites
- Storage, factual-extraction, and derivative-publication rights remain unresolved
- Exact official URLs for the service manual and parts catalog are unconfirmed
- Technically approved records cannot enter the public repository while the legal hold remains
- Transition timing and automatic transition conditions remain unknown because the cooling-flow chart does not specify them
- Package 3 topology cannot enter simulator runtime or drive an SVG schematic until all 48 assertions receive a separate technical decision

## Next action

Review private topology extension `RUN-ASXS6-20260804-003` against product-specification page 50 and the equivalent service/install drawings. Confirm the X1M L1/L2 mapping, A1P UO/VO/WO to M1C U/V/W mapping, positional X108A-to-M1F mapping, signal classifications, unknown wire colors, and bounded exclusions before creating a complete technical decision.

After the work unit passes validation, update this file, commit only the intended non-private files, and push the current branch to `origin`.

## Pilot target

- Organization: Daikin Comfort Technologies
- Brands: Amana and Goodman
- Family: S-Series inverter outdoor units
- Model: `ASXS6S4810AA`

## Last updated

2026-08-04
