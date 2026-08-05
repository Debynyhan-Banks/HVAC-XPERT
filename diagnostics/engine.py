from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from math import isfinite

from scripts.private_package_gate import PrivateKnowledgePackage
from simulator import DeterministicSimulator, DiagnosticMeasurementDefinition, SourceReference


class DiagnosticDefinitionError(ValueError):
    pass


class DiagnosticCaseInputError(ValueError):
    pass


class UnknownDiagnosticPathError(KeyError):
    pass


class CaseMode(Enum):
    FIELD = "FIELD"
    TRAINING = "TRAINING"


class CaseState(Enum):
    SAFETY_ACKNOWLEDGEMENT_REQUIRED = "SAFETY_ACKNOWLEDGEMENT_REQUIRED"
    AWAITING_RESULT = "AWAITING_RESULT"
    NEXT_TEST_AVAILABLE = "NEXT_TEST_AVAILABLE"
    COMPLETE = "COMPLETE"
    ESCALATION_REQUIRED = "ESCALATION_REQUIRED"
    STOPPED = "STOPPED"


class EvaluationOutcome(Enum):
    MATCHES_EXPECTED = "MATCHES_EXPECTED"
    DOES_NOT_MATCH_EXPECTED = "DOES_NOT_MATCH_EXPECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SafetyAcknowledgementDefinition:
    acknowledgement_id: str
    label: str
    safety_category: str
    required: bool


@dataclass(frozen=True)
class ExpectedResultDefinition:
    result_kind: str
    nominal: int | float | None
    minimum: int | float | None
    maximum: int | float | None
    unit: str | None
    qualitative_value: str | None


@dataclass(frozen=True)
class DiagnosticBranchDefinition:
    branch_id: str
    evaluation: EvaluationOutcome
    disposition: str
    next_step_id: str | None
    guidance: str


@dataclass(frozen=True)
class DiagnosticStepDefinition:
    step_id: str
    sequence: int
    measurement_id: str
    measurement: DiagnosticMeasurementDefinition
    rationale: str
    expected_result: ExpectedResultDefinition
    branches: tuple[DiagnosticBranchDefinition, ...]


@dataclass(frozen=True)
class DiagnosticPathDefinition:
    path_id: str
    model_id: str
    revision_id: str
    title: str
    complaint_summary: str
    entry_fault_ids: tuple[str, ...]
    entry_fault_codes: tuple[str, ...]
    safety_acknowledgements: tuple[SafetyAcknowledgementDefinition, ...]
    steps: tuple[DiagnosticStepDefinition, ...]
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class DiagnosticResult:
    result_id: str
    step_id: str
    measurement_id: str
    source_type: str
    result_kind: str
    numeric_value: int | float | None
    qualitative_value: str | None
    unit: str | None
    recorded_by: str
    recorded_at: str
    notes: str | None


@dataclass(frozen=True)
class DiagnosticEvaluation:
    step_id: str
    measurement_id: str
    outcome: EvaluationOutcome
    branch_id: str


@dataclass(frozen=True)
class DiagnosticCaseSnapshot:
    schema_version: str
    case_id: str
    model_id: str
    revision_id: str
    knowledge_package_ids: tuple[str, ...]
    path_id: str
    mode: CaseMode
    state: CaseState
    complaint_summary: str
    fault_codes: tuple[str, ...]
    safety_acknowledged: bool
    current_step_id: str | None
    results: tuple[DiagnosticResult, ...]
    evaluation: DiagnosticEvaluation | None
    disposition: str | None
    guidance: str | None
    created_at: str
    updated_at: str


