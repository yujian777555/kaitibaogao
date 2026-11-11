"""Locked Train-only D-079 mechanism diagnostic.

Search and diagnostic roles are disjoint Train-only scenario replicates. Robust
AND-OR labels enter the evaluator. Diagnostic outcomes never feed back into
search, mutation, or candidate archives. This is exploratory, not confirmatory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import subprocess
from collections import defaultdict
from pathlib import Path

from a3_bridge import evaluator_verdict_from_scenario
from d079_manifest_lock import verify_manifest_lock_files
from ea import run_evolution
from sbcg import (
    fsm_fingerprint,
    make_shared_initial_pool,
    select_train_diagnostic_candidate,
)
from sbcg_experiment import _fixed_policy, algorithm_specs
from sbcg_runner import run_sbcg_evolution
from sbcg import evaluate_sbcg_candidate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIAGNOSTIC_VERSION = "d079-train-only-locked-diagnostic-v1"
BOOTSTRAP_SEED = 20261115
BOOTSTRAP_DRAWS = 10000


def _canonical_sha256(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _code_sha256():
    names = (
        "d079_train_only_diagnostic.py", "d079_challenge_generator.py",
        "d079_manifest_lock.py", "sbcg.py", "sbcg_runner.py",
        "sbcg_experiment.py", "ea.py", "a3_bridge.py", "split_access.py",
        "contract_validator.py",
    )
    return _canonical_sha256({
        name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        for name in names
    })


def _record_view(record):
    return {
        "fingerprint": record.fingerprint,
        "objectives": list(record.objectives),
        "constraints": dict(record.constraints),
        "per_family_condrec": dict(record.per_family_condrec),
        "family_coverage": record.family_coverage,
        "worst_family_condrec": record.worst_family_condrec,
        "source_split": record.source_split,
    }


def _mean(values):
    values = list(values)
    return sum(values) / len(values) if values else None


def _paired_bootstrap(differences, seed=BOOTSTRAP_SEED, draws=BOOTSTRAP_DRAWS):
    values = list(differences)
    if not values:
        return {"n": 0, "mean": None, "ci95": None}
    rng = random.Random(seed)
    sampled_means = []
    for _ in range(draws):
        sampled_means.append(_mean(rng.choice(values) for _ in values))
    sampled_means.sort()
    return {
        "n": len(values),
        "mean": _mean(values),
        "ci95": [
            sampled_means[int(0.025 * (len(sampled_means) - 1))],
            sampled_means[int(0.975 * (len(sampled_means) - 1))],
        ],
        "note": "exploratory paired-seed bootstrap; not a confirmatory p-value",
    }


def _metric_values(record):
    metrics = record.metrics if record is not None else None
    if metrics is None:
        return None
    return {
        "cond_rec": metrics.get("cond_rec"),
        "correct_escalation": metrics.get("corr_esc"),
        "damage_containment": metrics.get("containment"),
        "avoidable_harm": metrics.get("avoid_resid"),
        "action_cost": metrics.get("unnec_actions_r12"),
        "recovery_cost": metrics.get("r34_action_cost_desc"),
        "constraint_violation": sum(float(metrics.get(name, 0.0) or 0.0)
                                     for name in ("dup", "sla_viol", "violations")),
    }


def _arm_summary(results):
    output = {}
    for algorithm in sorted({row["algorithm"] for row in results}):
        subset = [row for row in results if row["algorithm"] == algorithm]
        metrics = [_metric_values(row["selected_record"]) for row in subset]
        valid = [value for value in metrics if value is not None]
        fields = list(_metric_values(next(
            row["selected_record"] for row in subset if row["selected_record"] is not None
        ))) if valid else [
            "cond_rec", "correct_escalation", "damage_containment",
            "avoidable_harm", "action_cost", "recovery_cost", "constraint_violation",
        ]
        summary = {
            "runs": len(subset),
            "selected_runs": len(valid),
            "search_episodes": _mean(row["search_episodes"] for row in subset),
            "diagnostic_episodes": _mean(row["diagnostic_episodes"] for row in subset),
            "unique_evaluations": _mean(row["unique_evaluations"] for row in subset),
            "cache_hits": _mean(row["cache_hits"] for row in subset),
        }
        for field in fields:
            values = [value[field] for value in valid if value[field] is not None]
            summary[field] = {
                "mean": _mean(values),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "per_seed": {
                    str(row["seed"]): value[field]
                    for row, value in zip(subset, metrics)
                    if value is not None and value[field] is not None
                },
            }
        output[algorithm] = summary
    return output


def _contrasts(results):
    pairs = {
        "SBCG_minus_Hand": ("SBCG-NSGA-III", "Hand FSM"),
        "SBCG_minus_Random": ("SBCG-NSGA-III", "Random"),
        "SBCG_minus_Rule": ("SBCG-NSGA-III", "Rule-based"),
        "SBCG_minus_Reflection": ("SBCG-NSGA-III", "Reflection"),
        "SBCG_minus_NSGAII": ("SBCG-NSGA-III", "NSGA-II"),
        "SBCG_minus_NSGAIII": ("SBCG-NSGA-III", "NSGA-III"),
        "SBCG_minus_matched_NSGAII": ("SBCG-NSGA-III", "Matched-objective NSGA-II"),
        "SBCG_minus_matched_NSGAIII": ("SBCG-NSGA-III", "Matched-objective NSGA-III"),
        "SBCG_minus_noM1": ("SBCG-NSGA-III", "SBCG-NSGA-III-no-M1"),
        "SBCG_minus_noM2": ("SBCG-NSGA-III", "SBCG-NSGA-III-no-M2"),
        "SBCG_minus_noM3": ("SBCG-NSGA-III", "SBCG-NSGA-III-no-M3"),
    }
    output = {}
    for pair, (left, right) in pairs.items():
        for metric in (
            "cond_rec", "correct_escalation", "damage_containment",
            "avoidable_harm", "action_cost", "recovery_cost", "constraint_violation",
        ):
            differences = []
            for seed in sorted({row["seed"] for row in results}):
                a = next((row for row in results if row["algorithm"] == left and row["seed"] == seed), None)
                b = next((row for row in results if row["algorithm"] == right and row["seed"] == seed), None)
                if a is None or b is None:
                    continue
                ma = _metric_values(a["selected_record"])
                mb = _metric_values(b["selected_record"])
                if ma is not None and mb is not None and ma[metric] is not None and mb[metric] is not None:
                    differences.append(ma[metric] - mb[metric])
            output[f"{pair}|{metric}"] = {
                "left": left, "right": right, "metric": metric,
                **_paired_bootstrap(differences),
            }
    return output


def _write_csv_outputs(results, outdir):
    run_fields = [
        "algorithm", "seed", "search_episodes", "diagnostic_episodes",
        "total_simulator_episodes", "unique_evaluations", "cache_hits",
        "search_evaluation_calls", "initial_pool_sha256", "hand_anchor_used",
        "selection_status", "selected_fsm_fingerprint",
        "cond_rec", "correct_escalation", "damage_containment", "avoidable_harm",
        "action_cost", "recovery_cost", "constraint_violation",
    ]
    with (outdir / "d079_train_only_diagnostic_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=run_fields)
        writer.writeheader()
        for result in results:
            metrics = _metric_values(result["selected_record"]) or {}
            writer.writerow({
                "algorithm": result["algorithm"], "seed": result["seed"],
                "search_episodes": result["search_episodes"],
                "diagnostic_episodes": result["diagnostic_episodes"],
                "total_simulator_episodes": result["total_simulator_episodes"],
                "unique_evaluations": result["unique_evaluations"],
                "cache_hits": result["cache_hits"],
                "search_evaluation_calls": result["search_evaluation_calls"],
                "initial_pool_sha256": result["initial_pool_sha256"],
                "hand_anchor_used": result["hand_anchor_used"],
                "selection_status": result["diagnostic_selection"]["status"],
                "selected_fsm_fingerprint": result["selected_fsm_fingerprint"],
                **{field: metrics.get(field) for field in run_fields[12:]},
            })

    scenario_fields = [
        "algorithm", "seed", "scenario_id", "family_id", "difficulty_stratum",
        "robust_label", "analytic_label", "class_success", "task_success",
        "active_effects", "actual_harm", "avoidable_harm", "action_count",
        "decision_count", "duplicate", "duplicate_count", "sla_violation",
        "invariant_violation", "policy_selected_escalation",
    ]
    with (outdir / "d079_train_only_diagnostic_rows.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=scenario_fields)
        writer.writeheader()
        for result in results:
            record = result["selected_record"]
            if record is None:
                continue
            for row in record.metrics.get("rows", []):
                scenario = result["scenario_by_id"][row["scenario_id"]]
                writer.writerow({
                    "algorithm": result["algorithm"], "seed": result["seed"],
                    "scenario_id": row["scenario_id"],
                    "family_id": scenario["task_family_id"],
                    "difficulty_stratum": scenario["difficulty_stratum"],
                    "robust_label": row.get("label"),
                    "analytic_label": result["verdicts"][row["scenario_id"]].get("analytic_class"),
                    "class_success": row.get("class_success"),
                    "task_success": row.get("task_success"),
                    "active_effects": row.get("active_effects"),
                    "actual_harm": row.get("actual_harm"),
                    "avoidable_harm": row.get("avoidable_harm"),
                    "action_count": row.get("action_count"),
                    "decision_count": row.get("decision_count"),
                    "duplicate": row.get("duplicate"),
                    "duplicate_count": row.get("duplicate_count"),
                    "sla_violation": row.get("sla_violation"),
                    "invariant_violation": row.get("invariant_violation"),
                    "policy_selected_escalation": row.get("policy_selected_escalation"),
                })


def _render_report(result):
    lines = [
        "# D-079 locked Train-only algorithm diagnostic",
        "",
        "- Exploratory mechanism diagnostic; not confirmatory and not formal A-3b.",
        f"- Manifest content SHA-256: `{result['manifest_sha256']}`",
        f"- Manifest file SHA-256: `{result['manifest_file_sha256']}`",
        f"- Scenario ID SHA-256: `{result['scenario_ids_sha256']}`",
        f"- Robust label source: {result['label_source']}",
        f"- Runs: {result['run_count']}; search/diagnostic scenarios: {result['search_scenario_count']}/{result['diagnostic_scenario_count']}",
        "- Validation/Test/LLM/A800: not used.",
        "",
        "| Algorithm | Runs | Search episodes | Diagnostic episodes | CondRec | R3 correct | R4 containment | Avoidable harm | Action cost | Constraint violation |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for algorithm, summary in result["arm_summaries"].items():
        def value(field):
            item = summary[field]["mean"]
            return "NA" if item is None else f"{item:.4f}"
        lines.append(
            f"| {algorithm} | {summary['runs']} | {summary['search_episodes']:.1f} | "
            f"{summary['diagnostic_episodes']:.1f} | {value('cond_rec')} | "
            f"{value('correct_escalation')} | {value('damage_containment')} | "
            f"{value('avoidable_harm')} | {value('action_cost')} | {value('constraint_violation')} |"
        )
    lines.extend([
        "",
        "## Paired exploratory contrasts",
        "",
        "Seed-paired differences with 10,000 bootstrap draws are descriptive only; no confirmatory p-values are issued.",
        "",
        "| Contrast | Metric | Mean difference | 95% exploratory bootstrap CI | N seeds |",
        "|---|---|---:|---|---:|",
    ])
    for name, contrast in result["contrasts"].items():
        if contrast["mean"] is None:
            continue
        lines.append(
            f"| {name} | {contrast['metric']} | {contrast['mean']:.6f} | "
            f"[{contrast['ci95'][0]:.6f}, {contrast['ci95'][1]:.6f}] | {contrast['n']} |"
        )
    lines.extend([
        "",
        "These results do not establish EC uplift, Hand superiority, formal A-3b readiness, or Test generalization.",
        "",
    ])
    return "\n".join(lines)


def run_d079_train_only_diagnostic(
    manifest_path,
    lock_path,
    outdir,
    *,
    seeds=(411, 522, 633),
    spec_names=None,
    pop_size=8,
    generations=5,
    initial_pool_size=60,
):
    """Run the registered matrix only after manifest-lock verification passes."""
    lock = json.loads(Path(lock_path).read_text(encoding="utf-8"))
    lock_check = verify_manifest_lock_files(manifest_path, lock)
    if not lock_check["ok"]:
        raise ValueError("manifest lock verification failed: " + "; ".join(lock_check["problems"]))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not (manifest["train_only"] and not manifest["validation_included"] and not manifest["test_included"]):
        raise ValueError("D-079 diagnostic requires a Train-only manifest")

    scenarios = manifest["scenarios"]
    if any(row.get("split") != "train" for row in scenarios):
        raise ValueError("non-Train scenario entered D-079 diagnostic")
    search = [row for row in scenarios if row["evaluation_role"] == "search"]
    diagnostic = [row for row in scenarios if row["evaluation_role"] == "diagnostic"]
    if len(search) != 144 or len(diagnostic) != 144:
        raise ValueError("D-079 requires 144 Search and 144 Diagnostic Train scenarios")
    verdicts = {
        row["scenario_id"]: evaluator_verdict_from_scenario(row)
        for row in scenarios
    }
    if any(item["label_source"] != "observation-based-AND-OR-robust-reachability" for item in verdicts.values()):
        raise ValueError("evaluator verdicts do not use the robust label source")

    specs = algorithm_specs()
    if spec_names is not None:
        names = tuple(spec_names)
        specs = [spec for spec in specs if spec.name in names]
        if len(specs) != len(set(names)) or len(specs) != len(names):
            raise ValueError("unknown or duplicate algorithm selection")
    search_budget = pop_size * (generations + 1) * len(search)
    results = []
    for seed in seeds:
        random_pool = make_shared_initial_pool(seed, size=initial_pool_size, include_hand=False)
        anchored_pool = make_shared_initial_pool(seed, size=initial_pool_size, include_hand=True)
        for spec in specs:
            hand_anchor = bool(
                spec.kind == "sbcg"
                and spec.config.get("use_elite_archive")
                and not spec.config.get("remove_hand_from_pool")
            )
            pool = anchored_pool if hand_anchor else random_pool
            if spec.kind == "fixed":
                candidates = [_fixed_policy(spec.method)]
                search_out = {
                    "episodes": 0, "unique_evaluations": 0,
                    "cache_hits": 0, "evaluation_calls": 0,
                    "history": [], "strata": [], "mutation_audit": [],
                }
            else:
                if spec.kind == "legacy_ea":
                    search_out = run_evolution(
                        spec.method, pool, search, verdicts,
                        pop_size=pop_size, generations=generations,
                        eval_budget=search_budget, seed=seed,
                    )
                elif spec.kind == "sbcg":
                    search_out = run_sbcg_evolution(
                        pool, search, verdicts,
                        pop_size=pop_size, generations=generations,
                        eval_budget=search_budget, seed=seed, **spec.config,
                    )
                else:
                    raise ValueError("unknown algorithm kind")
                candidates = list(search_out.get(
                    "train_candidate_fsms", search_out.get("final_population", [])
                ))
            if search_out["episodes"] > search_budget:
                raise RuntimeError("search episode budget exceeded")
            if not candidates:
                raise RuntimeError("no frozen Search candidates are available for Diagnostic")

            diagnostic_records = [
                evaluate_sbcg_candidate(
                    candidate, diagnostic, verdicts, use_five_objectives=True,
                )
                for candidate in candidates
            ]
            if spec.kind == "fixed":
                selected = diagnostic_records[0]
                selection = {
                    "status": "FIXED_POLICY", "candidate": selected,
                    "rule": "fixed policy; no candidate selection",
                }
            else:
                selection = select_train_diagnostic_candidate(diagnostic_records)
                selected = selection["candidate"]
            selected_metrics = selected.metrics if selected is not None else None
            search_episodes = int(search_out.get("episodes", 0))
            diagnostic_episodes = len(diagnostic_records) * len(diagnostic)
            pool_fingerprints = [fsm_fingerprint(candidate) for candidate in pool]
            result = {
                "algorithm": spec.name,
                "kind": spec.kind,
                "config": dict(spec.config),
                "seed": seed,
                "search_budget": search_budget,
                "search_episodes": search_episodes,
                "diagnostic_episodes": diagnostic_episodes,
                "total_simulator_episodes": search_episodes + diagnostic_episodes,
                "unique_evaluations": search_out.get("unique_evaluations", 0),
                "cache_hits": search_out.get("cache_hits", 0),
                "search_evaluation_calls": search_out.get("evaluation_calls", 0),
                "initial_pool_sha256": _canonical_sha256(pool_fingerprints),
                "hand_anchor_used": hand_anchor,
                "diagnostic_candidate_count": len(diagnostic_records),
                "diagnostic_candidates": [_record_view(record) for record in diagnostic_records],
                "diagnostic_selection": {
                    "status": selection["status"],
                    "candidate": _record_view(selected) if selected is not None else None,
                    "rule": selection["rule"],
                },
                "selected_fsm_fingerprint": selected.fingerprint if selected is not None else None,
                "selected_metrics": selected_metrics,
                "selected_record": selected,
                "history": search_out.get("history", []),
                "strata": search_out.get("strata", []),
                "mutation_audit": search_out.get("mutation_audit", []),
                "scenario_by_id": {row["scenario_id"]: row for row in diagnostic},
                "verdicts": verdicts,
            }
            results.append(result)

    summary_results = []
    for row in results:
        public = dict(row)
        public.pop("selected_record", None)
        public.pop("scenario_by_id", None)
        public.pop("verdicts", None)
        summary_results.append(public)
    output = {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "status": "EXECUTED_TRAIN_ONLY_EXPLORATORY_NO_TEST",
        "manifest_sha256": lock["manifest_content_sha256"],
        "manifest_file_sha256": lock["manifest_file_sha256"],
        "scenario_ids_sha256": lock["scenario_ids_sha256"],
        "lock_version": lock["lock_version"],
        "generator_version": manifest["generator_version"],
        "seed_base": manifest["seed_base"],
        "label_source": "observation-based-AND-OR-robust-reachability",
        "code_sha256": _code_sha256(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True
        ).strip(),
        "seeds": list(seeds),
        "algorithm_count": len(specs),
        "run_count": len(results),
        "scenario_count": len(scenarios),
        "search_scenario_count": len(search),
        "diagnostic_scenario_count": len(diagnostic),
        "population": pop_size,
        "generations": generations,
        "initial_pool_size": initial_pool_size,
        "per_evolutionary_arm_search_episode_budget": search_budget,
        "validation_included": False,
        "test_included": False,
        "test_outcomes_read": False,
        "llm_api_calls": 0,
        "statistical_note": "paired-seed bootstrap intervals are exploratory; no confirmatory p-values",
        "bootstrap_draws": BOOTSTRAP_DRAWS,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "arm_summaries": _arm_summary(results),
        "contrasts": _contrasts(results),
        "results": summary_results,
    }
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "d079_train_only_diagnostic_results.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (outdir / "d079_train_only_diagnostic_report.md").write_text(
        _render_report(output) + "\n", encoding="utf-8"
    )
    _write_csv_outputs(results, outdir)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--seeds", default="411,522,633")
    parser.add_argument("--population", type=int, default=8)
    parser.add_argument("--generations", type=int, default=5)
    parser.add_argument("--initial-pool-size", type=int, default=60)
    args = parser.parse_args()
    result = run_d079_train_only_diagnostic(
        args.manifest, args.lock, args.outdir,
        seeds=tuple(int(value) for value in args.seeds.split(",")),
        pop_size=args.population, generations=args.generations,
        initial_pool_size=args.initial_pool_size,
    )
    print(json.dumps({
        "status": result["status"], "run_count": result["run_count"],
        "algorithm_count": result["algorithm_count"],
        "manifest_sha256": result["manifest_sha256"],
        "search_budget": result["per_evolutionary_arm_search_episode_budget"],
        "outdir": args.outdir, "test_outcomes_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
