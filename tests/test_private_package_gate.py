import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.private_package_gate import (
    PackageValidationError,
    PublicationBlockedError,
    assert_public_export_allowed,
    load_private_approved_package,
    load_private_approved_package_with_extensions,
)


PACKAGE_ID = "RUN-SYNTHETIC-001"
MODEL_ID = "SYNTHETIC-001"
REVISION_ID = "A"
REVIEWER_ID = "synthetic-reviewer"
REVIEWED_AT = "2026-08-02T00:00:00Z"
DOCUMENT_ID = "DOC-SYNTHETIC-001"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def provenance(fact_id, entity_id):
    return {
        "fact_id": fact_id,
        "entity_id": entity_id,
        "property": "/synthetic",
        "value": "synthetic",
        "unit": None,
        "source": {
            "document_id": DOCUMENT_ID,
            "document_title": "Synthetic Test Document",
            "page": 1,
            "section": "Synthetic",
            "source_url": None,
            "document_revision": None,
        },
        "extraction": {
            "method": "MANUAL_ENTRY",
            "confidence": 1.0,
            "extracted_at": "2026-08-02T00:00:00Z",
            "provider": None,
            "model_version": None,
            "prompt_version": None,
            "run_id": PACKAGE_ID,
        },
        "validation": {
            "level": "LEVEL_4_TECHNICIAN_REVIEWED",
            "outcome": "ACCEPTED",
            "reviewed_by": REVIEWER_ID,
            "reviewed_at": REVIEWED_AT,
            "notes": "Synthetic approval",
        },
    }


def extension_provenance(fact_id, entity_id, package_id):
    assertion = provenance(fact_id, entity_id)
    assertion["extraction"]["run_id"] = package_id
    return assertion


def package_data():
    manifest = {
        "schema_version": "1.0.0",
        "package_id": PACKAGE_ID,
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "status": "TECHNICALLY_APPROVED_LEGAL_HOLD",
        "assigned_reviewer": REVIEWER_ID,
        "publication_allowed": False,
        "contains_source_binaries": False,
        "document_ids": [DOCUMENT_ID],
        "record_counts": {
            "equipment_models": 1,
            "components": 1,
            "faults": 1,
            "wiring_diagram_assertions": 1,
        },
        "technical_review": {
            "outcome": "ACCEPTED",
            "scope": "ALL_ASSERTIONS",
            "reviewer_id": REVIEWER_ID,
            "reviewed_at": REVIEWED_AT,
            "assertion_count": 4,
            "decision_file": "review-decision.json",
            "legal_hold": True,
        },
    }
    decision = {
        "package_id": PACKAGE_ID,
        "reviewer_id": REVIEWER_ID,
        "outcome": "ACCEPTED",
        "scope": "ALL_ASSERTIONS",
        "reviewed_at": REVIEWED_AT,
        "publication_authorized": False,
    }
    equipment_model = {
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "provenance": [provenance("FACT-SYNTHETIC-MODEL", MODEL_ID)],
    }
    component_id = f"{MODEL_ID}:component:one"
    component = {
        "component_id": component_id,
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "provenance": [provenance("FACT-SYNTHETIC-COMPONENT", component_id)],
    }
    fault_id = f"{MODEL_ID}:fault:E01"
    fault = {
        "fault_id": fault_id,
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "code": "E01",
        "provenance": [provenance("FACT-SYNTHETIC-FAULT", fault_id)],
    }
    wiring = provenance("FACT-SYNTHETIC-WIRING", MODEL_ID)
    return manifest, decision, equipment_model, component, fault, wiring


