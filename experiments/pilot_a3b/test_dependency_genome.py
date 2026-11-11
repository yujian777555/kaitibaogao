"""Genome, variation, and public-view tests for the D-086 controller."""
import random
import unittest

from dependency_genome import (
    GenomePolicy,
    RecoveryGenome,
    crossover,
    make_initial_pool,
    mutate,
    random_genome,
)
from dependency_recovery import run_episode
from test_dependency_recovery import abort_with, route


class GenomeTests(unittest.TestCase):
    def test_initial_pool_is_shared_and_typed(self):
        first = make_initial_pool(711)
        second = make_initial_pool(711)
        self.assertEqual(len(first), 12)
        self.assertEqual([item.fingerprint() for item in first],
                         [item.fingerprint() for item in second])
        self.assertTrue(all(isinstance(item, RecoveryGenome) for item in first))
        self.assertNotEqual([item.fingerprint() for item in first],
                            [item.fingerprint() for item in make_initial_pool(822)])

    def test_mutation_changes_exactly_one_field_with_valid_types(self):
        original = random_genome(random.Random(17))
        for seed in range(8):
            child = mutate(original, random.Random(seed))
            self.assertIsInstance(child, RecoveryGenome)
            differences = [
                name for name in original.fingerprint()
                if getattr(original, name) != getattr(child, name)
            ]
            self.assertEqual(len(differences), 1)
        a, b = random_genome(random.Random(1)), random_genome(random.Random(2))
        child = crossover(a, b, random.Random(3))
        self.assertIsInstance(child, RecoveryGenome)
        for name in a.fingerprint():
            self.assertIn(getattr(child, name), (getattr(a, name), getattr(b, name)))

    def test_feedback_and_cost_weights_are_visible_in_behavior(self):
        cheap = RecoveryGenome(hint_weight=0, cost_weight=-2, failure_weight=-2,
                               dependency_weight=1, max_attempts=3)
        scenario = abort_with([
            route(outcomes=[False, False, True], cost=3, hint="HIGH"),
            route("alternate", outcomes=[True], cost=1, hint="LOW"),
        ])
        row = run_episode(GenomePolicy(cheap), scenario)
        self.assertEqual(row["class_success"], 1)
        self.assertEqual(row["action_cost"], 2)

    def test_pending_verification_ablation_cannot_claim_safe_completion(self):
        genome = RecoveryGenome(allow_verify=False)
        scenario = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        row = run_episode(GenomePolicy(genome), scenario)
        self.assertEqual(row["decision_count"], 24)
        self.assertEqual(row["runtime_forced_abort"], 1)
        self.assertEqual(row["pending_compensation"], 1)
        self.assertEqual(row["class_success"], 0)

    def test_retry_unknown_and_stop_pending_are_counted_not_hidden(self):
        scenario = abort_with([
            route(outcomes=[True], receipt="delayed", delay=1, idempotent=False),
        ])
        retry = RecoveryGenome(retry_unknown=True)
        row = run_episode(GenomePolicy(retry), scenario)
        self.assertEqual(row["duplicate_compensation"], 1)
        self.assertEqual(row["constraint_violation"], 1)
        stop = RecoveryGenome(stop_pending=True)
        row = run_episode(GenomePolicy(stop), scenario)
        self.assertEqual(row["pending_compensation"], 1)
        self.assertEqual(row["correct_escalation"], 0)


if __name__ == "__main__":
    unittest.main()
