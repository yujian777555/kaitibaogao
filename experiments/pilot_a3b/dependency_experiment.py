"""Execute the frozen D-086 exploratory protocol and preserve raw evidence."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

from dependency_challenge import LOCK_PATH, MANIFEST_PATH, validate_lock, validate_manifest
from dependency_evolution import run_search, select_validation
from dependency_gate import GATE_PATH

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "d086_experiment_config.json"
OUTDIR = HERE / "results" / "d086_evolution"
EXPECTED = {
    "protocol_id": "D-086-EVOLUTION",
    "preregistration": "90_D086_EVOLUTION_PREREGISTRATION.md",
    "generator_version": "d086-dependency-recovery-v1",
    "evaluator_version": "d086-dependency-v1",
    "manifest_sha256": "362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67",
    "population_size": 12,
    "generations": 6,
    "optimizer_seeds": [711, 822, 933, 1044, 1155],
    "methods": ["RandomSearch", "NSGA-II", "NSGA-III", "C-NSGA-III"],
    "ablations": ["NoDependencyPriority", "NoFailureFeedback", "NoAlternate", "NoPendingVerification"],
    "episode_cap_per_arm_seed": 6048,
    "decision_cap_per_episode": 24,
    "train_scenario_count": 72,
    "validation_scenario_count": 24,
    "random_policy_seed": 20261122,
    "status": "FROZEN_FOR_TRAIN_ONLY_EXPLORATORY_SEARCH",
    "test_access": False,
    "selection_rule": "feasible Pareto; R3; R4; harm; CondRecSucc; cost; fingerprint",
    "statistics": "five-seed exploratory paired descriptive comparisons only; no confirmatory test",
}
ARM_NAMES = EXPECTED["methods"] + ["Full/" + name for name in EXPECTED["ablations"]]


def validate_config(config):
    if config != EXPECTED:
        raise ValueError("D-086 config differs from the frozen preregistration")
    return config


def _record(record):
    return {
        "genome": record["genome"].fingerprint(),
        "objectives": record["objectives"],
        "metrics": record["metrics"],
        "summary": record["summary"],
    }


def _selection(selection):
    output = {key: value for key, value in selection.items() if key not in ("validation_rows", "ledger")}
    if selection.get("genome") is not None:
        output["genome"] = selection["genome"].fingerprint()
    return output


def _arm_name(method, ablation):
    return method if ablation is None else "Full/" + ablation


def run_experiment(config, manifest):
    validate_config(config)
    if not validate_manifest(manifest)["ok"] or not validate_lock(manifest, LOCK_PATH)["ok"]:
        raise ValueError("D-086 manifest or lock is invalid")
    train = [row for row in manifest["scenarios"] if row["split"] == "train"]
    validation = [row for row in manifest["scenarios"] if row["split"] == "validation"]
    if len(train) != 72 or len(validation) != 24:
        raise ValueError("unexpected Train/Validation sizes")
    runs = []
    for method, ablation in [(method, None) for method in EXPECTED["methods"]] + [
        ("C-NSGA-III", name) for name in EXPECTED["ablations"]
    ]:
        for seed in EXPECTED["optimizer_seeds"]:
            search = run_search(
                method, seed, train,
                population_size=config["population_size"],
                generations=config["generations"],
                episode_cap=config["episode_cap_per_arm_seed"],
                manifest_sha=config["manifest_sha256"],
                ablation=ablation,
            )
            selection = select_validation(search, validation)
            runs.append({
                "arm": _arm_name(method, ablation),
                "method": method,
                "ablation": ablation,
                "seed": seed,
                "archive": [_record(record) for record in search["archive"]],
                "initial_pool": search["initial_pool"],
                "final_population": [_record(record) for record in search["final_population"]],
                "history": search["history"],
                "budget_exhausted": search["budget_exhausted"],
                "test_accessed": search["test_accessed"],
                "ledger": search["ledger"],
                "selection": _selection(selection),
            })
    return runs


def _mean(values):
    return sum(values) / len(values) if values else None


def analyze_runs(runs):
    by_arm = {}
    for arm in ARM_NAMES:
        group = [run for run in runs if run["arm"] == arm]
        by_arm[arm] = [
            {
                "seed": run["seed"],
                "status": run["selection"]["status"],
                "metrics": run["selection"].get("metrics"),
                "budget_exhausted": run["budget_exhausted"],
                "archive_count": len(run["archive"]),
                "train_unique": run["ledger"].stats["unique_episode_equivalent"]["train"],
                "validation_unique": run["ledger"].stats["unique_episode_equivalent"]["validation"],
                "cache_hits": run["ledger"].stats["cache_hits"],
            }
            for run in group
        ]
    full = [run for run in runs if run["arm"] == "C-NSGA-III"]
    greedy_cost = json.loads(GATE_PATH.read_text(encoding="utf-8"))["summary"]["validation|Greedy|R3"]["recovery_cost_mean"]
    criteria = {
        "r3_all_one": all(run["selection"].get("metrics", {}).get("r3_success") == 1.0 for run in full),
        "r4_all_one": all(run["selection"].get("metrics", {}).get("r4_success") == 1.0 for run in full),
        "condrec_all_one": all(run["selection"].get("metrics", {}).get("condrec") == 1.0 for run in full),
        "zero_constraints": all(run["selection"].get("metrics", {}).get("constraint_count") == 0 for run in full),
        "cost_below_greedy": (
            all(run["selection"]["status"] == "SELECTED" for run in full)
            and _mean([run["selection"]["metrics"]["r3_cost"] for run in full]) < greedy_cost
        ),
        "budget_valid": all(not run["budget_exhausted"] and run["ledger"].stats["unique_episode_equivalent"]["train"] <= 6048 for run in runs),
        "selected_all_seeds": all(run["selection"]["status"] == "SELECTED" for run in full),
    }
    other_comparisons = {}
    for method in EXPECTED["methods"][:3]:
        group = [run for run in runs if run["arm"] == method]
        per_seed = []
        for full_run, other_run in zip(full, group):
            if full_run["seed"] != other_run["seed"]:
                raise ValueError("optimizer seeds are not paired")
            if full_run["selection"]["status"] != "SELECTED" or other_run["selection"]["status"] != "SELECTED":
                per_seed.append({"seed": full_run["seed"], "valid_comparison": False})
                continue
            first = full_run["selection"]["metrics"]
            second = other_run["selection"]["metrics"]
            per_seed.append({
                "seed": full_run["seed"],
                "valid_comparison": True,
                "r3_difference": first["r3_success"] - second["r3_success"],
                "r4_difference": first["r4_success"] - second["r4_success"],
                "condrec_difference": first["condrec"] - second["condrec"],
                "cost_difference": first["r3_cost"] - second["r3_cost"],
                "constraint_difference": first["constraint_count"] - second["constraint_count"],
            })
        other_comparisons[method] = {
            "per_seed": per_seed,
            "no_regression": all(
                item["valid_comparison"]
                and item["r3_difference"] >= 0
                and item["r4_difference"] >= 0
                and item["condrec_difference"] >= 0
                and item["cost_difference"] <= 0
                and item["constraint_difference"] <= 0
                for item in per_seed
            ),
        }
    criteria["no_regression_vs_ea"] = all(item["no_regression"] for item in other_comparisons.values())
    failed = [key for key, passed in criteria.items() if not passed]
    ablations = {}
    for name in EXPECTED["ablations"]:
        group = [run for run in runs if run["arm"] == "Full/" + name]
        metrics = [run["selection"].get("metrics") for run in group]
        ablations[name] = {
            "mean_r3_success": _mean([item["r3_success"] for item in metrics if item]),
            "mean_r3_cost": _mean([item["r3_cost"] for item in metrics if item]),
            "constraint_count": sum(item["constraint_count"] for item in metrics if item),
            "hold_seeds": [run["seed"] for run in group if run["selection"]["status"] != "SELECTED"],
        }
    return {
        "status": "CANDIDATE_IMPROVEMENT_EXPLORATORY" if not failed else "NO_GO",
        "failed_criteria": failed,
        "arms": by_arm,
        "full_vs_greedy": {
            "greedy_r3_cost": greedy_cost,
            "full_mean_r3_cost": _mean([
                run["selection"]["metrics"]["r3_cost"]
                for run in full if run["selection"]["status"] == "SELECTED"
            ]),
            "criteria": criteria,
        },
        "full_vs_other_ea": other_comparisons,
        "ablations": ablations,
        "interpretation": "exploratory five-seed comparison only; not a confirmatory statistical conclusion",
    }


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _write_text(path, text):
    path = Path(path)
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            if handle.read() != text:
                raise FileExistsError("refusing to overwrite different D-086 evidence: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(text)


def write_outputs(runs, analysis, outdir=OUTDIR):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    serial_runs = []
    raw_lines = []
    for run in runs:
        serial_runs.append({
            **{key: value for key, value in run.items() if key != "ledger"},
            "ledger_stats": run["ledger"].stats,
        })
        for key, row in run["ledger"].rows.items():
            raw_lines.append(json.dumps({
                "arm": run["arm"],
                "optimizer_seed": run["seed"],
                "ledger_key": list(key),
                "row": row,
            }, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    buffer = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buffer, mtime=0) as handle:
        handle.write(("\n".join(raw_lines) + "\n").encode("utf-8"))
    raw_bytes = buffer.getvalue()
    raw_path = outdir / "d086_experiment_rows.jsonl.gz"
    if raw_path.exists() and raw_path.read_bytes() != raw_bytes:
        raise FileExistsError("refusing to overwrite different D-086 raw ledger")
    if not raw_path.exists():
        raw_path.write_bytes(raw_bytes)
    summary = {
        "status": "EXPLORATORY_RESULTS_NOT_CONFIRMATION",
        "protocol_id": config["protocol_id"],
        "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        "manifest_sha256": config["manifest_sha256"],
        "arm_count": len(ARM_NAMES),
        "run_count": len(runs),
        "seed_count": len(config["optimizer_seeds"]),
        "raw_row_count": len(raw_lines),
        "analysis": analysis,
        "optimizer_api_calls": 0,
        "test_accessed": False,
    }
    report = [
        "# D-086 exploratory evolutionary results",
        "",
        "This is not a confirmatory statistical conclusion. No Test data or real LLM API was accessed.",
        "",
        f"- Decision: **{analysis['status']}**",
        f"- Runs: {len(runs)} across {len(ARM_NAMES)} arms and {len(config['optimizer_seeds'])} seeds.",
        f"- Raw evaluation rows: {len(raw_lines)}.",
        f"- Failed criteria: {analysis['failed_criteria']}.",
        "",
        "| Arm | Seed | R3 | R4 | CondRec | R3 cost | Constraints | Train unique episodes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARM_NAMES:
        for item in analysis["arms"][arm]:
            metrics = item["metrics"]
            if metrics is None:
                report.append(f"| {arm} | {item['seed']} | HOLD | — | — | — | — | {item['train_unique']} |")
            else:
                report.append(
                    f"| {arm} | {item['seed']} | {metrics['r3_success']:.4f} | {metrics['r4_success']:.4f} | "
                    f"{metrics['condrec']:.4f} | {metrics['r3_cost']:.4f} | {metrics['constraint_count']} | {item['train_unique']} |"
                )
    _write_text(outdir / "d086_experiment_runs.json", _json_text(serial_runs))
    _write_text(outdir / "d086_experiment_summary.json", _json_text(summary))
    _write_text(outdir / "d086_experiment_report.md", "\n".join(report) + "\n")
    manifest = {
        "raw_row_count": len(raw_lines),
        "files": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                outdir / "d086_experiment_runs.json",
                outdir / "d086_experiment_summary.json",
                outdir / "d086_experiment_rows.jsonl.gz",
                outdir / "d086_experiment_report.md",
            )
        },
    }
    _write_text(outdir / "d086_experiment_artifact_manifest.json", _json_text(manifest))
    return summary


def validate_artifact(outdir=OUTDIR):
    outdir = Path(outdir)
    runs = json.loads((outdir / "d086_experiment_runs.json").read_text(encoding="utf-8"))
    summary = json.loads((outdir / "d086_experiment_summary.json").read_text(encoding="utf-8"))
    count = 0
    with gzip.open(outdir / "d086_experiment_rows.jsonl.gz", "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row["row"]["split"] not in ("train", "validation"):
                raise ValueError("forbidden data split in raw ledger")
            count += 1
    if len(runs) != 40 or summary["run_count"] != 40 or summary["raw_row_count"] != count:
        raise ValueError("D-086 run or raw-row counts are inconsistent")
    if any(run["budget_exhausted"] for run in runs):
        raise ValueError("D-086 experiment exhausted its unique budget")
    return {"ok": True, "run_count": len(runs), "raw_row_count": count, "test_accessed": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--manifest", default=str(MANIFEST_PATH))
    parser.add_argument("--outdir", default=str(OUTDIR))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        print(json.dumps(validate_artifact(args.outdir), indent=2))
        return
    config = validate_config(json.loads(Path(args.config).read_text(encoding="utf-8")))
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    runs = run_experiment(config, manifest)
    analysis = analyze_runs(runs)
    summary = write_outputs(runs, analysis, args.outdir)
    print(json.dumps({
        "status": summary["status"],
        "decision": analysis["status"],
        "failed_criteria": analysis["failed_criteria"],
        "run_count": summary["run_count"],
        "raw_row_count": summary["raw_row_count"],
        "artifact_verification": validate_artifact(args.outdir),
    }, indent=2))


if __name__ == "__main__":
    main()
