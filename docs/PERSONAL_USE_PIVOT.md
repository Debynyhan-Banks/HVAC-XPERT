# Personal-Use Product Pivot

## Decision

HVAC XPERT is now developed first as a single-owner, local-first HVAC/R field copilot and personal training tool for `Debynyhan-Banks`. Public SaaS, multi-tenant collaboration, manufacturer-content publication, and broad commercial distribution are deferred.

This pivot does not discard the existing deterministic engine, private knowledge-package boundary, source traceability, safety controls, field case workflow, topology reference, virtual reference meter, or training replay. It changes which product outcome is optimized first.

## Personal product outcome

The application should help its owner during and after real service calls to:

- identify equipment and revision;
- find relevant fault, component, measurement, and wiring facts quickly;
- follow one safe, evidence-supported diagnostic test at a time;
- record actual observations without confusing them with references or simulations;
- compare results deterministically where a supported rule exists;
- stop or escalate when the personal knowledge base does not support another step;
- preserve a searchable local service history; and
- practice the same diagnostic reasoning with clearly labeled simulations.

## Operating model

- One owner and primary user
- Local-first and private by default
- Manual document upload and manual fact entry
- No crawler or automated manufacturer-site collection
- No public redistribution of manuals, copied diagrams, or private knowledge packages
- No live equipment control or fabricated field readings
- No requirement for cloud hosting, multi-tenant authentication, billing, or organization administration

Personal use reduces the product's operational and distribution exposure but does not itself establish permission to copy or redistribute protected content. Manufacturer wording, page images, diagrams, and source binaries remain private. The export guard remains fail closed.

## What stays

- Deterministic diagnostic-case and training engines
- One-next-test-at-a-time interaction
- Explicit safety acknowledgement
- Exact model and revision boundaries
- Reference, field, deterministic, simulated, and AI evidence separation
- Unknown and conflicted states
- Source document and page references
- Private runtime loading and localhost-only defaults
- Original semantic diagrams rather than copied source artwork

## What simplifies

The owner performs source comparison, technical confirmation, and field confirmation. Daily use should expose a small confidence vocabulary:

| Personal status | Meaning |
| --- | --- |
| `UNVERIFIED` | Entered or imported but not yet compared with a trusted source or field result |
| `MANUAL_CONFIRMED` | The owner compared the fact with a legitimately accessed private source |
| `FIELD_CONFIRMED` | The owner observed the behavior or result on an applicable real service call |
| `CONFLICTED` | A source, revision, or field observation disagrees and the fact must not drive deterministic guidance |

The canonical validation ladder and audit fields remain available underneath these labels for compatibility and traceability. Separate instructor, publisher, and content-administrator workflows are deferred rather than required for daily personal entry.

## Product priorities

1. Fast manual entry of one model, fault, measurement, or diagnostic branch in ten minutes or less.
2. Search by model, fault code, symptom, component, or recent case.
3. Local case history with field-confirmation notes and exact applicability.
4. Phone-first, offline-capable use without exposing the private knowledge base to a public network.
5. Breadth driven by equipment actually encountered on service calls.
6. Optional retrieval-grounded AI only after the local search and deterministic workflow are useful without it.

## Deferred product work

- Automated crawling or bulk manufacturer ingestion
- Public manufacturer-content library
- Multi-tenant SaaS architecture
- Team roles, organization administration, and customer billing
- Instructor portal and enterprise analytics
- Public knowledge-package publication
- Broad manufacturer expansion disconnected from real service needs
- AI model training on manufacturer PDFs
- General-purpose 3D equipment rendering
- Connected instruments, live control, and automatic repair authorization

## Repository and data boundary

The GitHub repository currently contains code, schemas, tests, governance records, and bounded reviewer documentation. Private PDFs and private packages remain excluded by `.gitignore` and must never be committed.

Making the repository private is recommended for the personal-use direction but remains an explicit owner action outside this documentation change. Until visibility changes, no new manufacturer-derived private record, copied procedure, page image, diagram, credential, case history, customer information, or equipment-site detail may enter Git.

Changing a repository from public to private does not retract copies that may already exist. Review GitHub's current visibility-change consequences before making that change: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility>.

## Personal success measures

- Time to add a useful entry after a service call
- Time to find the next applicable test
- Percentage of entries with exact model, revision, and source or field context
- Number of entries promoted from `UNVERIFIED` to `MANUAL_CONFIRMED` or `FIELD_CONFIRMED`
- Number of conflicts caught before guidance is shown
- Percentage of cases that stop or escalate rather than invent an unsupported step
- Repeat use on actual service calls
- Successful encrypted backup and restore of the personal knowledge base

## Re-productization boundary

A future commercial product may provide the software platform while customers supply and govern their own legitimately obtained content. That direction requires a new scope decision covering hosting, identity, customer data, security, support, source rights, and public or customer distribution. Personal field history and private manufacturer content do not become commercial seed data automatically.
