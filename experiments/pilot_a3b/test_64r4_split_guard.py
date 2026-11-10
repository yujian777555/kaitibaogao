"""R4 synthetic tests for split access and one-time final evaluation."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from a3_bridge import evaluate_controller, hand_fsm
from ea import run_evolution
from split_access import (
    consume_final_evaluation_once,
    execute_final_evaluation_once,
    public_manifest_view,
    scenarios_for_split,
)


def approval(manifest_sha="manifest-ok", code_sha="code-ok"):
    return {
        "status": "APPROVED",
        "preflight_status": "GO",
        "ci_conclusion": "success",
        "tests_passed": True,
        "independent_review_status": "ACCEPTED",
        "advisor_mde_approved": True,
        "user_approved": True,
        "manifest_sha256": manifest_sha,
        "code_sha256": code_sha,
    }


class SplitViewTests(unittest.TestCase):
    def test_public_manifest_view_strips_test_payload(self):
        manifest = {
            "schema_version": "synthetic-v1",
            "hashes": {"test_scenario_sha256": "test-hash"},
            "splits": {
                "train": {"summary": {"n_families": 1}, "scenarios": [{"split": "train"}]},
                "validation": {"summary": {"n_families": 1}, "scenarios": [{"split": "validation"}]},
                "test_locked": {
                    "summary": {"n_families": 1},
                    "family_sha256": "family-hash",
                    "scenario_sha256": "scenario-hash",
                    "payload_disclosed": False,
                    "scenarios": [{"scenario_id": "SECRET", "label": "R1"}],
                },
            },
        }
        view = public_manifest_view(manifest)
        self.assertNotIn("scenarios", view["splits"]["test_locked"])
        self.assertNotIn("families", view["splits"]["test_locked"])
        self.assertEqual(view["splits"]["test_locked"]["payload_disclosed"], False)
        self.assertEqual(len(view["splits"]["train"]["scenarios"]), 1)

    def test_scenarios_for_split_refuses_test(self):
        manifest = {
            "splits": {
                "train": {"scenarios": [{"split": "train"}]},
                "validation": {"scenarios": [{"split": "validation"}]},
                "test_locked": {"summary": {"n_families": 40}},
            }
        }
        with self.assertRaises(PermissionError):
            scenarios_for_split(manifest, "test")
        self.assertEqual(scenarios_for_split(manifest, "train")[0]["split"], "train")


class EvolutionSplitGuardTests(unittest.TestCase):
    def test_run_evolution_rejects_test_before_fitness(self):
        scenario = {"scenario_id": "sentinel", "split": "test"}
        with patch("ea.evaluate_controller", side_effect=AssertionError("fitness must not run")):
            with self.assertRaisesRegex(ValueError, "train split only"):
                run_evolution(
                    "nsga2", [hand_fsm()], [scenario], {},
                    pop_size=1, generations=0, eval_budget=10, seed=7,
                )

    def test_run_evolution_rejects_validation_as_fitness_input(self):
        scenario = {"scenario_id": "validation", "split": "validation"}
        with patch("ea.evaluate_controller", side_effect=AssertionError("fitness must not run")):
            with self.assertRaisesRegex(ValueError, "train split only"):
                run_evolution(
                    "nsga2", [hand_fsm()], [scenario], {},
                    pop_size=1, generations=0, eval_budget=10, seed=7,
                )

    def test_evaluate_controller_rejects_test_payload(self):
        scenario = {"scenario_id": "sentinel", "split": "test"}
        with self.assertRaisesRegex(ValueError, "test split is restricted"):
            evaluate_controller(hand_fsm(), [scenario], {})


class OneTimeFinalEvaluationTests(unittest.TestCase):
    def test_approved_final_evaluation_consumes_ledger_before_payload_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            calls = {"loader": 0, "evaluator": 0}

            def loader():
                calls["loader"] += 1
                self.assertTrue(ledger.exists(), "ledger must be consumed before payload read")
                return {"sentinel": "synthetic-test-only"}

            def evaluator(payload):
                calls["evaluator"] += 1
                return {"count": len(payload)}

            result = consume_final_evaluation_once(
                ledger, approval(), "manifest-ok", "manifest-ok", "code-ok", "code-ok", loader, evaluator
            )
            self.assertEqual(result, {"count": 1})
            self.assertEqual(calls, {"loader": 1, "evaluator": 1})
            with self.assertRaisesRegex(RuntimeError, "already consumed"):
                consume_final_evaluation_once(
                    ledger, approval(), "manifest-ok", "manifest-ok", "code-ok", "code-ok", loader, evaluator
                )
            self.assertEqual(calls, {"loader": 1, "evaluator": 1})

    def test_production_wrapper_requires_preflight_go_and_returns_bound_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            approvals = approval()
            approvals.update({"ci_conclusion": "success", "tests_passed": True})
            preflight = {"phase": "PRE_RUN_AUTHORIZATION", "status": "GO"}
            outcome, receipt = execute_final_evaluation_once(
                ledger, approvals, preflight,
                "manifest-ok", "manifest-ok", "code-ok", "code-ok",
                lambda: {"synthetic": True}, lambda payload: {"runs": [payload]},
            )
            self.assertEqual(outcome, {"runs": [{"synthetic": True}]})
            self.assertEqual(receipt["status"], "COMPLETED")
            self.assertTrue(ledger.exists())
            self.assertEqual(json.loads(ledger.read_text())["state"], "CONSUMED")
            access_log = Path(str(ledger) + ".access.json")
            self.assertTrue(access_log.exists())
            self.assertEqual(json.loads(access_log.read_text())["event"], "TEST_PAYLOAD_LOAD_ATTEMPT")

    def test_production_wrapper_rejects_hold_preflight_before_payload_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            calls = {"loader": 0}
            def loader():
                calls["loader"] += 1
                return {}
            with self.assertRaises(PermissionError):
                execute_final_evaluation_once(
                    ledger, approval(), {"phase": "PRE_RUN_AUTHORIZATION", "status": "HOLD"},
                    "manifest-ok", "manifest-ok", "code-ok", "code-ok",
                    loader, lambda payload: payload,
                )
            self.assertEqual(calls["loader"], 0)
            self.assertFalse(ledger.exists())

    def test_missing_preflight_go_does_not_read_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            bad = approval()
            bad.pop("preflight_status")
            with self.assertRaises(PermissionError):
                consume_final_evaluation_once(
                    ledger, bad, "manifest-ok", "manifest-ok", "code-ok", "code-ok",
                    lambda: {"sentinel": True}, lambda value: value,
                )
            self.assertFalse(ledger.exists())

    def test_unapproved_call_does_not_read_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            calls = {"loader": 0}

            def loader():
                calls["loader"] += 1
                return {"sentinel": "secret"}

            bad = approval()
            bad["user_approved"] = False
            with self.assertRaises(PermissionError):
                consume_final_evaluation_once(
                    ledger, bad, "manifest-ok", "manifest-ok", "code-ok", "code-ok", loader, lambda x: x
                )
            self.assertEqual(calls["loader"], 0)
            self.assertFalse(ledger.exists())

    def test_hash_mismatch_does_not_read_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"
            calls = {"loader": 0}

            def loader():
                calls["loader"] += 1
                return {"sentinel": "secret"}

            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                consume_final_evaluation_once(
                    ledger, approval(), "manifest-ok", "wrong-manifest", "code-ok", "code-ok", loader, lambda x: x
                )
            self.assertEqual(calls["loader"], 0)
            self.assertFalse(ledger.exists())

    def test_loader_failure_still_consumes_one_time_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "one-time.json"

            def broken_loader():
                raise OSError("synthetic read failure")

            with self.assertRaisesRegex(OSError, "synthetic read failure"):
                consume_final_evaluation_once(
                    ledger, approval(), "manifest-ok", "manifest-ok", "code-ok", "code-ok", broken_loader, lambda x: x
                )
            self.assertTrue(ledger.exists())
            with self.assertRaisesRegex(RuntimeError, "already consumed"):
                consume_final_evaluation_once(
                    ledger, approval(), "manifest-ok", "manifest-ok", "code-ok", "code-ok", lambda: {}, lambda x: x
                )


if __name__ == "__main__":
    unittest.main()
