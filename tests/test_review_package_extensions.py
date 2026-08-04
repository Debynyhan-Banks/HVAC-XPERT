import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_review_package
from scripts.apply_review_decision import apply


PACKAGE_ID = "RUN-SYNTHETIC-EXTENSION"
BASE_PACKAGE_ID = "RUN-SYNTHETIC-BASE"
MODEL_ID = "SYNTHETIC-MODEL"
REVISION_ID = "A"
REVIEWER_ID = "synthetic-reviewer"
DOCUMENT_ID = "DOC-SYNTHETIC"
REVIEWED_AT = "2026-08-02T00:00:00Z"
COMPONENT_ID = f"{MODEL_ID}:component:one"
STATE_ID = f"{MODEL_ID}:state:idle"
MEASUREMENT_ID = f"{MODEL_ID}:measurement:supply"
CONNECTOR_ID = f"{MODEL_ID}:connector:terminal-block"
PIN_A_ID = f"{MODEL_ID}:pin:terminal-a"
PIN_B_ID = f"{MODEL_ID}:pin:terminal-b"
NODE_A_ID = f"{MODEL_ID}:node:terminal-a"
NODE_B_ID = f"{MODEL_ID}:node:terminal-b"
CONNECTION_ID = f"{MODEL_ID}:connection:terminal-a-to-b"


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
            "document_title": "Synthetic Document",
            "page": 1,
            "section": "Synthetic",
            "source_url": None,
            "document_revision": None,
        },
        "extraction": {
            "method": "MANUAL_ENTRY",
            "confidence": 1.0,
            "extracted_at": REVIEWED_AT,
            "provider": None,
            "model_version": None,
            "prompt_version": None,
            "run_id": PACKAGE_ID,
        },
        "validation": {
            "level": "LEVEL_1_AI_EXTRACTED",
            "outcome": "PENDING",
            "reviewed_by": None,
            "reviewed_at": None,
            "notes": "Synthetic pending review",
        },
    }


class ReviewPackageExtensionTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.review_root = self.root / "review"
        self.manifest_root = self.root / "manifests"
        self.package_root = self.review_root / PACKAGE_ID / "package"
        self.original_review_root = validate_review_package.PRIVATE_REVIEW_ROOT
        self.original_manifest_root = validate_review_package.MANIFEST_ROOT
        validate_review_package.PRIVATE_REVIEW_ROOT = self.review_root
        validate_review_package.MANIFEST_ROOT = self.manifest_root
        self.write_fixture()

    def tearDown(self):
        validate_review_package.PRIVATE_REVIEW_ROOT = self.original_review_root
        validate_review_package.MANIFEST_ROOT = self.original_manifest_root
        self.temporary_directory.cleanup()

    def write_fixture(self):
        base_root = self.review_root / BASE_PACKAGE_ID / "package"
        write_json(
            base_root / "package-manifest.json",
            {
                "package_id": BASE_PACKAGE_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "status": "TECHNICALLY_APPROVED_LEGAL_HOLD",
            },
        )
        write_json(base_root / "components" / "one.json", {"component_id": COMPONENT_ID})
        write_json(
            self.manifest_root / f"{DOCUMENT_ID}.json",
            {"document_id": DOCUMENT_ID, "fingerprint": {"page_count": 1}},
        )
        write_json(
            self.package_root / "package-manifest.json",
            {
                "schema_version": "1.0.0",
                "package_kind": "KNOWLEDGE_EXTENSION",
                "package_id": PACKAGE_ID,
                "base_package_id": BASE_PACKAGE_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "status": "PENDING_TECHNICAL_REVIEW",
                "assigned_reviewer": REVIEWER_ID,
                "publication_allowed": False,
                "contains_source_binaries": False,
                "document_ids": [DOCUMENT_ID],
                "record_counts": {"operating_states": 1, "measurements": 1},
                "technical_review": {
                    "outcome": "PENDING",
                    "scope": "ALL_ASSERTIONS",
                    "reviewer_id": REVIEWER_ID,
                    "reviewed_at": None,
                    "assertion_count": 2,
                    "decision_file": None,
                    "legal_hold": True,
                },
            },
        )
        write_json(
            self.package_root / "operating-states" / "idle.json",
            {
                "schema_version": "1.0.0",
                "state_id": STATE_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "name": "Idle",
                "description": None,
                "entry_conditions": [],
                "component_commands": [
                    {"component_id": COMPONENT_ID, "property": "state", "value": "UNKNOWN", "unit": None}
                ],
                "transitions": [],
                "measurement_ids": [MEASUREMENT_ID],
                "provenance": [provenance("FACT-SYNTHETIC-STATE", STATE_ID)],
            },
        )
        write_json(
            self.package_root / "measurements" / "supply.json",
            {
                "schema_version": "1.0.0",
                "measurement_id": MEASUREMENT_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "operating_state_id": STATE_ID,
                "name": "Supply",
                "quantity": "VOLTAGE",
                "signal_type": "AC",
                "point_a": {"reference_type": "COMPONENT_TERMINAL", "reference_id": COMPONENT_ID, "label": "A"},
                "point_b": None,
                "meter_mode": "VAC",
                "expected": {"nominal": None, "minimum": None, "maximum": None, "unit": "VAC", "interpretation": None},
                "safety_category": "ENERGIZED_LINE_VOLTAGE",
                "procedure": None,
                "provenance": [provenance("FACT-SYNTHETIC-MEASUREMENT", MEASUREMENT_ID)],
            },
        )
        (self.package_root / "REVIEW_SUMMARY.md").write_text(
            "- Status: `PENDING_TECHNICAL_REVIEW`\n- Publication allowed: No\n",
            encoding="utf-8",
        )

    def validate(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return validate_review_package.validate(self.package_root)

    def write_topology_fixture(self):
        manifest_path = self.package_root / "package-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["record_counts"].update({"connectors": 1, "pins": 2, "nodes": 2, "connections": 1})
        manifest["technical_review"]["assertion_count"] = 8
        write_json(manifest_path, manifest)
        write_json(
            self.package_root / "connectors" / "terminal-block.json",
            {
                "schema_version": "1.0.0",
                "connector_id": CONNECTOR_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "component_id": COMPONENT_ID,
                "label": "Synthetic terminal block",
                "connector_type": "TERMINAL_BLOCK",
                "keying": None,
                "pin_ids": [PIN_A_ID, PIN_B_ID],
                "provenance": [provenance("FACT-SYNTHETIC-CONNECTOR", CONNECTOR_ID)],
            },
        )
        for pin_id, pin_number, node_id in (
            (PIN_A_ID, "A", NODE_A_ID),
            (PIN_B_ID, "B", NODE_B_ID),
        ):
            write_json(
                self.package_root / "pins" / f"{pin_number.lower()}.json",
                {
                    "schema_version": "1.0.0",
                    "pin_id": pin_id,
                    "model_id": MODEL_ID,
                    "revision_id": REVISION_ID,
                    "connector_id": CONNECTOR_ID,
                    "pin_number": pin_number,
                    "label": pin_number,
                    "node_id": node_id,
                    "signal_type": "LINE_VOLTAGE_AC" if pin_number == "A" else "INVERTER_3_PHASE_AC",
                    "wire_color": None,
                    "measurement_ids": [],
                    "provenance": [provenance(f"FACT-SYNTHETIC-PIN-{pin_number}", pin_id)],
                },
            )
            write_json(
                self.package_root / "nodes" / f"{pin_number.lower()}.json",
                {
                    "schema_version": "1.0.0",
                    "node_id": node_id,
                    "model_id": MODEL_ID,
                    "revision_id": REVISION_ID,
                    "label": f"Terminal {pin_number}",
                    "node_type": "POWER",
                    "reference_node_id": None,
                    "pin_ids": [pin_id],
                    "provenance": [provenance(f"FACT-SYNTHETIC-NODE-{pin_number}", node_id)],
                },
            )
        write_json(
            self.package_root / "connections" / "terminal-a-to-b.json",
            {
                "schema_version": "1.0.0",
                "connection_id": CONNECTION_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "from_node_id": NODE_A_ID,
                "to_node_id": NODE_B_ID,
                "connection_type": "WIRE",
                "controlled_by_component_id": None,
                "normally_closed": None,
                "provenance": [provenance("FACT-SYNTHETIC-CONNECTION", CONNECTION_ID)],
            },
        )
        (self.package_root / "REVIEW_SUMMARY.md").write_text(
            """# Synthetic Topology Review

- Status: `PENDING_TECHNICAL_REVIEW`
- Publication allowed: No

## Review actions

1. Compare every connector, pin, node, and connection to the cited private page 50.
2. Confirm the black/red supply mapping and red/yellow/blue compressor mapping.
3. Confirm positional fan-terminal mapping is acceptable while numeric identifiers remain unknown.
4. Reject or revise any record that overstates the diagram.
5. Keep `publication_authorized` false because the source-rights hold remains.
""",
            encoding="utf-8",
        )

    def test_validates_pending_extension_and_complete_approval(self):
        self.write_topology_fixture()
        self.assertEqual(self.validate(), 0)
        decision_path = self.package_root / "review-decision.json"
        write_json(
            decision_path,
            {
                "package_id": PACKAGE_ID,
                "reviewer_id": REVIEWER_ID,
                "outcome": "ACCEPTED",
                "scope": "ALL_ASSERTIONS",
                "reviewed_at": REVIEWED_AT,
                "reviewer_statement": "Synthetic approval",
                "publication_authorized": False,
            },
        )

        with contextlib.redirect_stdout(io.StringIO()):
            apply(self.package_root, decision_path)

        self.assertEqual(self.validate(), 0)
        approved_state = json.loads(
            (self.package_root / "operating-states" / "idle.json").read_text(encoding="utf-8")
        )
        self.assertEqual(approved_state["provenance"][0]["validation"]["level"], "LEVEL_4_TECHNICIAN_REVIEWED")
        approved_connector = json.loads(
            (self.package_root / "connectors" / "terminal-block.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            approved_connector["provenance"][0]["validation"]["level"],
            "LEVEL_4_TECHNICIAN_REVIEWED",
        )
        approved_summary = (self.package_root / "REVIEW_SUMMARY.md").read_text(encoding="utf-8")
        self.assertNotIn("PENDING_TECHNICAL_REVIEW", approved_summary)
        self.assertNotIn("## Review actions", approved_summary)
        self.assertIn("All 8 topology assertions were accepted", approved_summary)

    def test_rejects_unknown_component_command(self):
        state_path = self.package_root / "operating-states" / "idle.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["component_commands"][0]["component_id"] = "UNKNOWN-COMPONENT"
        write_json(state_path, state)
        self.assertEqual(self.validate(), 1)

    def test_rejects_incorrect_pending_assertion_count(self):
        manifest_path = self.package_root / "package-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["technical_review"]["assertion_count"] = 1
        write_json(manifest_path, manifest)
        self.assertEqual(self.validate(), 1)

    def test_rejects_unknown_topology_reference(self):
        self.write_topology_fixture()
        pin_path = self.package_root / "pins" / "a.json"
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        pin["node_id"] = "UNKNOWN-NODE"
        write_json(pin_path, pin)

        self.assertEqual(self.validate(), 1)

    def test_rejects_invalid_topology_enum(self):
        self.write_topology_fixture()
        connector_path = self.package_root / "connectors" / "terminal-block.json"
        connector = json.loads(connector_path.read_text(encoding="utf-8"))
        connector["connector_type"] = "INVENTED"
        write_json(connector_path, connector)

        self.assertEqual(self.validate(), 1)


if __name__ == "__main__":
    unittest.main()
