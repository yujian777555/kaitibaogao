import unittest

from pilot_a3 import (
    POLICIES,
    TASKS,
    TRAIN_TASKS,
    VALIDATION_TASKS,
    HELDOUT_TASKS,
    TRAIN_COMPOSITIONS,
    VALIDATION_COMPOSITIONS,
    HELDOUT_COMPOSITIONS,
    ToolRuntime,
    PublicToolView,
    build_scenarios,
    make_fault_vector,
    run_episode,
)


def custom_scenario(task, faults, name="custom"):
    return {
        "scenario_id": "custom|{}|{}".format(task, name),
        "split": "heldout_joint_shift",
        "task": task,
        "composition": name,
        "seed": 7,
        "tools": TASKS[task],
        "faults": faults,
    }


def fault(fault_name="none", delay=0, retry_after=0, comp=True):
    return {
        "fault": fault_name,
        "delay": delay,
        "retry_after": retry_after,
        "compensation_available": comp,
    }


class PilotA3Tests(unittest.TestCase):
    def test_factorized_task_and_composition_splits_are_disjoint(self):
        self.assertTrue(set(TRAIN_TASKS).isdisjoint(VALIDATION_TASKS))
        self.assertTrue(set(TRAIN_TASKS).isdisjoint(HELDOUT_TASKS))
        self.assertTrue(set(VALIDATION_TASKS).isdisjoint(HELDOUT_TASKS))
        self.assertTrue(set(TRAIN_COMPOSITIONS).isdisjoint(VALIDATION_COMPOSITIONS))
        self.assertTrue(set(TRAIN_COMPOSITIONS).isdisjoint(HELDOUT_COMPOSITIONS))
        self.assertTrue(set(VALIDATION_COMPOSITIONS).isdisjoint(HELDOUT_COMPOSITIONS))

    def test_frozen_episode_budget(self):
        scenarios = build_scenarios()
        self.assertEqual(len(scenarios), 954)
        self.assertEqual(sum(s["split"] == "train" for s in scenarios), 144)
        self.assertEqual(sum(s["split"].startswith("validation") for s in scenarios), 120)
        self.assertEqual(sum(s["split"].startswith("heldout_") for s in scenarios), 690)

    def test_faults_are_assigned_per_tool_not_broadcast(self):
        vector = make_fault_vector("inventory_order_payment", "delay_rate_permission", 17)
        self.assertEqual(
            [item["fault"] for item in vector],
            ["delayed_visibility", "rate_limit", "permission_denied"],
        )

    def test_timeout_latent_subtypes_share_public_signature(self):
        before = ToolRuntime("inventory", fault("timeout_before")).execute()
        after = ToolRuntime("inventory", fault("timeout_after", delay=3)).execute()
        delayed = ToolRuntime("inventory", fault("delayed_visibility", delay=2)).execute()
        self.assertEqual({before, after, delayed}, {"TIMEOUT"})

    def test_policy_view_hides_latent_simulator_labels(self):
        runtime = ToolRuntime("inventory", fault("timeout_after", delay=3, comp=False))
        view = PublicToolView(runtime)
        self.assertFalse(hasattr(view, "fault"))
        self.assertFalse(hasattr(view, "compensation_available"))
        self.assertFalse(hasattr(view, "visible_at"))
        self.assertEqual(view.contract["idempotent"], False)

    def test_non_idempotent_retry_after_commit_is_duplicate(self):
        tool = ToolRuntime("inventory", fault("timeout_after", delay=4))
        self.assertEqual(tool.execute(), "TIMEOUT")
        self.assertEqual(tool.retry(), "DUPLICATE")
        self.assertEqual(tool.violation_count, 1)

    def test_idempotent_replay_does_not_duplicate(self):
        tool = ToolRuntime("calendar", fault("timeout_after", delay=4))
        self.assertEqual(tool.execute(), "TIMEOUT")
        self.assertEqual(tool.retry(), "IDEMPOTENT_REPLAY")
        self.assertEqual(tool.violation_count, 0)

    def test_contract_aware_waits_for_visibility_sla(self):
        scenario = custom_scenario(
            "inventory_order_payment",
            [fault("timeout_after", delay=4), fault(), fault()],
            "delayed_commit",
        )
        safe = run_episode("contract_aware", scenario)
        unsafe = run_episode("verify_then_retry", scenario)
        self.assertEqual(safe["task_success"], 1)
        self.assertEqual(safe["invariant_violation"], 0)
        self.assertEqual(unsafe["invariant_violation"], 1)

    def test_saga_rolls_back_previous_steps_in_reverse_order(self):
        scenario = custom_scenario(
            "inventory_order_payment",
            [fault(), fault(), fault("permission_denied")],
            "late_permission",
        )
        row = run_episode("saga_aware", scenario)
        self.assertEqual(row["rollback_order"], "order>inventory")
        self.assertEqual(row["active_effects"], 0)
        self.assertEqual(row["safe_resolution"], 1)

    def test_downstream_steps_are_not_called_after_first_step_failure(self):
        scenario = custom_scenario(
            "inventory_order_payment",
            [fault("permission_denied"), fault(), fault()],
            "early_permission",
        )
        row = run_episode("saga_aware", scenario)
        self.assertEqual(row["tool_action_counts"].split("|")[1:], ["0", "0"])
        self.assertEqual(row["invariant_violation"], 0)

    def test_failed_compensation_remains_unresolved_and_escalates(self):
        scenario = custom_scenario(
            "inventory_order_payment",
            [fault("partial_commit", comp=False), fault(), fault()],
            "compensation_failure",
        )
        row = run_episode("saga_aware", scenario)
        self.assertEqual(row["compensation_failure"], 1)
        self.assertEqual(row["unresolved"], 1)
        self.assertEqual(row["steps_attempted"], 1)
        self.assertEqual(row["invariant_violation"], 0)

    def test_every_policy_uses_identical_scenario_ids(self):
        scenario = build_scenarios()[0]
        rows = [run_episode(policy, scenario) for policy in POLICIES]
        self.assertEqual({row["scenario_id"] for row in rows}, {scenario["scenario_id"]})
        self.assertEqual({row["seed"] for row in rows}, {scenario["seed"]})

    def test_fault_generation_is_reproducible(self):
        first = make_fault_vector("subscription_ledger_notification", "triple_mixed", 99)
        second = make_fault_vector("subscription_ledger_notification", "triple_mixed", 99)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
