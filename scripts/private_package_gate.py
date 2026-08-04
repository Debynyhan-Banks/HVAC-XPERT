#!/usr/bin/env python3

import argparse
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRIVATE_ROOT = PROJECT_ROOT / "sources" / "private"
INTERNAL_APPROVED_STATUS = "TECHNICALLY_APPROVED_LEGAL_HOLD"
PUBLIC_APPROVED_STATUS = "APPROVED_FOR_PUBLICATION"
CONNECTOR_TYPES = {"PLUG", "RECEPTACLE", "HEADER", "TERMINAL_BLOCK", "SPLICE", "OTHER", "UNKNOWN"}
SIGNAL_TYPES = {
    "LINE_VOLTAGE_AC", "INVERTER_3_PHASE_AC", "LOW_VOLTAGE_AC", "HIGH_VOLTAGE_DC",
    "LOW_VOLTAGE_DC", "GROUND", "COMMUNICATION", "ANALOG_SENSOR", "DIGITAL_INPUT",
    "DIGITAL_OUTPUT", "PWM", "CURRENT_LOOP", "OTHER", "UNKNOWN",
}
NODE_TYPES = {"POWER", "NEUTRAL", "GROUND", "SIGNAL", "COMMUNICATION", "SENSOR", "SWITCHED", "REFERENCE", "OTHER", "UNKNOWN"}
CONNECTION_TYPES = {"WIRE", "TRACE", "CONTACT", "SWITCH", "FUSE", "LOAD", "BUS", "VIRTUAL", "OTHER", "UNKNOWN"}


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
    operating_states: tuple[dict[str, Any], ...] = ()
    measurements: tuple[dict[str, Any], ...] = ()
    connectors: tuple[dict[str, Any], ...] = ()
    pins: tuple[dict[str, Any], ...] = ()
    nodes: tuple[dict[str, Any], ...] = ()
    connections: tuple[dict[str, Any], ...] = ()
    extension_package_ids: tuple[str, ...] = ()

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


def validate_operating_states(records, measurements, package, manifest):
    state_ids = set()
    component_ids = {record["component_id"] for record in package.components}
    measurement_ids = {record.get("measurement_id") for record in package.measurements}
    measurement_ids.update(record.get("measurement_id") for record in measurements)
    available_state_ids = {record.get("state_id") for record in package.operating_states}
    available_state_ids.update(record.get("state_id") for record in records)
    for record in records:
        state_id = record.get("state_id")
        require(state_id and state_id not in state_ids, f"Duplicate or missing operating-state ID: {state_id}")
        state_ids.add(state_id)
        require(record.get("model_id") == package.model_id, f"Operating state {state_id} model ID mismatch")
        require(record.get("revision_id") == package.revision_id, f"Operating state {state_id} revision mismatch")
        commands = record.get("component_commands")
        require(isinstance(commands, list), f"Operating state {state_id} component commands must be an array")
        for command in commands:
            require(isinstance(command, dict), f"Operating state {state_id} contains an invalid component command")
            require(command.get("component_id") in component_ids, f"Operating state {state_id} references an unknown component")
        transitions = record.get("transitions")
        require(isinstance(transitions, list), f"Operating state {state_id} transitions must be an array")
        for transition in transitions:
            require(isinstance(transition, dict), f"Operating state {state_id} contains an invalid transition")
            require(transition.get("target_state_id") in available_state_ids, f"Operating state {state_id} references an unknown target state")
        referenced_measurements = record.get("measurement_ids")
        require(isinstance(referenced_measurements, list), f"Operating state {state_id} measurement IDs must be an array")
        require(set(referenced_measurements) <= measurement_ids, f"Operating state {state_id} references an unknown measurement")
        validate_provenance(record.get("provenance"), state_id, manifest, f"operating state {state_id}")


