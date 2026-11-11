"""Synthetic tests for Prefix-aware compensation-before-escalation control."""
import json
import random
import unittest
from pathlib import Path

from a3_bridge import (
    ACT_COMPENSATE,
    ACT_ESCALATE,
    ACT_ROLLBACK,
    ACT_STOP,
    OBS_COMPENSATED,
    OBS_COMP_FAILED,
    OBS_PERMISSION,
    hand_fsm,
)
from prefix_recovery import PrefixAwareFSM, prefix_hand_fsm, prefix_random_fsm
from ea import crossover, mutate


def permission_scenario():
    return {
        "scenario_id": "synthetic-prefix-permission",
        "split": "train",
        "tools": ["inventory", "order", "payment"],
        "faults": [
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
            {"fault": "permission_denied", "delay": 0, "retry_after": 0, "compensation_available": True},
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
        ],
    }


def d6_scenario():
    return {
        "scenario_id": "synthetic-prefix-d6",
        "split": "train",
        "tools": ["inventory", "order", "payment"],
        "faults": [
            {"fault": "partial_commit", "delay": 0, "retry_after": 0, "compensation_available": False},
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
        ],
    }


def two_committed_scenario():
    return {
        "scenario_id": "synthetic-prefix-two-committed",
        "split": "train",
        "tools": ["inventory", "order", "payment"],
        "faults": [
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
            {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
            {"fault": "permission_denied", "delay": 0, "retry_after": 0, "compensation_available": True},
        ],
    }


def evaluate(fsm, scenario, label, minimum_harm=0):
    from a3_bridge import evaluate_controller
    verdict = {
        scenario["scenario_id"]: {
            "class": label,
            "min_reachable_harm": minimum_harm,
            "unavoidable_residual": minimum_harm,
        }
    }
    return evaluate_controller(fsm, [scenario], verdict)["rows"][0]


class PrefixStateTests(unittest.TestCase):
    def test_prefix_contains_only_public_commit_and_compensation_state(self):
        scenario = permission_scenario()
        fsm = prefix_hand_fsm()
        row = evaluate(fsm, scenario, "R3")
        self.assertEqual(row["class_success"], 1)
        trace = row["decision_trace"]
        self.assertEqual(trace[0][3], ACT_ROLLBACK)
        self.assertEqual(trace[-1][3], ACT_ESCALATE)
        state = fsm.last_controller_state
        self.assertEqual(state.prefix[0]["state"], "COMPENSATED")
        self.assertTrue(state.prefix[0]["compensatable"])
        self.assertTrue(state.prefix[0]["compensated"])
        self.assertFalse(state.prefix[0]["compensation_failed"])
        self.assertNotIn("fault", state.prefix[0])
        self.assertNotIn("delay", state.prefix[0])
        self.assertNotIn("retry_after", state.prefix[0])

    def test_controller_state_accepts_restricted_public_tool_views(self):
        from a3_bridge import ControllerState
        from pilot_a3 import PublicToolView, ToolRuntime
        runtime = ToolRuntime("inventory", {
            "fault": "timeout_after", "delay": 4, "retry_after": 0,
            "compensation_available": True,
        })
        runtime._commit()
        state = ControllerState(1, [PublicToolView(runtime)])
        self.assertEqual(state.prefix[0]["state"], "NOT_COMMITTED")
        self.assertFalse(state.prefix[0]["confirmed"])
        self.assertFalse(state.prefix[0]["compensated"])
        self.assertFalse(state.prefix[0]["compensation_failed"])

    def test_prefix_rollback_order_is_a_genome_parameter(self):
        fsm = prefix_hand_fsm()
        fsm.prefix_reverse = False
        row = evaluate(fsm, two_committed_scenario(), "R3")
        self.assertEqual(row["class_success"], 1)
        rollback = [entry[0] for entry in row["comp_log"]]
        self.assertEqual(rollback, [0, 1])
        self.assertEqual(row["tool_action_count"], 5)

    def test_successful_current_compensation_returns_to_base_recovery(self):
        scenario = d6_scenario()
        scenario["faults"][0]["compensation_available"] = True
        row = evaluate(prefix_hand_fsm(), scenario, "R2")
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["task_success"], 1)
        self.assertEqual(row["active_effects"], 3)
        self.assertEqual(row["avoidable_harm"], 0)
        self.assertEqual(row["invariant_violation"], 0)

    def test_successful_current_compensation_with_prefix_redoes_current_step(self):
        scenario = two_committed_scenario()
        scenario["faults"][1] = {
            "fault": "partial_commit", "delay": 0, "retry_after": 0,
            "compensation_available": True,
        }
        scenario["faults"][2] = {
            "fault": "none", "delay": 0, "retry_after": 0,
            "compensation_available": True,
        }
        row = evaluate(prefix_hand_fsm(), scenario, "R2")
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["task_success"], 1)
        self.assertEqual(row["avoidable_harm"], 0)
        self.assertEqual(row["invariant_violation"], 0)
        self.assertEqual([entry[3] for entry in row["decision_trace"][:2]],
                         [ACT_COMPENSATE, "RETRY"])

    def test_failed_compensation_does_not_pretend_success(self):
        fsm = prefix_hand_fsm()
        row = evaluate(fsm, d6_scenario(), "R4", minimum_harm=1)
        self.assertEqual(row["label"], "R4")
        self.assertEqual(row["avoidable_harm"], 0)
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["active_effects"], 1)
        self.assertEqual(fsm.last_controller_state.prefix[0]["state"], "PARTIAL")
        self.assertTrue(fsm.last_controller_state.prefix[0]["compensation_failed"])
        self.assertFalse(fsm.last_controller_state.prefix[0]["compensated"])

    def test_failed_prefix_rollback_preserves_failure_observation(self):
        scenario = permission_scenario()
        scenario["faults"][0]["compensation_available"] = False
        row = evaluate(prefix_hand_fsm(), scenario, "R4", minimum_harm=1)
        self.assertEqual(row["decision_trace"][0][3], ACT_ROLLBACK)
        self.assertEqual(row["decision_trace"][-1][0], OBS_COMP_FAILED)
        self.assertEqual(row["decision_trace"][-1][3], ACT_ESCALATE)
        self.assertEqual(row["active_effects"], 1)
        self.assertEqual(row["class_success"], 1)

    def test_current_compensation_failure_cleans_compensatable_prefix(self):
        scenario = two_committed_scenario()
        scenario["faults"][1] = {
            "fault": "partial_commit", "delay": 0, "retry_after": 0,
            "compensation_available": False,
        }
        row = evaluate(prefix_hand_fsm(), scenario, "R4", minimum_harm=1)
        actions = [entry[3] for entry in row["decision_trace"]]
        self.assertEqual(actions, [ACT_COMPENSATE, ACT_ROLLBACK, ACT_ESCALATE])
        self.assertEqual(row["active_effects"], 1)
        self.assertEqual(row["avoidable_harm"], 0)
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["comp_log"], [
            (1, "current", "FAILED"), (0, "rollback1", "COMPENSATED"),
        ])

    def test_verify_and_stop_action_are_genome_parameters(self):
        fsm = prefix_hand_fsm()
        fsm.prefix_verify = True
        fsm.prefix_stop_action = ACT_STOP
        row = evaluate(fsm, permission_scenario(), "R3")
        actions = [entry[3] for entry in row["decision_trace"]]
        self.assertIn("VERIFY_PREFIX", actions)
        self.assertEqual(actions[-1], ACT_STOP)

    def test_failed_retry_is_bounded_by_decision_budget(self):
        fsm = prefix_hand_fsm()
        fsm.prefix_retry_failed = True
        row = evaluate(fsm, d6_scenario(), "R4", minimum_harm=1)
        self.assertEqual(row["decision_count"], 24)
        self.assertEqual(row["runtime_forced_abort"], 1)
        self.assertEqual(row["class_success"], 0)

    def test_clone_and_variation_preserve_prefix_genome(self):
        rng = random.Random(17)
        original = prefix_random_fsm(rng)
        clone = original.clone()
        self.assertIsInstance(clone, PrefixAwareFSM)
        for name in ("prefix_reverse", "prefix_verify", "prefix_retry_failed", "prefix_stop_action"):
            self.assertEqual(getattr(clone, name), getattr(original, name))
        variants = [mutate(original, random.Random(i)) for i in range(8)]
        self.assertTrue(all(isinstance(item, PrefixAwareFSM) for item in variants))
        child = crossover(original, clone, random.Random(5))
        self.assertIsInstance(child, PrefixAwareFSM)
        self.assertIn(child.prefix_stop_action, (ACT_ESCALATE, ACT_STOP))

    def test_mixed_controller_representations_cannot_cross_over(self):
        with self.assertRaises(ValueError):
            crossover(hand_fsm(), prefix_hand_fsm(), random.Random(5))

    def test_repair_preserves_only_guarded_permission_rollback(self):
        from a3_bridge import repair_fsm
        fsm = prefix_hand_fsm()
        for gene in fsm.genes_list():
            if gene.error == OBS_PERMISSION:
                gene.action = ACT_ROLLBACK
        repaired = repair_fsm(fsm)
        self.assertIsInstance(repaired, PrefixAwareFSM)
        for gene in repaired.genes_list():
            if gene.error == OBS_PERMISSION:
                expected = ACT_ROLLBACK if gene.stack else ACT_ESCALATE
                self.assertEqual(gene.action, expected)

    def test_d5_all_diagnostic_scenarios_are_reachable_with_prefix_order(self):
        manifest = json.loads(Path(
            "experiments/pilot_a3b/results/d079_challenge_v2/d079_challenge_manifest.json"
        ).read_text(encoding="utf-8"))
        rows = [row for row in manifest["scenarios"]
                if row["difficulty_stratum"] == "D5_PERMISSION_AFTER_COMMITTED_PREFIX"
                and row["evaluation_role"] == "diagnostic"]
        self.assertEqual(len(rows), 24)
        from a3_bridge import evaluate_controller, evaluator_verdict_from_scenario
        verdicts = {row["scenario_id"]: evaluator_verdict_from_scenario(row) for row in rows}
        self.assertTrue(all(verdict["class"] == "R3" for verdict in verdicts.values()))
        result = evaluate_controller(prefix_hand_fsm(), rows, verdicts)
        self.assertTrue(all(row["class_success"] == 1 for row in result["rows"]))
        self.assertTrue(all(row["active_effects"] == 0 for row in result["rows"]))

    def test_prefix_verification_receipt_is_auditable(self):
        fsm = prefix_hand_fsm()
        fsm.prefix_verify = True
        row = evaluate(fsm, permission_scenario(), "R3")
        self.assertEqual(row["prefix_verification_log"], [(0, "COMPENSATED")])

    def test_shared_pool_preserves_base_genomes_across_prefix_representation(self):
        from sbcg import make_shared_initial_pool
        plain = make_shared_initial_pool(11, size=8, include_hand=False)
        prefixed = make_shared_initial_pool(
            11, size=8, include_hand=False, prefix_aware=True
        )
        for base, extended in zip(plain, prefixed):
            self.assertEqual(
                [(key, gene.action, gene.wait_n) for key, gene in sorted(base.genes.items())],
                [(key, gene.action, gene.wait_n) for key, gene in sorted(extended.genes.items())],
            )
            self.assertEqual(
                (base.default_action, base.default_wait, base.sla_aware, base.fixed_wait),
                (extended.default_action, extended.default_wait,
                 extended.sla_aware, extended.fixed_wait),
            )


if __name__ == "__main__":
    unittest.main()
