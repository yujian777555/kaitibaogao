"""Reproducibility tests for the D-086 fixed-policy optimization-space gate."""
import json
import unittest

from dependency_challenge import build_manifest
from dependency_gate import (
    GATE_PATH,
    METHODS,
    evaluate_manifest,
    gate_decision,
    summarize,
)


class DependencyGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = evaluate_manifest(build_manifest())
        cls.summary = summarize(cls.rows)
        cls.gate = gate_decision(cls.rows)

    def test_all_fixed_methods_run_on_paired_scenarios(self):
        self.assertEqual(len(self.rows), len(METHODS) * 96)
        self.assertEqual(self.rows, evaluate_manifest(build_manifest()))
        for scenario_id in {row["scenario_id"] for row in self.rows}:
            methods = {row["method"] for row in self.rows if row["scenario_id"] == scenario_id}
            self.assertEqual(methods, set(METHODS))
        for row in self.rows:
            for key in (
                "conditional_recovery_success", "correct_escalation",
                "prefix_compensation_success", "residual_side_effects",
                "avoidable_harm", "recovery_cost", "action_cost", "constraint_violation",
            ):
                self.assertIn(key, row)

    def test_family_equal_summary_and_decision_are_reproducible(self):
        for split, family_count in (("train", 6), ("validation", 2)):
            for method in METHODS:
                for label in ("R1", "R2", "R3", "R4"):
                    group = self.summary[f"{split}|{method}|{label}"]
                    self.assertEqual(group["family_count"], family_count)
                    self.assertEqual(group["scenario_count"], family_count * 3)
        recomputed = gate_decision(self.rows)
        self.assertEqual(recomputed, self.gate)
        self.assertIn(self.gate["status"], {
            "CEILING_NO_EA", "FIXED_DOMINANT_NO_EA", "CANDIDATE_SPACE_REVIEW_REQUIRED",
        })
        self.assertEqual(self.gate["optimizer_runs"], 0)
        self.assertFalse(self.gate["test_accessed"])

    def test_saved_gate_matches_raw_recomputation(self):
        saved = json.loads(GATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved["summary"], self.summary)
        self.assertEqual(saved["decision"], self.gate)


if __name__ == "__main__":
    unittest.main()
