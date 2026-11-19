"""D-094 R3 task, budget-preflight and five-arm Mock integration tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from d094_agent import LLMAgent
from d094_behavior import behavior_representation
from d094_genome import AgentGenome
from d094_ledger import canonical_json_bytes
from d094_llm_client import LLMClient, TransportResult
from d094_tasks import TrainRecoveryEnvironment, rule_policy
from d094_r3_tasks import r3_manifest, r3_tasks
from run_d094_r3 import R3Config, compute_budget_plan, run_r3


class PolicyMockTransport:
    backend = "mock"
    model = "mock-r3"

    def __init__(self, policy=rule_policy, include_usage=True, rationale=None):
        self.calls = []
        self.policy = policy
        self.include_usage = include_usage
        self.rationale = rationale

    def __call__(self, payload, timeout):
        self.calls.append((payload, timeout))
        text = payload["messages"][1]["content"]
        observation = json.loads(text.split("INPUT_JSON:\n", 1)[1])["observation"]
        decision = self.policy(observation)
        if self.rationale is not None:
            decision["rationale"] = self.rationale
        usage = (
            {
                "prompt_tokens": 10,
                "completion_tokens": 4,
                "total_tokens": 14,
            }
            if self.include_usage
            else None
        )
        body = {
            "id": f"mock-r3-{len(self.calls)}",
            "model": self.model,
            "choices": [
                {
                    "message": {"content": json.dumps(decision)},
                    "finish_reason": "stop",
                }
            ],
        }
        if usage is not None:
            body["usage"] = usage
        return TransportResult(status=200, body=body, headers={})


def mock_factory(policy=rule_policy, include_usage=True, rationale=None) -> LLMClient:
    return LLMClient(
        PolicyMockTransport(policy, include_usage, rationale),
        max_requests=32,
        max_cost_usd=1.0,
        input_price_per_1m=0.0,
        output_price_per_1m=0.0,
        max_retries=0,
    )


def retry_after_verification(observation):
    if observation["public_state"]["state"]["verified"]:
        return {
            "action": "tool_call",
            "tool_name": "retry_primary",
            "tool_arguments": {},
            "rationale": "retry",
            "verification_required": False,
        }
    return rule_policy(observation)


def compensate_repeatedly(_observation):
    return {
        "action": "tool_call",
        "tool_name": "compensate_primary",
        "tool_arguments": {},
        "rationale": "compensate",
        "verification_required": False,
    }


class TestR3MemoryBounds(unittest.TestCase):
    def test_structured_failures_remain_bounded_across_eight_failures(self):
        transport = PolicyMockTransport(policy=retry_after_verification)
        client = LLMClient(
            transport,
            max_requests=32,
            max_cost_usd=1.0,
            input_price_per_1m=0.0,
            output_price_per_1m=0.0,
            max_retries=0,
            max_message_bytes=4096,
        )
        genome = AgentGenome(
            memory_mode="structured_failures",
            recovery_mode="retry_priority",
            tool_call_guard="strict_schema",
            max_plan_steps=8,
        )
        task = next(task for task in r3_tasks() if task.family == "compensation")
        result = LLMAgent(client, genome.to_agent_config()).run(
            task.goal, TrainRecoveryEnvironment(task, 201)
        )
        self.assertEqual(result.status, "MAX_STEPS")
        sizes = [
            len(canonical_json_bytes(call[0]["messages"])) for call in transport.calls
        ]
        self.assertEqual(len(sizes), 8)
        self.assertLessEqual(max(sizes), 4096)

    def test_recent_trajectory_with_long_rationale_remains_bounded(self):
        for rationale in ("x" * 240, "界" * 240):
            with self.subTest(rationale=rationale[:1]):
                transport = PolicyMockTransport(
                    policy=compensate_repeatedly, rationale=rationale
                )
                client = LLMClient(
                    transport,
                    max_requests=32,
                    max_cost_usd=1.0,
                    input_price_per_1m=0.0,
                    output_price_per_1m=0.0,
                    max_retries=0,
                    max_message_bytes=4096,
                )
                genome = AgentGenome(
                    memory_mode="recent_trajectory",
                    recovery_mode="compensation_priority",
                    tool_call_guard="strict_schema",
                    max_plan_steps=8,
                )
                task = next(
                    task for task in r3_tasks() if task.family == "compensation"
                )
                result = LLMAgent(client, genome.to_agent_config()).run(
                    task.goal, TrainRecoveryEnvironment(task, 201)
                )
                self.assertEqual(result.status, "MAX_STEPS")
                sizes = [
                    len(canonical_json_bytes(call[0]["messages"]))
                    for call in transport.calls
                ]
                self.assertEqual(len(sizes), 8)
                self.assertLessEqual(max(sizes), 4096)

    def test_recent_memory_bounds_joint_rationale_and_arguments(self):
        def compensate_with_long_arguments(observation):
            decision = compensate_repeatedly(observation)
            decision["tool_arguments"] = {"x": "a" * 240}
            return decision

        transport = PolicyMockTransport(
            policy=compensate_with_long_arguments, rationale="x" * 240
        )
        client = LLMClient(
            transport,
            max_requests=32,
            max_cost_usd=1.0,
            input_price_per_1m=0.0,
            output_price_per_1m=0.0,
            max_retries=0,
            max_message_bytes=4096,
        )
        genome = AgentGenome(
            memory_mode="recent_trajectory",
            recovery_mode="compensation_priority",
            tool_call_guard="strict_schema",
            max_plan_steps=8,
        )
        task = next(task for task in r3_tasks() if task.family == "compensation")
        result = LLMAgent(client, genome.to_agent_config()).run(
            task.goal, TrainRecoveryEnvironment(task, 201)
        )
        self.assertEqual(result.status, "MAX_STEPS")
        self.assertEqual(len(transport.calls), 8)
        observations = [
            json.loads(
                call[0]["messages"][1]["content"].split("INPUT_JSON:\n", 1)[1]
            )["observation"]
            for call in transport.calls
        ]
        message_sizes = [
            len(canonical_json_bytes(call[0]["messages"])) for call in transport.calls
        ]
        memory_sizes = [
            len(canonical_json_bytes(observation["memory"]))
            for observation in observations
        ]
        self.assertLessEqual(max(message_sizes), 4096)
        self.assertLessEqual(max(memory_sizes), 512)
        self.assertTrue(
            any(observation["memory"]["truncated"] for observation in observations)
        )
        decisions = [
            event["payload"]
            for event in result.events
            if event["event_type"] == "decision"
        ]
        self.assertTrue(all(len(event["rationale"]) == 240 for event in decisions))
        self.assertTrue(
            all(len(event["tool_arguments"]["x"]) == 240 for event in decisions)
        )

    def test_compressed_summary_bounds_unicode_tool_names(self):
        def unknown_tool_with_long_arguments(observation):
            decision = compensate_repeatedly(observation)
            decision["tool_name"] = "工" * 64
            decision["tool_arguments"] = {"x": "a" * 240}
            return decision

        transport = PolicyMockTransport(
            policy=unknown_tool_with_long_arguments, rationale="x" * 240
        )
        client = LLMClient(
            transport,
            max_requests=32,
            max_cost_usd=1.0,
            input_price_per_1m=0.0,
            output_price_per_1m=0.0,
            max_retries=0,
            max_message_bytes=4096,
        )
        genome = AgentGenome(
            memory_mode="compressed_summary",
            recovery_mode="retry_priority",
            tool_call_guard="strict_schema",
            max_plan_steps=8,
        )
        task = next(task for task in r3_tasks() if task.family == "compensation")
        result = LLMAgent(client, genome.to_agent_config()).run(
            task.goal, TrainRecoveryEnvironment(task, 201)
        )
        self.assertEqual(result.status, "MAX_STEPS")
        self.assertEqual(len(transport.calls), 8)
        observations = [
            json.loads(
                call[0]["messages"][1]["content"].split("INPUT_JSON:\n", 1)[1]
            )["observation"]
            for call in transport.calls
        ]
        self.assertTrue(
            all(
                len(canonical_json_bytes(call[0]["messages"])) <= 4096
                for call in transport.calls
            )
        )
        self.assertTrue(
            all(
                len(canonical_json_bytes(observation["memory"])) <= 512
                for observation in observations
            )
        )
        self.assertTrue(
            any(observation["memory"]["truncated"] for observation in observations)
        )
        decisions = [
            event["payload"]
            for event in result.events
            if event["event_type"] == "decision"
        ]
        self.assertTrue(all(len(event["tool_name"]) == 64 for event in decisions))
        self.assertTrue(
            all(len(event["tool_arguments"]["x"]) == 240 for event in decisions)
        )


class TestR3TasksAndBudget(unittest.TestCase):
    def test_six_new_independent_train_tasks(self):
        manifest = r3_manifest()
        self.assertEqual(manifest["scenario_count"], 6)
        self.assertTrue(
            all(
                task["task_id"].startswith("d094_r3_train_")
                for task in manifest["tasks"]
            )
        )
        self.assertFalse(manifest["validation_included"])
        self.assertFalse(manifest["test_included"])

    def test_original_scale_is_blocked_by_request_and_cost_preflight(self):
        plan = compute_budget_plan(
            R3Config(), input_price_per_1m=0.3, output_price_per_1m=1.2
        )
        self.assertFalse(plan["fits"])
        self.assertGreater(plan["total_request_upper"], 1500)
        self.assertGreater(plan["total_cost_upper_usd"], 0.5)

    def test_revised_scale_is_bounded_and_uses_no_retries(self):
        config = R3Config.revised()
        plan = compute_budget_plan(
            config, input_price_per_1m=0.3, output_price_per_1m=1.2
        )
        self.assertTrue(plan["fits"])
        self.assertEqual(plan["total_request_upper"], 330)
        self.assertAlmostEqual(plan["total_cost_upper_usd"], 0.456192)
        self.assertEqual(config.max_retries, 0)
        self.assertEqual(set(plan["arm_plans"]), {"B1", "B2", "B3", "B4", "B5"})
        for arm in ("B2", "B3", "B4", "B5"):
            arm_plan = plan["arm_plans"][arm]
            self.assertEqual(arm_plan["initial_episodes"], 4)
            self.assertEqual(arm_plan["offspring_episodes"], 4)
            self.assertEqual(arm_plan["final_episodes"], 2)
            self.assertEqual(arm_plan["duplicate_proposal_request_upper"], 0)
            self.assertEqual(arm_plan["retry_request_upper"], 0)
            self.assertTrue(arm_plan["final_protected"])

    def test_preflight_only_never_executes_episodes(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_r3(
                Path(directory),
                R3Config.revised(),
                client_factory=mock_factory,
                preflight_only=True,
            )
            self.assertEqual(result["status"], "PREFLIGHT_PASS")
            self.assertEqual(result["actual_episode_count"], 0)
            self.assertEqual(result["budget"]["sent_request_count"], 0)
            self.assertFalse((Path(directory) / "episodes.jsonl").exists())

    def test_unknown_usage_invalidates_cost_accounting(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_r3(
                Path(directory),
                R3Config.revised(),
                client_factory=lambda: mock_factory(include_usage=False),
            )
            self.assertEqual(result["status"], "INVALID_COST_ACCOUNTING")
            self.assertTrue(result["budget"]["cost_unknown"])
            self.assertFalse(result["budget"]["cost_complete"])


class TestR3MockIntegration(unittest.TestCase):
    def test_revised_mock_five_arms_complete_with_hash_chains_and_finals(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_r3(
                Path(directory), R3Config.revised(), client_factory=mock_factory
            )
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["actual_episode_count"], 42)
            self.assertEqual(set(result["arms"]), {"B1", "B2", "B3", "B4", "B5"})
            for arm in ("B2", "B3", "B4", "B5"):
                self.assertEqual(result["arms"][arm]["search_episode_count"], 8)
                self.assertEqual(result["arms"][arm]["final_episode_count"], 2)
                self.assertEqual(result["arms"][arm]["execution_errors"], 0)
                self.assertTrue(result["arms"][arm]["hash_chain_valid"])
            self.assertEqual(result["budget"]["backend"], "mock")
            self.assertTrue(result["hash_chain_valid"])
            self.assertTrue((Path(directory) / "episodes.jsonl").exists())
            lock_path = Path(directory) / "execution_lock.json"
            self.assertTrue(lock_path.exists())
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            self.assertTrue(
                {
                    "d094_agent.py",
                    "d094_evaluator.py",
                    "d094_genome.py",
                    "d094_ledger.py",
                    "d094_llm_client.py",
                    "d094_prompts.py",
                    "d094_tasks.py",
                }.issubset(lock["source_files"])
            )
            rows = [
                json.loads(line)
                for line in (Path(directory) / "episodes.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ]
            for row in rows:
                behavior = behavior_representation(
                    row["events"],
                    agent_status=row["agent_status"],
                    final_public_observation=row["final_public_observation"],
                )
                self.assertEqual(
                    row["metrics"]["phenotype_hash"], behavior["canonical_sha256"]
                )
            for arm in ("B2", "B3", "B4", "B5"):
                self.assertTrue((Path(directory) / f"evolution_{arm}.json").exists())
                archive = json.loads(
                    (Path(directory) / f"archive_{arm}.json").read_text(
                        encoding="utf-8"
                    )
                )
                for entry in archive:
                    terminal_count = sum(
                        item.startswith("T|")
                        for item in entry["candidate"]["behavior"]["sequence"]
                    )
                    self.assertEqual(terminal_count, entry["episode_count"])


if __name__ == "__main__":
    unittest.main()
