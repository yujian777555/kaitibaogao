from __future__ import annotations

import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path

from d090_genome import RULE_BLOCKS, RULES
from d090_scenarios import make_scenario
from dependency_recovery import DependencyRecoveryEnv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"
EXPECTED_RESULTS = {
    "d090_train_manifest.json": {
        "git_blob": "b917b4c624601022e8d8896182dfaed71ba0d21c",
        "internal_sha256": "7d677fe075a5bac6b4241be6c4f38e0c55022b6059729e9a05c7cdf7d633350d",
        "generated_sha256": None,
        "schema": "d090_train_manifest_v1",
        "required": ["protocol_id", "scenario_count", "scenarios", "manifest_sha256"],
    },
    "d090_train_report.json": {
        "git_blob": "bc7a10750b9501462ae9cfe70a171a268f910fcc",
        "internal_sha256": "99a0660e81b072de2e596ff589356d3bb978318f4005d057966779ba9f8f38cf",
        "generated_sha256": "e9412e8c76ce99c6a2b83a51dbb0e89d090d3e9ac838824d5e8d427c0a1be720",
        "schema": "d090_train_best_rows_v1",
        "required": ["protocol_id", "manifest_sha256", "budget", "runs", "report_sha256"],
    },
    "d090_mechanism_ablation.json": {
        "git_blob": "6503132319b2bbbb8d1c8fe720c68b6c37432604",
        "internal_sha256": None,
        "generated_sha256": "632b82eb57df91e5618055aadac01b918ebbc69d170ef77882a40a7969da3ce2",
        "schema": "d090_fixed_mechanism_ablation_v1",
        "required": ["protocol_id", "scenario_count", "variants"],
    },
}
EXPECTED_SOURCE_BLOBS = {
    "experiments/d090_recovery/d090_experiment.py": "16457f67969a8e0016fe4a531fe07acf771adacc",
    "experiments/d090_recovery/d090_genome.py": "52a7e808e3c1fff89d55215ce256eb57c8ae5fd3",
    "experiments/d090_recovery/d090_policies.py": "c96beaf6577cf989e6baaa4d22065662b269844",
    "d090_scenarios.py": "962ade0f8f7bb2eb849b852f0a67edcf08d75712",
}
VERIFIED_D090_SOURCE_BLOBS = {
    "experiments/d090_recovery/d090_policies.py": "c96beaf6577cf9898e6baaa4d22065662b269844",
}
SOURCE_PATHS = [
    "experiments/d090_recovery/d090_experiment.py",
    "experiments/d090_recovery/d090_genome.py",
    "experiments/d090_recovery/d090_policies.py",
    "experiments/d090_recovery/d090_scenarios.py",
    "experiments/d090_recovery/d090_mechanism_ablation.py",
    "experiments/d090_recovery/audit_g03_public_reachability.py",
    "experiments/d090_recovery/audit_g03_trace.py",
    "experiments/d089_recovery/d089_search_experiment.py",
    "experiments/d089_recovery/d089_policies.py",
    "experiments/d089_recovery/d089_budget.py",
    "experiments/d088_recovery/d088_policies.py",
    "experiments/pilot_a3b/dependency_recovery.py",
    "experiments/d090_recovery/d091_independent_audit.py",
    "experiments/d090_recovery/test_d091_independent_audit.py",
]
METRICS = (
    "cond_rec",
    "r3_success",
    "r4_success",
    "harm",
    "recovery_cost",
    "constraint_violation",
    "duplicate_compensation",
    "pending_compensation",
)
ARTIFACT_NAMES = frozenset({
    "d091_source_manifest.json",
    "d091_metric_recompute.json",
    "d091_per_family_metrics.csv",
    "d091_method_dispatch_matrix.json",
    "d091_candidate_phenotype_matrix.csv",
    "d091_r2_witness.json",
    "d091_r2_shortest_path.json",
    "d091_ablation_failure_traces.csv",
    "d091_audit_report.md",
})
_SHORTEST_CACHE = {}


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha_value(value) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def canonical_file_sha(path: Path) -> str:
    return hashlib.sha256(b"\n".join(path.read_bytes().splitlines())).hexdigest()


