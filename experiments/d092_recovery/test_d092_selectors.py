"""D-092 selector synthetic tests; no genomes are searched or evaluated on Train."""
from __future__ import annotations

import math
import random
import unittest

from d092_selectors import (
    Candidate,
    associate_to_reference,
    crowding_distances,
    non_dominated_fronts,
    normalize_objectives,
    nsga2_survivor,
    nsga3_survivor,
    reference_directions,
    select_final_candidate,
    select_niche_candidate,
    select_survivors,
)


def candidate(name, r3=0.0, r4=0.0, cond=0.0, harm=0.0, cost=0.0, hard=0):
    return Candidate(
        genome_hash=name,
        objectives=(1.0 - r3, 1.0 - r4, 1.0 - cond, float(harm), float(cost)),
        hard_constraints={"pending_count": hard},
    )


class TestNSGA2(unittest.TestCase):
    def test_non_dominated_fronts_and_tie_break(self):
        a = candidate("a", r3=1, r4=1)
        b = candidate("b")
        c = candidate("c", r3=1)
        fronts = non_dominated_fronts([b, c, a])
        self.assertEqual([[x.genome_hash for x in front] for front in fronts], [["a"], ["c"], ["b"]])
        selected = nsga2_survivor([b, a], 1)
        self.assertEqual([x.genome_hash for x in selected], ["a"])

    def test_crowding_boundaries_and_zero_span(self):
        values = [candidate("a", cost=0, harm=1), candidate("b", cost=1, harm=1), candidate("c", cost=2, harm=1)]
        distances = crowding_distances(values)
        self.assertTrue(math.isinf(distances["a"]))
        self.assertTrue(math.isinf(distances["c"]))
        self.assertTrue(math.isfinite(distances["b"]))
        self.assertEqual(distances["b"], 1.0)

    def test_nsga2_does_not_consume_rng(self):
        rng = random.Random(5)
        before = rng.getstate()
        nsga2_survivor([candidate("b"), candidate("a")], 1)
        self.assertEqual(rng.getstate(), before)


class TestNSGA3Normalization(unittest.TestCase):
    def test_nonzero_ideal_diagonal_expected_answers(self):
        ideal = (10.0, 20.0, 30.0, 40.0, 50.0)
        diagonal = (2.0, 4.0, 5.0, 8.0, 10.0)
        extremes = [tuple(ideal[i] + (diagonal[i] if i == j else 0.0) for i in range(5)) for j in range(5)]
        point = tuple(value + 1.0 for value in ideal)
        result = normalize_objectives([point] + extremes, extreme_points=extremes)
        self.assertEqual(result["ideal"], ideal)
        self.assertEqual(result["scale"], diagonal)
        self.assertEqual(result["normalized"][0], (0.5, 0.25, 0.2, 0.125, 0.1))

    def test_non_diagonal_asymmetric_matrix_and_transpose_detection(self):
        ideal = (10.0, 20.0, 30.0, 40.0, 50.0)
        rows = [(2, 1, 0, 0, 0), (0, 3, 1, 0, 0), (0, 0, 4,1,0), (0,0,0,5,1), (0,0,0,0,6)]
        extremes = [tuple(ideal[i] + row[i] for i in range(5)) for row in rows]
        point = tuple(value + 1.0 for value in ideal)
        result = normalize_objectives([point] + extremes, extreme_points=extremes)
        expected_x = (53/144, 19/72, 5/24, 1/6, 1/6)
        for actual, expected in zip(result["solution"], expected_x):
            self.assertAlmostEqual(actual, expected, places=12)
        self.assertEqual(result["matrix"], rows)
        for actual, expected in zip(result["normalized"][0], expected_x):
            self.assertAlmostEqual(actual, expected, places=12)
        transposed = [tuple(row[i] for row in rows) for i in range(5)]
        self.assertNotEqual(transposed, rows)

    def test_singular_fallback_uses_translated_maximum(self):
        objectives = [(10.0, 20.0, 0.0, 0.0, 0.0), (12.0, 24.0, 0.0, 0.0, 0.0), (14.0, 22.0, 0.0, 0.0, 0.0)]
        extremes = [objectives[1], objectives[1]] * 2 + [objectives[2]]
        result = normalize_objectives(objectives, extreme_points=extremes)
        self.assertTrue(result["fallback"])
        self.assertEqual(result["raw_scale"], (4.0, 4.0, 0.0, 0.0, 0.0))
        self.assertEqual(result["scale"], (4.0, 4.0, 1.0, 1.0, 1.0))

    def test_zero_span_is_normalized_to_zero(self):
        result = normalize_objectives([(2.0, 3.0, 0.0, 0.0, 0.0), (2.0, 3.0, 0.0, 0.0, 0.0)])
        self.assertEqual(result["normalized"], [(0.0,) * 5, (0.0,) * 5])
        self.assertEqual(result["zero_span"], (True,) * 5)


