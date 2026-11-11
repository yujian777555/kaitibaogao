"""Fixed-policy discrimination tests for D-086; no optimizer runs."""
import unittest

from dependency_policies import make_policy
from dependency_recovery import run_episode
from test_dependency_recovery import abort_with, route, scenario, tool


class FixedPolicyTests(unittest.TestCase):
    def test_forward_dependency_requires_order_adaptation(self):
        sc = abort_with([route()])
        sc["tools"][1]["routes"][0]["requires"] = ["A"]
        fixed = run_episode(make_policy("FixedPrefix"), sc)
        rule = run_episode(make_policy("RuleBased"), sc)
        self.assertEqual(fixed["class_success"], 0)
        self.assertGreater(fixed["avoidable_harm"], 0)
        self.assertEqual(rule["class_success"], 1)
        self.assertEqual(rule["constraint_violation"], 0)

    def test_failure_feedback_can_beat_hint_greedy_without_hidden_information(self):
        sc = abort_with([
            route(outcomes=[False, False, True], cost=3, hint="HIGH"),
            route("alternate", outcomes=[True], cost=1, hint="LOW"),
        ])
        greedy = run_episode(make_policy("Greedy"), sc)
        adaptive = run_episode(make_policy("AdaptiveProbe"), sc)
        self.assertEqual(greedy["class_success"], 1)
        self.assertEqual(adaptive["class_success"], 1)
        self.assertGreater(greedy["action_cost"], adaptive["action_cost"])
        self.assertEqual(greedy["action_cost"], 10)
        self.assertEqual(adaptive["action_cost"], 5)
        cost_aware = run_episode(make_policy("CostAware"), sc)
        self.assertEqual(cost_aware["class_success"], 1)
        self.assertEqual(cost_aware["action_cost"], 2)

    def test_safe_pending_handling_prevents_duplicate_compensation(self):
        sc = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        for name in ("FixedPrefix", "RuleBased", "Greedy", "AdaptiveProbe"):
            with self.subTest(name=name):
                row = run_episode(make_policy(name), sc)
                self.assertEqual(row["duplicate_compensation"], 0)
                self.assertEqual(row["pending_compensation"], 0)
                self.assertEqual(row["class_success"], 1)

    def test_recoverable_controls_and_escalation_accounting(self):
        r1 = scenario([
            tool("A"), tool("B"), tool("C", state="NOT_COMMITTED"),
        ], terminal="timeout_before")
        r2 = scenario([
            tool("A"), tool("B"), tool("C", state="PARTIAL"),
        ], terminal="partial_recover")
        for name in ("FixedPrefix", "RuleBased", "Greedy", "AdaptiveProbe"):
            with self.subTest(name=name):
                self.assertEqual(run_episode(make_policy(name), r1)["class_success"], 1)
                self.assertEqual(run_episode(make_policy(name), r2)["class_success"], 1)
        stop = run_episode(make_policy("Hand"), abort_with([route()]))
        self.assertEqual(stop["policy_selected_escalation"], 1)
        self.assertEqual(stop["correct_escalation"], 0)

    def test_random_policy_is_reproducible_and_uses_public_actions(self):
        first = run_episode(make_policy("Random", seed=19), abort_with([route()]))
        second = run_episode(make_policy("Random", seed=19), abort_with([route()]))
        self.assertEqual(first, second)
        self.assertLessEqual(first["decision_count"], 24)


if __name__ == "__main__":
    unittest.main()
