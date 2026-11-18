"""D-094 request budgets, token/cost accounting and hash-chain execution logs."""
from __future__ import annotations

import hashlib
import json
import math
import re
import threading
from pathlib import Path
from typing import Any


class D094Error(Exception):
    """Base class for expected D-094 execution failures."""


class LLMConfigurationError(D094Error):
    """Raised when a real API configuration is incomplete or unsafe."""


class LLMBudgetExceeded(D094Error):
    """Raised before a request that would exceed the HTTP attempt budget."""


class LLMCostLimitExceeded(D094Error):
    """Raised when the configured or recorded cost reaches its hard limit."""


class LLMResponseError(D094Error):
    """Raised when a model response cannot produce the strict public decision."""


SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "set-cookie",
    "secret",
    "client_secret",
    "access_token",
    "refresh_token",
}
_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+")


def canonical_json_bytes(payload: Any) -> bytes:
    """Serialize public JSON data deterministically."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def payload_sha256(payload: Any) -> str:
    """Hash a canonical public payload."""
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def sanitize_public(value: Any) -> Any:
    """Redact credential-shaped fields without retaining their values."""
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]"
            if str(key).lower() in SENSITIVE_KEYS
            else sanitize_public(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_public(item) for item in value]
    if isinstance(value, str):
        return _BEARER.sub("Bearer [REDACTED]", value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite values cannot enter the ledger")
        return value
    raise ValueError("unsupported ledger value: " + type(value).__name__)


def safe_error(error: Exception) -> str:
    """Return a bounded, sanitized error without response bodies or headers."""
    text = _BEARER.sub("Bearer [REDACTED]", str(error))
    return text[:240]


class RequestLedger:
    """Account for every HTTP attempt, including failures and retries."""

    def __init__(
        self,
        max_requests: int,
        max_cost_usd: float,
        input_price_per_1m: float | None = None,
        output_price_per_1m: float | None = None,
    ) -> None:
        if max_requests <= 0 or not math.isfinite(max_cost_usd) or max_cost_usd < 0.0:
            raise ValueError("invalid request or cost budget")
        for price in (input_price_per_1m, output_price_per_1m):
            if price is not None and (not math.isfinite(price) or price < 0.0):
                raise ValueError("invalid token price")
        self.max_requests = max_requests
        self.max_cost_usd = max_cost_usd
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self.records: list[dict[str, Any]] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.cost_unknown = False
        self._total_cost_usd = 0.0
        self._total_cost_upper_usd = 0.0
        self.cost_upper_unknown = False

    @property
    def total_cost_usd(self) -> float | None:
        """Return None when any provider usage lacks a trustworthy price."""
        return None if self.cost_unknown else self._total_cost_usd

    @property
    def known_cost_usd(self) -> float:
        """Return the sum backed by actual provider token usage."""
        return self._total_cost_usd

    @property
    def total_cost_upper_usd(self) -> float | None:
        """Return a conservative cost upper bound, including no-response errors."""
        return None if self.cost_upper_unknown else self._total_cost_upper_usd

    def begin(self, model: str, backend: str, prompt_sha256: str) -> int:
        """Reserve one HTTP attempt and append its PENDING record."""
        if len(self.records) >= self.max_requests:
            raise LLMBudgetExceeded("HTTP attempt budget exhausted")
        if (
            self.total_cost_upper_usd is not None
            and self.total_cost_upper_usd >= self.max_cost_usd
        ):
            raise LLMCostLimitExceeded("API cost upper-bound budget exhausted")
        self.records.append(
            {
                "attempt": len(self.records),
                "status": "PENDING",
                "backend": backend,
                "model": model,
                "response_model": None,
                "request_id": None,
                "prompt_sha256": prompt_sha256,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "cost_usd": None,
                "latency_seconds": None,
                "error_type": None,
                "error": None,
            }
        )
        return len(self.records) - 1

    def finish(
        self,
        index: int,
        *,
        status: str,
        latency_seconds: float,
        response_model: str | None = None,
        request_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        cost_upper_usd: float | None = None,
        error: Exception | None = None,
    ) -> None:
        """Finalize exactly one reserved attempt with public accounting fields."""
        if status not in {"SUCCESS", "ERROR"}:
            raise ValueError("invalid terminal request status")
        record = self.records[index]
        if record["status"] != "PENDING":
            raise ValueError("request attempt was already finalized")
        for value in (input_tokens, output_tokens, total_tokens):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("invalid token usage")
        if cost_upper_usd is not None and (
            not math.isfinite(cost_upper_usd) or cost_upper_usd < 0.0
        ):
            raise ValueError("invalid cost upper bound")
        priced = (
            input_tokens is not None
            and output_tokens is not None
            and self.input_price_per_1m is not None
            and self.output_price_per_1m is not None
        )
        if priced:
            cost = (
                input_tokens * self.input_price_per_1m
                + output_tokens * self.output_price_per_1m
            ) / 1_000_000.0
            self._total_cost_usd += cost
            upper = cost
        else:
            cost = None
            self.cost_unknown = True
            upper = cost_upper_usd
        if upper is None:
            self.cost_upper_unknown = True
        else:
            self._total_cost_upper_usd += upper
        self.total_input_tokens += input_tokens or 0
        self.total_output_tokens += output_tokens or 0
        record.update(
            status=status,
            response_model=response_model,
            request_id=request_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost,
            cost_upper_usd=upper,
            latency_seconds=max(0.0, latency_seconds),
            error_type=None if error is None else type(error).__name__,
            error=None if error is None else safe_error(error),
        )

    def enforce_cost_limit(self) -> None:
        """Stop subsequent use when the conservative cost upper bound exceeds its cap."""
        if (
            self.total_cost_upper_usd is not None
            and self.total_cost_upper_usd > self.max_cost_usd
        ):
            raise LLMCostLimitExceeded(
                "API cost upper-bound budget exceeded by recorded usage"
            )


class ExecutionLedger:
    """Write sanitized hash-linked agent events without storing hidden reasoning."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        if self.path.exists() and self.path.stat().st_size > 0:
            raise ValueError("refusing to append a new hash chain to a nonempty trace")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.events: list[dict[str, Any]] = []

    def append(self, event_type: str, payload: Any) -> dict[str, Any]:
        """Append one canonical event and its SHA-256 link."""
        previous = self.events[-1]["event_sha256"] if self.events else None
        event = {
            "sequence": len(self.events),
            "event_type": event_type,
            "payload": sanitize_public(payload),
            "previous_event_sha256": previous,
        }
        event["event_sha256"] = payload_sha256(event)
        self.events.append(event)
        with self.path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(
                json.dumps(
                    event, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                )
                + "\n"
            )
        return event


