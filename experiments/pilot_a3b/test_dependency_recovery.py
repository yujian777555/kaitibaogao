"""State-transition and information-boundary tests for the D-086 model."""
import unittest

from dependency_recovery import (
    classify_scenario,
    public_view,
    run_episode,
)


def route(name="primary", outcomes=(True,), cost=1, hint="HIGH", requires=(),
          receipt="immediate", delay=0, idempotent=True):
    return {
        "name": name,
        "outcomes": list(outcomes),
        "cost": cost,
        "reliability_hint": hint,
        "requires": list(requires),
        "receipt": receipt,
        "receipt_delay": delay,
        "idempotent": idempotent,
        "visibility_bound": 3,
    }


def tool(name, state="COMMITTED", available=True, routes=None):
    return {
        "id": name,
        "state": state,
        "compensation_available": available,
        "routes": [route()] if routes is None else routes,
    }


def scenario(tools, terminal="permission", current="C", scenario_id="synthetic-d086"):
    return {
        "scenario_id": scenario_id,
        "split": "train",
        "seed": 17,
        "terminal_fault": terminal,
        "current_tool": current,
        "tools": tools,
    }


def script(actions):
    iterator = __import__("builtins").iter(actions)
    return lambda _view: next(iterator)


def abort_with(a_routes, b_routes=None):
    return scenario([
        tool("A", routes=a_routes),
        tool("B", routes=[route()] if b_routes is None else b_routes),
        tool("C", state="NOT_COMMITTED"),
    ])


class DependencyTransitionTests(unittest.TestCase):
    def test_dependency_blocks_then_allows_compensation(self):
        sc = abort_with([route(requires=["B"])])
        actions = [
            ("COMPENSATE", "A", "primary"),
            ("COMPENSATE", "B", "primary"),
            ("COMPENSATE", "A", "primary"),
            ("ESCALATE",),
        ]
        row = run_episode(script(actions), sc)
        observations = [entry["observation"] for entry in row["trace"]]
        self.assertEqual(observations, [
            "DEPENDENCY_BLOCKED", "COMPENSATED", "COMPENSATED", "ESCALATED",
        ])
        self.assertEqual(row["label"], "R3")
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["residual_side_effects"], 0)
        self.assertEqual(row["correct_escalation"], 1)

    def test_permanent_and_dependent_minimum_harm(self):
        sc = abort_with([route(requires=["B"])], [route()])
        sc["tools"][1]["compensation_available"] = False
        self.assertEqual(classify_scenario(sc), ("R4", 2))
        row = run_episode(script([
            ("COMPENSATE", "B", "primary"),
            ("COMPENSATE", "A", "primary"),
            ("ESCALATE",),
        ]), sc)
        self.assertEqual(row["residual_side_effects"], 2)
        self.assertEqual(row["min_reachable_harm"], 2)
        self.assertEqual(row["avoidable_harm"], 0)
        self.assertEqual(row["class_success"], 1)

    def test_alternate_route_can_succeed_after_primary_failure(self):
        sc = abort_with([
            route(outcomes=[False, True], cost=3),
            route("alternate", outcomes=[True], cost=1, hint="LOW"),
        ])
        row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("COMPENSATE", "A", "alternate"),
            ("COMPENSATE", "B", "primary"),
            ("ESCALATE",),
        ]), sc)
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["action_cost"], 5)
        self.assertEqual(row["min_reachable_harm"], 0)

    def test_pending_success_blind_retry_is_duplicate_but_verify_is_safe(self):
        unsafe = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        unsafe_row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("COMPENSATE", "A", "primary"),
            ("VERIFY", "A"),
            ("COMPENSATE", "B", "primary"),
            ("ESCALATE",),
        ]), unsafe)
        self.assertEqual(unsafe_row["duplicate_compensation"], 1)
        self.assertEqual(unsafe_row["constraint_violation"], 1)

        safe = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        safe_row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("WAIT",),
            ("VERIFY", "A"),
            ("COMPENSATE", "B", "primary"),
            ("ESCALATE",),
        ]), safe)
        self.assertEqual(safe_row["duplicate_compensation"], 0)
        self.assertEqual(safe_row["pending_compensation"], 0)
        self.assertEqual(safe_row["class_success"], 1)

    def test_pending_failure_needs_resolution_before_new_attempt(self):
        sc = abort_with([
            route(outcomes=[False, True], receipt="delayed", delay=1, idempotent=False),
        ])
        row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("VERIFY", "A"),
            ("WAIT",),
            ("VERIFY", "A"),
            ("COMPENSATE", "A", "primary"),
            ("WAIT",),
            ("VERIFY", "A"),
            ("COMPENSATE", "B", "primary"),
            ("ESCALATE",),
        ]), sc)
        self.assertEqual(row["duplicate_compensation"], 0)
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["action_cost"], 8)

    def test_pending_at_stop_is_not_correct_escalation(self):
        sc = abort_with([route(outcomes=[True], receipt="delayed", delay=2)])
        row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("COMPENSATE", "B", "primary"),
            ("ESCALATE",),
        ]), sc)
        self.assertEqual(row["residual_side_effects"], 0)
        self.assertEqual(row["pending_compensation"], 1)
        self.assertEqual(row["constraint_violation"], 1)
        self.assertEqual(row["correct_escalation"], 0)

    def test_stop_safe_is_not_misreported_as_escalation(self):
        row = run_episode(script([
            ("COMPENSATE", "A", "primary"),
            ("COMPENSATE", "B", "primary"),
            ("STOP_SAFE",),
        ]), abort_with([route()]))
        self.assertEqual(row["safe_stop"], 1)
        self.assertEqual(row["policy_selected_escalation"], 0)
        self.assertEqual(row["correct_escalation"], 0)
        self.assertEqual(row["constraint_violation"], 0)

    def test_timeout_before_and_partial_recoverable_controls(self):
        r1 = scenario([
            tool("A"), tool("B"), tool("C", state="NOT_COMMITTED"),
        ], terminal="timeout_before")
        r1_row = run_episode(script([("RETRY_WORKFLOW",)]), r1)
        self.assertEqual(r1_row["label"], "R1")
        self.assertEqual(r1_row["task_success"], 1)
        self.assertEqual(r1_row["conditional_recovery_success"], 1)
        self.assertEqual(r1_row["residual_side_effects"], 0)

        r2 = scenario([
            tool("A"), tool("B"), tool("C", state="PARTIAL"),
        ], terminal="partial_recover")
        r2_row = run_episode(script([
            ("COMPENSATE", "C", "primary"), ("RETRY_WORKFLOW",),
        ]), r2)
        self.assertEqual(r2_row["label"], "R2")
        self.assertEqual(r2_row["task_success"], 1)
        self.assertEqual(r2_row["conditional_recovery_success"], 1)
        self.assertEqual(r2_row["residual_side_effects"], 0)

    def test_permission_retry_does_not_complete_workflow(self):
        row = run_episode(script([
            ("RETRY_WORKFLOW",), ("STOP_SAFE",),
        ]), abort_with([route()]))
        self.assertEqual(row["trace"][0]["observation"], "PERMISSION")
        self.assertEqual(row["task_success"], 0)

    def test_decision_budget_is_fail_closed(self):
        row = run_episode(lambda _view: ("WAIT",), abort_with([route()]))
        self.assertEqual(row["decision_count"], 24)
        self.assertEqual(row["runtime_forced_abort"], 1)
        self.assertEqual(row["class_success"], 0)


