# Personal-Thread Delivery Protocol

The filename is retained for repository-link continuity; the active protocol is personal-thread delivery under ADR-020.

## Decision

HVAC XPERT uses personal threads as its active implementation method. Each personal thread is a thin, complete workflow that crosses the applicable private evidence, data-contract, deterministic logic, application, validation, owner review, and repository synchronization layers.

Personal threads do not bypass source, privacy, safety, validation, or export requirements. They prevent the project from building SaaS or ingestion infrastructure that does not improve the owner's field workflow. The original phase gates remain deferred controls for any future commercial or shared-use scope.

## Standard thread path

Every active thread follows the applicable portions of this path:

`private source or field context -> structured personal entry -> owner confirmation -> local knowledge -> deterministic rule -> field interface -> acceptance test -> owner outcome`

Unknown or unsupported steps fail closed. A thread may use synthetic fixtures for software validation, but personal manufacturer-facing guidance requires applicable confirmed evidence before owner acceptance.

## Active personal threads

| Thread | Outcome | Status | External access before start |
| --- | --- | --- | --- |
| `P-000` | Single-owner local-first scope and simplified governance | Complete; merged in PR #21 | No API, database, hardware, upload, or paid service |
| `P-001` | Ten-minute manual knowledge entry and personal confidence status | Implementation complete; owner acceptance pending | Existing private documents or field context only |
| `P-002` | Searchable private knowledge and local case history | Next after P-001 acceptance | Local storage decision; no cloud account required |
| `P-003` | Phone-first offline field use | Pending | Device/storage/security decisions; no public listener |
| `P-004` | Job-driven equipment and fault breadth | Pending | Private source or field context for each entry |
| `P-005` | Optional retrieval-grounded AI explanation | Deferred | Owner-supplied AI provider access if selected |
| `P-006` | Encrypted backup, restore, and owner-controlled export | Pending | Backup destination decision |
| `P-007` | Future customer-supplied-content platform evaluation | Deferred | New commercial, legal, security, and hosting scope |

## P-001 bounded objective

The next thread is deliberately narrow:

- one local manual-entry workflow;
- equipment identity and revision applicability;
- one of fault, measurement, or diagnostic-branch entry per submission;
- source document/page or field-context metadata;
- safety category where the entry can drive a test;
- owner-facing `UNVERIFIED`, `MANUAL_CONFIRMED`, `FIELD_CONFIRMED`, or `CONFLICTED` status;
- deterministic guidance limited to confirmed, non-conflicted entries; and
- focused schema, engine, privacy-boundary, and browser acceptance tests.

It does not require an AI API, cloud hosting, connected meter, crawler, public manufacturer records, or customer accounts. Persistent case history, phone packaging, AI explanation, and commercial workflows remain later personal threads.

## Thread anatomy

### 1. Access checklist

Before implementation begins, the contributor states:

- documents or evidence required;
- user technical decisions required;
- API, database, cloud, vendor, or hardware access required;
- privacy, source-rights, security, or export decisions required;
- expected paid accounts or material costs;
- owner actions and acceptance boundary; and
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
- Obtain explicit owner confirmation for new actionable technical assertions or behavior.
- Preserve export blocks independently from personal confirmation.

### 7. Repository synchronization

- Update `CURRENT_STATE.md`.
- Commit only the intended files.
- Push the focused branch.
- Open a pull request with validation results and the remaining blockers.
- Provide the owner a direct merge link.

## Definition of done

A personal thread is complete only when:

- its bounded user outcome works end to end;
- every manufacturer-derived fact has exact provenance and approval status;
- actual, reference, deterministic, simulated, and AI information remain distinguishable;
- safety and unsupported paths fail closed;
- the most specific tests and applicable broader tests pass;
- required owner acceptance is recorded;
- private documents, credentials, and generated private records remain outside Git;
- continuity documentation is current; and
- the intended commit is pushed and available through a pull request or recorded merged change.

Completing only a schema, API, UI mockup, extraction script, or AI prompt does not complete a personal thread unless it is the explicitly bounded enabling thread and its integration consumer is identified.

## Change control

If a thread discovers missing evidence, access, privacy, or safety requirements, narrow or stop the thread rather than inventing a workaround. New horizontal infrastructure is justified only when the active personal thread requires it and the decision is recorded. Deferred commercial integrations stay deferred until sustained personal field use supports a new scope decision.
