"""D-094 multi-turn LLM and deterministic-rule agents with a guarded tool gateway."""
from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Callable, Protocol

from d094_ledger import ExecutionLedger, canonical_json_bytes, sanitize_public
from d094_llm_client import LLMClient, LLMDecision
from d094_prompts import assert_public_input


class ToolValidationError(ValueError):
    """Raised when tool arguments violate their public JSON Schema."""


@dataclasses.dataclass(frozen=True)
class ToolSpec:
    """Public tool metadata and execution semantics."""

    name: str
    description: str
    parameters_schema: dict[str, Any]
    kind: str = "normal"
    dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.name
            or not self.description
            or self.kind not in {"normal", "verify", "compensate"}
        ):
            raise ValueError("invalid tool specification")
        if any(
            not isinstance(dependency, str) or not dependency
            for dependency in self.dependencies
        ):
            raise ValueError("invalid tool dependency")

    def to_public_dict(self) -> dict[str, Any]:
        """Return the allowlisted tool catalog exposed to the LLM."""
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class ToolResult:
    """Deterministic environment result and metric deltas."""

    success: bool
    observation: dict[str, Any]
    done: bool
    constraint_violation: int = 0
    harm: float = 0.0
    cost: float = 0.0


@dataclasses.dataclass
class AgentRunResult:
    """Auditable terminal result without hidden model reasoning."""

    status: str
    decision_source: str
    llm_decision_count: int
    api_attempt_count: int
    constraint_violations: int
    harm: float
    tool_cost: float
    events: list[dict[str, Any]]
    final_public_observation: dict[str, Any]


