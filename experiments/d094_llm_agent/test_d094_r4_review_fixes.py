"""Adversarial regressions for the three independent R4 review blockers."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from d094_budget import ReservedBudget, ReservedBudgetTransport
from d094_genome import AgentGenome
from d094_ledger import LLMCostLimitExceeded
from d094_llm_client import LLMClient, MockTransport, TransportError, TransportResult
from d094_r4_tasks import r4_manifest, r4_tasks as production_r4_tasks
import run_d094_r4 as r4
from run_d094_r4 import R4Config, run_r4, verify_execution_lock


class CountingTransport:
    backend = "mock"
    model = "mock-r4-budget"

    def __init__(self, *, unknown_usage: bool = False) -> None:
        self.calls = []
        self.unknown_usage = unknown_usage

    def __call__(self, payload, timeout):
        self.calls.append((payload, timeout))
        usage = (
            {}
            if self.unknown_usage
            else {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        )
        return TransportResult(
            status=200,
            body={"id": f"mock-{len(self.calls)}", "model": self.model, "usage": usage},
            headers={},
        )


def payload():
    return {"messages": [], "max_tokens": 128}


def reserve_three_search_pools(budget):
    for arm in ("B2", "B3", "B4"):
        budget.reserve(f"search:{arm}", 0.110592, request_count=80)


class TestR4001FrozenConfig(unittest.TestCase):
    def test_legal_frozen_config_passes_without_client_and_verifies_v2_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory) / "preflight"
            clients = []
            summary = run_r4(
                outdir,
                client_factory=lambda: clients.append("constructed"),
                preflight_only=True,
            )
            self.assertEqual(summary["status"], "PREFLIGHT_PASS")
            self.assertEqual(summary["planned_episode_count"], 64)
            self.assertEqual(clients, [])
            self.assertFalse(summary["api_used"])
            verification = verify_execution_lock(outdir / "execution_lock.json")
            self.assertEqual(verification["status"], "PASS")
            self.assertEqual(verification["source_file_count"], 17)
            self.assertEqual(
                verification["execution_lock_sha256"], summary["execution_lock_sha256"]
            )

    def test_every_config_override_fails_before_output_client_episode_or_api(self):
        cases = (
            ("seeds", {"seeds": (401, 402)}, "seeds"),
            ("search_seed", {"search_seed": 999}, "search_seed"),
            ("88_episodes", {"generations": 2}, "generations"),
            ("440_requests", {"global_request_cap": 440}, "global_request_cap"),
            ("raised_cost", {"global_cost_cap": 0.608256}, "global_cost_cap"),
            ("model", {"model": "other-model"}, "model"),
            ("five_steps", {"requests_per_episode_upper": 6}, "requests_per_episode_upper"),
            ("boolean_type_bypass", {"global_request_cap": True}, "global_request_cap"),
        )
        for label, changes, reason in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as directory:
                outdir = Path(directory) / "forbidden"
                clients = []
                config = dataclasses.replace(R4Config(), **changes)
                with self.assertRaisesRegex(ValueError, reason):
                    run_r4(
                        outdir,
                        config=config,
                        client_factory=lambda: clients.append("constructed"),
                    )
                self.assertFalse(outdir.exists())
                self.assertEqual(clients, [])
                self.assertFalse((outdir / "episodes.jsonl").exists())

    def test_train_task_id_tampering_fails_before_output_or_client(self):
        original = production_r4_tasks()

        def changed_tasks():
            return (
                dataclasses.replace(original[0], task_id="changed-task"),
                original[1],
            )

        with tempfile.TemporaryDirectory() as directory:
            outdir = Path(directory) / "forbidden"
            clients = []
            with patch.object(r4, "r4_tasks", changed_tasks):
                with self.assertRaisesRegex(ValueError, "task IDs"):
                    run_r4(outdir, client_factory=lambda: clients.append("constructed"))
            self.assertFalse(outdir.exists())
            self.assertEqual(clients, [])

    def test_arm_and_fixed_genome_tampering_fail_before_output_or_client(self):
        for label, patcher in (
            ("arm", patch.dict(r4.EVOLUTION_ARMS, {"B2": "failure_feedback"})),
            (
                "fixed_genome",
                patch.object(
                    r4,
                    "FIXED_GENOME",
                    dataclasses.replace(r4.FIXED_GENOME, max_plan_steps=3),
                ),
            ),
        ):
            with self.subTest(label=label), patcher, tempfile.TemporaryDirectory() as directory:
                outdir = Path(directory) / "forbidden"
                clients = []
                with self.assertRaisesRegex(ValueError, "R4"):
                    run_r4(outdir, client_factory=lambda: clients.append("constructed"))
                self.assertFalse(outdir.exists())
                self.assertEqual(clients, [])

    def test_budget_plan_entry_is_also_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "global_request_cap"):
            r4.compute_budget_plan(dataclasses.replace(R4Config(), global_request_cap=440))


class TestR4002StatisticalLock(unittest.TestCase):
    def assert_source_tamper_fails(self, filename, marker):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_dir = root / "experiments" / "d094_llm_agent"
            source_dir.mkdir(parents=True)
            production_hashes = {
                name: hashlib.sha256((r4.HERE / name).read_bytes()).hexdigest()
                for name in r4.SOURCE_NAMES
            }
            for name in r4.SOURCE_NAMES:
                shutil.copy2(r4.HERE / name, source_dir / name)
            for name in (
                "D094_R3_1_DEEP_ANALYSIS.md",
                "D094_R4_ALGORITHM_DESIGN.md",
                "D094_R4_PREREGISTRATION.md",
                "D094_R4_BUDGET_ANALYSIS.md",
            ):
                shutil.copy2(r4.HERE.parents[1] / name, root / name)
            plan_path = root / "budget_plan.json"
            r4._write_json(plan_path, r4.compute_budget_plan())
            lock_path = root / "execution_lock.json"
            with patch.object(r4, "HERE", source_dir):
                lock = r4._execution_lock(
                    r4_manifest(),
                    plan_path,
                    R4Config(),
                    "none",
                    created_utc="2026-11-23T00:00:00+00:00",
                )
                r4._write_json(lock_path, lock)
                self.assertEqual(verify_execution_lock(lock_path)["status"], "PASS")
                with (source_dir / filename).open("a", encoding="utf-8", newline="\n") as source:
                    source.write(f"\n# adversarial test: {marker}\n")
                with self.assertRaisesRegex(ValueError, filename.replace(".", r"\.")):
                    verify_execution_lock(lock_path)
            self.assertEqual(
                production_hashes,
                {
                    name: hashlib.sha256((r4.HERE / name).read_bytes()).hexdigest()
                    for name in r4.SOURCE_NAMES
                },
            )

    def test_sign_flip_source_tamper_invalidates_lock(self):
        self.assert_source_tamper_fails("d094_r4_statistics.py", "sign flip")

    def test_bootstrap_source_tamper_invalidates_lock(self):
        self.assert_source_tamper_fails("d094_r4_statistics.py", "bootstrap")

    def test_holm_source_tamper_invalidates_lock(self):
        self.assert_source_tamper_fails("d094_r4_statistics.py", "Holm")

    def test_final_analysis_entry_tamper_invalidates_lock(self):
        self.assert_source_tamper_fails("d094_r4_analysis.py", "analysis entry")


class TestR4003IndependentSearchPools(unittest.TestCase):
    def test_each_arm_request_81_is_denied_before_transport(self):
        for arm in ("B2", "B3", "B4"):
            with self.subTest(arm=arm):
                budget = ReservedBudget(0.442368, 0.3, 1.2, max_requests=320)
                reserve_three_search_pools(budget)
                transport = CountingTransport()
                wrapped = ReservedBudgetTransport(transport, budget, f"search:{arm}")
                for _ in range(80):
                    wrapped(payload(), 1.0)
                with self.assertRaises(LLMCostLimitExceeded):
                    wrapped(payload(), 1.0)
                self.assertEqual(len(transport.calls), 80)
                self.assertEqual(budget.pool_snapshot(f"search:{arm}")["sent_request_count"], 80)
                self.assertEqual(budget.snapshot()["sent_request_count"], 80)
                for other in ("B2", "B3", "B4"):
                    if other != arm:
                        self.assertEqual(
                            budget.pool_snapshot(f"search:{other}")["sent_request_count"], 0
                        )
                        self.assertEqual(
                            budget.pool_snapshot(f"search:{other}")["remaining_request_count"],
                            80,
                        )

    def assert_cannot_borrow(self, source_arm, target_arm):
        budget = ReservedBudget(0.442368, 0.3, 1.2, max_requests=320)
        reserve_three_search_pools(budget)
        source_transport = CountingTransport()
        target_transport = CountingTransport()
        source = ReservedBudgetTransport(source_transport, budget, f"search:{source_arm}")
        target = ReservedBudgetTransport(target_transport, budget, f"search:{target_arm}")
        source(payload(), 1.0)
        for _ in range(80):
            target(payload(), 1.0)
        with self.assertRaises(LLMCostLimitExceeded):
            target(payload(), 1.0)
        self.assertEqual(len(target_transport.calls), 80)
        self.assertEqual(budget.pool_snapshot(f"search:{source_arm}")["remaining_request_count"], 79)
        self.assertEqual(budget.pool_snapshot(f"search:{target_arm}")["remaining_request_count"], 0)
        self.assertEqual(budget.snapshot()["sent_request_count"], 81)

    def test_b2_remaining_budget_cannot_transfer_to_b3(self):
        self.assert_cannot_borrow("B2", "B3")

    def test_b3_remaining_budget_cannot_transfer_to_b4(self):
        self.assert_cannot_borrow("B3", "B4")

    def test_global_request_cap_still_blocks_before_transport(self):
        budget = ReservedBudget(1.0, 0.3, 1.2, max_requests=2)
        budget.reserve("search:B2", 0.110592, request_count=2)
        transport = CountingTransport()
        wrapped = ReservedBudgetTransport(transport, budget, "search:B2")
        wrapped(payload(), 1.0)
        wrapped(payload(), 1.0)
        with self.assertRaises(LLMCostLimitExceeded):
            wrapped(payload(), 1.0)
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(budget.snapshot()["sent_request_count"], 2)
        self.assertFalse(budget.snapshot()["over_budget"])

    def test_retries_and_exception_each_consume_the_same_arm_pool(self):
        decision = {
            "action": "finish",
            "tool_name": None,
            "tool_arguments": {},
            "rationale": "done",
            "verification_required": False,
        }
        success = TransportResult(
            status=200,
            body={
                "id": "retry-success",
                "model": "mock-model",
                "choices": [{"message": {"content": json.dumps(decision)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
            },
            headers={},
        )
        transport = MockTransport([TransportError("network", retryable=True), success])
        budget = ReservedBudget(1.0, 0.3, 1.2, max_requests=10)
        budget.reserve("search:B3", 0.01, request_count=3)
        client = LLMClient(
            ReservedBudgetTransport(transport, budget, "search:B3"),
            input_price_per_1m=0.3,
            output_price_per_1m=1.2,
            max_retries=1,
            max_requests=3,
            sleep_fn=lambda _seconds: None,
        )
        client.generate_action(
            {"task": "public", "public_state": {}, "memory": []},
            [],
            AgentGenome().to_agent_config(),
        )
        ledger = budget.pool_snapshot("search:B3")
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(ledger["sent_request_count"], 2)
        self.assertEqual(ledger["remaining_request_count"], 1)
        self.assertTrue(budget.snapshot()["cost_unknown"])
        self.assertEqual(len(client.ledger.records), 2)

    def test_unknown_usage_retains_worst_case_cost_in_its_own_pool(self):
        budget = ReservedBudget(0.442368, 0.3, 1.2, max_requests=320)
        reserve_three_search_pools(budget)
        transport = CountingTransport(unknown_usage=True)
        wrapped = ReservedBudgetTransport(transport, budget, "search:B4")
        wrapped(payload(), 1.0)
        upper = budget.request_cost_upper(payload())
        ledger = budget.pool_snapshot("search:B4")
        self.assertEqual(ledger["sent_request_count"], 1)
        self.assertEqual(ledger["pending_request_count"], 0)
        self.assertAlmostEqual(ledger["cost_upper_usd"], upper)
        self.assertTrue(budget.snapshot()["cost_unknown"])
        self.assertEqual(budget.pool_snapshot("search:B2")["cost_upper_usd"], 0.0)
        self.assertEqual(budget.pool_snapshot("search:B3")["cost_upper_usd"], 0.0)


if __name__ == "__main__":
    unittest.main()
