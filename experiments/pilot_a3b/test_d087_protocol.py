"""Pre-execution tests for D-087 frozen protocol and candidate integrity."""
import hashlib
import json
import unittest
from pathlib import Path

from d087_challenge import LOCK_PATH, MANIFEST_PATH, build_manifest, validate_lock, validate_manifest
from d087_replication import FROZEN_PATH, _decision, load_frozen_candidates
from dependency_recovery import classify_scenario, public_view


class D087PreExecutionTests(unittest.TestCase):
    def test_manifest_is_locked_independent_validation(self):
        manifest = build_manifest()
        self.assertTrue(validate_manifest(manifest)["ok"])
        self.assertTrue(validate_lock(manifest, LOCK_PATH)["ok"])
        self.assertEqual(json.loads(MANIFEST_PATH.read_text(encoding="utf-8")), manifest)
        self.assertEqual(manifest["scenario_count"], 80)
        self.assertEqual(manifest["scenario_counts"], {"validation": 80})
        self.assertFalse(manifest["test_included"])
        self.assertFalse(manifest["test_outcomes_read"])
        for row in manifest["scenarios"]:
            self.assertEqual(classify_scenario(row), (row["label"], row["min_reachable_harm"]))
            view = public_view(row)
            self.assertNotIn("scenario_id", view)
            self.assertNotIn("seed", view)
            self.assertNotIn("label", view)
            for tool in view["tools"].values():
                for route in tool["routes"]:
                    self.assertNotIn("outcomes", route)
                    self.assertNotIn("receipt_delay", route)

    def test_frozen_candidates_match_original_selected_genomes(self):
        frozen = load_frozen_candidates(FROZEN_PATH)
        original = json.loads(Path("experiments/pilot_a3b/results/d086_evolution/d086_experiment_runs.json").read_text(encoding="utf-8"))
        self.assertEqual(frozen["source_config_sha256"], hashlib.sha256(Path("experiments/pilot_a3b/d086_experiment_config.json").read_bytes()).hexdigest())
        self.assertFalse(frozen["train_search_performed"])
        self.assertFalse(frozen["new_genomes_created"])
        self.assertFalse(frozen["test_accessed"])
        for candidate in frozen["candidates"]:
            source = next(run for run in original if run["arm"] == "NSGA-III" and run["seed"] == candidate["seed"])
            self.assertEqual(candidate["genome"], source["selection"]["genome"])
            self.assertTrue(any(record["genome"] == candidate["genome"] for record in source["archive"]))

    def test_any_hard_violation_prevents_partial_success(self):
        decision = _decision(
            [{"seed": 711, "r3_success": 1.0, "r4_success": 1.0,
              "condrec": 1.0, "constraint_count": 1, "r3_cost": 1.0}],
            [], {"Greedy": {"r3_cost": 10.0}},
        )
        self.assertEqual(decision["status"], "REPLICATION_FAILED")
        self.assertEqual(decision["research_decision"], "NO_GO")

    def test_replication_module_has_no_search_or_test_entry(self):
        import d087_replication
        self.assertFalse(hasattr(d087_replication, "run_search"))
        self.assertFalse(hasattr(d087_replication, "execute_final_evaluation_once"))


if __name__ == "__main__":
    unittest.main()
