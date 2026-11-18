"""D-094 Typed-Genome NSGA-II with feasibility-first deterministic selection."""
from __future__ import annotations

import dataclasses
import math
import random
from typing import Callable, Sequence

from d094_genome import (
    AgentGenome,
    crossover_genomes,
    enumerate_genomes,
    genome_sha256,
    mutate_genome,
)


TOLERANCE = 1e-12


@dataclasses.dataclass(frozen=True)
class Candidate:
    """Evaluated genome and its minimization objectives."""

    genome: AgentGenome
    objectives: tuple[float, ...]
    constraint_violation: int = 0
    phenotype_hash: str = ""
    execution_errors: int = 0

    def __post_init__(self) -> None:
        if len(self.objectives) < 2 or any(
            not math.isfinite(value) for value in self.objectives
        ):
            raise ValueError("invalid objective vector")
        if type(self.constraint_violation) is not int or self.constraint_violation < 0:
            raise ValueError("invalid hard-constraint count")
        if type(self.execution_errors) is not int or self.execution_errors < 0:
            raise ValueError("invalid execution-error count")

    @property
    def genome_id(self) -> str:
        """Return the canonical genome identity."""
        return genome_sha256(self.genome)

    @property
    def feasible(self) -> bool:
        """Feasibility cannot be compensated by any objective or hidden error."""
        return self.constraint_violation == 0 and self.execution_errors == 0


def _dominates(first: Candidate, second: Candidate) -> bool:
    if len(first.objectives) != len(second.objectives):
        raise ValueError("objective dimensions differ")
    return all(
        a <= b + TOLERANCE for a, b in zip(first.objectives, second.objectives)
    ) and any(a < b - TOLERANCE for a, b in zip(first.objectives, second.objectives))


def non_dominated_fronts(candidates: Sequence[Candidate]) -> list[list[Candidate]]:
    """Compute deterministic Pareto fronts using pairwise dominance."""
    remaining = list(candidates)
    fronts = []
    while remaining:
        front = [
            candidate
            for candidate in remaining
            if not any(
                _dominates(other, candidate)
                for other in remaining
                if other is not candidate
            )
        ]
        if not front:
            raise ValueError("empty non-dominated front")
        fronts.append(sorted(front, key=lambda candidate: candidate.genome_id))
        remaining = [candidate for candidate in remaining if candidate not in front]
    return fronts


def crowding_distances(front: Sequence[Candidate]) -> dict[str, float]:
    """Compute NSGA-II crowding distance for every objective."""
    if not front:
        return {}
    distances = {candidate.genome_id: 0.0 for candidate in front}
    dimensions = len(front[0].objectives)
    for objective in range(dimensions):
        ordered = sorted(
            front,
            key=lambda candidate: (
                candidate.objectives[objective],
                candidate.genome_id,
            ),
        )
        low = ordered[0].objectives[objective]
        high = ordered[-1].objectives[objective]
        if high - low <= TOLERANCE:
            continue
        distances[ordered[0].genome_id] = math.inf
        distances[ordered[-1].genome_id] = math.inf
        for index in range(1, len(ordered) - 1):
            distances[ordered[index].genome_id] += (
                ordered[index + 1].objectives[objective]
                - ordered[index - 1].objectives[objective]
            ) / (high - low)
    return distances


def _unique(candidates: Sequence[Candidate]) -> list[Candidate]:
    unique = {}
    for candidate in candidates:
        unique.setdefault(candidate.genome_id, candidate)
    return list(unique.values())


def nsga2_survivors(candidates: Sequence[Candidate], size: int) -> list[Candidate]:
    """Select survivors feasibility-first, then by Pareto rank and crowding."""
    if size < 0:
        raise ValueError("negative survivor size")
    if size == 0:
        return []
    unique = _unique(candidates)
    feasible = [candidate for candidate in unique if candidate.feasible]
    infeasible = sorted(
        [candidate for candidate in unique if not candidate.feasible],
        key=lambda candidate: (candidate.constraint_violation, candidate.genome_id),
    )
    selected = []
    for front in non_dominated_fronts(feasible):
        if len(selected) + len(front) <= size:
            selected.extend(front)
            continue
        distances = crowding_distances(front)
        ordered = sorted(
            front,
            key=lambda candidate: (
                -distances[candidate.genome_id],
                candidate.genome_id,
            ),
        )
        selected.extend(ordered[: size - len(selected)])
        break
    if len(selected) < size:
        selected.extend(infeasible[: size - len(selected)])
    return selected


def feasible_pareto(candidates: Sequence[Candidate]) -> list[Candidate]:
    """Return the feasible first Pareto front, or no candidate when none exists."""
    feasible = [candidate for candidate in _unique(candidates) if candidate.feasible]
    return non_dominated_fronts(feasible)[0] if feasible else []