class DiagnosticCaseEngine:
    _REQUEST_KEYS = {
        "case_id",
        "path_id",
        "mode",
        "fault_codes",
        "safety_acknowledged",
        "results",
        "created_at",
        "updated_at",
    }
    _RESULT_KEYS = {
        "result_id",
        "step_id",
        "measurement_id",
        "source_type",
        "result_kind",
        "numeric_value",
        "qualitative_value",
        "unit",
        "recorded_by",
        "recorded_at",
        "notes",
    }
    _RESULT_KINDS = {"NUMERIC", "QUALITATIVE"}
    _QUALITATIVE_VALUES = {
        "CONTINUITY", "NO_CONTINUITY", "OPEN", "CLOSED", "PRESENT", "ABSENT", "OTHER", "UNKNOWN",
    }
    _DISPOSITIONS = {"NEXT_TEST", "COMPLETE", "ESCALATE", "STOP"}

    def __init__(self, package: PrivateKnowledgePackage):
        simulator = DeterministicSimulator(package)
        measurements_by_id = {
            measurement.measurement_id: measurement
            for measurement in simulator.diagnostic_measurements
        }
        fault_codes_by_id = self._read_fault_codes(package.faults)
        self._paths_by_id = self._read_paths(
            package.diagnostic_paths,
            package.model_id,
            package.revision_id,
            measurements_by_id,
            fault_codes_by_id,
        )
        package_ids = [package.manifest.get("package_id")]
        package_ids.extend(package.extension_package_ids)
        self._knowledge_package_ids = tuple(
            package_id for package_id in package_ids if isinstance(package_id, str) and package_id
        )
        if not self._knowledge_package_ids:
            self._knowledge_package_ids = (f"{package.model_id}:{package.revision_id}:private-runtime",)

    @property
    def diagnostic_paths(self):
        return tuple(self._paths_by_id[path_id] for path_id in sorted(self._paths_by_id))

    @property
    def known_path_ids(self):
        return tuple(sorted(self._paths_by_id))

    def evaluate(self, request):
        values = self._validate_request(request)
        path = self._paths_by_id.get(values["path_id"])
        if path is None:
            raise UnknownDiagnosticPathError(f"Unknown diagnostic path: {values['path_id']}")
        if tuple(values["fault_codes"]) != path.entry_fault_codes:
            raise DiagnosticCaseInputError("Fault codes must exactly match the approved diagnostic-path entry condition")

        if not values["safety_acknowledged"]:
            if values["results"]:
                raise DiagnosticCaseInputError("Results cannot be recorded before required safety acknowledgement")
            return self._snapshot(
                values,
                path,
                CaseState.SAFETY_ACKNOWLEDGEMENT_REQUIRED,
                None,
                (),
                None,
                None,
                "Acknowledge every approved safety requirement before loading the first test.",
            )

        current_step = path.steps[0]
        accepted_results = []
        final_evaluation = None
        final_disposition = None
        final_guidance = None
        steps_by_id = {step.step_id: step for step in path.steps}
        result_ids = set()
        previous_recorded_at = None
        for result_index, result_record in enumerate(values["results"]):
            result = self._read_result(result_record, values["mode"], current_step)
            if result.result_id in result_ids:
                raise DiagnosticCaseInputError(f"Duplicate diagnostic result ID: {result.result_id}")
            recorded_at = self._validate_timestamp(result.recorded_at, "recorded_at")
            if recorded_at < values["created_at_value"] or recorded_at > values["updated_at_value"]:
                raise DiagnosticCaseInputError("recorded_at must fall within the case timeline")
            if previous_recorded_at is not None and recorded_at < previous_recorded_at:
                raise DiagnosticCaseInputError("Diagnostic results must be recorded in chronological order")
            result_ids.add(result.result_id)
            previous_recorded_at = recorded_at
            accepted_results.append(result)
            outcome = self._evaluate_result(current_step.expected_result, result)
            branch = next(
                branch for branch in current_step.branches if branch.evaluation is outcome
            )
            final_evaluation = DiagnosticEvaluation(
                step_id=current_step.step_id,
                measurement_id=current_step.measurement_id,
                outcome=outcome,
                branch_id=branch.branch_id,
            )
            final_disposition = branch.disposition
            final_guidance = branch.guidance
            if branch.disposition == "NEXT_TEST":
                current_step = steps_by_id[branch.next_step_id]
                continue
            if result_index != len(values["results"]) - 1:
                raise DiagnosticCaseInputError("Results continue after the approved path reached a terminal disposition")
            current_step = None

        if current_step is not None:
            state = CaseState.AWAITING_RESULT if not accepted_results else CaseState.NEXT_TEST_AVAILABLE
            final_disposition = "NEXT_TEST" if accepted_results else None
            if accepted_results and final_guidance is None:
                final_guidance = "Continue with the next approved diagnostic test."
        else:
            state = self._state_for_disposition(final_disposition)

        return self._snapshot(
            values,
            path,
            state,
            current_step,
            tuple(accepted_results),
            final_evaluation,
            final_disposition,
            final_guidance,
        )

    def _snapshot(self, values, path, state, current_step, results, evaluation, disposition, guidance):
        return DiagnosticCaseSnapshot(
            schema_version="1.0.0",
            case_id=values["case_id"],
            model_id=path.model_id,
            revision_id=path.revision_id,
            knowledge_package_ids=self._knowledge_package_ids,
            path_id=path.path_id,
            mode=values["mode"],
            state=state,
            complaint_summary=path.complaint_summary,
            fault_codes=path.entry_fault_codes,
            safety_acknowledged=values["safety_acknowledged"],
            current_step_id=current_step.step_id if current_step is not None else None,
            results=results,
            evaluation=evaluation,
            disposition=disposition,
            guidance=guidance,
            created_at=values["created_at"],
            updated_at=values["updated_at"],
        )

    @classmethod
    def _validate_request(cls, request):
        if not isinstance(request, dict):
            raise DiagnosticCaseInputError("Case request must be a JSON object")
        missing_keys = cls._REQUEST_KEYS - set(request)
        unexpected_keys = set(request) - cls._REQUEST_KEYS
        if missing_keys:
            raise DiagnosticCaseInputError(f"Missing case request fields: {sorted(missing_keys)}")
        if unexpected_keys:
            raise DiagnosticCaseInputError(f"Unexpected case request fields: {sorted(unexpected_keys)}")
        for field_name in ("case_id", "path_id"):
            if not isinstance(request[field_name], str) or not request[field_name]:
                raise DiagnosticCaseInputError(f"{field_name} must be a non-empty string")
        try:
            mode = CaseMode(request["mode"])
        except (TypeError, ValueError) as error:
            raise DiagnosticCaseInputError("mode must be FIELD or TRAINING") from error
        fault_codes = request["fault_codes"]
        if not isinstance(fault_codes, list) or not fault_codes or not all(
            isinstance(code, str) and code for code in fault_codes
        ):
            raise DiagnosticCaseInputError("fault_codes must be a non-empty array of strings")
        if len(fault_codes) != len(set(fault_codes)):
            raise DiagnosticCaseInputError("fault_codes cannot contain duplicates")
        if type(request["safety_acknowledged"]) is not bool:
            raise DiagnosticCaseInputError("safety_acknowledged must be a boolean")
        if not isinstance(request["results"], list):
            raise DiagnosticCaseInputError("results must be an array")
        created_at_value = cls._validate_timestamp(request["created_at"], "created_at")
        updated_at_value = cls._validate_timestamp(request["updated_at"], "updated_at")
        if updated_at_value < created_at_value:
            raise DiagnosticCaseInputError("updated_at cannot precede created_at")
        return {
            "case_id": request["case_id"],
            "path_id": request["path_id"],
            "mode": mode,
            "fault_codes": tuple(sorted(fault_codes)),
            "safety_acknowledged": request["safety_acknowledged"],
            "results": request["results"],
            "created_at": request["created_at"],
            "updated_at": request["updated_at"],
            "created_at_value": created_at_value,
            "updated_at_value": updated_at_value,
        }

    @classmethod
    def _read_result(cls, record, mode, step):
        if not isinstance(record, dict):
            raise DiagnosticCaseInputError("Each diagnostic result must be an object")
        if set(record) != cls._RESULT_KEYS:
            raise DiagnosticCaseInputError("Diagnostic result fields do not match the canonical contract")
        for field_name in ("result_id", "step_id", "measurement_id", "recorded_by"):
            if not isinstance(record[field_name], str) or not record[field_name]:
                raise DiagnosticCaseInputError(f"Result {field_name} must be a non-empty string")
        if record["step_id"] != step.step_id or record["measurement_id"] != step.measurement_id:
            raise DiagnosticCaseInputError("Diagnostic result does not match the current approved step")
        allowed_source_types = {
            CaseMode.FIELD: {"TECHNICIAN_ENTRY"},
            CaseMode.TRAINING: {"SIMULATED"},
        }
        if record["source_type"] not in allowed_source_types[mode]:
            raise DiagnosticCaseInputError("Result source type is not allowed for the selected case mode")
        if record["result_kind"] not in cls._RESULT_KINDS or record["result_kind"] != step.expected_result.result_kind:
            raise DiagnosticCaseInputError("Result kind does not match the approved step")
        numeric_value = record["numeric_value"]
        qualitative_value = record["qualitative_value"]
        unit = record["unit"]
        if record["result_kind"] == "NUMERIC":
            if numeric_value is not None and (type(numeric_value) not in (int, float) or not isfinite(numeric_value)):
                raise DiagnosticCaseInputError("Numeric result must be finite or null")
            if qualitative_value is not None:
                raise DiagnosticCaseInputError("Numeric result cannot include a qualitative value")
            if unit != step.expected_result.unit:
                raise DiagnosticCaseInputError("Numeric result unit must exactly match the approved definition")
        else:
            if numeric_value is not None or unit is not None:
                raise DiagnosticCaseInputError("Qualitative result cannot include a numeric value or unit")
            if qualitative_value not in cls._QUALITATIVE_VALUES:
                raise DiagnosticCaseInputError("Qualitative result is unsupported")
        if record["notes"] is not None and not isinstance(record["notes"], str):
            raise DiagnosticCaseInputError("Result notes must be a string or null")
        cls._validate_timestamp(record["recorded_at"], "recorded_at")
        return DiagnosticResult(
            result_id=record["result_id"],
            step_id=record["step_id"],
            measurement_id=record["measurement_id"],
            source_type=record["source_type"],
            result_kind=record["result_kind"],
            numeric_value=numeric_value,
            qualitative_value=qualitative_value,
            unit=unit,
            recorded_by=record["recorded_by"],
            recorded_at=record["recorded_at"],
            notes=record["notes"],
        )

    @staticmethod
    def _evaluate_result(expected, result):
        if expected.result_kind == "QUALITATIVE":
            if result.qualitative_value == "UNKNOWN":
                return EvaluationOutcome.UNKNOWN
            if result.qualitative_value == expected.qualitative_value:
                return EvaluationOutcome.MATCHES_EXPECTED
            return EvaluationOutcome.DOES_NOT_MATCH_EXPECTED
        if result.numeric_value is None:
            return EvaluationOutcome.UNKNOWN
        if expected.minimum is not None and result.numeric_value < expected.minimum:
            return EvaluationOutcome.DOES_NOT_MATCH_EXPECTED
        if expected.maximum is not None and result.numeric_value > expected.maximum:
            return EvaluationOutcome.DOES_NOT_MATCH_EXPECTED
        if expected.minimum is not None or expected.maximum is not None:
            return EvaluationOutcome.MATCHES_EXPECTED
        if expected.nominal is None:
            return EvaluationOutcome.UNKNOWN
        if result.numeric_value == expected.nominal:
            return EvaluationOutcome.MATCHES_EXPECTED
        return EvaluationOutcome.DOES_NOT_MATCH_EXPECTED

    @staticmethod
    def _state_for_disposition(disposition):
        states = {
            "COMPLETE": CaseState.COMPLETE,
            "ESCALATE": CaseState.ESCALATION_REQUIRED,
            "STOP": CaseState.STOPPED,
        }
        if disposition not in states:
            raise DiagnosticDefinitionError(f"Terminal path has invalid disposition: {disposition}")
        return states[disposition]

    @staticmethod
    def _validate_timestamp(value, field_name):
        if not isinstance(value, str) or not value:
            raise DiagnosticCaseInputError(f"{field_name} must be an ISO 8601 timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise DiagnosticCaseInputError(f"{field_name} must be an ISO 8601 timestamp") from error
        if parsed.tzinfo is None:
            raise DiagnosticCaseInputError(f"{field_name} must include a timezone")
        return parsed

    @staticmethod
    def _read_fault_codes(records):
        fault_codes_by_id = {}
        for record in records:
            fault_id = record.get("fault_id")
            code = record.get("code")
            if not isinstance(fault_id, str) or not fault_id or not isinstance(code, str) or not code:
                raise DiagnosticDefinitionError("Fault record is missing fault ID or code")
            if fault_id in fault_codes_by_id:
                raise DiagnosticDefinitionError(f"Duplicate fault ID: {fault_id}")
            fault_codes_by_id[fault_id] = code
        return fault_codes_by_id

    @classmethod
    def _read_paths(cls, records, model_id, revision_id, measurements_by_id, fault_codes_by_id):
        paths_by_id = {}
        for record in records:
            path_id = record.get("path_id")
            if not isinstance(path_id, str) or not path_id:
                raise DiagnosticDefinitionError("Diagnostic path is missing path_id")
            if path_id in paths_by_id:
                raise DiagnosticDefinitionError(f"Duplicate diagnostic path ID: {path_id}")
            if record.get("model_id") != model_id or record.get("revision_id") != revision_id:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} model or revision mismatch")
            entry_fault_ids = record.get("entry_fault_ids")
            if not isinstance(entry_fault_ids, list) or not entry_fault_ids or not set(entry_fault_ids) <= set(fault_codes_by_id):
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has invalid entry faults")
            entry_fault_codes = tuple(sorted(fault_codes_by_id[fault_id] for fault_id in entry_fault_ids))
            acknowledgements = cls._read_acknowledgements(record.get("safety_acknowledgements"), path_id)
            steps = cls._read_steps(record.get("steps"), path_id, measurements_by_id)
            sources = cls._read_sources(record.get("provenance"), path_id)
            title = record.get("title")
            complaint_summary = record.get("complaint_summary")
            if not isinstance(title, str) or not title or not isinstance(complaint_summary, str) or not complaint_summary:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} is missing descriptive text")
            paths_by_id[path_id] = DiagnosticPathDefinition(
                path_id=path_id,
                model_id=model_id,
                revision_id=revision_id,
                title=title,
                complaint_summary=complaint_summary,
                entry_fault_ids=tuple(entry_fault_ids),
                entry_fault_codes=entry_fault_codes,
                safety_acknowledgements=acknowledgements,
                steps=steps,
                sources=sources,
            )
        return paths_by_id

    @staticmethod
    def _read_acknowledgements(records, path_id):
        if not isinstance(records, list) or not records:
            raise DiagnosticDefinitionError(f"Diagnostic path {path_id} requires safety acknowledgements")
        acknowledgements = []
        identifiers = set()
        for record in records:
            if not isinstance(record, dict):
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has an invalid safety acknowledgement")
            acknowledgement_id = record.get("acknowledgement_id")
            label = record.get("label")
            safety_category = record.get("safety_category")
            if not isinstance(acknowledgement_id, str) or not acknowledgement_id or acknowledgement_id in identifiers:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has an invalid safety acknowledgement ID")
            if not isinstance(label, str) or not label or not isinstance(safety_category, str) or not safety_category:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has incomplete safety acknowledgement")
            if record.get("required") is not True:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} safety acknowledgement must be required")
            identifiers.add(acknowledgement_id)
            acknowledgements.append(
                SafetyAcknowledgementDefinition(
                    acknowledgement_id=acknowledgement_id,
                    label=label,
                    safety_category=safety_category,
                    required=True,
                )
            )
        return tuple(acknowledgements)

    @classmethod
    def _read_steps(cls, records, path_id, measurements_by_id):
        if not isinstance(records, list) or not records:
            raise DiagnosticDefinitionError(f"Diagnostic path {path_id} requires steps")
        steps = []
        step_ids = set()
        for expected_sequence, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has an invalid step")
            step_id = record.get("step_id")
            measurement_id = record.get("measurement_id")
            rationale = record.get("rationale")
            if not isinstance(step_id, str) or not step_id or step_id in step_ids:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has an invalid step ID")
            if record.get("sequence") != expected_sequence:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} step sequence is invalid")
            if measurement_id not in measurements_by_id:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} references an unknown measurement")
            if not isinstance(rationale, str) or not rationale:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} is missing rationale")
            expected_result = cls._read_expected_result(record.get("expected_result"), step_id)
            branches = cls._read_branches(record.get("branches"), step_id)
            step_ids.add(step_id)
            steps.append(
                DiagnosticStepDefinition(
                    step_id=step_id,
                    sequence=expected_sequence,
                    measurement_id=measurement_id,
                    measurement=measurements_by_id[measurement_id],
                    rationale=rationale,
                    expected_result=expected_result,
                    branches=branches,
                )
            )
        sequence_by_id = {step.step_id: step.sequence for step in steps}
        for step in steps:
            for branch in step.branches:
                if branch.disposition == "NEXT_TEST":
                    if branch.next_step_id not in sequence_by_id or sequence_by_id[branch.next_step_id] <= step.sequence:
                        raise DiagnosticDefinitionError(f"Diagnostic step {step.step_id} next branch is invalid")
                elif branch.next_step_id is not None:
                    raise DiagnosticDefinitionError(f"Diagnostic step {step.step_id} terminal branch identifies a next step")
        return tuple(steps)

    @classmethod
    def _read_expected_result(cls, record, step_id):
        if not isinstance(record, dict) or record.get("result_kind") not in cls._RESULT_KINDS:
            raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has an invalid expected result")
        result_kind = record["result_kind"]
        nominal = record.get("nominal")
        minimum = record.get("minimum")
        maximum = record.get("maximum")
        unit = record.get("unit")
        qualitative_value = record.get("qualitative_value")
        if result_kind == "NUMERIC":
            numeric_values = [value for value in (nominal, minimum, maximum) if value is not None]
            if not numeric_values or not all(type(value) in (int, float) and isfinite(value) for value in numeric_values):
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has invalid numeric expectation")
            if not isinstance(unit, str) or not unit or qualitative_value is not None:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has invalid numeric unit or qualitative value")
            if minimum is not None and maximum is not None and minimum > maximum:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} expected minimum exceeds maximum")
        else:
            if any(value is not None for value in (nominal, minimum, maximum, unit)):
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} qualitative expectation contains numeric values")
            if qualitative_value not in cls._QUALITATIVE_VALUES:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has invalid qualitative expectation")
        return ExpectedResultDefinition(
            result_kind=result_kind,
            nominal=nominal,
            minimum=minimum,
            maximum=maximum,
            unit=unit,
            qualitative_value=qualitative_value,
        )

    @classmethod
    def _read_branches(cls, records, step_id):
        if not isinstance(records, list) or len(records) != len(EvaluationOutcome):
            raise DiagnosticDefinitionError(f"Diagnostic step {step_id} must define every evaluation branch")
        branches = []
        branch_ids = set()
        evaluations = set()
        for record in records:
            if not isinstance(record, dict):
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has an invalid branch")
            branch_id = record.get("branch_id")
            try:
                evaluation = EvaluationOutcome(record.get("evaluation"))
            except (TypeError, ValueError) as error:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has an invalid evaluation") from error
            disposition = record.get("disposition")
            guidance = record.get("guidance")
            if not isinstance(branch_id, str) or not branch_id or branch_id in branch_ids:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has an invalid branch ID")
            if evaluation in evaluations:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has duplicate evaluation branches")
            if disposition not in cls._DISPOSITIONS:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has an invalid disposition")
            if not isinstance(guidance, str) or not guidance:
                raise DiagnosticDefinitionError(f"Diagnostic step {step_id} has missing branch guidance")
            branch_ids.add(branch_id)
            evaluations.add(evaluation)
            branches.append(
                DiagnosticBranchDefinition(
                    branch_id=branch_id,
                    evaluation=evaluation,
                    disposition=disposition,
                    next_step_id=record.get("next_step_id"),
                    guidance=guidance,
                )
            )
        if evaluations != set(EvaluationOutcome):
            raise DiagnosticDefinitionError(f"Diagnostic step {step_id} does not cover every evaluation")
        return tuple(branches)

    @staticmethod
    def _read_sources(assertions, path_id):
        if not isinstance(assertions, list) or not assertions:
            raise DiagnosticDefinitionError(f"Diagnostic path {path_id} is missing provenance")
        sources = []
        for assertion in assertions:
            source = assertion.get("source", {})
            validation = assertion.get("validation", {})
            document_id = source.get("document_id")
            page = source.get("page")
            validation_level = validation.get("level")
            validation_outcome = validation.get("outcome")
            reviewed_by = validation.get("reviewed_by")
            reviewed_at = validation.get("reviewed_at")
            if not isinstance(document_id, str) or not document_id or not isinstance(page, int) or page < 1:
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has invalid source provenance")
            if not all(isinstance(value, str) and value for value in (validation_level, validation_outcome, reviewed_by, reviewed_at)):
                raise DiagnosticDefinitionError(f"Diagnostic path {path_id} has incomplete review provenance")
            sources.append(
                SourceReference(
                    document_id=document_id,
                    page=page,
                    section=source.get("section"),
                    validation_level=validation_level,
                    validation_outcome=validation_outcome,
                    reviewed_by=reviewed_by,
                    reviewed_at=reviewed_at,
                )
            )
        return tuple(sources)
