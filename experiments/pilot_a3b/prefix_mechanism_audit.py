"""Reproducible R3/R4 mechanism reachability audit; never an optimizer run."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path

from a3_bridge import evaluate_controller, evaluator_verdict_from_scenario, hand_fsm
from d079_challenge_generator import validate_challenge_manifest, validate_manifest_lock
from prefix_recovery import prefix_hand_fsm

ROOT = Path(__file__).resolve().parents[2]
STRATA = {
    "D5_PERMISSION_AFTER_COMMITTED_PREFIX",
    "D6_UNCOMPENSATABLE_PARTIAL_COMMIT",
}
FIELDS = (
    "method", "scenario_id", "task_family_id", "difficulty_stratum", "split",
    "evaluation_role", "seed", "label", "min_reachable_harm", "class_success",
    "task_success", "active_effects", "residual_side_effects", "avoidable_harm",
    "duplicate", "sla_violation", "invariant_violation", "constraint_violation",
    "policy_selected_escalation", "runtime_forced_abort", "escalation_reason",
    "compensation_attempts", "compensation_failures", "prefix_compensation_success",
    "decision_count", "action_count", "tool_action_count", "decision_trace_json", "comp_log_json",
    "prefix_verification_log_json",
)


def _source_hashes():
    paths = (
        "experiments/pilot_a_recovery/pilot_a3.py",
        "experiments/pilot_a3b/a3_bridge.py",
        "experiments/pilot_a3b/a3_verdicts.py",
        "experiments/pilot_a3b/contract_validator.py",
        "experiments/pilot_a3b/prefix_recovery.py",
        "experiments/pilot_a3b/prefix_mechanism_audit.py",
        "experiments/pilot_a3b/d079_challenge_generator.py",
    )
    return {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in paths
    }


def audit_prefix_mechanisms(manifest_path, lock_path=None):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    gates = {
        "manifest": validate_challenge_manifest(manifest),
        "lock": validate_manifest_lock(manifest, lock_path),
    }
    problems = [name + ": " + problem for name, gate in gates.items() for problem in gate["problems"]]
    if problems:
        raise ValueError("D-079 manifest/lock audit failed: " + "; ".join(problems))
    scenarios = [
        row for row in manifest["scenarios"]
        if row["evaluation_role"] == "diagnostic" and row["difficulty_stratum"] in STRATA
    ]
    if len(scenarios) != 48:
        raise ValueError("expected 24 D5 and 24 D6 Diagnostic scenarios")
    verdicts = {row["scenario_id"]: evaluator_verdict_from_scenario(row) for row in scenarios}
    rows = []
    for method, factory in (("Hand", hand_fsm), ("PrefixAware", prefix_hand_fsm)):
        result = evaluate_controller(factory(), scenarios, verdicts)
        for scenario, verdict, row in zip(scenarios, verdicts.values(), result["rows"]):
            residual = 0 if row["task_success"] else row["active_effects"]
            compensated = any(entry[2] == "COMPENSATED" for entry in row["comp_log"])
            rows.append({
                "method": method,
                "scenario_id": scenario["scenario_id"],
                "task_family_id": scenario["task_family_id"],
                "difficulty_stratum": scenario["difficulty_stratum"],
                "split": scenario["split"],
                "evaluation_role": scenario["evaluation_role"],
                "seed": scenario["seed"],
                "label": row["label"],
                "min_reachable_harm": verdict["min_reachable_harm"],
                "class_success": row["class_success"],
                "task_success": row["task_success"],
                "active_effects": row["active_effects"],
                "residual_side_effects": residual,
                "avoidable_harm": row["avoidable_harm"],
                "duplicate": row["duplicate"],
                "sla_violation": row["sla_violation"],
                "invariant_violation": row["invariant_violation"],
                "constraint_violation": int(bool(
                    row["duplicate"] or row["sla_violation"] or row["invariant_violation"]
                )),
                "policy_selected_escalation": row["policy_selected_escalation"],
                "runtime_forced_abort": row["runtime_forced_abort"],
                "escalation_reason": row["escalation_reason"],
                "compensation_attempts": row["compensation_attempts"],
                "compensation_failures": row["compensation_failures"],
                "prefix_compensation_success": (
                    int(row["class_success"] == 1 and residual == 0 and compensated)
                    if row["label"] == "R3" else None
                ),
                "decision_count": row["decision_count"],
                "action_count": row["action_count"],
                "tool_action_count": row["tool_action_count"],
                "decision_trace_json": json.dumps(row["decision_trace"], ensure_ascii=False),
                "comp_log_json": json.dumps(row["comp_log"], ensure_ascii=False),
                "prefix_verification_log_json": json.dumps(
                    row["prefix_verification_log"], ensure_ascii=False
                ),
            })
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["method"], row["label"])].append(row)
    methods = {}
    for method in ("Hand", "PrefixAware"):
        methods[method] = {}
        for label in ("R3", "R4"):
            group = buckets[(method, label)]
            if len(group) != 24:
                raise ValueError("each method/label audit group must contain 24 rows")
            methods[method][label] = {
                "n": len(group),
                "class_success_sum": sum(row["class_success"] for row in group),
                "class_success_rate": sum(row["class_success"] for row in group) / len(group),
                "residual_side_effects_mean": sum(row["residual_side_effects"] for row in group) / len(group),
                "avoidable_harm_mean": sum(row["avoidable_harm"] for row in group) / len(group),
                "constraint_violation_sum": sum(row["constraint_violation"] for row in group),
                "prefix_compensation_success_sum": (
                    sum(row["prefix_compensation_success"] for row in group)
                    if label == "R3" else None
                ),
            }
    try:
        git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        git_head = "UNKNOWN"
    summary = {
        "status": "MECHANISM_REACHABILITY_ONLY_NOT_ALGORITHM_PERFORMANCE_PROOF",
        "protocol": "D-085-R3-ROOT-CAUSE",
        "git_head_at_audit": git_head,
        "source_sha256": _source_hashes(),
        "d079_manifest_sha256": manifest["manifest_sha256"],
        "d079_lock_validated": True,
        "scenario_count_per_method": len(scenarios),
        "optimizer_runs": 0,
        "test_accessed": False,
        "validation_accessed": False,
        "data_splits": sorted({row["split"] for row in rows}),
        "historical_artifacts_overwritten": False,
        "methods": methods,
    }
    return summary, rows


def write_audit_outputs(summary, rows, outdir):
    outdir = Path(outdir)
    if not rows:
        raise ValueError("mechanism audit requires raw rows")
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    payloads = {
        "prefix_mechanism_summary.json": json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        "prefix_mechanism_rows.json": json.dumps(rows, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        "prefix_mechanism_rows.csv": buffer.getvalue(),
    }
    for filename, text in payloads.items():
        path = outdir / filename
        if path.exists():
            with path.open("r", encoding="utf-8", newline="") as handle:
                if handle.read() != text:
                    raise FileExistsError("refusing to overwrite different mechanism evidence: " + str(path))
    outdir.mkdir(parents=True, exist_ok=True)
    for filename, text in payloads.items():
        path = outdir / filename
        if not path.exists():
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(text)
    return {filename: hashlib.sha256(text.encode("utf-8")).hexdigest() for filename, text in payloads.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(
        ROOT / "experiments/pilot_a3b/results/d079_challenge_v2/d079_challenge_manifest.json"
    ))
    parser.add_argument("--lock-path")
    parser.add_argument("--outdir", default=str(
        ROOT / "experiments/pilot_a3b/results/d085_prefix_mechanism_audit"
    ))
    args = parser.parse_args()
    summary, rows = audit_prefix_mechanisms(args.manifest, args.lock_path)
    hashes = write_audit_outputs(summary, rows, args.outdir)
    print(json.dumps({
        "status": summary["status"],
        "raw_rows": len(rows),
        "methods": summary["methods"],
        "artifact_sha256": hashes,
        "optimizer_runs": 0,
        "test_accessed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
