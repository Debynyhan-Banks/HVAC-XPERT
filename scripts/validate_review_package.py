#!/usr/bin/env python3

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_REVIEW_ROOT = PROJECT_ROOT / "sources" / "private" / "review"
MANIFEST_ROOT = PROJECT_ROOT / "sources" / "manifests"


def load_json(path, failures):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"Invalid JSON in {path}: {error}")
        return None


def load_document_pages(failures):
    document_pages = {}
    for manifest_path in MANIFEST_ROOT.glob("*.json"):
        manifest = load_json(manifest_path, failures)
        if manifest is None:
            continue
        document_id = manifest.get("document_id")
        page_count = manifest.get("fingerprint", {}).get("page_count")
        if document_id and isinstance(page_count, int):
            document_pages[document_id] = page_count
    return document_pages


def validate_provenance(assertion, entity_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, location):
    required_keys = {"fact_id", "entity_id", "property", "value", "unit", "source", "extraction", "validation"}
    missing_keys = required_keys - set(assertion)
    if missing_keys:
        failures.append(f"{location}: missing provenance keys {sorted(missing_keys)}")
        return
    if assertion.get("entity_id") != entity_id:
        failures.append(f"{location}: provenance entity does not match {entity_id}")

    source = assertion.get("source", {})
    document_id = source.get("document_id")
    page = source.get("page")
    if document_id not in document_pages:
        failures.append(f"{location}: unknown source document {document_id}")
    elif not isinstance(page, int) or not 1 <= page <= document_pages[document_id]:
        failures.append(f"{location}: invalid page {page} for {document_id}")

    extraction = assertion.get("extraction", {})
    if extraction.get("run_id") != package_id:
        failures.append(f"{location}: extraction run does not match package ID")

    validation = assertion.get("validation", {})
    if package_status == "PENDING_TECHNICAL_REVIEW":
        if validation.get("level") != "LEVEL_1_AI_EXTRACTED":
            failures.append(f"{location}: unreviewed assertion must remain LEVEL_1_AI_EXTRACTED")
        if validation.get("outcome") != "PENDING":
            failures.append(f"{location}: unreviewed assertion must remain PENDING")
        if validation.get("reviewed_by") is not None or validation.get("reviewed_at") is not None:
            failures.append(f"{location}: pending assertion cannot contain reviewer approval")
    elif package_status == "TECHNICALLY_APPROVED_LEGAL_HOLD":
        if validation.get("level") != "LEVEL_4_TECHNICIAN_REVIEWED":
            failures.append(f"{location}: approved assertion must be LEVEL_4_TECHNICIAN_REVIEWED")
        if validation.get("outcome") != "ACCEPTED":
            failures.append(f"{location}: approved assertion must be ACCEPTED")
        if validation.get("reviewed_by") != assigned_reviewer:
            failures.append(f"{location}: approved assertion reviewer does not match assignment")
        if validation.get("reviewed_at") != expected_reviewed_at:
            failures.append(f"{location}: approved assertion timestamp does not match review decision")


def validate_entity(record, id_field, model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, location):
    entity_id = record.get(id_field)
    if not entity_id:
        failures.append(f"{location}: missing {id_field}")
        return
    if record.get("model_id") != model_id and id_field != "model_id":
        failures.append(f"{location}: model ID does not match package")
    if record.get("revision_id") != revision_id:
        failures.append(f"{location}: revision ID does not match package")
    provenance_entries = record.get("provenance")
    if not isinstance(provenance_entries, list) or not provenance_entries:
        failures.append(f"{location}: missing provenance")
        return
    for index, assertion in enumerate(provenance_entries):
        validate_provenance(assertion, entity_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, f"{location} provenance[{index}]")