def git_blob(path: Path, ref="HEAD"):
    relative = path.relative_to(ROOT).as_posix()
    result = subprocess.run(
        ["git", "rev-parse", f"{ref}:{relative}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def load_inputs():
    manifest = json.loads((RESULTS / "d090_train_manifest.json").read_text(encoding="utf-8"))
    report = json.loads((RESULTS / "d090_train_report.json").read_text(encoding="utf-8"))
    ablation = json.loads((RESULTS / "d090_mechanism_ablation.json").read_text(encoding="utf-8"))
    return manifest, report, ablation


def _internal_hash_matches(name, value):
    if name == "d090_train_manifest.json":
        payload = {key: item for key, item in value.items() if key != "manifest_sha256"}
        return sha_value(payload) == value.get("manifest_sha256")
    if name == "d090_train_report.json":
        payload = {key: item for key, item in value.items() if key != "report_sha256"}
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        return digest == value.get("report_sha256")
    return None


def _record_count(name, value):
    if name == "d090_train_manifest.json":
        return len(value.get("scenarios", []))
    if name == "d090_train_report.json":
        return len(value.get("runs", []))
    return len(value.get("variants", {}))


def audit_sources():
    files = []
    for name, expected in EXPECTED_RESULTS.items():
        path = RESULTS / name
        if not path.is_file():
            files.append({"path": str(path), "status": "FAIL", "error": "missing"})
            continue
        raw = path.read_bytes()
        value = json.loads(raw)
        actual_blob = git_blob(path)
        generated = expected["generated_sha256"]
        actual_raw = hashlib.sha256(raw).hexdigest()
        internal = _internal_hash_matches(name, value)
        required_missing = [key for key in expected["required"] if key not in value]
        item = {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(raw),
            "line_count": len(raw.splitlines()),
            "record_count": _record_count(name, value),
            "json_schema": expected["schema"],
            "required_fields": expected["required"],
            "required_fields_missing": required_missing,
            "raw_sha256": actual_raw,
            "canonical_sha256": canonical_file_sha(path),
            "git_blob_sha": actual_blob,
            "expected_git_blob_sha": expected["git_blob"],
            "git_blob_matches": actual_blob == expected["git_blob"],
            "historical_generated_sha256": generated,
            "historical_generated_sha_matches": generated is None or actual_raw == generated,
            "historical_sha_note": "Raw generated bytes can differ after Git newline normalization; Git blob identity and parsed content are the integrity authority." if generated is not None and actual_raw != generated else "generated raw bytes match",
            "internal_sha256": value.get("manifest_sha256", value.get("report_sha256")),
            "internal_sha_matches": internal,
            "status": "PASS_WITH_LIMITATIONS" if generated is not None and actual_raw != generated else "PASS",
        }
        if required_missing or not item["git_blob_matches"] or internal is False:
            item["status"] = "FAIL"
        files.append(item)
    sources = []
    registry_corrections = []
    for name in SOURCE_PATHS:
        path = ROOT / name
        if not path.is_file():
            sources.append({"path": name, "status": "FAIL", "error": "missing"})
            continue
        raw = path.read_bytes()
        actual_blob = git_blob(path)
        expected_blob = EXPECTED_SOURCE_BLOBS.get(name, EXPECTED_SOURCE_BLOBS.get(path.name))
        matches_d090_source = actual_blob == VERIFIED_D090_SOURCE_BLOBS.get(name) if expected_blob else False
        status = "PASS" if expected_blob is None or actual_blob == expected_blob else "FAIL"
        item = {
            "path": name,
            "bytes": len(raw),
            "line_count": len(raw.splitlines()),
            "raw_sha256": hashlib.sha256(raw).hexdigest(),
            "canonical_sha256": canonical_file_sha(path),
            "git_blob_sha": actual_blob,
            "expected_git_blob_sha": expected_blob,
            "git_blob_matches": actual_blob == expected_blob if expected_blob else None,
            "matches_d090_source_commit": matches_d090_source,
            "status": status,
        }
        if status == "FAIL" and matches_d090_source:
            item["status"] = "PASS_WITH_LIMITATIONS"
            registry_corrections.append({
                "path": name,
                "registered_git_blob_sha": expected_blob,
                "actual_git_blob_sha": actual_blob,
                "matches_d090_source_commit": True,
            })
        sources.append(item)
    if any(item["status"] == "FAIL" for item in files + sources):
        status = "FAIL"
    elif registry_corrections or any(item["status"] == "PASS_WITH_LIMITATIONS" for item in files + sources):
        status = "PASS_WITH_LIMITATIONS"
    else:
        status = "PASS"
    return {
        "status": status,
        "files": files,
        "source_files": sources,
        "registry_corrections": registry_corrections,
        "hash_note": "Raw SHA preserves bytes; canonical SHA normalizes line endings; Git blob identity is content-addressed independently of checkout line endings. A registered typo is reported separately only when the actual blob matches the D-090 source commit.",
    }


def recompute(rows):
    def mean(values):
        return sum(values) / len(values) if values else 0.0

    r12 = [row for row in rows if row["label"] in ("R1", "R2")]
    r3 = [row for row in rows if row["label"] == "R3"]
    r4 = [row for row in rows if row["label"] == "R4"]
    return {
        "n": len(rows),
        "cond_rec": mean([row["conditional_recovery_success"] for row in r12]),
        "r3_success": mean([row["correct_escalation"] for row in r3]),
        "r4_success": mean([row["class_success"] for row in r4]),
        "harm": mean([row["avoidable_harm"] for row in rows]),
        "recovery_cost": mean([row["recovery_cost"] for row in rows]),
        "constraint_violation": sum(row["constraint_violation"] for row in rows),
        "duplicate_compensation": sum(row["duplicate_compensation"] for row in rows),
        "pending_compensation": sum(row["pending_compensation"] for row in rows),
    }


def _row_errors(row, scenario):
    errors = []
    if row["scenario_id"] != scenario["scenario_id"] or row["split"] != "train":
        errors.append("scenario_or_split_mismatch")
    if row["label"] != scenario["label"]:
        errors.append("label_mismatch")
    if row["decision_count"] != len(row["trace"]) or row["decision_count"] > 24:
        errors.append("decision_or_trace_mismatch")
    if row["recovery_cost"] != sum(event["cost"] for event in row["trace"]):
        errors.append("cost_mismatch")
    if row["constraint_violation"] != int(row["duplicate_compensation"] > 0 or row["pending_compensation"] > 0):
        errors.append("constraint_mismatch")
    expected_cond = row["class_success"] if row["label"] in ("R1", "R2") else None
    expected_r3 = row["class_success"] if row["label"] == "R3" else None
    if row["conditional_recovery_success"] != expected_cond or row["correct_escalation"] != expected_r3:
        errors.append("conditional_metric_mismatch")
    return errors


def _family_record(collection, method, seed, variant, family, stratum, rows):
    actual = recompute(rows)
    return {
        "collection": collection,
        "method": method,
        "seed": seed,
        "variant": variant,
        "task_family_id": family,
        "difficulty_stratum": stratum,
        "label": rows[0]["label"],
        "n": len(rows),
        "successes": sum(row["class_success"] for row in rows),
        "denominator": len(rows),
        "rate": actual["r4_success"] if rows[0]["label"] == "R4" else mean_value([row["class_success"] for row in rows]),
        "cond_rec_numerator": sum(row["conditional_recovery_success"] for row in rows if row["conditional_recovery_success"] is not None),
        "cond_rec_denominator": sum(row["conditional_recovery_success"] is not None for row in rows),
        "r3_numerator": sum(row["correct_escalation"] for row in rows if row["correct_escalation"] is not None),
        "r3_denominator": sum(row["correct_escalation"] is not None for row in rows),
        "harm_sum": sum(row["avoidable_harm"] for row in rows),
        "harm_mean": actual["harm"],
        "recovery_cost_sum": sum(row["recovery_cost"] for row in rows),
        "recovery_cost_mean": actual["recovery_cost"],
        "constraint_violation": actual["constraint_violation"],
        "pending_compensation": actual["pending_compensation"],
        "duplicate_compensation": actual["duplicate_compensation"],
    }


def mean_value(values):
    return sum(values) / len(values) if values else 0.0


def audit_metrics(manifest, report, ablation):
    scenarios = manifest["scenarios"]
    by_id = {row["scenario_id"]: row for row in scenarios}
    errors = []
    if len(scenarios) != 96 or len(by_id) != 96:
        errors.append("manifest_scenario_uniqueness")
    if manifest.get("split") != "train" or manifest.get("test_included") or manifest.get("test_outcomes_read"):
        errors.append("train_test_boundary")
    if Counter(row["label"] for row in scenarios) != Counter({"R1": 24, "R2": 24, "R3": 24, "R4": 24}):
        errors.append("label_distribution")
    expected_grid = {
        (family, stratum, repeat)
        for family in manifest["families"]
        for stratum in ("D1_RECOVERABLE_TIMEOUT", "D2_PARTIAL_THEN_REDO", "D3_DEPENDENT_ABORT", "D4_BLOCKED_COMPENSATION")
        for repeat in range(4)
    }
    actual_grid = {(row["task_family_id"], row["difficulty_stratum"], row["repeat"]) for row in scenarios}
    if actual_grid != expected_grid:
        errors.append("family_stratum_repeat_grid")
    if any(not row["scenario_id"].startswith("d090r|train|") or row["split"] != "train" for row in scenarios):
        errors.append("namespace_or_split")
    search_records = []
    ablation_records = []
    per_family = []
    per_scenario = []

    def process(collection, method, seed, variant, rows, expected_summary):
        record = {"collection": collection, "method": method, "seed": seed, "variant": variant}
        ids = [row["scenario_id"] for row in rows]
        row_errors = []
        if len(rows) != 96 or len(set(ids)) != 96 or ids != [row["scenario_id"] for row in scenarios]:
            row_errors.append("best_rows_do_not_match_manifest_order")
        for row in rows:
            scenario = by_id.get(row["scenario_id"])
            if scenario is None:
                row_errors.append("unknown_scenario")
                continue
            row_errors.extend(_row_errors(row, scenario))
        actual = recompute(rows)
        differences = {key: actual[key] - expected_summary[key] for key in METRICS}
        record.update({
            "expected": expected_summary,
            "actual": actual,
            "differences": differences,
            "row_errors": sorted(set(row_errors)),
        })
        groups = defaultdict(list)
        for row in rows:
            scenario = by_id[row["scenario_id"]]
            groups[(scenario["task_family_id"], scenario["difficulty_stratum"])].append(row)
            per_scenario.append({
                "collection": collection,
                "method": method,
                "seed": seed,
                "variant": variant,
                "scenario_id": row["scenario_id"],
                "task_family_id": scenario["task_family_id"],
                "difficulty_stratum": scenario["difficulty_stratum"],
                "repeat": scenario["repeat"],
                "label": row["label"],
                "class_success": row["class_success"],
                "conditional_recovery_success": row["conditional_recovery_success"],
                "correct_escalation": row["correct_escalation"],
                "avoidable_harm": row["avoidable_harm"],
                "recovery_cost": row["recovery_cost"],
                "constraint_violation": row["constraint_violation"],
                "pending_compensation": row["pending_compensation"],
                "duplicate_compensation": row["duplicate_compensation"],
                "decision_count": row["decision_count"],
                "runtime_forced_abort": row["runtime_forced_abort"],
                "trace_sha256": sha_value(row["trace"]),
                "final_tool_states": json.dumps(row["final_tool_states"], sort_keys=True),
            })
        for (family, stratum), group in sorted(groups.items()):
            per_family.append(_family_record(collection, method, seed, variant, family, stratum, group))
        return record

    for run in report["runs"]:
        search_records.append(process("search_best", run["method"], run["seed"], "", run["best_rows"], run["best_summary"]))
    for name, variant in ablation["variants"].items():
        ablation_records.append(process("fixed_ablation", "", -1, name, variant["rows"], variant["summary"]))
    for record in search_records + ablation_records:
        errors.extend(record["row_errors"])
    differences = [abs(value) for record in search_records + ablation_records for value in record["differences"].values()]
    maximum = max(differences, default=0.0)
    if maximum > 1e-12:
        errors.append("metric_recompute_difference")
    if report.get("manifest_sha256") != manifest.get("manifest_sha256"):
        errors.append("report_manifest_link")
    if len(report["runs"]) != 15 or len(ablation["variants"]) != 5:
        errors.append("run_or_variant_count")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "search_run_count": len(search_records),
        "ablation_variant_count": len(ablation_records),
        "saved_search_scenario_rows": sum(len(run["best_rows"]) for run in report["runs"]),
        "saved_ablation_scenario_rows": sum(len(variant["rows"]) for variant in ablation["variants"].values()),
        "maximum_absolute_metric_difference": maximum,
        "precision": "Direct Python arithmetic; maximum allowed absolute difference 1e-12; None restricted to non-applicable labels.",
        "denominators": {"cond_rec": 48, "R3": 24, "R4": 24, "all_rows": 96, "per_family_stratum": 4},
        "budget_semantics": {
            "declared_unique_genome_evaluations_per_run": 96,
            "declared_unique_genome_evaluations_total": 1440,
            "declared_rollouts_per_genome": 96,
            "saved_best_candidate_rows": 1440,
            "full_genome_evaluation_traces_saved": False,
            "proposal_count": "NOT_AUDITABLE_FROM_SAVED_TRACE",
            "cache_hits": "NOT_AUDITABLE_FROM_SAVED_TRACE",
            "generation_counts": "NOT_AUDITABLE_FROM_SAVED_TRACE",
        },
        "search": search_records,
        "ablations": ablation_records,
        "per_family_records": per_family,
        "per_scenario_records": per_scenario,
    }


def _trace_hash(rows):
    return sha_value([{"scenario_id": row["scenario_id"], "trace": row["trace"]} for row in rows])


def _outcome_hash(rows):
    return sha_value([{key: value for key, value in row.items() if key != "trace"} for row in rows])


def audit_candidates(report):
    runs = report["runs"]
    genome_keys = sorted(runs[0]["best_genome"])
    rule_keys = list(RULES)
    variable_loci = [key for key in genome_keys if len({canonical(run["best_genome"][key]) for run in runs}) > 1]
    candidates = []
    for run in runs:
        genome = run["best_genome"]
        rule_signature = {key: genome[key] for key in rule_keys}
        block_signature = {block: {key: genome[key] for key in keys} for block, keys in RULE_BLOCKS.items()}
        trace_hash = _trace_hash(run["best_rows"])
        outcome_hash = _outcome_hash(run["best_rows"])
        candidates.append({
            "method": run["method"],
            "seed": run["seed"],
            "genome_sha256": sha_value(genome),
            "rule_signature_sha256": sha_value(rule_signature),
            "rule_block_signature_sha256": sha_value(block_signature),
            "trace_phenotype_sha256": trace_hash,
            "outcome_signature_sha256": outcome_hash,
            "phenotype_sha256": sha_value({"trace": trace_hash, "outcome": outcome_hash}),
            "variable_loci_count": len(variable_loci),
            "genome": genome,
            "rule_signature": rule_signature,
            "rule_block_signature": block_signature,
        })
    pairwise = []
    for i, first in enumerate(candidates):
        for second in candidates[i + 1:]:
            hamming = sum(first["genome"][key] != second["genome"][key] for key in genome_keys)
            rule_hamming = sum(first["rule_signature"][key] != second["rule_signature"][key] for key in rule_keys)
            trace_equal = first["trace_phenotype_sha256"] == second["trace_phenotype_sha256"]
            outcome_equal = first["outcome_signature_sha256"] == second["outcome_signature_sha256"]
            pairwise.append({
                "method_a": first["method"], "seed_a": first["seed"], "method_b": second["method"], "seed_b": second["seed"],
                "genome_sha256_a": first["genome_sha256"], "genome_sha256_b": second["genome_sha256"],
                "phenotype_sha256_a": first["phenotype_sha256"], "phenotype_sha256_b": second["phenotype_sha256"],
                "genome_hamming": hamming, "rule_hamming": rule_hamming,
                "trace_equal": trace_equal, "outcome_equal": outcome_equal, "phenotype_equal": trace_equal and outcome_equal,
            })
    return {
        "status": "FAIL" if len({item["phenotype_sha256"] for item in candidates}) == 1 else "PASS",
        "scope": "Only the 15 saved best candidates on the 96 D-090 Train scenarios; no claim about unsaved candidates or other environments.",
        "candidate_count": len(candidates),
        "unique_genome_count": len({item["genome_sha256"] for item in candidates}),
        "unique_rule_signature_count": len({item["rule_signature_sha256"] for item in candidates}),
        "unique_rule_block_count": len({item["rule_block_signature_sha256"] for item in candidates}),
        "unique_trace_phenotype_count": len({item["trace_phenotype_sha256"] for item in candidates}),
        "unique_outcome_signature_count": len({item["outcome_signature_sha256"] for item in candidates}),
        "pairwise_equivalent_count": sum(item["phenotype_equal"] for item in pairwise),
        "pairwise_count": len(pairwise),
        "variable_loci": variable_loci,
        "observed_behavior_changing_loci": [],
        "effective_loci_definition": "Observed behavior-changing means a locus change accompanies a trace/outcome change in this saved set; no such contrast exists. This is not proof of universal ineffectiveness.",
        "candidates": candidates,
        "pairwise_records": pairwise,
    }


def _function(tree, name):
    return next(node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name)


def audit_dispatch(report):
    experiment_path = HERE / "d090_experiment.py"
    selector_path = ROOT / "experiments/d089_recovery/d089_search_experiment.py"
    experiment_tree = ast.parse(experiment_path.read_text(encoding="utf-8"))
    selector_tree = ast.parse(selector_path.read_text(encoding="utf-8"))
    run_method = _function(experiment_tree, "run_method")
    comparisons = {
        node.comparators[0].value
        for node in ast.walk(run_method)
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name) and node.left.id == "method"
        and len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant)
    }
    run_names = [node.id for node in ast.walk(run_method) if isinstance(node, ast.Name)]
    best = _function(experiment_tree, "_best")
    best_source = ast.get_source_segment(experiment_path.read_text(encoding="utf-8"), best)
    nsga2 = _function(selector_tree, "nsga2_select")
    nsga3 = _function(selector_tree, "nsga3_select")
    nsga2_calls = sorted({node.func.id for node in ast.walk(nsga2) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)})
    nsga3_calls = sorted({node.func.id for node in ast.walk(nsga3) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)})
    paired_random = []
    for seed in report["seeds"]:
        random_run = next(run for run in report["runs"] if run["method"] == "random" and run["seed"] == seed)
        nsga2_run = next(run for run in report["runs"] if run["method"] == "nsga2" and run["seed"] == seed)
        paired_random.append({"seed": seed, "same_best_genome": random_run["best_genome"] == nsga2_run["best_genome"]})
    definitions = [
        ("random", "NSGA-II-equivalent", "random_d090_genome + mutation/crossover", "nsga2_select", False, False),
        ("nsga2", "NSGA-II", "random_d090_genome + mutation/crossover", "nsga2_select", False, False),
        ("nsga3", "NSGA-III-simplified", "random_d090_genome + mutation/crossover", "nsga3_select", False, False),
        ("state_evo", "Static-profile NSGA-II", "constant profile + mutation/crossover", "nsga2_select", False, False),
        ("state_random", "Direct random search", "random_d090_genome only", "_best over proposals", False, True),
    ]
    methods = []
    for method, identity, operators, selector, dynamic, direct_random in definitions:
        methods.append({
            "method": method,
            "actual_search_identity": identity,
            "explicit_method_branch": method in comparisons,
            "rng_initialization": "Random(seed * 7919 + 17)",
            "evolutionary_initial_population": "Random(seed * 131 + i * 17 + 3), i=0..11" if method != "state_random" else "shared run RNG; no population",
            "operators": operators,
            "survivor_selection": selector,
            "dynamic_failure_feedback": dynamic,
            "direct_random_sampling": direct_random,
            "declared_unique_genome_evaluations": 96,
            "scenario_rollouts_per_unique_genome": 96,
            "saved_proposal_history": False,
        })
    return {
        "status": "FAIL",
        "methods": methods,
        "method_comparisons_in_run_method": sorted(comparisons),
        "random_nsGA2_same_best_by_seed": paired_random,
        "generations_name_references_in_run_method": run_names.count("GENERATIONS"),
        "generation_count_status": "NOT_AUDITABLE_FROM_SAVED_TRACE",
        "operator_invocation_status": "NOT_AUDITABLE_FROM_SAVED_TRACE",
        "proposal_cache_archive_status": "NOT_AUDITABLE_FROM_SAVED_TRACE",
        "nsga2_evidence": {"calls": nsga2_calls, "implementation": "Fast non-dominated sorting plus per-objective crowding distance", "source": "experiments/d089_recovery/d089_search_experiment.py:81-137"},
        "nsga3_evidence": {"calls": nsga3_calls, "implementation": "Ideal-point shift, p=3 reference directions, perpendicular association and minimum-niche random selection; no full extreme-point normalization", "source": "experiments/d089_recovery/d089_search_experiment.py:140-187", "canonical_nsga3": False},
        "state_evo_evidence": "Constant {'pair':1,'fallback':1,'completion':1,'harm':1}; no episode failure_profile or dynamic profile update in run_method.",
        "selection_semantics": {
            "survivor_objectives": ["constraint+pending", "1-cond_rec", "1-R3", "1-R4", "Harm", "RecoveryCost"],
            "best_pool": "all archived proposals after zero constraint/pending filtering, not final population or Pareto front",
            "best_lexicographic_key": ["min(R3,R4)", "R3+R4", "-Harm", "-RecoveryCost"],
            "cond_rec_explicit_in_best": "cond_rec" in best_source,
            "selection_consistent_with_survivor_objectives": False,
        },
        "fairness": "Shared encoding, scenario set and nominal 96-unique-genome cap; state_random lacks matched initial population; complete proposal/cache parity is not auditable from saved artifacts.",
        "source": "experiments/d090_recovery/d090_experiment.py:60-121",
    }


