"""D-092 evaluator/view tests; no real Train rollout is executed."""
from __future__ import annotations

import unittest
from pathlib import Path

from d092_evaluator import (
    HARD_FIELDS,
    assert_optimizer_view,
    build_evaluation_views,
    complete_phenotype_collapse,
    evaluate_train_genome,
    evaluate_with_rollouts,
    load_train_manifest,
    semantic_trace_changed,
)
from d092_genome import TypedGenome


def row(scenario_id, family, label, success=1, harm=0, cost=1, action=("WAIT",), observation="WAITED"):
    conditional = success if label in ("R1", "R2") else None
    correct = success if label == "R3" else None
    return {
        "scenario_id": scenario_id,
        "task_family_id": family,
        "label": label,
        "class_success": success,
        "task_success": 0,
        "conditional_recovery_success": conditional,
        "correct_escalation": correct,
        "residual_side_effects": 0,
        "min_reachable_harm": 0,
        "avoidable_harm": harm,
        "action_cost": cost,
        "recovery_cost": cost,
        "decision_count": 1,
        "policy_selected_escalation": 1 if label in ("R3", "R4") else 0,
        "safe_stop": 0,
        "runtime_forced_abort": 0,
        "pending_compensation": 0,
        "duplicate_compensation": 0,
        "invalid_action_count": 0,
        "unauthorized_action_count": 0,
        "illegal_state_transition_count": 0,
        "pending_count": 0,
        "duplicate_count": 0,
        "runtime_abort_count": 0,
        "constraint_episode": 0,
        "contract_blocked_attempts": 0,
        "dependency_blocked_attempts": 0,
        "attempt_count": 0,
        "failure_attempt_count": 0,
        "dependency_blocked_attempt_count": 0,
        "final_tool_states": {"A": "COMMITTED"},
        "trace": [{"action": list(action), "observation": observation, "cost": cost, "tick": 0}],
    }


class TestAggregationAndViews(unittest.TestCase):
    def test_family_equal_fitness_and_feedback_marginals(self):
        rows = []
        for family, success, harm in [("fa", 1, 0), ("fb", 0, 2)]:
            for label in ("R1", "R2", "R3", "R4"):
                rows.append(row(f"{family}|{label}", family, label, success=success, harm=harm, cost=3))
        optimizer, audit = build_evaluation_views(rows, "genome-x")
        self.assertEqual(optimizer["fitness"]["R3"], 0.5)
        self.assertEqual(optimizer["fitness"]["R4"], 0.5)
        self.assertEqual(optimizer["fitness"]["CondRec"], 0.5)
        self.assertEqual(optimizer["fitness"]["Harm"], 1.0)
        self.assertEqual(optimizer["fitness"]["RecoveryCost"], 3.0)
        self.assertEqual(optimizer["feedback_marginals"]["row_count"], 8)
        self.assertEqual(optimizer["feedback_marginals"]["avoidable_harm_sum"], 8)
        self.assertEqual(optimizer["feedback_marginals"]["unsuccessful_escalation_row_count"], 2)
        self.assertEqual(audit["evaluator_internal_rows"], rows)
        self.assertIn("hash_to_record", audit)
        assert_optimizer_view(optimizer)

    def test_optimizer_has_no_per_scenario_or_joinable_fields(self):
        optimizer, audit = build_evaluation_views([row("synthetic|R3", "f", "R3")], "g")
        forbidden = {"scenario_id", "label", "episode_reference", "conditional_recovery_success", "correct_escalation", "class_success", "min_reachable_harm"}

        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)
        walk(optimizer)
        self.assertEqual(audit["evaluator_internal_rows"][0]["scenario_id"], "synthetic|R3")
        with self.assertRaises(ValueError):
            assert_optimizer_view(dict(optimizer, scenario_id="leak"))

    def test_trace_hash_and_semantic_probe_projection_are_distinct(self):
        first = row("s", "f", "R3", cost=1)
        cost_only = row("s", "f", "R3", cost=2)
        changed_action = row("s", "f", "R3", cost=2, action=("ESCALATE",), observation="ESCALATED")
        view_a, _ = build_evaluation_views([first], "g")
        view_b, _ = build_evaluation_views([cost_only], "g")
        view_c, _ = build_evaluation_views([changed_action], "g")
        self.assertNotEqual(view_a["phenotype_hashes"]["trace"], view_b["phenotype_hashes"]["trace"])
        self.assertFalse(semantic_trace_changed(first, cost_only))
        self.assertTrue(semantic_trace_changed(first, changed_action))

    def test_complete_collapse_and_diversity_ratio(self):
        view_a, _ = build_evaluation_views([row("s", "f", "R3")], "g")
        view_b, _ = build_evaluation_views([row("s", "f", "R3", harm=1, action=("ESCALATE",), observation="ESCALATED")], "h")
        collapsed = complete_phenotype_collapse([view_a, view_a])
        self.assertTrue(collapsed["complete_phenotype_collapse"])
        diverse = complete_phenotype_collapse([view_a, view_b])
        self.assertFalse(diverse["complete_phenotype_collapse"])
        self.assertEqual(diverse["diversity_ratio_trace"], 1.0)

    def test_nonfinite_metrics_fail_closed(self):
        invalid = row("s", "f", "R3")
        invalid["avoidable_harm"] = float("nan")
        with self.assertRaises(ValueError):
            build_evaluation_views([invalid], "g")


class TestSyntheticEvaluationAndTrainGuard(unittest.TestCase):
    def test_synthetic_rollout_adapter_is_reproducible_and_ordered(self):
        scenarios = [{"scenario_id": "b"}, {"scenario_id": "a"}]
        calls = []

        def rollout(genome, scenario, seed, unique_ordinal):
            calls.append((genome, scenario["scenario_id"], seed, unique_ordinal))
            return row(scenario["scenario_id"], "synthetic", "R3", action=("WAIT",), observation="WAITED")

        first = evaluate_with_rollouts(TypedGenome(), scenarios, rollout, seed=711, unique_ordinal=0)
        second = evaluate_with_rollouts(TypedGenome(), scenarios, rollout, seed=711, unique_ordinal=0)
        self.assertEqual(calls[:2], calls[2:])
        self.assertEqual(first["optimizer_reward_view"], second["optimizer_reward_view"])

    def test_train_execution_is_blocked_without_explicit_double_authorization(self):
        with self.assertRaises(PermissionError):
            evaluate_train_genome(TypedGenome())

    def test_train_manifest_can_be_validated_without_rollout(self):
        path = Path(__file__).resolve().parent.parent / "d090_recovery" / "results" / "d090_train_manifest.json"
        manifest = load_train_manifest(path)
        self.assertEqual(manifest["scenario_count"], 96)
        self.assertEqual(len({row["scenario_id"] for row in manifest["scenarios"]}), 96)
        self.assertTrue(all(row["split"] == "train" for row in manifest["scenarios"]))


if __name__ == "__main__":
    unittest.main()
