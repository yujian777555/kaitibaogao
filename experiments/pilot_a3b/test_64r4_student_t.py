"""R4 regression tests for one shared Student-t implementation.

These tests exercise the production inferential helper and the Monte Carlo
adapter. They intentionally cover degenerate and near-degenerate inputs.
"""
import math
import unittest

import numpy as np

from power_hierarchical import _pvals_student_t, student_t_summary


class StudentTBoundaryTests(unittest.TestCase):
    def test_all_zero_differences_are_not_significant(self):
        result = student_t_summary(np.zeros(34))
        self.assertEqual(result["status"], "zero_effect_zero_variance")
        self.assertEqual(result["t"], 0.0)
        self.assertEqual(result["p_two_sided"], 1.0)

    def test_positive_constant_differences_use_degenerate_limit(self):
        result = student_t_summary(np.full(34, 0.1))
        self.assertEqual(result["status"], "nonzero_constant_limit")
        self.assertTrue(math.isinf(result["t"]))
        self.assertGreater(result["t"], 0)
        self.assertEqual(result["p_two_sided"], 0.0)

    def test_negative_constant_differences_use_degenerate_limit(self):
        result = student_t_summary(np.full(34, -0.1))
        self.assertEqual(result["status"], "nonzero_constant_limit")
        self.assertTrue(math.isinf(result["t"]))
        self.assertLess(result["t"], 0)
        self.assertEqual(result["p_two_sided"], 0.0)

    def test_near_zero_but_resolvable_variance_is_not_collapsed(self):
        values = np.array([0.0, 1e-8, 2e-8, 3e-8, 4e-8])
        result = student_t_summary(values)
        self.assertEqual(result["status"], "regular")
        self.assertTrue(math.isfinite(result["t"]))
        self.assertGreater(result["p_two_sided"], 0.0)
        self.assertLess(result["p_two_sided"], 1.0)

    def test_known_answer_student_t(self):
        # [1,2,3,4,5]: t=4.2426406871, df=4, two-sided p=0.013846832988...
        result = student_t_summary(np.array([1., 2., 3., 4., 5.]))
        self.assertAlmostEqual(result["t"], 4.242640687119285, places=10)
        self.assertEqual(result["df"], 4)
        self.assertAlmostEqual(result["p_two_sided"], 0.013235599563683, places=9)

    def test_power_simulation_uses_same_zero_variance_rule(self):
        rows = np.zeros((3, 34), dtype=float)
        p_values = _pvals_student_t(rows)
        np.testing.assert_array_equal(p_values, np.ones(3))

    def test_power_simulation_uses_same_constant_limit(self):
        rows = np.full((2, 34), 0.1, dtype=float)
        p_values = _pvals_student_t(rows)
        np.testing.assert_array_equal(p_values, np.zeros(2))

    def test_rejects_fewer_than_two_families(self):
        with self.assertRaises(ValueError):
            student_t_summary([0.1])
        with self.assertRaises(ValueError):
            _pvals_student_t(np.array([[0.1]]))

    def test_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            student_t_summary([0.1, float("nan")])


if __name__ == "__main__":
    unittest.main()