def validate_measurements(records, operating_states, package, manifest):
    measurement_ids = set()
    component_ids = {record["component_id"] for record in package.components}
    available_state_ids = {record.get("state_id") for record in package.operating_states}
    available_state_ids.update(record.get("state_id") for record in operating_states)
    for record in records:
        measurement_id = record.get("measurement_id")
        require(measurement_id and measurement_id not in measurement_ids, f"Duplicate or missing measurement ID: {measurement_id}")
        measurement_ids.add(measurement_id)
        require(record.get("model_id") == package.model_id, f"Measurement {measurement_id} model ID mismatch")
        require(record.get("revision_id") == package.revision_id, f"Measurement {measurement_id} revision mismatch")
        operating_state_id = record.get("operating_state_id")
        require(operating_state_id is None or operating_state_id in available_state_ids, f"Measurement {measurement_id} references an unknown operating state")
        for point_name in ("point_a", "point_b"):
            point = record.get(point_name)
            if point is None:
                continue
            require(isinstance(point, dict), f"Measurement {measurement_id} {point_name} must be an object or null")
            if point.get("reference_type") == "COMPONENT_TERMINAL":
                require(point.get("reference_id") in component_ids, f"Measurement {measurement_id} references an unknown component")
        validate_provenance(record.get("provenance"), measurement_id, manifest, f"measurement {measurement_id}")


def record_map(existing, records, id_field, label):
    values = {record[id_field]: record for record in existing}
    require(len(values) == len(existing), f"Loaded package contains duplicate {label} IDs")
    for record in records:
        record_id = record.get(id_field)
        require(record_id and record_id not in values, f"Duplicate or missing {label} ID: {record_id}")
        values[record_id] = record
    return values


def validate_id_list(value, location):
    require(isinstance(value, list), f"{location} must be an array")
    require(all(isinstance(item, str) and item for item in value), f"{location} contains an invalid ID")
    require(len(value) == len(set(value)), f"{location} contains duplicate IDs")


