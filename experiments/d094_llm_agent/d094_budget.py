"""Request-before-send cost and request-slot reservation with protected final pools."""
from __future__ import annotations

import math
import threading
from typing import Any

from d094_ledger import (
    LLMCostLimitExceeded,
    LLMConfigurationError,
    canonical_json_bytes,
    payload_sha256,
)


class ReservedBudget:
    """Thread-safe conservative cost/request reservation with independent pools."""

    def __init__(
        self,
        max_cost_usd: float,
        input_price_per_1m: float | None,
        output_price_per_1m: float | None,
        max_requests: int = 1500,
    ) -> None:
        if not math.isfinite(max_cost_usd) or max_cost_usd <= 0.0 or max_requests <= 0:
            raise ValueError("invalid total budget")
        self.max_cost_usd = max_cost_usd
        self.max_requests = max_requests
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self.price_known = (
            input_price_per_1m is not None and output_price_per_1m is not None
        )
        self._reservations: dict[str, float] = {}
        self._request_reservations: dict[str, int] = {}
        self._pending: dict[str, dict[str, Any]] = {}
        self._spent_upper_by_pool: dict[str, float] = {}
        self._spent_requests_by_pool: dict[str, int] = {}
        self._cost_usd = 0.0
        self._cost_upper_usd = 0.0
        self.cost_unknown = False
        self.reservation_exceeded = False
        self.sent_request_count = 0
        self.budget_denied_count = 0
        self._id_ordinal = 0
        self._lock = threading.Lock()

    def request_cost_upper(self, payload: dict[str, Any]) -> float | None:
        """Price message bytes and output cap whenever prices are known, even after errors."""
        if not self.price_known:
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

    def _available_search_requests(self) -> int:
        return (
            self.max_requests
            - self.sent_request_count
            - sum(self._request_reservations.values())
        )

    def reserve(self, pool: str, amount_usd: float, request_count: int = 0) -> None:
        """Atomically reserve cost and request slots before any search request."""
        if not math.isfinite(amount_usd) or amount_usd < 0.0 or request_count < 0:
            raise ValueError("invalid reservation")
        with self._lock:
            if self._pending or pool in self._reservations:
                raise ValueError("invalid reservation state")
            if (
                amount_usd > self._available_search()
                or request_count > self._available_search_requests()
            ):
                self.budget_denied_count += 1
                raise LLMCostLimitExceeded("insufficient pre-run budget reservation")
            self._reservations[pool] = amount_usd
            self._request_reservations[pool] = request_count

    def begin(self, request_id: str, upper_usd: float, pool: str = "search") -> None:
        """Atomically reserve one request and its cost before transport."""
        if upper_usd is None:
            raise LLMConfigurationError("request prices are required before transport")
        if not math.isfinite(upper_usd) or upper_usd < 0.0:
            raise ValueError("invalid request upper bound")
        with self._lock:
            if request_id in self._pending:
                raise ValueError("duplicate pending request ID")
            if pool == "search":
                allowed = (
                    upper_usd <= self._available_search()
                    and self._available_search_requests() >= 1
                )
            else:
                allowed = (
                    upper_usd <= self._reservations.get(pool, 0.0)
                    and self._request_reservations.get(pool, 0) >= 1
                    and self.sent_request_count < self.max_requests
                )
            if not allowed:
                self.budget_denied_count += 1
                raise LLMCostLimitExceeded("request exceeds available pool budget")
            if pool != "search":
                self._reservations[pool] -= upper_usd
                self._request_reservations[pool] -= 1
            self._pending[request_id] = {"upper": upper_usd, "pool": pool}
            self.sent_request_count += 1

    def settle(self, request_id: str, actual_cost_usd: float | None) -> None:
        """Validate before removing pending; unknown usage retains the request upper bound."""
        if actual_cost_usd is not None and (
            not math.isfinite(actual_cost_usd) or actual_cost_usd < 0.0
        ):
            raise ValueError("invalid actual cost")
        with self._lock:
            if request_id not in self._pending:
                raise ValueError("unknown request reservation")
            record = self._pending[request_id]
            if actual_cost_usd is not None:
                self._cost_usd += actual_cost_usd
                settled_upper = actual_cost_usd
                if actual_cost_usd > record["upper"] + 1e-12:
                    self.reservation_exceeded = True
            else:
                self.cost_unknown = True
                settled_upper = record["upper"]
            self._pending.pop(request_id)
            self._cost_upper_usd += settled_upper
            pool = record["pool"]
            self._spent_upper_by_pool[pool] = (
                self._spent_upper_by_pool.get(pool, 0.0) + settled_upper
            )
            self._spent_requests_by_pool[pool] = (
                self._spent_requests_by_pool.get(pool, 0) + 1
            )

    def snapshot(self) -> dict[str, Any]:
        """Return consistent cost, request, reservation and settlement accounting."""
        with self._lock:
            pending = sum(record["upper"] for record in self._pending.values())
            upper = self._cost_upper_usd + pending
            return {
                "max_cost_usd": self.max_cost_usd,
                "max_requests": self.max_requests,
                "reserved_cost_usd": sum(self._reservations.values()),
                "reserved_pools": dict(sorted(self._reservations.items())),
                "reserved_request_count": sum(self._request_reservations.values()),
                "reserved_request_pools": dict(
                    sorted(self._request_reservations.items())
                ),
                "pending_cost_usd": pending,
                "spent_upper_by_pool": dict(sorted(self._spent_upper_by_pool.items())),
                "spent_requests_by_pool": dict(
                    sorted(self._spent_requests_by_pool.items())
                ),
                "available_search_cost_usd": self._available_search(),
                "available_search_requests": self._available_search_requests(),
                "sent_request_count": self.sent_request_count,
                "budget_denied_count": self.budget_denied_count,
                "cost_usd": self._cost_usd,
                "cost_complete": not self.cost_unknown,
                "cost_upper_usd": upper,
                "cost_unknown": self.cost_unknown,
                "reservation_exceeded": self.reservation_exceeded,
                "over_budget": self._cost_usd > self.max_cost_usd
                or upper > self.max_cost_usd
                or self.sent_request_count > self.max_requests
                or self.reservation_exceeded,
            }

    def next_request_id(self, payload: dict[str, Any]) -> str:
        """Atomically allocate a unique ordinal for every attempted transport call."""
        with self._lock:
            ordinal = self._id_ordinal
            self._id_ordinal += 1
        return payload_sha256(payload) + ":" + str(ordinal)


