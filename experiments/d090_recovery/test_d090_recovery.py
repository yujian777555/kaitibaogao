"""D-090 deterministic mechanism tests."""
from __future__ import annotations

import random
import unittest

from d090_genome import D090Genome, base_genome, crossover_blocks, mutate_d090, random_d090_genome
from d090_policies import D090Policy
from d090_scenarios import FAMILIES, STRATA, build_manifest


class TestD090Genome(unittest.TestCase):
    def test_rule_genome_is_state_conditioned(self):
        g = random_d090_genome(random.Random(7))
        self.assertIn(g.pair_rule, (0, 1, 2))
        self.assertIn(g.fallback_mode, (0, 1, 2))
        self.assertIn(g.completion_mode, (0, 1, 2))
        self.assertIn(g.harm_order_mode, (0, 1, 2))

    def test_mutation_and_block_crossover_preserve_base(self):
        a = random_d090_genome(random.Random(1))
        b = random_d090_genome(random.Random(2))
        c = mutate_d090(a, random.Random(3))
        d = crossover_blocks(a, b, random.Random(4))
        self.assertEqual(c.hint_weight, a.hint_weight)
        self.assertIn(d.pair_rule, (a.pair_rule, b.pair_rule))
        self.assertEqual(d.stop_mode, a.stop_mode)


class TestD090Manifest(unittest.TestCase):
    def test_train_manifest_is_new_and_complete(self):
        manifest = build_manifest()
        self.assertEqual(manifest["scenario_count"], len(FAMILIES) * len(STRATA) * 4)
        self.assertTrue(all(s["split"] == "train" for s in manifest["scenarios"]))
        self.assertTrue(all(s["scenario_id"].startswith("d090r|train|") for s in manifest["scenarios"]))
        self.assertFalse(any("d089r" in s["scenario_id"] for s in manifest["scenarios"]))
        self.assertFalse(manifest["test_included"])


class TestD090Policy(unittest.TestCase):
    def test_default_policy_exposes_structural_rules(self):
        policy = D090Policy(base_genome())
        self.assertTrue(policy.pair_race_alternate)
        self.assertTrue(policy.exhaustive_fallback)
        self.assertTrue(policy.completion_gate)


if __name__ == "__main__":
    unittest.main()
