"""D-094 NSGA-II, feasibility and multi-objective evaluation tests."""
from __future__ import annotations

import unittest

from d094_evaluator import (
    EpisodeRecord,
    evaluate_episodes,
    objective_vector,
    population_diversity,
)
from d094_evolution import (
    Candidate,
    NSGAII,
    crowding_distances,
    feasible_pareto,
    non_dominated_fronts,
    nsga2_survivors,
)
from d094_genome import AgentGenome, enumerate_genomes, genome_sha256


def candidate(
    index: int, objectives: tuple[float, ...], violation: int = 0
) -> Candidate:
    return Candidate(
        genome=enumerate_genomes()[index],
        objectives=objectives,
        constraint_violation=violation,
        phenotype_hash=f"behavior-{index}",
    )


def seven(value: float) -> tuple[float, ...]:
    return (value,) * 7


class TestEvaluator(unittest.TestCase):
    def test_multiobjective_aggregation_preserves_costs_and_diversity(self):
        episodes = [
            EpisodeRecord(True, True, 0, 0.0, 2.0, 10, 4, 0.001, 0.5, "trace-a"),
            EpisodeRecord(False, True, 1, 1.5, 3.0, 20, 6, 0.002, 1.5, "trace-b"),
            EpisodeRecord(True, False, 0, 0.5, 1.0, 30, 8, 0.003, 1.0, "trace-a"),
        ]
        metrics = evaluate_episodes(episodes)
        self.assertAlmostEqual(metrics.task_success_rate, 2 / 3)
        self.assertAlmostEqual(metrics.recovery_success_rate, 2 / 3)
        self.assertEqual(metrics.constraint_violation, 1)
        self.assertAlmostEqual(metrics.harm, 2.0)
        self.assertAlmostEqual(metrics.tool_cost, 6.0)
        self.assertEqual(metrics.input_tokens, 60)
        self.assertEqual(metrics.output_tokens, 18)
        self.assertAlmostEqual(metrics.token_cost_usd, 0.006)
        self.assertAlmostEqual(metrics.latency_seconds, 1.0)
        self.assertAlmostEqual(metrics.behavior_diversity, 2 / 3)
        for actual, expected in zip(
            objective_vector(metrics), (1 / 3, 1 / 3, 1, 2.0, 6.0, 0.006, 1.0)
        ):
            self.assertAlmostEqual(actual, expected)

    def test_unknown_cost_cannot_enter_formal_pareto_objective(self):
        episode = EpisodeRecord(True, True, 0, 0.0, 1.0, 10, 5, None, 1.0, "trace-a")
        metrics = evaluate_episodes([episode])
        self.assertIsNone(metrics.token_cost_usd)
        with self.assertRaises(ValueError):
            objective_vector(metrics)

    def test_population_diversity_detects_behavior_collapse(self):
        genomes = [AgentGenome(), AgentGenome(max_plan_steps=3), AgentGenome()]
        result = population_diversity(genomes, ["same", "same", "same"])
        self.assertEqual(result["genotype_count"], 3)
        self.assertEqual(result["unique_genotype_count"], 2)
        self.assertEqual(result["unique_phenotype_count"], 1)
        self.assertEqual(result["behavior_diversity"], 0.5)
        self.assertTrue(result["complete_behavior_collapse"])


class TestNSGAII(unittest.TestCase):
    def test_non_dominated_fronts_known_answer(self):
        a = candidate(0, (1.0, 1.0))
        b = candidate(1, (2.0, 2.0))
        c = candidate(2, (1.0, 2.0))
        d = candidate(3, (0.0, 3.0))
        fronts = non_dominated_fronts([a, b, c, d])
        self.assertEqual(
            [[item.genome for item in front] for front in fronts],
            [[a.genome, d.genome], [c.genome], [b.genome]],
        )

    def test_crowding_distance_known_answer(self):
        a = candidate(0, (0.0, 2.0))
        b = candidate(1, (1.0, 1.0))
        c = candidate(2, (2.0, 0.0))
        distances = crowding_distances([a, b, c])
        self.assertEqual(distances[genome_sha256(a.genome)], float("inf"))
        self.assertEqual(distances[genome_sha256(c.genome)], float("inf"))
        self.assertAlmostEqual(distances[genome_sha256(b.genome)], 2.0)

    def test_hard_constraints_cannot_be_compensated_by_success(self):
        feasible = candidate(0, seven(5.0), violation=0)
        attractive_but_invalid = candidate(1, seven(0.0), violation=1)
        selected = nsga2_survivors([feasible, attractive_but_invalid], 1)
        self.assertEqual(selected, [feasible])
        self.assertEqual(feasible_pareto([attractive_but_invalid]), [])

    def test_infeasible_fill_is_ordered_after_all_feasible_candidates(self):
        feasible = candidate(0, seven(5.0), violation=0)
        less_invalid = candidate(1, seven(0.0), violation=1)
        more_invalid = candidate(2, seven(-1.0), violation=3)
        selected = nsga2_survivors([more_invalid, less_invalid, feasible], 3)
        self.assertEqual(selected[0], feasible)
        self.assertEqual(selected[1:], [less_invalid, more_invalid])

    def test_optimizer_is_deterministic_and_records_real_genome_variation(self):
        def evaluate(genome: AgentGenome) -> Candidate:
            value = float(genome.max_plan_steps)
            return Candidate(
                genome=genome,
                objectives=(value, value, 0.0, value, value, value, value),
                constraint_violation=0,
                phenotype_hash=f"behavior-{genome_sha256(genome)}",
            )

        first = NSGAII().optimize(evaluate, population_size=4, generations=2, seed=19)
        second = NSGAII().optimize(evaluate, population_size=4, generations=2, seed=19)
        self.assertEqual(
            [genome_sha256(item.genome) for item in first],
            [genome_sha256(item.genome) for item in second],
        )
        self.assertTrue(all(item.feasible for item in first))
        optimizer = NSGAII()
        optimizer.optimize(evaluate, population_size=4, generations=2, seed=19)
        self.assertTrue(
            any(event["event_type"] == "variation" for event in optimizer.ledger)
        )
        variation = next(
            event for event in optimizer.ledger if event["event_type"] == "variation"
        )
        self.assertEqual(len(variation["parent_genome_hashes"]), 2)
        self.assertEqual(len(variation["child_genome_hash"]), 64)

    def test_cross_generation_duplicate_genomes_are_never_reevaluated(self):
        def evaluate(genome: AgentGenome) -> Candidate:
            return Candidate(genome, (float(genome.max_plan_steps),) * 7)

        optimizer = NSGAII()
        optimizer.optimize(evaluate, population_size=4, generations=4, seed=0)
        evaluated = [
            event["genome_hash"]
            for event in optimizer.ledger
            if event["event_type"] == "evaluation"
        ]
        self.assertEqual(len(evaluated), len(set(evaluated)))


if __name__ == "__main__":
    unittest.main()
