"""D-094 R3/R3.1 fair five-arm execution with preflight and protected final budgets."""
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

from d094_adaptive_evolution import AdaptiveNSGAII
from d094_agent import LLMAgent
from d094_behavior import behavior_representation
from d094_budget import ReservedBudget, ReservedBudgetTransport
from d094_evaluator import (
    EpisodeRecord,
    evaluate_episodes,
    objective_vector,
    population_diversity,
)
from d094_evolution import Candidate, feasible_pareto
from d094_feedback_evolution import classify_failures
from d094_genome import FIXED_GENOME, AgentGenome, genome_sha256
from d094_ledger import ExecutionLedger, payload_sha256, verify_execution_ledger
from d094_llm_client import LLMClient, real_configuration_missing
from d094_r3_tasks import r3_manifest, r3_tasks
from d094_tasks import TrainRecoveryEnvironment


HERE = Path(__file__).resolve().parent
EVOLUTION_ARMS = {
    "B2": "standard",
    "B3": "feedback",
    "B4": "diversity",
    "B5": "combined",
}


@dataclasses.dataclass(frozen=True)
class R3Config:
    """Frozen original R3 scale, with an explicit smaller revision for budget safety."""

    task_ids: tuple[str, ...] = ()
    seeds: tuple[int, ...] = (201, 202)
    population_size: int = 4
    generations: int = 1
    max_concurrency: int = 4
    global_request_cap: int = 1500
    global_cost_cap: float = 0.5
    max_output_tokens: int = 128
    timeout_seconds: float = 20.0
    max_retries: int = 1
    max_message_bytes: int = 2000
    search_seed: int = 711
    revision: str = "R3"

    @classmethod
    def revised(cls) -> "R3Config":
        """Return R3.1: one task, two seeds, two per generation, no retries."""
        return cls(
            task_ids=("d094_r3_train_compensation_0",),
            population_size=2,
            max_retries=0,
            max_message_bytes=4096,
            revision="R3.1",
        )