def verify_execution_ledger(events: list[dict[str, Any]]) -> bool:
    """Recompute the complete hash chain from loaded public events."""
    previous = None
    for index, event in enumerate(events):
        unsigned = {key: value for key, value in event.items() if key != "event_sha256"}
        if event["sequence"] != index or event["previous_event_sha256"] != previous:
            return False
        if payload_sha256(unsigned) != event["event_sha256"]:
            return False
        previous = event["event_sha256"]
    return True


class SharedBudget:
    """Thread-safe request and conservative token-cost budget across episodes."""

    def __init__(
        self,
        max_requests: int,
        max_cost_usd: float,
        input_price_per_1m: float | None,
        output_price_per_1m: float | None,
    ) -> None:
        if max_requests <= 0 or not math.isfinite(max_cost_usd) or max_cost_usd < 0.0:
            raise ValueError("invalid shared budget")
        self.max_requests = max_requests
        self.max_cost_usd = max_cost_usd
        self.input_price_per_1m = input_price_per_1m
        self.output_price_per_1m = output_price_per_1m
        self.request_count = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cost_usd = 0.0
        self._cost_upper_usd = 0.0
        self.cost_unknown = input_price_per_1m is None or output_price_per_1m is None
        self.cost_upper_unknown = self.cost_unknown
        self._pending_upper: dict[int, float] = {}
        self._lock = threading.Lock()

    def _request_upper(self, payload: dict[str, Any]) -> float | None:
        if self.cost_upper_unknown:
            return None
        input_bytes = len(canonical_json_bytes(payload.get("messages", [])))
        output_tokens = payload.get("max_tokens", 0)
        if type(output_tokens) is not int or output_tokens < 0:
            raise ValueError("invalid request output cap")
        return (
            input_bytes * self.input_price_per_1m
            + output_tokens * self.output_price_per_1m
        ) / 1_000_000.0

    def before_request(self, payload: dict[str, Any]) -> None:
        """Atomically reserve one real or Mock transport attempt and its upper bound."""
        upper = self._request_upper(payload)
        with self._lock:
            if self.request_count >= self.max_requests:
                raise LLMBudgetExceeded("shared HTTP attempt budget exhausted")
            current_upper = self._cost_upper_usd + sum(self._pending_upper.values())
            if self.cost_usd >= self.max_cost_usd or current_upper >= self.max_cost_usd:
                raise LLMCostLimitExceeded("shared API cost budget exhausted")
            self.request_count += 1
            if upper is not None:
                self._pending_upper[threading.get_ident()] = upper

    def after_response(self, result: Any) -> None:
        """Replace a request upper bound with actual provider usage when available."""
        usage = result.body.get("usage", {})
        input_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        output_tokens = (
            usage.get("completion_tokens") if isinstance(usage, dict) else None
        )
        with self._lock:
            upper = self._pending_upper.pop(threading.get_ident(), 0.0)
            if type(input_tokens) is not int or type(output_tokens) is not int:
                self.cost_unknown = True
                self._cost_upper_usd += upper
                return
            self.input_tokens += input_tokens
            self.output_tokens += output_tokens
            if not self.cost_unknown:
                actual = (
                    input_tokens * self.input_price_per_1m
                    + output_tokens * self.output_price_per_1m
                ) / 1_000_000.0
                self.cost_usd += actual
                self._cost_upper_usd += actual
            else:
                self._cost_upper_usd += upper

    def after_error(self) -> None:
        """Retain the conservative upper bound for a no-response transport error."""
        with self._lock:
            self.cost_unknown = True
            self._cost_upper_usd += self._pending_upper.pop(threading.get_ident(), 0.0)

    def snapshot(self) -> dict[str, Any]:
        """Return a consistent public accounting snapshot."""
        with self._lock:
            upper = self._cost_upper_usd + sum(self._pending_upper.values())
            return {
                "request_count": self.request_count,
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens,
                "cost_usd": None if self.cost_unknown else self.cost_usd,
                "cost_upper_usd": None if self.cost_upper_unknown else upper,
                "cost_unknown": self.cost_unknown,
                "max_requests": self.max_requests,
                "max_cost_usd": self.max_cost_usd,
                "over_budget": self.request_count > self.max_requests
                or self.cost_usd > self.max_cost_usd
                or (not self.cost_upper_unknown and upper > self.max_cost_usd),
            }


class SharedBudgetTransport:
    """Apply one shared budget around any real or Mock transport."""

    def __init__(self, transport: Any, budget: SharedBudget) -> None:
        self.transport = transport
        self.budget = budget
        self.backend = transport.backend
        self.model = transport.model

    def __call__(self, payload: dict[str, Any], timeout: float) -> Any:
        self.budget.before_request(payload)
        try:
            result = self.transport(payload, timeout)
        except Exception:
            self.budget.after_error()
            raise
        self.budget.after_response(result)
        return result
