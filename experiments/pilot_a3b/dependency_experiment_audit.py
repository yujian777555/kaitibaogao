"""Independent D-086 artifact recomputation; never starts an optimizer."""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from dependency_evolution import _metrics

OUTDIR = Path(__file__).resolve().parent / "results" / "d086_evolution"
EXPECTED_SEEDS = [711, 822, 933, 1044, 1155]
EXPECTED_METHODS = ["RandomSearch", "NSGA-II", "NSGA-III", "C-NSGA-III"]


def _mean(values):
    return sum(values) / len(values) if values else None


def audit_artifact(outdir=OUTDIR):
    outdir = Path(outdir)
    runs = json.loads((outdir / "d086_experiment_runs.json").read_text(encoding="utf-8"))
    summary = json.loads((outdir / "d086_experiment_summary.json").read_text(encoding="utf-8"))
    checks = {}
    checks["forty_runs"] = len(runs) == 40 and summary["run_count"] == 40
    checks["eight_arms_five_seeds"] = all(
        len([run for run in runs if run["arm"] == arm]) == 5
        for arm in {run["arm"] for run in runs}
    ) and len({run["arm"] for run in runs}) == 8
    checks["seed_pairs"] = all(
        [run["seed"] for run in runs if run["arm"] == method] == EXPECTED_SEEDS
        for method in EXPECTED_METHODS
    )
    checks["initial_pool_size"] = all(len(run["initial_pool"]) == 12 for run in runs)
    checks["initial_pool_shared"] = all(
        run["initial_pool"] == runs[0]["initial_pool"]
        for run in runs if run["ablation"] is None
    ) and all(
        run["initial_pool"] == group[0]["initial_pool"]
        for ablation in {run["ablation"] for run in runs if run["ablation"] is not None}
        for group in [[run for run in runs if run["ablation"] == ablation]]
        for run in group
    )
    checks["archive_cap"] = all(len(run["archive"]) <= 84 for run in runs)
    checks["history_complete"] = all(len(run["history"]) == 6 for run in runs)
    checks["no_budget_exhaustion"] = all(not run["budget_exhausted"] for run in runs)
    checks["train_budget"] = all(
        run["history"][-1]["unique_episode_equivalent"]["train"] <= 6048
        for run in runs
    )
    raw_counts = {}
    total = 0
    selected_records = {}
    with gzip.open(outdir / "d086_experiment_rows.jsonl.gz", "rt", encoding="utf-8") as handle:
        for line in handle:
            item = json.loads(line)
            row = item["row"]
            if row["split"] not in ("train", "validation"):
                raise ValueError("forbidden split in raw ledger")
            key = (item["arm"], item["optimizer_seed"], row["split"])
            raw_counts[key] = raw_counts.get(key, 0) + 1
            total += 1
            if row["split"] == "validation":
                selected_records.setdefault((item["arm"], item["optimizer_seed"], item["ledger_key"][3]), []).append(row)
    checks["raw_row_count"] = total == summary["raw_row_count"]
    checks["train_raw_budget"] = all(
        raw_counts.get((run["arm"], run["seed"], "train"), 0) <= 6048
        for run in runs
    )
    checks["validation_raw_budget"] = all(
        raw_counts.get((run["arm"], run["seed"], "validation"), 0) <= 2016
        for run in runs
    )
    checks["ledger_stats_match_raw"] = all(
        raw_counts.get((run["arm"], run["seed"], role), 0)
        == run["ledger_stats"]["unique_episode_equivalent"][role]
        for run in runs for role in ("train", "validation")
    )
    selected_metric_checks = []
    for run in runs:
        if run["selection"]["status"] != "SELECTED":
            continue
        genome_fp = repr(sorted(run["selection"]["genome"].items()))
        rows = selected_records[(run["arm"], run["seed"], genome_fp)]
        recomputed = _metrics(rows)["metrics"]
        for key in ("r3_success", "r4_success", "condrec", "avoid_harm", "r3_cost", "constraint_count"):
            if recomputed[key] != run["selection"]["metrics"][key]:
                selected_metric_checks.append((run["arm"], run["seed"], key))
    checks["selected_metrics_recomputed"] = not selected_metric_checks
    full = [run for run in runs if run["arm"] == "C-NSGA-III"]
    greedy = json.loads((outdir.parent / "d086_fixed_gate" / "fixed_policy_gate.json").read_text(encoding="utf-8"))
    greedy_cost = greedy["summary"]["validation|Greedy|R3"]["recovery_cost_mean"]
    full_cost = _mean([
        run["selection"]["metrics"]["r3_cost"]
        for run in full if run["selection"]["status"] == "SELECTED"
    ])
    criteria = {
        "r3_all_one": all(run["selection"].get("metrics", {}).get("r3_success") == 1.0 for run in full),
        "r4_all_one": all(run["selection"].get("metrics", {}).get("r4_success") == 1.0 for run in full),
        "condrec_all_one": all(run["selection"].get("metrics", {}).get("condrec") == 1.0 for run in full),
        "zero_constraints": all(run["selection"].get("metrics", {}).get("constraint_count") == 0 for run in full),
        "cost_below_greedy": all(run["selection"]["status"] == "SELECTED" for run in full) and full_cost < greedy_cost,
        "budget_valid": checks["no_budget_exhaustion"] and checks["train_budget"],
        "selected_all_seeds": all(run["selection"]["status"] == "SELECTED" for run in full),
    }
    no_regression = True
    for method in EXPECTED_METHODS[:3]:
        for full_run, other_run in zip(full, [run for run in runs if run["arm"] == method]):
            if full_run["seed"] != other_run["seed"]:
                raise ValueError("unpaired optimizer seed")
            if full_run["selection"]["status"] != "SELECTED" or other_run["selection"]["status"] != "SELECTED":
                no_regression = False
                continue
            first = full_run["selection"]["metrics"]
            second = other_run["selection"]["metrics"]
            if (first["r3_success"] < second["r3_success"]
                    or first["r4_success"] < second["r4_success"]
                    or first["condrec"] < second["condrec"]
                    or first["r3_cost"] > second["r3_cost"]
                    or first["constraint_count"] > second["constraint_count"]):
                no_regression = False
    criteria["no_regression_vs_ea"] = no_regression
    failed = sorted(key for key, passed in criteria.items() if not passed)
    expected_status = "CANDIDATE_IMPROVEMENT_EXPLORATORY" if not failed else "NO_GO"
    checks["decision_recomputed"] = (
        expected_status == summary["analysis"]["status"]
        and failed == sorted(summary["analysis"]["failed_criteria"])
    )
    return {
        "ok": all(checks.values()),
        "checks": checks,
        "selected_metric_mismatches": selected_metric_checks,
        "recomputed_failed_criteria": failed,
        "recomputed_status": expected_status,
        "run_count": len(runs),
        "raw_row_count": total,
        "full_mean_r3_cost": full_cost,
        "greedy_r3_cost": greedy_cost,
        "optimizer_runs_in_audit": 0,
        "test_accessed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(OUTDIR))
    args = parser.parse_args()
    report = audit_artifact(args.outdir)
    output = Path(args.outdir) / "d086_independent_artifact_audit.json"
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output.exists() and output.read_text(encoding="utf-8") != text:
        raise FileExistsError("refusing to overwrite different independent audit")
    if not output.exists():
        output.write_text(text, encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