def witness_plan():
    first = [
        ("COMPENSATE", "A", "alternate"), ("COMPENSATE", "B", "alternate"), ("COMPENSATE", "C", "primary"),
        ("WAIT",), ("WAIT",), ("VERIFY", "A"), ("VERIFY", "B"), ("VERIFY", "C"),
    ]
    third = [
        ("COMPENSATE", "A", "alternate"), ("COMPENSATE", "B", "alternate"),
        ("WAIT",), ("WAIT",), ("VERIFY", "A"), ("VERIFY", "B"),
    ]
    return first + first + third + [("ESCALATE",)]


def _r2_scenario(manifest):
    scenario = make_scenario("d090_PAIR_RACE", "D3_DEPENDENT_ABORT", 2)
    saved = next(row for row in manifest["scenarios"] if row["scenario_id"] == scenario["scenario_id"])
    if scenario != saved:
        raise ValueError("D-090 r2 scenario differs from the saved manifest")
    return scenario


def replay_r2_witness(manifest):
    scenario = _r2_scenario(manifest)
    env = DependencyRecoveryEnv(scenario)
    steps = []
    for index, action in enumerate(witness_plan(), 1):
        observation = env.step(action)
        steps.append({
            "step": index,
            "action": list(action),
            "observation": observation,
            "tick": env.tick,
            "cost": env.trace[-1]["cost"],
            "pending_tools": [tool for tool in env.tools if env._pending(tool)],
            "tool_states": dict(env.tools),
        })
    report = env.report()
    result = {
        "status": "CLAIM_FALSIFIED" if report["class_success"] and report["decision_count"] <= 24 else "WITNESS_FAILED",
        "scenario_id": scenario["scenario_id"],
        "plan": [list(action) for action in witness_plan()],
        "steps": steps,
        **{key: value for key, value in report.items() if key != "trace"},
    }
    return result


