"""Geometry and niching regression tests for canonical NSGA-III selection."""
import math
import random
import unittest

from ea import _associate_reference_directions, _nsga3_normalize, niching_select


class CanonicalNSGA3Tests(unittest.TestCase):
    def test_perpendicular_projection_divides_by_direction_norm_squared(self):
        associations, distances = _associate_reference_directions(
            [[2.0, 0.0]], [[1.0, 1.0]]
        )
        self.assertEqual(associations, [0])
        self.assertAlmostEqual(distances[0], math.sqrt(2.0), places=12)

    def test_extreme_points_are_taken_from_first_front(self):
        objectives = [(0.0, 1.0), (1.0, 0.0), (100.0, 100.0)]
        normalized, ideal, intercepts = _nsga3_normalize(
            objectives, extreme_indices=[0, 1]
        )
        self.assertEqual(ideal, [0.0, 0.0])
        self.assertAlmostEqual(intercepts[0], 1.0)
        self.assertAlmostEqual(intercepts[1], 1.0)
        self.assertGreater(normalized[2][0], 50.0)

    def test_previously_selected_front_contributes_to_niche_count(self):
        objectives = [(0.0, 1.0), (0.5, 0.5), (1.0, 0.0)]
        directions = [[1.0, 0.0], [0.0, 1.0]]
        order = niching_select(
            objectives, [1, 2], directions,
            selected=[0], rng=random.Random(7), extreme_indices=[0, 2],
        )
        self.assertEqual(order, [2, 1])

    def test_niching_is_deterministic_under_fixed_seed(self):
        objectives = [(0.0, 1.0), (0.3, 0.7), (0.7, 0.3), (1.0, 0.0)]
        directions = [[1.0, 0.0], [0.0, 1.0]]
        first = niching_select(
            objectives, [1, 2, 3], directions,
            selected=[0], rng=random.Random(13), extreme_indices=[0, 3],
        )
        second = niching_select(
            objectives, [1, 2, 3], directions,
            selected=[0], rng=random.Random(13), extreme_indices=[0, 3],
        )
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
