from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from diagnostics import DiagnosticCaseEngine, EvaluationOutcome
from scripts.private_package_gate import PrivateKnowledgePackage
from simulator import SourceReference


class TrainingAttemptInputError(ValueError):
    pass


class UnknownTrainingReplayError(KeyError):
    pass


class TrainingState(Enum):
    SAFETY_ACKNOWLEDGEMENT_REQUIRED = "SAFETY_ACKNOWLEDGEMENT_REQUIRED"
    AWAITING_LEARNER_RESPONSE = "AWAITING_LEARNER_RESPONSE"
    SCORED = "SCORED"


@dataclass(frozen=True)
class TrainingReplayDefinition:
    schema_version: str
    replay_id: str
    path_id: str
    model_id: str
    revision_id: str
    title: str
    learning_objective: str
    difficulty: str
    max_score: int
    pass_score: int
    hint_penalty: int
    sources: tuple[SourceReference, ...]


@dataclass(frozen=True)
class SimulatedObservation:
    result_kind: str
    numeric_value: int | float | None
    qualitative_value: str | None
    unit: str | None
    source_type: str


@dataclass(frozen=True)
class ScoringItem:
    criterion: str
    earned_points: int
    available_points: int
    correct: bool


@dataclass(frozen=True)
class TrainingAttemptSnapshot:
    schema_version: str
    attempt_id: str
    replay_id: str
    path_id: str
    model_id: str
    revision_id: str
    knowledge_package_ids: tuple[str, ...]
    state: TrainingState
    safety_acknowledged: bool
    simulated_observation: SimulatedObservation | None
    learner_evaluation: str | None
    learner_disposition: str | None
    target_evaluation: str | None
    target_disposition: str | None
    hint_used: bool
    hint: str | None
    score: int | None
    max_score: int
    pass_score: int
    passed: bool | None
    scoring: tuple[ScoringItem, ...]
    remediation: tuple[str, ...]
    guidance: str | None
    learner_id: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class _ReplayRule:
    definition: TrainingReplayDefinition
    fault_codes: tuple[str, ...]
    step_id: str
    measurement_id: str
    observation: SimulatedObservation
    hint: str