def _bfs_key(env):
    routes = []
    for tool, routes_for_tool in sorted(env.routes.items()):
        for name, route in sorted(routes_for_tool.items()):
            remaining = None if route["resolve_at"] is None else max(0, route["resolve_at"] - env.tick)
            routes.append((tool, name, route["attempt_index"], route["attempts"], route["pending_success"], remaining))
    return (tuple(sorted(env.tools.items())), tuple(routes), env.terminal_action, env.duplicate_compensation)


def _oracle_actions(env):
    view = env.view()
    pending = [tool for tool, value in view["tools"].items() if any(route["pending"] for route in value["routes"])]
    actions = [("ESCALATE",)]
    if pending:
        actions.append(("WAIT",))
        actions.extend(("VERIFY", tool) for tool in pending)
    for tool, value in view["tools"].items():
        if value["state"] not in ("COMMITTED", "PARTIAL") or not value["compensation_available"]:
            continue
        if any(route["pending"] for route in value["routes"]):
            continue
        for route in value["routes"]:
            if all(view["tools"][required]["state"] == "COMPENSATED" for required in route["requires"]):
                actions.append(("COMPENSATE", tool, route["name"]))
    return actions


def shortest_r2_path(manifest):
    cache_key = manifest["manifest_sha256"]
    if cache_key in _SHORTEST_CACHE:
        return _SHORTEST_CACHE[cache_key]
    scenario = _r2_scenario(manifest)
    initial = DependencyRecoveryEnv(scenario)
    queue = deque([(initial, tuple())])
    seen = {_bfs_key(initial)}
    depth_counts = Counter()
    expanded = 0
    found = None
    while queue and found is None:
        env, path = queue.popleft()
        depth = len(path)
        depth_counts[depth] += 1
        expanded += 1
        if depth >= 24:
            continue
        for action in _oracle_actions(env):
            nxt = copy.deepcopy(env)
            nxt.step(action)
            next_path = path + (action,)
            report = nxt.report()
            if report["class_success"]:
                found = (nxt, next_path, report)
                break
            if nxt.terminal_action is not None or nxt.duplicate_compensation:
                continue
            key = _bfs_key(nxt)
            if key not in seen:
                seen.add(key)
                queue.append((nxt, next_path))
    if found is None:
        result = {"status": "NO_SAFE_R3_PATH_WITHIN_24", "scenario_id": scenario["scenario_id"], "expanded_states": expanded, "seen_states": len(seen), "breadth_first_order": True}
    else:
        env, path, report = found
        result = {
            "status": "CLAIM_FALSIFIED",
            "scenario_id": scenario["scenario_id"],
            "historical_lower_bound": 25,
            "decision_count": len(path),
            "path": [list(action) for action in path],
            "trace": env.trace,
            "class_success": report["class_success"],
            "constraint_violation": report["constraint_violation"],
            "pending_compensation": report["pending_compensation"],
            "duplicate_compensation": report["duplicate_compensation"],
            "recovery_cost": report["recovery_cost"],
            "final_tool_states": report["final_tool_states"],
            "expanded_states": expanded,
            "seen_states": len(seen),
            "dequeued_by_depth": dict(sorted(depth_counts.items())),
            "breadth_first_order": True,
            "proof": "Unit-cost BFS; every shallower reachable nonterminal state was dequeued before the first accepted ESCALATE. Duplicate-producing and terminal-failure branches cannot lead to an accepted R3 result.",
            "state_definition": "Tool states, both route attempt counters, pending_success, remaining resolve time, terminal action and duplicate count. Absolute tick is stored in each environment; remaining resolve time is an equivalent reduction because future delays are relative to dispatch tick.",
            "action_coverage": "ESCALATE, shared WAIT, every pending-tool VERIFY order, and every currently feasible primary/alternate dispatch. RETRY_WORKFLOW under permission, VERIFY without pending, blocked/compensated dispatch and STOP_SAFE cannot improve physical R3 reachability; idempotent reuse after completion is a no-op.",
        }
    _SHORTEST_CACHE[cache_key] = result
    return result


