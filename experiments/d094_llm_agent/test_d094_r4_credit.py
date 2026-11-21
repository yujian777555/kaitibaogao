"""Independent unit tests for the new D-094 R4 credit and Fresh Train modules."""
from __future__ import annotations

import dataclasses
import unittest

from d094_evolution import Candidate
from d094_feedback_evolution import OPERATOR_NAMES, fixed_operator_probabilities
from d094_genome import AgentGenome
from d094_r4_credit import (
    PairedCreditNSGAII,
    PairedEpisode,
    PairedEvaluation,
    credit_probabilities,
    make_paired_evaluation,
    offspring_reward,
    paired_unit_rewards,
    r4_genome_pool,
    select_final_candidate,
)
from d094_r4_tasks import (
    fresh_train_isolation,
    r4_manifest,
    r4_tasks,
    task_sha256,
    validate_reachability,
)


PAIRS = tuple((task.task_id, seed) for task in r4_tasks() for seed in (301, 302))


def episodes(successes=0, recovery=None, violation=0, harm=0.0, error=False):
    recovery = successes if recovery is None else recovery
    return tuple(
        PairedEpisode(
            task_id=task,
            seed=seed,
            task_success=index < successes,
            recovery_success=index < recovery,
            constraint_violation=violation,
            harm=harm,
            execution_error=error,
        )
        for index, (task, seed) in enumerate(PAIRS)
    )


def evaluation(genome=None, successes=0, **kwargs):
    resources = {
        key: kwargs.pop(key)
        for key in ("tool_cost", "token_cost_upper_usd", "latency_seconds")
        if key in kwargs
    }
    return make_paired_evaluation(
        genome or AgentGenome(), episodes(successes=successes, **kwargs), **resources
    )