class TrainingReplayEngine:
    _REQUEST_KEYS = {
        "attempt_id",
        "replay_id",
        "safety_acknowledged",
        "hint_used",
        "learner_evaluation",
        "learner_disposition",
        "learner_id",
        "created_at",
        "updated_at",
    }
    _OPPOSITE_QUALITATIVE_VALUES = {
        "CONTINUITY": "NO_CONTINUITY",
        "NO_CONTINUITY": "CONTINUITY",
        "OPEN": "CLOSED",
        "CLOSED": "OPEN",
        "PRESENT": "ABSENT",
        "ABSENT": "PRESENT",
    }
    _EVALUATIONS = {outcome.value for outcome in EvaluationOutcome}
    _DISPOSITIONS = {"NEXT_TEST", "COMPLETE", "ESCALATE", "STOP"}
    _MAX_SCORE = 100
    _PASS_SCORE = 80
    _HINT_PENALTY = 10

    def __init__(self, package: PrivateKnowledgePackage):
        self._cases = DiagnosticCaseEngine(package)
        self._rules_by_id = self._build_rules(self._cases.diagnostic_paths)

    @property
    def training_replays(self):
        return tuple(
            self._rules_by_id[replay_id].definition
            for replay_id in sorted(self._rules_by_id)
        )

    @property
    def known_replay_ids(self):
        return tuple(sorted(self._rules_by_id))

    def evaluate(self, request):
        values = self._validate_request(request)
        rule = self._rules_by_id.get(values["replay_id"])
        if rule is None:
            raise UnknownTrainingReplayError(f"Unknown training replay: {values['replay_id']}")
        if not values["safety_acknowledged"]:
            if values["hint_used"] or self._has_answer(values):
                raise TrainingAttemptInputError(
                    "Training hints and answers remain unavailable until safety is acknowledged"
                )
            return self._snapshot(
                values,
                rule,
                TrainingState.SAFETY_ACKNOWLEDGEMENT_REQUIRED,
            )

        case_snapshot = self._evaluate_simulated_case(values, rule)
        if not self._has_answer(values):
            return self._snapshot(
                values,
                rule,
                TrainingState.AWAITING_LEARNER_RESPONSE,
                simulated_observation=rule.observation,
                hint=rule.hint if values["hint_used"] else None,
            )

        scoring = (
            self._score_item(
                "INTERPRET_SIMULATED_RESULT",
                values["learner_evaluation"] == case_snapshot.evaluation.outcome.value,
            ),
            self._score_item(
                "SELECT_APPROVED_DISPOSITION",
                values["learner_disposition"] == case_snapshot.disposition,
            ),
        )
        earned_score = sum(item.earned_points for item in scoring)
        if values["hint_used"]:
            earned_score = max(0, earned_score - self._HINT_PENALTY)
        remediation = self._remediation(values, case_snapshot, scoring)
        return self._snapshot(
            values,
            rule,
            TrainingState.SCORED,
            simulated_observation=rule.observation,
            target_evaluation=case_snapshot.evaluation.outcome.value,
            target_disposition=case_snapshot.disposition,
            hint=rule.hint if values["hint_used"] else None,
            score=earned_score,
            passed=earned_score >= self._PASS_SCORE,
            scoring=scoring,
            remediation=remediation,
            guidance=case_snapshot.guidance,
        )

    def _evaluate_simulated_case(self, values, rule):
        observation = rule.observation
        return self._cases.evaluate(
            {
                "case_id": f"{values['attempt_id']}:case",
                "path_id": rule.definition.path_id,
                "mode": "TRAINING",
                "fault_codes": list(rule.fault_codes),
                "safety_acknowledged": True,
                "results": [
                    {
                        "result_id": f"{values['attempt_id']}:simulated-result",
                        "step_id": rule.step_id,
                        "measurement_id": rule.measurement_id,
                        "source_type": observation.source_type,
                        "result_kind": observation.result_kind,
                        "numeric_value": observation.numeric_value,
                        "qualitative_value": observation.qualitative_value,
                        "unit": observation.unit,
                        "recorded_by": "HVAC-XPERT-DETERMINISTIC-TRAINING",
                        "recorded_at": values["updated_at"],
                        "notes": "Synthetic training observation; not a field measurement.",
                    }
                ],
                "created_at": values["created_at"],
                "updated_at": values["updated_at"],
            }
        )

    @classmethod
    def _validate_request(cls, request):
        if not isinstance(request, dict):
            raise TrainingAttemptInputError("Training attempt request must be a JSON object")
        missing_keys = cls._REQUEST_KEYS - set(request)
        unexpected_keys = set(request) - cls._REQUEST_KEYS
        if missing_keys:
            raise TrainingAttemptInputError(
                f"Missing training attempt fields: {sorted(missing_keys)}"
            )
        if unexpected_keys:
            raise TrainingAttemptInputError(
                f"Unexpected training attempt fields: {sorted(unexpected_keys)}"
            )
        for field_name in ("attempt_id", "replay_id"):
            if not isinstance(request[field_name], str) or not request[field_name]:
                raise TrainingAttemptInputError(f"{field_name} must be a non-empty string")
        for field_name in ("safety_acknowledged", "hint_used"):
            if type(request[field_name]) is not bool:
                raise TrainingAttemptInputError(f"{field_name} must be a boolean")
        learner_id = request["learner_id"]
        if learner_id is not None and (not isinstance(learner_id, str) or not learner_id):
            raise TrainingAttemptInputError("learner_id must be a non-empty string or null")
        learner_evaluation = request["learner_evaluation"]
        learner_disposition = request["learner_disposition"]
        if (learner_evaluation is None) != (learner_disposition is None):
            raise TrainingAttemptInputError(
                "Learner evaluation and disposition must be submitted together"
            )
        if learner_evaluation is not None:
            if learner_evaluation not in cls._EVALUATIONS:
                raise TrainingAttemptInputError("Learner evaluation is unsupported")
            if learner_disposition not in cls._DISPOSITIONS:
                raise TrainingAttemptInputError("Learner disposition is unsupported")
            if learner_id is None:
                raise TrainingAttemptInputError("learner_id is required when submitting answers")
        created_at_value = cls._validate_timestamp(request["created_at"], "created_at")
        updated_at_value = cls._validate_timestamp(request["updated_at"], "updated_at")
        if updated_at_value < created_at_value:
            raise TrainingAttemptInputError("updated_at cannot precede created_at")
        return {
            "attempt_id": request["attempt_id"],
            "replay_id": request["replay_id"],
            "safety_acknowledged": request["safety_acknowledged"],
            "hint_used": request["hint_used"],
            "learner_evaluation": learner_evaluation,
            "learner_disposition": learner_disposition,
            "learner_id": learner_id,
            "created_at": request["created_at"],
            "updated_at": request["updated_at"],
        }

    @staticmethod
    def _validate_timestamp(value, field_name):
        if not isinstance(value, str) or not value:
            raise TrainingAttemptInputError(f"{field_name} must be an ISO 8601 timestamp")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise TrainingAttemptInputError(
                f"{field_name} must be an ISO 8601 timestamp"
            ) from error
        if parsed.tzinfo is None:
            raise TrainingAttemptInputError(f"{field_name} must include a timezone")
        return parsed

    @staticmethod
    def _has_answer(values):
        return values["learner_evaluation"] is not None

    @staticmethod
    def _score_item(criterion, correct):
        return ScoringItem(
            criterion=criterion,
            earned_points=50 if correct else 0,
            available_points=50,
            correct=correct,
        )

    @staticmethod
    def _remediation(values, case_snapshot, scoring):
        messages = []
        if not scoring[0].correct:
            messages.append(
                "Compare the simulated observation with the approved expected result before classifying it."
            )
        if not scoring[1].correct:
            messages.append(
                f"The evaluated branch uses {case_snapshot.disposition}; do not invent an unsupported next action."
            )
        if values["hint_used"]:
            messages.append("A 10-point hint penalty was applied transparently.")
        return tuple(messages)

    def _snapshot(
        self,
        values,
        rule,
        state,
        simulated_observation=None,
        target_evaluation=None,
        target_disposition=None,
        hint=None,
        score=None,
        passed=None,
        scoring=(),
        remediation=(),
        guidance=None,
    ):
        definition = rule.definition
        return TrainingAttemptSnapshot(
            schema_version="1.0.0",
            attempt_id=values["attempt_id"],
            replay_id=definition.replay_id,
            path_id=definition.path_id,
            model_id=definition.model_id,
            revision_id=definition.revision_id,
            knowledge_package_ids=self._cases.knowledge_package_ids,
            state=state,
            safety_acknowledged=values["safety_acknowledged"],
            simulated_observation=simulated_observation,
            learner_evaluation=values["learner_evaluation"],
            learner_disposition=values["learner_disposition"],
            target_evaluation=target_evaluation,
            target_disposition=target_disposition,
            hint_used=values["hint_used"],
            hint=hint,
            score=score,
            max_score=definition.max_score,
            pass_score=definition.pass_score,
            passed=passed,
            scoring=scoring,
            remediation=remediation,
            guidance=guidance,
            learner_id=values["learner_id"],
            created_at=values["created_at"],
            updated_at=values["updated_at"],
        )

    @classmethod
    def _build_rules(cls, paths):
        rules = {}
        for path in paths:
            step = path.steps[0]
            expected = step.expected_result
            observation = cls._divergent_observation(expected)
            if observation is None:
                continue
            branch = next(
                (
                    candidate
                    for candidate in step.branches
                    if candidate.evaluation is EvaluationOutcome.DOES_NOT_MATCH_EXPECTED
                ),
                None,
            )
            if branch is None:
                continue
            replay_id = f"{path.path_id}:training-replay:divergent-result"
            definition = TrainingReplayDefinition(
                schema_version="1.0.0",
                replay_id=replay_id,
                path_id=path.path_id,
                model_id=path.model_id,
                revision_id=path.revision_id,
                title=f"{path.title} · deterministic replay",
                learning_objective=(
                    "Interpret a clearly labeled simulated result using the approved diagnostic "
                    "definition and select the supported disposition."
                ),
                difficulty="TECHNICIAN",
                max_score=cls._MAX_SCORE,
                pass_score=cls._PASS_SCORE,
                hint_penalty=cls._HINT_PENALTY,
                sources=path.sources,
            )
            rules[replay_id] = _ReplayRule(
                definition=definition,
                fault_codes=path.entry_fault_codes,
                step_id=step.step_id,
                measurement_id=step.measurement_id,
                observation=observation,
                hint=(
                    "Compare the simulated observation with the approved expected result, then "
                    "select the disposition defined by that evaluated branch."
                ),
            )
        return rules

    @classmethod
    def _divergent_observation(cls, expected):
        if expected.result_kind == "QUALITATIVE":
            simulated_value = cls._OPPOSITE_QUALITATIVE_VALUES.get(
                expected.qualitative_value
            )
            if simulated_value is None:
                return None
            return SimulatedObservation(
                result_kind="QUALITATIVE",
                numeric_value=None,
                qualitative_value=simulated_value,
                unit=None,
                source_type="SIMULATED",
            )
        if expected.maximum is not None:
            numeric_value = expected.maximum + 1
        elif expected.minimum is not None:
            numeric_value = expected.minimum - 1
        elif expected.nominal is not None:
            numeric_value = expected.nominal + 1
        else:
            return None
        return SimulatedObservation(
            result_kind="NUMERIC",
            numeric_value=numeric_value,
            qualitative_value=None,
            unit=expected.unit,
            source_type="SIMULATED",
        )
