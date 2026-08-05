#!/usr/bin/env python3

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"

REQUIRED_GOVERNANCE_FILES = {
    "README.md",
    "PROJECT_CHARTER.md",
    "CURRENT_STATE.md",
    "ROADMAP.md",
    "DECISIONS.md",
    "RISKS.md",
    "DATA_GOVERNANCE.md",
    "SOURCE_POLICY.md",
    "VALIDATION_POLICY.md",
    "AI_HANDOFF.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE_REVIEW.md",
    "sources/source-registry.yaml",
}

REQUIRED_SCHEMAS = {
    "manufacturer.schema.json",
    "brand.schema.json",
    "equipment-family.schema.json",
    "equipment-model.schema.json",
    "document.schema.json",
    "document-source.schema.json",
    "component.schema.json",
    "connector.schema.json",
    "pin.schema.json",
    "node.schema.json",
    "connection.schema.json",
    "operating-state.schema.json",
    "measurement.schema.json",
    "fault.schema.json",
    "diagnostic-path.schema.json",
    "diagnostic-case.schema.json",
    "training-replay.schema.json",
    "training-attempt.schema.json",
    "personal-knowledge-entry.schema.json",
    "scenario.schema.json",
    "provenance.schema.json",
    "source-registry.schema.json",
    "common.schema.json",
}


def walk_references(value):
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key == "$ref" and isinstance(nested_value, str):
                yield nested_value
            yield from walk_references(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from walk_references(nested_value)


def validate():
    failures = []

    for relative_path in sorted(REQUIRED_GOVERNANCE_FILES):
        if not (PROJECT_ROOT / relative_path).is_file():
            failures.append(f"Missing governance file: {relative_path}")

    available_schemas = {path.name for path in SCHEMA_ROOT.glob("*.schema.json")}
    for schema_name in sorted(REQUIRED_SCHEMAS - available_schemas):
        failures.append(f"Missing schema: {schema_name}")

    for schema_path in sorted(SCHEMA_ROOT.glob("*.schema.json")):
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"Invalid JSON in {schema_path.name}: {error}")
            continue

        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(f"Unexpected JSON Schema draft in {schema_path.name}")
        if not isinstance(schema.get("$id"), str):
            failures.append(f"Missing $id in {schema_path.name}")

        for reference in walk_references(schema):
            reference_file = reference.split("#", 1)[0]
            if not reference_file or reference_file.startswith(("http://", "https://")):
                continue
            if not (schema_path.parent / reference_file).is_file():
                failures.append(f"Broken $ref in {schema_path.name}: {reference}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"Validated {len(available_schemas)} schemas and {len(REQUIRED_GOVERNANCE_FILES)} governance files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate())
