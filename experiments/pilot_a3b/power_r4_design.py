"""R4 10,000-replicate ICC/power re-calibration for the frozen 34/40 x 5 design.

Uses only the historical diagnostic development input to estimate a residual
pool and total variance. It does not load or inspect the locked Test payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

import power_hierarchical as ph

ICC_GRID_R4 = (0.0, 0.05, 0.10, 0.20)
FAMILY_GRID_R4 = (33, 34, 40)
COMPOSITIONS_PER_FAMILY_R4 = 5
MDE_R4 = 0.10
ALPHA_R4 = 0.05
DEFAULT_REPS = 10000
DEFAULT_SEED = 20261114
MISSING_RATE_GRID = (0.0, 0.01, 0.02, 0.05)
TYPE_I_REPLICATES = 5


def wilson_interval(successes, trials, z=1.959963984540054):
    if trials < 1:
        raise ValueError("trials must be positive")
    p = successes / trials
    denom = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denom
    half = z * math.sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denom
    return [max(0.0, center - half), min(1.0, center + half)]


def simulate_power_grid(total_var, eps_pool, reps=DEFAULT_REPS, seed=DEFAULT_SEED):
    """Run null Type-I and MDE power for F={33,34,40}, m=5 and ICC grid."""
    if reps < 100:
        raise ValueError("R4 power simulation requires at least 100 replicates")
    residuals = np.asarray(eps_pool, dtype=float).reshape(-1)
    if residuals.size < 2 or not np.all(np.isfinite(residuals)):
        raise ValueError("empirical residual pool must contain at least two finite values")
    if not math.isfinite(total_var) or total_var <= 0:
        raise ValueError("total variance must be finite and positive")

    cells = []
    for n_families in FAMILY_GRID_R4:
        for icc in ICC_GRID_R4:
            for mu, role in ((0.0, "null_type_i"), (MDE_R4, "mde_power")):
                cell_seed = (
                    int(seed)
                    + n_families * 100000
                    + int(round(icc * 1000)) * 100
                    + int(round(mu * 10000))
                )
                rng = np.random.default_rng(cell_seed)
                family_means, overflow = ph.gen_family_means_hier(
                    rng,
                    reps,
                    n_families,
                    COMPOSITIONS_PER_FAMILY_R4,
                    icc,
                    mu,
                    total_var,
                    residuals,
                )
                p_values = ph._pvals_student_t(family_means)
                rejections = int(np.count_nonzero(p_values < ALPHA_R4))
                rate = rejections / reps
                cells.append({
                    "n_families": n_families,
                    "compositions_per_family": COMPOSITIONS_PER_FAMILY_R4,
                    "icc": icc,
                    "mu": mu,
                    "role": role,
                    "confirmatory_eligible": n_families >= 34,
                    "mc_reps": reps,
                    "random_seed": cell_seed,
                    "rejections": rejections,
                    "rejection_rate": rate,
                    "mcse": math.sqrt(max(rate * (1.0 - rate), 0.0) / reps),
                    "ci95_wilson": wilson_interval(rejections, reps),
                    "out_of_range_rate": overflow,
                })
    return cells



def simulate_missing_sensitivity(
    total_var, eps_pool, reps=DEFAULT_REPS, seed=DEFAULT_SEED,
    missing_rates=MISSING_RATE_GRID,
):
    """MCAR composition-cluster technical-missing sensitivity.

    A family is retained only when all five primary composition clusters are
    complete, matching the frozen R4 missing-data rule. The t test is run only
    when at least 34 complete families remain.
    """
    residuals = np.asarray(eps_pool, dtype=float).reshape(-1)
    if residuals.size < 2 or not np.all(np.isfinite(residuals)):
        raise ValueError("empirical residual pool must contain at least two finite values")
    cells = []
    for n_families in (34, 40):
        for missing_rate in missing_rates:
            if not 0.0 <= missing_rate < 1.0:
                raise ValueError("missing rates must be in [0, 1)")
            for mu, role in ((0.0, "null_type_i"), (MDE_R4, "mde_power")):
                cell_seed = int(seed) + 7000000 + n_families * 10000 + int(missing_rate * 10000) * 10 + int(mu * 1000)
                rng = np.random.default_rng(cell_seed)
                family_means, overflow = ph.gen_family_means_hier(
                    rng, reps, n_families, COMPOSITIONS_PER_FAMILY_R4,
                    0.20, mu, total_var, residuals,
                )
                composition_observed = rng.random(
                    (reps, n_families, COMPOSITIONS_PER_FAMILY_R4)
                ) >= missing_rate
                family_complete = composition_observed.all(axis=2)
                complete_counts = family_complete.sum(axis=1)
                eligible = complete_counts >= 34
                rejected = np.zeros(reps, dtype=bool)
                for observed_f in sorted(set(int(v) for v in complete_counts[eligible])):
                    row_indices = np.flatnonzero(complete_counts == observed_f)
                    samples = np.vstack([
                        family_means[row_index, family_complete[row_index]]
                        for row_index in row_indices
                    ])
                    p_values = ph._pvals_student_t(samples)
                    rejected[row_indices] = p_values < ALPHA_R4
                eligible_n = int(eligible.sum())
                conditional_rate = (
                    float(rejected[eligible].mean()) if eligible_n else None
                )
                joint_rate = float(rejected.mean())
                eligibility_rate = float(eligible.mean())
                cells.append({
                    "n_families_design": n_families,
                    "compositions_per_family": COMPOSITIONS_PER_FAMILY_R4,
                    "icc": 0.20,
                    "missing_rate_per_composition_cluster": float(missing_rate),
                    "mu": mu,
                    "role": role,
                    "mc_reps": reps,
                    "random_seed": cell_seed,
                    "mean_complete_families": float(complete_counts.mean()),
                    "analysis_eligibility_rate": eligibility_rate,
                    "analysis_eligibility_mcse": math.sqrt(
                        max(eligibility_rate * (1.0 - eligibility_rate), 0.0) / reps
                    ),
                    "conditional_rejection_rate_when_eligible": conditional_rate,
                    "joint_rejection_rate": joint_rate,
                    "eligible_replicates": eligible_n,
                    "out_of_range_rate": overflow,
                })
    return cells


def simulate_type_i_replication(
    total_var, eps_pool, reps=DEFAULT_REPS, seed=DEFAULT_SEED,
    n_replicates=TYPE_I_REPLICATES,
):
    """Independent-seed replication of the previously high F=40 / ICC=.20 null cell."""
    residuals = np.asarray(eps_pool, dtype=float).reshape(-1)
    if n_replicates < 2:
        raise ValueError("at least two independent Type-I replicates are required")
    cells = []
    total_rejections = 0
    total_trials = 0
    for replicate in range(n_replicates):
        cell_seed = int(seed) + 90000000 + replicate * 1000003
        rng = np.random.default_rng(cell_seed)
        means, overflow = ph.gen_family_means_hier(
            rng, reps, 40, COMPOSITIONS_PER_FAMILY_R4,
            0.20, 0.0, total_var, residuals,
        )
        p_values = ph._pvals_student_t(means)
        rejections = int(np.count_nonzero(p_values < ALPHA_R4))
        rate = rejections / reps
        total_rejections += rejections
        total_trials += reps
        cells.append({
            "replicate": replicate + 1,
            "n_families": 40,
            "icc": 0.20,
            "mu": 0.0,
            "role": "null_type_i_replication",
            "mc_reps": reps,
            "random_seed": cell_seed,
            "rejections": rejections,
            "rejection_rate": rate,
            "mcse": math.sqrt(max(rate * (1.0 - rate), 0.0) / reps),
            "ci95_wilson": wilson_interval(rejections, reps),
            "out_of_range_rate": overflow,
        })
    pooled_rate = total_rejections / total_trials
    return {
        "n_replicates": n_replicates,
        "total_mc_reps": total_trials,
        "total_rejections": total_rejections,
        "pooled_type_i": pooled_rate,
        "pooled_mcse": math.sqrt(pooled_rate * (1.0 - pooled_rate) / total_trials),
        "pooled_ci95_wilson": wilson_interval(total_rejections, total_trials),
        "cells": cells,
        "missing_rate_grid": list(MISSING_RATE_GRID),
        "missing_sensitivity": missing_sensitivity,
        "type_i_replication": type_i_replication,
    }


def json_input_hashes(input_path):
    """Record raw-byte and canonical-content hashes for cross-platform audit."""
    raw = Path(input_path).read_bytes()
    parsed = json.loads(raw)
    canonical = json.dumps(
        parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return {
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "canonical_sha256": hashlib.sha256(canonical).hexdigest(),
    }


def extract_empirical_variance(input_path):
    """Estimate pilot total variance and within-family residual pool."""
    hashes = json_input_hashes(input_path)
    hierarchy = ph.build_hierarchy(input_path)
    if hierarchy["problems"]:
        raise ValueError("historical diagnostic hierarchy failed: " + "; ".join(hierarchy["problems"]))
    all_cluster_means = []
    residuals = []
    for family, compositions in hierarchy["families"].items():
        family_mean = hierarchy["fam_means"][family]
        for item in compositions.values():
            value = float(item["mean_diff"])
            all_cluster_means.append(value)
            residuals.append(value - family_mean)
    total_var = float(np.var(np.asarray(all_cluster_means, dtype=float), ddof=1))
    return {
        "input_sha256": hashes["raw_sha256"],
        "input_canonical_sha256": hashes["canonical_sha256"],
        "total_var": total_var,
        "residual_pool": residuals,
        "n_diagnostic_families": len(hierarchy["families"]),
        "n_diagnostic_clusters": len(all_cluster_means),
        "diagnostic_family_means": hierarchy["fam_means"],
    }


def render_report(result):
    lines = [
        "# D-064-R4 — ICC / Type-I / power re-calibration",
        "",
        f"- Input raw SHA-256: {result['input_sha256']}",
        f"- Input canonical-content SHA-256: {result['input_canonical_sha256']}",
        f"- Code commit: {result['git_commit']}",
        f"- Repetitions per cell: {result['mc_reps']}",
        f"- Base seed: {result['base_seed']}",
        f"- Pilot total variance: {result['total_var']:.8f}",
        f"- Empirical residual pool size: {result['residual_pool_size']}",
        "- Design: 5 frozen primary compositions/family; F=33 boundary, F=34 minimum eligible, F=40 planned",
        "",
        "## Results",
        "",
        "| F | ICC | Role | μ | Rejection rate | MCSE | 95% Wilson CI | Eligible |",
        "|---:|---:|---|---:|---:|---:|---|---|",
    ]
    for cell in result["cells"]:
        ci = cell["ci95_wilson"]
        lines.append(
            f"| {cell['n_families']} | {cell['icc']:.2f} | {cell['role']} | "
            f"{cell['mu']:.2f} | {cell['rejection_rate']:.4f} | {cell['mcse']:.4f} | "
            f"[{ci[0]:.4f}, {ci[1]:.4f}] | {cell['confirmatory_eligible']} |"
        )
    lines.extend([
        "",
        "## Technical-missing sensitivity (MCAR at composition-cluster level)",
        "",
        "| F design | Missing rate | Role | Mean complete F | Eligibility rate | Conditional rejection when eligible | Joint rejection rate |",
        "|---:|---:|---|---:|---:|---:|---:|",
    ])
    for cell in result.get("missing_sensitivity", []):
        conditional = "NA" if cell["conditional_rejection_rate_when_eligible"] is None else f'{cell["conditional_rejection_rate_when_eligible"]:.4f}'
        lines.append(
            f'| {cell["n_families_design"]} | {cell["missing_rate_per_composition_cluster"]:.2%} | '
            f'{cell["role"]} | {cell["mean_complete_families"]:.2f} | '
            f'{cell["analysis_eligibility_rate"]:.4f} | {conditional} | {cell["joint_rejection_rate"]:.4f} |'
        )
    replication = result.get("type_i_replication", {})
    pooled_ci = replication.get("pooled_ci95_wilson")
    if pooled_ci:
        lines.extend([
            "",
            "## Independent-seed Type-I replication (F=40, ICC=0.20, null)",
            "",
            f'- Replicates: {replication["n_replicates"]} × {replication["cells"][0]["mc_reps"]:,} MC',
            f'- Pooled Type-I: {replication["pooled_type_i"]:.4f}',
            f'- Pooled 95% Wilson CI: [{pooled_ci[0]:.4f}, {pooled_ci[1]:.4f}]',
        ])
    lines.extend([
        "",
        "## Interpretation limits",
        "",
        "- F=33 cells are boundary sensitivity only and are not confirmatory-eligible.",
        "- Type-I cells use μ=0; power cells use the proposed absolute MDE=0.10.",
        "- ICC values are imposed sensitivity scenarios, not estimates from six diagnostic families.",
        "- Variance and residual shape are calibrated from the historical six-family diagnostic input; this is a pilot-based simulation assumption, not independent evidence of the true population distribution.",
        "- This simulation does not inspect Test labels/results and does not authorize formal A-3b.",
        "",
    ])
    return "\n".join(lines)


def run(input_path, outdir, reps=DEFAULT_REPS, seed=DEFAULT_SEED):
    empirical = extract_empirical_variance(input_path)
    cells = simulate_power_grid(empirical["total_var"], empirical["residual_pool"], reps, seed)
    missing_sensitivity = simulate_missing_sensitivity(
        empirical["total_var"], empirical["residual_pool"], reps, seed
    )
    type_i_replication = simulate_type_i_replication(
        empirical["total_var"], empirical["residual_pool"], reps, seed
    )
    result = {
        "kind": "D064_R4_POWER_RECALIBRATION",
        "status": "SIMULATION_ONLY_NOT_PREREGISTRATION_APPROVAL",
        "input_sha256": empirical["input_sha256"],
        "input_canonical_sha256": empirical["input_canonical_sha256"],
        "git_commit": ph.git_sha(),
        "base_seed": int(seed),
        "mc_reps": int(reps),
        "total_var": empirical["total_var"],
        "residual_pool_size": len(empirical["residual_pool"]),
        "n_diagnostic_families": empirical["n_diagnostic_families"],
        "n_diagnostic_clusters": empirical["n_diagnostic_clusters"],
        "family_grid": list(FAMILY_GRID_R4),
        "composition_count": COMPOSITIONS_PER_FAMILY_R4,
        "icc_grid": list(ICC_GRID_R4),
        "mde": MDE_R4,
        "alpha": ALPHA_R4,
        "cells": cells,
    }
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "power_r4_design.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (outdir / "power_r4_design_report.md").write_text(
        render_report(result) + "\n", encoding="utf-8"
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(Path(__file__).with_name("diagnostic3_results.json")))
    parser.add_argument("--outdir", default=str(Path(__file__).parent))
    parser.add_argument("--reps", type=int, default=DEFAULT_REPS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    result = run(args.input, args.outdir, args.reps, args.seed)
    print("R4 power cells:", len(result["cells"]))
    print("input_sha256:", result["input_sha256"])
    for cell in result["cells"]:
        print(cell["n_families"], cell["icc"], cell["role"],
              round(cell["rejection_rate"], 4), cell["ci95_wilson"])


if __name__ == "__main__":
    main()
