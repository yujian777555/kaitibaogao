"""D-088 recovery module regression tests — unittest compatible, no LLM/API."""
from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))

from d088_genome import (  # noqa: E402
    D088RecoveryGenome, random_genome, mutate, crossover, arm_flags, arm_label,
)
from d088_policies import D088RecoveryPolicy, build_graph, cycle_tools, topo_order  # noqa: E402
from d088_scenarios import build_manifest, validate_manifest, make_scenario  # noqa: E402
from d088_experiment import evaluate_rows, summarize_rows  # noqa: E402


class TestGenome(unittest.TestCase):
    def test_arm_flags_fixed_under_mutation(self):
        for arm in ("L", "A", "B", "C", "AB", "AC", "BC", "ABC"):
            rng = random.Random(7)
            g = random_genome(rng, arm)
            for _ in range(50):
                g = mutate(g, rng)
                self.assertEqual(arm_label(g), arm, f"mutation flipped flags for {arm}")
                g = crossover(g, random_genome(rng, arm), rng)
                self.assertEqual(arm_label(g), arm, f"crossover flipped flags for {arm}")

    def test_arm_label_roundtrip(self):
        for arm in ("L", "A", "B", "C", "AB", "AC", "BC", "ABC"):
            self.assertEqual(arm_label(D088RecoveryGenome(**arm_flags(arm))), arm)


class TestScenarios(unittest.TestCase):
    def test_development_manifest_valid(self):
        m = build_manifest()
        self.assertTrue(validate_manifest(m)["ok"])
        self.assertEqual(m["scenario_count"], 96)
        self.assertTrue(all(s["scenario_id"].startswith("d088r|train|") for s in m["scenarios"]))

    def test_fresh_manifest_valid_and_disjoint(self):
        dev = {s["scenario_id"] for s in build_manifest()["scenarios"]}
        fresh = build_manifest(tier="fresh")
        self.assertTrue(validate_manifest(fresh)["ok"])
        self.assertEqual(fresh["scenario_count"], 80)
        ids = {s["scenario_id"] for s in fresh["scenarios"]}
        self.assertFalse(ids & dev, "fresh ids must not overlap development ids")

    def test_labels(self):
        for family in ("t01_CHAIN_REVERSE", "t02_DIAMOND"):
            for stratum, label in (("D1_RECOVERABLE_TIMEOUT", "R1"),
                                   ("D3_DEPENDENT_ABORT", "R3"),
                                   ("D4_BLOCKED_COMPENSATION", "R4")):
                sc = make_scenario(family, stratum, 0)
                self.assertEqual(sc["label"], label)


class TestGraphUtils(unittest.TestCase):
    def test_cycle_detection(self):
        graph = {"A": ["B"], "B": ["A"], "C": []}
        self.assertEqual(cycle_tools(graph), {"A", "B"})

    def test_topo_order(self):
        graph = {"A": ["B"], "B": ["C"], "C": []}
        order = topo_order(graph, set())
        self.assertLess(order.index("C"), order.index("B"))
        self.assertLess(order.index("B"), order.index("A"))


class TestPolicySafety(unittest.TestCase):
    def _run_arm(self, arm):
        m = build_manifest()["scenarios"][:32]
        g = random_genome(random.Random(11), arm)
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), m)
        s = summarize_rows(rows)
        return s

    def test_all_arms_zero_hard_violations(self):
        for arm in ("L", "A", "B", "C", "AB", "AC", "BC", "ABC"):
            s = self._run_arm(arm)
            self.assertEqual(s["constraint_violation"], 0, arm)
            self.assertEqual(s["duplicate_compensation"], 0, arm)
            self.assertEqual(s["pending_compensation"], 0, arm)


if __name__ == "__main__":
    unittest.main()
