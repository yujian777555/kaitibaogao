"""D-094 multi-objective episode aggregation and behavior-diversity reports."""
from __future__ import annotations

import dataclasses
import math
from typing import Iterable

from d094_genome import AgentGenome, genome_sha256


@dataclasses.dataclass(frozen=True)
class EpisodeRecord:
    """Public evaluator outputs for one independent task episode."""

    task_success: bool
    recovery_success: bool
    constraint_violation: int
    harm: float
    tool_cost: float
    input_tokens: int
    output_tokens: int
    token_cost_usd: float | None
    latency_seconds: float
    phenotype_hash: str
    token_cost_upper_usd: float | None = None


@dataclasses.dataclass(frozen=True)
class EvaluationMetrics:
    """Aggregated metrics; success objectives are not collapsed into a score."""

    task_success_rate: float
    recovery_success_rate: float
    constraint_violation: int
    harm: float
    tool_cost: float
    input_tokens: int
    output_tokens: int
    token_cost_usd: float | None
    latency_seconds: float
    behavior_diversity: float
    token_cost_upper_usd: float | None = None


def evaluate_episodes(episodes: Iterable[EpisodeRecord]) -> EvaluationMetrics:
    """Aggregate independent episodes without hiding hard violations."""
    rows = list(episodes)
    if not rows:
        raise ValueError("at least one episode is required")
    for row in rows:
        if type(row.task_success) is not bool or type(row.recovery_success) is not bool:
            raise ValueError("episode success fields must be boolean")
        if type(row.constraint_violation) is not int or row.constraint_violation < 0:
            raise ValueError("invalid constraint count")
        for value in (row.harm, row.tool_cost, row.latency_seconds):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError("invalid episode cost")
        if type(row.input_tokens) is not int or row.input_tokens < 0:
            raise ValueError("invalid input tokens")
        if type(row.output_tokens) is not int or row.output_tokens < 0:
            raise ValueError("invalid output tokens")
        if row.token_cost_usd is not None and (
            not math.isfinite(row.token_cost_usd) or row.token_cost_usd < 0.0
        ):
            raise ValueError("invalid token cost")
        if row.token_cost_upper_usd is not None and (
            not math.isfinite(row.token_cost_upper_usd)
            or row.token_cost_upper_usd < 0.0
        ):
            raise ValueError("invalid token cost upper bound")
    count = len(rows)
    priced = all(row.token_cost_usd is not None for row in rows)
    upper_values = [
        row.token_cost_upper_usd
        if row.token_cost_upper_usd is not None
        else row.token_cost_usd
        for row in rows
    ]
    priced_upper = all(value is not None for value in upper_values)
    return EvaluationMetrics(
        task_success_rate=sum(row.task_success for row in rows) / count,
        recovery_success_rate=sum(row.recovery_success for row in rows) / count,
        constraint_violation=sum(row.constraint_violation for row in rows),
        harm=sum(row.harm for row in rows),
        tool_cost=sum(row.tool_cost for row in rows),
        input_tokens=sum(row.input_tokens for row in rows),
        output_tokens=sum(row.output_tokens for row in rows),
        token_cost_usd=sum(row.token_cost_usd for row in rows) if priced else None,
        latency_seconds=sum(row.latency_seconds for row in rows) / count,
        behavior_diversity=len({row.phenotype_hash for row in rows}) / count,
        token_cost_upper_usd=sum(upper_values) if priced_upper else None,
    )


def objective_vector(metrics: EvaluationMetrics) -> tuple[float, ...]:
    """Convert metrics to seven minimization objectives using conservative cost."""
    if metrics.token_cost_upper_usd is None:
        raise ValueError("formal Pareto cost objective requires locked token prices")
    return (
        1.0 - metrics.task_success_rate,
        1.0 - metrics.recovery_success_rate,
        float(metrics.constraint_violation),
        metrics.harm,
        metrics.tool_cost,
        metrics.token_cost_upper_usd,
        metrics.latency_seconds,
    )


def population_diversity(
    genomes: list[AgentGenome], phenotype_hashes: list[str]
) -> dict[str, float | int | bool]:
    """Measure genotype and actual public-behavior diversity at population level."""
    if len(genomes) != len(phenotype_hashes):
        raise ValueError("genome and phenotype counts differ")
    if not genomes:
        return {
            "genotype_count": 0,
            "unique_genotype_count": 0,
            "phenotype_count": 0,
            "unique_phenotype_count": 0,
            "genotype_diversity": 0.0,
            "behavior_diversity": 0.0,
            "complete_behavior_collapse": False,
        }
    unique_genotypes = len({genome_sha256(genome) for genome in genomes})
    unique_phenotypes = len(set(phenotype_hashes))
    return {
        "genotype_count": len(genomes),
        "unique_genotype_count": unique_genotypes,
        "phenotype_count": len(phenotype_hashes),
        "unique_phenotype_count": unique_phenotypes,
        "genotype_diversity": unique_genotypes / len(genomes),
        "behavior_diversity": unique_phenotypes / unique_genotypes,
        "complete_behavior_collapse": unique_phenotypes < 2,
    }
