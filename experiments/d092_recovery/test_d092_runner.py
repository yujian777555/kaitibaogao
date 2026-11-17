"""D-092 five-arm runner tests with synthetic aggregate evaluators only."""
from __future__ import annotations

import hashlib
import random
import unittest
from unittest import mock

from d092_evaluator import HARD_FIELDS, assert_optimizer_view
from d092_genome import TypedGenome, canonical_json_bytes, genome_sha256, sha256_hex
from d092_runner import (
    ARMS,
    ATTEMPT_CAP,
    MU,
    ROUNDS,
    SEEDS,
    UNIQUE_TARGET,
    BudgetError,
    BudgetLedger,
    EvaluationInterrupted,
    StreamRNG,
    derive_stream_seed,
    m1_equivalence,
    run_arm,
)


class SyntheticEvaluator:
    episodes_per_genome = 2

    def __init__(self, hard=0):
        self.hard = hard
        self.calls = []

    def evaluate(self, genome, seed, unique_ordinal):
        self.calls.append((genome_sha256(genome), seed, unique_ordinal))
        cycle = ("OFF", "FILTER_ONLY", "ALT_AND_FILTER").index(genome.cycle_mode)
        harm = 0 if genome.harm_reorder_budget is None else genome.harm_reorder_budget
        fitness = {
            "R3": min(1.0, (cycle + int(genome.fallback_enabled) + int(genome.completion_guarded)) / 3),
            "R4": 1.0 - (harm / 24),
            "CondRec": 1.0 - (genome.probe_wait / 4),
            "Harm": harm / 12,
            "RecoveryCost": cycle + genome.probe_wait + int(genome.fallback_enabled),
        }
        hard = {name: self.hard for name in HARD_FIELDS}
        typed = genome.to_dict()
        trace = sha256_hex({"trace": typed})
        outcome = sha256_hex({"outcome": typed})
        return {
            "genome_sha256": genome_sha256(genome),
            "fitness": fitness,
            "hard_constraints": hard,
            "constraint_episode_count": 2 if self.hard else 0,
            "contract_blocked_attempts": int(not genome.fallback_enabled),
            "dependency_blocked_attempts": cycle,
            "feedback_marginals": {
                "row_count": 2,
                "attempt_count": cycle + int(not genome.fallback_enabled),
                "failure_attempt_count": cycle + int(not genome.fallback_enabled),
                "dependency_blocked_attempt_count": cycle,
                "pending_row_count": int(not genome.completion_guarded),
                "runtime_abort_row_count": 0,
                "unsuccessful_escalation_row_count": int(genome.harm_reorder_budget is None),
                "avoidable_harm_sum": harm,
            },
            "phenotype_hashes": {"trace": trace, "outcome": outcome, "joint": sha256_hex({"trace": trace, "outcome": outcome})},
        }


