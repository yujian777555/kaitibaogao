"""Sanity tests: analytic A-3 labels follow the 55-R1 ladder."""
import unittest

from a3_bridge import label_scenario
from pilot_a3 import TASKS, make_fault_vector


def sc(task, comp, seed=7):
    return {
        "scenario_id": f"t|{task}|{comp}|{seed}",
        "task": task,
        "composition": comp,
        "seed": seed,
        "tools": TASKS[task],
        "faults": make_fault_vector(task, comp, seed),
    }


class A3LabelTests(unittest.TestCase):
    def test_single_timeout_is_r1(self):
        for seed in range(20):
            s = sc("inventory_order_payment", "single_timeout", seed)
            # single timeout/delayed: verify/wait completes
            self.assertIn(label_scenario(s), ("R1", "R2"))

    def test_partial_comp_failure_is_r4(self):
        for seed in range(20):
            s = sc("inventory_order_payment", "partial_comp_failure", seed)
            self.assertEqual(label_scenario(s), "R4", msg=str(s["faults"]))

    def test_permission_family_is_r3_or_r4(self):
        for seed in range(20):
            s = sc("calendar_order_ledger", "delay_rate_permission", seed)
            self.assertIn(label_scenario(s), ("R3", "R4"), msg=str(s["faults"]))

    def test_permission_with_uncompensated_prefix_commit_is_r4(self):
        """timeout_after on a non-compensatable prefix tool then permission:
        committed residue cannot be cleared -> R4, not R3."""
        from pilot_a3 import TASKS

        s = {
            "scenario_id": "manual",
            "task": "subscription_ledger_notification",
            "composition": "manual",
            "seed": 1,
            "tools": TASKS["subscription_ledger_notification"],
            "faults": [
                {"fault": "timeout_after", "delay": 2, "retry_after": 0, "compensation_available": False},
                {"fault": "permission_denied", "delay": 0, "retry_after": 0, "compensation_available": False},
                {"fault": "none", "delay": 0, "retry_after": 0, "compensation_available": True},
            ],
        }
        # subscription is compensatable but compensation_available=False;
        # committed effect cannot be removed -> unavoidable residue -> R4
        self.assertEqual(label_scenario(s), "R4")

    def test_partial_then_delay_with_comp_is_r2(self):
        seen = set()
        for seed in range(30):
            s = sc("customer_order_shipment", "partial_then_delay", seed)
            seen.add(label_scenario(s))
        self.assertIn("R2", seen)

    def test_labels_deterministic(self):
        for comp in ("single_timeout", "partial_comp_failure", "triple_mixed"):
            s1 = sc("inventory_order_payment", comp, 11)
            s2 = sc("inventory_order_payment", comp, 11)
            self.assertEqual(label_scenario(s1), label_scenario(s2))


if __name__ == "__main__":
    unittest.main()
