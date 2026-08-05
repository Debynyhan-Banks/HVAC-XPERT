import copy
import unittest

from tests.test_diagnostic_case_engine import PATH_ID, package
from tests.test_private_simulator_app import package as numeric_package
from training import (
    TrainingAttemptInputError,
    TrainingReplayEngine,
    TrainingState,
    UnknownTrainingReplayError,
)


TIMESTAMP = "2026-08-05T01:00:00Z"


def attempt_request(**overrides):
    engine = TrainingReplayEngine(package())
    values = {
        "attempt_id": "ATTEMPT-SYNTHETIC-001",
        "replay_id": engine.known_replay_ids[0],
        "safety_acknowledged": False,
        "hint_used": False,
        "learner_evaluation": None,
        "learner_disposition": None,
        "learner_id": None,
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
    }
    values.update(overrides)
    return values


class TrainingReplayEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = TrainingReplayEngine(package())
        self.replay_id = self.engine.known_replay_ids[0]

    def request(self, **overrides):
        values = {"replay_id": self.replay_id}
        values.update(overrides)
        return attempt_request(**values)

    def test_derives_answer_redacted_replay_from_approved_path(self):
        replay = self.engine.training_replays[0]

        self.assertEqual(replay.path_id, PATH_ID)
        self.assertEqual(replay.difficulty, "TECHNICIAN")
        self.assertEqual(replay.max_score, 100)
        self.assertEqual(replay.pass_score, 80)
        self.assertEqual(replay.hint_penalty, 10)
        self.assertEqual(replay.sources[0].validation_level, "LEVEL_4_TECHNICIAN_REVIEWED")
        self.assertFalse(hasattr(replay, "simulated_observation"))
        self.assertFalse(hasattr(replay, "target_evaluation"))

    def test_hides_simulated_observation_until_safety_acknowledgement(self):
        snapshot = self.engine.evaluate(self.request())

        self.assertEqual(snapshot.state, TrainingState.SAFETY_ACKNOWLEDGEMENT_REQUIRED)
        self.assertIsNone(snapshot.simulated_observation)
        self.assertIsNone(snapshot.target_evaluation)
        self.assertIsNone(snapshot.score)
        with self.assertRaisesRegex(TrainingAttemptInputError, "until safety"):
            self.engine.evaluate(self.request(hint_used=True))

    def test_reveals_only_simulated_observation_before_answer(self):
        snapshot = self.engine.evaluate(self.request(safety_acknowledged=True))

        self.assertEqual(snapshot.state, TrainingState.AWAITING_LEARNER_RESPONSE)
        self.assertEqual(snapshot.simulated_observation.qualitative_value, "NO_CONTINUITY")
        self.assertEqual(snapshot.simulated_observation.source_type, "SIMULATED")
        self.assertIsNone(snapshot.target_evaluation)
        self.assertIsNone(snapshot.target_disposition)
        self.assertIsNone(snapshot.guidance)
        self.assertIsNone(snapshot.score)

    def test_scores_correct_interpretation_and_disposition(self):
        snapshot = self.engine.evaluate(
            self.request(
                safety_acknowledged=True,
                learner_evaluation="DOES_NOT_MATCH_EXPECTED",
                learner_disposition="ESCALATE",
                learner_id="synthetic-learner",
            )
        )

        self.assertEqual(snapshot.state, TrainingState.SCORED)
        self.assertEqual(snapshot.score, 100)
        self.assertIs(snapshot.passed, True)
        self.assertEqual(snapshot.target_evaluation, "DOES_NOT_MATCH_EXPECTED")
        self.assertEqual(snapshot.target_disposition, "ESCALATE")
        self.assertTrue(all(item.correct for item in snapshot.scoring))
        self.assertEqual(snapshot.remediation, ())
        self.assertIn("service-action review", snapshot.guidance)

    def test_applies_transparent_hint_penalty(self):
        awaiting = self.engine.evaluate(
            self.request(safety_acknowledged=True, hint_used=True)
        )
        scored = self.engine.evaluate(
            self.request(
                safety_acknowledged=True,
                hint_used=True,
                learner_evaluation="DOES_NOT_MATCH_EXPECTED",
                learner_disposition="ESCALATE",
                learner_id="synthetic-learner",
            )
        )

        self.assertIn("Compare the simulated observation", awaiting.hint)
        self.assertEqual(scored.score, 90)
        self.assertIs(scored.passed, True)
        self.assertIn("10-point hint penalty", scored.remediation[0])

    def test_scores_partial_and_incorrect_answers_with_remediation(self):
        partial = self.engine.evaluate(
            self.request(
                safety_acknowledged=True,
                learner_evaluation="MATCHES_EXPECTED",
                learner_disposition="ESCALATE",
                learner_id="synthetic-learner",
            )
        )
        incorrect = self.engine.evaluate(
            self.request(
                safety_acknowledged=True,
                learner_evaluation="MATCHES_EXPECTED",
                learner_disposition="COMPLETE",
                learner_id="synthetic-learner",
            )
        )

        self.assertEqual(partial.score, 50)
        self.assertIs(partial.passed, False)
        self.assertEqual(len(partial.remediation), 1)
        self.assertEqual(incorrect.score, 0)
        self.assertEqual(len(incorrect.remediation), 2)

    def test_equal_requests_produce_equal_training_snapshots(self):
        request = self.request(
            safety_acknowledged=True,
            hint_used=True,
            learner_evaluation="DOES_NOT_MATCH_EXPECTED",
            learner_disposition="ESCALATE",
            learner_id="synthetic-learner",
        )

        self.assertEqual(
            self.engine.evaluate(request),
            self.engine.evaluate(copy.deepcopy(request)),
        )

    def test_derives_numeric_simulation_beyond_approved_bound(self):
        engine = TrainingReplayEngine(numeric_package())
        replay_id = engine.known_replay_ids[0]
        snapshot = engine.evaluate(
            attempt_request(
                replay_id=replay_id,
                safety_acknowledged=True,
            )
        )

        self.assertEqual(snapshot.simulated_observation.result_kind, "NUMERIC")
        self.assertEqual(snapshot.simulated_observation.numeric_value, 27)
        self.assertEqual(snapshot.simulated_observation.unit, "VAC")

    def test_rejects_partial_invalid_and_unknown_attempts(self):
        invalid_requests = (
            self.request(learner_evaluation="MATCHES_EXPECTED"),
            self.request(
                safety_acknowledged=True,
                learner_evaluation="INVENTED",
                learner_disposition="ESCALATE",
                learner_id="synthetic-learner",
            ),
            self.request(
                safety_acknowledged=True,
                learner_evaluation="MATCHES_EXPECTED",
                learner_disposition="ESCALATE",
                learner_id=None,
            ),
            self.request(created_at="2026-08-05T02:00:00Z"),
        )
        for request in invalid_requests:
            with self.subTest(request=request), self.assertRaises(TrainingAttemptInputError):
                self.engine.evaluate(request)
        with self.assertRaises(UnknownTrainingReplayError):
            self.engine.evaluate(self.request(replay_id="UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
