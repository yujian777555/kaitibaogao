"""D-094 multi-turn Agent, tool gateway, genome and execution-ledger tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from d094_agent import LLMAgent, RuleBasedAgent, ToolResult, ToolSpec
from d094_genome import (
    AgentGenome,
    crossover_genomes,
    enumerate_genomes,
    genome_sha256,
    mutate_genome,
)
from d094_ledger import ExecutionLedger, verify_execution_ledger
from d094_llm_client import LLMClient, MockTransport, TransportResult


def action(tool: str, arguments: dict | None = None) -> dict:
    return {
        "action": "tool_call",
        "tool_name": tool,
        "tool_arguments": {} if arguments is None else arguments,
        "rationale": "Use the selected public tool.",
        "verification_required": False,
    }


def finish() -> dict:
    return {
        "action": "finish",
        "tool_name": None,
        "tool_arguments": {},
        "rationale": "Finish this run.",
        "verification_required": False,
    }


def response(value: dict, index: int) -> TransportResult:
    return TransportResult(
        status=200,
        body={
            "id": f"mock-{index}",
            "model": "mock-model",
            "choices": [
                {"message": {"content": json.dumps(value)}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
        headers={},
    )


def client_for(decisions: list[dict]) -> LLMClient:
    return LLMClient(
        MockTransport(
            [response(value, index) for index, value in enumerate(decisions)]
        ),
        max_requests=max(1, len(decisions)),
        max_retries=0,
        sleep_fn=lambda _seconds: None,
    )


def schema(extra: bool = False) -> dict:
    properties = {"value": {"type": "integer", "minimum": 0}} if extra else {}
    return {
        "type": "object",
        "properties": properties,
        "required": ["value"] if extra else [],
        "additionalProperties": False,
    }


class FakeEnvironment:
    def __init__(self, tools: list[ToolSpec], terminal_tools: set[str] | None = None):
        self.tools = tools
        self.terminal_tools = terminal_tools or set()
        self.executed = []
        self.reviewed = []
        self.authorized = []
        self.last_observation = {"status": "initial"}
        self.last_failure = False
        self.done = False
        self.completed_tools = set()
        self.deny_tools = set()
        self.review_denials = set()

    def public_observation(self) -> dict:
        return {
            "state": {"done": self.done},
            "last_observation": self.last_observation,
            "last_failure": self.last_failure,
            "completed_tools": sorted(self.completed_tools),
        }

    def available_tools(self) -> list[ToolSpec]:
        return self.tools

    def review_call(self, tool: ToolSpec, _arguments: dict) -> tuple[bool, str]:
        self.reviewed.append(tool.name)
        return tool.name not in self.review_denials, "SEMANTIC_REVIEW_DENIED"

    def authorize(self, tool: ToolSpec, _arguments: dict) -> tuple[bool, str]:
        self.authorized.append(tool.name)
        return tool.name not in self.deny_tools, "ENVIRONMENT_PERMISSION_DENIED"

    def execute(self, tool: ToolSpec, arguments: dict) -> ToolResult:
        self.executed.append((tool.name, arguments))
        self.last_observation = {"tool": tool.name, "ok": True}
        self.last_failure = False
        self.completed_tools.add(tool.name)
        if tool.name in self.terminal_tools:
            self.done = True
        return ToolResult(
            success=True,
            observation=self.last_observation,
            done=self.done,
            constraint_violation=0,
            harm=0.0,
            cost=1.0,
        )

    def task_success(self) -> bool:
        return self.done


def tool(
    name: str,
    *,
    kind: str = "normal",
    dependencies: tuple[str, ...] = (),
    extra: bool = False,
) -> ToolSpec:
    return ToolSpec(
        name=name,
        description=f"Public {name} tool",
        parameters_schema=schema(extra),
        kind=kind,
        dependencies=dependencies,
    )


class TestAgentLoop(unittest.TestCase):
    def test_llm_participates_in_every_tool_decision(self):
        environment = FakeEnvironment([tool("inspect"), tool("complete")], {"complete"})
        client = client_for([action("inspect"), action("complete")])
        result = LLMAgent(client, AgentGenome().to_agent_config()).run(
            "Recover", environment
        )
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(len(client.transport.calls), 2)
        self.assertEqual(result.llm_decision_count, 2)
        self.assertEqual(result.api_attempt_count, 2)
        self.assertEqual(
            [name for name, _ in environment.executed], ["inspect", "complete"]
        )
        self.assertEqual(result.tool_cost, 2.0)

    def test_schema_rejection_skips_execution_and_reaches_next_llm(self):
        environment = FakeEnvironment([tool("inspect"), tool("complete")], {"complete"})
        client = client_for([action("inspect", {"unexpected": 1}), action("complete")])
        result = LLMAgent(client, AgentGenome().to_agent_config()).run(
            "Recover", environment
        )
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.constraint_violations, 1)
        self.assertEqual([name for name, _ in environment.executed], ["complete"])
        second_prompt = client.transport.calls[1][0]["messages"][1]["content"]
        self.assertIn("TOOL_SCHEMA_REJECTED", second_prompt)

    def test_environment_permission_denial_is_not_an_execution(self):
        environment = FakeEnvironment([tool("blocked")])
        environment.deny_tools.add("blocked")
        client = client_for([action("blocked"), finish()])
        result = LLMAgent(client, AgentGenome().to_agent_config()).run(
            "Recover", environment
        )
        self.assertEqual(result.status, "PREMATURE_FINISH")
        self.assertEqual(result.constraint_violations, 1)
        self.assertEqual(environment.executed, [])
        self.assertEqual(environment.authorized, ["blocked"])

    def test_post_plan_guard_invokes_semantic_review(self):
        environment = FakeEnvironment([tool("inspect")])
        environment.review_denials.add("inspect")
        genome = AgentGenome(tool_call_guard="post_plan_verify")
        client = client_for([action("inspect"), finish()])
        result = LLMAgent(client, genome.to_agent_config()).run("Recover", environment)
        self.assertEqual(result.constraint_violations, 1)
        self.assertEqual(environment.reviewed, ["inspect"])
        self.assertEqual(environment.authorized, [])
        self.assertEqual(environment.executed, [])

    def test_recovery_modes_gate_actual_tool_kinds(self):
        for mode, allowed_kind in (
            ("verify_priority", "verify"),
            ("compensation_priority", "compensate"),
        ):
            with self.subTest(mode=mode):
                environment = FakeEnvironment(
                    [tool("normal"), tool("recovery", kind=allowed_kind)], {"recovery"}
                )
                environment.last_failure = True
                genome = AgentGenome(recovery_mode=mode)
                client = client_for([action("normal"), action("recovery")])
                result = LLMAgent(client, genome.to_agent_config()).run(
                    "Recover", environment
                )
                self.assertEqual(result.status, "COMPLETED")
                self.assertEqual(result.constraint_violations, 1)
                self.assertEqual(
                    [name for name, _ in environment.executed], ["recovery"]
                )

    def test_dependency_aware_mode_filters_public_tool_catalog(self):
        environment = FakeEnvironment(
            [tool("dependent", dependencies=("prepare",)), tool("prepare")],
            {"prepare"},
        )
        client = client_for([action("prepare")])
        genome = AgentGenome(recovery_mode="dependency_aware")
        result = LLMAgent(client, genome.to_agent_config()).run("Recover", environment)
        self.assertEqual(result.status, "COMPLETED")
        prompt = client.transport.calls[0][0]["messages"][1]["content"]
        self.assertNotIn('"name":"dependent"', prompt)
        self.assertIn('"name":"prepare"', prompt)

    def test_memory_modes_change_public_memory_projection(self):
        for mode, marker in (
            ("recent_trajectory", "recent_trajectory"),
            ("structured_failures", "structured_failures"),
            ("compressed_summary", "compressed_summary"),
        ):
            with self.subTest(mode=mode):
                environment = FakeEnvironment(
                    [tool("inspect"), tool("complete")], {"complete"}
                )
                client = client_for([action("inspect", {"bad": 1}), action("complete")])
                genome = AgentGenome(
                    memory_mode=mode, reflection_trigger="after_failure"
                )
                LLMAgent(client, genome.to_agent_config()).run("Recover", environment)
                prompt = client.transport.calls[1][0]["messages"][1]["content"]
                self.assertIn(marker, prompt)
                self.assertIn("reflection_request", prompt)

    def test_max_plan_steps_counts_llm_decisions(self):
        environment = FakeEnvironment([tool("inspect")])
        client = client_for([action("inspect")] * 3)
        genome = AgentGenome(max_plan_steps=3)
        result = LLMAgent(client, genome.to_agent_config()).run("Recover", environment)
        self.assertEqual(result.status, "MAX_STEPS")
        self.assertEqual(result.llm_decision_count, 3)
        self.assertEqual(len(client.transport.calls), 3)

    def test_hidden_observation_never_reaches_transport(self):
        environment = FakeEnvironment([tool("inspect")])
        environment.last_observation = {"hidden_outcome": "future"}
        client = client_for([action("inspect")])
        result = LLMAgent(client, AgentGenome().to_agent_config()).run(
            "Recover", environment
        )
        self.assertEqual(result.status, "LLM_ERROR")
        self.assertEqual(len(client.transport.calls), 0)
        self.assertEqual(environment.executed, [])

    def test_rule_based_arm_has_no_llm_calls(self):
        environment = FakeEnvironment([tool("complete")], {"complete"})
        result = RuleBasedAgent(
            lambda _observation: action("complete"), AgentGenome().to_agent_config()
        ).run("Recover", environment)
        self.assertEqual(result.status, "COMPLETED")
        self.assertEqual(result.api_attempt_count, 0)
        self.assertEqual(result.decision_source, "rule")
        self.assertEqual(result.llm_decision_count, 0)

    def test_execution_hash_chain_and_secret_redaction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            ledger = ExecutionLedger(path)
            ledger.append(
                "redaction_test",
                {"api_key": "secret", "nested": {"authorization": "Bearer abc"}},
            )
            events = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertTrue(verify_execution_ledger(events))
            with self.assertRaises(ValueError):
                ExecutionLedger(path)
            serialized = json.dumps(events)
            self.assertNotIn("secret", serialized)
            self.assertNotIn("Bearer abc", serialized)
            events[0]["payload"]["nested"]["authorization"] = "tampered"
            self.assertFalse(verify_execution_ledger(events))


class TestAgentGenome(unittest.TestCase):
    def test_all_648_genomes_are_legal_and_unique(self):
        genomes = enumerate_genomes()
        self.assertEqual(len(genomes), 648)
        hashes = {genome_sha256(genome) for genome in genomes}
        self.assertEqual(len(hashes), 648)
        for genome in genomes:
            config = genome.to_agent_config()
            self.assertEqual(config["max_plan_steps"], genome.max_plan_steps)
            self.assertEqual(config["prompt_version"], "d094-react-json-v1")
            self.assertEqual(len(config["prompt_template_sha256"]), 64)

    def test_mutation_changes_exactly_one_gene(self):
        import random

        original = AgentGenome()
        mutated = mutate_genome(original, random.Random(7))
        differences = [
            field
            for field in original.to_dict()
            if original.to_dict()[field] != mutated.to_dict()[field]
        ]
        self.assertEqual(len(differences), 1)

    def test_crossover_inherits_each_gene_from_a_parent(self):
        import random

        first = AgentGenome()
        second = AgentGenome(
            planning_mode="direct",
            recovery_mode="retry_priority",
            reflection_trigger="none",
            memory_mode="recent_trajectory",
            tool_call_guard="strict_schema",
            max_plan_steps=3,
        )
        child = crossover_genomes(first, second, random.Random(11))
        for field, value in child.to_dict().items():
            self.assertIn(value, (first.to_dict()[field], second.to_dict()[field]))


if __name__ == "__main__":
    unittest.main()
