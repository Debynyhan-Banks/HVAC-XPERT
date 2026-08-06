import json
import stat
import tempfile
import unittest
from pathlib import Path

from personal_knowledge import PersonalCaseStore, PersonalCaseValidationError


def case_snapshot(**overrides):
    values = {
        "schema_version": "1.0.0",
        "case_id": "CASE-SYNTHETIC-001",
        "model_id": "SYNTHETIC-MODEL",
        "revision_id": "REV-A",
        "knowledge_package_ids": ["RUN-SYNTHETIC-001"],
        "path_id": "SYNTHETIC-MODEL:diagnostic-path:F42",
        "mode": "FIELD",
        "state": "ESCALATION_REQUIRED",
        "complaint_summary": "Synthetic unit reports F42 and does not operate.",
        "fault_codes": ["F42"],
        "safety_acknowledged": True,
        "current_step_id": None,
        "results": [
            {
                "result_id": "CASE-SYNTHETIC-001:result:1",
                "step_id": "SYNTHETIC-MODEL:step:pressure-switch",
                "measurement_id": "SYNTHETIC-MODEL:measurement:pressure-switch",
                "source_type": "TECHNICIAN_ENTRY",
                "result_kind": "QUALITATIVE",
                "numeric_value": None,
                "qualitative_value": "NO_CONTINUITY",
                "unit": None,
                "recorded_by": "Synthetic Technician",
                "recorded_at": "2026-08-05T12:01:00Z",
                "notes": None,
            }
        ],
        "evaluation": {
            "step_id": "SYNTHETIC-MODEL:step:pressure-switch",
            "measurement_id": "SYNTHETIC-MODEL:measurement:pressure-switch",
            "outcome": "DOES_NOT_MATCH_EXPECTED",
            "branch_id": "SYNTHETIC-MODEL:branch:escalate",
        },
        "disposition": "ESCALATE",
        "guidance": "Escalate the bounded synthetic case.",
        "created_at": "2026-08-05T12:00:00Z",
        "updated_at": "2026-08-05T12:01:00Z",
    }
    values.update(overrides)
    return values


class PersonalCaseStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "private" / "cases"
        self.store = PersonalCaseStore(self.root)

    def test_saves_private_field_case_with_owner_only_permissions(self):
        record = self.store.save(case_snapshot())

        destination = self.root / "CASE-SYNTHETIC-001.json"
        self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), record)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_searches_case_by_model_fault_complaint_and_recorder(self):
        self.store.save(case_snapshot())

        self.assertEqual(len(self.store.search("SYNTHETIC-MODEL")), 1)
        self.assertEqual(len(self.store.search("F42 operate")), 1)
        self.assertEqual(len(self.store.search("Synthetic Technician")), 1)
        self.assertEqual(len(self.store.search("not-present")), 0)

    def test_updates_same_case_with_newer_snapshot(self):
        self.store.save(case_snapshot())
        updated = case_snapshot(updated_at="2026-08-05T12:02:00Z", guidance="Updated bounded guidance.")

        record = self.store.save(updated)

        self.assertEqual(record["guidance"], "Updated bounded guidance.")
        self.assertEqual(self.store.search()[0]["updated_at"], "2026-08-05T12:02:00Z")

    def test_rejects_case_without_technician_result(self):
        with self.assertRaisesRegex(PersonalCaseValidationError, "technician result"):
            self.store.save(case_snapshot(results=[]))

    def test_rejects_training_case(self):
        with self.assertRaisesRegex(PersonalCaseValidationError, "Only field cases"):
            self.store.save(case_snapshot(mode="TRAINING"))

    def test_rejects_case_without_safety_acknowledgement(self):
        with self.assertRaisesRegex(PersonalCaseValidationError, "safety acknowledgement"):
            self.store.save(case_snapshot(safety_acknowledged=False))

    def test_rejects_older_snapshot_overwrite(self):
        self.store.save(case_snapshot(updated_at="2026-08-05T12:02:00Z"))

        with self.assertRaisesRegex(PersonalCaseValidationError, "newer private case"):
            self.store.save(case_snapshot(updated_at="2026-08-05T12:01:00Z"))


if __name__ == "__main__":
    unittest.main()
