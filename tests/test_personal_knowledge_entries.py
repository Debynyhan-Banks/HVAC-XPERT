import json
import stat
import tempfile
import unittest
from pathlib import Path

from personal_knowledge import PersonalEntryStore, PersonalEntryValidationError


def equipment(revision="REV-A"):
    return {
        "manufacturer": "Synthetic Manufacturer",
        "brand": "Synthetic Brand",
        "model_number": "SYN-36HP",
        "revision": revision,
    }


def manual_evidence():
    return {
        "context_type": "MANUAL",
        "document_id": "DOC-SYNTHETIC-SERVICE",
        "page": 42,
        "field_context": None,
    }


def field_evidence():
    return {
        "context_type": "FIELD",
        "document_id": None,
        "page": None,
        "field_context": "Observed on the applicable synthetic unit during a private service call.",
    }


def fault_request(**overrides):
    values = {
        "entry_kind": "FAULT",
        "equipment": equipment(),
        "title": "Synthetic pressure-switch fault",
        "details": {
            "fault_code": "F42",
            "meaning": "Synthetic pressure-switch circuit condition.",
            "notes": None,
        },
        "evidence": manual_evidence(),
        "safety_category": "NOT_ACTIONABLE",
        "confidence_status": "MANUAL_CONFIRMED",
    }
    values.update(overrides)
    return values


def measurement_request(**overrides):
    values = {
        "entry_kind": "MEASUREMENT",
        "equipment": equipment(),
        "title": "Synthetic control-voltage test",
        "details": {
            "name": "Control voltage",
            "meter_mode": "VAC",
            "point_a": "Terminal R",
            "point_b": "Terminal C",
            "expected_result": {
                "result_kind": "NUMERIC",
                "nominal": 24,
                "minimum": 22,
                "maximum": 26,
                "unit": "VAC",
                "qualitative_value": None,
            },
            "procedure": "Use the applicable synthetic low-voltage procedure.",
        },
        "evidence": field_evidence(),
        "safety_category": "ENERGIZED_LOW_VOLTAGE",
        "confidence_status": "FIELD_CONFIRMED",
    }
    values.update(overrides)
    return values


class PersonalEntryStoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "private" / "personal-entries"
        self.store = PersonalEntryStore(self.root)

    def test_saves_confirmed_reference_entry_as_private_json(self):
        record = self.store.create(fault_request())

        self.assertEqual(record["entry_kind"], "FAULT")
        self.assertEqual(record["confidence_status"], "MANUAL_CONFIRMED")
        self.assertEqual(record["guidance_status"], "REFERENCE_ONLY_CONFIRMED")
        self.assertIs(record["deterministic_guidance_active"], False)
        destination = self.root / f"{record['entry_id']}.json"
        self.assertTrue(destination.is_file())
        self.assertEqual(json.loads(destination.read_text(encoding="utf-8")), record)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_marks_confirmed_actionable_entry_for_rule_review_without_activating_it(self):
        record = self.store.create(measurement_request())

        self.assertEqual(record["guidance_status"], "ELIGIBLE_FOR_RULE_REVIEW")
        self.assertIs(record["deterministic_guidance_active"], False)
        self.assertEqual(record["details"]["expected_result"]["minimum"], 22)

    def test_unverified_entry_with_unknown_revision_and_safety_fails_closed(self):
        request = measurement_request(
            equipment=equipment(revision=None),
            confidence_status="UNVERIFIED",
            safety_category="UNKNOWN",
        )

        record = self.store.create(request)

        self.assertEqual(record["guidance_status"], "BLOCKED_UNVERIFIED")
        self.assertIs(record["deterministic_guidance_active"], False)

    def test_conflicted_entry_fails_closed(self):
        request = measurement_request(confidence_status="CONFLICTED")

        record = self.store.create(request)

        self.assertEqual(record["guidance_status"], "BLOCKED_CONFLICTED")

    def test_rejects_confirmed_entry_without_exact_revision(self):
        with self.assertRaisesRegex(PersonalEntryValidationError, "exact revision"):
            self.store.create(fault_request(equipment=equipment(revision=None)))

    def test_rejects_manual_confirmation_without_manual_evidence(self):
        with self.assertRaisesRegex(PersonalEntryValidationError, "MANUAL_CONFIRMED"):
            self.store.create(fault_request(evidence=field_evidence()))

    def test_rejects_manual_evidence_without_page(self):
        evidence = manual_evidence()
        evidence["page"] = None

        with self.assertRaisesRegex(PersonalEntryValidationError, "positive page"):
            self.store.create(fault_request(evidence=evidence))

    def test_rejects_confirmed_actionable_entry_with_unknown_safety(self):
        with self.assertRaisesRegex(PersonalEntryValidationError, "specific safety"):
            self.store.create(measurement_request(safety_category="UNKNOWN"))

    def test_rejects_invalid_numeric_range(self):
        request = measurement_request()
        request["details"]["expected_result"]["minimum"] = 27

        with self.assertRaisesRegex(PersonalEntryValidationError, "minimum cannot exceed"):
            self.store.create(request)

    def test_rejects_unexpected_fields(self):
        request = fault_request()
        request["publish"] = True

        with self.assertRaisesRegex(PersonalEntryValidationError, "Unexpected request fields"):
            self.store.create(request)


if __name__ == "__main__":
    unittest.main()
