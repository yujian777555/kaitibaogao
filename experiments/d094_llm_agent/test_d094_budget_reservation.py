"""D-094 request-before-send reservation and final-evaluation budget tests."""
from __future__ import annotations

import json
import unittest

from d094_budget import ReservedBudget, ReservedBudgetTransport
from d094_ledger import LLMCostLimitExceeded
from d094_genome import AgentGenome
from d094_llm_client import LLMClient, MockTransport, TransportError, TransportResult


class TestReservedBudget(unittest.TestCase):
    def test_search_cannot_spend_reserved_final_budget(self):
        budget = ReservedBudget(1.0, 0.3, 1.2)
        budget.reserve("B1", 0.2)
        budget.reserve("final:B2", 0.2, request_count=1)
        self.assertAlmostEqual(budget.snapshot()["available_search_cost_usd"], 0.6)
        budget.begin("search-1", 0.6, pool="search")
        budget.settle("search-1", actual_cost_usd=None)
        self.assertEqual(budget.snapshot()["reserved_cost_usd"], 0.4)
        with self.assertRaises(LLMCostLimitExceeded):
            budget.begin("search-2", 0.01, pool="search")
        budget.begin("final-request", 0.2, pool="final:B2")
        budget.settle("final-request", actual_cost_usd=0.1)
        snapshot = budget.snapshot()
        self.assertEqual(snapshot["sent_request_count"], 2)
        self.assertEqual(snapshot["budget_denied_count"], 1)
        self.assertEqual(snapshot["cost_usd"], 0.1)
        self.assertAlmostEqual(snapshot["cost_upper_usd"], 0.7)

    def test_insufficient_pre_run_reservation_fails_before_any_request(self):
        budget = ReservedBudget(0.5, 0.3, 1.2)
        with self.assertRaises(LLMCostLimitExceeded):
            budget.reserve("B1", 0.3)
            budget.reserve("final:B2", 0.3)
        self.assertEqual(budget.snapshot()["sent_request_count"], 0)

    def test_failed_and_retried_requests_each_consume_upper_bound(self):
        budget = ReservedBudget(1.0, 0.3, 1.2)
        budget.begin("attempt-1", 0.2, pool="search")
        budget.settle("attempt-1", actual_cost_usd=None)
        budget.begin("attempt-2", 0.2, pool="search")
        budget.settle("attempt-2", actual_cost_usd=0.1)
        snapshot = budget.snapshot()
        self.assertEqual(snapshot["sent_request_count"], 2)
        self.assertAlmostEqual(snapshot["cost_upper_usd"], 0.3)
        self.assertTrue(snapshot["cost_unknown"])

    def test_transport_reserves_before_call_and_settles_actual_usage(self):
        result = TransportResult(
            status=200,
            body={
                "id": "request-1",
                "model": "mock-model",
                "choices": [],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                },
            },
            headers={},
        )
        transport = MockTransport([result])
        budget = ReservedBudget(1.0, 0.3, 1.2)
        wrapped = ReservedBudgetTransport(transport, budget)
        payload = {
            "messages": [{"role": "user", "content": "public"}],
            "max_tokens": 128,
        }
        output = wrapped(payload, 1.0)
        self.assertEqual(output.body["id"], "request-1")
        snapshot = budget.snapshot()
        self.assertEqual(snapshot["sent_request_count"], 1)
        self.assertAlmostEqual(snapshot["cost_usd"], 0.000054)
        self.assertEqual(snapshot["pending_cost_usd"], 0.0)
        self.assertNotIn("secret", json.dumps(snapshot))

    def test_transport_error_preserves_pricing_and_allows_retry(self):
        result = TransportResult(
            status=200,
            body={
                "id": "request-2",
                "model": "mock-model",
                "choices": [],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "total_tokens": 120,
                },
            },
            headers={},
        )
        transport = MockTransport([TransportError("network", retryable=True), result])
        budget = ReservedBudget(1.0, 0.3, 1.2)
        wrapped = ReservedBudgetTransport(transport, budget)
        payload = {
            "messages": [{"role": "user", "content": "public"}],
            "max_tokens": 128,
        }
        with self.assertRaises(TransportError):
            wrapped(payload, 1.0)
        output = wrapped(payload, 1.0)
        self.assertEqual(output.body["id"], "request-2")
        snapshot = budget.snapshot()
        self.assertEqual(snapshot["sent_request_count"], 2)
        self.assertTrue(snapshot["cost_unknown"])
        self.assertAlmostEqual(snapshot["cost_usd"], 0.000054)
        self.assertGreater(snapshot["cost_upper_usd"], 0.000054)

    def test_negative_usage_retains_sent_request_upper_bound(self):
        result = TransportResult(
            status=200,
            body={
                "id": "bad-usage",
                "model": "mock-model",
                "choices": [],
                "usage": {
                    "prompt_tokens": -100,
                    "completion_tokens": 20,
                    "total_tokens": -80,
                },
            },
            headers={},
        )
        budget = ReservedBudget(1.0, 0.3, 1.2)
        wrapped = ReservedBudgetTransport(MockTransport([result]), budget)
        with self.assertRaises(ValueError):
            wrapped({"messages": [], "max_tokens": 128}, 1.0)
        snapshot = budget.snapshot()
        self.assertEqual(snapshot["sent_request_count"], 1)
        self.assertEqual(snapshot["pending_cost_usd"], 0.0)
        self.assertGreater(snapshot["cost_upper_usd"], 0.0)
        self.assertTrue(snapshot["cost_unknown"])

    def test_request_id_allocation_is_atomic_and_unique(self):
        budget = ReservedBudget(1.0, 0.3, 1.2)
        payload = {"messages": [], "max_tokens": 128}
        first = budget.next_request_id(payload)
        second = budget.next_request_id(payload)
        self.assertNotEqual(first, second)

    def test_global_request_cap_and_final_slot_are_protected(self):
        budget = ReservedBudget(1.0, 0.3, 1.2, max_requests=3)
        budget.reserve("final:B2", 0.1, request_count=1)
        budget.begin("search-1", 0.0, pool="search")
        budget.begin("search-2", 0.0, pool="search")
        with self.assertRaises(LLMCostLimitExceeded):
            budget.begin("search-3", 0.0, pool="search")
        budget.begin("final-1", 0.1, pool="final:B2")
        with self.assertRaises(LLMCostLimitExceeded):
            budget.begin("final-2", 0.0, pool="final:B2")
        self.assertEqual(budget.snapshot()["sent_request_count"], 3)
        self.assertEqual(budget.snapshot()["budget_denied_count"], 2)

    def test_budget_denial_is_not_real_client_cost_or_transport(self):
        transport = MockTransport([])
        budget = ReservedBudget(0.000001, 0.3, 1.2)
        client = LLMClient(
            ReservedBudgetTransport(transport, budget), max_requests=1, max_retries=0
        )
        observation = {"task": "public", "public_state": {}, "memory": []}
        with self.assertRaises(LLMCostLimitExceeded):
            client.generate_action(observation, [], AgentGenome().to_agent_config())
        self.assertEqual(len(transport.calls), 0)
        record = client.ledger.records[0]
        self.assertFalse(record["transport_sent"])
        self.assertEqual(record["cost_usd"], 0.0)
        self.assertEqual(record["cost_upper_usd"], 0.0)
        self.assertEqual(record["reservation_status"], "DENIED")
        self.assertIsNotNone(record["reserved_cost_upper_usd"])
        self.assertEqual(record["settled_cost_upper_usd"], 0.0)

    def test_client_preserves_per_request_reservation_and_settlement(self):
        transport = MockTransport(
            [
                TransportResult(
                    status=200,
                    body={
                        "id": "priced-request",
                        "model": "mock-model",
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "action": "finish",
                                            "tool_name": None,
                                            "tool_arguments": {},
                                            "rationale": "done",
                                            "verification_required": False,
                                        }
                                    )
                                }
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 10,
                            "completion_tokens": 2,
                            "total_tokens": 12,
                        },
                    },
                    headers={},
                )
            ]
        )
        budget = ReservedBudget(1.0, 0.3, 1.2)
        budget.reserve("final:B2", 0.01, request_count=1)
        client = LLMClient(
            ReservedBudgetTransport(transport, budget, "final:B2"),
            input_price_per_1m=0.3,
            output_price_per_1m=1.2,
            max_retries=0,
        )
        client.generate_action(
            {"task": "public", "public_state": {}, "memory": []},
            [],
            AgentGenome().to_agent_config(),
        )
        record = client.ledger.records[0]
        self.assertEqual(record["reservation_status"], "SETTLED")
        self.assertEqual(record["budget_pool"], "final:B2")
        self.assertTrue(record["budget_request_id"])
        self.assertGreater(record["reserved_cost_upper_usd"], 0.0)
        self.assertAlmostEqual(record["settled_cost_usd"], 0.0000054)
        self.assertLessEqual(
            record["settled_cost_upper_usd"], record["reserved_cost_upper_usd"]
        )
        self.assertFalse(record["reservation_exceeded"])

    def test_actual_cost_above_reserved_upper_is_invalid(self):
        budget = ReservedBudget(1.0, 0.3, 1.2)
        budget.begin("over-reservation", 0.01)
        budget.settle("over-reservation", actual_cost_usd=0.02)
        snapshot = budget.snapshot()
        self.assertTrue(snapshot["reservation_exceeded"])
        self.assertTrue(snapshot["over_budget"])


if __name__ == "__main__":
    unittest.main()