def compute_budget_plan(
    config: R3Config,
    input_price_per_1m: float,
    output_price_per_1m: float,
) -> dict[str, Any]:
    """Compute per-arm request/cost upper bounds before any real call."""
    task_count = len(config.task_ids) or 6
    paired = task_count * len(config.seeds)
    initial_candidates = config.population_size
    offspring_candidates = config.population_size * config.generations
    candidates_per_arm = initial_candidates + offspring_candidates
    retry_multiplier = 1 + config.max_retries
    input_cost = config.max_message_bytes * input_price_per_1m / 1_000_000.0
    output_cost = config.max_output_tokens * output_price_per_1m / 1_000_000.0
    per_request_cost = input_cost + output_cost
    b1_base_requests = paired * FIXED_GENOME.max_plan_steps
    b1_requests = b1_base_requests * retry_multiplier
    initial_requests = paired * initial_candidates * 8 * retry_multiplier
    offspring_requests = paired * offspring_candidates * 8 * retry_multiplier
    search_requests_per_arm = initial_requests + offspring_requests
    final_base_requests = paired * 8
    final_requests_per_arm = final_base_requests * retry_multiplier
    total_requests = b1_requests + 4 * (
        search_requests_per_arm + final_requests_per_arm
    )
    pools = {
        "B1": {
            "request_count": b1_requests,
            "cost_usd": b1_requests * per_request_cost,
        },
        **{
            f"final:{arm}": {
                "request_count": final_requests_per_arm,
                "cost_usd": final_requests_per_arm * per_request_cost,
            }
            for arm in EVOLUTION_ARMS
        },
    }
    arm_plans = {
        "B1": {
            "evaluation_episodes": paired,
            "base_request_upper": b1_base_requests,
            "retry_request_upper": b1_base_requests * config.max_retries,
            "request_upper": b1_requests,
            "cost_upper_usd": b1_requests * per_request_cost,
            "protected": True,
        }
    }
    for arm in EVOLUTION_ARMS:
        arm_plans[arm] = {
            "initial_candidates": initial_candidates,
            "offspring_candidates": offspring_candidates,
            "final_candidates": 1,
            "initial_episodes": paired * initial_candidates,
            "offspring_episodes": paired * offspring_candidates,
            "final_episodes": paired,
            "initial_request_upper": initial_requests,
            "offspring_request_upper": offspring_requests,
            "duplicate_proposal_request_upper": 0,
            "final_request_upper": final_requests_per_arm,
            "retry_request_upper": paired * (candidates_per_arm + 1) * 8
            * config.max_retries,
            "search_request_upper": search_requests_per_arm,
            "initial_cost_upper_usd": initial_requests * per_request_cost,
            "offspring_cost_upper_usd": offspring_requests * per_request_cost,
            "final_cost_upper_usd": final_requests_per_arm * per_request_cost,
            "cost_upper_usd": (search_requests_per_arm + final_requests_per_arm)
            * per_request_cost,
            "final_protected": True,
        }
    total_cost = total_requests * per_request_cost
    return {
        "protocol": f"D094_{config.revision}_BUDGET",
        "task_count": task_count,
        "paired_episode_count": paired,
        "candidates_per_arm": candidates_per_arm,
        "input_price_per_1m_usd": input_price_per_1m,
        "output_price_per_1m_usd": output_price_per_1m,
        "max_input_bytes_per_request": config.max_message_bytes,
        "max_output_tokens_per_request": config.max_output_tokens,
        "input_cost_upper_per_request_usd": input_cost,
        "output_cost_upper_per_request_usd": output_cost,
        "per_request_cost_upper_usd": per_request_cost,
        "B1_request_upper": b1_requests,
        "search_request_upper_per_arm": search_requests_per_arm,
        "final_request_upper_per_arm": final_requests_per_arm,
        "total_request_upper": total_requests,
        "total_cost_upper_usd": total_cost,
        "planned_episode_count": paired + 4 * (paired * candidates_per_arm + paired),
        "protected_pools": pools,
        "arm_plans": arm_plans,
        "search_cost_upper_usd": 4 * search_requests_per_arm * per_request_cost,
        "fits": total_requests <= config.global_request_cap
        and total_cost <= config.global_cost_cap,
    }


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
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
    priced = all(record["cost_usd"] is not None for record in sent)
    priced_upper = all(record.get("cost_upper_usd") is not None for record in sent)
    return {
        "raw_request_records": len(records),
        "real_transport_attempts": len(sent),
        "input_tokens": sum(record["input_tokens"] or 0 for record in sent),
        "output_tokens": sum(record["output_tokens"] or 0 for record in sent),
        "cost_usd": sum(record["cost_usd"] for record in sent) if priced else None,
        "cost_upper_usd": sum(record["cost_upper_usd"] for record in sent)
        if priced_upper
        else None,
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in sent),
    }


def _delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for field in (
        "task_success_rate",
        "recovery_success_rate",
        "constraint_violation",
        "harm",
        "tool_cost",
        "input_tokens",
        "output_tokens",
        "token_cost_usd",
        "token_cost_upper_usd",
        "latency_seconds",
        "behavior_diversity",
    ):
        result[field] = (
            second[field] - first[field]
            if first[field] is not None and second[field] is not None
            else None
        )
    return result


