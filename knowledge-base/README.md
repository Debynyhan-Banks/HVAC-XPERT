# Knowledge Package Access

## Personal entries

P-001 writes owner-entered equipment, fault, measurement, and diagnostic-branch
records to the ignored local directory:

```text
knowledge-base/private/personal-entries/
```

Each record conforms to `schemas/personal-knowledge-entry.schema.json`. Personal
entries remain outside Git and do not activate deterministic guidance automatically.
Confirmed actionable entries are candidates for a separate reviewed rule step.
Corrections create a new record with `supersedes_entry_id`; the prior record remains
available for personal audit and is marked non-current by the local search service.

## Personal field cases

P-002 writes explicitly saved field-case snapshots to the ignored local directory:

```text
knowledge-base/private/cases/
```

The server evaluates each case through the deterministic diagnostic engine before
storage. Only safety-acknowledged field cases with at least one technician-entered
result are accepted. Search is local and scans private entry and case JSON; no cloud
database, public index, or external service receives the records.

Technically approved manufacturer records remain private while source-rights and publication authorization are unresolved. Internal tools load them through `scripts/private_package_gate.py`; they must not read private JSON files directly.

## Internal load

```bash
python3 scripts/private_package_gate.py sources/private/review/RUN-ASXS6-20260802-001/package --mode internal
```

The loader verifies the private path boundary, package and decision status, technical-review identity and timestamp, model revision, record counts, unique identifiers, provenance, document references, and absence of embedded source binaries.

## Approved extensions

New facts do not modify an already approved package. They enter a separate `KNOWLEDGE_EXTENSION` package that identifies its approved base package and begins in `PENDING_TECHNICAL_REVIEW` status.

After a reviewer explicitly approves every extension assertion, internal tools compose it with the base package:

```bash
python3 scripts/private_package_gate.py \
  sources/private/review/RUN-ASXS6-20260802-001/package \
  --extension sources/private/review/RUN-ASXS6-20260802-002/package \
  --mode internal
```

Pending, mismatched, partially reviewed, or conflicting extensions fail closed. Extension commands and measurements must reference known components, states, and measurements from the approved package set.

The approved composed package can be inspected through `scripts/run_simulator.py`.
See `simulator/README.md` for state-listing, diagnostic-listing, and manual phase-selection commands.

## Public export gate

```bash
python3 scripts/private_package_gate.py sources/private/review/RUN-ASXS6-20260802-001/package --mode public
```

Public export fails unless all of these conditions are explicit:

- Package status is `APPROVED_FOR_PUBLICATION`.
- `publication_allowed` is `true`.
- Technical review is accepted.
- Legal hold is `false`.
- Publication review is accepted with an approver and timestamp.

Missing, false, malformed, or contradictory values block export.
