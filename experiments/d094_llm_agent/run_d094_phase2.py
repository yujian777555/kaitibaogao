"""Execute the small paired D-094 B0/B1/B2 Train experiment with hard API caps."""
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

from d094_agent import LLMAgent, RuleBasedAgent
from d094_evaluator import (
    EpisodeRecord,
    EvaluationMetrics,
    evaluate_episodes,
    objective_vector,
    population_diversity,
)
from d094_evolution import Candidate, NSGAII, feasible_pareto
from d094_genome import AgentGenome, FIXED_GENOME, genome_sha256, phenotype_sha256
from d094_ledger import SharedBudget, SharedBudgetTransport, payload_sha256
from d094_llm_client import LLMClient, real_configuration_missing
from d094_tasks import (
    TrainRecoveryEnvironment,
    rule_policy,
    train_manifest,
    train_tasks,
)


HERE = Path(__file__).resolve().parent


@dataclasses.dataclass(frozen=True)
class Phase2Config:
    """Frozen small-scale exploratory search and execution configuration."""

    seeds: tuple[int, ...] = (101, 202, 303)
    population_size: int = 8
    generations: int = 3
    max_concurrency: int = 4
    global_request_cap: int = 4000
    global_cost_cap: float = 1.0
    max_output_tokens: int = 128
    timeout_seconds: float = 20.0

    def __post_init__(self) -> None:
        if not self.seeds or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("paired seeds must be nonempty and unique")
        if self.population_size < 2 or self.generations < 0:
            raise ValueError("invalid NSGA-II scale")
        if self.max_concurrency < 1 or self.global_request_cap <= 0:
            raise ValueError("invalid concurrency or request cap")
        if not math.isfinite(self.global_cost_cap) or self.global_cost_cap <= 0.0:
            raise ValueError("invalid global cost cap")


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _episode(
    arm: str,
    phase: str,
    task_index: int,
    seed: int,
    genome: AgentGenome,
    config: Phase2Config,
    client_factory: Callable[[], LLMClient] | None,
    shared: SharedBudget,
) -> dict[str, Any]:
    task = train_tasks()[task_index]
    environment = TrainRecoveryEnvironment(task, seed)
    client = None
    if arm == "B0":
        result = RuleBasedAgent(rule_policy, genome.to_agent_config()).run(
            task.goal, environment
        )
    else:
        client = client_factory()
        client.max_retries = min(client.max_retries, 1)
        client.timeout = min(client.timeout, config.timeout_seconds)
        client.max_output_tokens = min(
            client.max_output_tokens, config.max_output_tokens
        )
        client.ledger.max_requests = 2 * genome.max_plan_steps
        client.ledger.max_cost_usd = min(client.ledger.max_cost_usd, 0.05)
        client.transport = SharedBudgetTransport(client.transport, shared)
        result = LLMAgent(client, genome.to_agent_config()).run(task.goal, environment)
    records = [] if client is None else client.ledger.records
    input_tokens = sum(record["input_tokens"] or 0 for record in records)
    output_tokens = sum(record["output_tokens"] or 0 for record in records)
    latency = sum(record["latency_seconds"] or 0.0 for record in records)
    token_cost = 0.0 if client is None else client.ledger.total_cost_usd
    token_cost_upper = 0.0 if client is None else client.ledger.total_cost_upper_usd
    metric = EpisodeRecord(
        task_success=environment.task_success(),
        recovery_success=environment.task_success(),
        constraint_violation=result.constraint_violations,
        harm=result.harm,
        tool_cost=result.tool_cost,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        token_cost_usd=token_cost,
        latency_seconds=latency,
        phenotype_hash=phenotype_sha256(result.events),
        token_cost_upper_usd=token_cost_upper,
    )
    genome_hash = genome_sha256(genome)
    payload = {
        "episode_id": payload_sha256(
            {
                "arm": arm,
                "phase": phase,
                "task_id": task.task_id,
                "seed": seed,
                "genome_sha256": genome_hash,
            }
        ),
        "arm": arm,
        "phase": phase,
        "task_id": task.task_id,
        "seed": seed,
        "genome": genome.to_dict(),
        "genome_sha256": genome_hash,
        "agent_status": result.status,
        "execution_error": result.status in {"LLM_ERROR", "RULE_ERROR"},
        "metrics": dataclasses.asdict(metric),
        "events": result.events,
        "request_ledger": records,
        "final_public_observation": result.final_public_observation,
    }
    return {"record": metric, "payload": payload}


