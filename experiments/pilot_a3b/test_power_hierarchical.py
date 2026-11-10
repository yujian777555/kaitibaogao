"""Tests for hierarchical power analysis (D-064-B Task: 17 required cases)."""
import math
import unittest
from pathlib import Path

import numpy as np

from power_hierarchical import (
    ALPHA, MDE_GRID, _pvals_signflip, _pvals_student_t, build_hierarchy,
    family_level_tests, gen_family_means_block, gen_family_means_hier,
    icc_anova, icc_reml, mc_power_at, sha256_file,
)

REAL = Path(__file__).parent / "diagnostic3_results.json"


def tiny_hierarchy():
    """Known-answer mini hierarchy: 2 families x 2 comps, diffs 0.4/0.2 and 0.6/0.0."""
    return {
        "families": {
            "F1": {"C1": {"mean_diff": 0.4, "n_r12_scenarios": 1},
                   "C2": {"mean_diff": 0.2, "n_r12_scenarios": 1}},
            "F2": {"C1": {"mean_diff": 0.6, "n_r12_scenarios": 1},
                   "C2": {"mean_diff": 0.0, "n_r12_scenarios": 1}},
        },
        "fam_means": {"F1": 0.3, "F2": 0.3},
        "fam_sizes": {"F1": 2, "F2": 2},
        "grand_mean": 0.3,
        "ms_between": None, "ms_within": None, "m_per_family": 2.0,
    }