def run_r3(
    outdir: Path,
    config: R3Config = R3Config(),
    client_factory: Callable[[], LLMClient] | None = None,
    preflight_only: bool = False,
) -> dict[str, Any]:
    """Run the five-arm protocol, or stop before transport for preflight/gates."""
    outdir = Path(outdir)
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("R3 output directory must be empty")
    outdir.mkdir(parents=True, exist_ok=True)
    factory = LLMClient.from_env if client_factory is None else client_factory
    prototype = factory()
    if (
        prototype.transport.backend == "openai-compatible"
        and real_configuration_missing(require_pricing=True)
    ):
        raise ValueError("incomplete real R3 environment")
    if (
        prototype.transport.backend == "openai-compatible"
        and prototype.transport.model != "deepseek-flash"
    ):
        summary = {
            "protocol": f"D094_{config.revision}_TRAIN",
            "status": "BLOCKED_MODEL",
            "model": prototype.transport.model,
            "required_model": "deepseek-flash",
            "actual_episode_count": 0,
        }
        _write_json(outdir / "summary.json", summary)
        return summary
    if prototype.ledger.cost_unknown:
        raise ValueError("R3 requires explicit token prices")
    manifest = r3_manifest(config.task_ids, config.revision)
    _write_json(outdir / "train_manifest.json", manifest)
    plan = compute_budget_plan(
        config,
        prototype.ledger.input_price_per_1m,
        prototype.ledger.output_price_per_1m,
    )
    _write_json(outdir / "budget_plan.json", plan)
    source_names = (
        "d094_adaptive_evolution.py",
        "d094_agent.py",
        "d094_behavior.py",
        "d094_budget.py",
        "d094_diversity.py",
        "d094_evaluator.py",
        "d094_evolution.py",
        "d094_feedback_evolution.py",
        "d094_genome.py",
        "d094_ledger.py",
        "d094_llm_client.py",
        "d094_prompts.py",
        "d094_r3_tasks.py",
        "d094_tasks.py",
        "run_d094_r3.py",
    )
    lock = {
        "protocol": f"D094_{config.revision}_TRAIN",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "backend": prototype.transport.backend,
        "model": prototype.transport.model,
        "temperature": 0.0,
        "thinking": {"type": "disabled"},
        "config": dataclasses.asdict(config),
        "train_manifest_sha256": manifest["manifest_sha256"],
        "budget_plan_sha256": hashlib.sha256(
            (outdir / "budget_plan.json").read_bytes()
        ).hexdigest(),
        "source_files": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in source_names
        },
    }
    _write_json(outdir / "execution_lock.json", lock)
    if not plan["fits"] or preflight_only:
        summary = {
            "protocol": f"D094_{config.revision}_TRAIN",
            "status": "BLOCKED_BUDGET" if not plan["fits"] else "PREFLIGHT_PASS",
            "actual_episode_count": 0,
            "budget": {
                "request_count": 0,
                "sent_request_count": 0,
                "cost_usd": 0.0,
                "backend": prototype.transport.backend,
            },
            "budget_plan_sha256": lock["budget_plan_sha256"],
            "scientific_scope": (
                "No API request was sent because the frozen design is not budget-safe"
                if not plan["fits"]
                else "Preflight only; no API request or episode was executed"
            ),
        }
        _write_json(outdir / "summary.json", summary)
        return summary

    budget = ReservedBudget(
        config.global_cost_cap,
        prototype.ledger.input_price_per_1m,
        prototype.ledger.output_price_per_1m,
        max_requests=config.global_request_cap,
    )
    for pool, reservation in plan["protected_pools"].items():
        budget.reserve(pool, reservation["cost_usd"], reservation["request_count"])

    selected_tasks = list(r3_tasks())
    if config.task_ids:
        selected_tasks = [
            task for task in selected_tasks if task.task_id in config.task_ids
        ]
    archive_by_arm: dict[str, list[dict[str, Any]]] = {}
    episodes_count = 0
    started = time.perf_counter()
    all_rows: list[dict[str, Any]] = []

    try:
        with (outdir / "episodes.jsonl").open(
            "x", encoding="utf-8", newline="\n"
        ) as episode_output:

            def evaluate(genome: AgentGenome, arm: str, phase: str):
                nonlocal episodes_count
                pool_name = (
                    "search"
                    if phase == "search"
                    else ("B1" if arm == "B1" else f"final:{arm}")
                )
                with ThreadPoolExecutor(max_workers=config.max_concurrency) as pool:
                    futures = [
                        pool.submit(
                            _episode,
                            task,
                            seed,
                            genome,
                            arm,
                            phase,
                            pool_name,
                            config,
                            factory,
                            budget,
                            outdir,
                        )
                        for task in selected_tasks
                        for seed in config.seeds
                    ]
                    rows = [future.result() for future in futures]
                rows.sort(
                    key=lambda row: (row["payload"]["task_id"], row["payload"]["seed"])
                )
                for row in rows:
                    episode_output.write(
                        json.dumps(
                            row["payload"],
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                            allow_nan=False,
                        )
                        + "\n"
                    )
                    episodes_count += 1
                    all_rows.append(row)
                episode_output.flush()
                metrics = evaluate_episodes([row["record"] for row in rows])
                behavior_events = []
                for row in rows:
                    behavior_events.extend(row["payload"]["events"])
                behavior = behavior_representation(
                    behavior_events, agent_status="MULTI_EPISODE"
                )
                failure_profile = classify_failures([row["payload"] for row in rows])
                execution_errors = sum(
                    row["payload"]["execution_error"] for row in rows
                )
                candidate = Candidate(
                    genome=genome,
                    objectives=objective_vector(metrics),
                    constraint_violation=metrics.constraint_violation,
                    phenotype_hash=behavior["canonical_sha256"],
                    execution_errors=execution_errors,
                    behavior=behavior,
                    failure_profile=failure_profile,
                )
                entry = {
                    "arm": arm,
                    "phase": phase,
                    "genome": genome.to_dict(),
                    "genome_sha256": genome_sha256(genome),
                    "candidate": dataclasses.asdict(candidate),
                    "metrics": dataclasses.asdict(metrics),
                    "execution_errors": execution_errors,
                    "episode_count": len(rows),
                    "per_seed": _per_seed(rows),
                    "usage": _usage(rows),
                    "hash_chain_valid": all(
                        row["payload"]["hash_chain_valid"] for row in rows
                    ),
                    "episode_ids": [row["payload"]["episode_id"] for row in rows],
                }
                return candidate, entry

            b1_candidate, b1_entry = evaluate(FIXED_GENOME, "B1", "fixed")
            arms = {"B1": b1_entry}
            per_seed = {"B1": b1_entry["per_seed"]}
            evolution_files = {}
            for arm, mode in EVOLUTION_ARMS.items():
                archive: list[dict[str, Any]] = []
                optimizer = AdaptiveNSGAII(mode)

                def search_evaluator(genome: AgentGenome) -> Candidate:
                    candidate, entry = evaluate(genome, arm, "search")
                    archive.append(entry)
                    return candidate

                optimizer.optimize(
                    search_evaluator,
                    config.population_size,
                    config.generations,
                    config.search_seed,
                )
                archive_by_arm[arm] = archive
                _write_json(outdir / f"evolution_{arm}.json", optimizer.ledger)
                _write_json(outdir / f"archive_{arm}.json", archive)
                evolution_files[arm] = f"evolution_{arm}.json"
                candidates = [
                    Candidate(
                        genome=AgentGenome(**entry["genome"]),
                        objectives=tuple(entry["candidate"]["objectives"]),
                        constraint_violation=entry["candidate"]["constraint_violation"],
                        phenotype_hash=entry["candidate"]["phenotype_hash"],
                        execution_errors=entry["candidate"]["execution_errors"],
                    )
                    for entry in archive
                ]
                front = feasible_pareto(candidates)
                selected = (
                    min(
                        front,
                        key=lambda candidate: (
                            candidate.objectives,
                            candidate.genome_id,
                        ),
                    )
                    if front
                    else None
                )
                final_entry = None
                if selected is not None:
                    _candidate, final_entry = evaluate(selected.genome, arm, "final")
                search_rows = [
                    row
                    for row in all_rows
                    if row["payload"]["arm"] == arm
                    and row["payload"]["phase"] == "search"
                ]
                final_rows = [
                    row
                    for row in all_rows
                    if row["payload"]["arm"] == arm
                    and row["payload"]["phase"] == "final"
                ]
                combined_rows = search_rows + final_rows
                execution_errors = sum(
                    row["payload"]["execution_error"] for row in combined_rows
                )
                entry = {
                    "arm": arm,
                    "mode": mode,
                    "selected_genome_sha256": None
                    if selected is None
                    else selected.genome_id,
                    "search_episode_count": len(search_rows),
                    "final_episode_count": len(final_rows),
                    "execution_errors": execution_errors,
                    "hash_chain_valid": all(
                        row["payload"]["hash_chain_valid"] for row in combined_rows
                    ),
                    "metrics": None if final_entry is None else final_entry["metrics"],
                    "per_seed": None
                    if final_entry is None
                    else final_entry["per_seed"],
                    "usage": _usage(combined_rows),
                    "search_unique_genomes": len(archive),
                    "pareto_front": [candidate.genome_id for candidate in front],
                    "population_diversity": population_diversity(
                        [AgentGenome(**entry["genome"]) for entry in archive],
                        [entry["candidate"]["phenotype_hash"] for entry in archive],
                    ),
                    "variation_count": sum(
                        event["event_type"] == "variation" for event in optimizer.ledger
                    ),
                    "duplicate_proposal_count": sum(
                        event["event_type"] == "duplicate_proposal"
                        for event in optimizer.ledger
                    ),
                }
                arms[arm] = entry
                if final_entry is not None:
                    per_seed[arm] = final_entry["per_seed"]
            comparisons = {}
            for label, first, second in (
                ("B3_minus_B2", "B2", "B3"),
                ("B4_minus_B2", "B2", "B4"),
                ("B5_minus_B3", "B3", "B5"),
                ("B5_minus_B4", "B4", "B5"),
            ):
                if (
                    arms[first]["metrics"] is not None
                    and arms[second]["metrics"] is not None
                ):
                    comparisons[label] = _delta(
                        arms[first]["metrics"], arms[second]["metrics"]
                    )
            per_seed_comparisons = {}
            for label, first, second in (
                ("B3_minus_B2", "B2", "B3"),
                ("B4_minus_B2", "B2", "B4"),
                ("B5_minus_B3", "B3", "B5"),
                ("B5_minus_B4", "B4", "B5"),
            ):
                if first in per_seed and second in per_seed:
                    per_seed_comparisons[label] = {
                        seed: _delta(per_seed[first][seed], per_seed[second][seed])
                        for seed in per_seed[first]
                        if seed in per_seed[second]
                    }
            execution_errors = sum(entry["execution_errors"] for entry in arms.values())
            invalid_final = any(
                arm != "B1"
                and (
                    entry["final_episode_count"]
                    != len(selected_tasks) * len(config.seeds)
                    or entry["metrics"] is None
                )
                for arm, entry in arms.items()
            )
            budget_snapshot = budget.snapshot()
            if budget_snapshot["over_budget"]:
                status = "INVALID_BUDGET"
            elif budget_snapshot["cost_unknown"]:
                status = "INVALID_COST_ACCOUNTING"
            elif execution_errors:
                status = "INVALID_EPISODES"
            elif invalid_final:
                status = "NO_FEASIBLE_CANDIDATE"
            else:
                status = "COMPLETED"
            summary = {
                "protocol": f"D094_{config.revision}_TRAIN",
                "status": status,
                "scientific_scope": "Small exploratory Train-only mechanism comparison; not confirmatory evidence",
                "backend": prototype.transport.backend,
                "model": prototype.transport.model,
                "config": dataclasses.asdict(config),
                "arms": arms,
                "per_seed": per_seed,
                "comparisons": comparisons,
                "per_seed_comparisons": per_seed_comparisons,
                "budget": {**budget_snapshot, "backend": prototype.transport.backend},
                "budget_plan_sha256": lock["budget_plan_sha256"],
                "execution_lock_sha256": hashlib.sha256(
                    (outdir / "execution_lock.json").read_bytes()
                ).hexdigest(),
                "actual_episode_count": episodes_count,
                "planned_episode_count": plan["planned_episode_count"],
                "hash_chain_valid": all(
                    row["payload"]["hash_chain_valid"] for row in all_rows
                ),
                "evolution_files": evolution_files,
                "wall_seconds": time.perf_counter() - started,
            }
            _write_json(outdir / "summary.json", summary)
            return summary
    except Exception as error:
        failure = {
            "protocol": f"D094_{config.revision}_TRAIN",
            "status": "INVALID",
            "error_type": type(error).__name__,
            "error": str(error)[:240],
            "actual_episode_count": episodes_count,
            "budget": {**budget.snapshot(), "backend": prototype.transport.backend},
            "partial_arms": list(archive_by_arm),
        }
        _write_json(outdir / "failure.json", failure)
        _write_json(outdir / "summary.json", failure)
        return failure