def _per_seed(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for seed in sorted({row["payload"]["seed"] for row in rows}):
        selected = [row["record"] for row in rows if row["payload"]["seed"] == seed]
        result[str(seed)] = dataclasses.asdict(evaluate_episodes(selected))
    return result


def _phase_usage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record for row in rows for record in row["payload"]["request_ledger"]]
    priced = all(record["cost_usd"] is not None for record in records)
    priced_upper = all(record.get("cost_upper_usd") is not None for record in records)
    return {
        "api_attempts": len(records),
        "input_tokens": sum(record["input_tokens"] or 0 for record in records),
        "output_tokens": sum(record["output_tokens"] or 0 for record in records),
        "cost_usd": sum(record["cost_usd"] for record in records) if priced else None,
        "cost_upper_usd": sum(record["cost_upper_usd"] for record in records)
        if priced_upper
        else None,
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in records),
    }


def _accumulate_usage(
    existing: dict[str, Any] | None, rows: list[dict[str, Any]]
) -> dict[str, Any]:
    current = _phase_usage(rows)
    if existing is None:
        return current
    result = {}
    for key in current:
        if key in {"cost_usd", "cost_upper_usd"} and (
            existing[key] is None or current[key] is None
        ):
            result[key] = None
        else:
            result[key] = existing[key] + current[key]
    return result


def _comparison(
    first: EvaluationMetrics, second: EvaluationMetrics
) -> dict[str, float | None]:
    """Return second-minus-first descriptive deltas, not confirmatory statistics."""
    return {
        "task_success_rate": second.task_success_rate - first.task_success_rate,
        "recovery_success_rate": second.recovery_success_rate
        - first.recovery_success_rate,
        "constraint_violation": second.constraint_violation
        - first.constraint_violation,
        "harm": second.harm - first.harm,
        "tool_cost": second.tool_cost - first.tool_cost,
        "input_tokens": second.input_tokens - first.input_tokens,
        "output_tokens": second.output_tokens - first.output_tokens,
        "token_cost_usd": (
            second.token_cost_usd - first.token_cost_usd
            if first.token_cost_usd is not None and second.token_cost_usd is not None
            else None
        ),
        "token_cost_upper_usd": (
            second.token_cost_upper_usd - first.token_cost_upper_usd
            if first.token_cost_upper_usd is not None
            and second.token_cost_upper_usd is not None
            else None
        ),
        "latency_seconds": second.latency_seconds - first.latency_seconds,
    }


def _genome_analysis(entries: list[dict[str, Any]]) -> dict[str, Any]:
    genomes = [AgentGenome(**entry["genome"]) for entry in entries]
    phenotypes = [entry["candidate"]["phenotype_hash"] for entry in entries]
    groups = {}
    for entry in entries:
        groups.setdefault(entry["candidate"]["phenotype_hash"], []).append(
            entry["genome_sha256"]
        )
    gene_names = tuple(AgentGenome().to_dict())
    gene_stats = {}
    for gene in gene_names:
        comparisons = []
        for index, first in enumerate(entries):
            for second in entries[index + 1 :]:
                differences = [
                    name
                    for name in gene_names
                    if first["genome"][name] != second["genome"][name]
                ]
                if differences != [gene]:
                    continue
                comparisons.append(
                    {
                        "behavior_changed": first["candidate"]["phenotype_hash"]
                        != second["candidate"]["phenotype_hash"],
                        "success_delta": second["metrics"]["task_success_rate"]
                        - first["metrics"]["task_success_rate"],
                        "token_cost_delta": second["metrics"]["token_cost_upper_usd"]
                        - first["metrics"]["token_cost_upper_usd"],
                    }
                )
        gene_stats[gene] = {
            "single_gene_pair_count": len(comparisons),
            "behavior_changed_count": sum(
                row["behavior_changed"] for row in comparisons
            ),
            "behavior_changed_fraction": (
                sum(row["behavior_changed"] for row in comparisons) / len(comparisons)
                if comparisons
                else None
            ),
            "mean_absolute_success_delta": (
                sum(abs(row["success_delta"]) for row in comparisons) / len(comparisons)
                if comparisons
                else None
            ),
            "mean_absolute_token_cost_delta": (
                sum(abs(row["token_cost_delta"]) for row in comparisons)
                / len(comparisons)
                if comparisons
                else None
            ),
        }
    return {
        "population_diversity": population_diversity(genomes, phenotypes),
        "identical_behavior_groups": [
            sorted(group) for group in groups.values() if len(group) > 1
        ],
        "gene_effects": gene_stats,
    }


