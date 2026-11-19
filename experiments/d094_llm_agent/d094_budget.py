"""Request-before-send cost reservation with protected final-evaluation pools."""
from __future__ import annotations

import math
import threading
from typing import Any

from d094_ledger import LLMCostLimitExceeded, canonical_json_bytes, payload_sha256


class ReservedBudget:
    """Thread-safe conservative reservation ledger for search and protected pools."""

    def __init__(
        self,
        max_cost_usd: float,
        input_price_per_1m: float | None,
        output_price_per_1m: float | None,
    ) -> None:
        if not math.isfinite(max_cost_usd) or max_cost_usd <= 0.0:
            raise ValueError("invalid total budget")
        self.max_cost_usd = max_cost_usd
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self._reservations: dict[str, float] = {}
        self._pending: dict[str, dict[str, Any]] = {}
        self._spent_upper_by_pool: dict[str, float] = {}
        self._cost_usd = 0.0
        self._cost_upper_usd = 0.0
        self.cost_unknown = input_price_per_1m is None or output_price_per_1m is None
        self.sent_request_count = 0
        self.budget_denied_count = 0
        self._raw_attempt_count = 0
        self._lock = threading.Lock()

    def request_cost_upper(self, payload: dict[str, Any]) -> float | None:
        """Price maximum message bytes and output tokens before transport."""
        if self.cost_unknown:
            return None
        input_bytes = len(canonical_json_bytes(payload.get("messages", [])))
        output_tokens = payload.get("max_tokens", 0)
        if type(output_tokens) is not int or output_tokens < 0:
            raise ValueError("invalid output-token cap")
        return (
            input_bytes * self.input_price_per_1m
            + output_tokens * self.output_price_per_1m
        ) / 1_000_000.0

    def _available_search(self) -> float:
        return (
            self.max_cost_usd
            - sum(self._reservations.values())
            - sum(self._spent_upper_by_pool.values())
            - sum(record["upper"] for record in self._pending.values())
        )

    def reserve(self, pool: str, amount_usd: float) -> None:
        """Reserve a named B1/final pool before any search request."""
        if not math.isfinite(amount_usd) or amount_usd < 0.0:
            raise ValueError("invalid reservation")
        with self._lock:
            if self._pending or pool in self._reservations:
                raise ValueError("invalid reservation state")
            if amount_usd > self._available_search():
                self.budget_denied_count += 1
                raise LLMCostLimitExceeded("insufficient pre-run budget reservation")
            self._reservations[pool] = amount_usd

    def begin(self, request_id: str, upper_usd: float, pool: str = "search") -> None:
        """Atomically reserve one request before it can be sent."""
        if not math.isfinite(upper_usd) or upper_usd < 0.0:
            raise ValueError("invalid request upper bound")
        with self._lock:
            if request_id in self._pending:
                raise ValueError("duplicate pending request ID")
            available = (
                self._reservations.get(pool, 0.0)
                if pool != "search"
                else self._available_search()
            )
            if upper_usd > available:
                self.budget_denied_count += 1
                raise LLMCostLimitExceeded("request exceeds available pool budget")
            if pool != "search":
                self._reservations[pool] -= upper_usd
            self._pending[request_id] = {"upper": upper_usd, "pool": pool}
            self.sent_request_count += 1
            self._raw_attempt_count += 1

    def settle(self, request_id: str, actual_cost_usd: float | None) -> None:
        """Settle actual usage or retain the request upper bound on unknown usage."""
        with self._lock:
            if request_id not in self._pending:
                raise ValueError("unknown request reservation")
            record = self._pending.pop(request_id)
            if actual_cost_usd is not None:
                if not math.isfinite(actual_cost_usd) or actual_cost_usd < 0.0:
                    raise ValueError("invalid actual cost")
                self._cost_usd += actual_cost_usd
                settled_upper = actual_cost_usd
            else:
                self.cost_unknown = True
                settled_upper = record["upper"]
            self._cost_upper_usd += settled_upper
            pool = record["pool"]
            self._spent_upper_by_pool[pool] = (
                self._spent_upper_by_pool.get(pool, 0.0) + settled_upper
            )

    def snapshot(self) -> dict[str, Any]:
        """Return a consistent public reservation and settlement snapshot."""
        with self._lock:
            return {
                "max_cost_usd": self.max_cost_usd,
                "reserved_cost_usd": sum(self._reservations.values()),
                "reserved_pools": dict(sorted(self._reservations.items())),
                "pending_cost_usd": sum(
                    record["upper"] for record in self._pending.values()
                ),
                "spent_upper_by_pool": dict(sorted(self._spent_upper_by_pool.items())),
                "available_search_cost_usd": self._available_search(),
                "sent_request_count": self.sent_request_count,
                "budget_denied_count": self.budget_denied_count,
                "cost_usd": self._cost_usd,
                "cost_complete": not self.cost_unknown,
                "cost_upper_usd": self._cost_upper_usd
                + sum(record["upper"] for record in self._pending.values()),
                "cost_unknown": self.cost_unknown,
                "over_budget": self._cost_usd > self.max_cost_usd
                or self._cost_upper_usd
                + sum(record["upper"] for record in self._pending.values())
                > self.max_cost_usd,
            }

    def next_request_id(self, payload: dict[str, Any]) -> str:
        """Create a unique audit ID for every attempt, including retries."""
        with self._lock:
            ordinal = self._raw_attempt_count
        return payload_sha256(payload) + ":" + str(ordinal)


class ReservedBudgetTransport:
    """Reserve before transport and settle actual response usage or failure upper bound."""

    def __init__(
        self, transport: Any, budget: ReservedBudget, pool: str = "search"
    ) -> None:
        self.transport = transport
        self.budget = budget
        self.pool = pool
        self.backend = transport.backend
        self.model = transport.model

    def __call__(self, payload: dict[str, Any], timeout: float) -> Any:
        request_id = self.budget.next_request_id(payload)
        upper = self.budget.request_cost_upper(payload)
        self.budget.begin(request_id, upper, self.pool)
        try:
            result = self.transport(payload, timeout)
            usage = result.body.get("usage", {})
            input_tokens = (
                usage.get("prompt_tokens") if isinstance(usage, dict) else None
            )
            output_tokens = (
                usage.get("completion_tokens") if isinstance(usage, dict) else None
            )
            actual = None
            if (
                type(input_tokens) is int
                and type(output_tokens) is int
                and not self.budget.cost_unknown
            ):
                actual = (
                    input_tokens * self.budget.input_price_per_1m
                    + output_tokens * self.budget.output_price_per_1m
                ) / 1_000_000.0
            self.budget.settle(request_id, actual)
            return result
        except Exception:
            if request_id in self.budget._pending:
                self.budget.settle(request_id, None)
            raise
