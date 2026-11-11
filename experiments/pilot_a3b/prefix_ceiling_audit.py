"""Fixed-controller ceiling audit on the locked D-085 development manifest."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from a3_bridge import evaluate_controller, evaluator_verdict_from_scenario, hand_fsm
from prefix_challenge_generator import (
    LOCK_PATH,
    MANIFEST_PATH,
    validate_manifest_lock,
    validate_prefix_manifest,
)
from prefix_recovery import prefix_hand_fsm

CEILING_PATH = MANIFEST_PATH.parent / "prefix_fixed_controller_ceiling_audit.json"


def audit_fixed_controllers(manifest_path=MANIFEST_PATH, lock_path=LOCK_PATH):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    for name, gate in (
        ("manifest", validate_prefix_manifest(manifest)),
        ("lock", validate_manifest_lock(manifest, lock_path)),
    ):
        if not gate["ok"]:
            raise ValueError(name + " gate failed: " + "; ".join(gate["problems"]))
    scenarios = manifest["scenarios"]
    verdicts = {row["scenario_id"]: evaluator_verdict_from_scenario(row) for row in scenarios}
    summary = {
        "status": "FIXED_CONTROLLER_CEILING_AUDIT_ONLY",
        "manifest_sha256": manifest["manifest_sha256"],
        "optimizer_runs": 0,
        "test_accessed": False,
        "methods": {},
    }
    rows_out = []
    for name, factory in (("Hand", hand_fsm), ("PrefixAware", prefix_hand_fsm)):
        result = evaluate_controller(factory(), scenarios, verdicts)
        grouped = defaultdict(list)
        for scenario, row in zip(scenarios, result["rows"]):
            grouped[(scenario["split"], row["label"])].append(row)
            violation = int(bool(row["invariant_violation"] or row["duplicate"] or row["sla_violation"]))
            rows_out.append({
                "method": name,
                "scenario_id": scenario["scenario_id"],
                "split": scenario["split"],
                "label": row["label"],
                "class_success": row["class_success"],
                "active_effects": row["active_effects"],
                "avoidable_harm": row["avoidable_harm"],
                "constraint_violation": violation,
                "decision_count": row["decision_count"],
                "tool_action_count": row["tool_action_count"],
            })
        groups = {}
        for (split, label), rows in sorted(grouped.items()):
            groups[f"{split}|{label}"] = {
                "n": len(rows),
                "success_sum": sum(row["class_success"] for row in rows),
                "avoidable_harm_sum": sum(row["avoidable_harm"] for row in rows),
                "constraint_violation_sum": sum(
                    int(bool(row["invariant_violation"] or row["duplicate"] or row["sla_violation"]))
                    for row in rows
                ),
                "tool_action_count_mean": sum(row["tool_action_count"] for row in rows) / len(rows),
            }
        summary["methods"][name] = groups
    prefix = [row for row in rows_out if row["method"] == "PrefixAware"]
    summary["prefix_all_class_success"] = all(row["class_success"] == 1 for row in prefix)
    summary["prefix_zero_avoidable_harm"] = all(row["avoidable_harm"] == 0 for row in prefix)
    summary["prefix_zero_constraint_violation"] = all(row["constraint_violation"] == 0 for row in prefix)
    summary["ceiling_for_required_behavior"] = (
        summary["prefix_all_class_success"]
        and summary["prefix_zero_avoidable_harm"]
        and summary["prefix_zero_constraint_violation"]
    )
    return summary, rows_out


def write_ceiling_outputs(summary, rows, path=CEILING_PATH):
    path = Path(path)
    text = json.dumps({"summary": summary, "rows": rows}, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise FileExistsError("refusing to overwrite different ceiling evidence: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    parser.add_argument("--lock-path", default=str(LOCK_PATH))
    parser.add_argument("--outfile", default=str(CEILING_PATH))
    args = parser.parse_args()
    summary, rows = audit_fixed_controllers(args.manifest, args.lock_path)
    write_ceiling_outputs(summary, rows, args.outfile)
    print(json.dumps({
        "status": summary["status"],
        "rows": len(rows),
        "ceiling_for_required_behavior": summary["ceiling_for_required_behavior"],
        "optimizer_runs": 0,
        "test_accessed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
