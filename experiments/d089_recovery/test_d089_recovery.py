"""D-089 regression tests — unittest compatible, no LLM/API."""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))
sys.path.insert(0, str(HERE.parent / "d088_recovery"))

from d089_budget import public_min_harm, reachable_routes, estimate_remaining_decisions  # noqa: E402
from d089_genome import (  # noqa: E402
    D089Genome, random_genome, mutate, mutate_feedback, crossover_segments,
    pareto_front, select_by_preference,
)
from d089_policies import D089BudgetPolicy  # noqa: E402
from d089_scenarios import build_manifest, validate_manifest  # noqa: E402
from d088_experiment import evaluate_rows, summarize_rows  # noqa: E402


class TestBudgetAnalytics(unittest.TestCase):
    def _view(self):
        return {
            "budget_remaining": 20, "decision_count": 4,
            "tools": {
                "A": {"state": "COMMITTED", "compensation_available": True,
                      "routes": [{"name": "primary", "requires": ["B"], "pending": False,
                                  "attempts": 0, "cost": 3},
                                 {"name": "alternate", "requires": [], "pending": False,
                                  "attempts": 0, "cost": 1}]},
                "B": {"state": "COMMITTED", "compensation_available": False,
                      "routes": [{"name": "primary", "requires": [], "pending": False,
                                  "attempts": 0, "cost": 3}]},
            },
        }

    def test_public_min_harm_counts_uncompensable(self):
        # B has no contract -> unavoidable; A is compensable via alternate
        self.assertEqual(public_min_harm(self._view()), 1)

    def test_reachable_routes_include_alternate(self):
        routes = reachable_routes(self._view(), allow_alternate=True)
        names = {(t, r["name"]) for t, r in routes}
        self.assertIn(("A", "alternate"), names)

    def test_estimate_is_positive_and_finite(self):
        est = estimate_remaining_decisions(self._view())
        self.assertTrue(4 <= est <= 30, est)


class TestGenome(unittest.TestCase):
    def test_mutation_keeps_arm_flags(self):
        rng = random.Random(3)
        g = random_genome(rng, "BC")
        for _ in range(30):
            g = mutate(g, rng)
            self.assertTrue(g.enable_b and g.enable_c and not g.enable_a)

    def test_feedback_and_segment_crossover(self):
        rng = random.Random(5)
        a = random_genome(rng, "ABC")
        b = random_genome(rng, "ABC")
        c = mutate_feedback(a, rng, {"early_stop": 2.0, "route_failures": 1.0})
        self.assertIsInstance(c, D089Genome)
        d = crossover_segments(a, b, rng)
        self.assertIsInstance(d, D089Genome)

    def test_pareto_and_preference_selection(self):
        cands = [
            ({"constraint_violation": 0, "pending_compensation": 0, "r3_success": 0.9,
              "r4_success": 0.5, "avoid_harm": 0.1, "recovery_cost": 8.0}, "g1", []),
            ({"constraint_violation": 0, "pending_compensation": 0, "r3_success": 0.5,
              "r4_success": 0.9, "avoid_harm": 0.1, "recovery_cost": 8.0}, "g2", []),
            ({"constraint_violation": 0, "pending_compensation": 0, "r3_success": 0.4,
              "r4_success": 0.4, "avoid_harm": 0.4, "recovery_cost": 20.0}, "g3", []),
        ]
        front = pareto_front(cands)
        self.assertEqual(len(front), 2)  # g3 dominated
        self.assertEqual(select_by_preference(front, "R3_priority")[1], "g1")
        self.assertEqual(select_by_preference(front, "R4_priority")[1], "g2")


class TestScenarios(unittest.TestCase):
    def test_manifests(self):
        dev = build_manifest("development")
        fresh = build_manifest("fresh")
        self.assertTrue(validate_manifest(dev)["ok"])
        self.assertTrue(validate_manifest(fresh)["ok"])
        self.assertEqual(dev["scenario_count"], 96)
        self.assertEqual(fresh["scenario_count"], 64)
        dev_ids = {s["scenario_id"] for s in dev["scenarios"]}
        fresh_ids = {s["scenario_id"] for s in fresh["scenarios"]}
        self.assertFalse(dev_ids & fresh_ids)


class TestPolicySafety(unittest.TestCase):
    def test_zero_violations_small(self):
        scenarios = build_manifest("development")["scenarios"][:24]
        for seed in (7, 99):
            g = random_genome(random.Random(seed), "ABC")
            rows = evaluate_rows(lambda: D089BudgetPolicy(g), scenarios)
            s = summarize_rows(rows)
            self.assertEqual(s["constraint_violation"], 0)
            self.assertEqual(s["pending_compensation"], 0)
            self.assertEqual(s["duplicate_compensation"], 0)


if __name__ == "__main__":
    unittest.main()
