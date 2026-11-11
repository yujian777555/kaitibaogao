"""D-086 fixed-policy optimization-space gate; contains no optimizer."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from dependency_challenge import MANIFEST_PATH, validate_lock, validate_manifest
from dependency_policies import make_policy
from dependency_recovery import run_episode

METHODS = (
    "Hand", "FixedPrefix", "FixedPrefixForward", "RuleBased",
    "Greedy", "AdaptiveProbe", "CostAware", "Random",
)
RANDOM_SEED = 20261122
OUTDIR = MANIFEST_PATH.parent.parent / "d086_fixed_gate"
GATE_PATH = OUTDIR / "fixed_policy_gate.json"
RAW_JSON_PATH = OUTDIR / "fixed_policy_rows.json"
RAW_CSV_PATH = OUTDIR / "fixed_policy_rows.csv"


def evaluate_manifest(manifest):
    rows = []
    for scenario in manifest["scenarios"]:
        for method in METHODS:
            policy = make_policy(method, seed=RANDOM_SEED)
            result = run_episode(policy, scenario)
            rows.append({
                "method": method,
                "policy_seed": RANDOM_SEED if method == "Random" else None,
                "scenario_id": scenario["scenario_id"],
                "task_family_id": scenario["task_family_id"],
                "split": scenario["split"],
                "difficulty_stratum": scenario["difficulty_stratum"],
                "composition": scenario["composition"],
                "repeat": scenario["repeat"],
                **result,
            })
    return rows


def summarize(rows):
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["split"], row["method"], row["label"], row["task_family_id"])].append(row)
    summary = {}
    for (split, method, label, family), group in sorted(buckets.items()):
        key = f"{split}|{method}|{label}"
        if key not in summary:
            summary[key] = {
                "scenario_count": 0,
                "family_count": 0,
                "families": [],
                "class_success_mean": 0.0,
                "residual_side_effects_mean": 0.0,
                "avoidable_harm_mean": 0.0,
                "recovery_cost_mean": 0.0,
                "action_cost_mean": 0.0,
                "constraint_violation_mean": 0.0,
                "conditional_recovery_success_mean": None,
                "correct_escalation_mean": None,
                "prefix_compensation_success_mean": None,
            }
        summary[key]["families"].append(group)
    for key, data in summary.items():
        families = data.pop("families")
        data["family_count"] = len(families)
        data["scenario_count"] = sum(len(group) for group in families)
        success_means = [
            sum(row["class_success"] for row in group) / len(group)
            for group in families
        ]
        data["class_success_mean"] = sum(success_means) / len(success_means)
        for metric in (
            "residual_side_effects", "avoidable_harm", "recovery_cost", "action_cost",
            "constraint_violation",
        ):
            family_means = [sum(row[metric] for row in group) / len(group) for group in families]
            data[metric + "_mean"] = sum(family_means) / len(family_means)
        label = key.rsplit("|", 1)[1]
        for metric, output in (
            ("conditional_recovery_success", "conditional_recovery_success_mean"),
            ("correct_escalation", "correct_escalation_mean"),
            ("prefix_compensation_success", "prefix_compensation_success_mean"),
        ):
            if label in ("R1", "R2") and metric == "conditional_recovery_success":
                data[output] = sum(row[metric] for group in families for row in group) / data["scenario_count"]
            elif label == "R3" and metric != "conditional_recovery_success":
                data[output] = sum(row[metric] for group in families for row in group) / data["scenario_count"]
    return summary


def _ceiling(rows, split, method):
    group = [row for row in rows if row["split"] == split and row["method"] == method]
    return all(
        row["class_success"] == 1
        and row["avoidable_harm"] == 0
        and row["constraint_violation"] == 0
        for row in group
    )


def _covers(rows, split, first, second):
    scenarios = sorted({row["scenario_id"] for row in rows if row["split"] == split})
    strict = False
    for scenario_id in scenarios:
        a = next(row for row in rows if row["split"] == split and row["method"] == first and row["scenario_id"] == scenario_id)
        b = next(row for row in rows if row["split"] == split and row["method"] == second and row["scenario_id"] == scenario_id)
        if (a["class_success"] < b["class_success"]
                or a["avoidable_harm"] > b["avoidable_harm"]
                or a["constraint_violation"] > b["constraint_violation"]
                or a["action_cost"] > b["action_cost"]):
            return False
        if (a["class_success"], -a["avoidable_harm"], -a["constraint_violation"], -a["action_cost"]) != (
            b["class_success"], -b["avoidable_harm"], -b["constraint_violation"], -b["action_cost"]
        ):
            strict = True
    return strict


def gate_decision(rows):
    ceilings = {
        f"{split}|{method}": _ceiling(rows, split, method)
        for split in ("train", "validation") for method in METHODS
    }
    dominants = {}
    for split in ("train", "validation"):
        dominants[split] = [
            method for method in METHODS
            if all(other == method or _covers(rows, split, method, other) for other in METHODS)
        ]
    shared_dominant = sorted(set(dominants["train"]) & set(dominants["validation"]))
    variation = any(
        (a["class_success"], a["avoidable_harm"], a["constraint_violation"], a["action_cost"])
        != (b["class_success"], b["avoidable_harm"], b["constraint_violation"], b["action_cost"])
        for scenario_id in {row["scenario_id"] for row in rows if row["split"] == "train"}
        for i, first in enumerate(METHODS)
        for second in METHODS[i + 1:]
        for a in [next(row for row in rows if row["split"] == "train" and row["method"] == first and row["scenario_id"] == scenario_id)]
        for b in [next(row for row in rows if row["split"] == "train" and row["method"] == second and row["scenario_id"] == scenario_id)]
    )
    if all(ceilings.values()) and shared_dominant:
        status = "CEILING_NO_EA"
    elif shared_dominant:
        status = "FIXED_DOMINANT_NO_EA"
    elif variation:
        status = "CANDIDATE_SPACE_REVIEW_REQUIRED"
    else:
        status = "CEILING_NO_EA"
    return {
        "status": status,
        "fixed_method_ceiling": ceilings,
        "dominant_methods_by_split": dominants,
        "shared_dominant_method": shared_dominant,
        "train_strategy_variation": variation,
        "optimizer_runs": 0,
        "test_accessed": False,
        "rule": "scenario-paired class success, avoidable harm, constraint and action-cost coverage; no scalar score",
    }


def _write_once(path, text):
    path = Path(path)
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            if handle.read() != text:
                raise FileExistsError("refusing to overwrite different gate evidence: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)


def write_outputs(summary, decision, rows, outdir=OUTDIR):
    outdir = Path(outdir)
    fields = [key for key in rows[0] if key != "trace"] + ["trace_json"]
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        output = {key: value for key, value in row.items() if key != "trace"}
        output["trace_json"] = json.dumps(row["trace"], ensure_ascii=False)
        writer.writerow(output)
    gate_text = json.dumps({"summary": summary, "decision": decision}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    raw_text = json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _write_once(outdir / GATE_PATH.name, gate_text)
    _write_once(outdir / RAW_JSON_PATH.name, raw_text)
    _write_once(outdir / RAW_CSV_PATH.name, buffer.getvalue())
    return outdir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    parser.add_argument("--outdir", default=str(OUTDIR))
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    for name, gate in (("manifest", validate_manifest(manifest)), ("lock", validate_lock(manifest))):
        if not gate["ok"]:
            raise RuntimeError(name + ": " + "; ".join(gate["problems"]))
    rows = evaluate_manifest(manifest)
    summary = summarize(rows)
    decision = gate_decision(rows)
    write_outputs(summary, decision, rows, args.outdir)
    print(json.dumps({
        "decision": decision,
        "raw_rows": len(rows),
        "train": {
            method: summary[f"train|{method}|R3"]
            for method in METHODS
        },
    }, indent=2))


if __name__ == "__main__":
    main()
