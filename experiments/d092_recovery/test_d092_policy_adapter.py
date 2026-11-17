"""Real D090Policy adapter checks on synthetic public views only."""
from __future__ import annotations

import unittest

from d092_genome import TypedGenome, probe_typed_genomes
from d090_policies import D090Policy
from d092_runtime import run_guarded_episode


def route(name, requires, cost, hint, attempts=0, last_receipt=None):
    return {
        "name": name,
        "requires": list(requires),
        "cost": cost,
        "reliability_hint": hint,
        "pending": False,
        "attempts": attempts,
        "last_receipt": last_receipt,
        "idempotent": False,
    }


def priority_view(budget):
    tools = {
        "A": {"state": "COMMITTED", "compensation_available": True, "routes": [route("primary", ["B"], 3, "HIGH"), route("alternate", [], 1, "LOW")]},
        "B": {"state": "COMMITTED", "compensation_available": True, "routes": [route("primary", ["C"], 3, "HIGH", attempts=1, last_receipt="FAILED"), route("alternate", [], 1, "LOW")]},
        "C": {"state": "COMPENSATED", "compensation_available": True, "routes": [route("primary", [], 3, "HIGH"), route("alternate", [], 1, "LOW")]},
        "D": {"state": "NOT_COMMITTED", "compensation_available": True, "routes": []},
    }
    return {"tools": tools, "current_tool": "D", "terminal_fault": "permission", "decision_count": 24 - budget, "budget_remaining": budget}


class TestPolicyPriorityAdapter(unittest.TestCase):
    def test_p06_p07_diverge_at_budget_ten(self):
        probes = probe_typed_genomes()
        view = priority_view(10)
        available = [("B", view["tools"]["B"]["routes"][0]), ("B", view["tools"]["B"]["routes"][1])]
        ordinary = D090Policy(probes["P06"].to_d090())._priority(view, available)
        tight = D090Policy(probes["P07"].to_d090())._priority(view, available)
        self.assertEqual(ordinary[1:], ("B", "primary"))
        self.assertEqual(tight[1:], ("B", "alternate"))

    def test_p07_threshold_twelve_and_none_never_compare_none(self):
        probes = probe_typed_genomes()
        view = priority_view(13)
        available = [("B", view["tools"]["B"]["routes"][0]), ("B", view["tools"]["B"]["routes"][1])]
        self.assertEqual(D090Policy(probes["P07"].to_d090())._priority(view, available)[2], "primary")
        view = priority_view(12)
        available = [("B", view["tools"]["B"]["routes"][0]), ("B", view["tools"]["B"]["routes"][1])]
        self.assertEqual(D090Policy(probes["P07"].to_d090())._priority(view, available)[2], "alternate")
        self.assertEqual(D090Policy(probes["P05"].to_d090())._priority(view, available)[2], "primary")

    def test_p03_fallback_contrast_uses_real_policy(self):
        probes = probe_typed_genomes()
        requirements = {"A": ["C"], "B": ["C"], "C": ["A"]}
        tools = {}
        for tool in ("A", "B", "C"):
            tools[tool] = {
                "state": "COMMITTED",
                "compensation_available": True,
                "routes": [route("primary", requirements[tool], 3, "HIGH"), route("alternate", [], 1, "LOW")],
            }
        tools["D"] = {"state": "NOT_COMMITTED", "compensation_available": True, "routes": []}
        view = {"tools": tools, "current_tool": "D", "terminal_fault": "permission", "budget_remaining": 24}
        enabled = D090Policy(probes["P01"].to_d090())._available_or_fallback(view)
        disabled = D090Policy(probes["P03"].to_d090())._available_or_fallback(view)
        self.assertEqual({(tool, item["name"]) for tool, item in enabled}, {("A", "alternate"), ("B", "alternate"), ("C", "alternate")})
        self.assertEqual(disabled, [])

    def test_typed_policy_runs_on_synthetic_environment(self):
        scenario = {
            "scenario_id": "synthetic|adapter",
            "split": "train",
            "terminal_fault": "permission",
            "current_tool": "D",
            "tools": [
                {"id": "A", "state": "COMMITTED", "compensation_available": True, "routes": [{"name": "primary", "outcomes": [True], "cost": 1, "reliability_hint": "HIGH", "requires": [], "receipt": "immediate", "receipt_delay": 0, "idempotent": True, "visibility_bound": 3}]},
                {"id": "D", "state": "NOT_COMMITTED", "compensation_available": True, "routes": []},
            ],
        }
        report = run_guarded_episode(D090Policy(TypedGenome().to_d090()), scenario)
        self.assertEqual(report["class_success"], 1)
        self.assertEqual(report["constraint_episode"], 0)
        self.assertEqual(report["illegal_state_transition_count"], 0)
        self.assertEqual(report["attempt_records"][0]["closing_receipt"], "COMPENSATED")


if __name__ == "__main__":
    unittest.main()
