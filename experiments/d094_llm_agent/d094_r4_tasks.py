"""Fresh D-094 R4 Train-only tasks, isolation proofs and local reachability gates.

No Validation/Test definition is imported or read.  R4 task specifications were
frozen from R3.1 failure analysis, not from held-out outcomes.
"""
from __future__ import annotations

import dataclasses
from typing import Any

from d094_agent import AgentRunResult, RuleBasedAgent
from d094_genome import FIXED_GENOME
from d094_ledger import payload_sha256
from d094_r3_tasks import r3_tasks
from d094_tasks import TrainRecoveryEnvironment, TrainTask, rule_policy, train_tasks


R4_SEEDS = (301, 302)
R4_MAX_PLAN_STEPS = 5
R4_PROTOCOL = "D094_R4_TRAIN_V1"


def r4_tasks() -> tuple[TrainTask, ...]:
    """Return two new, deterministic task specifications with frozen identities."""
    return (
        TrainTask(
            task_id="d094_r4_train_compensation_unverified_0",
            goal=(
                "R4 public recovery case: compensate the permanently failed route "
                "without a verification prerequisite, then complete safely."
            ),
            family="compensation_unverified",
            requires_verification=False,
            requires_compensation=True,
            retry_failures=0,
            retry_never=True,
            seed_jitter=False,
        ),
        TrainTask(
            task_id="d094_r4_train_transient_single_0",
            goal=(
                "R4 public recovery case: recover from exactly one deterministic "
                "transient failure with bounded retries, then complete safely."
            ),
            family="transient_single",
            requires_verification=False,
            requires_compensation=False,
            retry_failures=1,
            retry_never=False,
            seed_jitter=False,
        ),
    )


def task_sha256(task: TrainTask) -> str:
    """Hash every canonical task field, not merely its public name."""
    return payload_sha256(dataclasses.asdict(task))


def fresh_train_isolation() -> dict[str, Any]:
    """Prove bidirectional ID/specification separation from historical Train only."""
    fresh = r4_tasks()
    historical = (*train_tasks(), *r3_tasks())
    fresh_ids = {task.task_id for task in fresh}
    historical_ids = {task.task_id for task in historical}
    fresh_specs = {task_sha256(task) for task in fresh}
    historical_specs = {task_sha256(task) for task in historical}
    if len(fresh_ids) != len(fresh) or len(fresh_specs) != len(fresh):
        raise ValueError("duplicate R4 task identity or specification")
    r4_to_historical = sorted(fresh_ids & historical_ids)
    historical_to_r4 = sorted(historical_ids & fresh_ids)
    spec_forward = sorted(fresh_specs & historical_specs)
    spec_reverse = sorted(historical_specs & fresh_specs)
    if r4_to_historical or historical_to_r4 or spec_forward or spec_reverse:
        raise ValueError("R4 Fresh Train overlaps a historical Train task")
    return {
        "status": "PASS",
        "scope": "HISTORICAL_TRAIN_IDS_AND_COMPLETE_CANONICAL_SPECIFICATIONS",
        "fresh_task_count": len(fresh),
        "historical_train_task_count": len(historical),
        "r4_to_historical_id_matches": r4_to_historical,
        "historical_to_r4_id_matches": historical_to_r4,
        "r4_to_historical_specification_matches": spec_forward,
        "historical_to_r4_specification_matches": spec_reverse,
        "fresh_task_sha256": {task.task_id: task_sha256(task) for task in fresh},
        "held_out_overlap_check": "NOT_CHECKED_VALIDATION_TEST_ACCESS_FORBIDDEN",
        "validation_or_test_files_read": False,
        "independence_limit": (
            "Exact separation from historical Train is proven; semantic separation "
            "from inaccessible held-out tasks is not claimed."
        ),
    }


def _inspect_then_rule(observation: dict[str, Any]) -> dict[str, Any]:
    if not observation["public_state"]["state"]["inspected"]:
        return {
            "action": "tool_call",
            "tool_name": "inspect_state",
            "tool_arguments": {},
            "rationale": "Inspect public state before recovery.",
            "verification_required": False,
        }
    return rule_policy(observation)


def validate_reachability() -> dict[str, Any]:
    """Execute frozen public paths through the real local environment, without an LLM."""
    reports = []
    for task in r4_tasks():
        expected = (
            ["inspect_state", "compensate_primary", "complete_task"]
            if task.requires_compensation
            else ["inspect_state", "retry_primary", "retry_primary", "complete_task"]
        )
        for seed in R4_SEEDS:
            environment = TrainRecoveryEnvironment(task, seed)
            result: AgentRunResult = RuleBasedAgent(
                _inspect_then_rule, FIXED_GENOME.to_agent_config()
            ).run(task.goal, environment)
            if result.status != "COMPLETED" or not environment.task_success():
                raise ValueError(f"R4 reachability failed: {task.task_id}:{seed}")
            if environment.executed != expected:
                raise ValueError("R4 reachability path changed")
            if len(expected) > R4_MAX_PLAN_STEPS or result.constraint_violations:
                raise ValueError("R4 path exceeds common step budget or violates constraints")
            reports.append(
                {
                    "task_id": task.task_id,
                    "seed": seed,
                    "required_path": expected,
                    "executed_path": environment.executed,
                    "required_steps": len(expected),
                    "max_plan_steps": R4_MAX_PLAN_STEPS,
                    "remaining_step_allowance": R4_MAX_PLAN_STEPS - len(expected),
                    "task_success": environment.task_success(),
                    "agent_status": result.status,
                    "constraint_violation": result.constraint_violations,
                    "harm": result.harm,
                    "llm_requests": 0,
                }
            )
    return {
        "status": "PASS",
        "scope": "LOCAL_DETERMINISTIC_ENVIRONMENT_ONLY_NOT_REAL_LLM_PERFORMANCE",
        "common_eligible_pool_max_plan_steps": R4_MAX_PLAN_STEPS,
        "pool_size": 216,
        "planning_mutation_changes_max_plan_steps": False,
        "step_increase_is_not_innovation_credit": True,
        "episodes": reports,
        "api_used": False,
    }


def r4_manifest() -> dict[str, Any]:
    """Build an immutable-content manifest including per-task canonical hashes."""
    tasks = []
    for task in r4_tasks():
        row = dataclasses.asdict(task)
        row["task_sha256"] = task_sha256(task)
        tasks.append(row)
    manifest = {
        "protocol": R4_PROTOCOL,
        "split": "train",
        "scenario_count": len(tasks),
        "seeds": list(R4_SEEDS),
        "common_max_plan_steps": R4_MAX_PLAN_STEPS,
        "eligible_genome_pool_size": 216,
        "task_generation_rule": (
            "Two explicitly frozen TrainTask specifications; no outcome-driven "
            "generator, no hidden-label input and no held-out read."
        ),
        "validation_included": False,
        "test_included": False,
        "tasks": tasks,
        "fresh_train_isolation": fresh_train_isolation(),
        "reachability": validate_reachability(),
    }
    manifest["manifest_sha256"] = payload_sha256(manifest)
    return manifest
