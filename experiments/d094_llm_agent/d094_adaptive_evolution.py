"""D-094 standard, feedback-driven, behavior-aware and combined Typed-Genome NSGA-II."""
from __future__ import annotations

import dataclasses
import random
from typing import Any, Callable

from d094_diversity import diversity_survivors
from d094_evolution import Candidate, _selection_metadata, _tournament, feasible_pareto
from d094_feedback_evolution import (
    OPERATOR_NAMES,
    classify_failures,
    fixed_operator_probabilities,
    operator_probabilities,
)
from d094_genome import AgentGenome, crossover_genomes, enumerate_genomes, genome_sha256


MUTATION_LOCI = {
    "recovery_mutation": ("recovery_mode",),
    "memory_mutation": ("memory_mode",),
    "verification_mutation": ("reflection_trigger",),
    "tool_guard_mutation": ("tool_call_guard",),
}
MODE_MECHANISMS = {
    "standard": [],
    "genome": [],
    "phenotype": [],
    "feedback": ["feedback"],
    "diversity": ["diversity"],
    "combined": ["feedback", "diversity"],
}


class AdaptiveNSGAII:
    """Isolate feedback-driven variation and behavior-aware survivor selection."""

    def __init__(self, mode: str = "standard") -> None:
        if mode not in MODE_MECHANISMS:
            raise ValueError("unknown adaptive NSGA-II mode")
        self.mode = mode
        self.mechanisms = MODE_MECHANISMS[mode]
        self.ledger: list[dict[str, Any]] = []
        self._feedback = classify_failures([])

    def _probabilities(self) -> dict[str, float]:
        if "feedback" in self.mechanisms:
            return operator_probabilities(self._feedback)
        return fixed_operator_probabilities()

    def _operator(self, probabilities: dict[str, float], rng: random.Random) -> str:
        threshold = rng.random()
        cumulative = 0.0
        for name in OPERATOR_NAMES:
            cumulative += probabilities[name]
            if threshold <= cumulative:
                return name
        return OPERATOR_NAMES[-1]

    def _variation(
        self,
        first: Candidate,
        second: Candidate,
        operator: str,
        rng: random.Random,
    ) -> tuple[AgentGenome, dict[str, Any]]:
        if operator == "crossover":
            child = crossover_genomes(first.genome, second.genome, rng)
            return child, {
                "intermediate_genome": child.to_dict(),
                "mutation_locus": None,
                "before_value": None,
                "after_value": None,
            }
        if operator == "planning_mutation":
            locus = "planning_mode" if rng.random() < 0.5 else "max_plan_steps"
        else:
            locus = MUTATION_LOCI[operator][0]
        alternatives = [
            value for value in AgentGenome.__dataclass_fields__.keys() if value == locus
        ]
        if alternatives != [locus]:
            raise ValueError("unknown mutation locus")
        from d094_genome import ALLOWED_VALUES

        before = getattr(first.genome, locus)
        choices = [value for value in ALLOWED_VALUES[locus] if value != before]
        after = choices[rng.randrange(len(choices))]
        intermediate = first.genome.to_dict()
        child = dataclasses.replace(first.genome, **{locus: after})
        return child, {
            "intermediate_genome": intermediate,
            "mutation_locus": locus,
            "before_value": before,
            "after_value": after,
        }

    def optimize(
        self,
        evaluator: Callable[[AgentGenome], Candidate],
        population_size: int,
        generations: int,
        seed: int,
    ) -> list[Candidate]:
        """Run reproducible Typed-Genome evolution with complete variation/survivor logs."""
        if population_size < 2 or generations < 0:
            raise ValueError("invalid evolutionary scale")
        rng = random.Random(seed)
        evaluated: set[str] = set()

        def evaluate(genome: AgentGenome, generation: int) -> Candidate:
            candidate = evaluator(genome)
            if candidate.genome_id != genome_sha256(genome):
                raise ValueError("evaluator genome identity mismatch")
            self.ledger.append(
                {
                    "event_type": "evaluation",
                    "generation": generation,
                    "genome_hash": candidate.genome_id,
                    "objectives": candidate.objectives,
                    "constraint_violation": candidate.constraint_violation,
                    "execution_errors": candidate.execution_errors,
                    "phenotype_hash": candidate.phenotype_hash,
                }
            )
            if "feedback" in self.mechanisms and candidate.failure_profile is not None:
                self._feedback = candidate.failure_profile
                self.ledger.append(
                    {
                        "event_type": "feedback_update",
                        "generation": generation,
                        "genome_hash": candidate.genome_id,
                        "failure_profile": self._feedback,
                    }
                )
            return candidate

        initial = rng.sample(list(enumerate_genomes()), population_size)
        population = [evaluate(genome, -1) for genome in initial]
        evaluated = {candidate.genome_id for candidate in population}
        self.ledger.append(
            {
                "event_type": "survivor_selection",
                "generation": -1,
                "selection_method": "initial_population",
                "survivors": [
                    {
                        "genome_sha256": candidate.genome_id,
                        "phenotype_hash": candidate.phenotype_hash,
                    }
                    for candidate in population
                ],
                "genotype_diversity": 1.0,
                "phenotype_diversity": len(
                    {candidate.phenotype_hash for candidate in population}
                )
                / len(population),
                "performance_diversity": len(
                    {candidate.objectives for candidate in population}
                )
                / len(population),
            }
        )
        for generation in range(generations):
            ranks, distances = _selection_metadata(population)
            offspring = []
            attempts = 0
            while len(offspring) < population_size and attempts < population_size * 30:
                attempts += 1
                first = _tournament(population, ranks, distances, rng)
                second = _tournament(population, ranks, distances, rng)
                probabilities = self._probabilities()
                operator = self._operator(probabilities, rng)
                child, details = self._variation(first, second, operator, rng)
                child_hash = genome_sha256(child)
                duplicate = child_hash in evaluated
                event = {
                    "event_type": "variation",
                    "generation": generation,
                    "proposal_ordinal": attempts - 1,
                    "operator": operator,
                    "operator_probabilities": probabilities,
                    "parent_genome_hashes": [first.genome_id, second.genome_id],
                    "offspring_genome": child.to_dict(),
                    "offspring_genome_hash": child_hash,
                    "outcome": "DUPLICATE_PROPOSAL"
                    if duplicate
                    else "ACCEPTED_FOR_EVALUATION",
                    **details,
                }
                if "feedback" in self.mechanisms:
                    event["failure_profile"] = self._feedback
                self.ledger.append(event)
                if duplicate:
                    self.ledger.append(
                        {
                            "event_type": "duplicate_proposal",
                            "generation": generation,
                            "proposal_ordinal": attempts - 1,
                            "genome_hash": child_hash,
                            "outcome": "REJECTED_WITHOUT_EVALUATION",
                        }
                    )
                    continue
                offspring.append(evaluate(child, generation))
                evaluated.add(child_hash)
            method = "standard"
            if self.mode == "genome":
                method = "genome"
            elif self.mode == "phenotype":
                method = "phenotype"
            elif self.mode in {"diversity", "combined"}:
                method = "full"
            population = diversity_survivors(
                [*population, *offspring], population_size, method
            )
            self.ledger.append(
                {
                    "event_type": "survivor_selection",
                    "generation": generation,
                    "selection_method": method,
                    "survivors": [
                        {
                            "genome_sha256": candidate.genome_id,
                            "phenotype_hash": candidate.phenotype_hash,
                            "objectives": candidate.objectives,
                        }
                        for candidate in population
                    ],
                    "genotype_diversity": len(
                        {candidate.genome_id for candidate in population}
                    )
                    / len(population),
                    "phenotype_diversity": len(
                        {candidate.phenotype_hash for candidate in population}
                    )
                    / len(population),
                    "performance_diversity": len(
                        {candidate.objectives for candidate in population}
                    )
                    / len(population),
                }
            )
        return feasible_pareto(population)


def run_synthetic_ablation(
    evaluator: Callable[[AgentGenome], Candidate],
    population_size: int,
    generations: int,
    seed: int,
) -> dict[str, dict[str, Any]]:
    """Run six algorithm controls without any API or real-performance claim."""
    result = {}
    for mode in (
        "standard",
        "genome",
        "phenotype",
        "feedback",
        "diversity",
        "combined",
    ):
        optimizer = AdaptiveNSGAII(mode)
        survivors = optimizer.optimize(evaluator, population_size, generations, seed)
        generation_diversity = [
            event
            for event in optimizer.ledger
            if event["event_type"] == "survivor_selection"
        ]
        result[mode] = {
            "scope": "SYNTHETIC_ONLY",
            "survivor_genome_hashes": [candidate.genome_id for candidate in survivors],
            "unique_survivor_phenotypes": len(
                {candidate.phenotype_hash for candidate in survivors}
            ),
            "evaluation_count": sum(
                event["event_type"] == "evaluation" for event in optimizer.ledger
            ),
            "duplicate_proposal_count": sum(
                event["event_type"] == "duplicate_proposal"
                for event in optimizer.ledger
            ),
            "last_generation_diversity": generation_diversity[-1]
            if generation_diversity
            else None,
        }
    return result