class TestReferenceAndNiching(unittest.TestCase):
    def test_reference_directions_are_35_unique_sorted_and_unit_sum(self):
        directions = reference_directions()
        self.assertEqual(len(directions), 35)
        self.assertEqual(len(set(directions)), 35)
        integer_tuples = [tuple(int(value * 3) for value in direction) for direction in directions]
        self.assertEqual(integer_tuples, sorted(integer_tuples))
        self.assertTrue(all(sum(direction) == 1 for direction in directions))

    def test_association_uses_perpendicular_squared_distance(self):
        direction = (0.0, 1.0)
        index, distance = associate_to_reference((2.0, 1.0), [direction])
        self.assertEqual(index, 0)
        self.assertEqual(distance, 4.0)

    def test_niche_zero_uses_nearest_without_rng(self):
        remaining = [candidate("a"), candidate("b")]
        rng = random.Random(9)
        before = rng.getstate()
        audit = []
        selected = select_niche_candidate(remaining, [0], {"a": 0, "b": 0}, {"a": 2.0, "b": 1.0}, rng, audit)
        self.assertEqual(selected.genome_hash, "b")
        self.assertEqual(rng.getstate(), before)
        self.assertEqual(audit[0]["niche_count"], 0)

    def test_niche_positive_uses_seeded_uniform_choice(self):
        remaining = [candidate("a"), candidate("b")]
        audit = []
        selected = select_niche_candidate(remaining, [2], {"a": 0, "b": 0}, {"a": 0.0, "b": 0.0}, random.Random(9), audit)
        self.assertIn(selected.genome_hash, {"a", "b"})
        self.assertEqual(audit[0]["niche_count"], 2)

    def test_full_nsga3_returns_requested_population_and_audit(self):
        candidates = [candidate(f"g{i:02d}", r3=(i % 3) / 2, cost=i % 2) for i in range(15)]
        selected, audit = nsga3_survivor(candidates, 12, random.Random(11))
        self.assertEqual(len(selected), 12)
        self.assertEqual(len({x.genome_hash for x in selected}), 12)
        self.assertIn("association", audit)
        self.assertIn("niching", audit)


class TestFeasibilityAndFinalSelection(unittest.TestCase):
    def test_hard_violation_cannot_be_compensated_by_fitness(self):
        feasible = candidate("feasible", r3=1, r4=1, cond=1, harm=1, cost=1)
        unsafe = candidate("unsafe", r3=1, r4=1, cond=1, harm=0, cost=0, hard=1)
        self.assertEqual(select_final_candidate([unsafe, feasible]).genome_hash, "feasible")

    def test_final_selection_uses_frozen_lexicographic_order(self):
        worse_cost = candidate("a", r3=1, r4=1, cond=1, cost=2)
        better_cost = candidate("b", r3=1, r4=1, cond=1, cost=1)
        self.assertEqual(select_final_candidate([worse_cost, better_cost]).genome_hash, "b")

    def test_no_feasible_candidate_and_nonfinite_fail_closed(self):
        self.assertEqual(select_final_candidate([candidate("x", hard=1)]), "NO_FEASIBLE_CANDIDATE")
        invalid = Candidate("nan", (float("nan"), 0.0, 0.0, 0.0, 0.0), {})
        with self.assertRaises(ValueError):
            select_final_candidate([invalid])

    def test_survivor_wrapper_prioritizes_feasible_and_reports_infeasible_fill(self):
        feasible = [candidate(f"f{i}", r3=1) for i in range(2)]
        infeasible = candidate("bad", r3=1, r4=1, hard=1)
        selected = select_survivors(feasible + [infeasible], "A1", 3)
        self.assertEqual({x.genome_hash for x in selected}, {"f0", "f1", "bad"})
        self.assertEqual(selected[-1].genome_hash, "bad")


if __name__ == "__main__":
    unittest.main()
