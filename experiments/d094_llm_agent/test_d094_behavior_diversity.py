"""D-094 behavior representation, distances and Diversity-Aware NSGA-II tests."""
from __future__ import annotations

import unittest

from d094_behavior import (
    behavior_representation,
    feature_distance,
    sequence_edit_distance,
)
from d094_diversity import behavior_novelty, compare_selectors, diversity_survivors
from d094_evolution import Candidate
from d094_genome import enumerate_genomes, genome_sha256


def episode(
    tool_name: str,
    *,
    success: bool = True,
    terminal: str = "COMPLETED",
    rationale: str = "same",
) -> dict:
    return {
        "events": [
            {
                "event_type": "decision",
                "payload": {
                    "action": "tool_call",
                    "tool_name": tool_name,
                    "tool_arguments": {},
                    "rationale": rationale,
                },
            },
            {
                "event_type": "tool_result",
                "payload": {
                    "tool_name": tool_name,
                    "observation": {"status": "OK" if success else "FAILED"},
                    "success": success,
                    "done": terminal == "COMPLETED",
                    "before_state": {"step": 0},
                    "after_state": {"step": 1},
                },
            },
        ],
        "agent_status": terminal,
        "final_public_observation": {"state": {"completed": terminal == "COMPLETED"}},
    }


class TestBehaviorRepresentation(unittest.TestCase):
    def test_edit_distance_ignores_rationale_but_detects_tool_change(self):
        first = behavior_representation(**episode("verify_state"))
        second = behavior_representation(**episode("retry_primary"))
        wording = behavior_representation(
            **episode("verify_state", rationale="different public wording")
        )
        self.assertEqual(sequence_edit_distance(first, first), 0.0)
        self.assertEqual(sequence_edit_distance(first, wording), 0.0)
        self.assertEqual(sequence_edit_distance(first, second), 1.0)

    def test_two_action_sequences_have_known_normalized_edit_distance(self):
        first = behavior_representation(**episode("verify_state"))
        second = behavior_representation(**episode("verify_state"))
        second["sequence"].extend(second["sequence"])
        self.assertEqual(sequence_edit_distance(first, second), 0.5)

    def test_weighted_feature_distance_has_known_terminal_abort_answer(self):
        first = behavior_representation(
            **episode("verify_state", terminal="PREMATURE_FINISH")
        )
        second = behavior_representation(
            **episode("verify_state", terminal="MAX_STEPS")
        )
        self.assertAlmostEqual(feature_distance(first, second), 1 / 13)
        self.assertEqual(first["features"]["state_transition_count"], 1)

    def test_identical_behavior_has_identical_canonical_hash(self):
        first = behavior_representation(**episode("verify_state"))
        second = behavior_representation(
            **episode("verify_state", rationale="not behavior")
        )
        self.assertEqual(first["canonical_sha256"], second["canonical_sha256"])


class TestDiversitySelection(unittest.TestCase):
    def candidates(self) -> list[Candidate]:
        genomes = enumerate_genomes()[:4]
        behaviors = [
            behavior_representation(**episode("verify_state")),
            behavior_representation(**episode("verify_state")),
            behavior_representation(**episode("retry_primary")),
            behavior_representation(**episode("compensate_primary")),
        ]
        return [
            Candidate(
                genome=genome,
                objectives=(1.0, 1.0),
                phenotype_hash=behavior["canonical_sha256"],
                behavior=behavior,
            )
            for genome, behavior in zip(genomes, behaviors)
        ]

    def test_full_selector_controls_exact_duplicate_behavior(self):
        selected = diversity_survivors(self.candidates(), 2, method="full")
        self.assertEqual(len({candidate.phenotype_hash for candidate in selected}), 2)
        standard = diversity_survivors(self.candidates(), 2, method="standard")
        self.assertEqual(len({candidate.phenotype_hash for candidate in standard}), 1)

    def test_genome_diversity_is_measured_separately_from_behavior(self):
        selected = diversity_survivors(self.candidates(), 2, method="genome")
        self.assertEqual(len({candidate.genome_id for candidate in selected}), 2)
        comparison = compare_selectors(self.candidates(), 2)
        self.assertIn("unique_phenotypes", comparison["genome"])
        self.assertEqual(comparison["genome"]["unique_objective_vectors"], 1)

    def test_all_three_behavior_designs_preserve_distinct_phenotypes(self):
        for method in (
            "crowding_novelty",
            "behavior_tiebreak",
            "behavior_cluster",
            "phenotype",
        ):
            with self.subTest(method=method):
                selected = diversity_survivors(self.candidates(), 2, method=method)
                self.assertEqual(
                    len({candidate.phenotype_hash for candidate in selected}), 2
                )

    def test_pareto_and_hard_constraints_are_not_overridden(self):
        genomes = enumerate_genomes()
        good_behavior = behavior_representation(**episode("verify_state"))
        bad_behavior = behavior_representation(**episode("compensate_primary"))
        dominating = Candidate(
            genomes[0],
            (0.0, 0.0),
            phenotype_hash=good_behavior["canonical_sha256"],
            behavior=good_behavior,
        )
        dominated = Candidate(
            genomes[1],
            (1.0, 1.0),
            phenotype_hash=bad_behavior["canonical_sha256"],
            behavior=bad_behavior,
        )
        invalid = Candidate(
            genomes[2],
            (-1.0, -1.0),
            constraint_violation=1,
            phenotype_hash=bad_behavior["canonical_sha256"],
            behavior=bad_behavior,
        )
        selected = diversity_survivors(
            [dominated, invalid, dominating], 1, method="full"
        )
        self.assertEqual(selected, [dominating])

    def test_novelty_is_zero_for_duplicate_or_singleton(self):
        candidates = self.candidates()[:2]
        self.assertEqual(behavior_novelty(candidates[0], candidates), 0.0)
        self.assertEqual(behavior_novelty(candidates[0], [candidates[0]]), 0.0)

    def test_selector_comparison_reports_all_four_control_identities(self):
        result = compare_selectors(self.candidates(), 2)
        self.assertEqual(set(result), {"standard", "genome", "phenotype", "full"})
        self.assertEqual(result["standard"]["unique_phenotypes"], 1)
        self.assertEqual(result["full"]["unique_phenotypes"], 2)


if __name__ == "__main__":
    unittest.main()