def validate_topology(connectors, pins, nodes, connections, measurements, package, manifest):
    component_ids = {record["component_id"] for record in package.components}
    measurement_ids = {record["measurement_id"] for record in package.measurements}
    measurement_ids.update(record["measurement_id"] for record in measurements)
    connectors_by_id = record_map(package.connectors, connectors, "connector_id", "connector")
    pins_by_id = record_map(package.pins, pins, "pin_id", "pin")
    nodes_by_id = record_map(package.nodes, nodes, "node_id", "node")
    record_map(package.connections, connections, "connection_id", "connection")

    for connector in connectors:
        connector_id = connector["connector_id"]
        require(connector.get("model_id") == package.model_id, f"Connector {connector_id} model ID mismatch")
        require(connector.get("revision_id") == package.revision_id, f"Connector {connector_id} revision mismatch")
        require(connector.get("component_id") in component_ids, f"Connector {connector_id} references an unknown component")
        require(connector.get("connector_type") in CONNECTOR_TYPES, f"Connector {connector_id} has an unsupported type")
        validate_id_list(connector.get("pin_ids"), f"Connector {connector_id} pin IDs")
        require(set(connector["pin_ids"]) <= set(pins_by_id), f"Connector {connector_id} references an unknown pin")
        validate_provenance(connector.get("provenance"), connector_id, manifest, f"connector {connector_id}")

    for pin in pins:
        pin_id = pin["pin_id"]
        require(pin.get("model_id") == package.model_id, f"Pin {pin_id} model ID mismatch")
        require(pin.get("revision_id") == package.revision_id, f"Pin {pin_id} revision mismatch")
        require(pin.get("connector_id") in connectors_by_id, f"Pin {pin_id} references an unknown connector")
        node_id = pin.get("node_id")
        require(node_id is None or node_id in nodes_by_id, f"Pin {pin_id} references an unknown node")
        require(pin.get("signal_type") in SIGNAL_TYPES, f"Pin {pin_id} has an unsupported signal type")
        validate_id_list(pin.get("measurement_ids"), f"Pin {pin_id} measurement IDs")
        require(set(pin["measurement_ids"]) <= measurement_ids, f"Pin {pin_id} references an unknown measurement")
        validate_provenance(pin.get("provenance"), pin_id, manifest, f"pin {pin_id}")

    for node in nodes:
        node_id = node["node_id"]
        require(node.get("model_id") == package.model_id, f"Node {node_id} model ID mismatch")
        require(node.get("revision_id") == package.revision_id, f"Node {node_id} revision mismatch")
        require(node.get("node_type") in NODE_TYPES, f"Node {node_id} has an unsupported node type")
        reference_node_id = node.get("reference_node_id")
        require(reference_node_id is None or reference_node_id in nodes_by_id, f"Node {node_id} references an unknown reference node")
        validate_id_list(node.get("pin_ids"), f"Node {node_id} pin IDs")
        require(set(node["pin_ids"]) <= set(pins_by_id), f"Node {node_id} references an unknown pin")
        validate_provenance(node.get("provenance"), node_id, manifest, f"node {node_id}")

    for connection in connections:
        connection_id = connection["connection_id"]
        require(connection.get("model_id") == package.model_id, f"Connection {connection_id} model ID mismatch")
        require(connection.get("revision_id") == package.revision_id, f"Connection {connection_id} revision mismatch")
        from_node_id = connection.get("from_node_id")
        to_node_id = connection.get("to_node_id")
        require(from_node_id in nodes_by_id, f"Connection {connection_id} references an unknown from node")
        require(to_node_id in nodes_by_id, f"Connection {connection_id} references an unknown to node")
        require(from_node_id != to_node_id, f"Connection {connection_id} endpoints must differ")
        require(connection.get("connection_type") in CONNECTION_TYPES, f"Connection {connection_id} has an unsupported type")
        controlled_by = connection.get("controlled_by_component_id")
        require(controlled_by is None or controlled_by in component_ids, f"Connection {connection_id} references an unknown controller")
        require(type(connection.get("normally_closed")) in (bool, type(None)), f"Connection {connection_id} normally_closed must be boolean or null")
        validate_provenance(connection.get("provenance"), connection_id, manifest, f"connection {connection_id}")

    for connector in connectors:
        for pin_id in connector["pin_ids"]:
            require(pins_by_id[pin_id].get("connector_id") == connector["connector_id"], f"Connector {connector['connector_id']} lists a pin assigned elsewhere")
    for pin in pins:
        connector = connectors_by_id[pin["connector_id"]]
        require(pin["pin_id"] in connector.get("pin_ids", []), f"Pin {pin['pin_id']} is absent from its connector")
        if pin.get("node_id") is not None:
            require(pin["pin_id"] in nodes_by_id[pin["node_id"]].get("pin_ids", []), f"Pin {pin['pin_id']} is absent from its node")
    for node in nodes:
        for pin_id in node["pin_ids"]:
            require(pins_by_id[pin_id].get("node_id") == node["node_id"], f"Node {node['node_id']} lists a pin assigned elsewhere")


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


