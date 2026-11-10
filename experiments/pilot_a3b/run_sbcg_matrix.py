"""Run the non-confirmatory D-078 14-arm Train/Validation development pilot."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from a3_bridge import scenario_verdict
from formal_scenario_generator import build_candidate_manifest
from sbcg_experiment import run_algorithm_matrix, write_algorithm_matrix_outputs
from split_access import scenarios_for_split


def _sha256(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _code_hash():
    paths = (
        HERE / "run_sbcg_matrix.py", HERE / "formal_scenario_generator.py",
        HERE / "sbcg_experiment.py", HERE / "sbcg_runner.py", HERE / "sbcg.py",
        HERE / "ea.py", HERE / "a3_bridge.py", HERE / "split_access.py",
        HERE / "contract_validator.py",
    )
    entries = {}
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        entries[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _sha256(entries)


def run(outdir, seeds=(411, 522, 633), pop_size=8, generations=5, initial_pool_size=60):
    manifest, audit = build_candidate_manifest()
    if manifest.get("gate", {}).get("passed") is not True:
        raise RuntimeError("formal scenario manifest gate failed: " + "; ".join(manifest["gate"].get("problems", [])))
    if audit.get("catalog_audit", {}).get("ok") is not True:
        raise RuntimeError("split catalog audit failed")

    train = scenarios_for_split(manifest, "train")
    validation = scenarios_for_split(manifest, "validation")
    if not train or not validation:
        raise RuntimeError("Train and Validation splits must both be non-empty")
    if any(row.get("split") != "train" for row in train):
        raise RuntimeError("non-Train scenario entered the evolution split")
    if any(row.get("split") != "validation" for row in validation):
        raise RuntimeError("non-Validation scenario entered the selection split")

    development_rows = train + validation
    verdicts = {
        row["scenario_id"]: scenario_verdict(row)
        for row in development_rows
    }
    if len(verdicts) != len(train) + len(validation):
        raise RuntimeError("development verdict map does not cover Train and Validation exactly")
    if any("min_reachable_harm" not in verdict for verdict in verdicts.values()):
        raise RuntimeError("scenario verdict map lacks the evaluator's required reachable-harm contract")

    episode_budget = pop_size * (generations + 1) * len(train)
    result = run_algorithm_matrix(
        train, validation, verdicts, seeds=tuple(seeds),
        eval_budget=episode_budget, pop_size=pop_size,
        generations=generations, initial_pool_size=initial_pool_size,
    )
    result.update({
        "pilot_type": "EXPLORATORY_NONCONFIRMATORY_SYNTHETIC_TRAIN_VALIDATION",
        "manifest_sha256": manifest["manifest_sha256"],
        "manifest_generator_version": manifest["generator_version"],
        "scenario_semantics": manifest["semantic_scope"],
        "code_sha256": _code_hash(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True
        ).strip(),
        "test_policy": {
            "test_locked_metadata_only": True,
            "test_scenarios_passed_to_runner": False,
            "test_outcomes_read": False,
            "note": "The manifest builder creates the locked split transiently for catalog/hash validation; only Train and Validation rows are returned to this pilot.",
        },
        "mde_or_confirmatory_inference": "NOT_APPLICABLE_TO_THIS_EXPLORATORY_PILOT",
        "llm_api_calls": 0,
    })
    json_path, report_path = write_algorithm_matrix_outputs(result, outdir)
    return result, json_path, report_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(HERE / "results" / "d078_train_validation_pilot"))
    parser.add_argument("--seeds", default="411,522,633")
    parser.add_argument("--population", type=int, default=8)
    parser.add_argument("--generations", type=int, default=5)
    parser.add_argument("--initial-pool-size", type=int, default=60)
    args = parser.parse_args()
    seeds = tuple(int(value) for value in args.seeds.split(",") if value.strip())
    result, json_path, report_path = run(
        args.outdir, seeds=seeds, pop_size=args.population,
        generations=args.generations, initial_pool_size=args.initial_pool_size,
    )
    print(json.dumps({
        "status": result["status"],
        "pilot_type": result["pilot_type"],
        "manifest_sha256": result["manifest_sha256"],
        "algorithm_count": result["algorithm_count"],
        "run_count": result["run_count"],
        "train_scenarios": result["train_scenario_count"],
        "validation_scenarios": result["validation_scenario_count"],
        "per_evolutionary_arm_train_episode_budget": result["per_evolutionary_arm_train_episode_budget"],
        "json": str(json_path),
        "report": str(report_path),
        "test_outcomes_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
