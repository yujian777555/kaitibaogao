"""Independent R3 audit acceptance and tamper-detection tests."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from audit_d094_r3 import audit_r3
from run_d094_r3 import R3Config, run_r3
from test_d094_r3 import mock_factory


class TestR3IndependentAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tempdir.name) / "mock_r3"
        result = run_r3(cls.root, R3Config.revised(), client_factory=mock_factory)
        if result["status"] != "COMPLETED":
            raise RuntimeError("Mock R3 fixture did not complete")

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()

    def test_mock_run_is_fully_recomputable(self):
        result = audit_r3(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["episode_count"], 42)
        self.assertTrue(result["summary_matches_raw"])
        self.assertEqual(set(result["arms"]), {"B1", "B2", "B3", "B4", "B5"})
        expected_requests = json.loads(
            (self.root / "summary.json").read_text(encoding="utf-8")
        )["budget"]["sent_request_count"]
        self.assertEqual(result["budget"]["sent_request_count"], expected_requests)

    def test_trace_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "run"
            shutil.copytree(self.root, copied)
            trace = next((copied / "traces").glob("*.jsonl"))
            events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
            events[0]["payload"]["rationale"] = "tampered"
            trace.write_text(
                "\n".join(json.dumps(event) for event in events) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "trace SHA-256"):
                audit_r3(copied)

    def test_request_cost_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "run"
            shutil.copytree(self.root, copied)
            episodes = copied / "episodes.jsonl"
            rows = [json.loads(line) for line in episodes.read_text(encoding="utf-8").splitlines()]
            rows[0]["request_ledger"][0]["cost_usd"] = 0.01
            episodes.write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "provider token pricing"):
                audit_r3(copied)


if __name__ == "__main__":
    unittest.main()
