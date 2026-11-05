import unittest
import ast
from pathlib import Path

from pilot_a2 import (
    Env, TOOLS, PROFILES, POLICIES, make_episode, run_policy
)

class PilotA2Tests(unittest.TestCase):
    def test_observation_excludes_hidden_simulator_fields(self):
        env = Env(make_episode("order", "timeout_after", 7))
        obs = env.observe()
        forbidden = {
            "hidden_outcome", "effects", "visibility_delay",
            "compensation_available", "fault_profile", "seed",
        }
        self.assertTrue(forbidden.isdisjoint(obs))
        self.assertEqual(obs["contract"]["idempotency"], "keyed")
        self.assertIn("retry_after", obs)

    def test_timeout_before_and_after_share_initial_public_observation(self):
        before = Env(make_episode("calendar", "timeout_before", 13)).observe()
        after = Env(make_episode("calendar", "timeout_after", 13)).observe()
        self.assertEqual(before, after)

    def test_eventual_consistency_visibility_bound(self):
        spec = make_episode("order", "delayed_commit_timeout", 4)
        env = Env(spec)
        self.assertEqual(env.act("VERIFY"), "NOT_FOUND")
        env.act("WAIT", spec["contract"]["max_visibility_delay"])
        self.assertEqual(env.act("VERIFY"), "COMMITTED")

    def test_strong_consistency_is_immediately_visible(self):
        env = Env(make_episode("inventory", "timeout_after", 4))
        self.assertEqual(env.act("VERIFY"), "COMMITTED")

    def test_native_and_keyed_idempotency_prevent_duplicate(self):
        native = Env(make_episode("inventory", "timeout_after", 2))
        self.assertEqual(native.act("RETRY"), "ALREADY_COMMITTED")
        self.assertEqual(native.effects, 1)
        keyed = Env(make_episode("order", "timeout_after", 2))
        self.assertEqual(keyed.act("RETRY_WITH_KEY"), "ALREADY_COMMITTED")
        self.assertEqual(keyed.effects, 1)

    def test_non_idempotent_retry_can_duplicate(self):
        env = Env(make_episode("calendar", "timeout_after", 2))
        self.assertEqual(env.act("RETRY"), "DUPLICATE")
        self.assertTrue(env.violation)

    def test_compensation_contract_and_runtime_availability(self):
        available = Env(make_episode("order", "partial_commit", 2))
        self.assertEqual(available.act("COMPENSATE"), "COMPENSATED")
        unavailable = Env(make_episode("order", "partial_compensation_unavailable", 2))
        self.assertEqual(unavailable.act("COMPENSATE"), "COMPENSATION_UNAVAILABLE")

    def test_rate_limit_retry_after_is_public(self):
        env = Env(make_episode("inventory", "timeout_rate_before", 9))
        obs = env.observe()
        self.assertEqual(obs["retry_after"], env.spec["retry_after"])
        self.assertEqual(env.act("RETRY"), "RATE_LIMITED")
        env.act("WAIT", obs["retry_after"])
        self.assertEqual(env.act("RETRY"), "COMMITTED")

    def test_permission_failure_is_escalated_without_retry(self):
        result = run_policy(make_episode("calendar", "permission_timeout_before", 3),
                            "contract_optimized")
        self.assertEqual(result["escalated"], 1)
        self.assertEqual(result["invariant_violation"], 0)

    def test_contract_optimized_has_no_critical_violations_in_pilot_matrix(self):
        rows = [
            run_policy(make_episode(tool, profile, seed), "contract_optimized")
            for tool in TOOLS for profile in PROFILES for seed in range(100)
        ]
        self.assertEqual(len(rows), len(TOOLS) * len(PROFILES) * 100)
        self.assertEqual(sum(r["invariant_violation"] for r in rows), 0)
        self.assertEqual(sum(r["duplicate_side_effect"] for r in rows), 0)


    def test_only_oracle_branch_can_read_hidden_state(self):
        source_path = Path(__file__).with_name("pilot_a2.py")
        source = source_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        run_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_policy")
        oracle_marker = 'elif policy == "oracle_upper_bound":'
        oracle_line = source[:source.index(oracle_marker)].count("\\n") + 1
        hidden_keys = {"hidden_outcome", "effects", "visibility_delay", "compensation_available"}
        for node in ast.walk(run_fn):
            if isinstance(node, ast.Attribute) and node.attr in hidden_keys:
                self.assertGreaterEqual(node.lineno, oracle_line)
            if isinstance(node, ast.Subscript):
                sl = node.slice
                if isinstance(sl, ast.Constant) and sl.value in hidden_keys:
                    self.assertGreaterEqual(node.lineno, oracle_line)

    def test_all_policies_cover_complete_matrix(self):
        rows = [
            run_policy(make_episode(tool, profile, seed), policy)
            for policy in POLICIES for tool in TOOLS
            for profile in PROFILES for seed in range(100)
        ]
        self.assertEqual(len(rows), len(POLICIES) * len(TOOLS) * len(PROFILES) * 100)

if __name__ == "__main__":
    unittest.main()
