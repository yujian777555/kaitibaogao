"""Twelve independent D-094 Train recovery tasks and a strong deterministic baseline."""
from __future__ import annotations

import dataclasses
from typing import Any

from d094_agent import ToolResult, ToolSpec
from d094_ledger import payload_sha256


@dataclasses.dataclass(frozen=True)
class TrainTask:
    """Evaluator-owned task definition; hidden schedules never enter LLM input."""

    task_id: str
    goal: str
    family: str
    requires_verification: bool
    requires_compensation: bool
    retry_failures: int
    retry_never: bool
    seed_jitter: bool


def train_tasks() -> tuple[TrainTask, ...]:
    """Return the frozen, independent twelve-task Train grid."""
    tasks = []
    specifications = (
        ("verification", True, False, 0, False, False),
        ("transient", False, False, 1, False, True),
        ("compensation", True, True, 0, True, False),
        ("hybrid", True, False, 1, False, True),
    )
    goals = {
        "verification": "Verify the failed dependency, recover the primary route, and complete the task.",
        "transient": "Recover from the transient failure with bounded retries and complete the task.",
        "compensation": "Verify and compensate the permanently failed route, then complete the task.",
        "hybrid": "Verify the failure, handle bounded transient retries, and complete the task.",
    }
    for (
        family,
        requires_verification,
        requires_compensation,
        retries,
        never,
        jitter,
    ) in specifications:
        for ordinal in range(3):
            tasks.append(
                TrainTask(
                    task_id=f"d094_train_{family}_{ordinal}",
                    goal=goals[family] + f" Public case variant: {ordinal}.",
                    family=family,
                    requires_verification=requires_verification,
                    requires_compensation=requires_compensation,
                    retry_failures=retries,
                    retry_never=never,
                    seed_jitter=jitter,
                )
            )
    return tuple(tasks)


def train_manifest() -> dict[str, Any]:
    """Serialize the Train-only task manifest with an internal content hash."""
    tasks = [dataclasses.asdict(task) for task in train_tasks()]
    manifest = {
        "protocol": "D094_PHASE2_TRAIN_V1",
        "split": "train",
        "scenario_count": len(tasks),
        "validation_included": False,
        "test_included": False,
        "tasks": tasks,
    }
    manifest["manifest_sha256"] = payload_sha256(manifest)
    return manifest


