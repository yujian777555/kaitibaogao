"""Read-only, episode-level deep analysis of the completed D-094 R3.1 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from d094_behavior import behavior_distance, behavior_representation
from d094_feedback_evolution import classify_failures


TOLERANCE = 1e-12
ARMS = ("B1", "B2", "B3", "B4", "B5")
EVOLUTION_ARMS = ARMS[1:]
COMPARISONS = (
    ("B3_minus_B2", "B2", "B3"),
    ("B4_minus_B2", "B2", "B4"),
    ("B5_minus_B3", "B3", "B5"),
    ("B5_minus_B4", "B4", "B5"),
)
METRIC_NAMES = (
    "task_success_rate",
    "recovery_success_rate",
    "constraint_violation",
    "harm",
    "tool_cost",
    "input_tokens",
    "output_tokens",
    "token_cost_usd",
    "token_cost_upper_usd",
    "latency_seconds",
    "behavior_diversity",
)


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _assert_json_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"non-string JSON key at {path}: {key!r}")
            _assert_json_keys(item, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_json_keys(item, f"{path}[{index}]")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_episodes(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _sent_requests(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in row.get("request_ledger", [])
        if record.get("transport_sent") is not False
    ]


def _close(first: float, second: float) -> bool:
    return math.isclose(first, second, rel_tol=1e-10, abs_tol=1e-12)


def _episode_metrics(row: dict[str, Any]) -> dict[str, Any]:
    """Rebuild episode metrics from events, terminal state and sent request records."""
    requests = _sent_requests(row)
    tool_results = [
        event["payload"]
        for event in row["events"]
        if event.get("event_type") == "tool_result"
    ]
    finished = [
        event["payload"]
        for event in row["events"]
        if event.get("event_type") == "run_finished"
    ]
    if len(finished) != 1:
        raise ValueError(f"episode {row['episode_id']} has no unique terminal event")
    completed = row.get("final_public_observation", {}).get("state", {}).get("completed")
    if type(completed) is not bool:
        raise ValueError(f"episode {row['episode_id']} lacks a public terminal state")
    if any(record.get("cost_usd") is None for record in requests):
        raise ValueError("deep analysis requires known request costs")
    phenotype = behavior_representation(
        row["events"],
        agent_status=row["agent_status"],
        final_public_observation=row["final_public_observation"],
    )["canonical_sha256"]
    result = {
        "task_success": completed,
        "recovery_success": completed,
        "constraint_violation": finished[0]["constraint_violations"],
        "harm": sum(payload.get("harm", 0.0) for payload in tool_results),
        "tool_cost": sum(payload.get("cost", 0.0) for payload in tool_results),
        "input_tokens": sum(record.get("input_tokens") or 0 for record in requests),
        "output_tokens": sum(record.get("output_tokens") or 0 for record in requests),
        "token_cost_usd": sum(record["cost_usd"] for record in requests),
        "token_cost_upper_usd": sum(
            record.get("cost_upper_usd", record["cost_usd"]) for record in requests
        ),
        "latency_seconds": sum(
            record.get("latency_seconds") or 0.0 for record in requests
        ),
        "phenotype_hash": phenotype,
    }
    saved = row["metrics"]
    for key, value in result.items():
        if isinstance(value, float):
            if not _close(value, saved[key]):
                raise ValueError(f"saved episode metric mismatch: {row['episode_id']}:{key}")
        elif value != saved[key]:
            raise ValueError(f"saved episode metric mismatch: {row['episode_id']}:{key}")
    return result


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("cannot aggregate zero episodes")
    metrics = [row["_recomputed"] for row in rows]
    count = len(rows)
    return {
        "episode_count": count,
        "task_success_rate": sum(row["task_success"] for row in metrics) / count,
        "recovery_success_rate": sum(row["recovery_success"] for row in metrics) / count,
        "constraint_violation": sum(row["constraint_violation"] for row in metrics),
        "harm": sum(row["harm"] for row in metrics),
        "tool_cost": sum(row["tool_cost"] for row in metrics),
        "input_tokens": sum(row["input_tokens"] for row in metrics),
        "output_tokens": sum(row["output_tokens"] for row in metrics),
        "token_cost_usd": sum(row["token_cost_usd"] for row in metrics),
        "token_cost_upper_usd": sum(row["token_cost_upper_usd"] for row in metrics),
        "latency_seconds": sum(row["latency_seconds"] for row in metrics) / count,
        "behavior_diversity": len({row["phenotype_hash"] for row in metrics}) / count,
        "execution_errors": sum(bool(row["execution_error"]) for row in rows),
        "real_http_requests": sum(len(_sent_requests(row)) for row in rows),
    }


def _objectives(metrics: dict[str, Any]) -> tuple[float, ...]:
    return (
        1.0 - metrics["task_success_rate"],
        1.0 - metrics["recovery_success_rate"],
        float(metrics["constraint_violation"]),
        metrics["harm"],
        metrics["tool_cost"],
        metrics["token_cost_upper_usd"],
        metrics["latency_seconds"],
    )


def _dominates(first: Iterable[float], second: Iterable[float]) -> bool:
    left, right = tuple(first), tuple(second)
    if len(left) != len(right):
        raise ValueError("objective dimensions differ")
    return all(a <= b + TOLERANCE for a, b in zip(left, right)) and any(
        a < b - TOLERANCE for a, b in zip(left, right)
    )


def _delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    return {name: second[name] - first[name] for name in METRIC_NAMES}


def _episode_objectives(row: dict[str, Any]) -> tuple[float, ...]:
    metric = row["_recomputed"]
    return (
        1.0 - float(metric["task_success"]),
        1.0 - float(metric["recovery_success"]),
        float(metric["constraint_violation"]),
        metric["harm"],
        metric["tool_cost"],
        metric["token_cost_upper_usd"],
        metric["latency_seconds"],
    )


def _candidate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows = sorted(rows, key=lambda row: (row["task_id"], row["seed"]))
    identities = {(row["arm"], row["phase"], row["genome_sha256"]) for row in rows}
    if len(identities) != 1:
        raise ValueError("candidate group has mixed identities")
    metrics = _aggregate(rows)
    behavior_events = [event for row in rows for event in row["events"]]
    behavior = behavior_representation(behavior_events, agent_status="MULTI_EPISODE")
    return {
        "arm": rows[0]["arm"],
        "phase": rows[0]["phase"],
        "genome": rows[0]["genome"],
        "genome_sha256": rows[0]["genome_sha256"],
        "episode_ids": [row["episode_id"] for row in rows],
        "pair_keys": [f"{row['task_id']}:{row['seed']}" for row in rows],
        "metrics": metrics,
        "objectives": list(_objectives(metrics)),
        "feasible": metrics["constraint_violation"] == 0
        and metrics["execution_errors"] == 0,
        "phenotype_hash": behavior["canonical_sha256"],
        "phenotype_matches_saved": all(
            behavior["canonical_sha256"] == saved["candidate"]["phenotype_hash"]
            for saved in _load_json(
                rows[0]["_outdir"] / f"archive_{rows[0]['arm']}.json"
            )
            if saved["genome_sha256"] == rows[0]["genome_sha256"]
        ),
        "failure_profile": classify_failures(rows),
        "_rows": rows,
    }


def _front(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feasible = [candidate for candidate in candidates if candidate["feasible"]]
    return sorted(
        [
            candidate
            for candidate in feasible
            if not any(
                _dominates(other["objectives"], candidate["objectives"])
                for other in feasible
                if other is not candidate
            )
        ],
        key=lambda candidate: candidate["genome_sha256"],
    )


def _public_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in candidate.items() if key != "_rows"}


def _sequence(row: dict[str, Any]) -> str:
    actions = []
    for event in row["events"]:
        if event.get("event_type") == "decision":
            payload = event["payload"]
            actions.append(
                payload.get("tool_name")
                if payload.get("action") == "tool_call"
                else str(payload.get("action"))
            )
    return " -> ".join(actions)


def _failure_modes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rejections = Counter()
    sequences = Counter()
    terminals = Counter()
    for row in rows:
        terminals[row["agent_status"]] += 1
        sequences[_sequence(row)] += 1
        for event in row["events"]:
            if event.get("event_type") == "tool_rejected":
                observation = event["payload"].get("observation", {})
                rejections[str(observation.get("error", "UNKNOWN"))] += 1
    return {
        "terminal_status_counts": dict(sorted(terminals.items())),
        "action_sequence_counts": dict(sorted(sequences.items())),
        "rejection_error_counts": dict(sorted(rejections.items())),
        "failure_profile": classify_failures(rows),
    }


def _request_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    requests = [record for row in rows for record in _sent_requests(row)]
    failed = [
        record
        for record in requests
        if record.get("status") != "SUCCESS" or record.get("error") is not None
    ]
    costs = [record["cost_usd"] for record in requests]
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_task[row["task_id"]].append(row)
    return {
        "episodes": len(rows),
        "requests": len(requests),
        "input_tokens": sum(record.get("input_tokens") or 0 for record in requests),
        "output_tokens": sum(record.get("output_tokens") or 0 for record in requests),
        "cost_usd": sum(costs),
        "mean_input_tokens_per_request": (
            sum(record.get("input_tokens") or 0 for record in requests) / len(requests)
            if requests
            else None
        ),
        "mean_output_tokens_per_request": (
            sum(record.get("output_tokens") or 0 for record in requests) / len(requests)
            if requests
            else None
        ),
        "max_input_tokens_per_request": max(
            (record.get("input_tokens") or 0 for record in requests), default=0
        ),
        "max_output_tokens_per_request": max(
            (record.get("output_tokens") or 0 for record in requests), default=0
        ),
        "max_requests_per_episode": max(
            (len(_sent_requests(row)) for row in rows), default=0
        ),
        "transport_retry_status": "FROZEN_MAX_RETRIES_0; attempt is the per-episode request ordinal, not a retry counter",
        "same_prompt_repeat_records": sum(
            count - 1
            for row in rows
            for count in Counter(
                record.get("prompt_sha256") for record in _sent_requests(row)
            ).values()
            if count > 1
        ),
        "same_prompt_repeat_ratio": (
            sum(
                count - 1
                for row in rows
                for count in Counter(
                    record.get("prompt_sha256") for record in _sent_requests(row)
                ).values()
                if count > 1
            )
            / len(requests)
            if requests
            else None
        ),
        "failed_request_count": len(failed),
        "failed_request_cost_usd": sum(record["cost_usd"] for record in failed),
        "per_task": {
            task: {
                "episodes": len(task_rows),
                "mean_input_tokens_per_episode": _aggregate(task_rows)["input_tokens"]
                / len(task_rows),
                "mean_output_tokens_per_episode": _aggregate(task_rows)["output_tokens"]
                / len(task_rows),
                "mean_requests_per_episode": _aggregate(task_rows)["real_http_requests"]
                / len(task_rows),
            }
            for task, task_rows in sorted(by_task.items())
        },
        "canonical_message_bytes_status": "NOT_RECORDED_IN_EPISODES; frozen cap was 4096 bytes",
        "independent_audit_requires_real_api": False,
    }


def _quality_credit(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Constraint-first task/recovery/harm credit; resource-only changes earn zero."""
    parent, child = first["_recomputed"], second["_recomputed"]
    if child["constraint_violation"] > parent["constraint_violation"]:
        return -1.0
    if child["constraint_violation"] < parent["constraint_violation"]:
        return 1.0
    parent_quality = (
        1.0 - float(parent["task_success"]),
        1.0 - float(parent["recovery_success"]),
        parent["harm"],
    )
    child_quality = (
        1.0 - float(child["task_success"]),
        1.0 - float(child["recovery_success"]),
        child["harm"],
    )
    if _dominates(child_quality, parent_quality):
        return 1.0
    if _dominates(parent_quality, child_quality):
        return -1.0
    return 0.0


