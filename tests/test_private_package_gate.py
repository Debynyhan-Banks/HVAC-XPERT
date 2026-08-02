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


if __name__ == "__main__":
    unittest.main()
