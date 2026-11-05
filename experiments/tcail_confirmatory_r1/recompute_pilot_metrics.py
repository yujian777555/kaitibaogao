#!/usr/bin/env python3
"""Independently recompute pilot metrics from raw CSV outputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score


def average_precision(rows, column):
    return float(average_precision_score(rows["label"].astype(int), rows[column].astype(float)))


def paired_bootstrap(differences, seed, draws):
    rng = np.random.default_rng(seed)
    boot = np.asarray([
        rng.choice(differences, size=len(differences), replace=True).mean()
        for _ in range(draws)
    ])
    return [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]


def paired_summary(differences, seed, draws):
    differences = np.asarray(differences, dtype=float)
    wins = int(np.sum(differences > 0))
    losses = int(np.sum(differences < 0))
    return {
        "mean": float(differences.mean()),
        "mean_paired_difference": float(differences.mean()),
        "median": float(np.median(differences)),
        "median_paired_difference": float(np.median(differences)),
        "wins_ties_losses": [wins, int(np.sum(differences == 0)), losses],
        "sign_test_one_sided_p": float(stats.binomtest(
            wins, wins + losses, 0.5, alternative="greater").pvalue),
        "exact_sign_test_one_sided_p": float(stats.binomtest(
            wins, wins + losses, 0.5, alternative="greater").pvalue),
        "wilcoxon_signed_rank_one_sided_p": float(stats.wilcoxon(
            differences, alternative="greater", zero_method="wilcox").pvalue),
        "bootstrap_95pct_ci": paired_bootstrap(differences, seed, draws),
        "paired_bootstrap_95pct_ci": paired_bootstrap(differences, seed, draws),
    }


def recompute_estimator_summary(csv_path):
    rows = pd.read_csv(csv_path)
    test = rows[(rows["supported"] == 1) & rows["q_eb"].notna()].copy()
    per_seed = []
    for seed, group in test.groupby("seed", sort=True):
        per_seed.append({
            "seed": int(seed),
            "ap_q_eb": average_precision(group, "q_eb"),
            "ap_w_eb": average_precision(group, "w_eb"),
            "ap_zscore": average_precision(group, "zscore"),
            "ap_raw": average_precision(group, "raw"),
            "ap_pooled": average_precision(group, "pooled_abs"),
        })
    differences = np.asarray([
        row["ap_q_eb"] - row["ap_zscore"] for row in per_seed
    ])
    return {
        "n_supported_pair_contexts": int(len(test)),
        "positive_labels": int(test["label"].sum()),
        "ap": {
            "eb_q": average_precision(test, "q_eb"),
            "eb_w": average_precision(test, "w_eb"),
            "student_t_q": average_precision(test, "q_student"),
            "student_t_w": average_precision(test, "w_student"),
            "local_zscore": average_precision(test, "zscore"),
            "local_raw_abs_contrast": average_precision(test, "raw"),
            "context_pooled_abs_contrast": average_precision(test, "pooled_abs"),
        },
        "brier": {
            "eb_q": float(np.mean((test["q_eb"] - test["label"]) ** 2)),
            "student_t_q": float(np.mean((test["q_student"] - test["label"]) ** 2)),
        },
        "low_support_ap_eb_q": average_precision(test[test["n_blocks"] == 8], "q_eb"),
        "full_support_ap_eb_q": average_precision(test[test["n_blocks"] == 128], "q_eb"),
        "per_seed_ap": per_seed,
        "paired_ap_q_eb_minus_zscore": paired_summary(differences, 777, 20000),
    }


def recompute_fbl_summary(csv_path):
    rows = pd.read_csv(csv_path)
    test = rows[(rows["supported"] == 1) & rows["q_eb"].notna()
                & rows["fbl_calibrated"].notna()].copy()
    per_seed = []
    for seed, group in test.groupby("seed", sort=True):
        record = {
            "seed": int(seed),
            "ap_q_eb": average_precision(group, "q_eb"),
            "ap_fbl_scaled": average_precision(group, "fbl_calibrated"),
            "ap_zscore": average_precision(group, "zscore"),
        }
        if "fbl_abs_ungated" in group:
            record["ap_fbl_abs_ungated"] = average_precision(group, "fbl_abs_ungated")
            record["ap_fbl_abs_epsilon_zero"] = average_precision(group, "fbl_abs_epsilon_zero")
            valid = group["fbl_paper_domain_violation"] == 0
            record["ap_fbl_paper_signed"] = average_precision(
                group[valid], "fbl_paper_signed")
            record["paper_valid_n"] = int(valid.sum())
        per_seed.append(record)
    differences = np.asarray([
        row["ap_q_eb"] - row["ap_fbl_scaled"] for row in per_seed
    ])
    cell_errors = []
    mean_errors = []
    gate_errors = []
    for _, row in test.iterrows():
        outcomes = np.asarray([
            [int(value) for value in block.split(",")]
            for block in row["block_cell_outcomes"].split(";")
        ], dtype=int)
        contrasts = outcomes[:, 3] - outcomes[:, 1] - outcomes[:, 2] + outcomes[:, 0]
        recorded = np.asarray([int(value) for value in row["block_contrasts"].split(";")])
        cell_errors.append(float(np.max(np.abs(contrasts - recorded))))
        mean_errors.append(abs(float(contrasts.mean()) - float(row["mean_d"])))
        conditional_0 = outcomes[:, 1] - outcomes[:, 0]
        conditional_1 = outcomes[:, 3] - outcomes[:, 2]
        gate_errors.append(abs(
            abs(float(conditional_1.mean() - conditional_0.mean()))
            - abs(float(row["mean_d"]))
        ))
    result = {
        "n_supported_pair_contexts": int(len(test)),
        "positive_labels": int(test["label"].sum()),
        "auprc": {
            "eb_q": average_precision(test, "q_eb"),
            "eb_w": average_precision(test, "w_eb"),
            "scaled_fbl_adaptation": average_precision(test, "fbl_calibrated"),
            "student_t_q": average_precision(test, "q_student"),
            "local_zscore": average_precision(test, "zscore"),
            "local_raw_contrast": average_precision(test, "raw"),
            "context_pooled": average_precision(test, "pooled_abs"),
        },
        "brier_q": {
            "eb_q": float(np.mean((test["q_eb"] - test["label"]) ** 2)),
            "student_t_q": float(np.mean((test["q_student"] - test["label"]) ** 2)),
        },
        "low_support_eb_q_auprc": average_precision(test[test["n_blocks"] == 8], "q_eb"),
        "full_support_eb_q_auprc": average_precision(test[test["n_blocks"] == 128], "q_eb"),
        "per_seed": per_seed,
        "paired_seed_ap_difference_q_minus_fbl": paired_summary(differences, 20261104, 20000),
        "raw_four_cell_audit": {
            "n_blocks_recomputed": int(sum(len(row.split(";")) for row in test["block_contrasts"])),
            "cell_contrast_max_abs_error": float(max(cell_errors)),
            "mean_contrast_max_abs_error": float(max(mean_errors)),
            "gate_identity_max_abs_error": float(max(gate_errors)),
        },
    }
    if "fbl_abs_ungated" in test:
        result["auprc"]["scaled_fbl_abs_ungated"] = average_precision(test, "fbl_abs_ungated")
        result["auprc"]["scaled_fbl_abs_epsilon_zero"] = average_precision(test, "fbl_abs_epsilon_zero")
        paper_scores = []
        for _, row in test.iterrows():
            delta_i = float(row["mean_i_j0"])
            delta_ij = float(row["mean_i_j1"])
            if delta_i == 0.0 and delta_ij == 0.0:
                score = 0.0
            elif delta_i >= delta_ij:
                score = 1.0 - delta_ij / delta_i if delta_i != 0.0 else float("nan")
            else:
                score = 1.0 - delta_i / delta_ij if delta_ij != 0.0 else float("nan")
            paper_scores.append(score)
        paper_scores = np.asarray(paper_scores)
        recorded = test["fbl_paper_signed"].to_numpy(dtype=float)
        valid = np.isfinite(paper_scores) & (paper_scores >= 0) & (paper_scores < 1)
        assert np.allclose(paper_scores[np.isfinite(paper_scores)],
                           recorded[np.isfinite(paper_scores)], atol=1e-12, rtol=0)
        assert np.array_equal(valid, test["fbl_paper_domain_violation"].to_numpy(dtype=int) == 0)
        result["auprc"]["fbl_paper_signed_valid_only"] = average_precision(
            test.loc[valid], "fbl_paper_signed")
        result["fbl_paper_signed_domain"] = {
            "valid_n": int(valid.sum()), "total_supported_n": int(len(test)),
            "violation_n": int((~valid).sum()),
        }
    return result


def recompute_oracle_summary(csv_path):
    rows = pd.read_csv(csv_path)
    output = {}
    for landscape, group in rows.groupby("landscape", sort=True):
        methods = {}
        for method, method_rows in group.groupby("method", sort=True):
            best = method_rows["best"].to_numpy(dtype=float)
            methods[method] = {
                "n": int(len(method_rows)),
                "mean_best": float(best.mean()),
                "sd_best": float(best.std(ddof=1)),
                "median_best": float(np.median(best)),
                "successes": int(method_rows["success"].sum()),
                "mean_evaluations_used": float(method_rows["evaluations"].mean()),
            }
        paired = {}
        if landscape == "trap4":
            wide = group.pivot(index="seed", columns="method", values="best")
            for comparator in ["learned_lt", "random", "singleton"]:
                paired[comparator] = paired_summary(
                    (wide["oracle"] - wide[comparator]).to_numpy(), 20261104, 30000)
        output[landscape] = {"by_method": methods, "paired": paired}
    budget_audit = {
        "minimum_evaluations": int(rows["evaluations"].min()),
        "maximum_evaluations": int(rows["evaluations"].max()),
        "all_include_at_least_initial_population": bool((rows["evaluations"] >= 50).all()),
    }
    if "initial_population_hash" in rows:
        budget_audit["same_initial_population_within_seed_and_landscape"] = bool(
            rows.groupby(["landscape", "seed"])["initial_population_hash"].nunique().eq(1).all())
    return {"landscapes": output, "budget_audit": budget_audit}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["estimator", "fbl", "oracle"], required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    functions = {
        "estimator": recompute_estimator_summary,
        "fbl": recompute_fbl_summary,
        "oracle": recompute_oracle_summary,
    }
    result = functions[args.kind](args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
