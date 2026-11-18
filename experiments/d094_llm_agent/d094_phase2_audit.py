"""Independent recomputation of D-094 Phase 2 summaries from raw episodes."""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


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
    return first == second


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("D-094 Phase 2 audit failed: " + message)


def _metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    values = [row["metrics"] for row in rows]
    count = len(values)
    priced = all(value["token_cost_usd"] is not None for value in values)
    upper_values = [
        value.get("token_cost_upper_usd", value["token_cost_usd"]) for value in values
    ]
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
        "behavior_diversity": len({value["phenotype_hash"] for value in values})
        / count,
        "token_cost_upper_usd": sum(upper_values) if priced_upper else None,
    }


def _objectives(metrics: dict[str, Any]) -> list[float]:
    return [
        1.0 - metrics["task_success_rate"],
        1.0 - metrics["recovery_success_rate"],
        float(metrics["constraint_violation"]),
        metrics["harm"],
        metrics["tool_cost"],
        metrics["token_cost_upper_usd"],
        metrics["latency_seconds"],
    ]


def _behavior_hash(events: list[dict[str, Any]]) -> str:
    projected = []
    for event in events:
        if event["event_type"] == "decision":
            payload = event["payload"]
            projected.append(
                {
                    "event_type": "decision",
                    "action": payload["action"],
                    "tool_name": payload["tool_name"],
                    "tool_arguments": payload["tool_arguments"],
                }
            )
        elif event["event_type"] in {"tool_result", "tool_rejected"}:
            payload = event["payload"]
            projected.append(
                {
                    "event_type": event["event_type"],
                    "tool_name": payload.get("tool_name"),
                    "observation": payload.get("observation"),
                    "success": payload.get("success"),
                }
            )
    return _hash(projected)


def _candidate(genome_hash: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: (row["task_id"], row["seed"]))
    metrics = _metrics(ordered)
    return {
        "genome": ordered[0]["genome"],
        "genome_sha256": genome_hash,
        "candidate": {
            "genome": ordered[0]["genome"],
            "objectives": _objectives(metrics),
            "constraint_violation": metrics["constraint_violation"],
            "phenotype_hash": _hash(
                [row["metrics"]["phenotype_hash"] for row in ordered]
            ),
            "execution_errors": sum(row["execution_error"] for row in ordered),
        },
        "metrics": metrics,
        "rows": ordered,
    }


def _dominates(first: dict[str, Any], second: dict[str, Any]) -> bool:
    left = first["candidate"]["objectives"]
    right = second["candidate"]["objectives"]
    return all(a <= b + 1e-12 for a, b in zip(left, right)) and any(
        a < b - 1e-12 for a, b in zip(left, right)
    )