class TrainRecoveryEnvironment:
    """Deterministic state, permission and outcome environment for D-094 Train."""

    def __init__(self, task: TrainTask, seed: int) -> None:
        self.task = task
        self.seed = seed
        jitter = (seed + len(task.task_id)) % 2 if task.seed_jitter else 0
        self.retry_failures_remaining = task.retry_failures + jitter
        self.inspected = False
        self.verified = False
        self.primary_recovered = False
        self.compensated = False
        self.completed = False
        self.last_failure = True
        self.last_observation: dict[str, Any] = {"status": "PRIMARY_FAILED"}
        self.executed: list[str] = []

    @property
    def completed_tools(self) -> set[str]:
        completed = set()
        if self.inspected:
            completed.add("inspect_state")
        if self.verified:
            completed.add("verify_state")
        if self.primary_recovered:
            completed.add("retry_primary")
        if self.compensated:
            completed.add("compensate_primary")
        if self.completed:
            completed.add("complete_task")
        return completed

    def public_observation(self) -> dict[str, Any]:
        """Expose only current public state, not task ID, family or future outcomes."""
        return {
            "state": {
                "inspected": self.inspected,
                "verified": self.verified,
                "primary_recovered": self.primary_recovered,
                "compensated": self.compensated,
                "completed": self.completed,
                "requires_verification": self.task.requires_verification,
                "requires_compensation": self.task.requires_compensation,
            },
            "last_observation": self.last_observation,
            "last_failure": self.last_failure,
            "completed_tools": sorted(self.completed_tools),
        }

    def available_tools(self) -> list[ToolSpec]:
        """Return public tools with dependency metadata used by dependency-aware genomes."""
        empty = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        verification_dependency = (
            ("verify_state",) if self.task.requires_verification else ()
        )
        recovery_dependency = (
            ("compensate_primary",)
            if self.task.requires_compensation
            else ("retry_primary",)
        )
        return [
            ToolSpec(
                "inspect_state", "Inspect public failure and prerequisite state", empty
            ),
            ToolSpec(
                "verify_state",
                "Verify the failed public dependency",
                empty,
                kind="verify",
            ),
            ToolSpec(
                "retry_primary",
                "Retry the primary route once per decision",
                empty,
                dependencies=verification_dependency,
            ),
            ToolSpec(
                "compensate_primary",
                "Compensate the failed route after required verification",
                empty,
                kind="compensate",
                dependencies=verification_dependency,
            ),
            ToolSpec(
                "complete_task",
                "Complete only after public recovery prerequisites hold",
                empty,
                dependencies=recovery_dependency,
            ),
        ]

    def _allowed(self, tool: ToolSpec) -> tuple[bool, str]:
        if self.completed:
            return False, "TASK_ALREADY_COMPLETED"
        if (
            tool.name in {"retry_primary", "compensate_primary"}
            and self.task.requires_verification
            and not self.verified
        ):
            return False, "VERIFICATION_REQUIRED"
        if tool.name == "complete_task":
            if self.task.requires_verification and not self.verified:
                return False, "VERIFICATION_REQUIRED"
            if self.task.requires_compensation and not self.compensated:
                return False, "COMPENSATION_REQUIRED"
            if not self.task.requires_compensation and not self.primary_recovered:
                return False, "PRIMARY_RECOVERY_REQUIRED"
        return True, "ALLOWED"

    def review_call(
        self, tool: ToolSpec, _arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        """Deterministically review public preconditions before authorization."""
        return self._allowed(tool)

    def authorize(self, tool: ToolSpec, _arguments: dict[str, Any]) -> tuple[bool, str]:
        """Apply final environment permissions; denied calls are never executed."""
        return self._allowed(tool)

    def execute(self, tool: ToolSpec, _arguments: dict[str, Any]) -> ToolResult:
        """Apply the seed-paired state transition and return a public observation."""
        allowed, reason = self._allowed(tool)
        if not allowed:
            return ToolResult(False, {"error": reason}, False, 1, 1.0, 0.0)
        self.executed.append(tool.name)
        success = True
        harm = 0.0
        cost = {
            "inspect_state": 0.2,
            "verify_state": 0.5,
            "retry_primary": 1.0,
            "compensate_primary": 2.0,
            "complete_task": 1.0,
        }[tool.name]
        if tool.name == "inspect_state":
            self.inspected = True
            observation = {
                "status": "INSPECTED",
                "requires_verification": self.task.requires_verification,
            }
        elif tool.name == "verify_state":
            self.verified = True
            observation = {"status": "VERIFIED"}
        elif tool.name == "retry_primary":
            if self.task.retry_never or self.retry_failures_remaining > 0:
                if not self.task.retry_never:
                    self.retry_failures_remaining -= 1
                success = False
                harm = 0.25
                observation = {
                    "status": "TRANSIENT_FAILED"
                    if not self.task.retry_never
                    else "PRIMARY_FAILED"
                }
            else:
                self.primary_recovered = True
                observation = {"status": "PRIMARY_RECOVERED"}
        elif tool.name == "compensate_primary":
            self.compensated = True
            observation = {"status": "COMPENSATED"}
        elif tool.name == "complete_task":
            self.completed = True
            observation = {"status": "COMPLETED"}
        else:
            raise ValueError("unknown tool")
        self.last_failure = not success
        self.last_observation = observation
        return ToolResult(success, observation, self.completed, 0, harm, cost)

    def task_success(self) -> bool:
        """Success requires the real terminal state, not an LLM finish claim."""
        return self.completed


def rule_policy(observation: dict[str, Any]) -> dict[str, Any]:
    """Strong deterministic B0 policy using only public state."""
    state = observation["public_state"]["state"]

    def act(name: str) -> dict[str, Any]:
        return {
            "action": "tool_call",
            "tool_name": name,
            "tool_arguments": {},
            "rationale": "Deterministic public-state recovery rule.",
            "verification_required": name == "verify_state",
        }

    if state["requires_verification"] and not state["verified"]:
        return act("verify_state")
    if state["requires_compensation"] and not state["compensated"]:
        return act("compensate_primary")
    if not state["requires_compensation"] and not state["primary_recovered"]:
        return act("retry_primary")
    return act("complete_task")