def _parent_child(
    arm: str,
    ledger: list[dict[str, Any]],
    candidates: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    result = []
    for event in ledger:
        if event.get("event_type") != "variation":
            continue
        child_hash = event["offspring_genome_hash"]
        parent_hash = event["parent_genome_hashes"][0]
        base = {
            "arm": arm,
            "generation": event["generation"],
            "proposal_ordinal": event["proposal_ordinal"],
            "operator": event["operator"],
            "parent_genome_sha256": parent_hash,
            "offspring_genome_sha256": child_hash,
            "mutation_locus": event.get("mutation_locus"),
            "before_value": event.get("before_value"),
            "after_value": event.get("after_value"),
            "outcome": event["outcome"],
            "operator_probabilities": event["operator_probabilities"],
        }
        if event["outcome"] != "ACCEPTED_FOR_EVALUATION":
            result.append({**base, "credit_status": "NOT_EVALUATED_NO_CREDIT"})
            continue
        if parent_hash not in candidates or child_hash not in candidates:
            raise ValueError("accepted variation lacks raw parent or child episodes")
        parent, child = candidates[parent_hash], candidates[child_hash]
        parent_rows = {
            (row["task_id"], row["seed"]): row for row in parent["_rows"]
        }
        child_rows = {(row["task_id"], row["seed"]): row for row in child["_rows"]}
        if set(parent_rows) != set(child_rows) or len(parent_rows) != len(parent["_rows"]):
            raise ValueError("parent/offspring evaluation keys are not uniquely paired")
        pairs = []
        for key in sorted(parent_rows):
            first, second = parent_rows[key], child_rows[key]
            child_improves = _dominates(_episode_objectives(second), _episode_objectives(first))
            parent_improves = _dominates(_episode_objectives(first), _episode_objectives(second))
            pairs.append(
                {
                    "task_id": key[0],
                    "seed": key[1],
                    "delta_task_success": int(second["_recomputed"]["task_success"])
                    - int(first["_recomputed"]["task_success"]),
                    "delta_recovery_success": int(
                        second["_recomputed"]["recovery_success"]
                    )
                    - int(first["_recomputed"]["recovery_success"]),
                    "delta_constraint_violation": second["_recomputed"][
                        "constraint_violation"
                    ]
                    - first["_recomputed"]["constraint_violation"],
                    "delta_harm": second["_recomputed"]["harm"]
                    - first["_recomputed"]["harm"],
                    "delta_tool_cost": second["_recomputed"]["tool_cost"]
                    - first["_recomputed"]["tool_cost"],
                    "delta_token_cost_usd": second["_recomputed"]["token_cost_usd"]
                    - first["_recomputed"]["token_cost_usd"],
                    "delta_latency_seconds": second["_recomputed"]["latency_seconds"]
                    - first["_recomputed"]["latency_seconds"],
                    "offspring_pareto_improvement": child_improves,
                    "parent_pareto_improvement": parent_improves,
                    "paired_dominance_reward": float(child_improves) - float(parent_improves),
                    "paired_quality_credit": _quality_credit(first, second),
                }
            )
        reward = sum(pair["paired_dominance_reward"] for pair in pairs) / len(pairs)
        quality_credit = sum(pair["paired_quality_credit"] for pair in pairs) / len(pairs)
        result.append(
            {
                **base,
                "credit_status": "EX_POST_ANALYSIS_ONLY_NOT_USED_BY_R3_1",
                "paired_episode_count": len(pairs),
                "paired_dominance_reward": reward,
                "paired_quality_credit": quality_credit,
                "candidate_offspring_dominates_parent": _dominates(
                    child["objectives"], parent["objectives"]
                ),
                "candidate_parent_dominates_offspring": _dominates(
                    parent["objectives"], child["objectives"]
                ),
                "offspring_phenotype_changed": child["phenotype_hash"]
                != parent["phenotype_hash"],
                "pairs": pairs,
            }
        )
    return result


def _operator_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[record["operator"]].append(record)
    output = {}
    for operator, rows in sorted(grouped.items()):
        accepted = [row for row in rows if row["outcome"] == "ACCEPTED_FOR_EVALUATION"]
        output[operator] = {
            "proposals": len(rows),
            "accepted": len(accepted),
            "duplicates": len(rows) - len(accepted),
            "mean_paired_dominance_reward": (
                sum(row["paired_dominance_reward"] for row in accepted) / len(accepted)
                if accepted
                else None
            ),
            "mean_paired_quality_credit": (
                sum(row["paired_quality_credit"] for row in accepted) / len(accepted)
                if accepted
                else None
            ),
            "positive_reward_count": sum(
                row["paired_dominance_reward"] > 0 for row in accepted
            ),
            "negative_reward_count": sum(
                row["paired_dominance_reward"] < 0 for row in accepted
            ),
            "positive_quality_credit_count": sum(
                row["paired_quality_credit"] > 0 for row in accepted
            ),
            "negative_quality_credit_count": sum(
                row["paired_quality_credit"] < 0 for row in accepted
            ),
            "phenotype_changed_count": sum(
                row["offspring_phenotype_changed"] for row in accepted
            ),
        }
    return output


def analyze_r3_deep(source: Path, output: Path) -> dict[str, Any]:
    """Analyze saved R3.1 data without network access or writes to the source directory."""
    source = Path(source).resolve()
    output = Path(output).resolve()
    if output == source or source in output.parents:
        raise ValueError("deep-analysis output must be outside the immutable R3.1 directory")
    source_files = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }
    rows = _load_episodes(source / "episodes.jsonl")
    if len(rows) != 42 or len({row["episode_id"] for row in rows}) != 42:
        raise ValueError("expected 42 unique R3.1 episodes")
    for row in rows:
        row["_outdir"] = source
        row["_recomputed"] = _episode_metrics(row)
    manifest = _load_json(source / "train_manifest.json")
    independent_audit = _load_json(source / "independent_audit.json")

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["arm"], row["phase"])].append(row)
    aggregates = {
        f"{arm}:{phase}": _aggregate(group)
        for (arm, phase), group in sorted(grouped.items())
    }
    per_task_seed = {}
    for (arm, phase), group in sorted(grouped.items()):
        cells = defaultdict(list)
        for row in group:
            cells[(row["task_id"], row["seed"])].append(row)
        per_task_seed[f"{arm}:{phase}"] = {
            f"{task}:{seed}": _aggregate(cell)
            for (task, seed), cell in sorted(cells.items())
        }

    final_comparisons = {}
    for label, first_arm, second_arm in COMPARISONS:
        first_phase = "fixed" if first_arm == "B1" else "final"
        second_phase = "fixed" if second_arm == "B1" else "final"
        first = grouped[(first_arm, first_phase)]
        second = grouped[(second_arm, second_phase)]
        by_seed = {}
        for seed in sorted({row["seed"] for row in first + second}):
            left = [row for row in first if row["seed"] == seed]
            right = [row for row in second if row["seed"] == seed]
            by_seed[str(seed)] = _delta(_aggregate(left), _aggregate(right))
        final_comparisons[label] = {
            "overall": _delta(_aggregate(first), _aggregate(second)),
            "per_seed": by_seed,
        }

    candidates_by_arm = {}
    parent_child_by_arm = {}
    search_analysis = {}
    for arm in EVOLUTION_ARMS:
        ledger = _load_json(source / f"evolution_{arm}.json")
        search_groups = defaultdict(list)
        for row in rows:
            if row["arm"] == arm and row["phase"] == "search":
                search_groups[row["genome_sha256"]].append(row)
        candidates = {
            genome_hash: _candidate(group) for genome_hash, group in search_groups.items()
        }
        candidates_by_arm[arm] = candidates
        parent_child = _parent_child(arm, ledger, candidates)
        parent_child_by_arm[arm] = parent_child
        front = _front(list(candidates.values()))
        selected = min(front, key=lambda item: (item["objectives"], item["genome_sha256"])) if front else None
        survivor_events = [
            event for event in ledger if event.get("event_type") == "survivor_selection"
        ]
        feedback_events = [
            event for event in ledger if event.get("event_type") == "feedback_update"
        ]
        probability_ranges = {}
        for operator in sorted(
            {
                event["operator"]
                for event in ledger
                if event.get("event_type") == "variation"
            }
        ):
            values = [
                event["operator_probabilities"][operator]
                for event in ledger
                if event.get("event_type") == "variation"
            ]
            probability_ranges[operator] = {"min": min(values), "max": max(values)}
        search_analysis[arm] = {
            "candidates": [
                _public_candidate(candidates[key]) for key in sorted(candidates)
            ],
            "unique_genomes": len(candidates),
            "unique_phenotypes": len(
                {candidate["phenotype_hash"] for candidate in candidates.values()}
            ),
            "successful_candidates": sum(
                candidate["metrics"]["task_success_rate"] > 0
                for candidate in candidates.values()
            ),
            "independent_pareto_front": [
                candidate["genome_sha256"] for candidate in front
            ],
            "independent_final_selection": None
            if selected is None
            else selected["genome_sha256"],
            "variation_count": sum(
                event.get("event_type") == "variation" for event in ledger
            ),
            "duplicate_proposal_count": sum(
                event.get("event_type") == "duplicate_proposal" for event in ledger
            ),
            "feedback_update_count": len(feedback_events),
            "operator_probability_ranges": probability_ranges,
            "survivor_events": survivor_events,
            "parent_child": parent_child,
            "operator_summary": _operator_summary(parent_child),
        }

    behavior_pairs = {}
    for arm, candidates in candidates_by_arm.items():
        pairs = []
        ordered = [candidates[key] for key in sorted(candidates)]
        for index, first in enumerate(ordered):
            for second in ordered[index + 1 :]:
                first_behavior = behavior_representation(
                    [event for row in first["_rows"] for event in row["events"]],
                    agent_status="MULTI_EPISODE",
                )
                second_behavior = behavior_representation(
                    [event for row in second["_rows"] for event in row["events"]],
                    agent_status="MULTI_EPISODE",
                )
                pairs.append(
                    {
                        "first_genome_sha256": first["genome_sha256"],
                        "second_genome_sha256": second["genome_sha256"],
                        "same_phenotype": first["phenotype_hash"]
                        == second["phenotype_hash"],
                        "edit_distance": behavior_distance(first_behavior, second_behavior),
                        "feature_distance": behavior_distance(
                            first_behavior, second_behavior, metric="feature"
                        ),
                        "delta_task_success_rate": second["metrics"]["task_success_rate"]
                        - first["metrics"]["task_success_rate"],
                        "delta_recovery_success_rate": second["metrics"][
                            "recovery_success_rate"
                        ]
                        - first["metrics"]["recovery_success_rate"],
                    }
                )
        behavior_pairs[arm] = pairs

    result = {
        "analysis_schema": "d094_r3_1_deep_analysis_v1",
        "scientific_scope": "READ_ONLY_EXPLORATORY_ANALYSIS",
        "api_used": False,
        "source_directory": str(source),
        "source_files_sha256": source_files,
        "source_episodes_sha256": hashlib.sha256(
            (source / "episodes.jsonl").read_bytes()
        ).hexdigest(),
        "source_independent_audit_status": independent_audit.get("status"),
        "design": {
            "protocol": manifest["protocol"],
            "split": manifest["split"],
            "tasks": [task["task_id"] for task in manifest["tasks"]],
            "seeds": sorted({row["seed"] for row in rows}),
            "arms": list(ARMS),
            "phase_counts": {
                key: value["episode_count"] for key, value in aggregates.items()
            },
        },
        "episode_identity": {
            "count": len(rows),
            "unique_episode_ids": len({row["episode_id"] for row in rows}),
            "unique_provider_request_ids": len(
                {
                    record.get("request_id")
                    for row in rows
                    for record in _sent_requests(row)
                }
            ),
            "all_hash_chains_valid": all(row["hash_chain_valid"] for row in rows),
            "execution_errors": sum(bool(row["execution_error"]) for row in rows),
        },
        "aggregates": aggregates,
        "per_task_seed": per_task_seed,
        "final_comparisons": final_comparisons,
        "search": search_analysis,
        "behavior_pairs": behavior_pairs,
        "failure_modes": {
            f"{arm}:{phase}": _failure_modes(group)
            for (arm, phase), group in sorted(grouped.items())
        },
        "request_analysis": {
            "all": _request_analysis(rows),
            "by_arm_phase": {
                f"{arm}:{phase}": _request_analysis(group)
                for (arm, phase), group in sorted(grouped.items())
            },
        },
        "data_gaps": [
            "Only one Train task and two seeds were evaluated; no cross-task or confirmatory inference is possible.",
            "Final episodes repeat the same Train task and seeds; they are not held-out generalization evidence.",
            "Canonical request message bytes were not saved in episode records; only token usage and the frozen byte cap are auditable.",
            "One generation and two offspring per arm cannot identify stable operator credit or long-horizon effects.",
            "Ex-post parent/offspring credit describes this run; it was not used by R3.1 selection and is not a new experiment result.",
        ],
    }
    after_files = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }
    if after_files != source_files:
        raise RuntimeError("immutable R3.1 source changed during deep analysis")
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("deep-analysis output directory must be empty")
    _assert_json_keys(result)
    result["analysis_sha256"] = _sha256(result)
    (output / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze_r3_deep(args.source, args.outdir)
    print(
        json.dumps(
            {
                "status": "PASS",
                "scope": result["scientific_scope"],
                "episodes": result["episode_identity"]["count"],
                "analysis_sha256": result["analysis_sha256"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