class ReservedBudgetTransport:
    """Reserve before transport and settle actual usage or failure upper bound."""

    def __init__(
        self, transport: Any, budget: ReservedBudget, pool: str = "search"
    ) -> None:
        self.transport = transport
        self.budget = budget
        self.pool = pool
        self.backend = transport.backend
        self.model = transport.model
        self.last_budget_event = None

    def __call__(self, payload: dict[str, Any], timeout: float) -> Any:
        request_id = self.budget.next_request_id(payload)
        upper = self.budget.request_cost_upper(payload)
        event = {
            "budget_request_id": request_id,
            "budget_pool": self.pool,
            "reserved_cost_upper_usd": upper,
            "reservation_status": "PENDING",
            "settled_cost_usd": None,
            "settled_cost_upper_usd": None,
            "reservation_exceeded": None,
        }
        self.last_budget_event = event
        try:
            self.budget.begin(request_id, upper, self.pool)
        except Exception:
            event.update(
                reservation_status="DENIED",
                settled_cost_usd=0.0,
                settled_cost_upper_usd=0.0,
                reservation_exceeded=False,
            )
            raise
        event["reservation_status"] = "RESERVED"
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
                and self.budget.price_known
            ):
                actual = (
                    input_tokens * self.budget.input_price_per_1m
                    + output_tokens * self.budget.output_price_per_1m
                ) / 1_000_000.0
            self.budget.settle(request_id, actual)
            event.update(
                reservation_status="SETTLED",
                settled_cost_usd=actual,
                settled_cost_upper_usd=actual if actual is not None else upper,
                reservation_exceeded=actual is not None and actual > upper + 1e-12,
            )
            return result
        except Exception:
            if request_id in self.budget._pending:
                self.budget.settle(request_id, None)
                event.update(
                    reservation_status="SETTLED",
                    settled_cost_usd=None,
                    settled_cost_upper_usd=upper,
                    reservation_exceeded=False,
                )
            raise
