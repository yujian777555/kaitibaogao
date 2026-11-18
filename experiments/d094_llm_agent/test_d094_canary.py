"""D-094 Mock integration and real-Canary configuration-gate tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from run_d094_canary import execute_real_canary, run_mock_canary


class TestD094Canary(unittest.TestCase):
    def test_mock_canary_executes_two_llm_guided_tool_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_mock_canary(Path(directory))
            self.assertEqual(result["status"], "MOCK_PASS")
            self.assertEqual(result["backend"], "mock")
            self.assertFalse(result["api_connected"])
            self.assertEqual(result["agent_status"], "COMPLETED")
            self.assertGreaterEqual(result["llm_decision_count"], 2)
            self.assertEqual(result["api_attempt_count"], 2)
            self.assertEqual(
                result["executed_tools"], ["verify_dependency", "complete_recovery"]
            )
            self.assertTrue(result["hash_chain_valid"])
            self.assertEqual(result["constraint_violations"], 0)

    def test_real_canary_fails_closed_without_complete_configuration(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "os.environ", {"OPENAI_API_KEY": "present-but-not-logged"}, clear=True
        ):
            result = execute_real_canary(Path(directory))
            self.assertEqual(result["status"], "BLOCKED_CONFIGURATION")
            self.assertFalse(result["api_connected"])
            self.assertEqual(result["api_attempt_count"], 0)
            self.assertEqual(result["input_tokens"], 0)
            self.assertEqual(result["output_tokens"], 0)
            self.assertEqual(result["cost_usd"], 0.0)
            self.assertIn("BASE_URL", result["missing_configuration"])
            self.assertIn("MODEL", result["missing_configuration"])
            self.assertNotIn("API_KEY", result["missing_configuration"])
            self.assertFalse((Path(directory) / "trace.jsonl").exists())

    def test_invalid_price_configuration_fails_closed_before_network(self):
        environment = {
            "D094_LLM_API_KEY": "present-but-not-logged",
            "D094_LLM_BASE_URL": "https://api.example.com/v1",
            "D094_LLM_MODEL": "configured-model",
            "D094_LLM_INPUT_COST_PER_1M": "not-a-number",
            "D094_LLM_OUTPUT_COST_PER_1M": "1.0",
        }
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            "os.environ", environment, clear=True
        ):
            result = execute_real_canary(Path(directory))
            self.assertEqual(result["status"], "BLOCKED_CONFIGURATION")
            self.assertEqual(result["api_attempt_count"], 0)
            self.assertIn("D094_LLM_INPUT_COST_PER_1M", result["missing_configuration"])


if __name__ == "__main__":
    unittest.main()
