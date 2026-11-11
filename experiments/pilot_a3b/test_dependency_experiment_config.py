"""Protocol and failure-path tests for the D-086 experiment driver."""
import json
import unittest
from pathlib import Path

from dependency_experiment import (
    CONFIG_PATH,
    analyze_runs,
    validate_config,
)


class ExperimentConfigTests(unittest.TestCase):
    def test_frozen_config_is_exact(self):
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.assertEqual(validate_config(config), config)
        changed = dict(config)
        changed["optimizer_seeds"] = config["optimizer_seeds"] + [999]
        with self.assertRaises(ValueError):
            validate_config(changed)
        changed = dict(config)
        changed["population_size"] = 16
        with self.assertRaises(ValueError):
            validate_config(changed)

    def test_hold_is_no_go_not_a_fake_improvement(self):
        class Ledger:
            stats = {
                "evaluation_calls": {"train": 0, "validation": 0},
                "unique_episode_equivalent": {"train": 0, "validation": 0},
                "cache_hits": {"train": 0, "validation": 0},
            }
        runs = [{
            "arm": "C-NSGA-III",
            "seed": 711,
            "selection": {"status": "HOLD"},
            "budget_exhausted": False,
            "archive": [],
            "ledger": Ledger(),
        }]
        analysis = analyze_runs(runs)
        self.assertEqual(analysis["status"], "NO_GO")
        self.assertIn("selected_all_seeds", analysis["failed_criteria"])
        self.assertIn("cost_below_greedy", analysis["failed_criteria"])


if __name__ == "__main__":
    unittest.main()
