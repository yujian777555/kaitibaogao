"""D-094 independent Train tasks, global budget and Phase 2 runner tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from d094_agent import RuleBasedAgent
from d094_evolution import Candidate
from d094_genome import AgentGenome
from d094_ledger import (
    LLMBudgetExceeded,
    LLMCostLimitExceeded,
    SharedBudget,
    SharedBudgetTransport,
)
from d094_llm_client import LLMClient, MockTransport, TransportResult
from d094_tasks import (
    TrainRecoveryEnvironment,
    rule_policy,
    train_manifest,
    train_tasks,
)
from run_d094_phase2 import Phase2Config, run_phase2


def mock_result(index: int) -> TransportResult:
    content = {
        "action": "finish",
        "tool_name": None,
        "tool_arguments": {},
        "rationale": "Mock terminal decision.",
        "verification_required": False,
    }
    return TransportResult(
        status=200,
        body={
            "id": f"mock-phase2-{index}",
            "model": "mock-phase2",
            "choices": [
                {"message": {"content": json.dumps(content)}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
        headers={},
    )


def mock_client_factory() -> LLMClient:
    transport = MockTransport(
        [mock_result(index) for index in range(32)], model="mock-phase2"
    )
    return LLMClient(
        transport,
        max_requests=32,
        max_cost_usd=1.0,
        input_price_per_1m=0.0,
        output_price_per_1m=0.0,
        max_retries=0,
    )


class TestD094Tasks(unittest.TestCase):
    def test_manifest_has_twelve_independent_train_tasks(self):
        manifest = train_manifest()
        self.assertEqual(manifest["scenario_count"], 12)
        self.assertEqual(manifest["split"], "train")
        self.assertFalse(manifest["validation_included"])
        self.assertFalse(manifest["test_included"])
        self.assertEqual(len({task["task_id"] for task in manifest["tasks"]}), 12)
        self.assertEqual(len(train_tasks()), 12)

    def test_rule_baseline_solves_all_paired_train_tasks_without_violations(self):
        for task in train_tasks():
            for seed in (101, 202, 303):
                with self.subTest(task=task.task_id, seed=seed):
                    environment = TrainRecoveryEnvironment(task, seed)
                    result = RuleBasedAgent(
                        rule_policy, AgentGenome().to_agent_config()
                    ).run(task.goal, environment)
                    self.assertEqual(result.status, "COMPLETED")
                    self.assertEqual(result.constraint_violations, 0)
                    self.assertTrue(environment.task_success())

    def test_seed_is_paired_and_reproducible(self):
        task = next(task for task in train_tasks() if task.seed_jitter)
        first = TrainRecoveryEnvironment(task, 101)
        second = TrainRecoveryEnvironment(task, 101)
        different = TrainRecoveryEnvironment(task, 202)
        self.assertEqual(
            first.retry_failures_remaining, second.retry_failures_remaining
        )
        self.assertNotEqual(
            first.retry_failures_remaining, different.retry_failures_remaining
        )

    def test_execution_error_is_not_a_feasible_candidate(self):
        candidate = Candidate(AgentGenome(), (1.0, 1.0), execution_errors=1)
        self.assertFalse(candidate.feasible)


class TestSharedBudget(unittest.TestCase):
    def test_request_and_cost_caps_include_transport_attempts(self):
        shared = SharedBudget(1, 1.0, 0.0, 0.0)
        transport = SharedBudgetTransport(
            MockTransport([mock_result(0), mock_result(1)]), shared
        )
        transport({}, 1.0)
        with self.assertRaises(LLMBudgetExceeded):
            transport({}, 1.0)
        self.assertEqual(shared.snapshot()["request_count"], 1)

        priced = SharedBudget(2, 0.0000001, 1.0, 1.0)
        transport = SharedBudgetTransport(
            MockTransport([mock_result(0), mock_result(1)]), priced
        )
        transport({}, 1.0)
        with self.assertRaises(LLMCostLimitExceeded):
            transport({}, 1.0)
        self.assertEqual(priced.snapshot()["request_count"], 1)


class TestPhase2Runner(unittest.TestCase):
    def test_mock_b0_b1_b2_runner_preserves_real_accounting_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Phase2Config(
                seeds=(101,),
                population_size=4,
                generations=1,
                max_concurrency=2,
                global_request_cap=1000,
                global_cost_cap=1.0,
            )
            result = run_phase2(
                Path(directory), config, client_factory=mock_client_factory
            )
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["arms"]["B0"]["metrics"]["input_tokens"], 0)
            self.assertEqual(result["arms"]["B0"]["metrics"]["task_success_rate"], 1.0)
            self.assertEqual(result["arms"]["B1"]["metrics"]["task_success_rate"], 0.0)
            self.assertIn("B2", result["arms"])
            self.assertGreater(result["search"]["unique_evaluated_genomes"], 1)
            self.assertTrue((Path(directory) / "episodes.jsonl").exists())
            self.assertTrue((Path(directory) / "train_manifest.json").exists())
            self.assertTrue((Path(directory) / "evolution_ledger.json").exists())
            lock = json.loads(
                (Path(directory) / "execution_lock.json").read_text(encoding="utf-8")
            )
            self.assertEqual(lock["model"], "mock-phase2")
            self.assertEqual(lock["planned_episode_count"], 132)
            self.assertEqual(result["model"], "mock-phase2")
            self.assertEqual(result["budget"]["backend"], "mock")
            self.assertNotIn("configured-secret", json.dumps(result))

    def test_recovered_transport_error_uses_cost_upper_bound(self):
        from d094_llm_client import TransportError

        def factory() -> LLMClient:
            transport = MockTransport(
                [
                    TransportError("network disconnected", retryable=True),
                    mock_result(0),
                ],
                model="mock-phase2",
            )
            return LLMClient(
                transport,
                max_requests=32,
                input_price_per_1m=0.0,
                output_price_per_1m=0.0,
                max_retries=1,
            )

        with tempfile.TemporaryDirectory() as directory:
            config = Phase2Config(
                seeds=(101,),
                population_size=2,
                generations=0,
                max_concurrency=2,
                global_request_cap=1000,
                global_cost_cap=1.0,
            )
            result = run_phase2(Path(directory), config, client_factory=factory)
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["arms"]["B1"]["execution_errors"], 0)
            self.assertIsNotNone(
                result["arms"]["B1"]["metrics"]["token_cost_upper_usd"]
            )


if __name__ == "__main__":
    unittest.main()
