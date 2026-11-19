"""D-094 LLM transport, structured-output, budget and secret-safety tests."""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from d094_llm_client import (
    LLMBudgetExceeded,
    LLMConfigurationError,
    LLMCostLimitExceeded,
    LLMResponseError,
    LLMClient,
    MockTransport,
    OpenAICompatibleTransport,
    TransportError,
    TransportResult,
)


def decision() -> dict:
    return {
        "action": "tool_call",
        "tool_name": "verify",
        "tool_arguments": {},
        "rationale": "Check the failed dependency first.",
        "verification_required": True,
    }


def result(content: str | None = None, request_id: str = "req-1") -> TransportResult:
    body = {
        "id": request_id,
        "model": "configured-model",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": content or json.dumps(decision()),
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 5, "total_tokens": 17},
    }
    return TransportResult(status=200, body=body, headers={"x-request-id": request_id})


def inputs() -> tuple[dict, list[dict], dict]:
    observation = {
        "task": "Recover safely",
        "public_state": {"failed": True},
        "memory": [],
    }
    tools = [
        {
            "name": "verify",
            "description": "Verify the dependency",
            "parameters_schema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "kind": "verify",
            "dependencies": [],
        }
    ]
    config = {
        "planning_mode": "direct",
        "recovery_mode": "retry_priority",
        "reflection_trigger": "none",
        "memory_mode": "recent_trajectory",
        "tool_call_guard": "strict_schema",
        "max_plan_steps": 3,
        "prompt_version": "d094-react-json-v1",
    }
    return observation, tools, config


