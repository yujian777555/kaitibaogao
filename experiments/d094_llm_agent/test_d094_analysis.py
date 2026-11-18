"""D-094 paired-result and Genome/Phenotype analysis tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from d094_analysis import analyze_phase2
from run_d094_phase2 import Phase2Config, run_phase2
from test_d094_phase2 import mock_client_factory


class TestD094Analysis(unittest.TestCase):
    def test_analysis_has_paired_differences_gene_coverage_and_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_phase2(
                root,
                Phase2Config(
                    seeds=(101,),
                    population_size=4,
                    generations=1,
                    max_concurrency=2,
                    global_request_cap=1000,
                    global_cost_cap=1.0,
                ),
                client_factory=mock_client_factory,
            )
            result = analyze_phase2(root)
            self.assertEqual(result["research_decision"], "NO_CLEAR_GAIN")
            self.assertEqual(
                result["paired_differences"]["B1_minus_B0"]["101"]["task_success_rate"],
                -1.0,
            )
            self.assertEqual(
                result["paired_differences"]["B2_minus_B1"]["101"]["task_success_rate"],
                0.0,
            )
            self.assertEqual(len(result["gene_coverage"]), 6)
            self.assertEqual(result["evaluation_duplicate_count"], 0)
            self.assertIsNone(result["proposal_duplicate_rate"])
            self.assertIn("mutation_counts_status", result)
            self.assertTrue((root / "analysis.json").exists())


if __name__ == "__main__":
    unittest.main()
