"""Synthetic-only tests for R4 fail-closed pre-flight."""
import tempfile
import unittest
from pathlib import Path

from formal_preflight import run_formal_preflight, run_postrun_integrity_check, write_preflight_report


def good_context():
    return {
        "r4_preregistration_sha256": "a" * 64,
        "implementation_sha256": "b" * 64,
        "git_head": "c" * 40,
        "independent_review_status": "ACCEPTED",
        "advisor_mde_status": "APPROVED",
        "user_approved": True,
        "ci_conclusion": "success",
        "tests_passed": True,
        "manifest_hashes": {
            "train_family_sha256": "1" * 64,
            "train_scenario_sha256": "2" * 64,
            "validation_family_sha256": "3" * 64,
            "validation_scenario_sha256": "4" * 64,
            "test_family_sha256": "5" * 64,
            "test_scenario_sha256": "6" * 64,
        },
        "split_overlap_count": 0,
        "train_runner_split": "train",
        "validation_use": "selection_only",
        "test_payload_exposed": False,
        "test_payload_disclosed": False,
        "test_family_count": 40,
        "test_scenario_count": 1080,
        "expected_roster_valid": True,
        "analysis_schema_valid": True,
        "budget_within_cap": True,
        "seed_recorded": True,
        "stopping_rule_frozen": True,
        "test_access_log_count": 0,
        "one_time_ledger_state": "UNUSED",
    }


class FormalPreflightTests(unittest.TestCase):
    def test_all_conditions_required_for_go(self):
        result = run_formal_preflight(good_context())
        self.assertEqual(result["status"], "GO")
        self.assertEqual(result["blocking_reasons"], [])

    def test_pending_advisor_mde_forces_hold(self):
        context = good_context()
        context["advisor_mde_status"] = "PENDING"
        result = run_formal_preflight(context)
        self.assertEqual(result["status"], "HOLD")
        self.assertTrue(any("advisor" in x.lower() for x in result["blocking_reasons"]))

    def test_missing_user_approval_forces_hold(self):
        context = good_context()
        context["user_approved"] = False
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_r3_request_changes_forces_hold(self):
        context = good_context()
        context["independent_review_status"] = "REQUEST CHANGES"
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_ci_failure_forces_hold(self):
        context = good_context()
        context["ci_conclusion"] = "failure"
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_test_payload_exposure_forces_hold(self):
        context = good_context()
        context["test_payload_exposed"] = True
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_split_overlap_forces_hold(self):
        context = good_context()
        context["split_overlap_count"] = 1
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_pre_run_gate_does_not_require_post_run_outcome_rows(self):
        context = good_context()
        result = run_formal_preflight(context)
        self.assertEqual(result["status"], "GO")
        self.assertEqual(result["phase"], "PRE_RUN_AUTHORIZATION")
        self.assertNotIn("n_observed_families", result["checked_fields"])

    def test_test_access_or_consumed_ledger_forces_pre_run_hold(self):
        context = good_context()
        context["test_access_log_count"] = 1
        context["one_time_ledger_state"] = "CONSUMED"
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_post_run_gate_checks_outcomes_only_after_one_time_consumption(self):
        context = {
            "paired_rows_valid": True, "duplicate_count": 0,
            "labelled_null_count": 0, "metadata_mismatch_count": 0,
            "n_observed_families": 34,
            "family_composition_counts": {f"F{i:02d}": 5 for i in range(34)},
            "family_loss": [], "technical_missing_runs": 0,
            "design_deviation": False, "test_access_log_count": 1,
            "one_time_ledger_state": "CONSUMED",
        }
        result = run_postrun_integrity_check(context)
        self.assertEqual(result["phase"], "POST_RUN_ANALYSIS_INTEGRITY")
        self.assertEqual(result["status"], "GO")
        self.assertTrue(result["analysis_eligible"])

    def test_post_run_gate_rejects_incomplete_family(self):
        context = {
            "paired_rows_valid": True, "duplicate_count": 0,
            "labelled_null_count": 0, "metadata_mismatch_count": 0,
            "n_observed_families": 33,
            "family_composition_counts": {f"F{i:02d}": 5 for i in range(33)},
            "family_loss": ["F33"], "technical_missing_runs": 1,
            "design_deviation": True, "test_access_log_count": 1,
            "one_time_ledger_state": "CONSUMED",
        }
        self.assertEqual(run_postrun_integrity_check(context)["status"], "HOLD")

    def test_invalid_hash_or_missing_required_field_fails_closed(self):
        context = good_context()
        context["implementation_sha256"] = "not-a-sha"
        result = run_formal_preflight(context)
        self.assertEqual(result["status"], "HOLD")
        del context["user_approved"]
        self.assertEqual(run_formal_preflight(context)["status"], "HOLD")

    def test_machine_and_human_reports_are_written(self):
        result = run_formal_preflight(good_context())
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "preflight.json"
            md_path = Path(tmp) / "preflight.md"
            write_preflight_report(result, json_path, md_path)
            self.assertTrue(json_path.exists())
            self.assertTrue(md_path.exists())
            self.assertIn("GO", md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
