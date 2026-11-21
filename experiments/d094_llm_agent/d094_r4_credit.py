"""D-094 R4 quality-first paired parent/offspring operator credit.

This module is new for R4.  It does not alter the R3 B2/B3/B4/B5 code.
All search arms use identical feasibility-first NSGA-II survivor selection;
only operator-probability updates differ.  No function in this module performs
network I/O or selects tasks from a held-out split.
"""
from __future__ import annotations

import dataclasses
import math
import random
from collections import deque
from typing import Any, Callable, Sequence

from d094_evolution import (
    Candidate,
    _selection_metadata,
    _tournament,
    feasible_pareto,
    nsga2_survivors,
)
from d094_feedback_evolution import (
    OPERATOR_NAMES,
    fixed_operator_probabilities,
    operator_probabilities,
)
from d094_genome import AgentGenome, enumerate_genomes, genome_sha256


R4_MODES = ("standard", "failure_feedback", "paired_credit")
R4_MUTATION_LOCI = {
    "planning_mutation": "planning_mode",
    "recovery_mutation": "recovery_mode",
    "memory_mutation": "memory_mode",
    "verification_mutation": "reflection_trigger",
    "tool_guard_mutation": "tool_call_guard",
}
PairKey = tuple[str, int]


@dataclasses.dataclass(frozen=True)
class PairedEpisode:
    """Public quality outcomes for one task/seed unit of a candidate evaluation."""

    task_id: str
    seed: int
    task_success: bool
    recovery_success: bool
    constraint_violation: int
    harm: float
    execution_error: bool = False

    def __post_init__(self) -> None:
        if not self.task_id or type(self.seed) is not int:
            raise ValueError("invalid paired episode identity")
        if any(
            type(value) is not bool
            for value in (
                self.task_success,
                self.recovery_success,
                self.execution_error,
            )
        ):
            raise ValueError("paired episode success/error fields must be boolean")
        if (
            type(self.constraint_violation) is not int
            or self.constraint_violation < 0
            or not math.isfinite(self.harm)
            or self.harm < 0.0
        ):
            raise ValueError("invalid paired episode quality metric")

    @property
    def key(self) -> PairKey:
        return self.task_id, self.seed


