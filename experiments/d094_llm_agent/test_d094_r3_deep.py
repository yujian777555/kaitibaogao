"""Regression tests for the read-only R3.1 deep-analysis evidence and formulas."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from analyze_d094_r3_deep import _episode_metrics, _quality_credit, _request_analysis
from d094_behavior import behavior_representation


HERE = Path(__file__).resolve().parent


def episode_row():
    events = [
        {
            "event_type": "tool_result",
            "payload": {"tool_name": "retry_primary", "success": False, "observation": {}, "harm": 0.25, "cost": 1.0},
        },
        {"event_type": "run_finished", "payload": {"status": "MAX_STEPS", "constraint_violations": 2}},
    ]
    final = {"state": {"completed": False}}
    metrics = {
        "task_success": False,
        "recovery_success": False,
        "constraint_violation": 2,
        "harm": 0.25,
        "tool_cost": 1.0,
        "input_tokens": 20,
        "output_tokens": 8,
        "token_cost_usd": 0.001,
        "token_cost_upper_usd": 0.001,
        "latency_seconds": 0.2,
        "phenotype_hash": behavior_representation(events, agent_status="MAX_STEPS", final_public_observation=final)["canonical_sha256"],
    }
    return {
        "episode_id": "synthetic-deep-analysis",
        "task_id": "train-fixture",
        "seed": 1,
        "agent_status": "MAX_STEPS",
        "execution_error": False,
        "events": events,
        "final_public_observation": final,
        "metrics": metrics,
        "request_ledger": [
            {
                "attempt": 0,
                "status": "SUCCESS",
                "error": None,
                "transport_sent": True,
                "prompt_sha256": "same-prompt",
                "input_tokens": 12,
                "output_tokens": 5,
                "cost_usd": 0.0006,
                "cost_upper_usd": 0.0006,
                "latency_seconds": 0.1,
            },
            {
                "attempt": 1,
                "status": "SUCCESS",
                "error": None,
                "transport_sent": True,
                "prompt_sha256": "same-prompt",
                "input_tokens": 8,
                "output_tokens": 3,
                "cost_usd": 0.0004,
                "cost_upper_usd": 0.0004,
                "latency_seconds": 0.1,
            },
        ],
    }


class TestDeepAnalysis(unittest.TestCase):
    def test_episode_metrics_rebuilt_from_events_terminal_state_and_requests(self):
        row = episode_row()
        rebuilt = _episode_metrics(row)
        self.assertEqual(rebuilt, row["metrics"])
        row["_recomputed"] = rebuilt
        request = _request_analysis([row])
        self.assertEqual(request["requests"], 2)
        self.assertEqual(request["same_prompt_repeat_records"], 1)
        self.assertEqual(request["same_prompt_repeat_ratio"], 0.5)
        self.assertIn("MAX_RETRIES_0", request["transport_retry_status"])
        self.assertEqual(request["failed_request_count"], 0)

    def test_saved_metric_tampering_is_rejected(self):
        row = episode_row()
        row["metrics"]["harm"] = 0.0
        with self.assertRaisesRegex(ValueError, "saved episode metric mismatch"):
            _episode_metrics(row)

    def test_resource_only_change_has_zero_deep_quality_credit(self):
        parent = episode_row()
        child = copy.deepcopy(parent)
        parent["_recomputed"] = parent["metrics"]
        child["_recomputed"] = dict(child["metrics"], token_cost_usd=0.0, latency_seconds=0.0)
        self.assertEqual(_quality_credit(parent, child), 0.0)
        child["_recomputed"]["constraint_violation"] = 3
        self.assertEqual(_quality_credit(parent, child), -1.0)

    def test_saved_real_analysis_has_complete_identity_and_zero_search_success(self):
        result = json.loads((HERE / "results" / "r3_1_deep_analysis" / "analysis.json").read_text(encoding="utf-8"))
        self.assertEqual(result["analysis_sha256"], "2362a32e6923d6c516661b301e6d7bcdb68e3a8ef6d78b3a8ff44271ce43982e")
        self.assertFalse(result["api_used"])
        self.assertEqual(result["episode_identity"]["count"], 42)
        self.assertEqual(result["episode_identity"]["unique_provider_request_ids"], 169)
        self.assertTrue(result["episode_identity"]["all_hash_chains_valid"])
        self.assertEqual(result["source_independent_audit_status"], "PASS")
        for arm in ("B2", "B3", "B4", "B5"):
            self.assertEqual(result["search"][arm]["unique_genomes"], 4)
            self.assertEqual(result["search"][arm]["successful_candidates"], 0)

    def test_r3_1_source_files_still_match_analysis_snapshot(self):
        result = json.loads((HERE / "results" / "r3_1_deep_analysis" / "analysis.json").read_text(encoding="utf-8"))
        source = HERE / "results" / "r3_1_real"
        current = {
            str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(source.rglob("*"))
            if path.is_file()
        }
        self.assertEqual(current, result["source_files_sha256"])


if __name__ == "__main__":
    unittest.main()
