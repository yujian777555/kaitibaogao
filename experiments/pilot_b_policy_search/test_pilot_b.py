import ast
import random
import unittest
from pathlib import Path

from experiments.pilot_a2_multitool.pilot_a2 import TOOLS, PROFILES, make_episode
from experiments.pilot_b_policy_search.pilot_b import (
    GENE_SIZES, MANUAL_V1, MANUAL_V2, TRAIN_SEEDS, VALIDATION_SEEDS,
    TEST_SEEDS, EVAL_BUDGET, random_genome, repair_contracts, evaluate,
    execute_genome
)

class PilotBTests(unittest.TestCase):
    def test_fresh_seed_panels_do_not_overlap_pilot_a2(self):
        self.assertTrue(set(TRAIN_SEEDS).isdisjoint(range(100)))
        self.assertTrue(set(VALIDATION_SEEDS).isdisjoint(range(100)))
        self.assertTrue(set(TEST_SEEDS).isdisjoint(range(100)))
        self.assertTrue(set(TRAIN_SEEDS).isdisjoint(TEST_SEEDS))
        self.assertTrue(set(VALIDATION_SEEDS).isdisjoint(TEST_SEEDS))

    def test_genome_shape_and_bounds(self):
        g = random_genome(random.Random(7))
        self.assertEqual(len(g), len(GENE_SIZES))
        for value, size in zip(g, GENE_SIZES):
            self.assertGreaterEqual(value, 0)
            self.assertLess(value, size)

    def test_contract_repair_enforces_safety_invariants(self):
        rng = random.Random(19)
        for _ in range(500):
            g = repair_contracts(random_genome(rng))
            self.assertEqual(g[1], 0)       # bounded verification for non-idempotent timeout
            self.assertEqual(g[4], 0)       # repair schema
            self.assertEqual(g[5], 0)       # wait through retry-after
            self.assertGreaterEqual(g[6], 2)
            self.assertEqual(g[7], 0)       # keyed idempotency key
            self.assertGreaterEqual(g[8], 2)
            if g[2] == 1:
                self.assertGreaterEqual(g[3], 2)

    def test_manual_controllers_are_valid_genomes(self):
        for g in (MANUAL_V1, MANUAL_V2):
            self.assertEqual(len(g), len(GENE_SIZES))
            self.assertEqual(g, repair_contracts(g))

    def test_manual_v2_has_zero_violations_on_small_fresh_panel(self):
        rows = [
            execute_genome(make_episode(tool, profile, seed), MANUAL_V2)
            for tool in TOOLS for profile in PROFILES for seed in range(1000, 1005)
        ]
        self.assertEqual(sum(r["invariant_violation"] for r in rows), 0)

    def test_non_oracle_genome_executor_does_not_read_hidden_state(self):
        path = Path(__file__).with_name("pilot_b.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "execute_genome")
        hidden = {"hidden_outcome", "effects", "visibility_delay", "compensation_available"}
        for node in ast.walk(fn):
            if isinstance(node, ast.Attribute):
                self.assertNotIn(node.attr, hidden)
            if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
                self.assertNotIn(node.slice.value, hidden)

    def test_cost_floor_and_evaluation_budget_are_fixed(self):
        self.assertEqual(EVAL_BUDGET, 160)
        self.assertEqual(TRAIN_SEEDS, tuple(range(1000, 1040)))
        self.assertEqual(VALIDATION_SEEDS, tuple(range(1100, 1120)))
        self.assertEqual(TEST_SEEDS, tuple(range(1120, 1160)))

if __name__ == "__main__":
    unittest.main()
