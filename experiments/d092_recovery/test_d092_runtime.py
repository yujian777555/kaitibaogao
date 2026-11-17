"""D-092 guarded-runtime tests using synthetic scenarios only."""
from __future__ import annotations

import unittest

from d092_runtime import (
    AttemptLedger,
    public_action_allowed,
    run_guarded_episode,
    safe_action_snapshot,
    validate_action,
)


class SequencePolicy:
    def __init__(self, actions):
        self.actions = list(actions)

    def __call__(self, view):
        if self.actions:
            return self.actions.pop(0)
        return ("ESCALATE",)


def scenario(outcomes, delayed=False, state="COMMITTED", contract=True, requires=None):
    delay = 1 if delayed else 0
    tool = {
        "id": "C",
        "state": state,
        "compensation_available": contract,
        "routes": [{
            "name": "primary",
            "outcomes": list(outcomes),
            "cost": 1,
            "reliability_hint": "HIGH",
            "requires": list(requires or []),
            "receipt": "delayed" if delayed else "immediate",
            "receipt_delay": delay,
            "idempotent": not delayed,
            "visibility_bound": 3,
        }],
    }
    current = {"id": "D", "state": "NOT_COMMITTED", "compensation_available": True, "routes": []}
    return {
        "scenario_id": "synthetic|runtime",
        "split": "train",
        "terminal_fault": "permission",
        "current_tool": "D",
        "tools": [tool, current],
    }


class TestAttemptLifecycle(unittest.TestCase):
    def test_immediate_success_closes_without_failure(self):
        report = run_guarded_episode(SequencePolicy([("COMPENSATE", "C", "primary"), ("ESCALATE",)]), scenario([True]))
        self.assertEqual(report["attempt_records"][0]["closing_receipt"], "COMPENSATED")
        self.assertTrue(report["attempt_records"][0]["terminal_recorded"])
        self.assertEqual(report["failure_attempt_count"], 0)
        self.assertEqual(report["illegal_state_transition_count"], 0)

    def test_immediate_failure_and_blocked_receipts_are_unique(self):
        failed = run_guarded_episode(SequencePolicy([("COMPENSATE", "C", "primary"), ("ESCALATE",)]), scenario([False]))
        self.assertEqual(failed["failure_attempt_count"], 1)
        blocked = run_guarded_episode(SequencePolicy([("COMPENSATE", "C", "primary"), ("ESCALATE",)]), scenario([True], contract=False))
        self.assertEqual(blocked["contract_blocked_attempts"], 1)
        self.assertEqual(blocked["failure_attempt_count"], 1)
        self.assertEqual(blocked["illegal_state_transition_count"], 0)

    def test_delayed_success_and_repeated_verify_close_once(self):
        policy = SequencePolicy([
            ("COMPENSATE", "C", "primary"),
            ("WAIT",),
            ("VERIFY", "C"),
            ("VERIFY", "C"),
            ("ESCALATE",),
        ])
        report = run_guarded_episode(policy, scenario([True], delayed=True))
        self.assertEqual(len(report["attempt_records"]), 1)
        self.assertEqual(report["attempt_records"][0]["closing_receipt"], "COMPENSATED")
        self.assertEqual(report["attempt_records"][0]["terminal_tick"], 1)
        self.assertEqual(report["failure_attempt_count"], 0)
        self.assertEqual(report["pending_count"], 0)

    def test_delayed_failure_and_repeated_verify_do_not_double_count(self):
        policy = SequencePolicy([
            ("COMPENSATE", "C", "primary"),
            ("WAIT",),
            ("VERIFY", "C"),
            ("VERIFY", "C"),
            ("ESCALATE",),
        ])
        report = run_guarded_episode(policy, scenario([False], delayed=True))
        self.assertEqual(len(report["attempt_records"]), 1)
        self.assertEqual(report["attempt_records"][0]["closing_receipt"], "FAILED")
        self.assertEqual(report["failure_attempt_count"], 1)

    def test_nonprogress_pending_and_duplicate_dispatches_close_separately(self):
        policy = SequencePolicy([
            ("COMPENSATE", "C", "primary"),
            ("COMPENSATE", "C", "primary"),
            ("WAIT",),
            ("VERIFY", "C"),
            ("ESCALATE",),
        ])
        report = run_guarded_episode(policy, scenario([False], delayed=True))
        self.assertEqual(len(report["attempt_records"]), 2)
        self.assertEqual(report["attempt_records"][0]["closing_receipt"], "FAILED")
        self.assertEqual(report["attempt_records"][1]["closing_receipt"], "PENDING")
        self.assertTrue(all(record["terminal_recorded"] for record in report["attempt_records"]))
        self.assertEqual(report["failure_attempt_count"], 1)

    def test_duplicate_is_hard_but_not_route_failure(self):
        policy = SequencePolicy([
            ("COMPENSATE", "C", "primary"),
            ("COMPENSATE", "C", "primary"),
            ("ESCALATE",),
        ])
        report = run_guarded_episode(policy, scenario([True], delayed=True))
        self.assertEqual(report["duplicate_count"], 1)
        self.assertEqual(report["attempt_records"][-1]["closing_receipt"], "DUPLICATE_COMPENSATION")
        self.assertEqual(report["failure_attempt_count"], 0)

    def test_unresolved_timeout_is_marked_at_episode_end(self):
        report = run_guarded_episode(SequencePolicy([("COMPENSATE", "C", "primary"), ("ESCALATE",)]), scenario([False], delayed=True))
        self.assertTrue(report["attempt_records"][0]["unresolved_at_episode_end"])
        self.assertEqual(report["pending_count"], 1)

    def test_composite_attempt_identity_is_unique_per_episode(self):
        first = AttemptLedger("episode-a")
        second = AttemptLedger("episode-b")
        a = first.record_dispatch("C", "primary", "FAILED", 0)
        b = second.record_dispatch("C", "primary", "FAILED", 0)
        self.assertNotEqual(a["attempt_key"], b["attempt_key"])
        self.assertEqual(first.feedback_counts()["failure_attempt_count"], 1)


