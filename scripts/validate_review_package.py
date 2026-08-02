#!/usr/bin/env python3

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_REVIEW_ROOT = PROJECT_ROOT / "sources" / "private" / "review"
MANIFEST_ROOT = PROJECT_ROOT / "sources" / "manifests"
COMPLETE_PACKAGE_KIND = "COMPLETE_SNAPSHOT"
EXTENSION_PACKAGE_KIND = "KNOWLEDGE_EXTENSION"


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


def require_record_keys(record, required_keys, failures, location):
    missing_keys = required_keys - set(record)
    if missing_keys:
        failures.append(f"{location}: missing canonical keys {sorted(missing_keys)}")


def validate_complete_snapshot(package_root, manifest, context, failures):
    model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages = context
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
    actual_counts = {
        "equipment_models": 1 if model is not None else 0,
        "components": len(component_paths),
        "faults": len(fault_paths),
        "wiring_diagram_assertions": len(wiring_paths),
    }
    if manifest.get("record_counts", {}) != actual_counts:
        failures.append(f"Record counts differ: manifest={manifest.get('record_counts', {})}, actual={actual_counts}")

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
    return assertion_count, actual_counts


def validate_extension(package_root, manifest, context, failures):
    model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages = context
    base_package_id = manifest.get("base_package_id")
    if not isinstance(base_package_id, str) or not base_package_id:
        failures.append("Knowledge extension is missing base_package_id")
        base_root = None
    else:
        base_root = PRIVATE_REVIEW_ROOT / base_package_id / "package"

    component_ids = set()
    base_state_ids = set()
    base_measurement_ids = set()
    if base_root is not None:
        base_manifest = load_json(base_root / "package-manifest.json", failures)
        if base_manifest is not None:
            if base_manifest.get("status") != "TECHNICALLY_APPROVED_LEGAL_HOLD":
                failures.append("Knowledge extension base package is not technically approved")
            if base_manifest.get("model_id") != model_id or base_manifest.get("revision_id") != revision_id:
                failures.append("Knowledge extension model or revision differs from base package")
        for path in sorted((base_root / "components").glob("*.json")):
            component = load_json(path, failures)
            if component is not None and component.get("component_id"):
                component_ids.add(component["component_id"])
        for path in sorted((base_root / "operating-states").glob("*.json")):
            state = load_json(path, failures)
            if state is not None and state.get("state_id"):
                base_state_ids.add(state["state_id"])
        for path in sorted((base_root / "measurements").glob("*.json")):
            measurement = load_json(path, failures)
            if measurement is not None and measurement.get("measurement_id"):
                base_measurement_ids.add(measurement["measurement_id"])

    state_paths = sorted((package_root / "operating-states").glob("*.json"))
    measurement_paths = sorted((package_root / "measurements").glob("*.json"))
    actual_counts = {
        "operating_states": len(state_paths),
        "measurements": len(measurement_paths),
    }
    if manifest.get("record_counts", {}) != actual_counts:
        failures.append(f"Record counts differ: manifest={manifest.get('record_counts', {})}, actual={actual_counts}")

    state_records = []
    state_ids = set()
    state_required_keys = {
        "schema_version", "state_id", "model_id", "revision_id", "name", "description",
        "entry_conditions", "component_commands", "transitions", "measurement_ids", "provenance",
    }
    assertion_count = 0
    for path in state_paths:
        state = load_json(path, failures)
        if state is None:
            continue
        require_record_keys(state, state_required_keys, failures, str(path))
        state_id = state.get("state_id")
        if state_id in state_ids or state_id in base_state_ids:
            failures.append(f"Duplicate operating-state ID: {state_id}")
        state_ids.add(state_id)
        state_records.append((path, state))
        assertion_count += len(state.get("provenance", []))
        validate_entity(state, "state_id", model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, str(path))

    measurement_records = []
    measurement_ids = set()
    measurement_required_keys = {
        "schema_version", "measurement_id", "model_id", "revision_id", "operating_state_id", "name",
        "quantity", "signal_type", "point_a", "point_b", "meter_mode", "expected", "safety_category",
        "procedure", "provenance",
    }
    for path in measurement_paths:
        measurement = load_json(path, failures)
        if measurement is None:
            continue
        require_record_keys(measurement, measurement_required_keys, failures, str(path))
        measurement_id = measurement.get("measurement_id")
        if measurement_id in measurement_ids or measurement_id in base_measurement_ids:
            failures.append(f"Duplicate measurement ID: {measurement_id}")
        measurement_ids.add(measurement_id)
        measurement_records.append((path, measurement))
        assertion_count += len(measurement.get("provenance", []))
        validate_entity(measurement, "measurement_id", model_id, revision_id, package_id, package_status, assigned_reviewer, expected_reviewed_at, document_pages, failures, str(path))

    available_state_ids = base_state_ids | state_ids
    available_measurement_ids = base_measurement_ids | measurement_ids
    for path, state in state_records:
        if not isinstance(state.get("entry_conditions"), list):
            failures.append(f"{path}: entry_conditions must be an array")
        commands = state.get("component_commands")
        if not isinstance(commands, list):
            failures.append(f"{path}: component_commands must be an array")
        else:
            for command in commands:
                if not isinstance(command, dict):
                    failures.append(f"{path}: component_commands contains a non-object value")
                elif command.get("component_id") not in component_ids:
                    failures.append(f"{path}: command references unknown component {command.get('component_id')}")
        transitions = state.get("transitions")
        if not isinstance(transitions, list):
            failures.append(f"{path}: transitions must be an array")
        else:
            for transition in transitions:
                if not isinstance(transition, dict):
                    failures.append(f"{path}: transitions contains a non-object value")
                elif transition.get("target_state_id") not in available_state_ids:
                    failures.append(f"{path}: transition references unknown state {transition.get('target_state_id')}")
        referenced_measurements = state.get("measurement_ids")
        if not isinstance(referenced_measurements, list) or not set(referenced_measurements) <= available_measurement_ids:
            failures.append(f"{path}: measurement_ids contain an unknown measurement")

    for path, measurement in measurement_records:
        operating_state_id = measurement.get("operating_state_id")
        if operating_state_id is not None and operating_state_id not in available_state_ids:
            failures.append(f"{path}: operating_state_id references unknown state {operating_state_id}")
        for point_name in ("point_a", "point_b"):
            point = measurement.get(point_name)
            if point is None:
                continue
            if not isinstance(point, dict):
                failures.append(f"{path}: {point_name} must be an object or null")
            elif point.get("reference_type") == "COMPONENT_TERMINAL" and point.get("reference_id") not in component_ids:
                failures.append(f"{path}: {point_name} references unknown component {point.get('reference_id')}")
    return assertion_count, actual_counts


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
    package_kind = manifest.get("package_kind", COMPLETE_PACKAGE_KIND)
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
    if package_kind not in {COMPLETE_PACKAGE_KIND, EXTENSION_PACKAGE_KIND}:
        failures.append(f"Unsupported package kind: {package_kind}")

    document_pages = load_document_pages(failures)
    expected_document_ids = set(manifest.get("document_ids", []))
    if not expected_document_ids <= set(document_pages):
        failures.append("Package references an unknown document manifest")

    context = (
        model_id,
        revision_id,
        package_id,
        package_status,
        assigned_reviewer,
        expected_reviewed_at,
        document_pages,
    )
    if package_kind == EXTENSION_PACKAGE_KIND:
        assertion_count, actual_counts = validate_extension(package_root, manifest, context, failures)
    else:
        assertion_count, actual_counts = validate_complete_snapshot(package_root, manifest, context, failures)

    if package_status == "PENDING_TECHNICAL_REVIEW":
        if technical_review.get("outcome") != "PENDING" or technical_review.get("scope") != "ALL_ASSERTIONS":
            failures.append("Pending package requires a complete PENDING technical-review assignment")
        if technical_review.get("reviewer_id") != assigned_reviewer:
            failures.append("Pending technical-review reviewer does not match assignment")
        if technical_review.get("reviewed_at") is not None:
            failures.append("Pending technical review cannot have a review timestamp")
        if technical_review.get("assertion_count") != assertion_count:
            failures.append("Pending technical-review assertion count does not match package")
        if technical_review.get("decision_file") is not None:
            failures.append("Pending technical review cannot identify a completed decision file")
        if technical_review.get("legal_hold") is not True:
            failures.append("Pending private package must remain on legal hold")
    elif package_status == "TECHNICALLY_APPROVED_LEGAL_HOLD":
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

    count_summary = ", ".join(f"{count} {name.replace('_', ' ')}" for name, count in actual_counts.items())
    print(f"Validated private review package {package_id}: {count_summary}.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_review_package.py <private-package-directory>", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(validate(Path(sys.argv[1])))
