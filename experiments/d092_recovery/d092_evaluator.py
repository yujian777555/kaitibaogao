"""D-092 aggregate evaluator, phenotype hashes and explicit Train authorization."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from d092_feedback import MARGINAL_NAMES
from d092_genome import TypedGenome, canonical_json_bytes, genome_sha256, sha256_hex

HARD_FIELDS = (
    "invalid_action_count",
    "unauthorized_action_count",
    "illegal_state_transition_count",
    "pending_count",
    "duplicate_count",
    "runtime_abort_count",
)
FITNESS_FIELDS = ("R3", "R4", "CondRec", "Harm", "RecoveryCost")
VIEW_FIELDS = {
    "genome_sha256", "fitness", "hard_constraints", "constraint_episode_count",
    "contract_blocked_attempts", "dependency_blocked_attempts",
    "feedback_marginals", "phenotype_hashes",
}
FORBIDDEN_OPTIMIZER_FIELDS = {
    "scenario_id", "label", "episode_reference", "class_success",
    "conditional_recovery_success", "correct_escalation", "min_reachable_harm",
    "avoidable_harm", "evaluator_internal_rows", "hash_to_record", "audit_only_view",
}
DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "d090_recovery" / "results" / "d090_train_manifest.json"
EXPECTED_MANIFEST_CANONICAL = "be64100e49191d42174db0cacb0d26c58302fe009933849c3e2406e7220ee4c3"
EXPECTED_MANIFEST_INTERNAL = "7d677fe075a5bac6b4241be6c4f38e0c55022b6059729e9a05c7cdf7d633350d"


def _mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("empty metric denominator")
    return sum(values) / len(values)


def _family_metric(rows: Sequence[Dict[str, Any]], field: str, selector) -> float:
    families = sorted({row.get("task_family_id", "synthetic") for row in rows})
    family_values = []
    for family in families:
        selected = [row for row in rows if row.get("task_family_id", "synthetic") == family]
        values = [selector(row) for row in selected]
        values = [value for value in values if value is not None]
        if values:
            family_values.append(_mean(values))
    return _mean(family_values) if family_values else 0.0


def _fitness(rows: Sequence[Dict[str, Any]]) -> Dict[str, float]:
    return {
        "R3": _family_metric(rows, "R3", lambda row: row["correct_escalation"] if row["label"] == "R3" else None),
        "R4": _family_metric(rows, "R4", lambda row: row["class_success"] if row["label"] == "R4" else None),
        "CondRec": _family_metric(rows, "CondRec", lambda row: row["conditional_recovery_success"] if row["label"] in ("R1", "R2") else None),
        "Harm": _family_metric(rows, "Harm", lambda row: row["avoidable_harm"]),
        "RecoveryCost": _family_metric(rows, "RecoveryCost", lambda row: row["recovery_cost"]),
    }


def _phenotypes(rows: Sequence[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], Dict[str, str]]:
    ordered = sorted(rows, key=lambda row: row["scenario_id"])
    trace_bundle = []
    outcome_bundle = []
    outcome_fields = (
        "scenario_id", "class_success", "task_success", "conditional_recovery_success",
        "correct_escalation", "residual_side_effects", "min_reachable_harm", "avoidable_harm",
        "action_cost", "recovery_cost", "decision_count", "constraint_episode",
        *HARD_FIELDS, "policy_selected_escalation", "runtime_forced_abort", "final_tool_states",
    )
    for row in ordered:
        events = [
            {
                "action": list(event["action"]),
                "observation": event["observation"],
                "cost": event["cost"],
                "tick": event["tick"],
            }
            for event in row["trace"]
        ]
        trace_bundle.append({"scenario_id": row["scenario_id"], "events": events})
        outcome_bundle.append({field: row.get(field) for field in outcome_fields})
    hashes = {
        "trace": sha256_hex(trace_bundle),
        "outcome": sha256_hex(outcome_bundle),
    }
    hashes["joint"] = sha256_hex({
        "outcome_signature_sha256": hashes["outcome"],
        "trace_phenotype_sha256": hashes["trace"],
    })
    return trace_bundle, outcome_bundle, hashes


def assert_optimizer_view(view: Dict[str, Any]) -> None:
    if set(view) != VIEW_FIELDS:
        raise ValueError("optimizer view schema mismatch")
    if set(view["fitness"]) != set(FITNESS_FIELDS):
        raise ValueError("optimizer fitness schema mismatch")
    if set(view["hard_constraints"]) != set(HARD_FIELDS):
        raise ValueError("optimizer hard-constraint schema mismatch")
    if set(view["feedback_marginals"]) != set(MARGINAL_NAMES):
        raise ValueError("optimizer feedback schema mismatch")
    if set(view["phenotype_hashes"]) != {"trace", "outcome", "joint"}:
        raise ValueError("optimizer phenotype schema mismatch")

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if FORBIDDEN_OPTIMIZER_FIELDS.intersection(value):
                raise ValueError("forbidden optimizer-visible field")
            for item in value.values():
                walk(item)
        elif isinstance(value, (list, tuple)):
            raise ValueError("per-scenario/array data is not optimizer-visible")
        elif isinstance(value, float) and not math.isfinite(value):
            raise ValueError("nonfinite optimizer value")
    walk(view)


def build_evaluation_views(rows: Sequence[Dict[str, Any]], typed_genome_sha256: str) -> Tuple[Dict, Dict]:
    if not rows:
        raise ValueError("empty evaluator rows")
    for row in rows:
        for value in row.values():
            if isinstance(value, float) and not math.isfinite(value):
                raise ValueError("nonfinite evaluator metric")
    trace_bundle, outcome_bundle, phenotype_hashes = _phenotypes(rows)
    feedback = {
        "row_count": len(rows),
        "attempt_count": sum(row.get("attempt_count", 0) for row in rows),
        "failure_attempt_count": sum(row.get("failure_attempt_count", 0) for row in rows),
        "dependency_blocked_attempt_count": sum(row.get("dependency_blocked_attempt_count", 0) for row in rows),
        "pending_row_count": sum(row["pending_compensation"] > 0 for row in rows),
        "runtime_abort_row_count": sum(row["runtime_forced_abort"] == 1 for row in rows),
        "unsuccessful_escalation_row_count": sum(
            row["policy_selected_escalation"] == 1 and row["class_success"] == 0 and row["runtime_forced_abort"] == 0
            for row in rows
        ),
        "avoidable_harm_sum": sum(row["avoidable_harm"] for row in rows),
    }
    optimizer = {
        "genome_sha256": typed_genome_sha256,
        "fitness": _fitness(rows),
        "hard_constraints": {field: sum(row.get(field, 0) for row in rows) for field in HARD_FIELDS},
        "constraint_episode_count": sum(row["constraint_episode"] > 0 for row in rows),
        "contract_blocked_attempts": sum(row.get("contract_blocked_attempts", 0) for row in rows),
        "dependency_blocked_attempts": sum(row.get("dependency_blocked_attempts", 0) for row in rows),
        "feedback_marginals": feedback,
        "phenotype_hashes": phenotype_hashes,
    }
    assert_optimizer_view(optimizer)
    audit = {
        "evaluator_internal_rows": list(rows),
        "trace_bundle": trace_bundle,
        "outcome_bundle": outcome_bundle,
        "hash_to_record": {
            phenotype_hashes["joint"]: {
                "rows": list(rows),
                "trace_bundle": trace_bundle,
                "outcome_bundle": outcome_bundle,
            }
        },
    }
    return optimizer, audit


def complete_phenotype_collapse(views: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not views:
        raise ValueError("empty phenotype archive")
    counts = {
        name: len({view["phenotype_hashes"][name] for view in views})
        for name in ("trace", "outcome", "joint")
    }
    result = {
        "H_trace": counts["trace"],
        "H_outcome": counts["outcome"],
        "H_joint": counts["joint"],
        "diversity_ratio_trace": counts["trace"] / len(views),
        "diversity_ratio_outcome": counts["outcome"] / len(views),
        "diversity_ratio_joint": counts["joint"] / len(views),
    }
    result["complete_phenotype_collapse"] = any(value < 2 for value in counts.values())
    return result


def semantic_trace_changed(first: Dict[str, Any], second: Dict[str, Any]) -> bool:
    def project(row: Dict[str, Any]) -> List[Tuple[Tuple[str, ...], str]]:
        return [(tuple(event["action"]), event["observation"]) for event in row["trace"]]
    return project(first) != project(second)


def evaluate_with_rollouts(
    genome: TypedGenome,
    scenarios: Sequence[Dict[str, Any]],
    rollout,
    seed: int,
    unique_ordinal: int,
) -> Dict[str, Dict]:
    rows = [rollout(genome, scenario, seed, unique_ordinal) for scenario in scenarios]
    optimizer, audit = build_evaluation_views(rows, genome_sha256(genome))
    return {"optimizer_reward_view": optimizer, "audit_only_view": audit}


def load_train_manifest(path: Path = DEFAULT_MANIFEST) -> Dict[str, Any]:
    raw = Path(path).read_bytes()
    canonical_hash = hashlib.sha256(b"\n".join(raw.splitlines())).hexdigest()
    if canonical_hash != EXPECTED_MANIFEST_CANONICAL:
        raise ValueError("INVALID_HASH_BINDING: Train manifest canonical SHA")
    manifest = json.loads(raw.decode("utf-8"))
    internal = dict(manifest)
    actual_internal = internal.pop("manifest_sha256")
    computed = hashlib.sha256(
        json.dumps(internal, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if actual_internal != EXPECTED_MANIFEST_INTERNAL or computed != actual_internal:
        raise ValueError("INVALID_HASH_BINDING: Train manifest internal SHA")
    scenarios = manifest["scenarios"]
    if manifest["scenario_count"] != 96 or len(scenarios) != 96:
        raise ValueError("Train manifest must contain 96 scenarios")
    if len({scenario["scenario_id"] for scenario in scenarios}) != 96:
        raise ValueError("duplicate Train scenario IDs")
    if manifest.get("test_included") or any(scenario["split"] != "train" for scenario in scenarios):
        raise ValueError("Validation/Test data is forbidden")
    return manifest


def evaluate_train_genome(
    genome: TypedGenome,
    allow_train: bool = False,
    experiment_approved: bool = False,
    manifest_path: Path = DEFAULT_MANIFEST,
    seed: int = 711,
    unique_ordinal: int = 0,
) -> Dict[str, Dict]:
    if not (allow_train and experiment_approved):
        raise PermissionError("Train evaluation requires both explicit execution and experiment approval")
    manifest = load_train_manifest(manifest_path)
    from d090_policies import D090Policy
    from d092_runtime import run_guarded_episode
    rows = [
        run_guarded_episode(
            D090Policy(genome.to_d090()),
            scenario,
            seed=seed,
            unique_ordinal=unique_ordinal,
            typed_genome_sha256=genome_sha256(genome),
        )
        for scenario in manifest["scenarios"]
    ]
    optimizer, audit = build_evaluation_views(rows, genome_sha256(genome))
    return {"optimizer_reward_view": optimizer, "audit_only_view": audit}
