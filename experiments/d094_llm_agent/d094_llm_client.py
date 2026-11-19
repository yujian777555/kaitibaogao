"""OpenAI-compatible and Mock LLM clients with strict structured decisions."""
from __future__ import annotations

import http.client
import json
import math
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from d094_ledger import (
    LLMBudgetExceeded,
    LLMConfigurationError,
    LLMCostLimitExceeded,
    LLMResponseError,
    RequestLedger,
    canonical_json_bytes,
    payload_sha256,
)
from d094_prompts import build_messages, prompt_template_sha256


@dataclass(frozen=True)
class TransportResult:
    """Complete public HTTP result required from real and Mock transports."""

    status: int
    body: dict[str, Any]
    headers: dict[str, str]


class TransportError(Exception):
    """Sanitized transport failure with explicit retry semantics."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        retryable: bool = False,
        retry_after: float = 0.0,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.retryable = retryable
        self.retry_after = max(0.0, retry_after)


@dataclass(frozen=True)
class LLMDecision:
    """Validated structured action and final successful request metadata."""

    action: str
    tool_name: str | None
    tool_arguments: dict[str, Any]
    rationale: str
    verification_required: bool
    model: str
    request_id: str | None
    prompt_sha256: str
    input_tokens: int | None
    output_tokens: int | None
    latency_seconds: float


class MockTransport:
    """Scripted external-boundary double used only for tests and dry runs."""

    backend = "mock"

    def __init__(
        self, results: list[TransportResult | Exception], model: str = "mock-model"
    ) -> None:
        self.results = list(results)
        self.model = model
        self.calls: list[tuple[dict[str, Any], float]] = []

    def __call__(self, payload: dict[str, Any], timeout: float) -> TransportResult:
        self.calls.append((payload, timeout))
        if not self.results:
            raise TransportError("Mock response queue exhausted", retryable=False)
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class OpenAICompatibleTransport:
    """Synchronous OpenAI-compatible chat-completions HTTP transport."""

    backend = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str,
        urlopen_impl: Callable[..., Any] | None = None,
    ) -> None:
        if not model.strip() or not api_key:
            raise LLMConfigurationError("model and API key are required")
        parsed = urllib.parse.urlsplit(base_url.rstrip("/"))
        local_http = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not (parsed.scheme == "http" and local_http):
            raise LLMConfigurationError("API base URL must use HTTPS")
        if (
            parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise LLMConfigurationError(
                "API base URL cannot contain credentials, query or fragment"
            )
        if not parsed.netloc:
            raise LLMConfigurationError("API base URL is incomplete")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._api_key = api_key
        self._urlopen = urllib.request.urlopen if urlopen_impl is None else urlopen_impl
        self.endpoint = (
            self.base_url
            if self.base_url.endswith("/chat/completions")
            else self.base_url + "/chat/completions"
        )

    def __repr__(self) -> str:
        return f"OpenAICompatibleTransport(base_url={self.base_url!r}, model={self.model!r})"

    def __call__(self, payload: dict[str, Any], timeout: float) -> TransportResult:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(
                payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False
            ).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with self._urlopen(request, timeout=timeout) as response:
                raw = response.read()
                body = json.loads(raw.decode("utf-8"))
                headers = {
                    str(key).lower(): str(value)
                    for key, value in response.headers.items()
                }
                status = int(getattr(response, "status", 200))
        except urllib.error.HTTPError as error:
            retry_after = 0.0
            try:
                retry_after = float(error.headers.get("Retry-After", "0"))
            except (TypeError, ValueError):
                retry_after = 0.0
            raise TransportError(
                f"HTTP {error.code}",
                status=error.code,
                retryable=error.code in {408, 429} or 500 <= error.code <= 599,
                retry_after=retry_after,
            ) from None
        except (
            urllib.error.URLError,
            TimeoutError,
            socket.timeout,
            http.client.HTTPException,
        ):
            raise TransportError("transport failure", retryable=True) from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise TransportError(
                "invalid HTTP JSON envelope", retryable=False
            ) from None
        if status != 200:
            raise TransportError(
                f"HTTP {status}", status=status, retryable=status >= 500
            )
        if not isinstance(body, dict):
            raise TransportError("invalid HTTP response object", retryable=False)
        return TransportResult(status=status, body=body, headers=headers)


def _usage(body: dict[str, Any]) -> tuple[int | None, int | None, int | None]:
    usage = body.get("usage")
    if not isinstance(usage, dict):
        return None, None, None
    values = []
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        value = usage.get(key)
        if value is not None and (type(value) is not int or value < 0):
            raise LLMResponseError("invalid token usage")
        values.append(value)
    return values[0], values[1], values[2]


def _parse_decision(content: Any) -> dict[str, Any]:
    if not isinstance(content, str):
        raise LLMResponseError("assistant content is not text")
    try:
        value = json.loads(content)
    except json.JSONDecodeError:
        raise LLMResponseError("assistant content is not valid JSON") from None
    required = {
        "action",
        "tool_name",
        "tool_arguments",
        "rationale",
        "verification_required",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise LLMResponseError("decision schema mismatch")
    if value["action"] not in {"tool_call", "finish"}:
        raise LLMResponseError("invalid action")
    if not isinstance(value["tool_arguments"], dict) or not isinstance(
        value["verification_required"], bool
    ):
        raise LLMResponseError("invalid tool arguments or verification flag")
    if not isinstance(value["rationale"], str) or len(value["rationale"]) > 240:
        raise LLMResponseError("invalid public rationale")
    if value["action"] == "tool_call" and (
        not isinstance(value["tool_name"], str)
        or not value["tool_name"]
        or len(value["tool_name"]) > 64
    ):
        raise LLMResponseError("tool_call requires a bounded tool name")
    if len(canonical_json_bytes(value["tool_arguments"])) > 256:
        raise LLMResponseError("tool arguments exceed the public decision byte cap")
    if value["action"] == "finish" and (
        value["tool_name"] is not None or value["tool_arguments"]
    ):
        raise LLMResponseError("finish cannot include a tool call")
    return value


class LLMClient:
    """Generate validated actions with bounded retries, requests and priced cost."""

    def __init__(
        self,
        transport: Any,
        *,
        max_requests: int = 4,
        max_cost_usd: float = 0.10,
        input_price_per_1m: float | None = None,
        output_price_per_1m: float | None = None,
        max_retries: int = 1,
        timeout: float = 20.0,
        max_output_tokens: int = 128,
        max_message_bytes: int | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        if max_retries < 0 or timeout <= 0.0 or max_output_tokens <= 0:
            raise ValueError("invalid retry, timeout or output-token configuration")
        if max_message_bytes is not None and max_message_bytes <= 0:
            raise ValueError("invalid message byte cap")
        self.transport = transport
        self.max_retries = max_retries
        self.timeout = timeout
        self.max_output_tokens = max_output_tokens
        self.max_message_bytes = max_message_bytes
        self.sleep_fn = sleep_fn
        self.clock = clock
        self.ledger = RequestLedger(
            max_requests=max_requests,
            max_cost_usd=max_cost_usd,
            input_price_per_1m=input_price_per_1m,
            output_price_per_1m=output_price_per_1m,
        )

    @classmethod
    def from_env(cls) -> "LLMClient":
        """Construct the real client from environment variables without logging secrets."""
        api_key = (
            os.environ.get("D094_LLM_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        base_url = (
            os.environ.get("D094_LLM_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or os.environ.get("OPENAI_API_BASE")
        )
        model = (
            os.environ.get("D094_LLM_MODEL")
            or os.environ.get("DEEPSEEK_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or os.environ.get("OPENAI_MODEL_NAME")
        )
        missing = []
        if not api_key:
            missing.append("D094_LLM_API_KEY or OPENAI_API_KEY")
        if not base_url:
            missing.append("D094_LLM_BASE_URL or OPENAI_BASE_URL")
        if not model:
            missing.append("D094_LLM_MODEL or OPENAI_MODEL")
        if missing:
            raise LLMConfigurationError(
                "missing real API configuration: " + ", ".join(missing)
            )

        def number(name: str, default: float) -> float:
            raw = os.environ.get(name)
            try:
                return default if raw is None else float(raw)
            except ValueError:
                raise LLMConfigurationError(
                    "invalid numeric configuration: " + name
                ) from None

        def optional_number(name: str) -> float | None:
            return None if os.environ.get(name) is None else number(name, 0.0)

        transport = OpenAICompatibleTransport(
            base_url=base_url, model=model, api_key=api_key
        )
        return cls(
            transport,
            max_requests=int(number("D094_LLM_MAX_REQUESTS", 4)),
            max_cost_usd=number("D094_LLM_MAX_COST_USD", 0.10),
            input_price_per_1m=optional_number("D094_LLM_INPUT_COST_PER_1M"),
            output_price_per_1m=optional_number("D094_LLM_OUTPUT_COST_PER_1M"),
            max_retries=int(number("D094_LLM_MAX_RETRIES", 1)),
            timeout=number("D094_LLM_TIMEOUT_SECONDS", 20.0),
            max_output_tokens=int(number("D094_LLM_MAX_OUTPUT_TOKENS", 128)),
        )

    def generate_action(
        self,
        observation: dict[str, Any],
        available_tools: list[dict[str, Any]],
        agent_config: dict[str, Any],
    ) -> LLMDecision:
        """Generate one structured action; every HTTP attempt is ledgered."""
        messages = build_messages(observation, available_tools, agent_config)
        if (
            self.max_message_bytes is not None
            and len(canonical_json_bytes(messages)) > self.max_message_bytes
        ):
            raise LLMResponseError("message byte cap exceeded before transport")
        payload = {
            "model": self.transport.model,
            "messages": messages,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "max_tokens": self.max_output_tokens,
        }
        if self.transport.model == "deepseek-flash":
            payload["thinking"] = {"type": "disabled"}
        prompt_hash = payload_sha256(payload)
        input_price = self.ledger.input_price_per_1m
        output_price = self.ledger.output_price_per_1m
        cost_upper = None
        if input_price is not None and output_price is not None:
            input_upper = len(canonical_json_bytes(messages))
            cost_upper = (
                input_upper * input_price + self.max_output_tokens * output_price
            ) / 1_000_000.0
        for attempt in range(self.max_retries + 1):
            index = self.ledger.begin(
                self.transport.model, self.transport.backend, prompt_hash
            )
            started = self.clock()
            result: TransportResult | None = None
            try:
                result = self.transport(payload, self.timeout)
                budget_event = getattr(self.transport, "last_budget_event", None)
                if budget_event is not None:
                    self.ledger.records[index].update(budget_event)
                body = result.body
                choices = body.get("choices")
                if not isinstance(choices, list) or not choices:
                    raise LLMResponseError("missing response choices")
                message = choices[0].get("message", {})
                parsed = _parse_decision(message.get("content"))
                input_tokens, output_tokens, total_tokens = _usage(body)
                response_model = (
                    body.get("model")
                    if isinstance(body.get("model"), str)
                    else self.transport.model
                )
                request_id = body.get("id") or result.headers.get("x-request-id")
                self.ledger.finish(
                    index,
                    status="SUCCESS",
                    latency_seconds=self.clock() - started,
                    response_model=response_model,
                    request_id=str(request_id) if request_id is not None else None,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_upper_usd=cost_upper,
                    transport_sent=True,
                )
                self.ledger.enforce_cost_limit()
                return LLMDecision(
                    **parsed,
                    model=response_model,
                    request_id=str(request_id) if request_id is not None else None,
                    prompt_sha256=prompt_hash,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    latency_seconds=max(0.0, self.clock() - started),
                )
            except Exception as error:
                budget_event = getattr(self.transport, "last_budget_event", None)
                if budget_event is not None:
                    self.ledger.records[index].update(budget_event)
                if self.ledger.records[index]["status"] == "PENDING":
                    input_tokens = output_tokens = total_tokens = None
                    response_model = None
                    request_id = None
                    if result is not None:
                        try:
                            input_tokens, output_tokens, total_tokens = _usage(
                                result.body
                            )
                        except LLMResponseError:
                            input_tokens = output_tokens = total_tokens = None
                        response_model = (
                            result.body.get("model")
                            if isinstance(result.body.get("model"), str)
                            else self.transport.model
                        )
                        request_id = result.body.get("id") or result.headers.get(
                            "x-request-id"
                        )
                    self.ledger.finish(
                        index,
                        status="ERROR",
                        latency_seconds=self.clock() - started,
                        response_model=response_model,
                        request_id=str(request_id) if request_id is not None else None,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                        cost_upper_usd=cost_upper,
                        transport_sent=not isinstance(
                            error, (LLMBudgetExceeded, LLMCostLimitExceeded)
                        ),
                        error=error,
                    )
                retryable = isinstance(error, (TransportError, LLMResponseError)) and (
                    not isinstance(error, TransportError) or error.retryable
                )
                if attempt >= self.max_retries or not retryable:
                    raise
                retry_after = (
                    error.retry_after if isinstance(error, TransportError) else 0.0
                )
                self.sleep_fn(min(2.0, max(0.1 * (2**attempt), retry_after)))
        raise LLMResponseError("unreachable response state")


def real_configuration_missing(require_pricing: bool = True) -> list[str]:
    """Report missing real-Canary configuration names without reading secret values."""
    checks = {
        "API_KEY": bool(
            os.environ.get("D094_LLM_API_KEY")
            or os.environ.get("DEEPSEEK_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        ),
        "BASE_URL": bool(
            os.environ.get("D094_LLM_BASE_URL")
            or os.environ.get("DEEPSEEK_BASE_URL")
            or os.environ.get("OPENAI_BASE_URL")
            or os.environ.get("OPENAI_API_BASE")
        ),
        "MODEL": bool(
            os.environ.get("D094_LLM_MODEL")
            or os.environ.get("DEEPSEEK_MODEL")
            or os.environ.get("OPENAI_MODEL")
            or os.environ.get("OPENAI_MODEL_NAME")
        ),
    }
    missing = [name for name, present in checks.items() if not present]
    if require_pricing:
        for name in ("D094_LLM_INPUT_COST_PER_1M", "D094_LLM_OUTPUT_COST_PER_1M"):
            raw = os.environ.get(name)
            if raw is None:
                missing.append(name)
                continue
            try:
                valid = math.isfinite(float(raw)) and float(raw) >= 0.0
            except ValueError:
                valid = False
            if not valid:
                missing.append(name)
    return missing


__all__ = [
    "LLMBudgetExceeded",
    "LLMClient",
    "LLMConfigurationError",
    "LLMCostLimitExceeded",
    "LLMDecision",
    "LLMResponseError",
    "MockTransport",
    "OpenAICompatibleTransport",
    "TransportError",
    "TransportResult",
    "prompt_template_sha256",
    "real_configuration_missing",
]
