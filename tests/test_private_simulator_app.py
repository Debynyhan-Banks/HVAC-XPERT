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


def package():
    return PrivateKnowledgePackage(
        root=Path("/synthetic/private/package"),
        manifest={"model_id": MODEL_ID, "revision_id": REVISION_ID},
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


class PrivateSimulatorApplicationTests(unittest.TestCase):
    def setUp(self):
        self.application = PrivateSimulatorApplication(package())

    def test_lists_only_local_runtime_definitions(self):
        definitions = self.application.definitions()

        self.assertEqual(definitions["classification"], "PRIVATE_LOCAL_ONLY")
        self.assertIs(definitions["automatic_transitions_enabled"], False)
        self.assertEqual(definitions["measurement_behavior"], "REFERENCE_DEFINITION_ONLY")
        self.assertEqual(definitions["model"]["model_id"], MODEL_ID)
        self.assertEqual(definitions["model"]["component_count"], 1)
        self.assertEqual(definitions["fault_codes"], ["F01"])
        self.assertEqual(definitions["operating_states"][0]["state_id"], STATE_ID)
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


if __name__ == "__main__":
    unittest.main()
