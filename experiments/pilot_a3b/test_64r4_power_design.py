"""Synthetic-only tests for the R4 power simulation driver."""
import tempfile
import unittest
from pathlib import Path

import numpy as np

from power_r4_design import (
    json_input_hashes, simulate_adversarial_missing, simulate_missing_sensitivity,
    simulate_power_grid, simulate_type_i_replication, wilson_interval,
)


class R4PowerDesignTests(unittest.TestCase):
    def test_wilson_interval_contains_estimate(self):
        interval = wilson_interval(50, 100)
        self.assertLessEqual(interval[0], 0.5)
        self.assertGreaterEqual(interval[1], 0.5)

    def test_grid_has_expected_family_icc_and_mde_cells(self):
        cells = simulate_power_grid(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=20261114,
        )
        self.assertEqual(len(cells), 24)
        self.assertEqual({c["n_families"] for c in cells}, {33, 34, 40})
        self.assertEqual({c["icc"] for c in cells}, {0.0, 0.05, 0.10, 0.20})
        self.assertEqual({c["role"] for c in cells}, {"null_type_i", "mde_power"})
        self.assertTrue(all(c["mc_reps"] == 100 for c in cells))
        self.assertTrue(all(len(c["ci95_wilson"]) == 2 for c in cells))

    def test_33_family_boundary_is_not_confirmatory_eligible(self):
        cells = simulate_power_grid(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=7,
        )
        f33 = [c for c in cells if c["n_families"] == 33]
        f34 = [c for c in cells if c["n_families"] == 34]
        self.assertTrue(all(not c["confirmatory_eligible"] for c in f33))
        self.assertTrue(all(c["confirmatory_eligible"] for c in f34))

    def test_same_seed_reproduces_exact_cells(self):
        kwargs = dict(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=19,
        )
        self.assertEqual(simulate_power_grid(**kwargs), simulate_power_grid(**kwargs))

    def test_json_content_hash_is_independent_of_line_endings(self):
        with tempfile.TemporaryDirectory() as tmp:
            lf = Path(tmp) / "lf.json"
            crlf = Path(tmp) / "crlf.json"
            lf.write_bytes(b'{"runs": []}\n')
            crlf.write_bytes(b'{"runs": []}\r\n')
            lf_hashes = json_input_hashes(lf)
            crlf_hashes = json_input_hashes(crlf)
            self.assertNotEqual(lf_hashes["raw_sha256"], crlf_hashes["raw_sha256"])
            self.assertEqual(lf_hashes["canonical_sha256"], crlf_hashes["canonical_sha256"])

    def test_technical_missing_sensitivity_tracks_family_loss_and_eligibility(self):
        cells = simulate_missing_sensitivity(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=11,
            missing_rates=(0.0, 0.05),
        )
        self.assertEqual(len(cells), 8)
        zero = [c for c in cells if c["missing_rate_per_composition_cluster"] == 0.0]
        self.assertTrue(all(c["analysis_eligibility_rate"] == 1.0 for c in zero))
        high_missing_f40 = [
            c for c in cells
            if c["n_families_design"] == 40
            and c["missing_rate_per_composition_cluster"] == 0.05
        ]
        self.assertTrue(all(c["analysis_eligibility_rate"] < 1.0 for c in high_missing_f40))

    def test_independent_seed_type_i_replication_is_reproducible(self):
        kwargs = dict(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=13,
            n_replicates=3,
        )
        first = simulate_type_i_replication(**kwargs)
        second = simulate_type_i_replication(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(first["total_mc_reps"], 300)
        self.assertEqual(len(first["cells"]), 3)

    def test_missing_sensitivity_reports_conditional_and_joint_uncertainty(self):
        cells = simulate_missing_sensitivity(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=23,
            missing_rates=(0.0, 0.01),
        )
        for cell in cells:
            self.assertIn("conditional_rejections_when_eligible", cell)
            self.assertIn("conditional_rejection_mcse", cell)
            self.assertIn("conditional_ci95_wilson", cell)
            self.assertIn("joint_rejections", cell)
            self.assertIn("joint_rejection_mcse", cell)
            self.assertIn("joint_ci95_wilson", cell)

    def test_adversarial_missing_is_reproducible_and_explicitly_labelled(self):
        kwargs = dict(
            total_var=0.08,
            eps_pool=np.array([-0.2, -0.1, 0.0, 0.1, 0.2]),
            reps=100,
            seed=29,
            missing_rates=(0.0, 0.05),
        )
        first = simulate_adversarial_missing(**kwargs)
        second = simulate_adversarial_missing(**kwargs)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 8)
        self.assertTrue(all(c["missing_pattern"] == "contiguous_prefix" for c in first))
        self.assertTrue(all("conditional_ci95_wilson" in c for c in first))
        zero = [c for c in first if c["missing_rate_per_composition_cluster"] == 0.0]
        self.assertTrue(all(c["analysis_eligibility_rate"] == 1.0 for c in zero))

    def test_invalid_residual_pool_or_variance_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "residual pool"):
            simulate_power_grid(0.08, np.array([0.1]), reps=100)
        with self.assertRaisesRegex(ValueError, "variance"):
            simulate_power_grid(0.0, np.array([-0.1, 0.1]), reps=100)


if __name__ == "__main__":
    unittest.main()
