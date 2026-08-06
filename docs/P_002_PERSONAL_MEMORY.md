# P-002 Searchable Personal Memory

## Outcome

P-002 turns private P-001 records and completed diagnostic cases into a searchable local memory. The localhost interface can find prior knowledge, start an immutable correction, review recent field cases, and explicitly save a completed deterministic field case for later reference.

The workflow does not publish records, edit historical entries in place, activate personal entries as deterministic rules, generate equipment readings, or send private data to a cloud service.

## Access checklist

| Requirement | P-002 decision |
| --- | --- |
| Documents or evidence | Existing private personal entries and approved local diagnostic packages |
| Owner technical decisions | Search terms, whether to create a correction, and whether a completed field case should be retained |
| API, cloud, database, or hardware | None |
| Credentials | None |
| Paid services or material cost | None |
| Privacy boundary | Entries remain under `knowledge-base/private/personal-entries/`; cases remain under `knowledge-base/private/cases/` |
| Source-rights boundary | Search returns structured private facts and references; it does not copy source PDFs or publicize manufacturer content |
| Acceptance boundary | Owner confirms that private search, correction prefill, and explicit case saving are understandable |
| Current blocker | No implementation blocker; owner acceptance remains required before P-002 is complete |

## Search contract

Search performs a bounded local scan of private JSON records. It can match nested text such as:

- model, revision, manufacturer, brand, title, fault code, symptom, component, and entry details;
- case complaint, fault code, test result, technician identity, package lineage, and deterministic outcome; and
- recent entries or cases when no search term is supplied.

Search does not establish technical truth or change confidence. Invalid, mismatched, or symlinked private records fail closed instead of entering results.

## Correction contract

A correction never overwrites the original entry. The form preloads the selected current record, and saving creates a new entry with `supersedes_entry_id` pointing to the prior entry. Search identifies the new record as current and the prior record as superseded. A record that already has a correction cannot be corrected a second time directly; the owner corrects the current replacement instead.

Corrections must preserve the entry kind and exact model identity. They may update revision applicability, owner-authored details, evidence context, confidence, and safety through the same P-001 validation rules.

## Case-history contract

The browser can save only the exact case request currently evaluated by the server. Storage requires:

- `FIELD` mode;
- required safety acknowledgement;
- at least one explicitly technician-entered result;
- exact approved diagnostic-path and package lineage; and
- a canonical deterministic evaluation and outcome produced by the server.

Saved cases distinguish technician observations from deterministic evaluation. They do not imply connected-instrument input, autonomous diagnosis, repair authorization, or manufacturer publication approval.

## Local storage

P-002 continues the one-file-per-record JSON approach accepted in ADR-021 and ADR-022. Directories are created with owner-only permissions, records are written atomically with owner read/write permissions, and both paths are ignored by Git. A database or search index remains deferred until actual personal usage establishes a scale, concurrency, or cross-device requirement.

## Owner acceptance

1. Run the private localhost application.
2. Search for the representative P-001 model or fault and confirm the expected record appears.
3. Select `Use as correction`, verify that the form is prefilled, then cancel unless a real correction is needed.
4. On an appropriate real field case, complete the bounded diagnostic workflow and select `Save case to private history`.
5. Search the model, fault, complaint, or technician name and confirm that the saved case appears.

Do not create a fake field case only to satisfy acceptance. Software fixtures validate persistence; real personal history should represent real owner-entered field work.

## Validation

Focused tests cover search across nested private fields, correction lineage, current-versus-superseded status, duplicate correction rejection, owner-only case storage, newer case updates, field/safety/result requirements, server-side evaluation, browser integration, and static-asset privacy.