def _selection_metadata(candidates: Sequence[Candidate]):
    feasible = [candidate for candidate in candidates if candidate.feasible]
    ranks = {
        candidate.genome_id: 0 for candidate in candidates if not candidate.feasible
    }
    distances = {
        candidate.genome_id: -float(candidate.constraint_violation)
        for candidate in candidates
        if not candidate.feasible
    }
    for rank, front in enumerate(non_dominated_fronts(feasible)):
        front_distances = crowding_distances(front)
        for candidate in front:
            ranks[candidate.genome_id] = rank
            distances[candidate.genome_id] = front_distances[candidate.genome_id]
    infeasible_rank = len(non_dominated_fronts(feasible)) if feasible else 0
    for candidate in candidates:
        if not candidate.feasible:
            ranks[candidate.genome_id] = infeasible_rank
    return ranks, distances


def _tournament(
    candidates: Sequence[Candidate], ranks, distances, rng: random.Random
) -> Candidate:
    first, second = (
        rng.sample(list(candidates), 2)
        if len(candidates) >= 2
        else (candidates[0], candidates[0])
    )
    if first.feasible != second.feasible:
        return first if first.feasible else second
    if not first.feasible and first.constraint_violation != second.constraint_violation:
        return (
            first
            if first.constraint_violation < second.constraint_violation
            else second
        )
    if ranks[first.genome_id] != ranks[second.genome_id]:
        return first if ranks[first.genome_id] < ranks[second.genome_id] else second
    if distances[first.genome_id] != distances[second.genome_id]:
        return (
            first
            if distances[first.genome_id] > distances[second.genome_id]
            else second
        )
    return min((first, second), key=lambda candidate: candidate.genome_id)


class NSGAII:
    """Optimize executable Agent Genomes, never unconstrained prompt strings."""

    def __init__(
        self, crossover_rate: float = 0.9, mutation_rate: float = 1.0 / 6.0
    ) -> None:
        if not 0.0 <= crossover_rate <= 1.0 or not 0.0 <= mutation_rate <= 1.0:
            raise ValueError("invalid variation probability")
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.ledger: list[dict] = []

    def optimize(
        self,
        evaluator: Callable[[AgentGenome], Candidate],
        population_size: int,
        generations: int,
        seed: int,
    ) -> list[Candidate]:
        """Run paired parent/offspring NSGA-II and return the feasible Pareto front."""
        if population_size < 2 or generations < 0:
            raise ValueError("population size must be >=2 and generations >=0")
        rng = random.Random(seed)

        def evaluate(genome: AgentGenome, generation: int) -> Candidate:
            candidate = evaluator(genome)
            if candidate.genome_id != genome_sha256(genome):
                raise ValueError("evaluator returned a different genome")
            if len(candidate.objectives) != 7:
                raise ValueError("D-094 formal optimization requires seven objectives")
            self.ledger.append(
                {
                    "event_type": "evaluation",
                    "generation": generation,
                    "genome_hash": candidate.genome_id,
                    "objectives": candidate.objectives,
                    "constraint_violation": candidate.constraint_violation,
                    "phenotype_hash": candidate.phenotype_hash,
                }
            )
            return candidate

        initial = rng.sample(list(enumerate_genomes()), population_size)
        population = [evaluate(genome, -1) for genome in initial]
        evaluated = {candidate.genome_id for candidate in population}
        for generation in range(generations):
            ranks, distances = _selection_metadata(population)
            existing = set(evaluated)
            offspring = []
            attempts = 0
            while len(offspring) < population_size and attempts < population_size * 20:
                attempts += 1
                first = _tournament(population, ranks, distances, rng)
                second = _tournament(population, ranks, distances, rng)
                crossed = rng.random() < self.crossover_rate
                child = (
                    crossover_genomes(first.genome, second.genome, rng)
                    if crossed
                    else first.genome
                )
                mutated = rng.random() < self.mutation_rate
                if mutated:
                    child = mutate_genome(child, rng)
                child_hash = genome_sha256(child)
                if child_hash in existing:
                    continue
                self.ledger.append(
                    {
                        "event_type": "variation",
                        "generation": generation,
                        "parent_genome_hashes": [first.genome_id, second.genome_id],
                        "child_genome_hash": child_hash,
                        "crossover": crossed,
                        "mutation": mutated,
                    }
                )
                offspring.append(evaluate(child, generation))
                existing.add(child_hash)
                evaluated.add(child_hash)
            population = nsga2_survivors([*population, *offspring], population_size)
        return feasible_pareto(population)
