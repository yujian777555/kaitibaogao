"""D-094 B3/B4/B5 integrated evolution and audit-ledger tests."""
from __future__ import annotations

import unittest

from d094_adaptive_evolution import AdaptiveNSGAII, run_synthetic_ablation
from d094_behavior import behavior_representation
from d094_evolution import Candidate
from d094_feedback_evolution import fixed_operator_probabilities
from d094_genome import AgentGenome


def public_profile(failing: bool) -> dict:
    return {
        "counts": {"recovery_failure": int(failing)},
        "denominators": {"episode_count": 1, "recovery_attempt_count": 1},
        "rates": {
            "planning_failure": 0.0,
            "tool_call_failure": 0.0,
            "dependency_failure": 0.0,
            "recovery_failure": float(failing),
            "verification_failure": 0.0,
            "task_incompletion": float(failing),
            "unnecessary_tool_call": 0.0,
        },
    }


def behavior_for(genome: AgentGenome) -> dict:
    tool = {
        "retry_priority": "retry_primary",
        "verify_priority": "verify_state",
        "compensation_priority": "compensate_primary",
        "dependency_aware": "inspect_state",
    }[genome.recovery_mode]
    return behavior_representation(
        [
            {
                "event_type": "decision",
                "payload": {
                    "action": "tool_call",
                    "tool_name": tool,
                    "tool_arguments": {},
                },
            },
            {
                "event_type": "tool_result",
                "payload": {
                    "tool_name": tool,
                    "success": True,
                    "observation": {"status": "OK"},
                    "done": True,
                },
            },
        ],
        agent_status="COMPLETED",
    )


def evaluate(genome: AgentGenome) -> Candidate:
    behavior = behavior_for(genome)
    failing = True
    return Candidate(
        genome=genome,
        objectives=(float(genome.max_plan_steps), float(genome.max_plan_steps)),
        phenotype_hash=behavior["canonical_sha256"],
        behavior=behavior,
        failure_profile=public_profile(failing),
    )


class TestAdaptiveEvolution(unittest.TestCase):
    def test_standard_arm_uses_fixed_uniform_operator_control(self):
        optimizer = AdaptiveNSGAII(mode="standard")
        optimizer.optimize(evaluate, population_size=4, generations=1, seed=42)
        variations = [
            event for event in optimizer.ledger if event["event_type"] == "variation"
        ]
        self.assertTrue(variations)
        self.assertEqual(
            variations[0]["operator_probabilities"], fixed_operator_probabilities()
        )

    def test_feedback_arm_uses_real_candidate_profile_and_dynamic_probabilities(self):
        optimizer = AdaptiveNSGAII(mode="feedback")
        optimizer.optimize(evaluate, population_size=4, generations=1, seed=42)
        variations = [
            event for event in optimizer.ledger if event["event_type"] == "variation"
        ]
        self.assertTrue(
            any(
                event["operator_probabilities"] != fixed_operator_probabilities()
                for event in variations
            )
        )
        self.assertIn("failure_profile", variations[0])
        self.assertIn(
            "feedback_update", {event["event_type"] for event in optimizer.ledger}
        )

    def test_mutation_ledger_has_locus_before_after_and_intermediate_genome(self):
        optimizer = AdaptiveNSGAII(mode="combined")
        optimizer.optimize(evaluate, population_size=4, generations=2, seed=42)
        variations = [
            event for event in optimizer.ledger if event["event_type"] == "variation"
        ]
        mutations = [event for event in variations if event["operator"] != "crossover"]
        self.assertTrue(mutations)
        for event in mutations:
            self.assertIn(event["mutation_locus"], AgentGenome().to_dict())
            self.assertIn("before_value", event)
            self.assertIn("after_value", event)
            self.assertIn("intermediate_genome", event)
            self.assertIn("offspring_genome", event)
            self.assertEqual(len(event["parent_genome_hashes"]), 2)

    def test_survivor_ledger_contains_phenotype_and_generation_diversity(self):
        optimizer = AdaptiveNSGAII(mode="diversity")
        optimizer.optimize(evaluate, population_size=4, generations=1, seed=42)
        survivors = [
            event
            for event in optimizer.ledger
            if event["event_type"] == "survivor_selection" and event["generation"] >= 0
        ]
        self.assertTrue(survivors)
        for event in survivors:
            self.assertEqual(event["selection_method"], "full")
            self.assertIn("genotype_diversity", event)
            self.assertIn("phenotype_diversity", event)
            self.assertIn("performance_diversity", event)
            for survivor in event["survivors"]:
                self.assertIn("phenotype_hash", survivor)
                self.assertIn("genome_sha256", survivor)

    def test_b5_combines_only_feedback_and_diversity(self):
        optimizer = AdaptiveNSGAII(mode="combined")
        optimizer.optimize(evaluate, population_size=4, generations=1, seed=42)
        self.assertEqual(optimizer.mechanisms, ["feedback", "diversity"])
        survivor = next(
            event
            for event in optimizer.ledger
            if event["event_type"] == "survivor_selection" and event["generation"] >= 0
        )
        self.assertEqual(survivor["selection_method"], "full")
        variation = next(
            event for event in optimizer.ledger if event["event_type"] == "variation"
        )
        self.assertIn("failure_profile", variation)

    def test_duplicate_proposals_never_trigger_duplicate_evaluation(self):
        optimizer = AdaptiveNSGAII(mode="combined")
        optimizer.optimize(evaluate, population_size=3, generations=4, seed=0)
        evaluations = [
            event for event in optimizer.ledger if event["event_type"] == "evaluation"
        ]
        ids = [event["genome_hash"] for event in evaluations]
        self.assertEqual(len(ids), len(set(ids)))
        duplicates = [
            event
            for event in optimizer.ledger
            if event["event_type"] == "duplicate_proposal"
        ]
        for event in duplicates:
            self.assertEqual(event["outcome"], "REJECTED_WITHOUT_EVALUATION")

    def test_synthetic_ablation_reports_all_controls_without_performance_claim(self):
        result = run_synthetic_ablation(
            evaluate, population_size=4, generations=1, seed=42
        )
        self.assertEqual(
            set(result),
            {"standard", "genome", "phenotype", "feedback", "diversity", "combined"},
        )
        for mode, report in result.items():
            self.assertEqual(report["scope"], "SYNTHETIC_ONLY")
            self.assertIn("unique_survivor_phenotypes", report)
            self.assertIn("evaluation_count", report)


if __name__ == "__main__":
    unittest.main()
