import unittest
from pathlib import Path

from apps.private_simulator.server import (
    STATIC_FILES,
    STATIC_ROOT,
    ApplicationRequestError,
    PrivateSimulatorApplication,
    create_server,
    is_local_host_header,
)
from scripts.private_package_gate import PrivateKnowledgePackage
from simulator import UnknownFaultError, UnknownOperatingStateError


MODEL_ID = "SYNTHETIC-MODEL"
REVISION_ID = "SYNTHETIC-REVISION"
COMPONENT_ID = f"{MODEL_ID}:component:compressor"
STATE_ID = f"{MODEL_ID}:state:cooling"
MEASUREMENT_ID = f"{MODEL_ID}:measurement:control-voltage"
CONNECTOR_ID = f"{MODEL_ID}:connector:compressor"
PIN_A_ID = f"{MODEL_ID}:pin:compressor-a"
PIN_B_ID = f"{MODEL_ID}:pin:compressor-b"
NODE_A_ID = f"{MODEL_ID}:node:compressor-a"
NODE_B_ID = f"{MODEL_ID}:node:compressor-b"
CONNECTION_ID = f"{MODEL_ID}:connection:compressor-a-to-b"
PATH_ID = f"{MODEL_ID}:diagnostic-path:F01"
STEP_ID = f"{PATH_ID}:step:control-voltage"


def topology_provenance(fact_id, entity_id):
    return [
        {
            "fact_id": fact_id,
            "entity_id": entity_id,
            "source": {"document_id": "DOC-SYNTHETIC", "page": 3, "section": "Topology"},
            "validation": {
                "level": "LEVEL_4_TECHNICIAN_REVIEWED",
                "outcome": "ACCEPTED",
                "reviewed_by": "SYNTHETIC-REVIEWER",
                "reviewed_at": "2026-01-01T00:00:00Z",
            },
        }
    ]


