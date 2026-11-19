"""D-094 public failure classification and dynamic operator-probability tests."""
from __future__ import annotations

import random
import unittest

from d094_feedback_evolution import (
    OPERATOR_NAMES,
    classify_failures,
    fixed_operator_probabilities,
    operator_probabilities,
    random_operator_probabilities,
)


def result_event(tool: str, success: bool) -> dict:
    return {
        "event_type": "tool_result",
        "payload": {
            "tool_name": tool,
            "success": success,
            "observation": {"status": "OK" if success else "FAILED"},
        },
    }


def rejection(code: str) -> dict:
    return {
        "event_type": "tool_rejected",
        "payload": {
            "tool_name": "tool",
            "success": False,
            "observation": {"error": code},
        },
    }


class TestFailureClassification(unittest.TestCase):
    def test_public_failure_types_and_denominators_are_recomputable(self):
        episodes = [
            {"agent_status": "PREMATURE_FINISH", "events": []},
            {
                "agent_status": "MAX_STEPS",
                "events": [
                    rejection("TOOL_SCHEMA_REJECTED"),
                    rejection("DEPENDENCY_VERIFICATION_REQUIRED"),
                    result_event("retry_primary", False),
                    result_event("verify_state", False),
                    result_event("inspect_state", True),
                    result_event("inspect_state", True),
                ],
            },
        ]
        profile = classify_failures(episodes)
        self.assertEqual(profile["counts"]["planning_failure"], 1)
        self.assertEqual(profile["counts"]["tool_call_failure"], 1)
        self.assertEqual(profile["counts"]["dependency_failure"], 1)
        self.assertEqual(profile["counts"]["recovery_failure"], 1)
        self.assertEqual(profile["counts"]["verification_failure"], 1)
        self.assertEqual(profile["counts"]["task_incompletion"], 2)
        self.assertEqual(profile["counts"]["unnecessary_tool_call"], 1)
        self.assertEqual(profile["denominators"]["episode_count"], 2)
        self.assertEqual(profile["rates"]["task_incompletion"], 1.0)
        self.assertEqual(profile["rates"]["unnecessary_tool_call"], 0.5)

    def test_hidden_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            classify_failures(
                [
                    {
                        "agent_status": "COMPLETED",
                        "events": [],
                        "hidden_outcome": "future",
                    }
                ]
            )


class TestOperatorFeedback(unittest.TestCase):
    def test_zero_feedback_is_exactly_uniform(self):
        profile = classify_failures(
            [
                {
                    "agent_status": "COMPLETED",
                    "events": [result_event("complete_task", True)],
                }
            ]
        )
        probabilities = operator_probabilities(profile)
        self.assertEqual(set(probabilities), set(OPERATOR_NAMES))
        for value in probabilities.values():
            self.assertAlmostEqual(value, 1 / 6)
        self.assertEqual(probabilities, fixed_operator_probabilities())

    def test_recovery_failure_increases_recovery_operator_probability(self):
        zero = classify_failures(
            [
                {
                    "agent_status": "COMPLETED",
                    "events": [result_event("complete_task", True)],
                }
            ]
        )
        recovery = classify_failures(
            [
                {
                    "agent_status": "MAX_STEPS",
                    "events": [result_event("retry_primary", False)],
                }
            ]
        )
        zero_p = operator_probabilities(zero)
        recovery_p = operator_probabilities(recovery)
        self.assertGreater(recovery_p["recovery_mutation"], zero_p["recovery_mutation"])
        self.assertAlmostEqual(sum(recovery_p.values()), 1.0)
        for value in recovery_p.values():
            self.assertGreaterEqual(value, 0.1 / 6)

    def test_tool_failure_increases_tool_guard_probability(self):
        profile = classify_failures(
            [
                {
                    "agent_status": "MAX_STEPS",
                    "events": [rejection("TOOL_SCHEMA_REJECTED")],
                }
            ]
        )
        probabilities = operator_probabilities(profile)
        self.assertGreater(
            probabilities["tool_guard_mutation"], probabilities["memory_mutation"]
        )

    def test_random_control_preserves_probability_multiset(self):
        profile = classify_failures(
            [
                {
                    "agent_status": "MAX_STEPS",
                    "events": [result_event("retry_primary", False)],
                }
            ]
        )
        dynamic = operator_probabilities(profile)
        randomized = random_operator_probabilities(dynamic, random.Random(3))
        self.assertEqual(sorted(randomized.values()), sorted(dynamic.values()))
        self.assertNotEqual(randomized, dynamic)

    def test_invalid_feedback_parameters_are_rejected(self):
        profile = classify_failures([{"agent_status": "COMPLETED", "events": []}])
        with self.assertRaises(ValueError):
            operator_probabilities(profile, tau=0.0)
        with self.assertRaises(ValueError):
            operator_probabilities(profile, epsilon=0.0)


if __name__ == "__main__":
    unittest.main()
