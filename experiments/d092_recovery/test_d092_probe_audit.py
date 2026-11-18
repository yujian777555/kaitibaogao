"""Independent raw-artifact audit tests for the executed D-092 Probe."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from d092_probe_audit import RESULTS, audit_episode_row, audit_probe


class TestD092ProbeAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lock = json.loads((RESULTS / "execution_lock.json").read_text(encoding="utf-8"))
        cls.train_ids = {
            row["scenario_id"]
            for row in json.loads(
                (RESULTS.parents[2] / "d090_recovery" / "results" / "d090_train_manifest.json").read_text(encoding="utf-8")
            )["scenarios"]
        }
        with (RESULTS / "episodes.jsonl").open(encoding="utf-8") as source:
            for line in source:
                candidate = json.loads(line)
                if candidate["report"]["attempt_records"]:
                    cls.first_row = candidate
                    break
        cls.audit = audit_probe(RESULTS)

    def test_real_960_probe_recomputes_to_hold(self):
        result = self.audit
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["probe_status"], "HOLD")
        self.assertEqual(result["episode_count"], 960)
        self.assertEqual(result["unique_episode_references"], 960)
        self.assertEqual(result["unique_compensation_attempt_ids"], 2032)
        self.assertEqual(result["cache_hits"], 0)
        self.assertEqual(result["summary_matches_raw"], True)
        self.assertEqual(result["criteria"]["P05"]["status"], "HOLD")
        self.assertEqual(result["criteria"]["P06"]["status"], "HOLD")
        self.assertEqual(result["criteria"]["P07"]["status"], "PASS")

    def test_q3_hold_is_supported_by_actual_priority_control_flow(self):
        diagnostic = self.audit["q3_harm_priority_diagnostic"]
        self.assertTrue(diagnostic["p00_p05_trace_equal"])
        self.assertTrue(diagnostic["p00_p06_trace_equal"])
        self.assertEqual(diagnostic["p00_p05_first_difference"], None)
        self.assertEqual(diagnostic["p00_p06_first_difference"], None)
        self.assertEqual(diagnostic["p05_eligible_steps"], [])
        self.assertEqual(diagnostic["p06_eligible_steps"], [])
        budget_three = next(row for row in diagnostic["states"] if row["budget_remaining"] == 3)
        self.assertEqual(budget_three["available"], [["A", "primary"], ["A", "alternate"]])
        self.assertEqual(budget_three["ordinary"], ["A", "primary"])
        self.assertEqual(budget_three["tight"], ["A", "alternate"])
        self.assertEqual(budget_three["actual_action"], ["VERIFY", "B"])

    def test_trace_tampering_is_rejected(self):
        row = copy.deepcopy(self.first_row)
        row["report"]["trace"][0]["observation"] = "FAILED"
        errors = audit_episode_row(row, self.lock, self.train_ids)
        self.assertIn("trace_transition_mismatch", errors)
        self.assertIn("trace_hash_mismatch", errors)

    def test_attempt_tampering_is_rejected(self):
        row = copy.deepcopy(self.first_row)
        row["report"]["attempt_records"][0]["closing_receipt"] = "COMPENSATED"
        errors = audit_episode_row(row, self.lock, self.train_ids)
        self.assertIn("attempt_lifecycle_mismatch", errors)


if __name__ == "__main__":
    unittest.main()
