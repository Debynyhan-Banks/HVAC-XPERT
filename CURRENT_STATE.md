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
- All seventeen private-gate and simulator tests pass together

## In progress

- Written collection and extraction permission request
- Copyright, storage, factual-extraction, and derivative-use determination
- Confirmation of exact official service, parts, and specification asset URLs
- Manual-upload ingestion design using authorized documents or synthetic fixtures
- Deterministic simulator foundation using runtime-loaded private approved records

## Blockers

- No pilot source is approved for automated collection
- Posted terms prohibit automated monitoring or copying of covered sites
- Storage, factual-extraction, and derivative-publication rights remain unresolved
- Exact official URLs for the service manual and parts catalog are unconfirmed
- Technically approved records cannot enter the public repository while the legal hold remains
- Manufacturer-specific component commands, timing, transitions, measurements, and lockout behavior cannot be simulated until operating-state and measurement records are extracted and technically approved

## Next action

Extend the private extraction package and gate to load canonical operating-state and measurement records. Extract model- and revision-specific sequence facts from the private service and installation documents for `Debynyhan-Banks` to review; use synthetic fixtures until those facts are accepted.

After the work unit passes validation, update this file, commit only the intended non-private files, and push the current branch to `origin`.

## Pilot target

- Organization: Daikin Comfort Technologies
- Brands: Amana and Goodman
- Family: S-Series inverter outdoor units
- Model: `ASXS6S4810AA`

## Last updated

2026-08-02