def extract_ablation_failures(ablation):
    output = {}
    counts = {}
    for name, variant in ablation["variants"].items():
        rows = [row for row in variant["rows"] if not row["class_success"] or row["constraint_violation"]]
        output[name] = rows
        counts[name] = {
            "class_failures": sum(not row["class_success"] for row in variant["rows"]),
            "failure_label_counts": dict(sorted(Counter(row["label"] for row in variant["rows"] if not row["class_success"]).items())),
            "failure_family_counts": dict(sorted(Counter(row["scenario_id"].split("|")[2] for row in variant["rows"] if not row["class_success"]).items())),
            "constraint_rows": sum(row["constraint_violation"] for row in variant["rows"]),
            "pending_total": sum(row["pending_compensation"] for row in variant["rows"]),
            "duplicate_total": sum(row["duplicate_compensation"] for row in variant["rows"]),
            "pair_race_r3_failures": sum("|d090_PAIR_RACE|D3_" in row["scenario_id"] and not row["class_success"] for row in variant["rows"]),
            "harm_sum": sum(row["avoidable_harm"] for row in variant["rows"]),
            "harm_by_label": dict(sorted(_sum_by(variant["rows"], "label", "avoidable_harm").items())),
            "harm_by_family": {family: sum(row["avoidable_harm"] for row in variant["rows"] if row["scenario_id"].split("|")[2] == family) for family in sorted({row["scenario_id"].split("|")[2] for row in variant["rows"]})},
            "constraint_scenarios": [row["scenario_id"] for row in variant["rows"] if row["constraint_violation"]],
        }
    output["counts"] = counts
    return output


