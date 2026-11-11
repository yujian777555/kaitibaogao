"""Small synthetic tests for the D-086 evolutionary search implementation."""
import unittest

from dependency_evolution import (
    choose_validation_metrics,
    run_search,
    select_validation,
)
from dependency_genome import RecoveryGenome
from dependency_recovery import run_episode
from test_dependency_recovery import abort_with, route


def small_train():
    first = abort_with([route()])
    first["scenario_id"] = "synthetic-ea-a"
    second = abort_with([route(outcomes=[True], receipt="delayed", delay=1, idempotent=False)])
    second["scenario_id"] = "synthetic-ea-b"
    for scenario in (first, second):
        scenario.update({
            "task_family_id": "synthetic-family",
            "difficulty_stratum": "D3_DEPENDENT_ABORT",
            "composition": "synthetic",
            "repeat": 0,
        })
    return [first, second]


class EvolutionTests(unittest.TestCase):
    def test_default_genome_objectives_and_public_view(self):
        from dependency_evolution import evaluate_genome, EvaluationLedger
        ledger = EvaluationLedger(manifest_sha="synthetic", episode_cap=10)
        record = evaluate_genome(RecoveryGenome(), small_train(), ledger, role="train")
        self.assertEqual(record["metrics"]["r3_success"], 1.0)
        self.assertEqual(record["metrics"]["constraint_count"], 0)
        self.assertEqual(record["objectives"][0], 0.0)
        self.assertEqual(ledger.stats["unique_episode_equivalent"]["train"], 2)

    def test_search_is_deterministic_and_respects_budget(self):
        first = run_search("NSGA-III", 711, small_train(), population_size=4,
                           generations=1, episode_cap=16)
        second = run_search("NSGA-III", 711, small_train(), population_size=4,
                            generations=1, episode_cap=16)
        self.assertEqual(first["initial_pool"], second["initial_pool"])
        self.assertEqual(first["history"], second["history"])
        self.assertEqual(len(first["final_population"]), 4)
        self.assertLessEqual(first["ledger"].stats["unique_episode_equivalent"]["train"], 16)
        self.assertEqual(first["ledger"].stats["unique_episode_equivalent"]["train"], 16)
        limited = run_search("NSGA-II", 711, small_train(), population_size=4,
                             generations=1, episode_cap=4)
        self.assertLessEqual(limited["ledger"].stats["unique_episode_equivalent"]["train"], 4)
        self.assertTrue(limited["budget_exhausted"])

    def test_all_search_methods_share_initial_pool(self):
        pools = []
        for method in ("RandomSearch", "NSGA-II", "NSGA-III", "C-NSGA-III"):
            result = run_search(method, 711, small_train(), population_size=4,
                                generations=1, episode_cap=16)
            pools.append(result["initial_pool"])
        self.assertTrue(all(pool == pools[0] for pool in pools))

    def test_constraint_choice_does_not_use_scalar_objective_sum(self):
        safe = RecoveryGenome(hint_weight=0)
        unsafe = RecoveryGenome(hint_weight=1)
        records = [
            {
                "genome": unsafe,
                "objectives": (0, 0, 0, 0, 0),
                "metrics": {
                    "r3_success": 1, "r4_success": 1, "avoid_harm": 0,
                    "condrec": 1, "r3_cost": 0, "constraint_count": 1,
                },
            },
            {
                "genome": safe,
                "objectives": (1, 1, 1, 1, 1),
                "metrics": {
                    "r3_success": 0, "r4_success": 0, "avoid_harm": 1,
                    "condrec": 0, "r3_cost": 1, "constraint_count": 0,
                },
            },
        ]
        selected = choose_validation_metrics(records)
        self.assertEqual(selected["status"], "SELECTED")
        self.assertIs(selected["genome"], safe)

    def test_no_pending_verification_returns_hold(self):
        scenario = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        scenario["scenario_id"] = "synthetic-ea-pending"
        scenario.update({
            "task_family_id": "synthetic-family",
            "difficulty_stratum": "D3_DEPENDENT_ABORT",
            "composition": "synthetic",
            "repeat": 0,
        })
        result = run_search("C-NSGA-III", 711, [scenario], population_size=1,
                            generations=0, episode_cap=4,
                            ablation="NoPendingVerification")
        validation = dict(scenario)
        validation["split"] = "validation"
        selected = select_validation(result, [validation])
        self.assertEqual(selected["status"], "HOLD")

    def test_test_split_is_rejected(self):
        scenario = abort_with([route()])
        scenario["split"] = "test"
        with self.assertRaises(ValueError):
            run_search("NSGA-II", 711, [scenario], episode_cap=10)


if __name__ == "__main__":
    unittest.main()
