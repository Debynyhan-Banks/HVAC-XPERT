import copy
import unittest
from pathlib import Path

from diagnostics import (
    CaseState,
    DiagnosticCaseEngine,
    DiagnosticCaseInputError,
    DiagnosticDefinitionError,
    EvaluationOutcome,
    UnknownDiagnosticPathError,
)
from scripts.private_package_gate import PrivateKnowledgePackage


MODEL_ID = "SYNTHETIC-MODEL"
REVISION_ID = "A"
FAULT_ID = f"{MODEL_ID}:fault:E24"
MEASUREMENT_ID = f"{MODEL_ID}:measurement:hps-continuity"
PATH_ID = f"{MODEL_ID}:diagnostic-path:E24-hps-open"
STEP_ID = f"{PATH_ID}:step:continuity"
TIMESTAMP = "2026-08-04T12:00:00Z"


def source_provenance(entity_id):
    return [
        {
            "entity_id": entity_id,
            "source": {"document_id": "DOC-SYNTHETIC", "page": 1, "section": "Synthetic"},
            "validation": {
                "level": "LEVEL_4_TECHNICIAN_REVIEWED",
                "outcome": "ACCEPTED",
                "reviewed_by": "synthetic-reviewer",
                "reviewed_at": TIMESTAMP,
            },
        }
    ]


def diagnostic_path():
    return {
        "schema_version": "1.0.0",
        "path_id": PATH_ID,
        "model_id": MODEL_ID,
        "revision_id": REVISION_ID,
        "title": "E24 high-pressure-switch open",
        "complaint_summary": "Active E24 indicates the high-pressure switch is open.",
        "entry_fault_ids": [FAULT_ID],
        "safety_acknowledgements": [
            {
                "acknowledgement_id": f"{PATH_ID}:safety:disconnect-power",
                "label": "Disconnect all power before servicing.",
                "safety_category": "DEENERGIZED_ONLY",
                "required": True,
            }
        ],
        "steps": [
            {
                "step_id": STEP_ID,
                "sequence": 1,
                "measurement_id": MEASUREMENT_ID,
                "rationale": "Check whether the high-pressure-switch circuit is open.",
                "expected_result": {
                    "result_kind": "QUALITATIVE",
                    "nominal": None,
                    "minimum": None,
                    "maximum": None,
                    "unit": None,
                    "qualitative_value": "CONTINUITY",
                },
                "branches": [
                    {
                        "branch_id": f"{STEP_ID}:branch:matches",
                        "evaluation": "MATCHES_EXPECTED",
                        "disposition": "ESCALATE",
                        "next_step_id": None,
                        "guidance": "The open-switch condition was not reproduced; no further approved branch exists.",
                    },
                    {
                        "branch_id": f"{STEP_ID}:branch:not-matches",
                        "evaluation": "DOES_NOT_MATCH_EXPECTED",
                        "disposition": "ESCALATE",
                        "next_step_id": None,
                        "guidance": "The circuit is open; escalate for service-action review.",
                    },
                    {
                        "branch_id": f"{STEP_ID}:branch:unknown",
                        "evaluation": "UNKNOWN",
                        "disposition": "STOP",
                        "next_step_id": None,
                        "guidance": "The result is unknown; stop or repeat the approved test.",
                    },
                ],
            }
        ],
        "provenance": source_provenance(PATH_ID),
    }


def package(path_record=None):
    component_id = f"{MODEL_ID}:component:hps"
    return PrivateKnowledgePackage(
        root=Path("/synthetic/private/package"),
        manifest={"package_id": "RUN-SYNTHETIC-BASE", "model_id": MODEL_ID, "revision_id": REVISION_ID},
        equipment_model={},
        components=({"component_id": component_id},),
        faults=(
            {
                "fault_id": FAULT_ID,
                "code": "E24",
                "simulator_effects": [],
            },
        ),
        wiring_assertions=(),
        measurements=(
            {
                "measurement_id": MEASUREMENT_ID,
                "operating_state_id": None,
                "name": "High-pressure-switch continuity",
                "quantity": "CONTINUITY",
                "signal_type": "NONE",
                "point_a": {"reference_type": "COMPONENT_TERMINAL", "reference_id": component_id, "label": "A"},
                "point_b": {"reference_type": "COMPONENT_TERMINAL", "reference_id": component_id, "label": "B"},
                "meter_mode": "CONTINUITY",
                "expected": {
                    "nominal": None,
                    "minimum": None,
                    "maximum": None,
                    "unit": None,
                    "interpretation": "Continuity indicates closed; no continuity indicates open.",
                },
                "safety_category": "DEENERGIZED_ONLY",
                "procedure": "Disconnect all power and check continuity.",
                "provenance": source_provenance(MEASUREMENT_ID),
            },
        ),
        diagnostic_paths=((path_record or diagnostic_path()),),
        extension_package_ids=("RUN-SYNTHETIC-MEASUREMENTS", "RUN-SYNTHETIC-PATH"),
    )


def case_request(**overrides):
    values = {
        "case_id": "CASE-SYNTHETIC-001",
        "path_id": PATH_ID,
        "mode": "FIELD",
        "fault_codes": ["E24"],
        "safety_acknowledged": False,
        "results": [],
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    }
    values.update(overrides)
    return values


def qualitative_result(value="CONTINUITY", **overrides):
    result = {
        "result_id": "RESULT-SYNTHETIC-001",
        "step_id": STEP_ID,
        "measurement_id": MEASUREMENT_ID,
        "source_type": "TECHNICIAN_ENTRY",
        "result_kind": "QUALITATIVE",
        "numeric_value": None,
        "qualitative_value": value,
        "unit": None,
        "recorded_by": "synthetic-technician",
        "recorded_at": TIMESTAMP,
        "notes": None,
    }
    result.update(overrides)
    return result


class DiagnosticCaseEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = DiagnosticCaseEngine(package())

    def test_lists_reviewed_path_and_measurement_definition(self):
        path = self.engine.diagnostic_paths[0]

        self.assertEqual(path.path_id, PATH_ID)
        self.assertEqual(path.entry_fault_codes, ("E24",))
        self.assertEqual(path.steps[0].measurement.measurement_id, MEASUREMENT_ID)
        self.assertEqual(path.sources[0].validation_level, "LEVEL_4_TECHNICIAN_REVIEWED")

    def test_requires_safety_acknowledgement_before_loading_test(self):
        snapshot = self.engine.evaluate(case_request())

        self.assertEqual(snapshot.state, CaseState.SAFETY_ACKNOWLEDGEMENT_REQUIRED)
        self.assertIsNone(snapshot.current_step_id)
        with self.assertRaisesRegex(DiagnosticCaseInputError, "before required safety"):
            self.engine.evaluate(case_request(results=[qualitative_result()]))

    def test_loads_first_test_after_safety_acknowledgement(self):
        snapshot = self.engine.evaluate(case_request(safety_acknowledged=True))

        self.assertEqual(snapshot.state, CaseState.AWAITING_RESULT)
        self.assertEqual(snapshot.current_step_id, STEP_ID)
        self.assertEqual(snapshot.fault_codes, ("E24",))

    def test_evaluates_continuity_as_matching_expected(self):
        snapshot = self.engine.evaluate(
            case_request(safety_acknowledged=True, results=[qualitative_result("CONTINUITY")])
        )

        self.assertEqual(snapshot.state, CaseState.ESCALATION_REQUIRED)
        self.assertEqual(snapshot.evaluation.outcome, EvaluationOutcome.MATCHES_EXPECTED)
        self.assertEqual(snapshot.disposition, "ESCALATE")

    def test_evaluates_no_continuity_as_not_matching_expected(self):
        snapshot = self.engine.evaluate(
            case_request(safety_acknowledged=True, results=[qualitative_result("NO_CONTINUITY")])
        )

        self.assertEqual(snapshot.state, CaseState.ESCALATION_REQUIRED)
        self.assertEqual(snapshot.evaluation.outcome, EvaluationOutcome.DOES_NOT_MATCH_EXPECTED)
        self.assertIn("service-action review", snapshot.guidance)

    def test_unknown_result_stops_fail_closed(self):
        snapshot = self.engine.evaluate(
            case_request(safety_acknowledged=True, results=[qualitative_result("UNKNOWN")])
        )

        self.assertEqual(snapshot.state, CaseState.STOPPED)
        self.assertEqual(snapshot.evaluation.outcome, EvaluationOutcome.UNKNOWN)

    def test_equal_requests_produce_equal_snapshots(self):
        request = case_request(safety_acknowledged=True, results=[qualitative_result("NO_CONTINUITY")])

        self.assertEqual(self.engine.evaluate(request), self.engine.evaluate(copy.deepcopy(request)))

    def test_requires_exact_fault_entry_condition(self):
        with self.assertRaisesRegex(DiagnosticCaseInputError, "exactly match"):
            self.engine.evaluate(case_request(fault_codes=["E24", "E25"]))
        with self.assertRaises(UnknownDiagnosticPathError):
            self.engine.evaluate(case_request(path_id="UNKNOWN"))

    def test_separates_field_and_training_result_sources(self):
        for source_type in ("SIMULATED", "IMPORTED"):
            with self.subTest(source_type=source_type), self.assertRaisesRegex(
                DiagnosticCaseInputError,
                "source type",
            ):
                self.engine.evaluate(
                    case_request(
                        safety_acknowledged=True,
                        results=[qualitative_result(source_type=source_type)],
                    )
                )
        training_snapshot = self.engine.evaluate(
            case_request(
                mode="TRAINING",
                safety_acknowledged=True,
                results=[qualitative_result(source_type="SIMULATED")],
            )
        )
        self.assertEqual(training_snapshot.state, CaseState.ESCALATION_REQUIRED)

    def test_requires_chronological_case_and_result_timestamps(self):
        with self.assertRaisesRegex(DiagnosticCaseInputError, "cannot precede"):
            self.engine.evaluate(
                case_request(
                    created_at="2026-08-04T13:00:00Z",
                    updated_at="2026-08-04T12:00:00Z",
                )
            )
        with self.assertRaisesRegex(DiagnosticCaseInputError, "case timeline"):
            self.engine.evaluate(
                case_request(
                    safety_acknowledged=True,
                    results=[qualitative_result(recorded_at="2026-08-04T13:00:00Z")],
                )
            )

    def test_rejects_invalid_result_contract(self):
        invalid_results = (
            qualitative_result(result_kind="NUMERIC"),
            qualitative_result(unit="OHMS"),
            qualitative_result(step_id="UNKNOWN"),
            qualitative_result(recorded_at="2026-08-04"),
        )

        for result in invalid_results:
            with self.subTest(result=result), self.assertRaises(DiagnosticCaseInputError):
                self.engine.evaluate(case_request(safety_acknowledged=True, results=[result]))

    def test_rejects_unknown_measurement_in_definition(self):
        invalid_path = diagnostic_path()
        invalid_path["steps"][0]["measurement_id"] = "UNKNOWN"

        with self.assertRaisesRegex(DiagnosticDefinitionError, "unknown measurement"):
            DiagnosticCaseEngine(package(invalid_path))


if __name__ == "__main__":
    unittest.main()