def run_phase2(
    outdir: Path,
    config: Phase2Config = Phase2Config(),
    client_factory: Callable[[], LLMClient] | None = None,
) -> dict[str, Any]:
    """Run B0/B1/B2 with paired tasks and separate search/final API accounting."""
    outdir = Path(outdir)
    if outdir.exists() and any(outdir.iterdir()):
        raise ValueError("Phase 2 output directory must be empty")
    outdir.mkdir(parents=True, exist_ok=True)
    _write_json(outdir / "train_manifest.json", train_manifest())
    factory = LLMClient.from_env if client_factory is None else client_factory
    prototype = factory()
    if (
        prototype.transport.backend == "openai-compatible"
        and real_configuration_missing(require_pricing=True)
    ):
        raise ValueError("real Phase 2 requires complete environment configuration")
    if prototype.ledger.cost_unknown:
        raise ValueError("Phase 2 requires explicit input/output token prices")
    shared = SharedBudget(
        config.global_request_cap,
        config.global_cost_cap,
        prototype.ledger.input_price_per_1m,
        prototype.ledger.output_price_per_1m,
    )
    backend = prototype.transport.backend
    tasks = train_tasks()
    paired_episode_count = len(tasks) * len(config.seeds)
    planned_episode_count = paired_episode_count * (
        2 + config.population_size * (config.generations + 1) + 1
    )
    source_names = (
        "d094_agent.py",
        "d094_evaluator.py",
        "d094_evolution.py",
        "d094_genome.py",
        "d094_ledger.py",
        "d094_llm_client.py",
        "d094_prompts.py",
        "d094_tasks.py",
        "run_d094_phase2.py",
    )
    execution_lock = {
        "protocol": "D094_PHASE2_TRAIN_V2",
        "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "backend": backend,
        "model": prototype.transport.model,
        "temperature": 0.0,
        "thinking": {"type": "disabled"},
        "config": dataclasses.asdict(config),
        "train_manifest_sha256": train_manifest()["manifest_sha256"],
        "train_task_count": len(tasks),
        "paired_seeds": config.seeds,
        "genome_space": 648,
        "planned_search_candidates": config.population_size * (config.generations + 1),
        "planned_final_candidates": 1,
        "planned_episode_count": planned_episode_count,
        "price_basis": "Peak/cache-miss priced usage plus no-response request upper bounds; not a billing invoice",
        "cost_objective": "token_cost_upper_usd",
        "pricing_source": "https://api-docs.deepseek.com/quick_start/pricing",
        "input_price_per_1m": prototype.ledger.input_price_per_1m,
        "output_price_per_1m": prototype.ledger.output_price_per_1m,
        "source_files": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in source_names
        },
    }
    _write_json(outdir / "execution_lock.json", execution_lock)
    archive: list[dict[str, Any]] = []
    evolution_ledger: list[dict[str, Any]] = []
    episode_count = 0
    usage: dict[str, Any] = {}
    started = time.perf_counter()

    try:
        with (outdir / "episodes.jsonl").open(
            "x", encoding="utf-8", newline="\n"
        ) as episode_output:

            def evaluate(genome: AgentGenome, arm: str, phase: str):
                nonlocal episode_count
                with ThreadPoolExecutor(max_workers=config.max_concurrency) as pool:
                    futures = [
                        pool.submit(
                            _episode,
                            arm,
                            phase,
                            task_index,
                            seed,
                            genome,
                            config,
                            factory,
                            shared,
                        )
                        for task_index in range(len(tasks))
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
                    episode_count += 1
                episode_output.flush()
                metrics = evaluate_episodes([row["record"] for row in rows])
                execution_errors = sum(
                    row["payload"]["execution_error"] for row in rows
                )
                phenotype_hash = payload_sha256(
                    [row["payload"]["metrics"]["phenotype_hash"] for row in rows]
                )
                candidate = Candidate(
                    genome=genome,
                    objectives=objective_vector(metrics),
                    constraint_violation=metrics.constraint_violation,
                    phenotype_hash=phenotype_hash,
                    execution_errors=execution_errors,
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
                    "episode_ids": [row["payload"]["episode_id"] for row in rows],
                }
                key = arm + "/" + phase
                usage[key] = _accumulate_usage(usage.get(key), rows)
                return candidate, metrics, entry

            b0_candidate, b0_metrics, b0_entry = evaluate(FIXED_GENOME, "B0", "fixed")
            b1_candidate, b1_metrics, b1_entry = evaluate(FIXED_GENOME, "B1", "fixed")
            optimizer = NSGAII()

            def search_evaluator(genome: AgentGenome) -> Candidate:
                candidate, _metrics, entry = evaluate(genome, "B2", "search")
                archive.append(entry)
                return candidate

            optimizer.optimize(
                search_evaluator,
                population_size=config.population_size,
                generations=config.generations,
                seed=711,
            )
            evolution_ledger = optimizer.ledger
            _write_json(outdir / "evolution_ledger.json", evolution_ledger)
            candidates = [AgentGenome(**entry["genome"]) for entry in archive]
            front = feasible_pareto(
                [
                    Candidate(
                        genome=entry["genome"] and AgentGenome(**entry["genome"]),
                        objectives=tuple(entry["candidate"]["objectives"]),
                        constraint_violation=entry["candidate"]["constraint_violation"],
                        phenotype_hash=entry["candidate"]["phenotype_hash"],
                        execution_errors=entry["candidate"]["execution_errors"],
                    )
                    for entry in archive
                ]
            )
            selected_entry = None
            b2_entry = None
            b2_metrics = None
            if front:
                selected = min(
                    front,
                    key=lambda candidate: (candidate.objectives, candidate.genome_id),
                )
                selected_hash = selected.genome_id
                selected_entry = next(
                    entry
                    for entry in archive
                    if entry["genome_sha256"] == selected_hash
                )
                _candidate, b2_metrics, b2_entry = evaluate(
                    selected.genome, "B2", "final"
                )
            per_seed = {"B0": b0_entry["per_seed"], "B1": b1_entry["per_seed"]}
            if b2_entry is not None:
                per_seed["B2"] = b2_entry["per_seed"]
            comparisons = {"B1_minus_B0": _comparison(b0_metrics, b1_metrics)}
            if b2_metrics is not None:
                comparisons["B2_minus_B1"] = _comparison(b1_metrics, b2_metrics)
                comparisons["B2_minus_B0"] = _comparison(b0_metrics, b2_metrics)
            execution_errors = sum(entry["execution_errors"] for entry in archive)
            execution_errors += b1_entry["execution_errors"]
            if b2_entry is not None:
                execution_errors += b2_entry["execution_errors"]
            budget_snapshot = shared.snapshot()
            if budget_snapshot["over_budget"]:
                status = "INVALID_BUDGET"
            elif execution_errors:
                status = "INVALID_EPISODES"
            elif selected_entry is None:
                status = "NO_FEASIBLE_CANDIDATE"
            else:
                status = "COMPLETED"
            analysis = _genome_analysis(archive)
            summary = {
                "protocol": "D094_PHASE2_TRAIN_V2",
                "status": status,
                "scientific_scope": "Small exploratory Train-only comparison; not confirmatory statistical evidence",
                "backend": backend,
                "model": prototype.transport.model,
                "planned_episode_count": planned_episode_count,
                "execution_lock_sha256": hashlib.sha256(
                    (outdir / "execution_lock.json").read_bytes()
                ).hexdigest(),
                "config": dataclasses.asdict(config),
                "arms": {
                    "B0": b0_entry,
                    "B1": b1_entry,
                    **({"B2": b2_entry} if b2_entry is not None else {}),
                },
                "search": {
                    "unique_evaluated_genomes": len(archive),
                    "initial_population": config.population_size,
                    "generations": config.generations,
                    "selected_genome_sha256": None
                    if selected_entry is None
                    else selected_entry["genome_sha256"],
                    "feasible_pareto_front": [
                        candidate.genome_id for candidate in front
                    ],
                    **analysis,
                },
                "per_seed": per_seed,
                "comparisons": comparisons,
                "usage_by_arm_phase": usage,
                "budget": {**budget_snapshot, "backend": backend},
                "actual_episode_count": episode_count,
                "wall_seconds": time.perf_counter() - started,
                "evolution_event_count": len(evolution_ledger),
            }
            _write_json(outdir / "summary.json", summary)
            return summary
    except Exception as error:
        failure = {
            "protocol": "D094_PHASE2_TRAIN_V2",
            "status": "INVALID",
            "error_type": type(error).__name__,
            "error": str(error)[:240],
            "budget": {**shared.snapshot(), "backend": backend},
            "actual_episode_count": episode_count,
            "partial_archive": archive,
            "evolution_ledger": evolution_ledger,
        }
        _write_json(outdir / "failure.json", failure)
        _write_json(outdir / "summary.json", failure)
        return failure


def main() -> None:
    """Run the real experiment only with complete environment pricing and explicit execution."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute-real", action="store_true", required=True)
    parser.add_argument("--outdir", type=Path, default=HERE / "results" / "phase2_r1")
    args = parser.parse_args()
    missing = real_configuration_missing(require_pricing=True)
    if missing:
        result = {
            "status": "BLOCKED_CONFIGURATION",
            "missing_configuration": missing,
            "api_attempt_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
        }
        args.outdir.mkdir(parents=True, exist_ok=True)
        _write_json(args.outdir / "summary.json", result)
    else:
        result = run_phase2(args.outdir)
    print(
        json.dumps(
            {
                "status": result["status"],
                "budget": result.get("budget"),
                "episodes": result.get("actual_episode_count", 0),
            }
        )
    )


if __name__ == "__main__":
    main()
