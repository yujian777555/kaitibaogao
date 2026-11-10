"""R4 regression tests for one shared Student-t implementation.

These tests exercise the production inferential helper and the Monte Carlo
adapter. They intentionally cover degenerate and near-degenerate inputs.
"""
import math
import unittest

import numpy as np

from power_hierarchical import _pvals_student_t, family_level_tests, student_t_summary


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

    def test_known_answer_confidence_interval(self):
        result = student_t_summary(np.array([1., 2., 3., 4., 5.]))
        self.assertAlmostEqual(result["ci95"][0], 1.036756838522443, places=8)
        self.assertAlmostEqual(result["ci95"][1], 4.963243161477557, places=8)

    def test_degenerate_effect_has_no_misleading_confidence_interval(self):
        self.assertIsNone(student_t_summary(np.zeros(34))["ci95"])
        self.assertIsNone(student_t_summary(np.full(34, 0.1))["ci95"])

    def test_monte_carlo_mode_skips_ci_inversion_without_changing_p(self):
        values = np.array([1., 2., 3., 4., 5.])
        full = student_t_summary(values)
        fast = student_t_summary(values, include_ci=False)
        self.assertEqual(fast["p_two_sided"], full["p_two_sided"])
        self.assertIsNone(fast["ci95"])

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

    def test_family_level_analysis_reports_all_zero_as_p_one(self):
        hierarchy = {"fam_means": {"f0": 0.0, "f1": 0.0}}
        result = family_level_tests(hierarchy)
        self.assertEqual(result["student_t"]["status"], "zero_effect_zero_variance")
        self.assertEqual(result["student_t"]["t"], 0.0)
        self.assertEqual(result["student_t"]["p_two_sided"], 1.0)

    def test_family_level_analysis_marks_nonzero_constant_limit(self):
        hierarchy = {"fam_means": {"f0": 0.1, "f1": 0.1}}
        result = family_level_tests(hierarchy)
        self.assertEqual(result["student_t"]["status"], "nonzero_constant_limit")
        self.assertTrue(math.isinf(result["student_t"]["t"]))
        self.assertEqual(result["student_t"]["p_two_sided"], 0.0)

    def test_signflip_uses_neutral_name_and_records_actual_seed(self):
        hierarchy = {"fam_means": {f"f{i}": 0.1 + i * 0.01 for i in range(16)}}
        result = family_level_tests(hierarchy, seed=20261112)
        self.assertIn("signflip", result)
        self.assertNotIn("signflip_exact", result)
        signflip = result["signflip"]
        self.assertEqual(signflip["n_resamples"], 10000)
        self.assertEqual(signflip["random_seed_used"], 20261113)
        self.assertEqual(signflip["n_families"], 16)
        self.assertIn("Monte Carlo", signflip["method"])

    def test_exact_signflip_records_no_random_seed(self):
        hierarchy = {"fam_means": {f"f{i}": 0.1 + i * 0.01 for i in range(6)}}
        signflip = family_level_tests(hierarchy)["signflip"]
        self.assertEqual(signflip["n_resamples"], 64)
        self.assertIsNone(signflip["random_seed_used"])
        self.assertIn("exact enumeration", signflip["method"])


if __name__ == "__main__":
    unittest.main()
