"""Tests for the stateful controller and the fixed evaluator (57 F1-F4)."""
import unittest

from a3_bridge import (
    ACT_COMPENSATE, ACT_ESCALATE, ACT_ROLLBACK, ACT_STOP,
    evaluate_controller, hand_fsm, random_fsm, run_episode_fsm, scenario_verdict,
    score_episode,
)
from pilot_a3 import TASKS, make_fault_vector


def sc(task, comp, seed=7):
    return {
        "scenario_id": f"t|{task}|{comp}|{seed}",
        "split": "train", "task": task, "composition": comp,
        "seed": seed, "tools": TASKS[task],
        "faults": make_fault_vector(task, comp, seed),
    }


class StatefulControllerTests(unittest.TestCase):
    def test_no_implicit_saga_rollback(self):
        """57 F1: a genome whose genes never select COMPENSATE/ROLLBACK must
        never trigger compensation, even if prior steps committed."""
        fsm = hand_fsm()
        # force every gene to ESCALATE: no compensation actions at all
        for g in fsm.genes_list():
            g.action = ACT_ESCALATE
        s = sc("inventory_order_payment", "partial_then_delay", 5)
        row = run_episode_fsm(fsm, s)
        self.assertEqual(row["compensation_attempts"], 0,
                         "unused genes must not cause rollback")
        self.assertEqual(row["policy_selected_escalation"], 1)

    def test_explicit_rollback_records_log(self):
        fsm = hand_fsm()
        s = sc("inventory_order_payment", "partial_comp_failure", 9)
        row = run_episode_fsm(fsm, s)
        # any compensation that happened must be logged with target+result
        for entry in row["comp_log"]:
            self.assertEqual(len(entry), 3)  # (target, order, result)

    def test_policy_escalation_vs_runtime_abort(self):
        """57 F2: ESCALATE sets policy_selected_escalation; budget overrun
        sets runtime_forced_abort; they are never conflated."""
        fsm = hand_fsm()
        for g in fsm.genes_list():
            g.action = ACT_ESCALATE
        row = run_episode_fsm(fsm, sc("inventory_order_payment", "single_timeout", 3))
        self.assertEqual(row["policy_selected_escalation"], 1)
        self.assertEqual(row["runtime_forced_abort"], 0)

        # a looping policy exhausts the decision budget -> runtime abort
        fsm2 = hand_fsm()
        for g in fsm2.genes_list():
            g.action = "WAIT"
        row2 = run_episode_fsm(fsm2, sc("inventory_order_payment", "single_timeout", 3))
        self.assertEqual(row2["runtime_forced_abort"], 1)
        self.assertEqual(row2["policy_selected_escalation"], 0)

    def test_decision_trace_records_genes(self):
        fsm = hand_fsm()
        row = run_episode_fsm(fsm, sc("calendar_order_ledger", "timeout_then_rate_limit", 11))
        self.assertGreater(len(row["decision_trace"]), 0)
        obs, att, stack, action = row["decision_trace"][0]
        self.assertIn(att, (0, 1, 2))
        self.assertIsInstance(stack, bool)


class EvaluatorTests(unittest.TestCase):
    def test_r4_requires_containment_not_mere_escalation(self):
        """57 F3: ESCALATE alone is not DamageContainment when avoidable harm
        remains (duplicates or avoidable residual)."""
        verdict = {"class": "R4", "unavoidable_residual": 1, "min_reachable_harm": 1}
        row_bad = {"task_success": 0, "active_effects": 3, "duplicate_count": 2,
                   "duplicate": 1, "policy_selected_escalation": 1}
        s_bad = score_episode(verdict, row_bad)
        self.assertEqual(s_bad["class_success"], 0)
        self.assertEqual(s_bad["avoidable_harm"], 2 + 3 - 1)
        row_ok = {"task_success": 0, "active_effects": 1, "duplicate_count": 0,
                  "duplicate": 0, "policy_selected_escalation": 1}
        s_ok = score_episode(verdict, row_ok)
        self.assertEqual(s_ok["class_success"], 1)
        self.assertEqual(s_ok["avoidable_harm"], 0)

    def test_r3_counts_only_explicit_escalation(self):
        verdict = {"class": "R3", "unavoidable_residual": 0, "min_reachable_harm": 0}
        forced = {"task_success": 0, "active_effects": 0, "duplicate_count": 0,
                  "duplicate": 0, "policy_selected_escalation": 0}
        self.assertEqual(score_episode(verdict, forced)["class_success"], 0)
        explicit = dict(forced, policy_selected_escalation=1)
        self.assertEqual(score_episode(verdict, explicit)["class_success"], 1)

    def test_r2_safe_abort_is_not_success(self):
        verdict = {"class": "R2", "unavoidable_residual": 0, "min_reachable_harm": 0}
        abort = {"task_success": 0, "active_effects": 0, "duplicate_count": 0,
                 "duplicate": 0, "policy_selected_escalation": 1}
        self.assertEqual(score_episode(verdict, abort)["class_success"], 0)
        done = dict(abort, task_success=1, policy_selected_escalation=0)
        self.assertEqual(score_episode(verdict, done)["class_success"], 1)

    def test_necessary_escalation_not_in_r12_cost(self):
        """57 F4: objectives exclude R3/R4 action cost; unnec cost counts only
        R1/R2 rows."""
        fsm = hand_fsm()
        scenarios = [sc("inventory_order_payment", "partial_comp_failure", 1)]
        verdicts = {s["scenario_id"]: scenario_verdict(s) for s in scenarios}
        res = evaluate_controller(fsm, scenarios, verdicts)
        # R4-only set: unnec R1/R2 cost must be 0
        self.assertEqual(res["n_r1"] + res["n_r2"], 0)
        self.assertEqual(res["unnec_actions_r12"], 0.0)
        self.assertGreater(res["r34_action_cost_desc"], 0.0)

    def test_verdict_rules_smoke(self):
        v1 = scenario_verdict(sc("inventory_order_payment", "single_timeout", 2))
        self.assertIn(v1["class"], ("R1", "R2"))
        v2 = scenario_verdict(sc("inventory_order_payment", "partial_comp_failure", 2))
        self.assertEqual(v2["class"], "R4")
        v3 = scenario_verdict(sc("calendar_order_ledger", "delay_rate_permission", 2))
        self.assertIn(v3["class"], ("R3", "R4"))


if __name__ == "__main__":
    unittest.main()
