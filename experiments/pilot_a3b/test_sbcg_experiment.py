"""Synthetic tests for the SBCG comparison matrix and accounting interfaces."""
import unittest
from unittest.mock import patch

from a3_bridge import hand_fsm
from ea import run_evolution
from sbcg import make_shared_initial_pool
from sbcg_experiment import (
    algorithm_specs,
    run_algorithm_matrix,
    reflection_proxy_fsm,
    rule_based_fsm,
    run_algorithm_arm,
)
from sbcg import fsm_fingerprint


SCENARIO = {"scenario_id": "train|synthetic", "split": "train", "task": "f1"}
VALIDATION_SCENARIO = {"scenario_id": "validation|synthetic", "split": "validation", "task": "f1"}
VERDICTS = {"train|synthetic": {"class": "R1"}, "validation|synthetic": {"class": "R1"}}


def fake_metrics(fsm, scenarios, verdicts, _weights=None):
    return {
        "objectives": (0.5, 0.0, 0.1),
        "cond_rec": 0.5,
        "avoid_resid": 0.0,
        "unnec_esc": 0.0,
        "unnec_actions_r12": 0.2,
        "corr_esc": 1.0,
        "containment": 1.0,
        "dup": 0.0,
        "sla_viol": 0.0,
        "violations": 0.0,
        "rows": [{
            "scenario_id": scenarios[0]["scenario_id"], "label": "R1",
            "class_success": 1, "decision_trace": [],
        }],
    }


class ComparisonMatrixTests(unittest.TestCase):
    def test_required_baselines_and_three_ablations_are_registered(self):
        names = {spec.name for spec in algorithm_specs()}
        self.assertEqual(names, {
            "Hand FSM", "Random", "Rule-based", "Reflection",
            "NSGA-II", "NSGA-III", "Matched-objective NSGA-II",
            "Matched-objective NSGA-III", "A", "AB", "SBCG-NSGA-III",
            "SBCG-NSGA-III-no-M1", "SBCG-NSGA-III-no-M2", "SBCG-NSGA-III-no-M3",
        })

    def test_non_llm_rule_and_reflection_proxies_are_distinct_valid_fsm(self):
        self.assertNotEqual(fsm_fingerprint(rule_based_fsm()), fsm_fingerprint(hand_fsm()))
        self.assertNotEqual(fsm_fingerprint(reflection_proxy_fsm()), fsm_fingerprint(hand_fsm()))

    def test_matched_nsga2_uses_five_objectives_without_m2_or_archive(self):
        spec = next(s for s in algorithm_specs() if s.name == "Matched-objective NSGA-II")
        sentinel = {"selection": {"status": "SELECTED"}, "episodes": 0}
        with patch("sbcg_experiment.run_sbcg_evolution", return_value=sentinel) as mocked:
            run_algorithm_arm(
                spec, make_shared_initial_pool(3, size=4), [SCENARIO], VERDICTS,
                eval_budget=4, seed=3, pop_size=2, generations=0,
            )
        kwargs = mocked.call_args.kwargs
        self.assertTrue(kwargs["use_five_objectives"])
        self.assertFalse(kwargs["use_stratified_counterexamples"])
        self.assertFalse(kwargs["use_elite_archive"])
        self.assertEqual(kwargs["optimizer"], "nsga2")

    def test_no_m3_ablation_removes_hand_and_archive(self):
        spec = next(s for s in algorithm_specs() if s.name == "SBCG-NSGA-III-no-M3")
        sentinel = {"selection": {"status": "HOLD"}, "episodes": 0}
        with patch("sbcg_experiment.run_sbcg_evolution", return_value=sentinel) as mocked:
            run_algorithm_arm(
                spec, make_shared_initial_pool(3, size=4), [SCENARIO], VERDICTS,
                eval_budget=4, seed=3, pop_size=2, generations=0,
            )
        kwargs = mocked.call_args.kwargs
        self.assertFalse(kwargs["use_elite_archive"])
        self.assertTrue(kwargs["remove_hand_from_pool"])

    def test_fixed_baseline_has_explicit_episode_and_unique_evaluation_counts(self):
        spec = next(s for s in algorithm_specs() if s.name == "Hand FSM")
        with patch("sbcg_experiment.evaluate_sbcg_candidate") as mocked:
            mocked.return_value = type("Record", (), {
                "source_split": "validation", "fingerprint": "fixed",
                "objectives": (0.5, 0.0, 0.2, 0.0, 0.0),
                "constraints": {"duplicate": 0.0, "sla_violation": 0.0, "invariant_violation": 0.0},
                "family_coverage": 1, "worst_family_condrec": 0.5,
                "per_family_condrec": {"f1": 0.5},
                "metrics": {"cond_rec": 0.5}, "feasible": True, "fsm": hand_fsm(),
            })()
            result = run_algorithm_arm(
                spec, make_shared_initial_pool(3, size=4), [SCENARIO], VERDICTS,
                eval_budget=1, seed=3, pop_size=2, generations=0,
                validation_scenarios=[VALIDATION_SCENARIO],
            )
        self.assertEqual(result["episodes"], 0)
        self.assertEqual(result["unique_evaluations"], 0)
        self.assertEqual(result["cache_hits"], 0)
        self.assertEqual(result["validation_calls"], 1)
        self.assertEqual(result["information_scope"], "validation_only_no_test")

    def test_test_sentinel_is_rejected_before_fixed_evaluation(self):
        spec = next(s for s in algorithm_specs() if s.name == "Hand FSM")
        with patch("sbcg_experiment.evaluate_controller", side_effect=AssertionError("must not run")):
            with self.assertRaisesRegex(ValueError, "test split"):
                run_algorithm_arm(
                    spec, make_shared_initial_pool(3, size=4),
                    [{"scenario_id": "sentinel", "split": "test"}], {},
                    eval_budget=1, seed=3, pop_size=2, generations=0,
                )

    def test_legacy_evolution_reports_unique_and_cache_counts(self):
        with patch("ea.evaluate_controller", side_effect=fake_metrics):
            result = run_evolution(
                "nsga2", [hand_fsm()], [SCENARIO], VERDICTS,
                pop_size=1, generations=1, eval_budget=4, seed=7,
            )
        self.assertIn("unique_evaluations", result)
        self.assertIn("cache_hits", result)
        self.assertEqual(result["unique_evaluations"] + result["cache_hits"], result["evaluation_calls"])


if __name__ == "__main__":
    unittest.main()