def failure_profile(genome):
    failing = genome.recovery_mode in {"retry_priority", "compensation_priority"}
    return {
        "counts": {"recovery_failure": int(failing)},
        "denominators": {"episode_count": 4, "recovery_attempt_count": 4},
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


def synthetic_evaluator(genome):
    quality = {
        "dependency_aware": 4,
        "verify_priority": 3,
        "retry_priority": 1,
        "compensation_priority": 0,
    }[genome.recovery_mode]
    if genome.planning_mode == "verification_first":
        quality = min(4, quality + 1)
    return make_paired_evaluation(
        genome,
        episodes(successes=quality),
        tool_cost=float(4 - quality),
        token_cost_upper_usd=0.001 * (5 - quality),
        latency_seconds=float(5 - quality),
        phenotype_hash=f"{genome.recovery_mode}:{genome.planning_mode}",
        failure_profile=failure_profile(genome),
    )


class TestPairedCreditMath(unittest.TestCase):
    def test_constraint_improvement_and_regression_dominate_quality(self):
        parent = evaluation(violation=2, successes=0)
        improved = evaluation(violation=1, successes=0)
        regressed = evaluation(violation=3, successes=4)
        self.assertEqual(offspring_reward(parent, improved), 1.0)
        self.assertEqual(offspring_reward(parent, regressed), -1.0)

    def test_quality_pareto_improvement_and_regression(self):
        parent = evaluation(successes=0, recovery=0, harm=0.5)
        child = evaluation(successes=4, recovery=4, harm=0.5)
        self.assertEqual(offspring_reward(parent, child), 1.0)
        self.assertEqual(offspring_reward(child, parent), -1.0)

    def test_resource_only_change_has_zero_primary_credit(self):
        parent = evaluation(successes=2, tool_cost=4.0, token_cost_upper_usd=0.1, latency_seconds=9.0)
        child = evaluation(successes=2, tool_cost=0.0, token_cost_upper_usd=0.0, latency_seconds=0.0)
        self.assertNotEqual(parent.candidate.objectives, child.candidate.objectives)
        self.assertEqual(offspring_reward(parent, child), 0.0)
        self.assertTrue(all(row["reward"] == 0.0 for row in paired_unit_rewards(parent, child).values()))

    def test_non_dominated_tradeoff_has_zero_credit(self):
        parent = evaluation(successes=0, harm=0.0)
        child = evaluation(successes=4, harm=1.0)
        self.assertEqual(offspring_reward(parent, child), 0.0)

    def test_missing_pair_and_execution_error_are_rejected(self):
        parent = evaluation()
        broken = PairedEvaluation(
            candidate=Candidate(AgentGenome(), (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
            episodes=episodes()[:1],
        )
        with self.assertRaisesRegex(ValueError, "identical"):
            offspring_reward(parent, broken)
        with self.assertRaisesRegex(ValueError, "execution error"):
            offspring_reward(parent, evaluation(error=True))

    def test_cold_start_and_exploration_floor(self):
        cold = credit_probabilities([])
        self.assertEqual(cold, fixed_operator_probabilities())
        probabilities = credit_probabilities([1.0], tau=0.25, epsilon=0.2)
        self.assertAlmostEqual(sum(probabilities.values()), 1.0)
        for value in probabilities.values():
            self.assertGreaterEqual(value, 0.2 / 6.0 - 1e-15)

    def test_sliding_window_uses_only_last_four_accepted_rewards(self):
        optimizer = PairedCreditNSGAII("paired_credit", window=4)
        optimizer._rewards["recovery_mutation"].extend([1.0, -1.0, -1.0, -1.0, -1.0])
        snapshot = optimizer._credit_snapshot()["recovery_mutation"]
        self.assertEqual(snapshot["accepted_rewards"], [-1.0, -1.0, -1.0, -1.0])
        self.assertEqual(snapshot["credit"], -1.0)


class TestPairedCreditSearch(unittest.TestCase):
    def test_three_arms_share_initial_population_and_evaluation_budget(self):
        reports = {}
        for mode in ("standard", "failure_feedback", "paired_credit"):
            optimizer = PairedCreditNSGAII(mode)
            optimizer.optimize(synthetic_evaluator, 2, 1, 711, PAIRS)
            evaluations = [row for row in optimizer.ledger if row["event_type"] == "evaluation"]
            self.assertEqual(len(evaluations), 4)
            self.assertEqual(len({row["genome_hash"] for row in evaluations}), 4)
            reports[mode] = (optimizer, evaluations)
        initial = {
            mode: [row["genome_hash"] for row in values[1] if row["generation"] == -1]
            for mode, values in reports.items()
        }
        self.assertEqual(initial["standard"], initial["failure_feedback"])
        self.assertEqual(initial["standard"], initial["paired_credit"])
        standard_events = {row["event_type"] for row in reports["standard"][0].ledger}
        self.assertNotIn("credit_update", standard_events)
        self.assertNotIn("feedback_update", standard_events)
        feedback_events = {row["event_type"] for row in reports["failure_feedback"][0].ledger}
        self.assertIn("feedback_update", feedback_events)
        self.assertNotIn("credit_update", feedback_events)
        credit_events = [row for row in reports["paired_credit"][0].ledger if row["event_type"] == "credit_update"]
        self.assertEqual(len(credit_events), 2)

    def test_credit_update_only_affects_later_proposals(self):
        optimizer = PairedCreditNSGAII("paired_credit")
        optimizer.optimize(synthetic_evaluator, 2, 2, 711, PAIRS)
        variations = [row for row in optimizer.ledger if row["event_type"] == "variation"]
        updates = [row for row in optimizer.ledger if row["event_type"] == "credit_update"]
        self.assertEqual(variations[0]["operator_probabilities"], fixed_operator_probabilities())
        for update in updates:
            index = next(
                i for i, row in enumerate(optimizer.ledger)
                if row["event_type"] == "credit_update" and row is update
            )
            variation = next(row for row in reversed(optimizer.ledger[:index]) if row["event_type"] == "variation")
            self.assertEqual(variation["operator_probabilities"], update["probabilities_before"])
            following = next(
                (row for row in optimizer.ledger[index + 1:] if row["event_type"] == "variation"),
                None,
            )
            if following is None:
                self.assertIs(update, updates[-1])
            else:
                self.assertEqual(following["operator_probabilities"], update["probabilities_after"])
            self.assertFalse(update["future_information_used"])
            self.assertFalse(update["resource_objectives_used"])

    def test_duplicate_never_evaluates_or_updates_credit(self):
        optimizer = PairedCreditNSGAII("paired_credit")
        optimizer.optimize(synthetic_evaluator, 2, 5, 3, PAIRS)
        duplicates = [row for row in optimizer.ledger if row["event_type"] == "duplicate_proposal"]
        self.assertTrue(duplicates)
        for row in duplicates:
            self.assertFalse(row["credit_updated"])
            self.assertFalse(row["evaluated"])
        accepted = [row for row in optimizer.ledger if row["event_type"] == "variation" and row["outcome"] == "ACCEPTED_FOR_EVALUATION"]
        updates = [row for row in optimizer.ledger if row["event_type"] == "credit_update"]
        self.assertEqual(len(accepted), len(updates))

    def test_reproducibility_and_complete_survivor_ledger(self):
        runs = []
        for _ in range(2):
            optimizer = PairedCreditNSGAII("paired_credit")
            optimizer.optimize(synthetic_evaluator, 2, 2, 711, PAIRS)
            runs.append(optimizer)
        self.assertEqual(runs[0].ledger, runs[1].ledger)
        self.assertEqual([row.candidate.genome_id for row in runs[0].archive], [row.candidate.genome_id for row in runs[1].archive])
        survivors = [row for row in runs[0].ledger if row["event_type"] == "survivor_selection"]
        self.assertEqual(len(survivors), 3)
        self.assertTrue(all(row["survivors"] for row in survivors))

    def test_evaluation_with_missing_frozen_pair_invalidates_run(self):
        optimizer = PairedCreditNSGAII("paired_credit")
        with self.assertRaisesRegex(ValueError, "complete paired"):
            optimizer.optimize(lambda genome: evaluation(genome), 2, 0, 711, PAIRS[:1])

    def test_pool_and_planning_mutation_keep_common_five_steps(self):
        self.assertEqual(len(r4_genome_pool()), 216)
        self.assertTrue(all(genome.max_plan_steps == 5 for genome in r4_genome_pool()))
        optimizer = PairedCreditNSGAII("paired_credit")
        optimizer.optimize(synthetic_evaluator, 2, 2, 711, PAIRS)
        variations = [row for row in optimizer.ledger if row["event_type"] == "variation"]
        self.assertTrue(all(row["offspring_genome"]["max_plan_steps"] == 5 for row in variations))
        planning = [row for row in variations if row["operator"] == "planning_mutation"]
        self.assertTrue(all(row["mutation_locus"] == "planning_mode" for row in planning))

    def test_final_selection_uses_all_archive_and_lexicographic_tiebreak(self):
        genomes = [AgentGenome(planning_mode=mode) for mode in ("direct", "stepwise", "verification_first")]
        candidates = [
            Candidate(genomes[0], (0.0, 0.0, 0.0, 0.0, 1.0, 0.1, 1.0)),
            Candidate(genomes[1], (0.0, 0.0, 0.0, 0.0, 1.0, 0.1, 1.0)),
            Candidate(genomes[2], (1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
        ]
        selected = select_final_candidate(candidates)
        expected = min(candidates[:2], key=lambda row: (row.objectives, row.genome_id))
        self.assertEqual(selected.genome_id, expected.genome_id)


class TestFreshTrain(unittest.TestCase):
    def test_manifest_hashes_and_historical_train_nonoverlap(self):
        manifest = r4_manifest()
        isolation = fresh_train_isolation()
        self.assertEqual(isolation["status"], "PASS")
        self.assertEqual(manifest["scenario_count"], 2)
        self.assertFalse(manifest["validation_included"])
        self.assertFalse(manifest["test_included"])
        self.assertEqual(len({task_sha256(task) for task in r4_tasks()}), 2)
        self.assertEqual(isolation["held_out_overlap_check"], "NOT_CHECKED_VALIDATION_TEST_ACCESS_FORBIDDEN")

    def test_local_reachability_for_every_task_and_seed_without_api(self):
        proof = validate_reachability()
        self.assertEqual(proof["status"], "PASS")
        self.assertEqual(len(proof["episodes"]), 4)
        self.assertTrue(all(row["task_success"] for row in proof["episodes"]))
        self.assertTrue(all(row["required_steps"] <= 5 for row in proof["episodes"]))
        self.assertTrue(all(row["llm_requests"] == 0 for row in proof["episodes"]))
        self.assertFalse(proof["api_used"])

    def test_task_specification_change_changes_hash(self):
        task = r4_tasks()[0]
        changed = dataclasses.replace(task, retry_failures=1)
        self.assertNotEqual(task_sha256(task), task_sha256(changed))


if __name__ == "__main__":
    unittest.main()
