"""Independent D-094 Phase 2 raw-episode audit tests."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from d094_phase2_audit import (
    audit_phase2,
    hard_constraint_counts,
    reconcile_budget_records,
)
from run_d094_phase2 import Phase2Config, run_phase2
from test_d094_phase2 import mock_client_factory


class TestD094Phase2Audit(unittest.TestCase):
    def test_mock_runner_summary_is_independently_recomputable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = Phase2Config(
                seeds=(101,),
                population_size=4,
                generations=1,
                max_concurrency=2,
                global_request_cap=1000,
                global_cost_cap=1.0,
            )
            run_phase2(root, config, client_factory=mock_client_factory)
            result = audit_phase2(root)
            self.assertEqual(result["status"], "PASS_WITH_LIMITATIONS")
            self.assertEqual(result["event_hash_chain"], "NOT_PROVIDED_BY_RUNNER")
            self.assertEqual(result["episode_count"], 132)
            self.assertEqual(result["unique_search_genomes"], 8)
            self.assertTrue(result["summary_matches_raw"])

    def test_metric_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = Phase2Config(
                seeds=(101,),
                population_size=4,
                generations=1,
                max_concurrency=2,
                global_request_cap=1000,
                global_cost_cap=1.0,
            )
            run_phase2(root, config, client_factory=mock_client_factory)
            path = root / "episodes.jsonl"
            rows = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ]
            rows[0]["metrics"]["task_success"] = False
            path.write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                audit_phase2(root)

    def test_execution_lock_accepts_canonical_lf_after_crlf_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_phase2(
                root,
                Phase2Config(
                    seeds=(101,),
                    population_size=2,
                    generations=0,
                    max_concurrency=1,
                    global_request_cap=1000,
                    global_cost_cap=1.0,
                ),
                client_factory=mock_client_factory,
            )
            lock_path = root / "execution_lock.json"
            canonical = hashlib.sha256(
                b"\n".join(lock_path.read_bytes().splitlines())
            ).hexdigest()
            summary_path = root / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["execution_lock_sha256"] = canonical
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            lock_path.write_bytes(
                lock_path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            )
            result = audit_phase2(root)
            self.assertTrue(result["execution_lock_canonical_match"])

    def test_public_events_map_to_six_hard_constraint_categories(self):
        events = [
            {
                "event_type": "tool_rejected",
                "payload": {"observation": {"error": "TOOL_SCHEMA_REJECTED"}},
            },
            {
                "event_type": "tool_rejected",
                "payload": {"observation": {"error": "ENVIRONMENT_PERMISSION_DENIED"}},
            },
            {
                "event_type": "tool_rejected",
                "payload": {"observation": {"error": "TASK_ALREADY_COMPLETED"}},
            },
            {
                "event_type": "tool_result",
                "payload": {"observation": {"status": "PENDING"}},
            },
            {
                "event_type": "tool_result",
                "payload": {"observation": {"status": "DUPLICATE_COMPENSATION"}},
            },
        ]
        result = hard_constraint_counts(
            [{"events": events, "agent_status": "MAX_STEPS"}]
        )
        self.assertEqual(result["invalid_action_count"], 1)
        self.assertEqual(result["unauthorized_action_count"], 1)
        self.assertEqual(result["illegal_transition_count"], 1)
        self.assertEqual(result["pending_count"], 1)
        self.assertEqual(result["duplicate_count"], 1)
        self.assertEqual(result["runtime_abort_count"], 1)

    def test_budget_denied_attempts_are_not_counted_as_sent_api_calls(self):
        records = [
            {
                "status": "SUCCESS",
                "error_type": None,
                "input_tokens": 10,
                "output_tokens": 5,
                "cost_usd": 0.1,
                "cost_upper_usd": 0.1,
            },
            {
                "status": "ERROR",
                "error_type": "LLMCostLimitExceeded",
                "request_id": None,
                "response_model": None,
                "input_tokens": None,
                "output_tokens": None,
                "cost_usd": None,
                "cost_upper_usd": 0.2,
            },
        ]
        result = reconcile_budget_records(records)
        self.assertEqual(result["request_count"], 1)
        self.assertEqual(result["budget_denied_count"], 1)
        self.assertEqual(result["input_tokens"], 10)
        self.assertEqual(result["cost_usd"], 0.1)
        self.assertEqual(result["cost_upper_usd"], 0.1)


if __name__ == "__main__":
    unittest.main()