class PrivatePackageFixture:
    def __init__(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.private_root = self.root / "private"
        self.package_root = self.private_root / "review" / PACKAGE_ID / "package"
        self.manifest, self.decision, self.equipment_model, self.component, self.fault, self.wiring = package_data()
        self.write()

    def write(self):
        write_json(self.package_root / "package-manifest.json", self.manifest)
        write_json(self.package_root / "review-decision.json", self.decision)
        write_json(self.package_root / "equipment-model.json", self.equipment_model)
        write_json(self.package_root / "components" / "one.json", self.component)
        write_json(self.package_root / "faults" / "E01.json", self.fault)
        write_json(self.package_root / "wiring" / "one.json", self.wiring)

    def close(self):
        self.temporary_directory.cleanup()

    def write_extension(self, package_id="RUN-SYNTHETIC-EXTENSION-001"):
        extension_root = self.private_root / "review" / package_id / "package"
        state_id = f"{MODEL_ID}:state:idle"
        measurement_id = f"{MODEL_ID}:measurement:supply"
        manifest = {
            "schema_version": "1.0.0",
            "package_kind": "KNOWLEDGE_EXTENSION",
            "package_id": package_id,
            "base_package_id": PACKAGE_ID,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "status": "TECHNICALLY_APPROVED_LEGAL_HOLD",
            "assigned_reviewer": REVIEWER_ID,
            "publication_allowed": False,
            "contains_source_binaries": False,
            "document_ids": [DOCUMENT_ID],
            "record_counts": {"operating_states": 1, "measurements": 1},
            "technical_review": {
                "outcome": "ACCEPTED",
                "scope": "ALL_ASSERTIONS",
                "reviewer_id": REVIEWER_ID,
                "reviewed_at": REVIEWED_AT,
                "assertion_count": 2,
                "decision_file": "review-decision.json",
                "legal_hold": True,
            },
        }
        decision = {
            "package_id": package_id,
            "reviewer_id": REVIEWER_ID,
            "outcome": "ACCEPTED",
            "scope": "ALL_ASSERTIONS",
            "reviewed_at": REVIEWED_AT,
            "publication_authorized": False,
        }
        measurement = {
            "schema_version": "1.0.0",
            "measurement_id": measurement_id,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "operating_state_id": state_id,
            "point_a": {"reference_type": "COMPONENT_TERMINAL", "reference_id": self.component["component_id"]},
            "point_b": None,
            "provenance": [extension_provenance("FACT-SYNTHETIC-MEASUREMENT", measurement_id, package_id)],
        }
        state = {
            "schema_version": "1.0.0",
            "state_id": state_id,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "component_commands": [
                {"component_id": self.component["component_id"], "property": "state", "value": "UNKNOWN", "unit": None}
            ],
            "transitions": [],
            "measurement_ids": [measurement_id],
            "provenance": [extension_provenance("FACT-SYNTHETIC-STATE", state_id, package_id)],
        }
        write_json(extension_root / "package-manifest.json", manifest)
        write_json(extension_root / "review-decision.json", decision)
        write_json(extension_root / "measurements" / "supply.json", measurement)
        write_json(extension_root / "operating-states" / "idle.json", state)
        return extension_root, manifest, state

    def write_topology_extension(self, package_id="RUN-SYNTHETIC-TOPOLOGY-001"):
        extension_root = self.private_root / "review" / package_id / "package"
        connector_id = f"{MODEL_ID}:connector:terminal"
        pin_a_id = f"{MODEL_ID}:pin:terminal-a"
        pin_b_id = f"{MODEL_ID}:pin:terminal-b"
        node_a_id = f"{MODEL_ID}:node:terminal-a"
        node_b_id = f"{MODEL_ID}:node:terminal-b"
        connection_id = f"{MODEL_ID}:connection:terminal-a-to-b"
        manifest = {
            "schema_version": "1.0.0",
            "package_kind": "KNOWLEDGE_EXTENSION",
            "package_id": package_id,
            "base_package_id": PACKAGE_ID,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "status": "TECHNICALLY_APPROVED_LEGAL_HOLD",
            "assigned_reviewer": REVIEWER_ID,
            "publication_allowed": False,
            "contains_source_binaries": False,
            "document_ids": [DOCUMENT_ID],
            "record_counts": {"connectors": 1, "pins": 2, "nodes": 2, "connections": 1},
            "technical_review": {
                "outcome": "ACCEPTED",
                "scope": "ALL_ASSERTIONS",
                "reviewer_id": REVIEWER_ID,
                "reviewed_at": REVIEWED_AT,
                "assertion_count": 6,
                "decision_file": "review-decision.json",
                "legal_hold": True,
            },
        }
        decision = {
            "package_id": package_id,
            "reviewer_id": REVIEWER_ID,
            "outcome": "ACCEPTED",
            "scope": "ALL_ASSERTIONS",
            "reviewed_at": REVIEWED_AT,
            "publication_authorized": False,
        }
        connector = {
            "schema_version": "1.0.0",
            "connector_id": connector_id,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "component_id": self.component["component_id"],
            "label": "Synthetic terminal",
            "connector_type": "TERMINAL_BLOCK",
            "keying": None,
            "pin_ids": [pin_a_id, pin_b_id],
            "provenance": [extension_provenance("FACT-SYNTHETIC-CONNECTOR", connector_id, package_id)],
        }
        pins = []
        nodes = []
        for pin_id, pin_number, node_id in (
            (pin_a_id, "A", node_a_id),
            (pin_b_id, "B", node_b_id),
        ):
            pins.append(
                {
                    "schema_version": "1.0.0",
                    "pin_id": pin_id,
                    "model_id": MODEL_ID,
                    "revision_id": REVISION_ID,
                    "connector_id": connector_id,
                    "pin_number": pin_number,
                    "label": pin_number,
                    "node_id": node_id,
                    "signal_type": "LINE_VOLTAGE_AC",
                    "wire_color": None,
                    "measurement_ids": [],
                    "provenance": [extension_provenance(f"FACT-SYNTHETIC-PIN-{pin_number}", pin_id, package_id)],
                }
            )
            nodes.append(
                {
                    "schema_version": "1.0.0",
                    "node_id": node_id,
                    "model_id": MODEL_ID,
                    "revision_id": REVISION_ID,
                    "label": f"Terminal {pin_number}",
                    "node_type": "POWER",
                    "reference_node_id": None,
                    "pin_ids": [pin_id],
                    "provenance": [extension_provenance(f"FACT-SYNTHETIC-NODE-{pin_number}", node_id, package_id)],
                }
            )
        connection = {
            "schema_version": "1.0.0",
            "connection_id": connection_id,
            "model_id": MODEL_ID,
            "revision_id": REVISION_ID,
            "from_node_id": node_a_id,
            "to_node_id": node_b_id,
            "connection_type": "WIRE",
            "controlled_by_component_id": None,
            "normally_closed": None,
            "provenance": [extension_provenance("FACT-SYNTHETIC-CONNECTION", connection_id, package_id)],
        }
        write_json(extension_root / "package-manifest.json", manifest)
        write_json(extension_root / "review-decision.json", decision)
        write_json(extension_root / "connectors" / "terminal.json", connector)
        for pin, node in zip(pins, nodes):
            write_json(extension_root / "pins" / f"{pin['pin_number'].lower()}.json", pin)
            write_json(extension_root / "nodes" / f"{pin['pin_number'].lower()}.json", node)
        write_json(extension_root / "connections" / "terminal-a-to-b.json", connection)
        return extension_root, connection


class PrivatePackageGateTests(unittest.TestCase):
    def setUp(self):
        self.fixture = PrivatePackageFixture()

    def tearDown(self):
        self.fixture.close()

    def load(self):
        return load_private_approved_package(self.fixture.package_root, self.fixture.private_root)

    def test_loads_valid_technically_approved_package(self):
        package = self.load()
        self.assertEqual(package.model_id, MODEL_ID)
        self.assertEqual(len(package.components), 1)
        self.assertEqual(len(package.faults), 1)

    def test_rejects_invalid_package_status(self):
        self.fixture.manifest["status"] = "PENDING_TECHNICAL_REVIEW"
        self.fixture.write()
        with self.assertRaisesRegex(PackageValidationError, "Package status"):
            self.load()

    def test_rejects_missing_provenance(self):
        self.fixture.component["provenance"] = []
        self.fixture.write()
        with self.assertRaisesRegex(PackageValidationError, "missing provenance"):
            self.load()

    def test_rejects_wrong_model_revision(self):
        self.fixture.fault["revision_id"] = "B"
        self.fixture.write()
        with self.assertRaisesRegex(PackageValidationError, "revision mismatch"):
            self.load()

    def test_publication_gate_blocks_legal_hold(self):
        package = self.load()
        with self.assertRaisesRegex(PublicationBlockedError, "legal hold is active"):
            assert_public_export_allowed(package)

    def test_publication_gate_requires_explicit_public_approval(self):
        public_manifest = copy.deepcopy(self.fixture.manifest)
        public_manifest.update(
            {
                "status": "APPROVED_FOR_PUBLICATION",
                "publication_allowed": True,
                "publication_review": {
                    "outcome": "ACCEPTED",
                    "approved_by": "synthetic-publisher",
                    "approved_at": "2026-08-02T01:00:00Z",
                },
            }
        )
        public_manifest["technical_review"]["legal_hold"] = False
        assert_public_export_allowed(public_manifest)

    def test_rejects_package_outside_private_root(self):
        with self.assertRaisesRegex(PackageValidationError, "must remain under private root"):
            load_private_approved_package(self.fixture.package_root, self.fixture.private_root / "different")

    def test_loads_approved_extension_records(self):
        extension_root, _, _ = self.fixture.write_extension()
        package = load_private_approved_package_with_extensions(
            self.fixture.package_root,
            (extension_root,),
            self.fixture.private_root,
        )
        self.assertEqual(len(package.operating_states), 1)
        self.assertEqual(len(package.measurements), 1)
        self.assertEqual(package.extension_package_ids, ("RUN-SYNTHETIC-EXTENSION-001",))

    def test_composes_approved_state_and_topology_extensions(self):
        state_extension_root, _, _ = self.fixture.write_extension()
        topology_extension_root, _ = self.fixture.write_topology_extension()
        package = load_private_approved_package_with_extensions(
            self.fixture.package_root,
            (state_extension_root, topology_extension_root),
            self.fixture.private_root,
        )

        self.assertEqual(len(package.operating_states), 1)
        self.assertEqual(len(package.measurements), 1)
        self.assertEqual(len(package.connectors), 1)
        self.assertEqual(len(package.pins), 2)
        self.assertEqual(len(package.nodes), 2)
        self.assertEqual(len(package.connections), 1)
        self.assertEqual(
            package.extension_package_ids,
            ("RUN-SYNTHETIC-EXTENSION-001", "RUN-SYNTHETIC-TOPOLOGY-001"),
        )

    def test_rejects_topology_extension_with_unknown_endpoint(self):
        topology_extension_root, connection = self.fixture.write_topology_extension()
        connection["to_node_id"] = "UNKNOWN-NODE"
        write_json(topology_extension_root / "connections" / "terminal-a-to-b.json", connection)

        with self.assertRaisesRegex(PackageValidationError, "unknown to node"):
            load_private_approved_package_with_extensions(
                self.fixture.package_root,
                (topology_extension_root,),
                self.fixture.private_root,
            )

    def test_rejects_extension_for_different_base_package(self):
        extension_root, manifest, _ = self.fixture.write_extension()
        manifest["base_package_id"] = "DIFFERENT-BASE"
        write_json(extension_root / "package-manifest.json", manifest)
        with self.assertRaisesRegex(PackageValidationError, "base package ID mismatch"):
            load_private_approved_package_with_extensions(
                self.fixture.package_root,
                (extension_root,),
                self.fixture.private_root,
            )

    def test_rejects_extension_with_unknown_component_reference(self):
        extension_root, _, state = self.fixture.write_extension()
        state["component_commands"][0]["component_id"] = "UNKNOWN-COMPONENT"
        write_json(extension_root / "operating-states" / "idle.json", state)
        with self.assertRaisesRegex(PackageValidationError, "unknown component"):
            load_private_approved_package_with_extensions(
                self.fixture.package_root,
                (extension_root,),
                self.fixture.private_root,
            )


if __name__ == "__main__":
    unittest.main()
