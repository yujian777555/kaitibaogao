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

    def test_csv_output_includes_candidate_only_fields(self):
        import csv
        import tempfile
        from d087_replication import write_outputs
        metrics = {
            "r3_success": 1.0, "r4_success": 1.0, "condrec": 1.0,
            "r3_cost": 1.0, "constraint_count": 0,
            "duplicate_count": 0, "pending_count": 0,
        }
        summary = {
            "decision": "PARTIAL_REPLICATION",
            "decision_detail": {"candidate_pass_count": 0},
            "raw_row_count": 2, "evaluation_calls": 2, "cache_hits": 0,
            "manifest_sha256": "synthetic", "candidate_sha256": "synthetic",
            "source_config_sha256": "synthetic", "algorithm_sha256": {},
            "budget": {"total_cap": 1040},
            "baselines": {"Hand": {"method": "Hand", "seed": -1, **metrics}},
            "candidates": [{"method": "FrozenNSGA-III", "seed": 711, **metrics}],
        }
        rows = [
            {"method": "Hand", "optimizer_seed": -1, "scenario_id": "a", "trace": []},
            {"method": "FrozenNSGA-III", "optimizer_seed": 711,
             "scenario_id": "b", "genome_sha256": "candidate-only", "trace": []},
        ]
        with tempfile.TemporaryDirectory() as temp:
            write_outputs(summary, rows, [], temp)
            with (Path(temp) / "d087_replication_rows.csv").open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertIn("genome_sha256", reader.fieldnames)
                self.assertEqual(next(reader)["genome_sha256"], "")
                self.assertEqual(next(reader)["genome_sha256"], "candidate-only")
            raw = (Path(temp) / "d087_replication_rows.csv").read_bytes()
            self.assertNotIn(b"\r\r\n", raw)

    def test_artifact_hashes_are_line_ending_independent(self):
        import tempfile
        from d087_replication import _canonical_file_sha
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "crlf"
            second = Path(temp) / "lf"
            first.write_bytes(b"a\r\nb\r\n")
            second.write_bytes(b"a\nb\n")
            self.assertEqual(_canonical_file_sha(first), _canonical_file_sha(second))
            self.assertNotEqual(hashlib.sha256(first.read_bytes()), hashlib.sha256(second.read_bytes()))

    def test_replication_module_has_no_search_or_test_entry(self):
        import d087_replication
        self.assertFalse(hasattr(d087_replication, "run_search"))
        self.assertFalse(hasattr(d087_replication, "execute_final_evaluation_once"))


if __name__ == "__main__":
    unittest.main()
