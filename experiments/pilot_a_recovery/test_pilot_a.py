import unittest
from pilot_a import Env, FAULTS, POLICIES, run

class PilotATests(unittest.TestCase):
    def test_timeout_subtypes_share_public_signature(self):
        signatures = {
            Env(fault, 0).observe()["failure"]
            for fault in ("timeout_before_dispatch", "timeout_after_commit", "delayed_visibility")
        }
        self.assertEqual(signatures, {"TIMEOUT"})

    def test_unknown_outcome_retry_can_duplicate(self):
        env = Env("timeout_after_commit", 0)
        self.assertEqual(env.act("RETRY"), "DUPLICATE")
        self.assertTrue(env.violation)

    def test_partial_commit_requires_compensation_before_retry(self):
        env = Env("partial_commit", 0)
        self.assertEqual(env.act("COMPENSATE"), "COMPENSATED")
        self.assertEqual(env.act("RETRY"), "COMMITTED")
        self.assertFalse(env.violation)

    def test_delayed_visibility_is_stale_until_delay(self):
        env = Env("delayed_visibility", 2)
        self.assertEqual(env.act("VERIFY"), "NOT_DISPATCHED")
        for _ in range(3):
            env.act("WAIT")
        self.assertEqual(env.act("VERIFY"), "COMMITTED")

    def test_permission_failure_does_not_commit(self):
        env = Env("permission_denied", 0)
        self.assertEqual(env.act("RETRY"), "PERMISSION_DENIED")
        self.assertEqual(env.effects, 0)

    def test_all_policies_cover_all_faults(self):
        rows = [run(p, f, s) for p in POLICIES for f in FAULTS for s in range(10)]
        self.assertEqual(len(rows), len(POLICIES) * len(FAULTS) * 10)

if __name__ == "__main__":
    unittest.main()