class TestGrammarMaskAndMonitor(unittest.TestCase):
    def test_unhashable_and_cyclic_actions_are_safe_invalid(self):
        cyclic = []
        cyclic.append(cyclic)
        for malformed in [("VERIFY", ["C"]), ("COMPENSATE", ["C"], "primary"), ("COMPENSATE", "C", ["primary"]), ("VERIFY", {"C": 1}), cyclic, ("UNKNOWN",)]:
            policy = SequencePolicy([malformed, ("ESCALATE",)])
            report = run_guarded_episode(policy, scenario([True]))
            self.assertEqual(report["invalid_action_count"], 1)
            self.assertEqual(report["illegal_state_transition_count"], 0)
            self.assertEqual(report["decision_count"], 2)
            self.assertIn("malformed_action_snapshot", report["adapter_events"][0])

    def test_unknown_ids_never_reach_environment_membership(self):
        report = run_guarded_episode(SequencePolicy([("VERIFY", "missing"), ("ESCALATE",)]), scenario([True]))
        self.assertEqual(report["invalid_action_count"], 1)
        self.assertEqual(report["adapter_events"][0]["observation"], "INVALID_ACTION")

    def test_unauthorized_partial_retry_is_not_dispatched(self):
        report = run_guarded_episode(SequencePolicy([("RETRY_WORKFLOW",), ("ESCALATE",)]), scenario([True], state="PARTIAL", requires=[]))
        # The synthetic fault remains permission; use a partial-recover variant for the mask check.
        report = run_guarded_episode(SequencePolicy([("RETRY_WORKFLOW",), ("ESCALATE",)]), dict(scenario([True], state="PARTIAL"), terminal_fault="partial_recover"))
        self.assertEqual(report["unauthorized_action_count"], 1)
        self.assertEqual(report["decision_count"], 1)

    def test_public_mask_allows_soft_blocked_and_pending_requests(self):
        view = {
            "terminal_fault": "permission",
            "current_tool": "D",
            "tools": {"C": {"state": "COMMITTED", "compensation_available": False, "routes": [{"name": "primary", "pending": False}]}},
        }
        self.assertTrue(public_action_allowed(("COMPENSATE", "C", "primary"), view))
        self.assertTrue(validate_action(("COMPENSATE", "C", "primary"), view))

    def test_snapshot_does_not_call_custom_repr_or_hash(self):
        class Hostile:
            def __repr__(self):
                raise AssertionError("repr called")
            def __hash__(self):
                raise AssertionError("hash called")
        snapshot = safe_action_snapshot(("VERIFY", Hostile()))
        self.assertIn("Hostile", snapshot)


if __name__ == "__main__":
    unittest.main()
