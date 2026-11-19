"""D-094 request-before-send reservation and final-evaluation budget tests."""
from __future__ import annotations

import json
import unittest

from d094_budget import ReservedBudget, ReservedBudgetTransport
from d094_ledger import LLMCostLimitExceeded
from d094_llm_client import MockTransport, TransportResult


class TestReservedBudget(unittest.TestCase):
    def test_search_cannot_spend_reserved_final_budget(self):
        budget = ReservedBudget(1.0, 0.3, 1.2)
        budget.reserve("B1", 0.2)
        budget.reserve("final:B2", 0.2)
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


if __name__ == "__main__":
    unittest.main()
