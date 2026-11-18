"""Run D-094 Mock integration or a strictly bounded real API Canary."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from d094_agent import LLMAgent, ToolResult, ToolSpec
from d094_genome import AgentGenome
from d094_ledger import verify_execution_ledger
from d094_llm_client import (
    LLMClient,
    MockTransport,
    TransportResult,
    real_configuration_missing,
)


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class CanaryEnvironment:
    """Independent D-094 task with public dependencies and deterministic permissions."""

    def __init__(self) -> None:
        self.completed: set[str] = set()
        self.done = False
        self.last_observation: dict[str, Any] = {
            "primary_route": "FAILED",
            "dependency": "C",
        }
        self.executed_tools: list[str] = []

    def public_observation(self) -> dict[str, Any]:
        return {
            "task_family": "d094_canary_recovery",
            "last_observation": self.last_observation,
            "last_failure": not self.done,
            "completed_tools": sorted(self.completed),
        }

    def available_tools(self) -> list[ToolSpec]:
        empty = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }
        return [
            ToolSpec(
                "inspect_dependencies", "Inspect the public failed dependency", empty
            ),
            ToolSpec(
                "verify_dependency",
                "Verify the failed dependency before recovery",
                empty,
                kind="verify",
            ),
            ToolSpec(
                "complete_recovery",
                "Complete recovery after dependency verification",
                empty,
                dependencies=("verify_dependency",),
            ),
        ]

    def review_call(
        self, tool: ToolSpec, _arguments: dict[str, Any]
    ) -> tuple[bool, str]:
        if (
            tool.name == "complete_recovery"
            and "verify_dependency" not in self.completed
        ):
            return False, "DEPENDENCY_VERIFICATION_REQUIRED"
        return True, "ALLOWED"

    def authorize(self, tool: ToolSpec, arguments: dict[str, Any]) -> tuple[bool, str]:
        return self.review_call(tool, arguments)

    def execute(self, tool: ToolSpec, _arguments: dict[str, Any]) -> ToolResult:
        allowed, _ = self.review_call(tool, _arguments)
        if not allowed:
            return ToolResult(
                False, {"error": "DEPENDENCY_VERIFICATION_REQUIRED"}, False, 1, 1.0, 0.0
            )
        self.executed_tools.append(tool.name)
        self.completed.add(tool.name)
        if tool.name == "complete_recovery":
            self.done = True
        self.last_observation = {
            "tool": tool.name,
            "status": "COMPLETED" if self.done else "VERIFIED",
        }
        return ToolResult(True, self.last_observation, self.done, 0, 0.0, 1.0)

    def task_success(self) -> bool:
        return self.done


def _decision(tool_name: str) -> dict[str, Any]:
    return {
        "action": "tool_call",
        "tool_name": tool_name,
        "tool_arguments": {},
        "rationale": "Follow the public dependency state.",
        "verification_required": tool_name == "verify_dependency",
    }


def _mock_client() -> LLMClient:
    responses = []
    for index, tool_name in enumerate(("verify_dependency", "complete_recovery")):
        responses.append(
            TransportResult(
                status=200,
                body={
                    "id": f"mock-canary-{index}",
                    "model": "mock-canary-model",
                    "choices": [
                        {
                            "message": {"content": json.dumps(_decision(tool_name))},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 4,
                        "total_tokens": 14,
                    },
                },
                headers={},
            )
        )
    return LLMClient(
        MockTransport(responses, model="mock-canary-model"),
        max_requests=4,
        max_retries=0,
    )


def _run_with_client(client: LLMClient, outdir: Path) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    trace_path = outdir / "trace.jsonl"
    if trace_path.exists():
        raise ValueError("Canary trace already exists; refusing to overwrite evidence")
    environment = CanaryEnvironment()
    genome = AgentGenome(max_plan_steps=3, planning_mode="verification_first")
    result = LLMAgent(client, genome.to_agent_config(), ledger_path=trace_path).run(
        "Verify the failed dependency and complete recovery safely",
        environment,
    )
    records = client.ledger.records
    events = [
        json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
    ]
    real = client.transport.backend == "openai-compatible"
    connected = real and any(record["response_model"] is not None for record in records)
    chain_valid = verify_execution_ledger(events)
    passed = (
        result.status == "COMPLETED" and result.llm_decision_count >= 2 and chain_valid
    )
    status = (
        (
            "PASS"
            if connected and passed and result.constraint_violations == 0
            else "FAIL_CANARY"
        )
        if real
        else ("MOCK_PASS" if passed else "MOCK_FAIL")
    )
    return {
        "status": status,
        "backend": client.transport.backend,
        "api_connected": connected,
        "agent_status": result.status,
        "llm_decision_count": result.llm_decision_count,
        "api_attempt_count": len(records),
        "input_tokens": client.ledger.total_input_tokens,
        "output_tokens": client.ledger.total_output_tokens,
        "cost_usd": client.ledger.total_cost_usd,
        "cost_status": "UNKNOWN" if client.ledger.cost_unknown else "PRICED",
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in records),
        "models": sorted(
            {record["response_model"] for record in records if record["response_model"]}
        ),
        "request_ids": [
            record["request_id"] for record in records if record["request_id"]
        ],
        "prompt_hashes": [record["prompt_sha256"] for record in records],
        "errors": [
            {"error_type": record["error_type"], "error": record["error"]}
            for record in records
            if record["error_type"]
        ],
        "constraint_violations": result.constraint_violations,
        "tool_cost": result.tool_cost,
        "executed_tools": environment.executed_tools,
        "hash_chain_valid": chain_valid,
        "request_ledger": records,
        "events": events,
    }


def run_mock_canary(outdir: Path) -> dict[str, Any]:
    """Run the complete multi-turn loop with an explicitly labeled Mock backend."""
    summary = _run_with_client(_mock_client(), Path(outdir))
    (Path(outdir) / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def execute_real_canary(outdir: Path) -> dict[str, Any]:
    """Run at most three decisions/four HTTP attempts, or fail closed before network."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    missing = real_configuration_missing(require_pricing=True)
    if missing:
        summary = {
            "status": "BLOCKED_CONFIGURATION",
            "backend": "openai-compatible",
            "api_connected": False,
            "credential_status": "PRESENT"
            if os.environ.get("D094_LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
            else "MISSING",
            "missing_configuration": missing,
            "api_attempt_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "latency_seconds": 0.0,
            "llm_decision_count": 0,
            "agent_status": "NOT_RUN",
        }
    else:
        client = LLMClient.from_env()
        client.ledger.max_requests = min(client.ledger.max_requests, 4)
        client.ledger.max_cost_usd = min(client.ledger.max_cost_usd, 0.10)
        client.max_retries = min(client.max_retries, 1)
        client.timeout = min(client.timeout, 20.0)
        client.max_output_tokens = min(client.max_output_tokens, 128)
        try:
            summary = _run_with_client(client, outdir)
        except Exception as error:
            summary = {
                "status": "FAIL_CANARY",
                "backend": "openai-compatible",
                "api_connected": any(
                    record["response_model"] is not None
                    for record in client.ledger.records
                ),
                "error_type": type(error).__name__,
                "api_attempt_count": len(client.ledger.records),
                "input_tokens": client.ledger.total_input_tokens,
                "output_tokens": client.ledger.total_output_tokens,
                "cost_usd": client.ledger.total_cost_usd,
                "latency_seconds": sum(
                    record["latency_seconds"] or 0.0 for record in client.ledger.records
                ),
                "request_ledger": client.ledger.records,
            }
    (outdir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def render_markdown(mock: dict[str, Any] | None, real: dict[str, Any] | None) -> str:
    """Render only measured Mock and real Canary outcomes."""
    lines = [
        "# D-094 API Canary Report",
        "",
        "本报告区分 Mock 与真实 OpenAI-compatible API。Mock 不构成真实 LLM 接通或性能证据。",
        "",
        "## 真实 API",
        "",
    ]
    if real is None:
        lines.append("真实 Canary：NOT RUN。")
    else:
        lines += [
            f"- 状态：**{real['status']}**",
            f"- API 真实接通：{real['api_connected']}",
            f"- HTTP attempts：{real['api_attempt_count']}",
            f"- 输入/输出 Token：{real['input_tokens']} / {real['output_tokens']}",
            f"- 成本（USD）：{real['cost_usd']}",
            f"- 延迟（秒）：{real['latency_seconds']}",
            f"- Agent 状态：{real.get('agent_status', 'NOT_RUN')}",
            f"- LLM decisions：{real.get('llm_decision_count', 0)}",
        ]
        if real.get("missing_configuration"):
            lines.append(
                "- 缺失配置（仅名称）：`" + "`、`".join(real["missing_configuration"]) + "`"
            )
        if real.get("models"):
            lines.append("- 响应模型：`" + "`、`".join(real["models"]) + "`")
        if real.get("errors"):
            lines.append(
                "- 错误类型：`"
                + "`、`".join(sorted({row["error_type"] for row in real["errors"]}))
                + "`"
            )
    lines += ["", "## Mock 多轮集成", ""]
    if mock is None:
        lines.append("Mock Canary：NOT RUN。")
    else:
        lines += [
            f"- 状态：**{mock['status']}**；backend=`mock`，不是实际 API 调用。",
            f"- Agent 状态：{mock['agent_status']}；LLM decisions={mock['llm_decision_count']}；Mock attempts={mock['api_attempt_count']}。",
            f"- 工具轨迹：`{'` → `'.join(mock['executed_tools'])}`",
            f"- 硬约束违规：{mock['constraint_violations']}；hash chain valid={mock['hash_chain_valid']}。",
        ]
    lines += [
        "",
        "## 边界",
        "",
        "Phase 2 B0/B1/B2、API genome search、Validation/Test 和模型训练均未执行。没有可验证的算法提升结论。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Execute exactly one explicitly selected Canary mode and update its report."""
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--mock", action="store_true")
    group.add_argument("--execute-real", action="store_true")
    parser.add_argument("--outdir", type=Path, default=HERE / "results")
    args = parser.parse_args()
    mock_path = args.outdir / "mock" / "summary.json"
    real_path = args.outdir / "real" / "summary.json"
    if args.mock:
        summary = run_mock_canary(args.outdir / "mock")
    else:
        summary = execute_real_canary(args.outdir / "real")
    mock = (
        json.loads(mock_path.read_text(encoding="utf-8"))
        if mock_path.exists()
        else None
    )
    real = (
        json.loads(real_path.read_text(encoding="utf-8"))
        if real_path.exists()
        else None
    )
    report = ROOT / "D094_API_CANARY_REPORT.md"
    report.write_text(render_markdown(mock, real), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": summary["status"],
                "api_connected": summary["api_connected"],
                "api_attempt_count": summary["api_attempt_count"],
            }
        )
    )


if __name__ == "__main__":
    main()