def _front(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feasible = [
        candidate
        for candidate in candidates
        if candidate["candidate"]["constraint_violation"] == 0
        and candidate["candidate"]["execution_errors"] == 0
    ]
    selected = [
        candidate
        for candidate in feasible
        if not any(
            _dominates(other, candidate) for other in feasible if other is not candidate
        )
    ]
    return sorted(selected, key=lambda candidate: candidate["genome_sha256"])


def _gene_analysis(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    genes = tuple(candidates[0]["genome"])
    result = {}
    for gene in genes:
        pairs = []
        for index, first in enumerate(candidates):
            for second in candidates[index + 1 :]:
                if [
                    name
                    for name in genes
                    if first["genome"][name] != second["genome"][name]
                ] != [gene]:
                    continue
                pairs.append(
                    (
                        first["candidate"]["phenotype_hash"]
                        != second["candidate"]["phenotype_hash"],
                        second["metrics"]["task_success_rate"]
                        - first["metrics"]["task_success_rate"],
                        second["metrics"]["token_cost_upper_usd"]
                        - first["metrics"]["token_cost_upper_usd"],
                    )
                )
        result[gene] = {
            "single_gene_pair_count": len(pairs),
            "behavior_changed_count": sum(pair[0] for pair in pairs),
            "behavior_changed_fraction": sum(pair[0] for pair in pairs) / len(pairs)
            if pairs
            else None,
            "mean_absolute_success_delta": sum(abs(pair[1]) for pair in pairs)
            / len(pairs)
            if pairs
            else None,
            "mean_absolute_token_cost_delta": sum(abs(pair[2]) for pair in pairs)
            / len(pairs)
            if pairs
            else None,
        }
    return result


def hard_constraint_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    """Map only explicit public D-094 event markers into six audit categories."""
    invalid = {"TOOL_SCHEMA_REJECTED", "UNKNOWN_OR_UNAVAILABLE_TOOL"}
    unauthorized = {
        "ENVIRONMENT_PERMISSION_DENIED",
        "VERIFICATION_REQUIRED",
        "COMPENSATION_REQUIRED",
        "PRIMARY_RECOVERY_REQUIRED",
        "RECOVERY_VERIFICATION_REQUIRED",
        "RECOVERY_COMPENSATION_REQUIRED",
        "DEPENDENCY_VERIFICATION_REQUIRED",
    }
    counts = {
        "invalid_action_count": 0,
        "unauthorized_action_count": 0,
        "illegal_transition_count": 0,
        "pending_count": 0,
        "duplicate_count": 0,
        "runtime_abort_count": 0,
    }
    for row in rows:
        for event in row["events"]:
            observation = event["payload"].get("observation", {})
            markers = {str(value) for value in observation.values()}
            code = observation.get("error")
            counts["invalid_action_count"] += code in invalid
            counts["unauthorized_action_count"] += code in unauthorized
            counts["illegal_transition_count"] += code == "TASK_ALREADY_COMPLETED"
            counts["pending_count"] += "PENDING" in markers
            counts["duplicate_count"] += "DUPLICATE_COMPENSATION" in markers
        counts["runtime_abort_count"] += row["agent_status"] == "MAX_STEPS"
    return counts


def reconcile_budget_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Separate budget-denied ledger entries from requests actually sent."""
    denied = [
        record
        for record in records
        if record.get("error_type") in {"LLMBudgetExceeded", "LLMCostLimitExceeded"}
        and record.get("request_id") is None
        and record.get("response_model") is None
        and record.get("input_tokens") is None
        and record.get("output_tokens") is None
    ]
    sent = [record for record in records if record not in denied]
    priced = all(record["cost_usd"] is not None for record in sent)
    priced_upper = all(record.get("cost_upper_usd") is not None for record in sent)
    return {
        "request_count": len(sent),
        "budget_denied_count": len(denied),
        "input_tokens": sum(record["input_tokens"] or 0 for record in sent),
        "output_tokens": sum(record["output_tokens"] or 0 for record in sent),
        "cost_usd": sum(record["cost_usd"] for record in sent) if priced else None,
        "cost_upper_usd": sum(record["cost_upper_usd"] for record in sent)
        if priced_upper
        else None,
    }


def audit_phase2(outdir: Path) -> dict[str, Any]:
    """Audit saved evidence without calling an API or rerunning any episode."""
    outdir = Path(outdir)
    summary = json.loads((outdir / "summary.json").read_text(encoding="utf-8"))
    lock = json.loads((outdir / "execution_lock.json").read_text(encoding="utf-8"))
    manifest = json.loads((outdir / "train_manifest.json").read_text(encoding="utf-8"))
    evolution = json.loads(
        (outdir / "evolution_ledger.json").read_text(encoding="utf-8")
    )
    rows = [
        json.loads(line)
        for line in (outdir / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    _require(bool(rows), "empty episode ledger")
    internal = dict(manifest)
    manifest_hash = internal.pop("manifest_sha256")
    _require(
        _hash(internal) == manifest_hash == lock["train_manifest_sha256"],
        "Train manifest identity",
    )
    _require(
        not manifest["validation_included"] and not manifest["test_included"],
        "held-out data included",
    )
    train_ids = {task["task_id"] for task in manifest["tasks"]}
    _require(len(train_ids) == 12, "Train task count")
    lock_raw = (outdir / "execution_lock.json").read_bytes()
    lock_raw_sha = hashlib.sha256(lock_raw).hexdigest()
    lock_canonical_sha = hashlib.sha256(b"\n".join(lock_raw.splitlines())).hexdigest()
    lock_crlf_sha = hashlib.sha256(
        lock_raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    ).hexdigest()
    _require(
        summary["execution_lock_sha256"]
        in {lock_raw_sha, lock_canonical_sha, lock_crlf_sha},
        "execution lock hash",
    )
    execution_lock_canonical_match = (
        summary["execution_lock_sha256"] == lock_canonical_sha
    )
    execution_lock_crlf_match = summary["execution_lock_sha256"] == lock_crlf_sha
    seen = set()
    all_records = []
    request_identities = set()
    response_request_ids = set()
    hash_chain_present = True
    for row in rows:
        identity = {
            "arm": row["arm"],
            "phase": row["phase"],
            "task_id": row["task_id"],
            "seed": row["seed"],
            "genome_sha256": row["genome_sha256"],
        }
        _require(row["episode_id"] == _hash(identity), "episode identity")
        key = tuple(identity.values())
        _require(key not in seen, "duplicate episode")
        seen.add(key)
        _require(row["task_id"] in train_ids, "non-Train episode")
        metrics = row["metrics"]
        _require(
            metrics["phenotype_hash"] == _behavior_hash(row["events"]), "phenotype hash"
        )
        records = row["request_ledger"]
        all_records.extend(records)
        hash_chain_present = hash_chain_present and all(
            "sequence" in event and "event_sha256" in event for event in row["events"]
        )
        for attempt, record in enumerate(records):
            _require(record["attempt"] == attempt, "request attempt ordinal")
            _require(record["backend"] == lock["backend"], "mixed API backend")
            _require(record["model"] == lock["model"], "request model mismatch")
            _require(
                record["response_model"] in {None, lock["model"]},
                "response model mismatch",
            )
            _require(len(record["prompt_sha256"]) == 64, "missing prompt hash")
            composite = (row["episode_id"], attempt)
            _require(composite not in request_identities, "duplicate request identity")
            request_identities.add(composite)
            if record["request_id"] is not None:
                if lock["backend"] == "openai-compatible":
                    _require(
                        record["request_id"] not in response_request_ids,
                        "duplicate provider request ID",
                    )
                response_request_ids.add(record["request_id"])
        _require(
            metrics["input_tokens"]
            == sum(record["input_tokens"] or 0 for record in records),
            "input-token ledger",
        )
        _require(
            metrics["output_tokens"]
            == sum(record["output_tokens"] or 0 for record in records),
            "output-token ledger",
        )
        expected_cost = (
            sum(record["cost_usd"] for record in records)
            if all(record["cost_usd"] is not None for record in records)
            else None
        )
        _require(_same(metrics["token_cost_usd"], expected_cost), "episode cost ledger")
        _require(
            _same(
                metrics["latency_seconds"],
                sum(record["latency_seconds"] or 0.0 for record in records),
            ),
            "episode latency",
        )
    _require(summary["actual_episode_count"] == len(rows), "summary episode count")
    if summary["status"] == "COMPLETED":
        _require(len(rows) == lock["planned_episode_count"], "planned episode count")

    for arm, entry in summary["arms"].items():
        selected = [
            row for row in rows if row["arm"] == arm and row["phase"] == entry["phase"]
        ]
        _require(len(selected) == entry["episode_count"], arm + " episode count")
        _require(_same(_metrics(selected), entry["metrics"]), arm + " metrics")
        for seed, expected in entry["per_seed"].items():
            seed_rows = [row for row in selected if str(row["seed"]) == seed]
            _require(_same(_metrics(seed_rows), expected), arm + " seed " + seed)

    search_rows = [row for row in rows if row["phase"] == "search"]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in search_rows:
        grouped[row["genome_sha256"]].append(row)
    candidates = [
        _candidate(genome_hash, group) for genome_hash, group in grouped.items()
    ]
    evaluation_events = [
        event for event in evolution if event["event_type"] == "evaluation"
    ]
    _require(
        len({event["genome_hash"] for event in evaluation_events})
        == len(evaluation_events),
        "cross-generation duplicate evaluation",
    )
    _require(len(evaluation_events) == len(candidates), "search evaluation count")
    by_hash = {candidate["genome_sha256"]: candidate for candidate in candidates}
    for event in evaluation_events:
        candidate = by_hash[event["genome_hash"]]
        _require(
            _same(candidate["candidate"]["objectives"], event["objectives"]),
            "search objectives",
        )
        _require(
            candidate["candidate"]["constraint_violation"]
            == event["constraint_violation"],
            "search hard constraints",
        )
        _require(
            candidate["candidate"]["phenotype_hash"] == event["phenotype_hash"],
            "search phenotype",
        )
    front = _front(candidates)
    front_ids = [candidate["genome_sha256"] for candidate in front]
    _require(summary["search"]["feasible_pareto_front"] == front_ids, "Pareto front")
    if front:
        selected = min(
            front,
            key=lambda candidate: (
                candidate["candidate"]["objectives"],
                candidate["genome_sha256"],
            ),
        )
        _require(
            summary["search"]["selected_genome_sha256"] == selected["genome_sha256"],
            "final selection",
        )
    _require(
        summary["search"]["unique_evaluated_genomes"] == len(candidates),
        "unique search genomes",
    )
    unique_genomes = len({candidate["genome_sha256"] for candidate in candidates})
    unique_phenotypes = len(
        {candidate["candidate"]["phenotype_hash"] for candidate in candidates}
    )
    diversity = {
        "genotype_count": len(candidates),
        "unique_genotype_count": unique_genomes,
        "phenotype_count": len(candidates),
        "unique_phenotype_count": unique_phenotypes,
        "genotype_diversity": unique_genomes / len(candidates),
        "behavior_diversity": unique_phenotypes / unique_genomes,
        "complete_behavior_collapse": unique_phenotypes < 2,
    }
    _require(
        _same(summary["search"]["population_diversity"], diversity),
        "population diversity",
    )
    _require(
        _same(summary["search"]["gene_effects"], _gene_analysis(candidates)),
        "gene effects",
    )
    groups = defaultdict(list)
    for candidate in candidates:
        groups[candidate["candidate"]["phenotype_hash"]].append(
            candidate["genome_sha256"]
        )
    identical = [sorted(group) for group in groups.values() if len(group) > 1]
    _require(
        summary["search"]["identical_behavior_groups"] == identical,
        "identical behavior groups",
    )

    for key, expected in summary["usage_by_arm_phase"].items():
        arm, phase = key.split("/", 1)
        selected_records = [
            record
            for row in rows
            if row["arm"] == arm and row["phase"] == phase
            for record in row["request_ledger"]
        ]
        priced = all(record["cost_usd"] is not None for record in selected_records)
        priced_upper = all(
            record.get("cost_upper_usd") is not None for record in selected_records
        )
        actual = {
            "api_attempts": len(selected_records),
            "input_tokens": sum(
                record["input_tokens"] or 0 for record in selected_records
            ),
            "output_tokens": sum(
                record["output_tokens"] or 0 for record in selected_records
            ),
            "cost_usd": sum(record["cost_usd"] for record in selected_records)
            if priced
            else None,
            "cost_upper_usd": sum(
                record["cost_upper_usd"] for record in selected_records
            )
            if priced_upper
            else None,
            "latency_seconds": sum(
                record["latency_seconds"] or 0.0 for record in selected_records
            ),
        }
        _require(_same(actual, expected), key + " usage")
    budget = summary["budget"]
    expected_budget = reconcile_budget_records(all_records)
    _require(
        all(
            _same(budget[key], value)
            for key, value in expected_budget.items()
            if key != "budget_denied_count"
        ),
        "global budget",
    )
    _require(budget["request_count"] <= budget["max_requests"], "request cap exceeded")
    _require(
        summary["evolution_event_count"] == len(evolution), "evolution event count"
    )
    result = {
        "audit_schema": "d094_phase2_independent_audit_v1",
        "status": "PASS" if hash_chain_present else "PASS_WITH_LIMITATIONS",
        "event_hash_chain": "VERIFIED_PRESENT"
        if hash_chain_present
        else "NOT_PROVIDED_BY_RUNNER",
        "summary_status": summary["status"],
        "summary_matches_raw": True,
        "execution_lock_canonical_match": execution_lock_canonical_match,
        "execution_lock_crlf_match": execution_lock_crlf_match,
        "episode_count": len(rows),
        "unique_search_genomes": len(candidates),
        "request_count": expected_budget["request_count"],
        "raw_request_records": len(all_records),
        "budget_denied_count": expected_budget["budget_denied_count"],
        "unique_request_identities": len(request_identities),
        "unique_provider_request_ids": len(response_request_ids),
        "hard_constraints": hard_constraint_counts(rows),
        "input_tokens": expected_budget["input_tokens"],
        "output_tokens": expected_budget["output_tokens"],
        "cost_usd": expected_budget["cost_usd"],
        "cost_upper_usd": expected_budget["cost_upper_usd"],
        "selected_genome_sha256": summary["search"]["selected_genome_sha256"],
        "episodes_sha256": hashlib.sha256(
            (outdir / "episodes.jsonl").read_bytes()
        ).hexdigest(),
        "scientific_scope": "Audit consistency only; not algorithm performance or confirmatory statistical evidence",
    }
    (outdir / "independent_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit_phase2(args.outdir)))
