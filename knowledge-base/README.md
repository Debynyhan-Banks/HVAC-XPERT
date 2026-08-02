# Knowledge Package Access

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
