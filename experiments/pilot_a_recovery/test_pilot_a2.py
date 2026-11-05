import unittest
from pilot_a2 import Tool, TOOLS, TASKS, FAULTS, POLICIES, episode

class PilotA2Tests(unittest.TestCase):
    def test_timeout_subtypes_share_public_observation(self):
        obs = [Tool("order", f, 2).observe()["error"]
               for f in ("timeout_before", "timeout_after", "stale_read", "compound_timeout_stale")]
        self.assertEqual(set(obs), {"TIMEOUT"})

    def test_non_idempotent_replay_is_blocked_by_contract_policy(self):
        row = episode("contract_aware", "reserve_inventory_then_order", "timeout_after", 1)
        self.assertEqual(row["invariant_violation"], 0)

    def test_idempotent_calendar_replay_is_safe(self):
        tool = Tool("calendar", "timeout_after", 0)
        self.assertEqual(tool.act("RETRY"), "IDEMPOTENT_REPLAY")
        self.assertFalse(tool.violation)

    def test_noncompensatable_partial_state_is_not_retried(self):
        row = episode("contract_aware", "reserve_inventory_then_ledger", "partial_commit", 0)
        self.assertEqual(row["invariant_violation"], 0)

    def test_compound_fault_suite_coverage(self):
        self.assertIn("compound_timeout_stale", FAULTS)
        self.assertIn("compound_partial_rate", FAULTS)
        self.assertEqual(len(TASKS), 4)
        self.assertEqual(len(POLICIES), 6)

    def test_episode_outputs_are_bounded(self):
        for p in POLICIES:
            row=episode(p,TASKS[0],FAULTS[0],3)
            for key in ("task_success","safe","duplicate","invariant_violation","unresolved","escalated"):
                self.assertIn(row[key], (0,1))

if __name__ == "__main__":
    unittest.main()