def validate(package_path):
    failures = []
    package_root = package_path.resolve()
    try:
        package_root.relative_to(PRIVATE_REVIEW_ROOT.resolve())
    except ValueError:
        failures.append("Review package must remain inside sources/private/review")

    manifest = load_json(package_root / "package-manifest.json", failures)
    if manifest is None:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    package_id = manifest.get("package_id")
    model_id = manifest.get("model_id")
    revision_id = manifest.get("revision_id")
    package_status = manifest.get("status")
    assigned_reviewer = manifest.get("assigned_reviewer")
    technical_review = manifest.get("technical_review", {})
    expected_reviewed_at = technical_review.get("reviewed_at")
    if package_status not in {"PENDING_TECHNICAL_REVIEW", "TECHNICALLY_APPROVED_LEGAL_HOLD"}:
        failures.append(f"Unsupported package status: {package_status}")
    if manifest.get("publication_allowed") is not False:
        failures.append("Private review package cannot be publication-approved while legal hold remains")
    if manifest.get("contains_source_binaries") is not False:
        failures.append("Review package manifest must not claim embedded source binaries")

    document_pages = load_document_pages(failures)
    expected_document_ids = set(manifest.get("document_ids", []))
    if not expected_document_ids <= set(document_pages):
        failures.append("Package references an unknown document manifest")

    model = load_json(package_root / "equipment-model.json", failures)
    assertion_count = 0
    if model is not None:
        if model.get("model_id") != model_id:
            failures.append("Equipment model ID does not match package")
        assertion_count += len(model.get("provenance", []))
        validate_entity(model, "model_id", model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, "equipment-model.json")

    component_paths = sorted((package_root / "components").glob("*.json"))
    fault_paths = sorted((package_root / "faults").glob("*.json"))
    wiring_paths = sorted((package_root / "wiring").glob("*.json"))
    record_counts = manifest.get("record_counts", {})
    actual_counts = {
        "equipment_models": 1 if model is not None else 0,
        "components": len(component_paths),
        "faults": len(fault_paths),
        "wiring_diagram_assertions": len(wiring_paths),
    }
    if record_counts != actual_counts:
        failures.append(f"Record counts differ: manifest={record_counts}, actual={actual_counts}")

    component_ids = set()
    for path in component_paths:
        component = load_json(path, failures)
        if component is None:
            continue
        component_id = component.get("component_id")
        if component_id in component_ids:
            failures.append(f"Duplicate component ID: {component_id}")
        component_ids.add(component_id)
        assertion_count += len(component.get("provenance", []))
        validate_entity(component, "component_id", model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, str(path))

    fault_ids = set()
    fault_codes = set()
    for path in fault_paths:
        fault = load_json(path, failures)
        if fault is None:
            continue
        fault_id = fault.get("fault_id")
        fault_code = fault.get("code")
        if fault_id in fault_ids:
            failures.append(f"Duplicate fault ID: {fault_id}")
        if fault_code in fault_codes:
            failures.append(f"Duplicate fault code: {fault_code}")
        fault_ids.add(fault_id)
        fault_codes.add(fault_code)
        assertion_count += len(fault.get("provenance", []))
        validate_entity(fault, "fault_id", model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, str(path))

    wiring_fact_ids = set()
    for path in wiring_paths:
        assertion = load_json(path, failures)
        if assertion is None:
            continue
        fact_id = assertion.get("fact_id")
        if fact_id in wiring_fact_ids:
            failures.append(f"Duplicate wiring fact ID: {fact_id}")
        wiring_fact_ids.add(fact_id)
        assertion_count += 1
        validate_provenance(assertion, model_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, str(path))

    if package_status == "TECHNICALLY_APPROVED_LEGAL_HOLD":
        if technical_review.get("outcome") != "ACCEPTED" or technical_review.get("scope") != "ALL_ASSERTIONS":
            failures.append("Approved package requires a complete ACCEPTED technical review")
        if technical_review.get("reviewer_id") != assigned_reviewer:
            failures.append("Technical-review manifest reviewer does not match assignment")
        if technical_review.get("assertion_count") != assertion_count:
            failures.append("Technical-review assertion count does not match package")
        if technical_review.get("legal_hold") is not True:
            failures.append("Technically approved package must remain on legal hold")
        decision_file = technical_review.get("decision_file")
        if not isinstance(decision_file, str) or Path(decision_file).name != decision_file:
            failures.append("Technical review has an invalid decision filename")
        else:
            decision = load_json(package_root / decision_file, failures)
            if decision is not None:
                expected_decision = {
                    "package_id": package_id,
                    "reviewer_id": assigned_reviewer,
                    "outcome": "ACCEPTED",
                    "scope": "ALL_ASSERTIONS",
                    "reviewed_at": expected_reviewed_at,
                    "publication_authorized": False,
                }
                for key, expected_value in expected_decision.items():
                    if decision.get(key) != expected_value:
                        failures.append(f"Review decision {key} does not match package approval")

    forbidden_files = [path for path in package_root.rglob("*") if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}]
    if forbidden_files:
        failures.append(f"Review package contains source or rendered binaries: {forbidden_files}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(
        f"Validated private review package {package_id}: "
        f"{actual_counts['equipment_models']} model, "
        f"{actual_counts['components']} components, "
        f"{actual_counts['faults']} faults, "
        f"{actual_counts['wiring_diagram_assertions']} wiring assertions."
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_review_package.py <private-package-directory>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(validate(Path(sys.argv[1])))
