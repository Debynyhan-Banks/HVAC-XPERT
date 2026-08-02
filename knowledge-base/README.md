# Knowledge Package Access

Technically approved manufacturer records remain private while source-rights and publication authorization are unresolved. Internal tools load them through `scripts/private_package_gate.py`; they must not read private JSON files directly.

## Internal load

```bash
python3 scripts/private_package_gate.py sources/private/review/RUN-ASXS6-20260802-001/package --mode internal
```

The loader verifies the private path boundary, package and decision status, technical-review identity and timestamp, model revision, record counts, unique identifiers, provenance, document references, and absence of embedded source binaries.

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