def package():
    return PrivateKnowledgePackage(
        root=Path("/synthetic/private/package"),
        manifest={"package_id": "RUN-SYNTHETIC-BASE", "model_id": MODEL_ID, "revision_id": REVISION_ID},
        equipment_model={},
        components=({"component_id": COMPONENT_ID},),
        faults=(
            {
                "fault_id": f"{MODEL_ID}:fault:F01",
                "code": "F01",
                "simulator_effects": [
                    {
                        "target_id": COMPONENT_ID,
                        "property": "availability",
                        "value": False,
                        "unit": None,
                    }
                ],
            },
        ),
        wiring_assertions=(),
        operating_states=(
            {
                "state_id": STATE_ID,
                "name": "Cooling",
                "description": "Synthetic cooling phase",
                "entry_conditions": [],
                "component_commands": [
                    {
                        "component_id": COMPONENT_ID,
                        "property": "operating_state",
                        "value": "RUNNING",
                        "unit": None,
                    }
                ],
                "transitions": [],
                "measurement_ids": [MEASUREMENT_ID],
                "provenance": [
                    {
                        "source": {"document_id": "DOC-SYNTHETIC", "page": 1, "section": "Test"},
                        "validation": {
                            "level": "LEVEL_4_TECHNICIAN_REVIEWED",
                            "outcome": "ACCEPTED",
                            "reviewed_by": "SYNTHETIC-REVIEWER",
                            "reviewed_at": "2026-01-01T00:00:00Z",
                        },
                    }
                ],
            },
        ),
        measurements=(
            {
                "measurement_id": MEASUREMENT_ID,
                "operating_state_id": STATE_ID,
                "name": "Control Voltage",
                "quantity": "VOLTAGE",
                "signal_type": "AC",
                "point_a": {
                    "reference_type": "COMPONENT_TERMINAL",
                    "reference_id": COMPONENT_ID,
                    "label": "A",
                },
                "point_b": None,
                "meter_mode": "VAC",
                "expected": {
                    "nominal": 24,
                    "minimum": 22,
                    "maximum": 26,
                    "unit": "VAC",
                    "interpretation": "Synthetic range",
                },
                "safety_category": "ENERGIZED_LOW_VOLTAGE",
                "procedure": "Synthetic procedure",
                "provenance": [
                    {
                        "source": {"document_id": "DOC-SYNTHETIC", "page": 2, "section": "Test"},
                        "validation": {
                            "level": "LEVEL_4_TECHNICIAN_REVIEWED",
                            "outcome": "ACCEPTED",
                            "reviewed_by": "SYNTHETIC-REVIEWER",
                            "reviewed_at": "2026-01-01T00:00:00Z",
                        },
                    }
                ],
            },
        ),
        connectors=(
            {
                "connector_id": CONNECTOR_ID,
                "component_id": COMPONENT_ID,
                "label": "Compressor terminals",
                "connector_type": "TERMINAL_BLOCK",
                "pin_ids": [PIN_A_ID, PIN_B_ID],
                "provenance": topology_provenance("FACT-SYNTHETIC-CONNECTOR", CONNECTOR_ID),
            },
        ),
        pins=(
            {
                "pin_id": PIN_A_ID,
                "connector_id": CONNECTOR_ID,
                "pin_number": "A",
                "label": "A",
                "node_id": NODE_A_ID,
                "signal_type": "INVERTER_3_PHASE_AC",
                "wire_color": "RED",
                "measurement_ids": [],
                "provenance": topology_provenance("FACT-SYNTHETIC-PIN-A", PIN_A_ID),
            },
            {
                "pin_id": PIN_B_ID,
                "connector_id": CONNECTOR_ID,
                "pin_number": "B",
                "label": "B",
                "node_id": NODE_B_ID,
                "signal_type": "INVERTER_3_PHASE_AC",
                "wire_color": "RED",
                "measurement_ids": [],
                "provenance": topology_provenance("FACT-SYNTHETIC-PIN-B", PIN_B_ID),
            },
        ),
        nodes=(
            {
                "node_id": NODE_A_ID,
                "label": "Compressor terminal A",
                "node_type": "POWER",
                "reference_node_id": None,
                "pin_ids": [PIN_A_ID],
                "provenance": topology_provenance("FACT-SYNTHETIC-NODE-A", NODE_A_ID),
            },
            {
                "node_id": NODE_B_ID,
                "label": "Compressor terminal B",
                "node_type": "POWER",
                "reference_node_id": None,
                "pin_ids": [PIN_B_ID],
                "provenance": topology_provenance("FACT-SYNTHETIC-NODE-B", NODE_B_ID),
            },
        ),
        connections=(
            {
                "connection_id": CONNECTION_ID,
                "from_node_id": NODE_A_ID,
                "to_node_id": NODE_B_ID,
                "connection_type": "WIRE",
                "controlled_by_component_id": None,
                "normally_closed": None,
                "provenance": topology_provenance("FACT-SYNTHETIC-CONNECTION", CONNECTION_ID),
            },
        ),
        diagnostic_paths=(
            {
                "schema_version": "1.0.0",
                "path_id": PATH_ID,
                "model_id": MODEL_ID,
                "revision_id": REVISION_ID,
                "title": "Synthetic F01 diagnostic path",
                "complaint_summary": "Synthetic F01 is active.",
                "entry_fault_ids": [f"{MODEL_ID}:fault:F01"],
                "safety_acknowledgements": [
                    {
                        "acknowledgement_id": f"{PATH_ID}:safety:qualified",
                        "label": "Use the approved low-voltage procedure.",
                        "safety_category": "ENERGIZED_LOW_VOLTAGE",
                        "required": True,
                    }
                ],
                "steps": [
                    {
                        "step_id": STEP_ID,
                        "sequence": 1,
                        "measurement_id": MEASUREMENT_ID,
                        "rationale": "Determine whether control voltage is within the approved range.",
                        "expected_result": {
                            "result_kind": "NUMERIC",
                            "nominal": 24,
                            "minimum": 22,
                            "maximum": 26,
                            "unit": "VAC",
                            "qualitative_value": None,
                        },
                        "branches": [
                            {
                                "branch_id": f"{STEP_ID}:branch:matches",
                                "evaluation": "MATCHES_EXPECTED",
                                "disposition": "COMPLETE",
                                "next_step_id": None,
                                "guidance": "The bounded synthetic path is complete.",
                            },
                            {
                                "branch_id": f"{STEP_ID}:branch:not-matches",
                                "evaluation": "DOES_NOT_MATCH_EXPECTED",
                                "disposition": "ESCALATE",
                                "next_step_id": None,
                                "guidance": "Escalate the synthetic out-of-range result.",
                            },
                            {
                                "branch_id": f"{STEP_ID}:branch:unknown",
                                "evaluation": "UNKNOWN",
                                "disposition": "STOP",
                                "next_step_id": None,
                                "guidance": "Stop because the synthetic result is unknown.",
                            },
                        ],
                    }
                ],
                "provenance": topology_provenance("FACT-SYNTHETIC-PATH", PATH_ID),
            },
        ),
        extension_package_ids=("RUN-SYNTHETIC-STATE", "RUN-SYNTHETIC-PATH"),
    )