class AgentEnvironment(Protocol):
    """Public deterministic environment contract used by both agent arms."""

    def public_observation(self) -> dict[str, Any]:
        ...

    def available_tools(self) -> list[ToolSpec]:
        ...

    def review_call(
        self, tool: ToolSpec, arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        ...

    def authorize(self, tool: ToolSpec, arguments: dict[str, Any]) -> tuple[bool, str]:
        ...

    def execute(self, tool: ToolSpec, arguments: dict[str, Any]) -> ToolResult:
        ...

    def task_success(self) -> bool:
        ...


def _matches_type(value: Any, expected: str) -> bool:
    checks = {
        "object": lambda: isinstance(value, dict),
        "array": lambda: isinstance(value, list),
        "string": lambda: isinstance(value, str),
        "integer": lambda: type(value) is int,
        "number": lambda: type(value) in {int, float},
        "boolean": lambda: type(value) is bool,
        "null": lambda: value is None,
    }
    if expected not in checks:
        raise ToolValidationError("unsupported schema type")
    return checks[expected]()


def validate_arguments(schema: dict[str, Any], value: Any) -> None:
    """Validate the self-contained JSON Schema subset accepted by the gateway."""
    if "$ref" in schema:
        raise ToolValidationError("external schema references are not allowed")
    if "enum" in schema and value not in schema["enum"]:
        raise ToolValidationError("value is outside the schema enum")
    expected = schema.get("type")
    if isinstance(expected, list):
        if not any(_matches_type(value, item) for item in expected):
            raise ToolValidationError("value does not match schema types")
    elif isinstance(expected, str) and not _matches_type(value, expected):
        raise ToolValidationError("value does not match schema type")
    if isinstance(value, dict):
        required = schema.get("required", [])
        if any(not isinstance(key, str) for key in required):
            raise ToolValidationError("invalid required schema")
        if any(key not in value for key in required):
            raise ToolValidationError("missing required tool argument")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            raise ToolValidationError("invalid properties schema")
        if schema.get("additionalProperties") is False and any(
            key not in properties for key in value
        ):
            raise ToolValidationError("additional tool argument is forbidden")
        for key, item in value.items():
            if key in properties:
                validate_arguments(properties[key], item)
    if isinstance(value, list):
        if "items" in schema:
            for item in value:
                validate_arguments(schema["items"], item)
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get(
            "maxItems", len(value)
        ):
            raise ToolValidationError("array size is outside the schema")
    if isinstance(value, str) and not schema.get("minLength", 0) <= len(
        value
    ) <= schema.get("maxLength", len(value)):
        raise ToolValidationError("string length is outside the schema")
    if type(value) in {int, float}:
        if "minimum" in schema and value < schema["minimum"]:
            raise ToolValidationError("number is below the schema minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ToolValidationError("number is above the schema maximum")


def _rule_decision(payload: dict[str, Any]) -> LLMDecision:
    required = {
        "action",
        "tool_name",
        "tool_arguments",
        "rationale",
        "verification_required",
    }
    if set(payload) != required:
        raise ValueError("rule policy decision schema mismatch")
    return LLMDecision(
        **payload,
        model="deterministic-rule",
        request_id=None,
        prompt_sha256="RULE_BASED",
        input_tokens=0,
        output_tokens=0,
        latency_seconds=0.0,
    )


class _AgentLoop:
    def __init__(
        self, agent_config: dict[str, Any], ledger_path: Path | None = None
    ) -> None:
        self.agent_config = dict(agent_config)
        self.execution_ledger = (
            None if ledger_path is None else ExecutionLedger(ledger_path)
        )
        self.events: list[dict[str, Any]] = []
        self.constraint_violations = 0
        self.harm = 0.0
        self.tool_cost = 0.0
        self.failed = False
        self.last_failed_action: dict[str, Any] | None = None

    def _record(self, event_type: str, payload: Any) -> None:
        safe = sanitize_public(payload)
        event = {"event_type": event_type, "payload": safe}
        self.events.append(event)
        if self.execution_ledger is not None:
            self.execution_ledger.append(event_type, safe)

    @staticmethod
    def _bounded_memory(memory: dict[str, Any]) -> dict[str, Any]:
        """Bound only the model-facing projection, never the raw event ledger."""
        bounded = {**memory, "truncated": False}
        if "entries" in memory:
            bounded["entries"] = list(memory["entries"])
            items = bounded["entries"]
        else:
            bounded["summary"] = {
                **memory["summary"],
                "tool_names": list(memory["summary"]["tool_names"]),
            }
            items = bounded["summary"]["tool_names"]
        while items and len(canonical_json_bytes(bounded)) > 512:
            items.pop(0)
            bounded["truncated"] = True
        if len(canonical_json_bytes(bounded)) > 512:
            items.clear()
            bounded["truncated"] = True
        return bounded

    def _memory(self) -> dict[str, Any]:
        mode = self.agent_config["memory_mode"]
        if mode == "recent_trajectory":
            entries = []
            for event in self.events[-3:]:
                if event["event_type"] == "decision":
                    payload = event["payload"]
                    fields = (
                        "action",
                        "tool_name",
                        "tool_arguments",
                        "rationale",
                        "verification_required",
                    )
                    projected = {field: payload[field] for field in fields}
                    projected["rationale"] = projected["rationale"].encode("utf-8")[
                        :80
                    ].decode("utf-8", "ignore")
                    event = {"event_type": "decision", "payload": projected}
                entries.append(event)
            return self._bounded_memory(
                {"kind": "recent_trajectory", "entries": entries}
            )
        if mode == "structured_failures":
            failures = [
                event
                for event in self.events
                if event["event_type"] == "tool_rejected"
                or (
                    event["event_type"] == "tool_result"
                    and not event["payload"]["success"]
                )
            ]
            return self._bounded_memory(
                {
                    "kind": "structured_failures",
                    "entries": failures[-3:],
                    "total_failure_count": len(failures),
                }
            )
        decisions = [
            event["payload"]
            for event in self.events
            if event["event_type"] == "decision"
        ]
        failures = sum(event["event_type"] == "tool_rejected" for event in self.events)
        return self._bounded_memory(
            {
                "kind": "compressed_summary",
                "summary": {
                    "event_count": len(self.events),
                    "failure_count": failures,
                    "tool_names": [
                        event["tool_name"]
                        for event in decisions
                        if event["action"] == "tool_call"
                    ],
                },
            }
        )

    def _reflection(self) -> dict[str, Any] | None:
        trigger = self.agent_config["reflection_trigger"]
        if trigger == "after_failure" and self.failed:
            return {
                "reflection_request": "previous_action_failed",
                "failed_action": self.last_failed_action,
            }
        if trigger == "after_subtask":
            results = [
                event for event in self.events if event["event_type"] == "tool_result"
            ]
            if results:
                return {
                    "reflection_request": "subtask_completed",
                    "tool_name": results[-1]["payload"]["tool_name"],
                }
        return None

    def _public_tools(self, environment: AgentEnvironment) -> list[ToolSpec]:
        tools = list(environment.available_tools())
        if self.agent_config["recovery_mode"] == "dependency_aware":
            completed = set(environment.public_observation().get("completed_tools", []))
            tools = [
                tool for tool in tools if set(tool.dependencies).issubset(completed)
            ]
        return tools

    def _observation(self, task: str, environment: AgentEnvironment) -> dict[str, Any]:
        observation = {
            "task": task,
            "public_state": environment.public_observation(),
            "memory": self._memory(),
            "directives": {
                "planning_mode": self.agent_config["planning_mode"],
                "recovery_mode": self.agent_config["recovery_mode"],
            },
        }
        reflection = self._reflection()
        if reflection is not None:
            observation.update(reflection)
        return observation

    def _reject(self, code: str, tool_name: str | None) -> None:
        self.constraint_violations += 1
        self.failed = True
        observation = {"error": code, "tool_name": tool_name, "executed": False}
        self.last_failed_action = observation
        self._record(
            "tool_rejected",
            {"tool_name": tool_name, "observation": observation, "success": False},
        )

    def _execute(
        self,
        decision: LLMDecision,
        tools: list[ToolSpec],
        environment: AgentEnvironment,
    ) -> None:
        matching = [tool for tool in tools if tool.name == decision.tool_name]
        if len(matching) != 1:
            self._reject("UNKNOWN_OR_UNAVAILABLE_TOOL", decision.tool_name)
            return
        tool = matching[0]
        try:
            validate_arguments(tool.parameters_schema, decision.tool_arguments)
        except ToolValidationError:
            self._reject("TOOL_SCHEMA_REJECTED", tool.name)
            return
        recovery = self.agent_config["recovery_mode"]
        if self.failed and recovery == "verify_priority" and tool.kind != "verify":
            self._reject("RECOVERY_VERIFICATION_REQUIRED", tool.name)
            return
        if (
            self.failed
            and recovery == "compensation_priority"
            and tool.kind != "compensate"
        ):
            self._reject("RECOVERY_COMPENSATION_REQUIRED", tool.name)
            return
        if self.agent_config["tool_call_guard"] == "post_plan_verify":
            allowed, reason = environment.review_call(tool, decision.tool_arguments)
            if not allowed:
                self._reject(reason, tool.name)
                return
        allowed, reason = environment.authorize(tool, decision.tool_arguments)
        if not allowed:
            self._reject(reason, tool.name)
            return
        try:
            result = environment.execute(tool, decision.tool_arguments)
            assert_public_input(result.observation)
        except Exception:
            self._reject("ENVIRONMENT_EXECUTION_OR_VISIBILITY_ERROR", tool.name)
            return
        self.tool_cost += result.cost
        self.harm += result.harm
        self.constraint_violations += result.constraint_violation
        self.failed = not result.success
        observation = (
            result.observation
            if result.success
            else {"tool_result": result.observation}
        )
        if not result.success:
            self.last_failed_action = {
                "tool_name": tool.name,
                "observation": observation,
            }
        self._record(
            "tool_result",
            {
                "tool_name": tool.name,
                "observation": observation,
                "success": result.success,
                "done": result.done,
                "constraint_violation": result.constraint_violation,
                "harm": result.harm,
                "cost": result.cost,
            },
        )

    def _run(
        self,
        task: str,
        environment: AgentEnvironment,
        decider: Callable[[dict[str, Any], list[dict[str, Any]]], LLMDecision],
        source: str,
        api_attempts: Callable[[], int],
    ) -> AgentRunResult:
        self.failed = bool(environment.public_observation().get("last_failure", False))
        status = "MAX_STEPS"
        for _step in range(self.agent_config["max_plan_steps"]):
            tools = self._public_tools(environment)
            public_tools = [tool.to_public_dict() for tool in tools]
            observation = self._observation(task, environment)
            try:
                decision = decider(observation, public_tools)
            except Exception as error:
                self._record(
                    "llm_error" if source == "llm" else "rule_error",
                    {"error_type": type(error).__name__},
                )
                status = "LLM_ERROR" if source == "llm" else "RULE_ERROR"
                break
            self._record("decision", dataclasses.asdict(decision))
            if decision.action == "finish":
                status = (
                    "COMPLETED" if environment.task_success() else "PREMATURE_FINISH"
                )
                break
            self._execute(decision, tools, environment)
            if environment.task_success():
                status = "COMPLETED"
                break
            latest = self.events[-1]
            if latest["event_type"] == "tool_result" and latest["payload"]["done"]:
                status = "TERMINATED_BY_ENVIRONMENT"
                break
        result = AgentRunResult(
            status=status,
            decision_source=source,
            llm_decision_count=sum(
                event["event_type"] == "decision" for event in self.events
            )
            if source == "llm"
            else 0,
            api_attempt_count=api_attempts(),
            constraint_violations=self.constraint_violations,
            harm=self.harm,
            tool_cost=self.tool_cost,
            events=self.events,
            final_public_observation=sanitize_public(environment.public_observation()),
        )
        self._record(
            "run_finished",
            {"status": status, "constraint_violations": self.constraint_violations},
        )
        result.events = self.events
        return result


class LLMAgent(_AgentLoop):
    """An agent that requires a real LLM decision on every planning turn."""

    def __init__(
        self,
        client: LLMClient,
        agent_config: dict[str, Any],
        ledger_path: Path | None = None,
    ) -> None:
        super().__init__(agent_config, ledger_path)
        self.client = client
        self._initial_attempts = len(client.ledger.records)

    def run(self, task: str, environment: AgentEnvironment) -> AgentRunResult:
        """Run the public observe-LLM-validate-execute loop to its terminal state."""
        return self._run(
            task,
            environment,
            lambda observation, tools: self.client.generate_action(
                observation, tools, self.agent_config
            ),
            "llm",
            lambda: sum(
                record.get("transport_sent") is not False
                for record in self.client.ledger.records[self._initial_attempts :]
            ),
        )


class RuleBasedAgent(_AgentLoop):
    """B0 adapter around an existing deterministic policy, with no LLM client."""

    def __init__(
        self,
        policy: Callable[[dict[str, Any]], dict[str, Any]],
        agent_config: dict[str, Any],
        ledger_path: Path | None = None,
    ) -> None:
        super().__init__(agent_config, ledger_path)
        self.policy = policy

    def run(self, task: str, environment: AgentEnvironment) -> AgentRunResult:
        """Run a deterministic policy through the same guarded environment."""
        return self._run(
            task,
            environment,
            lambda observation, _tools: _rule_decision(self.policy(observation)),
            "rule",
            lambda: 0,
        )
