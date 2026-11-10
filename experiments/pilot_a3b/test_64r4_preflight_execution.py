"""Synthetic-output tests for executing the current R4 pre-flight."""
import json
import tempfile
import unittest
from pathlib import Path

from run_r4_preflight import run_current_preflight


class CurrentPreflightExecutionTests(unittest.TestCase):
    def test_current_unapproved_preflight_writes_hold_without_test_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, json_path, markdown_path = run_current_preflight(
                tmp,
                git_head="c" * 40,
                ci_conclusion="success",
                tests_passed=True,
            )
            self.assertEqual(result["status"], "HOLD")
            self.assertTrue(any("independent review" in x for x in result["blocking_reasons"]))
            self.assertTrue(any("advisor" in x for x in result["blocking_reasons"]))
            self.assertTrue(any("user" in x for x in result["blocking_reasons"]))
            self.assertEqual(result["test_lock"]["access_log_count"], 0)
            self.assertEqual(result["test_lock"]["one_time_ledger_state"], "UNUSED")
            saved_text = Path(json_path).read_text(encoding="utf-8")
            saved = json.loads(saved_text)
            self.assertEqual(saved["status"], "HOLD")
            self.assertNotIn("test_scenarios", saved_text)
            self.assertNotIn("test_families", saved_text)
            self.assertIn("HOLD", Path(markdown_path).read_text(encoding="utf-8"))

    def test_failed_ci_cannot_produce_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _, _ = run_current_preflight(
                tmp,
                git_head="c" * 40,
                ci_conclusion="failure",
                tests_passed=False,
                approvals={
                    "independent_review_status": "ACCEPTED",
                    "advisor_mde_status": "APPROVED",
                    "user_approved": True,
                },
            )
            self.assertEqual(result["status"], "HOLD")
            self.assertTrue(any("tests/CI" in x for x in result["blocking_reasons"]))


if __name__ == "__main__":
    unittest.main()