@dataclasses.dataclass(frozen=True)
class PairedEvaluation:
    """A seven-objective candidate with its complete public paired units."""

    candidate: Candidate
    episodes: tuple[PairedEpisode, ...]

    def __post_init__(self) -> None:
        keys = [episode.key for episode in self.episodes]
        if not keys or len(keys) != len(set(keys)):
            raise ValueError("paired evaluation needs unique nonempty task/seed units")
        if len(self.candidate.objectives) != 7:
            raise ValueError("R4 requires seven minimization objectives")
        expected = quality_objectives(self.episodes)
        if self.candidate.constraint_violation != expected[2]:
            raise ValueError("candidate constraint total differs from paired episodes")
        if self.candidate.execution_errors != sum(
            episode.execution_error for episode in self.episodes
        ):
            raise ValueError("candidate execution errors differ from paired episodes")
        for actual, wanted in zip(self.candidate.objectives[:4], expected):
            if not math.isclose(actual, wanted, rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("candidate quality objectives differ from paired episodes")

    @property
    def pair_keys(self) -> frozenset[PairKey]:
        return frozenset(episode.key for episode in self.episodes)


def quality_objectives(episodes: Sequence[PairedEpisode]) -> tuple[float, ...]:
    """Return the four ordered quality terms used by the primary credit rule."""
    if not episodes:
        raise ValueError("quality objectives require at least one episode")
    count = len(episodes)
    return (
        1.0 - sum(episode.task_success for episode in episodes) / count,
        1.0 - sum(episode.recovery_success for episode in episodes) / count,
        sum(episode.constraint_violation for episode in episodes),
        sum(episode.harm for episode in episodes),
    )


def make_paired_evaluation(
    genome: AgentGenome,
    episodes: Sequence[PairedEpisode],
    *,
    tool_cost: float = 0.0,
    token_cost_upper_usd: float = 0.0,
    latency_seconds: float = 0.0,
    phenotype_hash: str = "",
    failure_profile: dict[str, Any] | None = None,
) -> PairedEvaluation:
    """Build a consistent evaluation; resource terms never enter primary credit."""
    rows = tuple(episodes)
    quality = quality_objectives(rows)
    resources = (tool_cost, token_cost_upper_usd, latency_seconds)
    if any(not math.isfinite(value) or value < 0.0 for value in resources):
        raise ValueError("invalid resource objective")
    candidate = Candidate(
        genome=genome,
        objectives=(*quality, *resources),
        constraint_violation=quality[2],
        execution_errors=sum(row.execution_error for row in rows),
        phenotype_hash=phenotype_hash,
        failure_profile=failure_profile,
    )
    return PairedEvaluation(candidate=candidate, episodes=rows)


def _dominates(first: Sequence[float], second: Sequence[float]) -> bool:
    return all(a <= b for a, b in zip(first, second)) and any(
        a < b for a, b in zip(first, second)
    )


def paired_unit_rewards(
    parent: PairedEvaluation, child: PairedEvaluation
) -> dict[str, dict[str, Any]]:
    """Compare matched public outcomes only, with hard constraints taking priority."""
    if parent.pair_keys != child.pair_keys:
        raise ValueError("parent and child task/seed sets must be identical")
    if any(
        episode.execution_error
        for evaluation in (parent, child)
        for episode in evaluation.episodes
    ):
        raise ValueError("execution error invalidates paired credit")
    child_by_key = {episode.key: episode for episode in child.episodes}
    result = {}
    for old in sorted(parent.episodes, key=lambda row: row.key):
        new = child_by_key[old.key]
        if new.constraint_violation > old.constraint_violation:
            reward = -1.0
            reason = "CONSTRAINT_REGRESSION"
        elif new.constraint_violation < old.constraint_violation:
            reward = 1.0
            reason = "CONSTRAINT_IMPROVEMENT"
        else:
            old_quality = (
                1.0 - float(old.task_success),
                1.0 - float(old.recovery_success),
                old.harm,
            )
            new_quality = (
                1.0 - float(new.task_success),
                1.0 - float(new.recovery_success),
                new.harm,
            )
            if _dominates(new_quality, old_quality):
                reward = 1.0
                reason = "QUALITY_PARETO_IMPROVEMENT"
            elif _dominates(old_quality, new_quality):
                reward = -1.0
                reason = "QUALITY_PARETO_REGRESSION"
            else:
                reward = 0.0
                reason = "NO_STRICT_QUALITY_DOMINANCE"
        result[f"{old.task_id}:{old.seed}"] = {
            "task_id": old.task_id,
            "seed": old.seed,
            "parent_quality": dataclasses.asdict(old),
            "child_quality": dataclasses.asdict(new),
            "reward": reward,
            "reason": reason,
        }
    return result


def offspring_reward(parent: PairedEvaluation, child: PairedEvaluation) -> float:
    """Average the frozen per-unit rewards with an explicit nonzero denominator."""
    units = paired_unit_rewards(parent, child)
    return sum(unit["reward"] for unit in units.values()) / len(units)


def credit_probabilities(
    rewards: Sequence[float], tau: float = 0.25, epsilon: float = 0.2
) -> dict[str, float]:
    """Compute the frozen softmax-over-window-credit distribution for six operators."""
    if not math.isfinite(tau) or not math.isfinite(epsilon):
        raise ValueError("nonfinite credit parameter")
    if tau <= 0.0 or not 0.0 < epsilon < 1.0:
        raise ValueError("invalid credit temperature or exploration floor")
    if any(not math.isfinite(value) or not -1.0 <= value <= 1.0 for value in rewards):
        raise ValueError("operator credit history must contain values in [-1,1]")
    credit = {
        name: (sum(rewards) / len(rewards) if rewards else 0.0)
        for name in OPERATOR_NAMES
    }
    shift = max(credit.values()) / tau
    weights = {
        name: math.exp(value / tau - shift) for name, value in credit.items()
    }
    total = sum(weights.values())
    probabilities = {
        name: (1.0 - epsilon) * weights[name] / total
        + epsilon / len(OPERATOR_NAMES)
        for name in OPERATOR_NAMES
    }
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-12):
        raise ValueError("credit probabilities are not normalized")
    return probabilities


def r4_genome_pool() -> tuple[AgentGenome, ...]:
    """Enumerate the common five-step eligible pool (3*4*3*3*2=216)."""
    return tuple(genome for genome in enumerate_genomes() if genome.max_plan_steps == 5)


def select_final_candidate(candidates: Sequence[Candidate]) -> Candidate | None:
    """Select from all evaluated candidates, never from only the last population."""
    front = feasible_pareto(candidates)
    return min(front, key=lambda row: (row.objectives, row.genome_id)) if front else None