class TestLLMClient(unittest.TestCase):
    def make_client(self, responses, **overrides) -> LLMClient:
        options = {
            "max_requests": 4,
            "max_cost_usd": 1.0,
            "input_price_per_1m": 1000.0,
            "output_price_per_1m": 2000.0,
            "max_retries": 0,
            "max_output_tokens": 128,
            "sleep_fn": lambda _seconds: None,
        }
        options.update(overrides)
        return LLMClient(MockTransport(list(responses)), **options)

    def test_mock_structured_output_and_usage_ledger(self):
        client = self.make_client([result()])
        output = client.generate_action(*inputs())
        self.assertEqual(output.tool_name, "verify")
        self.assertTrue(output.verification_required)
        self.assertEqual(output.model, "configured-model")
        self.assertEqual(output.request_id, "req-1")
        self.assertEqual(client.transport.calls[0][0]["temperature"], 0.0)
        self.assertEqual(
            client.transport.calls[0][0]["response_format"], {"type": "json_object"}
        )
        self.assertEqual(client.transport.calls[0][0]["max_tokens"], 128)
        record = client.ledger.records[0]
        self.assertEqual(record["backend"], "mock")
        self.assertEqual(record["input_tokens"], 12)
        self.assertEqual(record["output_tokens"], 5)
        self.assertEqual(record["status"], "SUCCESS")
        self.assertEqual(len(record["prompt_sha256"]), 64)
        self.assertGreaterEqual(record["latency_seconds"], 0.0)
        self.assertAlmostEqual(client.ledger.total_cost_usd, 0.022)

    def test_transport_error_retries_and_preserves_both_attempts(self):
        sleeps = []
        client = self.make_client(
            [
                TransportError("timeout", retryable=True),
                result(
                    '{"action":"finish","tool_name":null,"tool_arguments":{},"rationale":"Done","verification_required":false}',
                    "req-2",
                ),
            ],
            max_retries=1,
            max_cost_usd=100.0,
            sleep_fn=sleeps.append,
        )
        output = client.generate_action(*inputs())
        self.assertEqual(output.action, "finish")
        self.assertEqual(len(client.transport.calls), 2)
        self.assertEqual(
            [row["status"] for row in client.ledger.records], ["ERROR", "SUCCESS"]
        )
        self.assertEqual(client.ledger.records[0]["error_type"], "TransportError")
        self.assertEqual(len(sleeps), 1)

    def test_malformed_json_retries_without_logging_raw_response(self):
        client = self.make_client(
            [result("not json", "bad-1"), result(request_id="good-2")], max_retries=1
        )
        output = client.generate_action(*inputs())
        self.assertEqual(output.request_id, "good-2")
        serialized = json.dumps(client.ledger.records)
        self.assertNotIn("not json", serialized)
        self.assertEqual(client.ledger.records[0]["error_type"], "LLMResponseError")

    def test_extra_cot_field_is_rejected(self):
        payload = decision()
        payload["chain_of_thought"] = "private reasoning"
        client = self.make_client([result(json.dumps(payload))])
        with self.assertRaises(LLMResponseError):
            client.generate_action(*inputs())
        self.assertNotIn("private reasoning", json.dumps(client.ledger.records))

    def test_request_cap_blocks_second_call(self):
        client = self.make_client([result()], max_requests=1)
        client.generate_action(*inputs())
        with self.assertRaises(LLMBudgetExceeded):
            client.generate_action(*inputs())
        self.assertEqual(len(client.transport.calls), 1)
        self.assertEqual(len(client.ledger.records), 1)

    def test_cost_cap_records_then_stops(self):
        client = self.make_client([result()], max_cost_usd=0.01)
        with self.assertRaises(LLMCostLimitExceeded):
            client.generate_action(*inputs())
        self.assertAlmostEqual(client.ledger.total_cost_usd, 0.022)
        self.assertEqual(len(client.ledger.records), 1)

    def test_unknown_cost_is_not_zero(self):
        client = self.make_client(
            [result()], input_price_per_1m=None, output_price_per_1m=None
        )
        client.generate_action(*inputs())
        self.assertIsNone(client.ledger.total_cost_usd)
        self.assertTrue(client.ledger.cost_unknown)

    def test_hidden_label_and_evaluator_fields_never_reach_transport(self):
        for field in ("label", "min_reachable_harm", "class_success", "avoidable_harm"):
            with self.subTest(field=field):
                observation, tools, config = inputs()
                observation["public_state"][field] = "forbidden"
                client = self.make_client([result()])
                with self.assertRaises(ValueError):
                    client.generate_action(observation, tools, config)
                self.assertEqual(len(client.transport.calls), 0)

    def test_from_env_requires_complete_configuration(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "secret"}, clear=True):
            with self.assertRaises(LLMConfigurationError):
                LLMClient.from_env()

    def test_deepseek_flash_explicitly_disables_thinking(self):
        transport = MockTransport([result()], model="deepseek-flash")
        client = LLMClient(
            transport, max_requests=1, max_retries=0, sleep_fn=lambda _seconds: None
        )
        client.generate_action(*inputs())
        payload = transport.calls[0][0]
        self.assertEqual(payload["thinking"], {"type": "disabled"})
        self.assertNotIn("reasoning_effort", payload)

    def test_deepseek_environment_aliases_construct_real_client(self):
        from d094_llm_client import real_configuration_missing

        environment = {
            "DEEPSEEK_API_KEY": "configured-secret",
            "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
            "DEEPSEEK_MODEL": "deepseek-flash",
            "D094_LLM_INPUT_COST_PER_1M": "0.3",
            "D094_LLM_OUTPUT_COST_PER_1M": "1.2",
        }
        with patch.dict("os.environ", environment, clear=True):
            client = LLMClient.from_env()
            self.assertEqual(client.transport.model, "deepseek-flash")
            self.assertEqual(real_configuration_missing(), [])
            self.assertNotIn("configured-secret", repr(client.transport))

    def test_transport_error_has_conservative_cost_upper_bound(self):
        client = self.make_client(
            [TransportError("network disconnected", retryable=True), result()],
            max_retries=1,
            max_cost_usd=100.0,
        )
        client.generate_action(*inputs())
        self.assertTrue(client.ledger.cost_unknown)
        self.assertIsNone(client.ledger.total_cost_usd)
        self.assertGreater(client.ledger.total_cost_upper_usd, 0.022)
        self.assertGreater(client.ledger.records[0]["cost_upper_usd"], 0.0)

    def test_message_byte_cap_blocks_before_transport(self):
        transport = MockTransport([result()])
        client = LLMClient(
            transport, max_requests=1, max_retries=0, max_message_bytes=1
        )
        with self.assertRaises(LLMResponseError):
            client.generate_action(*inputs())
        self.assertEqual(len(transport.calls), 0)

    def test_real_http_path_serializes_openai_compatible_request(self):
        captured = []

        class FakeResponse:
            status = 200
            headers = {"x-request-id": "req-http"}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return json.dumps(result().body).encode("utf-8")

        def fake_urlopen(request, timeout):
            captured.append((request, timeout))
            return FakeResponse()

        transport = OpenAICompatibleTransport(
            base_url="https://api.example.com/v1",
            model="configured-model",
            api_key="secret-key",
            urlopen_impl=fake_urlopen,
        )
        client = LLMClient(
            transport, max_requests=1, max_retries=0, sleep_fn=lambda _seconds: None
        )
        output = client.generate_action(*inputs())
        self.assertEqual(output.request_id, "req-1")
        request, timeout = captured[0]
        self.assertEqual(
            request.full_url, "https://api.example.com/v1/chat/completions"
        )
        self.assertEqual(request.get_header("Authorization"), "Bearer secret-key")
        self.assertEqual(json.loads(request.data)["model"], "configured-model")
        self.assertEqual(timeout, 20.0)
        self.assertEqual(client.ledger.records[0]["backend"], "openai-compatible")
        self.assertNotIn("secret-key", json.dumps(client.ledger.records))
        self.assertNotIn("secret-key", repr(transport))

    def test_base_url_rejects_embedded_credentials_and_query(self):
        for url in (
            "https://user:pass@example.com/v1",
            "https://example.com/v1?api_key=secret",
        ):
            with self.subTest(url=url), self.assertRaises(LLMConfigurationError):
                OpenAICompatibleTransport(url, "m", "secret")


if __name__ == "__main__":
    unittest.main()
