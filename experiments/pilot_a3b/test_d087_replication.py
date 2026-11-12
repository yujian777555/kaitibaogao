"""D-087 frozen-candidate replication, isolation, and artifact tests."""
import hashlib
import json
import unittest
from pathlib import Path

from d087_challenge import (
    LOCK_PATH,
    MANIFEST_PATH,
    build_manifest,
    make_lock,
    validate_lock,
    validate_manifest,
)
from d087_replication import (
    FROZEN_PATH,
    OUTDIR,
    write_outputs,
)
from d087_replication_audit import audit_replication


class D087ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_manifest()
        cls.frozen = json.loads(FROZEN_PATH.read_text(encoding="utf-8"))
        cls.summary = json.loads((OUTDIR / "d087_replication_summary.json").read_text(encoding="utf-8"))

    def test_new_validation_is_independent_and_deterministic(self):
        self.assertEqual(self.manifest, build_manifest())
        self.assertEqual(self.manifest["scenario_count"], 80)
        self.assertEqual(self.manifest["scenario_counts"], {"validation": 80})
        self.assertEqual(self.manifest["family_count"], 4)
        self.assertEqual(len({row["scenario_id"] for row in self.manifest["scenarios"]}), 80)
        self.assertTrue(all(row["split"] == "validation" for row in self.manifest["scenarios"]))
        self.assertFalse(self.manifest["test_included"])
        self.assertFalse(self.manifest["test_outcomes_read"])
        self.assertFalse(self.manifest["train_included"])
        old = json.loads(Path("experiments/pilot_a3b/results/d086_dependency_challenge/dependency_manifest.json").read_text(encoding="utf-8"))
        self.assertFalse({row["scenario_id"] for row in self.manifest["scenarios"]} & {row["scenario_id"] for row in old["scenarios"]})
        self.assertFalse({row["task_family_id"] for row in self.manifest["scenarios"]} & {row["task_family_id"] for row in old["scenarios"]})

    def test_exact_repeat_transitions_and_public_view(self):
        for row in self.manifest["scenarios"]:
            repeat = row["repeat"]
            primary = row["tools"][0]["routes"][0]
            if row["difficulty_stratum"] in ("D3_DEPENDENT_ABORT", "D4_BLOCKED_COMPENSATION"):
                if repeat == 0:
                    self.assertEqual(primary["outcomes"], [True])
                elif repeat == 1:
                    self.assertEqual(primary["outcomes"], [False, True])
                elif repeat == 2:
                    self.assertEqual(primary["outcomes"], [False, False, True])
                elif repeat == 3:
                    self.assertEqual(primary["outcomes"], [True])
                else:
                    self.assertEqual(primary["outcomes"], [False, True])
            view = __import__("dependency_recovery").public_view(row)
            self.assertNotIn("scenario_id", view)
            self.assertNotIn("seed", view)
            self.assertNotIn("label", view)
            for tool in view["tools"].values():
                for route in tool["routes"]:
                    self.assertNotIn("outcomes", route)
                    self.assertNotIn("receipt_delay", route)
                    self.assertNotIn("receipt", route)
                    self.assertNotIn("pending_success", route)

    def test_every_label_recomputes_and_saved_lock_matches(self):
        from dependency_recovery import classify_scenario
        for row in self.manifest["scenarios"]:
            label, minimum = classify_scenario(row)
            self.assertEqual(label, row["label"])
            self.assertEqual(minimum, row["min_reachable_harm"])
        saved = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.manifest)
        self.assertTrue(LOCK_PATH.is_file())
        self.assertTrue(validate_lock(saved, LOCK_PATH)["ok"])
        self.assertTrue(validate_manifest(saved)["ok"])

    def test_frozen_candidates_match_original_selection_without_search(self):
        self.assertEqual(len(self.frozen["candidates"]), 5)
        self.assertFalse(self.frozen["train_search_performed"])
        self.assertFalse(self.frozen["new_genomes_created"])
        self.assertFalse(self.frozen["test_accessed"])
        original = json.loads(Path("experiments/pilot_a3b/results/d086_evolution/d086_experiment_runs.json").read_text(encoding="utf-8"))
        for item in self.frozen["candidates"]:
            source = next(run for run in original if run["arm"] == "NSGA-III" and run["seed"] == item["seed"])
            self.assertEqual(item["genome"], source["selection"]["genome"])
            self.assertTrue(any(record["genome"] == item["genome"] for record in source["archive"]))
        self.assertEqual(self.frozen["source_config_sha256"], hashlib.sha256(Path("experiments/pilot_a3b/d086_experiment_config.json").read_bytes()).hexdigest())
        self.assertEqual(self.frozen["source_runs_sha256"], hashlib.sha256(Path("experiments/pilot_a3b/results/d086_evolution/d086_experiment_runs.json").read_bytes()).hexdigest())

    def test_saved_replication_scope_and_raw_ledger(self):
        summary = self.summary
        self.assertEqual(summary["raw_row_count"], 1040)
        self.assertEqual(summary["evaluation_calls"], 1040)
        self.assertEqual(summary["cache_hits"], 0)
        self.assertEqual(summary["candidate_count"], 5)
        self.assertEqual(summary["baseline_count"], 8)
        self.assertFalse(summary["train_search_performed"])
        self.assertFalse(summary["test_accessed"])
        self.assertEqual(len(summary["candidates"]), 5)
        self.assertEqual(len(summary["baselines"]), 8)
        self.assertEqual(len(summary["per_family"]), 20)
        self.assertIn(summary["decision"], {
            "REPLICATION_SUPPORTED", "PARTIAL_REPLICATION", "REPLICATION_FAILED", "INVALID",
        })

    def test_any_hard_violation_prevents_partial_success(self):
        from d087_replication import _decision
        decision = _decision(
            [{
                "seed": 711, "r3_success": 1.0, "r4_success": 1.0,
                "condrec": 1.0, "constraint_count": 1, "r3_cost": 1.0,
            }],
            [],
            {"Greedy": {"r3_cost": 10.0}},
        )
        self.assertTrue(decision["any_candidate_hard_violation"])
        self.assertEqual(decision["status"], "REPLICATION_FAILED")
        self.assertEqual(decision["research_decision"], "NO_GO")

    def test_independent_audit_and_immutable_outputs(self):
        report = audit_replication(OUTDIR)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["raw_row_count"], 1040)
        self.assertFalse(report["test_accessed"])
        changed = dict(self.summary)
        changed["decision"] = "INVALID"
        with self.assertRaises(FileExistsError):
            write_outputs(changed, [], [], OUTDIR)


if __name__ == "__main__":
    unittest.main()
