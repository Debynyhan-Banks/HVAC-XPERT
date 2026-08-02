#!/usr/bin/env python3

import hashlib
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_ROOT = PROJECT_ROOT / "sources" / "manifests"
VAULT_ROOT = PROJECT_ROOT / "sources" / "private" / "documents"


def sha256_file(file_path):
    digest = hashlib.sha256()
    with file_path.open("rb") as file_stream:
        for file_chunk in iter(lambda: file_stream.read(1024 * 1024), b""):
            digest.update(file_chunk)
    return digest.hexdigest()


def validate():
    failures = []
    document_ids = set()
    fingerprints = set()
    validated_count = 0

    for manifest_path in sorted(MANIFEST_ROOT.glob("*.json")):
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"Invalid manifest {manifest_path.name}: {error}")
            continue

        document_id = manifest.get("document_id")
        fingerprint = manifest.get("fingerprint", {}).get("sha256")
        expected_size = manifest.get("fingerprint", {}).get("file_size_bytes")

        if not document_id or not fingerprint:
            failures.append(f"Missing document identity in {manifest_path.name}")
            continue
        if document_id in document_ids:
            failures.append(f"Duplicate document ID: {document_id}")
        if fingerprint in fingerprints:
            failures.append(f"Duplicate fingerprint: {fingerprint}")
        document_ids.add(document_id)
        fingerprints.add(fingerprint)

        vault_path = VAULT_ROOT / document_id / f"{fingerprint}.pdf"
        if not vault_path.is_file():
            failures.append(f"Missing private PDF for {document_id}")
            continue
        if vault_path.stat().st_size != expected_size:
            failures.append(f"File size mismatch for {document_id}")
            continue
        if sha256_file(vault_path) != fingerprint:
            failures.append(f"SHA-256 mismatch for {document_id}")
            continue

        validated_count += 1

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"Validated {validated_count} private documents against their manifests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