class PairedCreditNSGAII:
    """R4 standard/failure-feedback/paired-credit NSGA-II with a full audit ledger."""

    def __init__(
        self,
        mode: str = "standard",
        *,
        window: int = 4,
        tau: float = 0.25,
        epsilon: float = 0.2,
    ) -> None:
        if mode not in R4_MODES or type(window) is not int or window <= 0:
            raise ValueError("invalid R4 optimizer mode or credit window")
        if tau <= 0.0 or not 0.0 < epsilon < 1.0:
            raise ValueError("invalid R4 credit parameters")
        self.mode = mode
        self.window = window
        self.tau = tau
        self.epsilon = epsilon
        self.ledger: list[dict[str, Any]] = []
        self.archive: list[PairedEvaluation] = []
        self._rewards = {name: deque(maxlen=window) for name in OPERATOR_NAMES}
        self._feedback: dict[str, Any] | None = None

    def _probabilities(self) -> dict[str, float]:
        if self.mode == "paired_credit":
            return credit_probabilities(
                [], tau=self.tau, epsilon=self.epsilon
            ) if not any(self._rewards.values()) else {
                name: probability
                for name, probability in self._window_probabilities().items()
            }
        if self.mode == "failure_feedback":
            if self._feedback is None:
                return fixed_operator_probabilities()
            return operator_probabilities(self._feedback)
        return fixed_operator_probabilities()

    def _window_probabilities(self) -> dict[str, float]:
        credits = {
            name: sum(self._rewards[name]) / len(self._rewards[name])
            if self._rewards[name]
            else 0.0
            for name in OPERATOR_NAMES
        }
        shift = max(credits.values()) / self.tau
        weights = {
            name: math.exp(value / self.tau - shift)
            for name, value in credits.items()
        }
        total = sum(weights.values())
        return {
            name: (1.0 - self.epsilon) * weights[name] / total
            + self.epsilon / len(OPERATOR_NAMES)
            for name in OPERATOR_NAMES
        }

    def _credit_snapshot(self) -> dict[str, Any]:
        return {
            name: {
                "accepted_rewards": list(self._rewards[name]),
                "credit": sum(self._rewards[name]) / len(self._rewards[name])
                if self._rewards[name]
                else 0.0,
            }
            for name in OPERATOR_NAMES
        }

    @staticmethod
    def _choose(probabilities: dict[str, float], rng: random.Random) -> str:
        threshold = rng.random()
        cumulative = 0.0
        for name in OPERATOR_NAMES:
            cumulative += probabilities[name]
            if threshold <= cumulative:
                return name
        return OPERATOR_NAMES[-1]

    @staticmethod
    def _variation(
        first: Candidate,
        second: Candidate,
        operator: str,
        rng: random.Random,
    ) -> tuple[AgentGenome, dict[str, Any]]:
        if operator == "crossover":
            values = {
                field: getattr(first.genome if rng.random() < 0.5 else second.genome, field)
                for field in AgentGenome.__dataclass_fields__
                if field != "max_plan_steps"
            }
            child = dataclasses.replace(first.genome, **values)
            return child, {
                "mutation_locus": None,
                "before_value": None,
                "after_value": None,
            }
        from d094_genome import ALLOWED_VALUES

        locus = R4_MUTATION_LOCI[operator]
        before = getattr(first.genome, locus)
        choices = [value for value in ALLOWED_VALUES[locus] if value != before]
        after = choices[rng.randrange(len(choices))]
        return dataclasses.replace(first.genome, **{locus: after}), {
            "mutation_locus": locus,
            "before_value": before,
            "after_value": after,
        }

    def optimize(
        self,
        evaluator: Callable[[AgentGenome], PairedEvaluation],
        population_size: int,
        generations: int,
        seed: int,
        pair_keys: Sequence[PairKey],
    ) -> list[Candidate]:
        """Run fixed-budget paired evaluation with no duplicate credit updates."""
        if population_size < 2 or generations < 0:
            raise ValueError("population size must be >=2 and generations >=0")
        expected_pairs = frozenset(pair_keys)
        if not expected_pairs or len(expected_pairs) != len(pair_keys):
            raise ValueError("invalid expected task/seed set")
        if len(r4_genome_pool()) != 216:
            raise ValueError("R4 eligible genome pool changed")
        rng = random.Random(seed)
        evaluated: set[str] = set()

        def evaluate(genome: AgentGenome, generation: int) -> PairedEvaluation:
            evaluation = evaluator(genome)
            if not isinstance(evaluation, PairedEvaluation):
                raise ValueError("R4 evaluator must return PairedEvaluation")
            candidate = evaluation.candidate
            if candidate.genome_id != genome_sha256(genome):
                raise ValueError("evaluator genome identity mismatch")
            if evaluation.pair_keys != expected_pairs:
                raise ValueError("evaluation lacks the frozen complete paired units")
            if candidate.execution_errors:
                raise ValueError("execution error invalidates R4 search evaluation")
            event = {
                "event_type": "evaluation",
                "generation": generation,
                "genome_hash": candidate.genome_id,
                "genome": genome.to_dict(),
                "objectives": candidate.objectives,
                "constraint_violation": candidate.constraint_violation,
                "execution_errors": candidate.execution_errors,
                "phenotype_hash": candidate.phenotype_hash,
                "pair_keys": [f"{task}:{episode_seed}" for task, episode_seed in pair_keys],
                "episodes": [dataclasses.asdict(row) for row in evaluation.episodes],
            }
            self.ledger.append(event)
            self.archive.append(evaluation)
            if self.mode == "failure_feedback":
                if candidate.failure_profile is None:
                    raise ValueError("failure-feedback arm needs a public failure profile")
                self._feedback = candidate.failure_profile
                self.ledger.append(
                    {
                        "event_type": "feedback_update",
                        "generation": generation,
                        "genome_hash": candidate.genome_id,
                        "failure_profile": self._feedback,
                        "probabilities_after": self._probabilities(),
                    }
                )
            return evaluation

        initial = rng.sample(list(r4_genome_pool()), population_size)
        population = [evaluate(genome, -1).candidate for genome in initial]
        evaluated = {candidate.genome_id for candidate in population}
        self._record_survivors(-1, population)
        for generation in range(generations):
            ranks, distances = _selection_metadata(population)
            offspring: list[Candidate] = []
            attempts = 0
            while len(offspring) < population_size:
                attempts += 1
                if attempts > population_size * 30:
                    raise RuntimeError("R4 duplicate proposal cap exhausted")
                first = _tournament(population, ranks, distances, rng)
                second = _tournament(population, ranks, distances, rng)
                probabilities = self._probabilities()
                operator = self._choose(probabilities, rng)
                child, details = self._variation(first, second, operator, rng)
                child_hash = genome_sha256(child)
                duplicate = child_hash in evaluated
                event = {
                    "event_type": "variation",
                    "generation": generation,
                    "proposal_ordinal": attempts - 1,
                    "mode": self.mode,
                    "operator": operator,
                    "operator_probabilities": probabilities,
                    "credit_state_before": self._credit_snapshot()
                    if self.mode == "paired_credit"
                    else None,
                    "parent_genome_hashes": [first.genome_id, second.genome_id],
                    "primary_parent_genome_hash": first.genome_id,
                    "offspring_genome": child.to_dict(),
                    "offspring_genome_hash": child_hash,
                    "outcome": "DUPLICATE_PROPOSAL"
                    if duplicate
                    else "ACCEPTED_FOR_EVALUATION",
                    **details,
                }
                self.ledger.append(event)
                if duplicate:
                    self.ledger.append(
                        {
                            "event_type": "duplicate_proposal",
                            "generation": generation,
                            "proposal_ordinal": attempts - 1,
                            "operator": operator,
                            "genome_hash": child_hash,
                            "credit_updated": False,
                            "evaluated": False,
                            "outcome": "REJECTED_WITHOUT_EVALUATION",
                        }
                    )
                    continue
                parent = next(
                    row for row in self.archive if row.candidate.genome_id == first.genome_id
                )
                child_evaluation = evaluate(child, generation)
                if self.mode == "paired_credit":
                    units = paired_unit_rewards(parent, child_evaluation)
                    reward = sum(row["reward"] for row in units.values()) / len(units)
                    before = self._credit_snapshot()
                    probabilities_before = self._window_probabilities()
                    self._rewards[operator].append(reward)
                    self.ledger.append(
                        {
                            "event_type": "credit_update",
                            "generation": generation,
                            "proposal_ordinal": attempts - 1,
                            "operator": operator,
                            "primary_parent_genome_hash": first.genome_id,
                            "offspring_genome_hash": child_hash,
                            "paired_units": units,
                            "offspring_reward": reward,
                            "window": self.window,
                            "tau": self.tau,
                            "epsilon": self.epsilon,
                            "credit_before": before,
                            "credit_after": self._credit_snapshot(),
                            "probabilities_before": probabilities_before,
                            "probabilities_after": self._window_probabilities(),
                            "resource_objectives_used": False,
                            "future_information_used": False,
                        }
                    )
                offspring.append(child_evaluation.candidate)
                evaluated.add(child_hash)
            population = nsga2_survivors([*population, *offspring], population_size)
            self._record_survivors(generation, population)
        return feasible_pareto(population)

    def _record_survivors(self, generation: int, population: Sequence[Candidate]) -> None:
        self.ledger.append(
            {
                "event_type": "survivor_selection",
                "generation": generation,
                "selection_method": "feasibility_first_standard_nsga2"
                if generation >= 0
                else "initial_population",
                "survivors": [
                    {
                        "genome_sha256": row.genome_id,
                        "phenotype_hash": row.phenotype_hash,
                        "objectives": row.objectives,
                        "constraint_violation": row.constraint_violation,
                    }
                    for row in population
                ],
                "genotype_diversity": len({row.genome_id for row in population})
                / len(population),
                "phenotype_diversity": len({row.phenotype_hash for row in population})
                / len(population),
                "performance_diversity": len({row.objectives for row in population})
                / len(population),
            }
        )