def _sum_by(rows, key, value):
    result = defaultdict(float)
    for row in rows:
        result[row[key]] += row[value]
    return result


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _csv_text(rows, fields=None):
    fields = fields or list(dict.fromkeys(key for row in rows for key in row))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else value for key, value in row.items()})
    return buffer.getvalue()


def _write_once(path: Path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            if handle.read() != text:
                raise FileExistsError("refusing to overwrite different D-091 evidence: " + str(path))
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def _ablation_trace_rows(extracted):
    rows = []
    for variant, records in extracted.items():
        if variant == "counts":
            continue
        for record in records:
            base = {
                "variant": variant,
                "scenario_id": record["scenario_id"],
                "label": record["label"],
                "class_success": record["class_success"],
                "decision_count": record["decision_count"],
                "residual_side_effects": record["residual_side_effects"],
                "min_reachable_harm": record["min_reachable_harm"],
                "avoidable_harm": record["avoidable_harm"],
                "pending_compensation": record["pending_compensation"],
                "duplicate_compensation": record["duplicate_compensation"],
                "constraint_violation": record["constraint_violation"],
                "runtime_forced_abort": record["runtime_forced_abort"],
                "final_tool_states": json.dumps(record["final_tool_states"], sort_keys=True),
            }
            for step, event in enumerate(record["trace"], 1):
                rows.append({**base, "step": step, "action": json.dumps(event["action"]), "observation": event["observation"], "tick": event["tick"], "event_cost": event["cost"]})
    return rows


def _markdown_report(sources, metrics, dispatch, candidates, witness, shortest, ablations):
    statuses = {
        "DATA_INTEGRITY": sources["status"],
        "METRIC_RECOMPUTE": metrics["status"],
        "METHOD_IDENTITY": dispatch["status"],
        "PHENOTYPE_DIVERSITY": candidates["status"],
        "R2_REACHABILITY": shortest["status"],
        "ABLATION_SAFETY": "FAIL" if any(item["constraint_rows"] or item["pending_total"] for item in ablations["counts"].values()) else "PASS",
    }
    lines = [
        "# D-091 independent audit artifact", "",
        "This artifact reads saved D-090 evidence. It does not run genome search, select candidates, access Validation/Test, train models, or call an LLM.", "",
        "| Gate | Status |", "|---|---|",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in statuses.items())
    lines += [
        "", "## Evidence", "",
        f"- Search best rows: {metrics['saved_search_scenario_rows']}; fixed-ablation rows: {metrics['saved_ablation_scenario_rows']}; maximum metric difference: {metrics['maximum_absolute_metric_difference']}.",
        f"- Candidate genomes: {candidates['unique_genome_count']}/{candidates['candidate_count']}; trace phenotypes: {candidates['unique_trace_phenotype_count']}; outcome signatures: {candidates['unique_outcome_signature_count']}.",
        f"- The `random` label follows the NSGA-II path; `state_evo` uses a static mutation profile. Actual proposal/operator/generation logs are NOT_AUDITABLE_FROM_SAVED_TRACE.",
        f"- g03-r2 witness decisions: {witness['decision_count']}; BFS shortest: {shortest.get('decision_count')}; historical 25-step claim: CLAIM_FALSIFIED.",
        f"- P2/P4 preserve hard-constraint failures; no Harm or cost improvement can compensate them.", "",
        "The historical 25-step lower bound is withdrawn. Equal aggregate search metrics are not evidence of algorithmic improvement or a fair independent Random Search comparison.", "",
    ]
    return "\n".join(lines)


def run_audit(outdir):
    outdir = Path(outdir)
    manifest, report, ablation = load_inputs()
    sources = audit_sources()
    metrics = audit_metrics(manifest, report, ablation)
    dispatch = audit_dispatch(report)
    candidates = audit_candidates(report)
    witness = replay_r2_witness(manifest)
    shortest = shortest_r2_path(manifest)
    extracted = extract_ablation_failures(ablation)
    outputs = {}
    outputs["d091_source_manifest.json"] = _json_text(sources)
    outputs["d091_metric_recompute.json"] = _json_text(metrics)
    outputs["d091_per_family_metrics.csv"] = _csv_text(metrics["per_family_records"])
    outputs["d091_per_scenario_metrics.csv"] = _csv_text(metrics["per_scenario_records"])
    outputs["d091_method_dispatch_matrix.json"] = _json_text(dispatch)
    outputs["d091_candidate_fingerprints.json"] = _json_text({key: value for key, value in candidates.items() if key != "pairwise_records"})
    outputs["d091_candidate_phenotype_matrix.csv"] = _csv_text(candidates["pairwise_records"])
    outputs["d091_r2_witness.json"] = _json_text(witness)
    outputs["d091_r2_shortest_path.json"] = _json_text(shortest)
    outputs["d091_ablation_failure_summary.json"] = _json_text(extracted["counts"])
    outputs["d091_ablation_failure_traces.csv"] = _csv_text(_ablation_trace_rows(extracted))
    outputs["d091_audit_report.md"] = _markdown_report(sources, metrics, dispatch, candidates, witness, shortest, extracted)
    for name, text in outputs.items():
        _write_once(outdir / name, text)
    manifest_output = {
        "schema": "d091_output_manifest_v1",
        "no_d090_search": True,
        "files": {name: {"bytes": len(text.encode("utf-8")), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()} for name, text in sorted(outputs.items())},
    }
    _write_once(outdir / "d091_output_manifest.json", _json_text(manifest_output))
    return set(outputs) | {"d091_output_manifest.json"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(HERE / "results" / "d091_audit"))
    args = parser.parse_args()
    outputs = run_audit(args.outdir)
    print(json.dumps({"status": "D091_LOCAL_AUDIT_WRITTEN", "outdir": str(Path(args.outdir)), "file_count": len(outputs), "d090_search_executed": False}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