def _episode(
    task,
    seed: int,
    genome: AgentGenome,
    arm: str,
    phase: str,
    pool_name: str,
    config: R3Config,
    factory: Callable[[], LLMClient],
    budget: ReservedBudget,
    outdir: Path,
) -> dict[str, Any]:
    environment = TrainRecoveryEnvironment(task, seed)
    client = factory()
    client.max_retries = min(client.max_retries, config.max_retries)
    client.timeout = min(client.timeout, config.timeout_seconds)
    client.max_output_tokens = min(client.max_output_tokens, config.max_output_tokens)
    client.max_message_bytes = config.max_message_bytes
    client.ledger.max_requests = max(
        1, genome.max_plan_steps * (1 + config.max_retries)
    )
    client.ledger.max_cost_usd = min(client.ledger.max_cost_usd, 0.05)
    client.transport = ReservedBudgetTransport(client.transport, budget, pool_name)
    episode_id = payload_sha256(
        {
            "arm": arm,
            "phase": phase,
            "task_id": task.task_id,
            "seed": seed,
            "genome_sha256": genome_sha256(genome),
        }
    )
    trace_path = outdir / "traces" / f"{episode_id}.jsonl"
    result = LLMAgent(client, genome.to_agent_config(), ledger_path=trace_path).run(
        task.goal, environment
    )
    trace_events = [
        json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
    ]
    chain_valid = verify_execution_ledger(trace_events)
    records = client.ledger.records
    sent_records = [
        record for record in records if record.get("transport_sent") is not False
    ]
    metric = EpisodeRecord(
        task_success=environment.task_success(),
        recovery_success=environment.task_success(),
        constraint_violation=result.constraint_violations,
        harm=result.harm,
        tool_cost=result.tool_cost,
        input_tokens=sum(record["input_tokens"] or 0 for record in sent_records),
        output_tokens=sum(record["output_tokens"] or 0 for record in sent_records),
        token_cost_usd=client.ledger.total_cost_usd,
        latency_seconds=sum(
            record["latency_seconds"] or 0.0 for record in sent_records
        ),
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
        or not chain_valid
    )
    payload = {
        "episode_id": episode_id,
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
        "request_ledger": records,
        "final_public_observation": result.final_public_observation,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "trace_path": str(trace_path.relative_to(outdir)),
        "hash_chain_valid": chain_valid,
        "api_attempt_count": result.api_attempt_count,
    }
    return {"record": metric, "payload": payload}


def main() -> None:
    """Preflight or execute R3 through the same reviewed budgeted entry point."""
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--execute-real", action="store_true")
    action.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--outdir", type=Path, default=HERE / "results" / "r3_real")
    parser.add_argument("--revised", action="store_true")
    args = parser.parse_args()
    missing = real_configuration_missing(require_pricing=True)
    if missing:
        result = {
            "status": "BLOCKED_CONFIGURATION",
            "missing_configuration": missing,
            "actual_episode_count": 0,
        }
        args.outdir.mkdir(parents=True, exist_ok=True)
        _write_json(args.outdir / "summary.json", result)
    else:
        result = run_r3(
            args.outdir,
            R3Config.revised() if args.revised else R3Config(),
            preflight_only=args.preflight_only,
        )
    print(
        json.dumps(
            {
                "status": result["status"],
                "episodes": result.get("actual_episode_count", 0),
                "budget": result.get("budget"),
            }
        )
    )


if __name__ == "__main__":
    main()
