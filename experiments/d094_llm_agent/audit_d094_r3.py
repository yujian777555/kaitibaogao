"""Independent, API-free recomputation of a completed D-094 R3/R3.1 run."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


EVOLUTION_ARMS = ("B2", "B3", "B4", "B5")
FAILURE_NAMES = (
    "planning_failure",
    "tool_call_failure",
    "dependency_failure",
    "recovery_failure",
    "verification_failure",
    "task_incompletion",
    "unnecessary_tool_call",
)
FEATURE_WEIGHTS = {
    "tool_call_count": 2.0,
    "verification_count": 1.0,
    "recovery_count": 2.0,
    "failed_call_count": 2.0,
    "rejected_call_count": 1.0,
    "retry_count": 2.0,
    "completed": 1.0,
    "runtime_abort": 1.0,
    "state_transition_count": 1.0,
}
DELTA_FIELDS = (
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
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _same(first: Any, second: Any) -> bool:
    if isinstance(first, float) or isinstance(second, float):
        return (
            first is not None
            and second is not None
            and math.isclose(first, second, rel_tol=1e-9, abs_tol=1e-12)
        )
    if isinstance(first, dict) and isinstance(second, dict):
        return set(first) == set(second) and all(
            _same(first[key], second[key]) for key in first
        )
    if isinstance(first, list) and isinstance(second, list):
        return len(first) == len(second) and all(
            _same(a, b) for a, b in zip(first, second)
        )
    return first == second


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("D-094 R3 independent audit failed: " + message)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _verify_chain(events: list[dict[str, Any]]) -> bool:
    previous = None
    for index, event in enumerate(events):
        unsigned = {key: value for key, value in event.items() if key != "event_sha256"}
        if event.get("sequence") != index or event.get("previous_event_sha256") != previous:
            return False
        if _hash(unsigned) != event.get("event_sha256"):
            return False
        previous = event["event_sha256"]
    return True


def _behavior(
    events: list[dict[str, Any]],
    status: str,
    final_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sequence = []
    features = {name: 0.0 for name in FEATURE_WEIGHTS}
    transitions = []
    for event in events:
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        if event_type == "decision":
            action = payload.get("action")
            tool_name = payload.get("tool_name")
            arguments = _canonical(payload.get("tool_arguments", {})).decode("utf-8")
            sequence.append(f"D|{action}|{tool_name}|{arguments}")
            if action == "tool_call":
                features["tool_call_count"] += 1
                features["verification_count"] += "verify" in str(tool_name)
                features["recovery_count"] += any(
                    word in str(tool_name) for word in ("recover", "compensate")
                )
                features["retry_count"] += "retry" in str(tool_name)
        elif event_type in {"tool_result", "tool_rejected"}:
            observation = _canonical(payload.get("observation", {})).decode("utf-8")
            success = bool(payload.get("success"))
            done = bool(payload.get("done"))
            sequence.append(
                f"R|{event_type}|{payload.get('tool_name')}|{success}|{done}|{observation}"
            )
            features["failed_call_count"] += event_type == "tool_result" and not success
            features["rejected_call_count"] += event_type == "tool_rejected"
            if "before_state" in payload and "after_state" in payload:
                before = payload["before_state"]
                after = payload["after_state"]
                if before != after:
                    transitions.append({"before": before, "after": after})
        elif event_type == "run_finished":
            sequence.append(f"T|{payload.get('status')}")
    features["state_transition_count"] = float(len(transitions))
    final_state = (final_observation or {}).get("state", {})
    features["completed"] = float(
        status == "COMPLETED" or final_state.get("completed") is True
    )
    features["runtime_abort"] = float(status == "MAX_STEPS")
    canonical = {
        "sequence": sequence,
        "features": features,
        "terminal_status": status,
        "state_transitions": transitions,
    }
    return {**canonical, "canonical_sha256": _hash(canonical)}


def _failure_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {name: 0 for name in FAILURE_NAMES}
    tool_events = recovery_attempts = verification_attempts = successful_tools = 0
    for row in rows:
        status = row.get("agent_status", "UNKNOWN")
        counts["task_incompletion"] += status != "COMPLETED"
        counts["planning_failure"] += status == "PREMATURE_FINISH"
        seen_successful = set()
        for event in row.get("events", []):
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            if event_type not in {"tool_result", "tool_rejected"}:
                continue
            tool_events += 1
            tool_name = str(payload.get("tool_name"))
            success = bool(payload.get("success"))
            observation = payload.get("observation", {})
            nested = observation.get("tool_result", {})
            error = str(
                observation.get(
                    "error", nested.get("error", "") if isinstance(nested, dict) else ""
                )
            )
            counts["tool_call_failure"] += error in {
                "TOOL_SCHEMA_REJECTED",
                "UNKNOWN_OR_UNAVAILABLE_TOOL",
            }
            counts["dependency_failure"] += any(
                marker in error
                for marker in (
                    "DEPENDENCY",
                    "COMPENSATION_REQUIRED",
                    "PRIMARY_RECOVERY_REQUIRED",
                )
            )
            is_recovery = any(
                marker in tool_name for marker in ("retry", "recover", "compensate")
            )
            is_verification = "verify" in tool_name
            recovery_attempts += is_recovery
            verification_attempts += is_verification
            counts["recovery_failure"] += is_recovery and not success
            counts["verification_failure"] += is_verification and not success
            if event_type == "tool_result" and success:
                successful_tools += 1
                if tool_name in seen_successful:
                    counts["unnecessary_tool_call"] += 1
                seen_successful.add(tool_name)
    denominators = {
        "episode_count": len(rows),
        "tool_event_count": tool_events,
        "recovery_attempt_count": recovery_attempts,
        "verification_attempt_count": verification_attempts,
        "successful_tool_call_count": successful_tools,
    }
    rates = {
        "planning_failure": counts["planning_failure"] / len(rows) if rows else 0.0,
        "tool_call_failure": counts["tool_call_failure"] / tool_events
        if tool_events
        else 0.0,
        "dependency_failure": counts["dependency_failure"] / tool_events
        if tool_events
        else 0.0,
        "recovery_failure": counts["recovery_failure"] / recovery_attempts
        if recovery_attempts
        else 0.0,
        "verification_failure": counts["verification_failure"] / verification_attempts
        if verification_attempts
        else 0.0,
        "task_incompletion": counts["task_incompletion"] / len(rows) if rows else 0.0,
        "unnecessary_tool_call": counts["unnecessary_tool_call"] / successful_tools
        if successful_tools
        else 0.0,
    }
    return {"counts": counts, "denominators": denominators, "rates": rates}


def _sent(record: dict[str, Any]) -> bool:
    return record.get("transport_sent") is not False


def _audit_request(
    record: dict[str, Any],
    row: dict[str, Any],
    attempt: int,
    lock: dict[str, Any],
    plan: dict[str, Any],
) -> None:
    _require(record["attempt"] == attempt, "request attempt ordinal")
    _require(record["status"] in {"SUCCESS", "ERROR"}, "pending request record")
    _require(record["backend"] == lock["backend"], "mixed API backend")
    _require(record["model"] == lock["model"], "request model mismatch")
    _require(
        record["response_model"] in {None, lock["model"]}, "response model mismatch"
    )
    _require(len(record["prompt_sha256"]) == 64, "missing prompt hash")
    if not _sent(record):
        _require(record["reservation_status"] == "DENIED", "unsent reservation state")
        _require(record["cost_usd"] == 0.0, "unsent request actual cost")
        _require(record["cost_upper_usd"] == 0.0, "unsent request upper cost")
        return
    expected_pool = (
        "search"
        if row["phase"] == "search"
        else ("B1" if row["arm"] == "B1" else f"final:{row['arm']}")
    )
    _require(record["budget_pool"] == expected_pool, "request budget pool")
    _require(record["reservation_status"] == "SETTLED", "unsettled sent request")
    _require(record["budget_request_id"], "missing budget request ID")
    reserved = record["reserved_cost_upper_usd"]
    _require(
        isinstance(reserved, (int, float)) and math.isfinite(reserved) and reserved >= 0,
        "invalid reserved cost",
    )
    input_tokens = record["input_tokens"]
    output_tokens = record["output_tokens"]
    known = type(input_tokens) is int and type(output_tokens) is int
    actual = (
        (
            input_tokens * plan["input_price_per_1m_usd"]
            + output_tokens * plan["output_price_per_1m_usd"]
        )
        / 1_000_000.0
        if known
        else None
    )
    upper = actual if actual is not None else reserved
    _require(_same(record["cost_usd"], actual), "provider token pricing")
    _require(_same(record["settled_cost_usd"], actual), "actual settlement")
    _require(_same(record["cost_upper_usd"], upper), "request upper-bound accounting")
    _require(_same(record["settled_cost_upper_usd"], upper), "upper-bound settlement")
    exceeded = actual is not None and actual > reserved + 1e-12
    _require(record["reservation_exceeded"] is exceeded, "reservation exceeded flag")
    if record["total_tokens"] is not None and known:
        _require(
            record["total_tokens"] == input_tokens + output_tokens,
            "provider total-token usage",
        )


def _episode_metrics(row: dict[str, Any]) -> dict[str, Any]:
    records = row["request_ledger"]
    sent = [record for record in records if _sent(record)]
    completed = row["final_public_observation"].get("state", {}).get("completed") is True
    constraint = 0
    harm = 0.0
    tool_cost = 0.0
    for event in row["events"]:
        if event["event_type"] == "tool_rejected":
            constraint += 1
        elif event["event_type"] == "tool_result":
            payload = event["payload"]
            constraint += payload["constraint_violation"]
            harm += payload["harm"]
            tool_cost += payload["cost"]
    priced = all(record["cost_usd"] is not None for record in sent)
    priced_upper = all(record["cost_upper_usd"] is not None for record in sent)
    return {
        "task_success": completed,
        "recovery_success": completed,
        "constraint_violation": constraint,
        "harm": harm,
        "tool_cost": tool_cost,
        "input_tokens": sum(record["input_tokens"] or 0 for record in sent),
        "output_tokens": sum(record["output_tokens"] or 0 for record in sent),
        "token_cost_usd": sum(record["cost_usd"] for record in sent) if priced else None,
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in sent),
        "phenotype_hash": _behavior(
            row["events"], row["agent_status"], row["final_public_observation"]
        )["canonical_sha256"],
        "token_cost_upper_usd": sum(record["cost_upper_usd"] for record in sent)
        if priced_upper
        else None,
    }


def _metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    _require(bool(rows), "empty metric group")
    values = [row["_audit_metrics"] for row in rows]
    count = len(values)
    priced = all(value["token_cost_usd"] is not None for value in values)
    upper_values = [value["token_cost_upper_usd"] for value in values]
    priced_upper = all(value is not None for value in upper_values)
    return {
        "task_success_rate": sum(value["task_success"] for value in values) / count,
        "recovery_success_rate": sum(value["recovery_success"] for value in values)
        / count,
        "constraint_violation": sum(value["constraint_violation"] for value in values),
        "harm": sum(value["harm"] for value in values),
        "tool_cost": sum(value["tool_cost"] for value in values),
        "input_tokens": sum(value["input_tokens"] for value in values),
        "output_tokens": sum(value["output_tokens"] for value in values),
        "token_cost_usd": sum(value["token_cost_usd"] for value in values)
        if priced
        else None,
        "latency_seconds": sum(value["latency_seconds"] for value in values) / count,
        "behavior_diversity": len({value["phenotype_hash"] for value in values}) / count,
        "token_cost_upper_usd": sum(upper_values) if priced_upper else None,
    }


def _objectives(metrics: dict[str, Any]) -> list[float]:
    _require(metrics["token_cost_upper_usd"] is not None, "unknown Pareto cost")
    return [
        1.0 - metrics["task_success_rate"],
        1.0 - metrics["recovery_success_rate"],
        float(metrics["constraint_violation"]),
        metrics["harm"],
        metrics["tool_cost"],
        metrics["token_cost_upper_usd"],
        metrics["latency_seconds"],
    ]


def _usage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record for row in rows for record in row["request_ledger"]]
    sent = [record for record in records if _sent(record)]
    priced = all(record["cost_usd"] is not None for record in sent)
    priced_upper = all(record["cost_upper_usd"] is not None for record in sent)
    return {
        "raw_request_records": len(records),
        "real_transport_attempts": len(sent),
        "input_tokens": sum(record["input_tokens"] or 0 for record in sent),
        "output_tokens": sum(record["output_tokens"] or 0 for record in sent),
        "cost_usd": sum(record["cost_usd"] for record in sent) if priced else None,
        "cost_upper_usd": sum(record["cost_upper_usd"] for record in sent)
        if priced_upper
        else None,
        "latency_seconds": sum(record["latency_seconds"] or 0.0 for record in sent),
    }


def _per_seed(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        str(seed): _metrics([row for row in rows if row["seed"] == seed])
        for seed in sorted({row["seed"] for row in rows})
    }


def _candidate_entry(rows: list[dict[str, Any]], arm: str, phase: str) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (row["task_id"], row["seed"]))
    _require(bool(ordered), arm + " empty candidate")
    _require(
        len({row["genome_sha256"] for row in ordered}) == 1,
        arm + " mixed candidate genome",
    )
    genome = ordered[0]["genome"]
    genome_hash = ordered[0]["genome_sha256"]
    metrics = _metrics(ordered)
    events = [event for row in ordered for event in row["events"]]
    behavior = _behavior(events, "MULTI_EPISODE")
    execution_errors = sum(row["execution_error"] for row in ordered)
    candidate = {
        "genome": genome,
        "objectives": _objectives(metrics),
        "constraint_violation": metrics["constraint_violation"],
        "phenotype_hash": behavior["canonical_sha256"],
        "execution_errors": execution_errors,
        "behavior": behavior,
        "failure_profile": _failure_profile(ordered),
    }
    return {
        "arm": arm,
        "phase": phase,
        "genome": genome,
        "genome_sha256": genome_hash,
        "candidate": candidate,
        "metrics": metrics,
        "execution_errors": execution_errors,
        "episode_count": len(ordered),
        "per_seed": _per_seed(ordered),
        "usage": _usage(ordered),
        "hash_chain_valid": all(row["hash_chain_valid"] for row in ordered),
        "episode_ids": [row["episode_id"] for row in ordered],
    }


def _dominates(first: dict[str, Any], second: dict[str, Any]) -> bool:
    left = first["candidate"]["objectives"]
    right = second["candidate"]["objectives"]
    return all(a <= b + 1e-12 for a, b in zip(left, right)) and any(
        a < b - 1e-12 for a, b in zip(left, right)
    )


def _front(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feasible = [
        entry
        for entry in entries
        if entry["candidate"]["constraint_violation"] == 0
        and entry["candidate"]["execution_errors"] == 0
    ]
    selected = [
        entry
        for entry in feasible
        if not any(_dominates(other, entry) for other in feasible if other is not entry)
    ]
    return sorted(selected, key=lambda entry: entry["genome_sha256"])


def _diversity(entries: list[dict[str, Any]]) -> dict[str, Any]:
    genomes = {entry["genome_sha256"] for entry in entries}
    phenotypes = {entry["candidate"]["phenotype_hash"] for entry in entries}
    return {
        "genotype_count": len(entries),
        "unique_genotype_count": len(genomes),
        "phenotype_count": len(entries),
        "unique_phenotype_count": len(phenotypes),
        "genotype_diversity": len(genomes) / len(entries),
        "behavior_diversity": len(phenotypes) / len(genomes),
        "complete_behavior_collapse": len(phenotypes) < 2,
    }


def _delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    return {
        field: second[field] - first[field]
        if first[field] is not None and second[field] is not None
        else None
        for field in DELTA_FIELDS
    }


def _budget(
    rows: list[dict[str, Any]], plan: dict[str, Any], lock: dict[str, Any]
) -> dict[str, Any]:
    records = [record for row in rows for record in row["request_ledger"]]
    sent = [record for record in records if _sent(record)]
    spent_requests: dict[str, int] = defaultdict(int)
    spent_upper: dict[str, float] = defaultdict(float)
    reserved_used: dict[str, float] = defaultdict(float)
    for record in sent:
        pool = record["budget_pool"]
        spent_requests[pool] += 1
        spent_upper[pool] += record["settled_cost_upper_usd"]
        reserved_used[pool] += record["reserved_cost_upper_usd"]
    remaining_pools = {
        pool: reservation["cost_usd"] - reserved_used[pool]
        for pool, reservation in plan["protected_pools"].items()
    }
    remaining_requests = {
        pool: reservation["request_count"] - spent_requests[pool]
        for pool, reservation in plan["protected_pools"].items()
    }
    cost_unknown = any(record["settled_cost_usd"] is None for record in sent)
    actual = sum(record["settled_cost_usd"] or 0.0 for record in sent)
    upper = sum(record["settled_cost_upper_usd"] for record in sent)
    exceeded = any(record["reservation_exceeded"] for record in sent)
    config = lock["config"]
    return {
        "max_cost_usd": config["global_cost_cap"],
        "max_requests": config["global_request_cap"],
        "reserved_cost_usd": sum(remaining_pools.values()),
        "reserved_pools": remaining_pools,
        "reserved_request_count": sum(remaining_requests.values()),
        "reserved_request_pools": remaining_requests,
        "pending_cost_usd": 0,
        "spent_upper_by_pool": dict(spent_upper),
        "spent_requests_by_pool": dict(spent_requests),
        "available_search_cost_usd": config["global_cost_cap"]
        - sum(remaining_pools.values())
        - sum(spent_upper.values()),
        "available_search_requests": config["global_request_cap"]
        - len(sent)
        - sum(remaining_requests.values()),
        "sent_request_count": len(sent),
        "budget_denied_count": sum(
            record.get("reservation_status") == "DENIED" for record in records
        ),
        "cost_usd": actual,
        "cost_complete": not cost_unknown,
        "cost_upper_usd": upper,
        "cost_unknown": cost_unknown,
        "reservation_exceeded": exceeded,
        "over_budget": actual > config["global_cost_cap"]
        or upper > config["global_cost_cap"]
        or len(sent) > config["global_request_cap"]
        or exceeded,
        "backend": lock["backend"],
    }


def audit_r3(outdir: Path) -> dict[str, Any]:
    """Recompute saved evidence without calling an API or rerunning an episode."""
    outdir = Path(outdir)
    summary = _load(outdir / "summary.json")
    lock = _load(outdir / "execution_lock.json")
    plan = _load(outdir / "budget_plan.json")
    manifest = _load(outdir / "train_manifest.json")
    _require(summary["status"] == "COMPLETED", "only completed runs are auditable")
    _require(lock["model"] == summary["model"], "locked model")
    _require(lock["backend"] == summary["backend"], "locked backend")
    if lock["backend"] == "openai-compatible":
        _require(lock["model"] == "deepseek-flash", "real model requirement")
    _require(lock["config"] == summary["config"], "execution config")
    _require(lock["temperature"] == 0.0, "temperature")
    _require(lock["thinking"] == {"type": "disabled"}, "thinking configuration")
    _require(
        summary["execution_lock_sha256"]
        == hashlib.sha256((outdir / "execution_lock.json").read_bytes()).hexdigest(),
        "execution lock SHA-256",
    )
    _require(
        lock["budget_plan_sha256"]
        == summary["budget_plan_sha256"]
        == hashlib.sha256((outdir / "budget_plan.json").read_bytes()).hexdigest(),
        "budget plan SHA-256",
    )
    internal_manifest = dict(manifest)
    manifest_hash = internal_manifest.pop("manifest_sha256")
    _require(
        _hash(internal_manifest) == manifest_hash == lock["train_manifest_sha256"],
        "Train manifest identity",
    )
    _require(
        not manifest["validation_included"] and not manifest["test_included"],
        "held-out data included",
    )
    for name, expected in lock["source_files"].items():
        actual = hashlib.sha256((Path(__file__).resolve().parent / name).read_bytes()).hexdigest()
        _require(actual == expected, "source lock: " + name)

    rows = [
        json.loads(line)
        for line in (outdir / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    _require(len(rows) == summary["actual_episode_count"], "actual episode count")
    _require(len(rows) == summary["planned_episode_count"], "planned episode count")
    _require(len(rows) == plan["planned_episode_count"], "budget episode design")
    train_ids = {task["task_id"] for task in manifest["tasks"]}
    _require(
        train_ids == set(lock["config"]["task_ids"]), "locked Train task subset"
    )
    seen_episodes = set()
    seen_budget_ids = set()
    provider_ids = set()
    budget_ordinals = set()
    for row in rows:
        identity = {
            "arm": row["arm"],
            "phase": row["phase"],
            "task_id": row["task_id"],
            "seed": row["seed"],
            "genome_sha256": row["genome_sha256"],
        }
        _require(row["episode_id"] == _hash(identity), "episode identity")
        _require(row["episode_id"] not in seen_episodes, "duplicate episode")
        seen_episodes.add(row["episode_id"])
        _require(row["task_id"] in train_ids, "non-Train episode")
        _require(row["genome_sha256"] == _hash(row["genome"]), "genome identity")
        trace_path = Path(row["trace_path"])
        _require(not trace_path.is_absolute() and ".." not in trace_path.parts, "trace path")
        trace_bytes = (outdir / trace_path).read_bytes()
        _require(
            row["trace_sha256"] == hashlib.sha256(trace_bytes).hexdigest(),
            "trace SHA-256",
        )
        trace_events = [json.loads(line) for line in trace_bytes.splitlines()]
        chain_valid = _verify_chain(trace_events)
        _require(chain_valid and row["hash_chain_valid"], "episode hash chain")
        projection = [
            {"event_type": event["event_type"], "payload": event["payload"]}
            for event in trace_events
        ]
        _require(projection == row["events"], "episode/trace event mismatch")
        finished = [event for event in row["events"] if event["event_type"] == "run_finished"]
        _require(
            len(finished) == 1
            and finished[0]["payload"]["status"] == row["agent_status"],
            "terminal status",
        )
        for attempt, record in enumerate(row["request_ledger"]):
            _audit_request(record, row, attempt, lock, plan)
            budget_id = record["budget_request_id"]
            if budget_id is not None:
                _require(budget_id not in seen_budget_ids, "duplicate budget request ID")
                seen_budget_ids.add(budget_id)
                ordinal = int(budget_id.rsplit(":", 1)[1])
                _require(ordinal not in budget_ordinals, "duplicate budget ordinal")
                budget_ordinals.add(ordinal)
            if (
                lock["backend"] == "openai-compatible"
                and record["request_id"] is not None
                and _sent(record)
            ):
                _require(record["request_id"] not in provider_ids, "provider request ID")
                provider_ids.add(record["request_id"])
        sent_count = sum(_sent(record) for record in row["request_ledger"])
        _require(row["api_attempt_count"] == sent_count, "episode API attempt count")
        expected_error = (
            row["agent_status"] in {"LLM_ERROR", "RULE_ERROR"}
            or sent_count == 0
            or not chain_valid
        )
        _require(row["execution_error"] is expected_error, "execution error flag")
        row["_audit_metrics"] = _episode_metrics(row)
        _require(_same(row["metrics"], row["_audit_metrics"]), "raw episode metrics")
    _require(
        budget_ordinals == set(range(len(budget_ordinals))), "budget ordinal sequence"
    )
    _require(summary["hash_chain_valid"], "summary hash-chain gate")

    by_id = {row["episode_id"]: row for row in rows}
    b1_rows = [row for row in rows if row["arm"] == "B1" and row["phase"] == "fixed"]
    b1 = _candidate_entry(b1_rows, "B1", "fixed")
    _require(_same(summary["arms"]["B1"], b1), "B1 full candidate entry")

    recomputed_arms = {"B1": b1}
    final_metrics = {"B1": b1["metrics"]}
    final_per_seed = {"B1": b1["per_seed"]}
    for arm in EVOLUTION_ARMS:
        archive = _load(outdir / f"archive_{arm}.json")
        evolution = _load(outdir / f"evolution_{arm}.json")
        expected_archive = []
        for entry in archive:
            entry_rows = [by_id[episode_id] for episode_id in entry["episode_ids"]]
            expected = _candidate_entry(entry_rows, arm, "search")
            _require(_same(entry, expected), arm + " archive candidate")
            expected_archive.append(expected)
        _require(
            len({entry["genome_sha256"] for entry in expected_archive})
            == len(expected_archive),
            arm + " duplicate archive genome",
        )
        front = _front(expected_archive)
        _require(bool(front), arm + " empty feasible Pareto front")
        selected = min(
            front, key=lambda entry: (entry["candidate"]["objectives"], entry["genome_sha256"])
        )
        search_rows = [row for row in rows if row["arm"] == arm and row["phase"] == "search"]
        final_rows = [row for row in rows if row["arm"] == arm and row["phase"] == "final"]
        _require(final_rows, arm + " missing final episodes")
        _require(
            {row["genome_sha256"] for row in final_rows} == {selected["genome_sha256"]},
            arm + " final selection",
        )
        final_entry = _candidate_entry(final_rows, arm, "final")
        combined = search_rows + final_rows
        entry = summary["arms"][arm]
        _require(entry["selected_genome_sha256"] == selected["genome_sha256"], arm + " selected hash")
        _require(entry["search_episode_count"] == len(search_rows), arm + " search count")
        _require(
            entry["final_episode_count"]
            == len(final_rows)
            == len(train_ids) * len(lock["config"]["seeds"]),
            arm + " final count",
        )
        _require(
            entry["execution_errors"] == sum(row["execution_error"] for row in combined) == 0,
            arm + " execution errors",
        )
        _require(
            entry["hash_chain_valid"] == all(row["hash_chain_valid"] for row in combined),
            arm + " hash chain",
        )
        _require(_same(entry["metrics"], final_entry["metrics"]), arm + " final metrics")
        _require(_same(entry["per_seed"], final_entry["per_seed"]), arm + " final per-seed")
        _require(_same(entry["usage"], _usage(combined)), arm + " total usage")
        _require(entry["search_unique_genomes"] == len(expected_archive), arm + " search genomes")
        _require(
            entry["pareto_front"] == [item["genome_sha256"] for item in front],
            arm + " Pareto front",
        )
        _require(_same(entry["population_diversity"], _diversity(expected_archive)), arm + " diversity")
        _require(
            entry["variation_count"]
            == sum(event["event_type"] == "variation" for event in evolution),
            arm + " variation count",
        )
        _require(
            entry["duplicate_proposal_count"]
            == sum(event["event_type"] == "duplicate_proposal" for event in evolution),
            arm + " duplicate count",
        )
        evaluations = [event for event in evolution if event["event_type"] == "evaluation"]
        _require(len(evaluations) == len(expected_archive), arm + " evaluation count")
        for event in evaluations:
            candidate = next(
                item for item in expected_archive if item["genome_sha256"] == event["genome_hash"]
            )
            _require(_same(event["objectives"], candidate["candidate"]["objectives"]), arm + " evaluation objectives")
            _require(event["phenotype_hash"] == candidate["candidate"]["phenotype_hash"], arm + " evaluation phenotype")
        final_metrics[arm] = final_entry["metrics"]
        final_per_seed[arm] = final_entry["per_seed"]
        recomputed_arms[arm] = {
            **entry,
            "metrics": final_entry["metrics"],
            "per_seed": final_entry["per_seed"],
            "usage": _usage(combined),
            "population_diversity": _diversity(expected_archive),
            "final_usage": final_entry["usage"],
            "final_phenotype_hash": final_entry["candidate"]["phenotype_hash"],
        }

    comparisons = {}
    per_seed_comparisons = {}
    for label, first, second in (
        ("B3_minus_B2", "B2", "B3"),
        ("B4_minus_B2", "B2", "B4"),
        ("B5_minus_B3", "B3", "B5"),
        ("B5_minus_B4", "B4", "B5"),
    ):
        comparisons[label] = _delta(final_metrics[first], final_metrics[second])
        per_seed_comparisons[label] = {
            seed: _delta(final_per_seed[first][seed], final_per_seed[second][seed])
            for seed in final_per_seed[first]
        }
    _require(_same(summary["comparisons"], comparisons), "overall comparisons")
    _require(
        _same(summary["per_seed_comparisons"], per_seed_comparisons),
        "per-seed comparisons",
    )
    _require(_same(summary["per_seed"], final_per_seed), "summary per-seed metrics")
    expected_budget = _budget(rows, plan, lock)
    _require(_same(summary["budget"], expected_budget), "global budget reconciliation")
    _require(not expected_budget["over_budget"], "over-budget completed run")
    _require(expected_budget["cost_complete"], "incomplete cost accounting")

    artifact_hashes = {}
    for path in sorted(outdir.rglob("*")):
        if path.is_file() and path.name != "independent_audit.json":
            artifact_hashes[str(path.relative_to(outdir))] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    result = {
        "audit_schema": "d094_r3_independent_audit_v1",
        "status": "PASS",
        "summary_status": summary["status"],
        "summary_matches_raw": True,
        "episode_count": len(rows),
        "arms": recomputed_arms,
        "comparisons": comparisons,
        "per_seed_comparisons": per_seed_comparisons,
        "budget": expected_budget,
        "input_tokens": expected_budget and sum(
            row["_audit_metrics"]["input_tokens"] for row in rows
        ),
        "output_tokens": sum(row["_audit_metrics"]["output_tokens"] for row in rows),
        "unique_provider_request_ids": len(provider_ids),
        "episodes_sha256": hashlib.sha256((outdir / "episodes.jsonl").read_bytes()).hexdigest(),
        "artifact_sha256": artifact_hashes,
        "scientific_scope": "Independent consistency recomputation only; not confirmatory statistical evidence",
    }
    (outdir / "independent_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("outdir", type=Path)
    args = parser.parse_args()
    result = audit_r3(args.outdir)
    print(
        json.dumps(
            {
                "status": result["status"],
                "episodes": result["episode_count"],
                "requests": result["budget"]["sent_request_count"],
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "cost_usd": result["budget"]["cost_usd"],
            }
        )
    )
