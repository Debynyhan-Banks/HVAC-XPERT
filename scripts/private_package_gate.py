#!/usr/bin/env python3

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_ROOT = PROJECT_ROOT / "sources" / "private"
INTERNAL_APPROVED_STATUS = "TECHNICALLY_APPROVED_LEGAL_HOLD"
PUBLIC_APPROVED_STATUS = "APPROVED_FOR_PUBLICATION"


class PackageValidationError(ValueError):
    pass


class PublicationBlockedError(PermissionError):
    pass


@dataclass(frozen=True)
class PrivateKnowledgePackage:
    root: Path
    manifest: dict[str, Any]
    equipment_model: dict[str, Any]
    components: tuple[dict[str, Any], ...]
    faults: tuple[dict[str, Any], ...]
    wiring_assertions: tuple[dict[str, Any], ...]

    @property
    def model_id(self):
        return self.manifest["model_id"]

    @property
    def revision_id(self):
        return self.manifest["revision_id"]


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise PackageValidationError(f"Cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise PackageValidationError(f"Invalid JSON in {path}: {error}") from error


def require(condition, message):
    if not condition:
        raise PackageValidationError(message)


def require_private_path(package_root, private_root):
    resolved_package = package_root.resolve()
    resolved_private = private_root.resolve()
    try:
        resolved_package.relative_to(resolved_private)
    except ValueError as error:
        raise PackageValidationError(f"Package must remain under private root {resolved_private}") from error
    return resolved_package


def validate_decision(package_root, manifest):
    technical_review = manifest.get("technical_review", {})
    decision_file = technical_review.get("decision_file")
    require(isinstance(decision_file, str) and Path(decision_file).name == decision_file, "Technical review decision filename is invalid")
    decision = load_json(package_root / decision_file)
    expected = {
        "package_id": manifest.get("package_id"),
        "reviewer_id": manifest.get("assigned_reviewer"),
        "outcome": "ACCEPTED",
        "scope": "ALL_ASSERTIONS",
        "reviewed_at": technical_review.get("reviewed_at"),
        "publication_authorized": False,
    }
    for key, expected_value in expected.items():
        require(decision.get(key) == expected_value, f"Review decision {key} does not match manifest")


def validate_provenance(assertions, entity_id, manifest, location):
    require(isinstance(assertions, list) and assertions, f"{location} is missing provenance")
    technical_review = manifest["technical_review"]
    document_ids = set(manifest["document_ids"])
    for index, assertion in enumerate(assertions):
        assertion_location = f"{location} provenance[{index}]"
        require(assertion.get("entity_id") == entity_id, f"{assertion_location} entity ID mismatch")
        require(assertion.get("extraction", {}).get("run_id") == manifest["package_id"], f"{assertion_location} run ID mismatch")
        source = assertion.get("source", {})
        require(source.get("document_id") in document_ids, f"{assertion_location} references an unlisted document")
        require(isinstance(source.get("page"), int) and source["page"] >= 1, f"{assertion_location} has an invalid source page")
        validation = assertion.get("validation", {})
        require(validation.get("level") == "LEVEL_4_TECHNICIAN_REVIEWED", f"{assertion_location} is not technician-reviewed")
        require(validation.get("outcome") == "ACCEPTED", f"{assertion_location} is not accepted")
        require(validation.get("reviewed_by") == manifest["assigned_reviewer"], f"{assertion_location} reviewer mismatch")
        require(validation.get("reviewed_at") == technical_review["reviewed_at"], f"{assertion_location} review timestamp mismatch")


def load_records(record_root):
    return tuple(load_json(path) for path in sorted(record_root.glob("*.json")))


def validate_record_counts(manifest, equipment_model, components, faults, wiring_assertions):
    actual_counts = {
        "equipment_models": 1 if equipment_model else 0,
        "components": len(components),
        "faults": len(faults),
        "wiring_diagram_assertions": len(wiring_assertions),
    }
    require(manifest.get("record_counts") == actual_counts, f"Record counts do not match manifest: {actual_counts}")


def validate_equipment_model(record, manifest):
    require(record.get("model_id") == manifest["model_id"], "Equipment model ID does not match package")
    require(record.get("revision_id") == manifest["revision_id"], "Equipment model revision does not match package")
    validate_provenance(record.get("provenance"), record["model_id"], manifest, "equipment model")


def validate_components(records, manifest):
    component_ids = set()
    for record in records:
        component_id = record.get("component_id")
        require(component_id and component_id not in component_ids, f"Duplicate or missing component ID: {component_id}")
        component_ids.add(component_id)
        require(record.get("model_id") == manifest["model_id"], f"Component {component_id} model ID mismatch")
        require(record.get("revision_id") == manifest["revision_id"], f"Component {component_id} revision mismatch")
        validate_provenance(record.get("provenance"), component_id, manifest, f"component {component_id}")


def validate_faults(records, manifest):
    fault_ids = set()
    fault_codes = set()
    for record in records:
        fault_id = record.get("fault_id")
        fault_code = record.get("code")
        require(fault_id and fault_id not in fault_ids, f"Duplicate or missing fault ID: {fault_id}")
        require(fault_code and fault_code not in fault_codes, f"Duplicate or missing fault code: {fault_code}")
        fault_ids.add(fault_id)
        fault_codes.add(fault_code)
        require(record.get("model_id") == manifest["model_id"], f"Fault {fault_id} model ID mismatch")
        require(record.get("revision_id") == manifest["revision_id"], f"Fault {fault_id} revision mismatch")
        validate_provenance(record.get("provenance"), fault_id, manifest, f"fault {fault_id}")


def validate_wiring_assertions(records, manifest):
    fact_ids = set()
    for assertion in records:
        fact_id = assertion.get("fact_id")
        require(fact_id and fact_id not in fact_ids, f"Duplicate or missing wiring fact ID: {fact_id}")
        fact_ids.add(fact_id)
        validate_provenance([assertion], manifest["model_id"], manifest, f"wiring assertion {fact_id}")


def validate_no_binaries(package_root):
    forbidden_suffixes = {".pdf", ".png", ".jpg", ".jpeg"}
    forbidden_files = [path for path in package_root.rglob("*") if path.is_file() and path.suffix.lower() in forbidden_suffixes]
    require(not forbidden_files, f"Private knowledge package contains source or rendered binaries: {forbidden_files}")


def load_private_approved_package(package_path, private_root=DEFAULT_PRIVATE_ROOT):
    package_root = require_private_path(Path(package_path), Path(private_root))
    manifest = load_json(package_root / "package-manifest.json")
    require(manifest.get("status") == INTERNAL_APPROVED_STATUS, f"Package status must be {INTERNAL_APPROVED_STATUS}")
    require(manifest.get("publication_allowed") is False, "Internal package must not be marked for publication")
    require(manifest.get("contains_source_binaries") is False, "Package manifest cannot claim embedded source binaries")
    require(isinstance(manifest.get("document_ids"), list) and manifest["document_ids"], "Package document list is missing")

    technical_review = manifest.get("technical_review", {})
    require(technical_review.get("outcome") == "ACCEPTED", "Technical review outcome must be ACCEPTED")
    require(technical_review.get("scope") == "ALL_ASSERTIONS", "Technical review must cover all assertions")
    require(technical_review.get("reviewer_id") == manifest.get("assigned_reviewer"), "Technical reviewer does not match assignment")
    require(technical_review.get("legal_hold") is True, "Internal approved package must retain legal hold")
    require(isinstance(technical_review.get("reviewed_at"), str), "Technical review timestamp is missing")
    validate_decision(package_root, manifest)

    equipment_model = load_json(package_root / "equipment-model.json")
    components = load_records(package_root / "components")
    faults = load_records(package_root / "faults")
    wiring_assertions = load_records(package_root / "wiring")
    validate_record_counts(manifest, equipment_model, components, faults, wiring_assertions)
    validate_equipment_model(equipment_model, manifest)
    validate_components(components, manifest)
    validate_faults(faults, manifest)
    validate_wiring_assertions(wiring_assertions, manifest)
    validate_no_binaries(package_root)

    assertion_count = len(equipment_model["provenance"])
    assertion_count += sum(len(record["provenance"]) for record in components)
    assertion_count += sum(len(record["provenance"]) for record in faults)
    assertion_count += len(wiring_assertions)
    require(technical_review.get("assertion_count") == assertion_count, "Technical-review assertion count does not match package")

    return PrivateKnowledgePackage(
        root=package_root,
        manifest=manifest,
        equipment_model=equipment_model,
        components=components,
        faults=faults,
        wiring_assertions=wiring_assertions,
    )


def publication_blockers(package_or_manifest):
    manifest = package_or_manifest.manifest if isinstance(package_or_manifest, PrivateKnowledgePackage) else package_or_manifest
    blockers = []
    if manifest.get("status") != PUBLIC_APPROVED_STATUS:
        blockers.append(f"status is not {PUBLIC_APPROVED_STATUS}")
    if manifest.get("publication_allowed") is not True:
        blockers.append("publication_allowed is not true")
    technical_review = manifest.get("technical_review", {})
    if technical_review.get("outcome") != "ACCEPTED":
        blockers.append("technical review is not accepted")
    if technical_review.get("legal_hold") is not False:
        blockers.append("legal hold is active")
    publication_review = manifest.get("publication_review", {})
    if publication_review.get("outcome") != "ACCEPTED":
        blockers.append("publication review is not accepted")
    if not publication_review.get("approved_by") or not publication_review.get("approved_at"):
        blockers.append("publication approval identity or timestamp is missing")
    return tuple(blockers)


def assert_public_export_allowed(package_or_manifest):
    blockers = publication_blockers(package_or_manifest)
    if blockers:
        raise PublicationBlockedError("Public export blocked: " + "; ".join(blockers))


def package_summary(package):
    return {
        "package_id": package.manifest["package_id"],
        "model_id": package.model_id,
        "revision_id": package.revision_id,
        "status": package.manifest["status"],
        "publication_allowed": package.manifest["publication_allowed"],
        "components": len(package.components),
        "faults": len(package.faults),
        "wiring_assertions": len(package.wiring_assertions),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Load an approved private knowledge package and enforce its publication gate.")
    parser.add_argument("package", type=Path)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--mode", choices=("internal", "public"), default="internal")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        package = load_private_approved_package(args.package, args.private_root)
        if args.mode == "public":
            assert_public_export_allowed(package)
    except (PackageValidationError, PublicationBlockedError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(package_summary(package), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
