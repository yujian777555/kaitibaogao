"""D-092 typed-genome adapter and identity tests; no Train rollouts."""
from __future__ import annotations

import hashlib
import json
import random
import unittest

from d092_genome import (
    BLOCKS,
    TypedGenome,
    canonical_json_bytes,
    compensation_attempt_id,
    enumerate_typed_genomes,
    episode_reference,
    genome_sha256,
    probe_typed_genomes,
    typed_crossover,
    typed_mutation,
)


class TestCanonicalSerialization(unittest.TestCase):
    def test_canonical_json_is_compact_sorted_and_utf8(self):
        payload = {"场景": "甲", "a": [None, True, 2]}
        self.assertEqual(
            canonical_json_bytes(payload),
            '{"a":[null,true,2],"场景":"甲"}'.encode("utf-8"),
        )

    def test_float_normalization_and_nonfinite_rejection(self):
        self.assertEqual(canonical_json_bytes({"x": -0.0}), b'{"x":0.0}')
        with self.assertRaises(ValueError):
            canonical_json_bytes({"x": float("nan")})

    def test_identity_hash_known_vector(self):
        payload = {
            "seed": 711,
            "unique_ordinal": 0,
            "genome_sha256": "g",
            "scenario_id": "场景",
        }
        expected_bytes = '{"genome_sha256":"g","scenario_id":"场景","seed":711,"unique_ordinal":0}'.encode("utf-8")
        self.assertEqual(canonical_json_bytes(payload), expected_bytes)
        episode = episode_reference(711, 0, "g", "场景")
        self.assertEqual(episode, hashlib.sha256(expected_bytes).hexdigest())
        attempt_payload = {"episode_reference": episode, "dispatch_ordinal": 0}
        self.assertEqual(
            compensation_attempt_id(episode, 0),
            hashlib.sha256(canonical_json_bytes(attempt_payload)).hexdigest(),
        )

    def test_same_scenario_ordinal_is_distinct_across_genomes(self):
        keys = set()
        for ordinal in range(12):
            genome_hash = hashlib.sha256(f"genome-{ordinal}".encode()).hexdigest()
            episode = episode_reference(711, ordinal, genome_hash, "fixed")
            keys.add((episode, compensation_attempt_id(episode, 0)))
        self.assertEqual(len(keys), 12)


class TestTypedAdapter(unittest.TestCase):
    def test_default_typed_genome_expands_to_expected_controls(self):
        genome = TypedGenome()
        full = genome.to_d090()
        self.assertEqual(full.pair_rule, 0)
        self.assertTrue(full.pair_race_alternate)
        self.assertTrue(full.exhaustive_fallback)
        self.assertEqual(full.fallback_mode, 2)
        self.assertTrue(full.completion_gate)
        self.assertEqual(full.completion_mode, 1)
        self.assertTrue(full.harm_first_ordering)
        self.assertEqual(full.harm_order_mode, 1)
        self.assertEqual(full.harm_budget_threshold, 8)
        self.assertEqual(full.delay_probe_wait, 1.0)

    def test_all_144_mappings_are_unique_and_roundtrip(self):
        typed = enumerate_typed_genomes()
        self.assertEqual(len(typed), 144)
        full_hashes = {genome_sha256(g.to_d090().fingerprint()) for g in typed}
        self.assertEqual(len(full_hashes), 144)
        for genome in typed:
            self.assertEqual(TypedGenome.from_d090(genome.to_d090()), genome)

    def test_off_false_and_none_cannot_be_reenabled_by_base_modes(self):
        off = TypedGenome(cycle_mode="OFF").to_d090()
        self.assertEqual((off.pair_rule, off.pair_race_alternate), (1, False))
        no_fallback = TypedGenome(fallback_enabled=False).to_d090()
        self.assertFalse(no_fallback.exhaustive_fallback or no_fallback.fallback_mode == 2)
        no_completion = TypedGenome(completion_guarded=False).to_d090()
        self.assertFalse(no_completion.completion_gate or no_completion.completion_mode >= 1)
        no_harm = TypedGenome(harm_reorder_budget=None).to_d090()
        self.assertFalse(no_harm.harm_first_ordering)
        self.assertEqual(no_harm.harm_order_mode, 0)
        self.assertEqual(no_harm.harm_budget_threshold, 8)

    def test_probe_expansions_preserve_single_mechanism_contrasts(self):
        probes = probe_typed_genomes()
        self.assertEqual(list(probes), [f"P{i:02d}" for i in range(10)])
        p01 = probes["P01"].to_d090().fingerprint()
        p03 = probes["P03"].to_d090().fingerprint()
        self.assertEqual(
            {k for k in p01 if p01[k] != p03[k]},
            {"exhaustive_fallback", "fallback_mode"},
        )
        p06 = probes["P06"].to_d090().fingerprint()
        p07 = probes["P07"].to_d090().fingerprint()
        self.assertEqual(
            {k for k in p06 if p06[k] != p07[k]},
            {"harm_budget_threshold"},
        )
        self.assertEqual(probes["P07"].harm_reorder_budget, 12)

    def test_invalid_values_are_rejected(self):
        with self.assertRaises(ValueError):
            TypedGenome(cycle_mode="UNKNOWN")
        with self.assertRaises(ValueError):
            TypedGenome(harm_reorder_budget=7)

    def test_mutation_changes_one_locus_and_crossover_preserves_blocks(self):
        genome = TypedGenome()
        for block in BLOCKS:
            mutant = typed_mutation(genome, block, random.Random(7))
            self.assertNotEqual(mutant, genome)
            self.assertTrue(all(getattr(mutant, f) in genome.allowed_values(f) for f in BLOCKS[block]))
        other = TypedGenome(cycle_mode="OFF", fallback_enabled=False, completion_guarded=False, harm_reorder_budget=None, probe_wait=2.0)
        child = typed_crossover(genome, other, random.Random(9))
        for block, fields in BLOCKS.items():
            self.assertIn(tuple(getattr(child, f) for f in fields), [tuple(getattr(genome, f) for f in fields), tuple(getattr(other, f) for f in fields)])


if __name__ == "__main__":
    unittest.main()