class PublicInformationTests(unittest.TestCase):
    def test_public_view_excludes_latent_outcomes_and_labels(self):
        sc = abort_with([
            route(outcomes=[False, True], receipt="delayed", delay=2),
        ])
        view = public_view(sc)
        self.assertNotIn("scenario_id", view)
        self.assertNotIn("seed", view)
        self.assertNotIn("label", view)
        self.assertNotIn("min_reachable_harm", view)
        route_view = view["tools"]["A"]["routes"][0]
        self.assertNotIn("outcomes", route_view)
        self.assertNotIn("receipt_delay", route_view)
        self.assertNotIn("pending_success", route_view)
        self.assertNotIn("receipt", route_view)
        self.assertEqual(route_view["reliability_hint"], "HIGH")
        self.assertEqual(route_view["visibility_bound"], 3)

    def test_attempt_observations_do_not_expand_information_permissions(self):
        from dependency_recovery import DependencyRecoveryEnv
        sc = abort_with([route(outcomes=[True], receipt="delayed", delay=2)])
        env = DependencyRecoveryEnv(sc)
        self.assertEqual(env.step(("COMPENSATE", "A", "primary")), "TIMEOUT")
        view = env.view()
        route_view = view["tools"]["A"]["routes"][0]
        self.assertNotIn("pending_success", view["tools"]["A"])
        self.assertNotIn("outcomes", route_view)
        self.assertNotIn("resolve_at", route_view)
        self.assertTrue(route_view["pending"])


if __name__ == "__main__":
    unittest.main()
