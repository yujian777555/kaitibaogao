"""D-094 R4 preflight and Mock-only protocol execution.

There is deliberately no real-API execution flag in this module.  A future
independently reviewed revision may add one only after explicit user approval.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from d094_agent import LLMAgent
from d094_behavior import behavior_representation
from d094_budget import ReservedBudget, ReservedBudgetTransport
from d094_evaluator import EpisodeRecord, evaluate_episodes, objective_vector
from d094_evolution import Candidate, feasible_pareto
from d094_feedback_evolution import classify_failures
from d094_genome import FIXED_GENOME, AgentGenome, genome_sha256
from d094_ledger import payload_sha256, verify_execution_ledger
from d094_llm_client import LLMClient
from d094_r4_analysis import COMPARISONS
from d094_r4_credit import (
    PairedCreditNSGAII,
    PairedEpisode,
    make_paired_evaluation,
    select_final_candidate,
)
from d094_r4_statistics import R4_BOOTSTRAP_REPLICATES, R4_STATISTICAL_SEED
from d094_r4_tasks import R4_MAX_PLAN_STEPS, R4_SEEDS, r4_manifest, r4_tasks
from d094_tasks import TrainRecoveryEnvironment


HERE = Path(__file__).resolve().parent
EVOLUTION_ARMS = {"B2": "standard", "B3": "paired_credit", "B4": "failure_feedback"}
FROZEN_EVOLUTION_ARMS = {
    "B2": "standard",
    "B3": "paired_credit",
    "B4": "failure_feedback",
}
FROZEN_TASK_IDS = (
    "d094_r4_train_compensation_unverified_0",
    "d094_r4_train_transient_single_0",
)
FROZEN_MANIFEST_SHA256 = "e8412c74c33faf7a56195d685d49080b5669dbe46efd3ae1ab6dee88917b5bff"
EXECUTION_LOCK_VERSION = "D094_R4_EXECUTION_LOCK_V2"
SOURCE_NAMES = (
    "d094_agent.py",
    "d094_behavior.py",
    "d094_budget.py",
    "d094_evaluator.py",
    "d094_evolution.py",
    "d094_feedback_evolution.py",
    "d094_genome.py",
    "d094_ledger.py",
    "d094_llm_client.py",
    "d094_prompts.py",
    "d094_r3_tasks.py",
    "d094_r4_analysis.py",
    "d094_r4_credit.py",
    "d094_r4_statistics.py",
    "d094_r4_tasks.py",
    "d094_tasks.py",
    "run_d094_r4.py",
)


@dataclasses.dataclass(frozen=True)
class R4Config:
    """Frozen R4 scale, prices and request controls; all values are pre-real-run."""

    seeds: tuple[int, ...] = R4_SEEDS
    population_size: int = 2
    generations: int = 1
    max_concurrency: int = 4
    global_request_cap: int = 320
    global_cost_cap: float = 0.442368
    max_output_tokens: int = 128
    timeout_seconds: float = 20.0
    max_retries: int = 0
    max_message_bytes: int = 4096
    search_seed: int = 711
    model: str = "deepseek-flash"
    input_price_per_1m: float = 0.3
    output_price_per_1m: float = 1.2
    requests_per_episode_upper: int = 5


FROZEN_CONFIG = R4Config()


def _validate_frozen_config(config: R4Config) -> None:
    """Reject every caller/task/arm deviation before output or client construction."""
    if type(config) is not R4Config:
        raise ValueError("R4 frozen config mismatch: config must be R4Config")
    for field in dataclasses.fields(R4Config):
        actual = getattr(config, field.name)
        expected = getattr(FROZEN_CONFIG, field.name)
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError(
                f"R4 frozen config mismatch: {field.name} expected {expected!r}, got {actual!r}"
            )
        if field.name == "seeds" and any(type(seed) is not int for seed in actual):
            raise ValueError("R4 frozen config mismatch: seeds must contain integers")
    tasks = r4_tasks()
    task_ids = tuple(task.task_id for task in tasks)
    if task_ids != FROZEN_TASK_IDS:
        raise ValueError(
            f"R4 frozen Train task IDs mismatch: expected {FROZEN_TASK_IDS!r}, got {task_ids!r}"
        )
    manifest = r4_manifest()
    if manifest["manifest_sha256"] != FROZEN_MANIFEST_SHA256:
        raise ValueError("R4 frozen Train manifest canonical SHA-256 mismatch")
    if manifest["common_max_plan_steps"] != R4_MAX_PLAN_STEPS or R4_MAX_PLAN_STEPS != 5:
        raise ValueError("R4 common eligible pool must use exactly five plan steps")
    if type(EVOLUTION_ARMS) is not dict or EVOLUTION_ARMS != FROZEN_EVOLUTION_ARMS:
        raise ValueError(
            f"R4 frozen arms mismatch: expected B1 Fixed and {FROZEN_EVOLUTION_ARMS!r}"
        )
    if FIXED_GENOME != AgentGenome() or FIXED_GENOME.max_plan_steps != 5:
        raise ValueError("R4 B1 must remain the frozen five-step Fixed genome")


def _statistical_method_lock() -> dict[str, Any]:
    labels = tuple(label for label, _first, _second in COMPARISONS)
    return {
        "version": "D094_R4_STATISTICS_V1",
        "ordered_final_units": "sorted_(task_id,seed)",
        "independent_unit_count": 4,
        "sign_flip_pattern_count": 16,
        "sign_patterns_are_not_independent_units": True,
        "bootstrap_replicates": R4_BOOTSTRAP_REPLICATES,
        "bootstrap_base_seed": R4_STATISTICAL_SEED,
        "comparison_order": list(labels),
        "comparison_seed_offsets": {label: offset for offset, label in enumerate(labels)},
        "holm_family": list(labels),
        "minimum_meaningful_effect": 0.25,
        "primary_comparison": "B3_minus_B2",
        "interpretation": "SMALL_SAMPLE_EXPLORATORY_MECHANISM_COMPARISON",
    }


def _r3_1_empirical_basis() -> dict[str, Any]:
    """Use only the already completed R3.1 aggregate; never read held-out data."""
    episodes = 42
    requests = 169
    input_tokens = 127148
    output_tokens = 8090
    return {
        "source": "results/r3_1_real historical completed Train aggregate",
        "episode_count": episodes,
        "request_count": requests,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": 0.0478524,
        "requests_per_episode": requests / episodes,
        "input_tokens_per_request": input_tokens / requests,
        "output_tokens_per_request": output_tokens / requests,
        "failed_request_count": 0,
        "failed_request_cost_usd": 0.0,
        "http_retry_policy": "max_retries=0; request-ledger attempt is episode-local ordinal",
        "same_prompt_repeat_records": 6,
        "same_prompt_repeat_fraction": 6 / 169,
        "canonical_message_bytes_available": False,
        "message_byte_policy": "4096-byte frozen cap audited; historical maximum not reconstructed",
    }


def compute_budget_plan(config: R4Config = R4Config()) -> dict[str, Any]:
    """Calculate empirical estimates separately from conservative before-send bounds."""
    _validate_frozen_config(config)
    task_count = len(r4_tasks())
    paired = task_count * len(config.seeds)
    candidates = config.population_size * (1 + config.generations)
    search_episodes_per_arm = paired * candidates
    b1_requests = paired * config.requests_per_episode_upper
    search_requests = search_episodes_per_arm * config.requests_per_episode_upper
    final_requests = paired * config.requests_per_episode_upper
    total_requests = b1_requests + len(EVOLUTION_ARMS) * (search_requests + final_requests)
    input_cost = config.max_message_bytes * config.input_price_per_1m / 1_000_000.0
    output_cost = config.max_output_tokens * config.output_price_per_1m / 1_000_000.0
    request_cost = input_cost + output_cost
    total_cost = total_requests * request_cost
    total_episodes = paired + len(EVOLUTION_ARMS) * (search_episodes_per_arm + paired)
    protected = {
        "B1": {"request_count": b1_requests, "cost_usd": b1_requests * request_cost},
        **{
            f"final:{arm}": {
                "request_count": final_requests,
                "cost_usd": final_requests * request_cost,
            }
            for arm in EVOLUTION_ARMS
        },
    }
    search_pools = {
        f"search:{arm}": {
            "request_count": search_requests,
            "cost_usd": search_requests * request_cost,
        }
        for arm in EVOLUTION_ARMS
    }
    arm_plans = {
        "B1": {
            "evaluation_episodes": paired,
            "request_upper": b1_requests,
            "cost_upper_usd": b1_requests * request_cost,
            "protected": True,
        }
    }
    for arm in EVOLUTION_ARMS:
        arm_plans[arm] = {
            "initial_candidates": config.population_size,
            "offspring_candidates": config.population_size * config.generations,
            "final_candidates": 1,
            "search_episodes": search_episodes_per_arm,
            "final_episodes": paired,
            "search_request_upper": search_requests,
            "final_request_upper": final_requests,
            "duplicate_proposal_request_upper": 0,
            "search_cost_upper_usd": search_requests * request_cost,
            "final_cost_upper_usd": final_requests * request_cost,
            "search_budget_pool": f"search:{arm}",
            "final_budget_pool": f"final:{arm}",
            "final_protected": True,
        }
    basis = _r3_1_empirical_basis()
    empirical_requests = total_episodes * basis["requests_per_episode"]
    empirical_input = empirical_requests * basis["input_tokens_per_request"]
    empirical_output = empirical_requests * basis["output_tokens_per_request"]
    empirical_cost = (
        empirical_input * config.input_price_per_1m
        + empirical_output * config.output_price_per_1m
    ) / 1_000_000.0
    plan = {
        "protocol": "D094_R4_BUDGET_V1",
        "scope": "PRE_REAL_RUN_PLAN_NOT_AN_API_INVOICE",
        "task_count": task_count,
        "paired_episode_count": paired,
        "candidates_per_evolution_arm": candidates,
        "max_input_bytes_per_request": config.max_message_bytes,
        "max_output_tokens_per_request": config.max_output_tokens,
        "input_price_per_1m_usd": config.input_price_per_1m,
        "output_price_per_1m_usd": config.output_price_per_1m,
        "input_cost_upper_per_request_usd": input_cost,
        "output_cost_upper_per_request_usd": output_cost,
        "per_request_cost_upper_usd": request_cost,
        "B1_request_upper": b1_requests,
        "search_request_upper_per_arm": search_requests,
        "final_request_upper_per_arm": final_requests,
        "total_request_upper": total_requests,
        "total_cost_upper_usd": total_cost,
        "planned_episode_count": total_episodes,
        "protected_pools": protected,
        "search_pools": search_pools,
        "arm_plans": arm_plans,
        "r3_1_empirical_basis": basis,
        "r4_empirical_estimate": {
            "episode_count": total_episodes,
            "request_count": empirical_requests,
            "input_tokens": empirical_input,
            "output_tokens": empirical_output,
            "cost_usd": empirical_cost,
            "warning": "Historical-distribution planning estimate, not a cap or predicted result",
        },
        "independent_recalculation_requires_api": False,
        "fits": total_requests <= config.global_request_cap
        and total_cost <= config.global_cost_cap,
    }
    if total_episodes != 64 or total_requests != 320:
        raise ValueError("R4 frozen scale mismatch: expected 64 episodes and 320 requests")
    if not math.isclose(total_cost, 0.442368, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("R4 frozen cost upper mismatch: expected 0.442368 USD")
    if set(protected) != {"B1", "final:B2", "final:B3", "final:B4"}:
        raise ValueError("R4 B1/final protected pool allocation changed")
    for pool, reservation in protected.items():
        if reservation["request_count"] != 20 or not math.isclose(
            reservation["cost_usd"], 0.027648, rel_tol=0.0, abs_tol=1e-15
        ):
            raise ValueError(f"R4 protected pool budget mismatch: {pool}")
    if set(search_pools) != {"search:B2", "search:B3", "search:B4"}:
        raise ValueError("R4 search pools must be independently allocated to B2/B3/B4")
    for pool, reservation in search_pools.items():
        if reservation["request_count"] != 80 or not math.isclose(
            reservation["cost_usd"], 0.110592, rel_tol=0.0, abs_tol=1e-15
        ):
            raise ValueError(f"R4 independent search pool budget mismatch: {pool}")
    if plan["fits"] is not True:
        raise ValueError("R4 frozen budget plan does not fit the frozen global caps")
    return plan


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _per_seed(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        str(seed): dataclasses.asdict(
            evaluate_episodes(
                [row["record"] for row in rows if row["payload"]["seed"] == seed]
            )
        )
        for seed in sorted({row["payload"]["seed"] for row in rows})
    }


def _usage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record for row in rows for record in row["payload"]["request_ledger"]]
    sent = [record for record in records if record.get("transport_sent") is not False]
    return {
        "raw_request_records": len(records),
        "transport_attempts": len(sent),
        "input_tokens": sum(record["input_tokens"] or 0 for record in sent),
        "output_tokens": sum(record["output_tokens"] or 0 for record in sent),
        "cost_usd": sum(record["cost_usd"] or 0.0 for record in sent)
        if all(record["cost_usd"] is not None for record in sent)
        else None,
        "cost_upper_usd": sum(record["cost_upper_usd"] or 0.0 for record in sent)
        if all(record["cost_upper_usd"] is not None for record in sent)
        else None,
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in sent),
        "backend": "mock",
    }


def _delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    return {
        key: second[key] - first[key]
        for key in (
            "task_success_rate",
            "recovery_success_rate",
            "constraint_violation",
            "harm",
            "tool_cost",
            "input_tokens",
            "output_tokens",
            "token_cost_usd",
            "latency_seconds",
            "behavior_diversity",
        )
    }


def _execution_lock(
    manifest: dict[str, Any],
    plan_path: Path,
    config: R4Config,
    backend: str,
    created_utc: str | None = None,
) -> dict[str, Any]:
    _validate_frozen_config(config)
    return {
        "protocol": "D094_R4_TRAIN_V1",
        "execution_lock_version": EXECUTION_LOCK_VERSION,
        "created_utc": created_utc
        or datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "backend": backend,
        "real_api_execution_available": False,
        "required_future_real_model": config.model,
        "temperature": 0.0,
        "thinking": {"type": "disabled"},
        "config": dataclasses.asdict(config),
        "train_manifest_sha256": manifest["manifest_sha256"],
        "budget_plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "statistical_method": _statistical_method_lock(),
        "source_files": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in SOURCE_NAMES
        },
        "protocol_documents": {
            name: hashlib.sha256((HERE.parents[1] / name).read_bytes()).hexdigest()
            for name in (
                "D094_R3_1_DEEP_ANALYSIS.md",
                "D094_R4_ALGORITHM_DESIGN.md",
                "D094_R4_PREREGISTRATION.md",
                "D094_R4_BUDGET_ANALYSIS.md",
            )
        },
    }


def _first_lock_difference(expected: Any, actual: Any, path: str = "") -> str | None:
    if type(expected) is not type(actual):
        return f"{path or 'execution_lock'}: type {type(actual).__name__} != {type(expected).__name__}"
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            missing = sorted(set(expected) - set(actual))
            extra = sorted(set(actual) - set(expected))
            return f"{path or 'execution_lock'}: missing={missing}, extra={extra}"
        for key in expected:
            difference = _first_lock_difference(
                expected[key], actual[key], f"{path}.{key}" if path else key
            )
            if difference is not None:
                return difference
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return f"{path}: list length {len(actual)} != {len(expected)}"
        for index, (wanted, got) in enumerate(zip(expected, actual)):
            difference = _first_lock_difference(wanted, got, f"{path}[{index}]")
            if difference is not None:
                return difference
        return None
    if expected != actual:
        return f"{path}: expected {expected!r}, got {actual!r}"
    return None


def verify_execution_lock(lock_path: Path) -> dict[str, Any]:
    """Rebuild V2 from current inputs and fail on the first changed lock field."""
    lock_path = Path(lock_path)
    raw = lock_path.read_bytes()
    actual = json.loads(raw.decode("utf-8"))
    if actual.get("execution_lock_version") != EXECUTION_LOCK_VERSION:
        raise ValueError("execution lock mismatch: execution_lock_version")
    config_data = dict(actual["config"])
    config_data["seeds"] = tuple(config_data["seeds"])
    config = R4Config(**config_data)
    expected = _execution_lock(
        r4_manifest(),
        lock_path.parent / "budget_plan.json",
        config,
        actual["backend"],
        created_utc=actual["created_utc"],
    )
    expected_json = json.loads(
        json.dumps(expected, ensure_ascii=False, sort_keys=True, allow_nan=False)
    )
    difference = _first_lock_difference(expected_json, actual)
    if difference is not None:
        raise ValueError(f"execution lock mismatch: {difference}")
    return {
        "status": "PASS",
        "execution_lock_version": EXECUTION_LOCK_VERSION,
        "execution_lock_sha256": hashlib.sha256(raw).hexdigest(),
        "train_manifest_sha256": actual["train_manifest_sha256"],
        "statistics_source_sha256": actual["source_files"]["d094_r4_statistics.py"],
        "analysis_entry_source_sha256": actual["source_files"]["d094_r4_analysis.py"],
        "source_file_count": len(actual["source_files"]),
    }


def run_r4(
    outdir: Path,
    config: R4Config = R4Config(),
    client_factory: Callable[[], LLMClient] | None = None,
    preflight_only: bool = True,
) -> dict[str, Any]:
    """Preflight with zero transport, or execute the identical protocol with Mock only."""
    _validate_frozen_config(config)
    outdir = Path(outdir)
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("R4 output directory must be empty")
    outdir.mkdir(parents=True, exist_ok=True)
    manifest = r4_manifest()
    _write_json(outdir / "train_manifest.json", manifest)
    plan = compute_budget_plan(config)
    _write_json(outdir / "budget_plan.json", plan)
    if not plan["fits"]:
        summary = {
            "protocol": "D094_R4_TRAIN_V1",
            "status": "BLOCKED_BUDGET",
            "actual_episode_count": 0,
            "api_used": False,
        }
        _write_json(outdir / "summary.json", summary)
        return summary
    if preflight_only:
        lock = _execution_lock(manifest, outdir / "budget_plan.json", config, "none")
        lock_path = outdir / "execution_lock.json"
        _write_json(lock_path, lock)
        summary = {
            "protocol": "D094_R4_TRAIN_V1",
            "execution_lock_version": EXECUTION_LOCK_VERSION,
            "status": "PREFLIGHT_PASS",
            "real_execution_status": "NOT_APPROVED_AND_NOT_IMPLEMENTED",
            "scientific_scope": "Preflight only; zero API requests and zero episodes",
            "actual_episode_count": 0,
            "api_used": False,
            "backend": "none",
            "planned_episode_count": plan["planned_episode_count"],
            "train_manifest_sha256": manifest["manifest_sha256"],
            "budget_plan_sha256": lock["budget_plan_sha256"],
            "execution_lock_sha256": hashlib.sha256(lock_path.read_bytes()).hexdigest(),
        }
        _write_json(outdir / "summary.json", summary)
        return summary
    if client_factory is None:
        raise ValueError("Mock client factory is required; real R4 execution is unavailable")
    prototype = client_factory()
    if prototype.transport.backend != "mock":
        raise ValueError("R4 pre-registration implementation permits Mock transport only")
    lock = _execution_lock(manifest, outdir / "budget_plan.json", config, "mock")
    _write_json(outdir / "execution_lock.json", lock)
    budget = ReservedBudget(
        config.global_cost_cap,
        config.input_price_per_1m,
        config.output_price_per_1m,
        max_requests=config.global_request_cap,
    )
    for reservations in (plan["protected_pools"], plan["search_pools"]):
        for pool, reservation in reservations.items():
            budget.reserve(pool, reservation["cost_usd"], reservation["request_count"])
    selected_tasks = list(r4_tasks())
    pair_keys = tuple((task.task_id, seed) for task in selected_tasks for seed in config.seeds)
    all_rows: list[dict[str, Any]] = []
    episodes_count = 0
    started = time.perf_counter()
    arms: dict[str, Any] = {}
    evolution_files = {}
    try:
        with (outdir / "episodes.jsonl").open("x", encoding="utf-8", newline="\n") as output:

            def evaluate(genome: AgentGenome, arm: str, phase: str):
                nonlocal episodes_count
                pool_name = (
                    f"search:{arm}"
                    if phase == "search"
                    else ("B1" if arm == "B1" else f"final:{arm}")
                )
                with ThreadPoolExecutor(max_workers=config.max_concurrency) as pool:
                    futures = [
                        pool.submit(
                            _episode, task, seed, genome, arm, phase, pool_name,
                            config, client_factory, budget, outdir,
                        )
                        for task in selected_tasks
                        for seed in config.seeds
                    ]
                    rows = [future.result() for future in futures]
                rows.sort(key=lambda row: (row["payload"]["task_id"], row["payload"]["seed"]))
                for row in rows:
                    output.write(json.dumps(row["payload"], ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
                    all_rows.append(row)
                    episodes_count += 1
                output.flush()
                metrics = evaluate_episodes([row["record"] for row in rows])
                behavior_events = [event for row in rows for event in row["payload"]["events"]]
                behavior = behavior_representation(behavior_events, agent_status="MULTI_EPISODE")
                failure_profile = classify_failures([row["payload"] for row in rows])
                candidate = Candidate(
                    genome=genome,
                    objectives=objective_vector(metrics),
                    constraint_violation=metrics.constraint_violation,
                    phenotype_hash=behavior["canonical_sha256"],
                    execution_errors=sum(row["payload"]["execution_error"] for row in rows),
                    behavior=behavior,
                    failure_profile=failure_profile,
                )
                paired_episodes = tuple(
                    PairedEpisode(
                        task_id=row["payload"]["task_id"],
                        seed=row["payload"]["seed"],
                        task_success=row["record"].task_success,
                        recovery_success=row["record"].recovery_success,
                        constraint_violation=row["record"].constraint_violation,
                        harm=row["record"].harm,
                        execution_error=row["payload"]["execution_error"],
                    )
                    for row in rows
                )
                paired = make_paired_evaluation(
                    genome,
                    paired_episodes,
                    tool_cost=metrics.tool_cost,
                    token_cost_upper_usd=metrics.token_cost_upper_usd,
                    latency_seconds=metrics.latency_seconds,
                    phenotype_hash=candidate.phenotype_hash,
                    failure_profile=failure_profile,
                )
                if paired.candidate.objectives != candidate.objectives:
                    raise ValueError("R4 candidate and paired-equality objectives differ")
                entry = {
                    "arm": arm,
                    "phase": phase,
                    "genome": genome.to_dict(),
                    "genome_sha256": genome_sha256(genome),
                    "candidate": dataclasses.asdict(candidate),
                    "metrics": dataclasses.asdict(metrics),
                    "execution_errors": candidate.execution_errors,
                    "episode_count": len(rows),
                    "per_seed": _per_seed(rows),
                    "per_task_seed": [
                        {"task_id": row["payload"]["task_id"], "seed": row["payload"]["seed"], **dataclasses.asdict(row["record"])}
                        for row in rows
                    ],
                    "usage": _usage(rows),
                    "hash_chain_valid": all(row["payload"]["hash_chain_valid"] for row in rows),
                    "episode_ids": [row["payload"]["episode_id"] for row in rows],
                }
                return paired, entry

            _b1, b1_entry = evaluate(FIXED_GENOME, "B1", "fixed")
            arms["B1"] = b1_entry
            for arm, mode in EVOLUTION_ARMS.items():
                archive = []
                optimizer = PairedCreditNSGAII(mode)

                def search_evaluator(genome: AgentGenome):
                    paired, entry = evaluate(genome, arm, "search")
                    archive.append(entry)
                    return paired

                optimizer.optimize(
                    search_evaluator,
                    config.population_size,
                    config.generations,
                    config.search_seed,
                    pair_keys,
                )
                selected = select_final_candidate([row.candidate for row in optimizer.archive])
                if selected is None:
                    raise ValueError(f"{arm} has no feasible final candidate")
                _final_candidate, final_entry = evaluate(selected.genome, arm, "final")
                search_rows = [row for row in all_rows if row["payload"]["arm"] == arm and row["payload"]["phase"] == "search"]
                final_rows = [row for row in all_rows if row["payload"]["arm"] == arm and row["payload"]["phase"] == "final"]
                front = feasible_pareto([row.candidate for row in optimizer.archive])
                arms[arm] = {
                    "arm": arm,
                    "mode": mode,
                    "selected_genome_sha256": selected.genome_id,
                    "selection_rule": "all_search_archive_feasible_first_front_min_objectives_then_genome_sha256",
                    "search_episode_count": len(search_rows),
                    "final_episode_count": len(final_rows),
                    "execution_errors": sum(row["payload"]["execution_error"] for row in search_rows + final_rows),
                    "hash_chain_valid": all(row["payload"]["hash_chain_valid"] for row in search_rows + final_rows),
                    "metrics": final_entry["metrics"],
                    "per_seed": final_entry["per_seed"],
                    "per_task_seed": final_entry["per_task_seed"],
                    "usage": _usage(search_rows + final_rows),
                    "search_unique_genomes": len(archive),
                    "pareto_front": [row.genome_id for row in front],
                    "variation_count": sum(row["event_type"] == "variation" for row in optimizer.ledger),
                    "duplicate_proposal_count": sum(row["event_type"] == "duplicate_proposal" for row in optimizer.ledger),
                    "credit_update_count": sum(row["event_type"] == "credit_update" for row in optimizer.ledger),
                    "feedback_update_count": sum(row["event_type"] == "feedback_update" for row in optimizer.ledger),
                }
                _write_json(outdir / f"evolution_{arm}.json", optimizer.ledger)
                _write_json(outdir / f"archive_{arm}.json", archive)
                _write_json(outdir / f"final_{arm}.json", final_entry)
                evolution_files[arm] = f"evolution_{arm}.json"
            snapshot = budget.snapshot()
            expected = plan["planned_episode_count"]
            execution_errors = sum(row["payload"]["execution_error"] for row in all_rows)
            if snapshot["over_budget"] or snapshot["cost_unknown"]:
                status = "INVALID_BUDGET"
            elif execution_errors or episodes_count != expected:
                status = "INVALID_EPISODES"
            else:
                status = "MOCK_COMPLETED"
            summary = {
                "protocol": "D094_R4_TRAIN_V1",
                "execution_lock_version": EXECUTION_LOCK_VERSION,
                "status": status,
                "scientific_scope": "MOCK_SOFTWARE_VALIDATION_ONLY_NOT_AGENT_PERFORMANCE_EVIDENCE",
                "backend": "mock",
                "real_api_used": False,
                "config": dataclasses.asdict(config),
                "arms": arms,
                "comparisons": {
                    label: _delta(arms[first]["metrics"], arms[second]["metrics"])
                    for label, first, second in COMPARISONS
                },
                "budget": snapshot,
                "search_pool_ledgers": {
                    pool: budget.pool_snapshot(pool) for pool in plan["search_pools"]
                },
                "actual_episode_count": episodes_count,
                "planned_episode_count": expected,
                "train_manifest_sha256": manifest["manifest_sha256"],
                "hash_chain_valid": all(row["payload"]["hash_chain_valid"] for row in all_rows),
                "evolution_files": evolution_files,
                "execution_lock_sha256": hashlib.sha256((outdir / "execution_lock.json").read_bytes()).hexdigest(),
                "wall_seconds": time.perf_counter() - started,
            }
            _write_json(outdir / "summary.json", summary)
            return summary
    except Exception as error:
        failure = {
            "protocol": "D094_R4_TRAIN_V1",
            "status": "INVALID",
            "error_type": type(error).__name__,
            "error": str(error)[:240],
            "actual_episode_count": episodes_count,
            "real_api_used": False,
            "budget": budget.snapshot(),
        }
        _write_json(outdir / "failure.json", failure)
        _write_json(outdir / "summary.json", failure)
        return failure


def _episode(
    task: Any,
    seed: int,
    genome: AgentGenome,
    arm: str,
    phase: str,
    pool_name: str,
    config: R4Config,
    factory: Callable[[], LLMClient],
    budget: ReservedBudget,
    outdir: Path,
) -> dict[str, Any]:
    if genome.max_plan_steps != 5:
        raise ValueError("R4 common eligible pool requires five plan steps")
    environment = TrainRecoveryEnvironment(task, seed)
    client = factory()
    if client.transport.backend != "mock":
        raise ValueError("only Mock transport is permitted")
    client.max_retries = 0
    client.timeout = min(client.timeout, config.timeout_seconds)
    client.max_output_tokens = min(client.max_output_tokens, config.max_output_tokens)
    client.max_message_bytes = config.max_message_bytes
    client.ledger.max_requests = config.requests_per_episode_upper
    client.ledger.max_cost_usd = min(client.ledger.max_cost_usd, 0.05)
    client.transport = ReservedBudgetTransport(client.transport, budget, pool_name)
    episode_id = payload_sha256({
        "protocol": "D094_R4_TRAIN_V1",
        "arm": arm,
        "phase": phase,
        "task_id": task.task_id,
        "seed": seed,
        "genome_sha256": genome_sha256(genome),
    })
    trace_path = outdir / "traces" / f"{episode_id}.jsonl"
    result = LLMAgent(client, genome.to_agent_config(), ledger_path=trace_path).run(task.goal, environment)
    trace_events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    chain_valid = verify_execution_ledger(trace_events)
    sent = [record for record in client.ledger.records if record.get("transport_sent") is not False]
    metric = EpisodeRecord(
        task_success=environment.task_success(),
        recovery_success=environment.task_success(),
        constraint_violation=result.constraint_violations,
        harm=result.harm,
        tool_cost=result.tool_cost,
        input_tokens=sum(record["input_tokens"] or 0 for record in sent),
        output_tokens=sum(record["output_tokens"] or 0 for record in sent),
        token_cost_usd=client.ledger.total_cost_usd,
        latency_seconds=sum(record["latency_seconds"] or 0.0 for record in sent),
        phenotype_hash=behavior_representation(
            result.events,
            agent_status=result.status,
            final_public_observation=result.final_public_observation,
        )["canonical_sha256"],
        token_cost_upper_usd=client.ledger.total_cost_upper_usd,
    )
    execution_error = (
        result.status in {"LLM_ERROR", "RULE_ERROR"}
        or result.api_attempt_count == 0
        or result.api_attempt_count > config.requests_per_episode_upper
        or not chain_valid
    )
    payload = {
        "episode_id": episode_id,
        "protocol": "D094_R4_TRAIN_V1",
        "arm": arm,
        "phase": phase,
        "task_id": task.task_id,
        "seed": seed,
        "genome": genome.to_dict(),
        "genome_sha256": genome_sha256(genome),
        "agent_status": result.status,
        "execution_error": execution_error,
        "metrics": dataclasses.asdict(metric),
        "events": result.events,
        "request_ledger": client.ledger.records,
        "final_public_observation": result.final_public_observation,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "trace_path": str(trace_path.relative_to(outdir)),
        "hash_chain_valid": chain_valid,
        "api_attempt_count": result.api_attempt_count,
        "real_api_used": False,
    }
    return {"record": metric, "payload": payload}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=HERE / "results" / "r4_preflight")
    args = parser.parse_args()
    result = run_r4(args.outdir, preflight_only=True)
    print(json.dumps({"status": result["status"], "episodes": result["actual_episode_count"], "api_used": False}))


if __name__ == "__main__":
    main()
