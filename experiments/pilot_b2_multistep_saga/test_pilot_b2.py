import ast
import unittest
from pathlib import Path

from experiments.pilot_b2_multistep_saga.pilot_b2 import (
    TASKS, PROFILES, POLICIES, Env, make_episode, run_policy,
    TEST_SEEDS
)

class PilotB2Tests(unittest.TestCase):
    def test_each_workflow_has_three_cross_tool_steps(self):
        self.assertEqual(set(TASKS), {
            "order_fulfillment", "appointment_confirmation", "return_refund"
        })
        for steps in TASKS.values():
            self.assertEqual(len(steps), 3)
            self.assertGreaterEqual(len({x["tool"] for x in steps}), 2)

    def test_observation_hides_current_effect_and_compensation_availability(self):
        env = Env(make_episode("order_fulfillment", 1, "timeout_after", 7))
        obs = env.observe()
        forbidden = {"current_outcome", "current_effects", "visibility_delay",
                     "current_comp_available", "previous_comp_failure_index",
                     "fault_profile", "seed"}
        self.assertTrue(forbidden.isdisjoint(obs))
        self.assertEqual(len(obs["completed_prefix"]), 1)

    def test_timeout_before_and_after_share_public_observation(self):
        before = Env(make_episode("appointment_confirmation", 2, "timeout_before", 11)).observe()
        after = Env(make_episode("appointment_confirmation", 2, "timeout_after", 11)).observe()
        self.assertEqual(before, after)

    def test_eventual_read_is_stale_until_contract_bound(self):
        spec = make_episode("appointment_confirmation", 0, "delayed_timeout_after", 5)
        env = Env(spec)
        self.assertEqual(env.act("VERIFY_CURRENT"), "NOT_FOUND")
        env.act("WAIT", spec["steps"][0]["max_visibility_delay"])
        self.assertEqual(env.act("VERIFY_CURRENT"), "COMMITTED")

    def test_idempotency_contract_prevents_duplicate(self):
        native = Env(make_episode("order_fulfillment", 0, "timeout_after", 3))
        self.assertEqual(native.act("RETRY_CURRENT"), "ALREADY_COMMITTED")
        keyed = Env(make_episode("order_fulfillment", 1, "timeout_after", 3))
        self.assertEqual(keyed.act("RETRY_CURRENT_WITH_KEY"), "ALREADY_COMMITTED")

    def test_non_idempotent_retry_after_commit_duplicates(self):
        env = Env(make_episode("appointment_confirmation", 0, "timeout_after", 3))
        self.assertEqual(env.act("RETRY_CURRENT"), "DUPLICATE")
        self.assertTrue(env.violation)

    def test_compensation_must_follow_reverse_dependency_order(self):
        env = Env(make_episode("order_fulfillment", 2, "partial_commit", 4))
        self.assertEqual(env.act("COMPENSATE_CURRENT"), "COMPENSATED")
        self.assertEqual(env.act("COMPENSATE_PREVIOUS", index=1), "COMPENSATED")
        self.assertEqual(env.act("COMPENSATE_PREVIOUS", index=0), "COMPENSATED")
        self.assertEqual(env.act("FINALIZE_ROLLBACK"), "ROLLBACK_COMPLETE")

    def test_out_of_order_compensation_is_rejected(self):
        env = Env(make_episode("order_fulfillment", 2, "partial_commit", 4))
        self.assertEqual(env.act("COMPENSATE_PREVIOUS", index=0), "COMPENSATION_ORDER_VIOLATION")
        self.assertTrue(env.violation)

    def test_contract_resume_never_duplicates_in_full_matrix(self):
        rows = [
            run_policy(make_episode(task, step, profile, seed), "contract_resume")
            for task in TASKS for step in range(3) for profile in PROFILES
            for seed in range(3000, 3010)
        ]
        self.assertEqual(sum(r["invariant_violation"] for r in rows), 0)

    def test_compensation_failures_escalate(self):
        current = run_policy(
            make_episode("appointment_confirmation", 1, "partial_compensation_unavailable", 8),
            "contract_resume"
        )
        previous = run_policy(
            make_episode("order_fulfillment", 2, "partial_previous_comp_failure", 8),
            "contract_resume"
        )
        self.assertEqual(current["escalated"], 1)
        self.assertEqual(previous["escalated"], 1)

    def test_non_oracle_policy_code_does_not_read_hidden_state(self):
        path = Path(__file__).with_name("pilot_b2.py")
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_policy")
        marker = 'elif policy=="oracle_upper_bound":'
        oracle_line = source[:source.index(marker)].count("\n") + 1
        hidden = {"current_outcome", "current_effects", "visibility_delay",
                  "current_comp_available", "previous_comp_failure_index"}
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute) and node.attr in hidden:
                self.assertGreaterEqual(node.lineno, oracle_line)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                if node.slice.value in hidden:
                    self.assertGreaterEqual(node.lineno, oracle_line)

    def test_seed_panels_are_new_and_disjoint(self):
        self.assertTrue(set(TEST_SEEDS).isdisjoint(range(1000, 1160)))
        self.assertEqual(TEST_SEEDS, tuple(range(3120, 3160)))

    def test_all_policies_cover_full_episode_matrix(self):
        rows = [
            run_policy(make_episode(task, step, profile, seed), policy)
            for policy in POLICIES for task in TASKS for step in range(3)
            for profile in PROFILES for seed in range(3000, 3002)
        ]
        self.assertEqual(len(rows), len(POLICIES) * len(TASKS) * 3 * len(PROFILES) * 2)

if __name__ == "__main__":
    unittest.main()