def snapshot_request(**overrides):
    values = {
        "power_available": True,
        "operation_requested": True,
        "operating_state_id": STATE_ID,
        "fault_codes": [],
    }
    values.update(overrides)
    return values


def case_request(**overrides):
    values = {
        "case_id": "CASE-SYNTHETIC-001",
        "path_id": PATH_ID,
        "mode": "FIELD",
        "fault_codes": ["F01"],
        "safety_acknowledged": True,
        "results": [],
        "created_at": "2026-08-04T12:00:00Z",
        "updated_at": "2026-08-04T12:00:00Z",
    }
    values.update(overrides)
    return values


def numeric_result(value):
    return {
        "result_id": "RESULT-SYNTHETIC-001",
        "step_id": STEP_ID,
        "measurement_id": MEASUREMENT_ID,
        "source_type": "TECHNICIAN_ENTRY",
        "result_kind": "NUMERIC",
        "numeric_value": value,
        "qualitative_value": None,
        "unit": "VAC",
        "recorded_by": "synthetic-technician",
        "recorded_at": "2026-08-04T12:00:00Z",
        "notes": None,
    }


class PrivateSimulatorApplicationTests(unittest.TestCase):
    def setUp(self):
        self.application = PrivateSimulatorApplication(package())

    def test_lists_only_local_runtime_definitions(self):
        definitions = self.application.definitions()

        self.assertEqual(definitions["classification"], "PRIVATE_LOCAL_ONLY")
        self.assertIs(definitions["automatic_transitions_enabled"], False)
        self.assertEqual(definitions["measurement_behavior"], "REFERENCE_DEFINITION_ONLY")
        self.assertEqual(definitions["topology_behavior"], "REFERENCE_DEFINITION_ONLY")
        self.assertEqual(definitions["diagnostic_case_behavior"], "TECHNICIAN_ENTRY_DETERMINISTIC_EVALUATION")
        self.assertEqual(definitions["model"]["model_id"], MODEL_ID)
        self.assertEqual(definitions["model"]["component_count"], 1)
        self.assertEqual(definitions["fault_codes"], ["F01"])
        self.assertEqual(definitions["operating_states"][0]["state_id"], STATE_ID)
        self.assertEqual(definitions["model"]["connection_count"], 1)
        self.assertEqual(definitions["model"]["diagnostic_path_count"], 1)
        self.assertEqual(definitions["diagnostic_paths"][0]["path_id"], PATH_ID)
        self.assertEqual(definitions["topology"]["connections"][0]["connection_id"], CONNECTION_ID)
        self.assertNotIn("package_root", definitions)

    def test_creates_manual_deterministic_snapshot(self):
        first = self.application.snapshot(snapshot_request())
        second = self.application.snapshot(snapshot_request())

        self.assertEqual(first, second)
        self.assertEqual(first["step_index"], 0)
        self.assertEqual(first["selected_operating_state_id"], STATE_ID)
        self.assertEqual(first["applied_commands"][0]["value"], "RUNNING")
        self.assertEqual(first["diagnostic_measurements"][0]["measurement_id"], MEASUREMENT_ID)
        self.assertEqual(
            first["diagnostic_measurements"][0]["sources"][0]["validation_level"],
            "LEVEL_4_TECHNICIAN_REVIEWED",
        )

    def test_applies_exact_approved_fault(self):
        snapshot = self.application.snapshot(snapshot_request(fault_codes=["F01"]))

        self.assertEqual(snapshot["status"], "FAULT_ACTIVE")
        self.assertEqual(snapshot["active_fault_codes"], ["F01"])
        self.assertEqual(snapshot["applied_effects"][0]["value"], False)

    def test_evaluates_technician_entered_case_result(self):
        awaiting = self.application.case_snapshot(case_request())
        completed = self.application.case_snapshot(case_request(results=[numeric_result(24)]))

        self.assertEqual(awaiting["state"], "AWAITING_RESULT")
        self.assertEqual(awaiting["current_step_id"], STEP_ID)
        self.assertEqual(completed["state"], "COMPLETE")
        self.assertEqual(completed["evaluation"]["outcome"], "MATCHES_EXPECTED")
        self.assertEqual(completed["results"][0]["source_type"], "TECHNICIAN_ENTRY")

    def test_rejects_invalid_request_shapes(self):
        invalid_requests = (
            None,
            {},
            snapshot_request(power_available=1),
            snapshot_request(operating_state_id=""),
            snapshot_request(fault_codes="F01"),
            {**snapshot_request(), "automatic_transitions": True},
        )

        for request in invalid_requests:
            with self.subTest(request=request), self.assertRaises(ApplicationRequestError):
                self.application.snapshot(request)

    def test_rejects_unknown_exact_identifiers(self):
        with self.assertRaises(UnknownOperatingStateError):
            self.application.snapshot(snapshot_request(operating_state_id="UNKNOWN"))
        with self.assertRaises(UnknownFaultError):
            self.application.snapshot(snapshot_request(fault_codes=["UNKNOWN"]))

    def test_server_binds_only_to_loopback(self):
        server = create_server(self.application, port=0)
        try:
            self.assertEqual(server.server_address[0], "127.0.0.1")
        finally:
            server.server_close()

    def test_host_header_allows_only_loopback_names(self):
        self.assertTrue(is_local_host_header("127.0.0.1:8765"))
        self.assertTrue(is_local_host_header("localhost:8765"))
        self.assertFalse(is_local_host_header("example.com"))
        self.assertFalse(is_local_host_header("192.168.1.10:8765"))
        self.assertFalse(is_local_host_header(None))

    def test_static_assets_are_fixed_and_contain_no_private_package_data(self):
        self.assertEqual(set(STATIC_FILES), {"/", "/assets/app.css", "/assets/app.js"})
        static_text = "\n".join(
            (STATIC_ROOT / filename).read_text(encoding="utf-8")
            for filename, _content_type in STATIC_FILES.values()
        )
        self.assertNotIn("sources/private", static_text)
        self.assertNotIn("ASXS6S4810AA", static_text)

    def test_meter_interface_is_explicitly_reference_only_and_traceable(self):
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        javascript = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn("Reference only", html)
        self.assertIn("No live or simulated reading is generated", html)
        self.assertIn("Manufacturer verification pending", html)
        self.assertIn("REFERENCE_DEFINITION_ONLY", javascript)
        self.assertIn("validation_level", javascript)
        self.assertIn("reviewed_by", javascript)

    def test_commands_and_diagnostics_have_explicit_controls(self):
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        javascript = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
        stylesheet = (STATIC_ROOT / "app.css").read_text(encoding="utf-8")

        self.assertIn('id="diagnostic-select"', html)
        self.assertIn("Load approved diagnostic test", html)
        self.assertIn("Variable steps 0–8", javascript)
        self.assertIn("Exact compressor demand percentage is not specified", javascript)
        self.assertIn("Inspect test", javascript)
        self.assertIn("diagnostic-name-button", stylesheet)

    def test_topology_interface_is_reference_only_and_non_simulating(self):
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        javascript = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="topology-view"', html)
        self.assertIn("No voltage propagation, switching, current flow, or live state is calculated", html)
        self.assertIn("topology_behavior", javascript)
        self.assertIn("REFERENCE_DEFINITION_ONLY", javascript)
        self.assertIn("renderTopology", javascript)

    def test_case_interface_requires_technician_entry_and_deterministic_evaluation(self):
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        javascript = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="case-path-select"', html)
        self.assertIn("One approved test at a time", html)
        self.assertIn("Technician-entered actual result", html)
        self.assertIn("does not connect to or measure the equipment", html)
        self.assertIn("TECHNICIAN_ENTRY_DETERMINISTIC_EVALUATION", javascript)
        self.assertIn('requestJson("/api/case"', javascript)
        self.assertIn('source_type: "TECHNICIAN_ENTRY"', javascript)


if __name__ == "__main__":
    unittest.main()
