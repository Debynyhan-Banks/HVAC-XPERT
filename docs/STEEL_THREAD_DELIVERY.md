# Steel-Thread Delivery Protocol

## Decision

HVAC XPERT uses steel threads as its implementation method. Each steel thread is a thin, complete, reviewable workflow that crosses the evidence, data-contract, deterministic-logic, application, validation, technical-review, and repository-publication layers.

The phase gates in `ROADMAP.md` remain mandatory governance and maturity controls. Steel threads do not bypass source, legal, safety, validation, or publication requirements. They prevent the project from building large horizontal subsystems that do not yet work together for a technician.

## Standard thread path

Every product thread follows the applicable portions of this path:

`authorized evidence -> structured assertion -> HVAC approval -> versioned knowledge package -> deterministic rule -> technician interface -> acceptance test -> reviewed outcome`

Unknown or unsupported steps fail closed. A thread may use synthetic fixtures for software validation, but manufacturer-facing behavior requires applicable approved evidence before technical acceptance.

## Planned steel threads

| Thread | Outcome | Status | External access before start |
| --- | --- | --- | --- |
| `ST-000` | Governance, source controls, schemas, private ingestion, and approval gates | Foundation available; legal work ongoing | No API; manufacturer permission remains external |
| `ST-001` | One approved pilot model loads into the deterministic reference simulator, virtual reference meter, and SVG topology | Complete for current bounded records | No API |
| `ST-002` | One complaint completes the field diagnostic case loop from intake through summary or escalation | Complete for bounded E24 pilot path | No API |
| `ST-003` | The same approved case runs as a scored deterministic training scenario | Implementation candidate; instructor/HVAC acceptance pending | No API; requires instructor and HVAC acceptance |
| `ST-004` | AI explains the approved case evidence with citations and explicit uncertainty | Pending | AI provider access and approved retrieval records |
| `ST-005` | Reviewers author, review, version, and publish procedures and scenarios through a controlled portal | Pending | Authentication and reviewer-role decisions |
| `ST-006` | Additional complaints and models in the approved pilot family reuse the same workflow | Pending | Additional authorized evidence as gaps are identified |
| `ST-007` | The product is hardened for persistent, mobile, offline-capable field use and lead-tech escalation | Pending | Hosting, database, identity, security, and support decisions |
| `ST-008` | Confirmed nameplate OCR and user-authorized read-only instrument imports reduce manual entry | Deferred until pilot proof | Vendor SDK or API access, test hardware, and privacy review |
| `ST-009` | Additional manufacturers enter through the same governed acquisition and diagnostic workflow | Deferred until pilot proof | Manufacturer agreements, licensed feeds, or approved collection access |

## ST-003 bounded objective

This thread is deliberately narrow:

- reuse the exact approved `ST-002` model, revision, complaint, safety boundary, test, expected result, and result branches;
- generate one deterministic divergent observation labeled `SIMULATED` and never represent it as a field measurement;
- hide the observation, hint, and response controls until safety acknowledgement;
- hide target answers and branch guidance until the learner submits both an interpretation and disposition;
- award 50 points for interpretation and 50 for disposition, subtract 10 points for a requested hint, and pass at 80 points;
- expose the scoring breakdown, supported answers, approved branch guidance, remediation, package lineage, and source pages after submission; and
- validate equal-input replay determinism with synthetic and approved private-package acceptance tests.

It does not require an AI API, database service, cloud hosting, connected meter, new crawler, new source upload, or public manufacturer records. It is not secure examination software, learner-history storage, a manufacturer certification, or repair authorization. AI explanation and persistent production storage remain later threads.

## Thread anatomy

### 1. Access checklist

Before implementation begins, the contributor states:

- documents or evidence required;
- user technical decisions required;
- API, database, cloud, vendor, or hardware access required;
- legal, source-rights, security, or publication approvals required;
- expected paid accounts or material costs;
- reviewer actions and acceptance boundary; and
- current blockers.

Credentials are never requested in chat or committed to Git. When required, they are supplied through ignored local environment files, repository secrets, or approved cloud secret storage.

### 2. Evidence boundary

- Identify the exact model and revision.
- List the approved records the thread may use.
- Record missing, conflicting, and intentionally excluded evidence.
- Prevent a prior approval from silently expanding to new assertions.

### 3. Data contracts

- Add or extend canonical JSON schemas.
- Validate identifiers, references, units, states, and provenance.
- Preserve evidence classes such as manufacturer fact, technician observation, deterministic evaluation, simulation result, and AI hypothesis.

### 4. Deterministic behavior

- Implement only approved comparisons, state changes, and branches.
- Keep unsupported behavior unknown.
- Make equal inputs produce equal outputs.
- Fail closed on conflicts, invalid applicability, or missing safety information.

### 5. Technician experience

- Deliver the smallest useful end-to-end interface.
- Present one primary next action when the evidence supports one.
- Keep safety, expected result, actual result, evaluation, and source visibly distinct.
- Provide stop and escalation paths.

### 6. Validation and review

- Add focused unit, integration, private-package, and acceptance tests.
- Check that no private source binary or record enters Git.
- Obtain HVAC technical review for new technical assertions or behavior.
- Preserve legal and publication holds independently from technical acceptance.

### 7. Repository publication

- Update `CURRENT_STATE.md`.
- Commit only the intended files.
- Push the focused branch.
- Open a pull request with validation results and the remaining blockers.
- Provide the reviewer a direct merge link.

## Definition of done

A steel thread is complete only when:

- its bounded user outcome works end to end;
- every manufacturer-derived fact has exact provenance and approval status;
- actual, reference, deterministic, simulated, and AI information remain distinguishable;
- safety and unsupported paths fail closed;
- the most specific tests and applicable broader tests pass;
- required HVAC acceptance is recorded;
- private documents, credentials, and generated private records remain outside Git;
- continuity documentation is current; and
- the intended commit is pushed and available through a pull request or recorded merged change.

Completing only a schema, API, UI mockup, extraction script, or AI prompt does not complete a product steel thread unless it is the explicitly bounded enabling thread and its integration consumer is identified.

## Change control

If a thread discovers missing evidence, access, or safety requirements, narrow or stop the thread rather than inventing a workaround. New horizontal infrastructure is justified only when the active steel thread requires it and the decision is recorded. Deferred integrations stay deferred until the pilot proof measures in `COMPETITIVE_POSITIONING.md` are reviewed.