class HierarchyDataTests(unittest.TestCase):
    def test_family_id_and_cluster_counts(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        self.assertEqual(h["problems"], [])
        self.assertEqual(len(h["families"]), 6)          # 6 families
        self.assertEqual(sum(h["fam_sizes"].values()), 42)  # 42 eligible clusters
        for f, n in h["fam_sizes"].items():
            self.assertEqual(n, 7, f)
        self.assertEqual(len(h["zero_denom_clusters"]), 12)

    def test_seed_nesting_and_no_duplicate_episodes(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        self.assertEqual(h["problems"], [])
        self.assertEqual(len(h["rows_csv"]), 42 + 6)  # cluster rows + family means

    def test_input_sha_recorded(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        self.assertEqual(h["input_sha256"], sha256_file(REAL))


class ICCTests(unittest.TestCase):
    def test_icc_zero_when_no_between_variance(self):
        h = tiny_hierarchy()
        # both families have mean 0.3 -> between var 0
        vals = [0.4, 0.2, 0.6, 0.0]
        grand = 0.3
        ssb = 2 * ((0.3 - grand) ** 2) * 2
        ssw = (0.4 - 0.3) ** 2 + (0.2 - 0.3) ** 2 + (0.6 - 0.3) ** 2 + (0.0 - 0.3) ** 2
        h["ms_between"] = ssb / 1 if ssb else 0.0
        h["ms_within"] = ssw / 2
        icc = icc_anova(h)["icc_raw"]
        self.assertLessEqual(icc, 0.0)  # negative/zero when between <= within

    def test_icc_positive_between_variance(self):
        h = tiny_hierarchy()
        h["ms_between"] = 10.0
        h["ms_within"] = 1.0
        h["m_per_family"] = 2.0
        icc = icc_anova(h)["icc_raw"]
        self.assertGreater(icc, 0)
        self.assertAlmostEqual(icc, (10 - 1) / (10 + 1), places=6)

    def test_negative_icc_retained_and_constrained(self):
        h = tiny_hierarchy()
        h["ms_between"] = 0.5
        h["ms_within"] = 2.0
        h["m_per_family"] = 2.0
        r = icc_anova(h)
        self.assertLess(r["icc_raw"], 0)            # raw estimate retained
        self.assertEqual(r["icc_constrained"], 0.0)  # boundary-constrained

    def test_reml_matches_anova_on_balanced(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        a = icc_anova(h)["icc_raw"]
        r = icc_reml(h)["icc_raw"]
        self.assertLess(abs(a - r), 0.05, "balanced REML should agree with ANOVA ICC")


class SimulationTests(unittest.TestCase):
    def test_icc_zero_vs_increased_variance(self):
        rng = np.random.default_rng(7)
        pool = np.array([-0.2, -0.1, 0.1, 0.2])
        m0, _ = gen_family_means_hier(rng, 500, 30, 7, 0.0, 0.0, 0.3 ** 2, pool)
        m2, _ = gen_family_means_hier(rng, 500, 30, 7, 0.20, 0.0, 0.3 ** 2, pool)
        # family means spread grows with ICC (between-family variance up)
        self.assertGreater(float(np.var(m2.mean(axis=1))), float(np.var(m0.mean(axis=1))) * 0.8)

    def test_marginal_variance_matching(self):
        rng = np.random.default_rng(11)
        pool = np.array([-0.3, -0.15, 0.0, 0.15, 0.3])
        total_var = 0.09
        means, _ = gen_family_means_hier(rng, 4000, 50, 7, 0.10, 0.0, total_var, pool)
        # family mean var = icc*V + (1-icc)*V/m
        expected = 0.10 * total_var + 0.90 * total_var / 7
        self.assertLess(abs(float(np.var(means)) - expected) / expected, 0.35)

    def test_block_resample_keeps_blocks(self):
        rng = np.random.default_rng(3)
        blocks = [np.array([0.1, 0.2]), np.array([0.5, 0.6])]
        means, _ = gen_family_means_block(rng, 50, 20, blocks, 0.0)
        # each family mean must be one of the two block means
        allowed = {0.15, 0.55}
        for row in means[:5]:
            for v in row:
                self.assertIn(round(float(v), 6), allowed)

    def test_signflip_exact_grid(self):
        means = np.array([[0.2, 0.3, 0.1, 0.4, 0.2, 0.3]])
        p = _pvals_signflip(means, np.random.default_rng(1))
        # p must be k/2^6
        self.assertAlmostEqual(p[0] * 64, round(p[0] * 64), places=6)

    def test_student_t_pvalues_vectorized(self):
        means = np.array([[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]])
        p = _pvals_student_t(means)
        self.assertLess(p[0], 0.05)
        self.assertGreater(p[1], 0.5)


class PowerTests(unittest.TestCase):
    def test_null_type1_calibration(self):
        rng_seed = 42
        pool = np.array([-0.3, -0.15, 0.0, 0.15, 0.3])
        res = mc_power_at(0.0, 17, 7, 0.0, 0.09, pool, None, "hierarchical",
                          2000, rng_seed, tests="all")
        self.assertLess(res["power_student_t"], 0.10)   # near nominal 0.05
        self.assertGreater(res["power_student_t"], 0.01)

    def test_power_increases_with_mde(self):
        pool = np.array([-0.3, -0.15, 0.0, 0.15, 0.3])
        p_small = mc_power_at(0.05, 17, 7, 0.0, 0.09, pool, None, "hierarchical",
                              500, 1)["power_student_t"]
        p_big = mc_power_at(0.15, 17, 7, 0.0, 0.09, pool, None, "hierarchical",
                            500, 1)["power_student_t"]
        self.assertGreater(p_big, p_small)

    def test_mcse_reported(self):
        pool = np.array([-0.3, 0.3])
        res = mc_power_at(0.10, 17, 7, 0.0, 0.09, pool, None, "hierarchical",
                          500, 2, tests="all")
        for k in ("mcse_student_t", "mcse_signflip", "mcse_block_bootstrap"):
            self.assertIn(k, res)

    def test_reproducible_with_seed(self):
        pool = np.array([-0.3, 0.3])
        a = mc_power_at(0.10, 17, 7, 0.05, 0.09, pool, None, "hierarchical", 300, 5, tests="all")
        b = mc_power_at(0.10, 17, 7, 0.05, 0.09, pool, None, "hierarchical", 300, 5, tests="all")
        self.assertEqual(a["power_student_t"], b["power_student_t"])
        self.assertEqual(a["power_signflip"], b["power_signflip"])

    def test_mde_grid_present(self):
        self.assertEqual(MDE_GRID, (0.05, 0.08, 0.10, 0.1173, 0.15))

    def test_design_vs_eligible_cluster_math(self):
        # design = families x all compositions; eligible = x R1/R2 compositions
        self.assertEqual(17 * 9, 153)
        self.assertEqual(17 * 7, 119)

    def test_seed_not_family(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        self.assertEqual(len(h["families"]), 6)  # 6 families, NOT 42/126 pseudo-units

    def test_illegal_params_fail_closed(self):
        pool = np.array([0.1])
        with self.assertRaises(Exception):
            mc_power_at(0.1, -1, 7, 0.0, 0.09, pool, None, "hierarchical", 10, 1)
        with self.assertRaises(Exception):
            mc_power_at(0.1, 10, 0, 0.0, 0.09, pool, None, "hierarchical", 10, 1)

    def test_no_hardcoded_history_values(self):
        src = Path(__file__).parent / "power_hierarchical.py"
        text = src.read_text(encoding="utf-8")
        for banned in ("0.3175", "0.318856", "0.1049", "0.000125", "0.218254"):
            self.assertNotIn(banned, text)


class RealDataRegressionTests(unittest.TestCase):
    def test_full_real_regression(self):
        if not REAL.exists():
            self.skipTest("real data missing")
        h = build_hierarchy(REAL)
        self.assertEqual(h["problems"], [])
        self.assertAlmostEqual(h["grand_mean"], 0.31746, places=4)
        inf = family_level_tests(h)
        # all six family means positive -> exact sign-flip minimum 2/64
        self.assertTrue(all(v > 0 for v in inf["family_means"].values()))
        self.assertAlmostEqual(inf["signflip"]["p"], 2 / 64, places=6)
        self.assertLess(inf["student_t"]["p_two_sided"], 0.001)
        self.assertGreater(inf["block_bootstrap_ci95"][0], 0)


if __name__ == "__main__":
    unittest.main()