class TestBudgetAndRNG(unittest.TestCase):
    def test_frozen_budget_constants(self):
        self.assertEqual((MU, ROUNDS, UNIQUE_TARGET, ATTEMPT_CAP), (12, 7, 96, 384))
        self.assertEqual(ARMS, ("A0", "A1", "A2", "A3", "A4"))
        self.assertEqual(SEEDS, (711, 822, 933, 1044, 1155))

    def test_stream_seed_uses_exact_utf8_sha_prefix(self):
        expected = int.from_bytes(hashlib.sha256(b"D092-R2|711|variation").digest()[:8], "big")
        self.assertEqual(derive_stream_seed(711, "variation"), expected)

    def test_direct_integer_seed_does_not_call_system_entropy(self):
        with mock.patch("random._os.urandom", side_effect=AssertionError("system entropy used")):
            stream = StreamRNG(711, "variation", "A1")
            self.assertEqual(stream.random(), random.Random(derive_stream_seed(711, "variation")).random())

    def test_duplicate_consumes_attempt_and_cache_but_not_new_rollout(self):
        evaluator = SyntheticEvaluator()
        ledger = BudgetLedger(evaluator, "A1", 711, episodes_per_genome=2)
        genome = TypedGenome()
        first = ledger.offer(genome, 0)
        second = ledger.offer(genome, 0)
        self.assertEqual(first["status"], "NEW_UNIQUE")
        self.assertEqual(second["status"], "DUPLICATE_CACHED")
        self.assertEqual(len(evaluator.calls), 1)
        self.assertEqual(ledger.attempts, 2)
        self.assertEqual(ledger.unique_evaluations, 1)
        self.assertEqual(ledger.cache_hits, 1)
        self.assertEqual(ledger.duplicate_proposals, 1)
        self.assertEqual(ledger.full_episodes, 2)

    def test_attempt_cap_and_interruption_fail_closed(self):
        evaluator = SyntheticEvaluator()
        ledger = BudgetLedger(evaluator, "A1", 711, attempt_cap=0, episodes_per_genome=2)
        with self.assertRaises(BudgetError):
            ledger.offer(TypedGenome(), 0)

        def interrupted(genome, seed, ordinal):
            raise EvaluationInterrupted(1)
        ledger = BudgetLedger(interrupted, "A1", 711, episodes_per_genome=2)
        with self.assertRaises(EvaluationInterrupted):
            ledger.offer(TypedGenome(), 0)
        self.assertEqual(ledger.partial_episodes, 1)
        self.assertIn("EVALUATION_INTERRUPT", ledger.invalid_reason)


