# Controlled Extraction

Raw extraction and unreviewed sourced assertions are restricted data. They remain under the ignored `sources/private/review/` tree while technical review is pending. The public repository contains only extraction tooling, validation logic, approved knowledge records, and non-sensitive workflow state.

## Pilot review workflow

1. Generate a private review package from manually supplied, authorized source documents.
2. Keep every extracted assertion at `LEVEL_1_AI_EXTRACTED` with outcome `PENDING`.
3. Validate record structure, source document IDs, page ranges, model applicability, and private-storage boundaries.
4. Have the assigned technical reviewer compare every assertion to its cited PDF page.
5. Record `ACCEPTED`, `REVISED`, `REJECTED`, or `CONFLICTED` with reviewer identity, timestamp, and notes.
6. Promote only accepted or revised records that pass the publication gate.

Complete-package approval is applied from a private decision record:

```bash
python3 scripts/apply_review_decision.py sources/private/review/RUN-ASXS6-20260802-001/package sources/private/review/RUN-ASXS6-20260802-001/package/review-decision.json
```

Technical approval advances accepted assertions to `LEVEL_4_TECHNICIAN_REVIEWED`. It does not set `publication_allowed` while licensing, storage, or source-rights questions remain unresolved.

## Private package validation

```bash
python3 scripts/validate_review_package.py sources/private/review/RUN-ASXS6-20260802-001/package
```

Schema validation uses the canonical record contracts:

```bash
npx --yes --package ajv-cli@5.0.0 --package ajv-formats@3.0.1 ajv validate --spec=draft2020 -c ajv-formats -s schemas/equipment-model.schema.json -r schemas/common.schema.json -r schemas/provenance.schema.json -d sources/private/review/RUN-ASXS6-20260802-001/package/equipment-model.json
npx --yes --package ajv-cli@5.0.0 --package ajv-formats@3.0.1 ajv validate --spec=draft2020 -c ajv-formats -s schemas/component.schema.json -r schemas/common.schema.json -r schemas/provenance.schema.json -d 'sources/private/review/RUN-ASXS6-20260802-001/package/components/*.json'
npx --yes --package ajv-cli@5.0.0 --package ajv-formats@3.0.1 ajv validate --spec=draft2020 -c ajv-formats -s schemas/fault.schema.json -r schemas/common.schema.json -r schemas/provenance.schema.json -d 'sources/private/review/RUN-ASXS6-20260802-001/package/faults/*.json'
npx --yes --package ajv-cli@5.0.0 --package ajv-formats@3.0.1 ajv validate --spec=draft2020 -c ajv-formats -s schemas/provenance.schema.json -r schemas/common.schema.json -d 'sources/private/review/RUN-ASXS6-20260802-001/package/wiring/*.json'
```
