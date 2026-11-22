"""R4 budget, statistical, preflight and full Mock protocol regression tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from d094_evolution import Candidate, feasible_pareto
from d094_r4_credit import select_final_candidate
from d094_r4_statistics import (
    exact_sign_flip_test,
    holm_adjust,
    paired_bootstrap_ci,
    preregistered_analysis,
)
from run_d094_r4 import R4Config, compute_budget_plan, run_r4
from run_d094_r4_synthetic import _mock_statistics, mock_factory


class TestR4BudgetAndStatistics(unittest.TestCase):
    def test_conservative_budget_and_protected_pools(self):
        plan = compute_budget_plan()
        self.assertTrue(plan["fits"])
        self.assertEqual(plan["planned_episode_count"], 64)
        self.assertEqual(plan["total_request_upper"], 320)
        self.assertAlmostEqual(plan["per_request_cost_upper_usd"], 0.0013824)
        self.assertAlmostEqual(plan["total_cost_upper_usd"], 0.442368)
        self.assertLessEqual(plan["total_cost_upper_usd"], R4Config.global_cost_cap)
        self.assertEqual(set(plan["protected_pools"]), {"B1", "final:B2", "final:B3", "final:B4"})
        for pool in plan["protected_pools"].values():
            self.assertEqual(pool["request_count"], 20)
            self.assertAlmostEqual(pool["cost_usd"], 0.027648)
        for arm in ("B2", "B3", "B4"):
            self.assertEqual(plan["arm_plans"][arm]["search_episodes"], 16)
            self.assertEqual(plan["arm_plans"][arm]["final_episodes"], 4)
            self.assertEqual(plan["arm_plans"][arm]["search_request_upper"], 80)
        self.assertIn("r4_empirical_estimate", plan)
        self.assertNotEqual(plan["r4_empirical_estimate"]["cost_usd"], plan["total_cost_upper_usd"])
        self.assertFalse(plan["independent_recalculation_requires_api"])

    def test_exact_sign_flip_and_frozen_bootstrap(self):
        result = exact_sign_flip_test([1.0, 1.0, 1.0, 1.0])
        self.assertEqual(result["null_count"], 16)
        self.assertEqual(result["p_value"], 0.125)
        interval = paired_bootstrap_ci([1.0, 1.0, 1.0, 1.0])
        self.assertEqual(interval["replicates"], 20000)
        self.assertEqual(interval["lower"], 1.0)
        self.assertEqual(interval["upper"], 1.0)
        self.assertEqual(interval, paired_bootstrap_ci([1.0, 1.0, 1.0, 1.0]))

    def test_holm_and_complete_preregistered_family(self):
        self.assertEqual(holm_adjust({"a": 0.01, "b": 0.04}), {"a": 0.02, "b": 0.04})
        differences = {
            "B3_minus_B2": [0.0, 1.0, 0.0, 0.0],
            "B4_minus_B2": [0.0, 0.0, 0.0, 0.0],
            "B3_minus_B4": [0.0, 1.0, 0.0, 0.0],
            "B2_minus_B1": [-1.0, -1.0, -1.0, -1.0],
        }
        result = preregistered_analysis(differences)
        self.assertEqual(result["primary_comparison"], "B3_minus_B2")
        self.assertEqual(result["comparisons"]["B3_minus_B2"]["sign_flip"]["observed_mean_difference"], 0.25)
        self.assertEqual(len(result["comparisons"]), 4)
        with self.assertRaises(ValueError):
            preregistered_analysis({"B3_minus_B2": [0.0] * 4})


class TestR4Protocol(unittest.TestCase):
    def test_preflight_does_not_construct_client_or_execute_episode(self):
        with tempfile.TemporaryDirectory() as directory:
            called = []
            result = run_r4(
                Path(directory) / "preflight",
                client_factory=lambda: called.append(True),
                preflight_only=True,
            )
            self.assertEqual(result["status"], "PREFLIGHT_PASS")
            self.assertEqual(called, [])
            self.assertEqual(result["actual_episode_count"], 0)
            self.assertFalse(result["api_used"])
            self.assertFalse((Path(directory) / "preflight" / "episodes.jsonl").exists())

    def test_non_mock_transport_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = SimpleNamespace(transport=SimpleNamespace(backend="openai-compatible"))
            with self.assertRaisesRegex(ValueError, "Mock transport only"):
                run_r4(Path(directory) / "blocked", client_factory=lambda: fake, preflight_only=False)
            self.assertFalse((Path(directory) / "blocked" / "episodes.jsonl").exists())

    def test_complete_mock_protocol_has_fair_budget_and_independent_finals(self):
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory) / "mock"
            summary = run_r4(outdir, client_factory=mock_factory, preflight_only=False)
            self.assertEqual(summary["status"], "MOCK_COMPLETED", summary)
            self.assertEqual(summary["actual_episode_count"], 64)
            self.assertFalse(summary["real_api_used"])
            self.assertTrue(summary["hash_chain_valid"])
            self.assertLessEqual(summary["budget"]["sent_request_count"], 320)
            self.assertLessEqual(summary["budget"]["cost_upper_usd"], 0.442368)
            self.assertFalse(summary["budget"]["over_budget"])
            pools = summary["budget"]["spent_requests_by_pool"]
            self.assertLessEqual(pools.get("B1", 0), 20)
            self.assertNotIn("search", pools)
            for arm in ("B2", "B3", "B4"):
                self.assertEqual(summary["arms"][arm]["search_episode_count"], 16)
                self.assertEqual(summary["arms"][arm]["final_episode_count"], 4)
                self.assertLessEqual(pools.get(f"search:{arm}", 0), 80)
                self.assertLessEqual(pools.get(f"final:{arm}", 0), 20)
                self.assertEqual(
                    summary["search_pool_ledgers"][f"search:{arm}"]["sent_request_count"],
                    pools.get(f"search:{arm}", 0),
                )
            self.assertGreater(summary["arms"]["B3"]["credit_update_count"], 0)
            self.assertEqual(summary["arms"]["B2"]["credit_update_count"], 0)
            self.assertEqual(summary["arms"]["B4"]["credit_update_count"], 0)
            episodes = [json.loads(line) for line in (outdir / "episodes.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len({row["episode_id"] for row in episodes}), 64)
            self.assertTrue(all(row["api_attempt_count"] <= 5 for row in episodes))
            self.assertTrue(all(not row["real_api_used"] for row in episodes))
            statistics = _mock_statistics(summary)
            self.assertEqual(statistics["primary_comparison"], "B3_minus_B2")

    def test_mock_final_uses_all_search_archive_not_only_survivors(self):
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory) / "mock"
            summary = run_r4(outdir, client_factory=mock_factory, preflight_only=False)
            self.assertEqual(summary["status"], "MOCK_COMPLETED", summary)
            for arm in ("B2", "B3", "B4"):
                archive = json.loads((outdir / f"archive_{arm}.json").read_text(encoding="utf-8"))
                self.assertEqual(len(archive), 4)
                candidates = [
                    Candidate(
                        genome=__import__("d094_genome").AgentGenome(**row["genome"]),
                        objectives=tuple(row["candidate"]["objectives"]),
                        constraint_violation=row["candidate"]["constraint_violation"],
                        phenotype_hash=row["candidate"]["phenotype_hash"],
                        execution_errors=row["candidate"]["execution_errors"],
                    )
                    for row in archive
                ]
                expected = select_final_candidate(candidates)
                self.assertIsNotNone(expected)
                self.assertEqual(summary["arms"][arm]["selected_genome_sha256"], expected.genome_id)
                self.assertEqual(summary["arms"][arm]["pareto_front"], [row.genome_id for row in feasible_pareto(candidates)])


if __name__ == "__main__":
    unittest.main()
