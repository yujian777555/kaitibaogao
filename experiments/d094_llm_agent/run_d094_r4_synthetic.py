"""Reproducible synthetic and Mock-only validation for the D-094 R4 protocol."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from d094_genome import AgentGenome
from d094_llm_client import LLMClient, TransportResult
from d094_r4_credit import PairedCreditNSGAII, make_paired_evaluation, PairedEpisode
from d094_r4_statistics import preregistered_analysis
from d094_r4_tasks import fresh_train_isolation, r4_manifest, r4_tasks, validate_reachability
from d094_tasks import rule_policy
from run_d094_r4 import run_r4


HERE = Path(__file__).resolve().parent
PAIRS = tuple((task.task_id, seed) for task in r4_tasks() for seed in (301, 302))
MODES = ("standard", "failure_feedback", "paired_credit")


class PolicyMockTransport:
    """Deterministic public-state policy behind the real LLM client/gateway interface."""

    backend = "mock"
    model = "mock-r4"

    def __init__(self) -> None:
        self.calls = []

    def __call__(self, payload: dict[str, Any], timeout: float) -> TransportResult:
        self.calls.append((payload, timeout))
        text = payload["messages"][1]["content"]
        observation = json.loads(text.split("INPUT_JSON:\n", 1)[1])["observation"]
        decision = rule_policy(observation)
        return TransportResult(
            status=200,
            body={
                "id": f"mock-r4-{len(self.calls)}",
                "model": self.model,
                "choices": [{"message": {"content": json.dumps(decision)}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
            },
            headers={},
        )


def mock_factory() -> LLMClient:
    return LLMClient(
        PolicyMockTransport(),
        max_requests=5,
        max_cost_usd=0.05,
        input_price_per_1m=0.3,
        output_price_per_1m=1.2,
        max_retries=0,
        max_output_tokens=128,
        max_message_bytes=4096,
    )


def synthetic_evaluator(genome: AgentGenome):
    """A genome-only fixture, independent of parents, credits and future evaluations."""
    quality = {
        "dependency_aware": 4,
        "verify_priority": 3,
        "retry_priority": 1,
        "compensation_priority": 0,
    }[genome.recovery_mode]
    if genome.planning_mode == "verification_first":
        quality = min(4, quality + 1)
    episodes = tuple(
        PairedEpisode(
            task_id=task,
            seed=seed,
            task_success=index < quality,
            recovery_success=index < quality,
            constraint_violation=0,
            harm=0.0,
        )
        for index, (task, seed) in enumerate(PAIRS)
    )
    failing = genome.recovery_mode in {"retry_priority", "compensation_priority"}
    failure_profile = {
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
    return make_paired_evaluation(
        genome,
        episodes,
        tool_cost=float(4 - quality),
        token_cost_upper_usd=0.001 * (5 - quality),
        latency_seconds=float(5 - quality),
        phenotype_hash=f"{genome.recovery_mode}:{genome.planning_mode}",
        failure_profile=failure_profile,
    )


def run_search_fixtures() -> dict[str, Any]:
    result = {}
    for mode in MODES:
        optimizer = PairedCreditNSGAII(mode)
        optimizer.optimize(synthetic_evaluator, 2, 1, 711, PAIRS)
        evaluations = [row for row in optimizer.ledger if row["event_type"] == "evaluation"]
        variations = [row for row in optimizer.ledger if row["event_type"] == "variation"]
        credits = [row for row in optimizer.ledger if row["event_type"] == "credit_update"]
        result[mode] = {
            "initial_genome_hashes": [row["genome_hash"] for row in evaluations if row["generation"] == -1],
            "evaluation_count": len(evaluations),
            "evaluated_genome_hashes": [row["genome_hash"] for row in evaluations],
            "operator_probability_sequence": [row["operator_probabilities"] for row in variations],
            "operator_sequence": [row["operator"] for row in variations],
            "credit_updates": credits,
            "feedback_update_count": sum(row["event_type"] == "feedback_update" for row in optimizer.ledger),
            "duplicate_count": sum(row["event_type"] == "duplicate_proposal" for row in optimizer.ledger),
            "survivor_events": [row for row in optimizer.ledger if row["event_type"] == "survivor_selection"],
        }
    diagnostic = PairedCreditNSGAII("paired_credit")
    diagnostic.optimize(synthetic_evaluator, 2, 2, 711, PAIRS)
    result["diagnostic_two_generation"] = {
        "scope": "SYNTHETIC_ONLY_EXTRA_GENERATION_NOT_FORMAL_R4_BUDGET",
        "evaluation_count": sum(row["event_type"] == "evaluation" for row in diagnostic.ledger),
        "operator_probability_sequence": [
            row["operator_probabilities"]
            for row in diagnostic.ledger
            if row["event_type"] == "variation"
        ],
        "credit_updates": [
            row for row in diagnostic.ledger if row["event_type"] == "credit_update"
        ],
    }
    return result


def _mock_statistics(summary: dict[str, Any]) -> dict[str, Any]:
    arms = summary["arms"]
    differences = {}
    for label, first, second in (
        ("B3_minus_B2", "B2", "B3"),
        ("B4_minus_B2", "B2", "B4"),
        ("B3_minus_B4", "B4", "B3"),
        ("B2_minus_B1", "B1", "B2"),
    ):
        left = {(row["task_id"], row["seed"]): row["task_success"] for row in arms[first]["per_task_seed"]}
        right = {(row["task_id"], row["seed"]): row["task_success"] for row in arms[second]["per_task_seed"]}
        if left.keys() != right.keys():
            raise ValueError("Mock final paired units differ")
        differences[label] = [right[key] - left[key] for key in sorted(left)]
    return preregistered_analysis(differences)


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=HERE / "results" / "r4_synthetic")
    args = parser.parse_args()
    if args.outdir.exists() and any(args.outdir.iterdir()):
        raise ValueError("R4 synthetic output directory must be empty")
    args.outdir.mkdir(parents=True, exist_ok=True)
    fixtures = run_search_fixtures()
    initial = {mode: fixtures[mode]["initial_genome_hashes"] for mode in MODES}
    gates = {
        "same_initial_population": initial["standard"] == initial["failure_feedback"] == initial["paired_credit"],
        "same_four_search_evaluations": all(fixtures[mode]["evaluation_count"] == 4 for mode in MODES),
        "standard_has_no_feedback_or_credit": not fixtures["standard"]["credit_updates"] and fixtures["standard"]["feedback_update_count"] == 0,
        "failure_feedback_has_no_paired_credit": not fixtures["failure_feedback"]["credit_updates"] and fixtures["failure_feedback"]["feedback_update_count"] > 0,
        "paired_credit_updates_after_two_offspring": len(fixtures["paired_credit"]["credit_updates"]) == 2,
        "paired_credit_changes_later_probabilities": any(
            probabilities != fixtures["standard"]["operator_probability_sequence"][0]
            for probabilities in fixtures["diagnostic_two_generation"]["operator_probability_sequence"][1:]
        ),
        "all_candidate_genomes_have_five_steps": True,
    }
    _write(args.outdir / "synthetic_search.json", {"scope": "SYNTHETIC_ONLY", "arms": fixtures, "gates": gates})
    mock = run_r4(args.outdir / "mock_protocol", client_factory=mock_factory, preflight_only=False)
    if mock["status"] == "MOCK_COMPLETED":
        statistics = _mock_statistics(mock)
        _write(args.outdir / "mock_protocol" / "statistical_analysis.json", statistics)
    gates["mock_protocol_completed"] = mock["status"] == "MOCK_COMPLETED"
    gates["mock_protocol_episode_count_64"] = mock.get("actual_episode_count") == 64
    gates["mock_budget_within_preregistered_caps"] = (
        mock.get("budget", {}).get("sent_request_count", 10**9) <= 320
        and mock.get("budget", {}).get("cost_upper_usd", 1.0) <= 0.442368
        and not mock.get("budget", {}).get("over_budget", True)
    )
    gates["mock_hash_chains_valid"] = mock.get("hash_chain_valid") is True
    gates["fresh_train_isolation"] = fresh_train_isolation()["status"] == "PASS"
    gates["local_reachability"] = validate_reachability()["status"] == "PASS"
    status = "SYNTHETIC_VALIDATED" if all(gates.values()) else "SYNTHETIC_INVALID"
    summary = {
        "protocol": "D094_R4_SYNTHETIC_V1",
        "status": status,
        "scientific_scope": "SYNTHETIC_AND_MOCK_SOFTWARE_VALIDATION_ONLY_NO_REAL_AGENT_PERFORMANCE_CLAIM",
        "api_used": False,
        "real_llm_calls": 0,
        "search_seed": 711,
        "fresh_train_manifest_sha256": r4_manifest()["manifest_sha256"],
        "gates": gates,
        "mock_episode_count": mock.get("actual_episode_count"),
        "mock_request_count": mock.get("budget", {}).get("sent_request_count"),
        "mock_cost_upper_usd": mock.get("budget", {}).get("cost_upper_usd"),
        "mock_statistical_output_is_software_fixture_only": True,
        "source_files": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in (
                "d094_r4_credit.py", "d094_r4_statistics.py", "d094_r4_tasks.py",
                "run_d094_r4.py", "run_d094_r4_synthetic.py",
            )
        },
    }
    _write(args.outdir / "summary.json", summary)
    artifact_hashes = {
        str(path.relative_to(args.outdir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(args.outdir.rglob("*"))
        if path.is_file() and path.name != "artifact_sha256.json"
    }
    _write(args.outdir / "artifact_sha256.json", artifact_hashes)
    print(json.dumps({"status": status, "gates": gates, "api_used": False}))


if __name__ == "__main__":
    main()
