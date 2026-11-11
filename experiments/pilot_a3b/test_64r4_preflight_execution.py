"""Synthetic-output tests for executing the current R4 pre-flight."""
import json
import subprocess
import sys
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

    def test_actual_execution_config_and_access_log_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_config = Path(tmp) / "bad_config.json"
            bad_config.write_text(json.dumps({"stopping_rule": "early_stop_when_significant"}), encoding="utf-8")
            access_log = Path(tmp) / "test_access.json"
            access_log.write_text('{"event": "TEST_PAYLOAD_LOAD_ATTEMPT"}\n', encoding="utf-8")
            result, _, _ = run_current_preflight(
                tmp,
                git_head="c" * 40,
                ci_conclusion="success",
                tests_passed=True,
                config_path=bad_config,
                access_log_path=access_log,
            )
            self.assertEqual(result["status"], "HOLD")
            self.assertTrue(any("stopping_rule_frozen" in x for x in result["blocking_reasons"]))
            self.assertTrue(any("access log" in x for x in result["blocking_reasons"]))
            self.assertEqual(result["test_lock"]["access_log_count"], 1)

    def test_frozen_statistics_seed_values_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_config = Path(tmp) / "bad_seed_config.json"
            valid_config = json.loads(Path("experiments/pilot_a3b/r4_execution_config.json").read_text(encoding="utf-8"))
            valid_config["power_base_seed"] = 1
            bad_config.write_text(json.dumps(valid_config), encoding="utf-8")
            result, _, _ = run_current_preflight(
                tmp, git_head="c" * 40, ci_conclusion="success",
                tests_passed=True, config_path=bad_config,
            )
            self.assertEqual(result["status"], "HOLD")
            self.assertTrue(any("seed_recorded" in x for x in result["blocking_reasons"]))

    def test_cli_exposes_config_ledger_and_access_log_paths(self):
        script = Path(__file__).with_name("run_r4_preflight.py")
        completed = subprocess.run(
            [sys.executable, str(script), "--help"],
            check=True, capture_output=True, text=True,
        )
        for flag in ("--config-path", "--ledger-path", "--access-log-path"):
            self.assertIn(flag, completed.stdout)

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
