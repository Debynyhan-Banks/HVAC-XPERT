import argparse
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.private_package_gate import PrivateKnowledgePackage
from scripts.run_simulator import json_value, run


def package():
    return PrivateKnowledgePackage(
        root=Path("/synthetic/private/package"),
        manifest={"model_id": "SYNTHETIC-MODEL", "revision_id": "A"},
        equipment_model={},
        components=(),
        faults=(),
        wiring_assertions=(),
    )


def arguments(**overrides):
    values = {
        "package": Path("/synthetic/private/package"),
        "extension": [],
        "private_root": Path("/synthetic/private"),
        "state": None,
        "fault": [],
        "power_available": True,
        "operation_requested": False,
        "list_states": False,
        "list_measurements": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


class SimulatorRunnerTests(unittest.TestCase):
    @patch("scripts.run_simulator.load_private_approved_package_with_extensions", return_value=package())
    def test_emits_json_ready_snapshot(self, _loader):
        output = json_value(run(arguments()))

        self.assertEqual(output["status"], "IDLE")
        self.assertEqual(output["model_id"], "SYNTHETIC-MODEL")
        self.assertEqual(output["components"], [])

    @patch("scripts.run_simulator.load_private_approved_package_with_extensions", return_value=package())
    def test_lists_approved_definitions_without_stepping(self, _loader):
        output = json_value(run(arguments(list_states=True, list_measurements=True)))

        self.assertEqual(output, {"operating_states": [], "diagnostic_measurements": []})


if __name__ == "__main__":
    unittest.main()