class TestFiveArmSyntheticIntegration(unittest.TestCase):
    def test_all_five_arms_share_unique_budget_and_emit_json_audits(self):
        results = {}
        for arm in ARMS:
            evaluator = SyntheticEvaluator()
            result = run_arm(arm, 711, evaluator, episodes_per_genome=2)
            self.assertIn(result["status"], {"VALID", "INVALID"})
            if result["status"] == "VALID":
                self.assertEqual(result["budget"]["unique_evaluations"], 96)
                self.assertEqual(result["budget"]["full_episodes"], 192)
                self.assertNotEqual(result["final_candidate"]["status"], "NO_FEASIBLE_CANDIDATE")
                assert_optimizer_view(result["archive"][0]["optimizer_reward_view"])
            else:
                self.assertEqual(result["final_candidate"]["status"], "INVALID")
                self.assertLess(result["budget"]["unique_evaluations"], 96)
                self.assertTrue(result["proposal_log"])
                self.assertTrue(result["invalid_reason"])
            self.assertEqual(result["budget"]["partial_episodes"], 0)
            self.assertLessEqual(result["budget"]["attempts"], 384)
            self.assertEqual(len(result["feedback"]), len(result["rounds"]))
            canonical_json_bytes(result)
            results[arm] = result
        self.assertEqual(results["A0"]["status"], "VALID")
        self.assertEqual(results["A0"]["budget"]["attempts"], 96)
        self.assertEqual(results["A0"]["budget"]["cache_hits"], 0)
        self.assertTrue(all(row["status"] == "NO_SURVIVOR" for row in results["A0"]["survivor_log"]))
        self.assertNotEqual(
            [row["genome_sha256"] for row in results["A0"]["proposal_log"]],
            [row["genome_sha256"] for row in results["A1"]["proposal_log"]],
        )

    def test_a1_a4_have_identical_search_trajectories(self):
        first = run_arm("A1", 711, SyntheticEvaluator(), episodes_per_genome=2)
        second = run_arm("A4", 711, SyntheticEvaluator(), episodes_per_genome=2)
        self.assertTrue(m1_equivalence(first, second))
        self.assertEqual(first["status"], second["status"])
        self.assertEqual(first["final_candidate"], second["final_candidate"])
        self.assertTrue(all(row["probabilities"] == [0.25, 0.25, 0.25, 0.25] for row in second["feedback"]))

    def test_a3_feedback_uses_only_previous_12_unique_offspring(self):
        result = run_arm("A3", 711, SyntheticEvaluator(), episodes_per_genome=2)
        self.assertTrue(result["feedback"])
        if result["status"] == "VALID":
            self.assertEqual(len(result["feedback"]), 7)
        for round_index, feedback in enumerate(result["feedback"], start=1):
            self.assertEqual(feedback["round"], round_index)
            self.assertEqual(len(feedback["input_genomes"]), 12)
            self.assertEqual(feedback["combined"]["row_count"], 24)
            self.assertEqual(feedback["next_probabilities"], result["rounds"][round_index - 1]["next_probabilities"])

    def test_no_feasible_candidate_is_preserved(self):
        result = run_arm("A0", 711, SyntheticEvaluator(hard=1), episodes_per_genome=2)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(result["final_candidate"]["status"], "NO_FEASIBLE_CANDIDATE")
        self.assertEqual(result["budget"]["unique_evaluations"], 96)

    def test_repeated_run_is_reproducible(self):
        first = run_arm("A2", 711, SyntheticEvaluator(), episodes_per_genome=2)
        second = run_arm("A2", 711, SyntheticEvaluator(), episodes_per_genome=2)
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
    def test_a2_never_niches_infeasible_candidates_when_feasible_pool_is_sufficient(self):
        class MixedEvaluator(SyntheticEvaluator):
            def evaluate(self, genome, seed, unique_ordinal):
                view = super().evaluate(genome, seed, unique_ordinal)
                if genome.cycle_mode == "OFF":
                    view["hard_constraints"]["pending_count"] = 1
                    view["constraint_episode_count"] = 2
                    view["fitness"] = {"R3": 1.0, "R4": 1.0, "CondRec": 1.0, "Harm": 0.0, "RecoveryCost": 0.0}
                return view

        result = run_arm("A2", 711, MixedEvaluator(), episodes_per_genome=2)
        self.assertTrue(result["survivor_log"])
        infeasible = {row["genome_sha256"] for row in result["proposal_log"] if row["genome"]["cycle_mode"] == "OFF"}
        selected = {genome_hash for row in result["survivor_log"] for genome_hash in row["selected"]}
        self.assertFalse(infeasible.intersection(selected))

    def test_evaluator_episode_count_must_match_ledger(self):
        class WrongRowEvaluator(SyntheticEvaluator):
            def evaluate(self, genome, seed, unique_ordinal):
                view = super().evaluate(genome, seed, unique_ordinal)
                view["feedback_marginals"]["row_count"] = 1
                return view

        ledger = BudgetLedger(WrongRowEvaluator(), "A1", 711, episodes_per_genome=2)
        with self.assertRaises(BudgetError):
            ledger.offer(TypedGenome(), 0)
        self.assertEqual(ledger.invalid_reason, "EPISODE_COUNT_MISMATCH")

    def test_attempt_cap_invalid_run_preserves_partial_evidence(self):
        result = run_arm("A1", 711, SyntheticEvaluator(), episodes_per_genome=2)
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(result["invalid_reason"], "INVALID_ATTEMPT_CAP")
        self.assertEqual(result["budget"]["attempts"], 384)
        self.assertLess(result["budget"]["unique_evaluations"], 96)
        self.assertTrue(result["proposal_log"])
    def test_dual_evaluator_preserves_audit_without_exposing_it_to_optimizer(self):
        class DualEvaluator(SyntheticEvaluator):
            def evaluate(self, genome, seed, unique_ordinal):
                view = super().evaluate(genome, seed, unique_ordinal)
                return {
                    "optimizer_reward_view": view,
                    "audit_only_view": {
                        "evaluator_internal_rows": [{"scenario_id": "synthetic", "label": "R3", "unique_ordinal": unique_ordinal}],
                        "hash_to_record": {view["phenotype_hashes"]["joint"]: "synthetic-record"},
                    },
                }

        result = run_arm("A0", 711, DualEvaluator(), episodes_per_genome=2)
        self.assertEqual(result["status"], "VALID")
        self.assertEqual(len(result["audit_archive"]), 96)
        self.assertTrue(all("audit_only_view" not in row for row in result["proposal_log"]))
        self.assertTrue(all("audit_only_view" not in row for row in result["archive"]))
        self.assertTrue(all("audit_only_view" not in row["optimizer_reward_view"] for row in result["archive"]))


if __name__ == "__main__":
    unittest.main()
