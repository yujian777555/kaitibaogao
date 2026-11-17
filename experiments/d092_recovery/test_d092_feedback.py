"""D-092 feedback aggregation and operator-probability synthetic tests."""
from __future__ import annotations

import math
import unittest

from d092_feedback import (
    FEEDBACK_NAMES,
    combine_feedback,
    compute_feedback,
    feedback_features,
    operator_probabilities,
)


def view(**overrides):
    values = {
        "row_count": 96,
        "attempt_count": 0,
        "failure_attempt_count": 0,
        "dependency_blocked_attempt_count": 0,
        "pending_row_count": 0,
        "runtime_abort_row_count": 0,
        "unsuccessful_escalation_row_count": 0,
        "avoidable_harm_sum": 0,
    }
    values.update(overrides)
    return {"feedback_marginals": values}


class TestFeedbackAggregation(unittest.TestCase):
    def test_combine_only_sums_the_current_offspring_views(self):
        views = [view(attempt_count=1, failure_attempt_count=1, pending_row_count=1) for _ in range(12)]
        combined = combine_feedback(views)
        self.assertEqual(combined["row_count"], 1152)
        self.assertEqual(combined["attempt_count"], 12)
        self.assertEqual(combined["failure_attempt_count"], 12)
        self.assertEqual(combined["pending_row_count"], 12)

    def test_six_features_have_exact_preregistered_denominators(self):
        combined = combine_feedback([
            view(
                attempt_count=10,
                failure_attempt_count=2,
                dependency_blocked_attempt_count=1,
                pending_row_count=24,
                runtime_abort_row_count=12,
                unsuccessful_escalation_row_count=48,
                avoidable_harm_sum=48,
            )
        ])
        result = compute_feedback(combined)
        self.assertEqual(result["r"], 0.2)
        self.assertEqual(result["d"], 0.1)
        self.assertEqual(result["p"], 24 / 96)
        self.assertEqual(result["a"], 12 / 96)
        self.assertEqual(result["u"], 48 / 96)
        self.assertEqual(result["h"], 48 / (4 * 96))
        self.assertEqual(tuple(result[name] for name in FEEDBACK_NAMES), (result["r"], result["d"], result["p"], result["a"], result["u"], result["h"]))

    def test_zero_denominator_and_invalid_counts_fail_closed(self):
        zero = compute_feedback(combine_feedback([view()]))
        self.assertTrue(all(zero[name] == 0 for name in FEEDBACK_NAMES))
        with self.assertRaises(ValueError):
            compute_feedback(combine_feedback([view(attempt_count=1, failure_attempt_count=2)]))
        with self.assertRaises(ValueError):
            compute_feedback(combine_feedback([view(pending_row_count=97)]))

    def test_harm_is_capped_at_one(self):
        self.assertEqual(compute_feedback(combine_feedback([view(avoidable_harm_sum=1000)]))["h"], 1.0)


class TestFeedbackMapping(unittest.TestCase):
    def test_matrix_maps_features_to_expected_blocks(self):
        features = {"r": 0.2, "d": 0.1, "p": 0.25, "a": 0.125, "u": 0.5, "h": 1.0}
        actual = feedback_features(features)
        for value, expected in zip(actual, (0.1125, 0.15, 0.28125, 1.0)):
            self.assertAlmostEqual(value, expected, places=12)

    def test_zero_feedback_is_exactly_uniform(self):
        probabilities = operator_probabilities((0.0, 0.0, 0.0, 0.0))
        self.assertEqual(probabilities, (0.25, 0.25, 0.25, 0.25))

    def test_softmax_is_stable_bounded_and_normalized(self):
        probabilities = operator_probabilities((1000.0, 0.0, -1000.0, 1.0))
        self.assertAlmostEqual(sum(probabilities), 1.0, places=12)
        self.assertTrue(all(0.025 <= value <= 0.925 for value in probabilities))
        self.assertTrue(math.isfinite(value) for value in probabilities)
        self.assertGreater(probabilities[0], probabilities[2])

    def test_feature_vector_rejects_wrong_length(self):
        with self.assertRaises(ValueError):
            operator_probabilities((0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