def load_private_approved_extension(extension_path, package, private_root=DEFAULT_PRIVATE_ROOT):
    extension_root = require_private_path(Path(extension_path), Path(private_root))
    manifest = load_json(extension_root / "package-manifest.json")
    require(manifest.get("package_kind") == "KNOWLEDGE_EXTENSION", "Extension package kind must be KNOWLEDGE_EXTENSION")
    require(manifest.get("base_package_id") == package.manifest["package_id"], "Extension base package ID mismatch")
    require(manifest.get("model_id") == package.model_id, "Extension model ID mismatch")
    require(manifest.get("revision_id") == package.revision_id, "Extension revision ID mismatch")
    require(manifest.get("status") == INTERNAL_APPROVED_STATUS, f"Extension status must be {INTERNAL_APPROVED_STATUS}")
    require(manifest.get("publication_allowed") is False, "Internal extension cannot be marked for publication")
    require(manifest.get("contains_source_binaries") is False, "Extension manifest cannot claim embedded source binaries")
    require(isinstance(manifest.get("document_ids"), list) and manifest["document_ids"], "Extension document list is missing")

    technical_review = manifest.get("technical_review", {})
    require(technical_review.get("outcome") == "ACCEPTED", "Extension technical review outcome must be ACCEPTED")
    require(technical_review.get("scope") == "ALL_ASSERTIONS", "Extension technical review must cover all assertions")
    require(technical_review.get("reviewer_id") == manifest.get("assigned_reviewer"), "Extension technical reviewer does not match assignment")
    require(technical_review.get("legal_hold") is True, "Approved extension must retain legal hold")
    require(isinstance(technical_review.get("reviewed_at"), str), "Extension technical review timestamp is missing")
    validate_decision(extension_root, manifest)

    records = {
        "operating_states": load_records(extension_root / "operating-states"),
        "measurements": load_records(extension_root / "measurements"),
        "connectors": load_records(extension_root / "connectors"),
        "pins": load_records(extension_root / "pins"),
        "nodes": load_records(extension_root / "nodes"),
        "connections": load_records(extension_root / "connections"),
    }
    actual_counts = {name: len(values) for name, values in records.items() if values}
    require(actual_counts, "Extension contains no supported records")
    require(manifest.get("record_counts") == actual_counts, f"Extension record counts do not match manifest: {actual_counts}")
    operating_states = records["operating_states"]
    measurements = records["measurements"]
    validate_measurements(measurements, operating_states, package, manifest)
    validate_operating_states(operating_states, measurements, package, manifest)
    validate_topology(
        records["connectors"], records["pins"], records["nodes"], records["connections"],
        measurements, package, manifest,
    )
    validate_no_binaries(extension_root)

    assertion_count = sum(
        len(record["provenance"])
        for record_group in records.values()
        for record in record_group
    )
    require(technical_review.get("assertion_count") == assertion_count, "Extension technical-review assertion count does not match package")
    return manifest, records


def load_private_approved_package_with_extensions(package_path, extension_paths, private_root=DEFAULT_PRIVATE_ROOT):
    package = load_private_approved_package(package_path, private_root)
    for extension_path in extension_paths:
        manifest, records = load_private_approved_extension(extension_path, package, private_root)
        operating_states = records["operating_states"]
        measurements = records["measurements"]
        existing_state_ids = {record["state_id"] for record in package.operating_states}
        new_state_ids = {record["state_id"] for record in operating_states}
        require(existing_state_ids.isdisjoint(new_state_ids), "Extension operating-state IDs overlap a loaded extension")
        existing_measurement_ids = {record["measurement_id"] for record in package.measurements}
        new_measurement_ids = {record["measurement_id"] for record in measurements}
        require(existing_measurement_ids.isdisjoint(new_measurement_ids), "Extension measurement IDs overlap a loaded extension")
        package = replace(
            package,
            operating_states=package.operating_states + operating_states,
            measurements=package.measurements + measurements,
            connectors=package.connectors + records["connectors"],
            pins=package.pins + records["pins"],
            nodes=package.nodes + records["nodes"],
            connections=package.connections + records["connections"],
            extension_package_ids=package.extension_package_ids + (manifest["package_id"],),
        )
    return package


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
        "operating_states": len(package.operating_states),
        "measurements": len(package.measurements),
        "connectors": len(package.connectors),
        "pins": len(package.pins),
        "nodes": len(package.nodes),
        "connections": len(package.connections),
        "extension_package_ids": package.extension_package_ids,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Load an approved private knowledge package and enforce its publication gate.")
    parser.add_argument("package", type=Path)
    parser.add_argument("--private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--extension", action="append", type=Path, default=[])
    parser.add_argument("--mode", choices=("internal", "public"), default="internal")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        package = load_private_approved_package_with_extensions(args.package, args.extension, args.private_root)
        if args.mode == "public":
            assert_public_export_allowed(package)
    except (PackageValidationError, PublicationBlockedError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(package_summary(package), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
