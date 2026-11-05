#!/usr/bin/env python3
"""Post-hoc failure diagnostics for the failed estimator gate.

These analyses reuse the frozen held-out predictions.  They are explicitly
EXPLORATORY: they were computed after the confirmatory gate was unblinded and
must not be used to claim a gate pass.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

ROOT = Path("experiments/tcail_confirmatory_r1/results")
SEED = 20261105
DRAWS = 50000


def bootstrap_ci(values, seed):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array([
        rng.choice(values, size=len(values), replace=True).mean()
        for _ in range(DRAWS)
    ])
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main():
    evaluation = pd.read_csv(ROOT / "held_out_evaluation_raw.csv")
    evaluation = evaluation.loc[evaluation["support_status"] != "unsupported"].copy()
    t_abstain = evaluation["tcail_abstain"].fillna(True).astype(bool)
    s_abstain = evaluation["standardized_abstain"].fillna(True).astype(bool)

    def rank(values, abstain):
        values = pd.to_numeric(values, errors="coerce")
        return np.where((~abstain) & np.isfinite(values), values, -1.0)

    variants = {
        "q_min": (evaluation["tcail_q"], t_abstain),
        "q_m2": (evaluation["q_m2"], t_abstain),
        "q_m3": (evaluation["q_m3"], t_abstain),
        "q_max": (np.maximum(evaluation["q_m2"], evaluation["q_m3"]), t_abstain),
        "standardized": (evaluation["standardized_score"], s_abstain),
    }
    rows = []
    for (seed, scenario), group in evaluation.groupby(["seed", "scenario"]):
        for name, (values, abstain) in variants.items():
            score = rank(values, abstain)[group.index]
            rows.append({
                "seed": seed, "scenario": scenario, "variant": name,
                "auprc": average_precision_score(group["label"], score),
            })
    per_scenario = pd.DataFrame(rows)
    pivot = per_scenario.pivot_table(
        index=["seed", "scenario"], columns="variant", values="auprc")
    comparisons = {}
    for name in ("q_min", "q_m2", "q_m3", "q_max"):
        differences = (pivot[name] - pivot["standardized"]).groupby(
            level=0).mean().dropna().to_numpy()
        comparisons[name] = {
            "mean_difference_vs_standardized": float(np.mean(differences)),
            "ci": bootstrap_ci(differences, SEED),
        }

    evaluation["support_stratum"] = np.where(
        evaluation["n_block"] <= 32, "<=32",
        np.where(evaluation["n_block"] <= 128, "33-128", ">128"))
    strata_rows = []
    for (seed, scenario, stratum), group in evaluation.groupby(
            ["seed", "scenario", "support_stratum"]):
        if group["label"].sum() in (0, len(group)):
            continue
        strata_rows.append({
            "seed": seed, "scenario": scenario, "stratum": stratum,
            "tcail": average_precision_score(
                group["label"], rank(group["tcail_q"], t_abstain.loc[group.index])),
            "standardized": average_precision_score(
                group["label"], rank(group["standardized_score"],
                                      s_abstain.loc[group.index])),
        })
    strata = pd.DataFrame(strata_rows).groupby("stratum")[
        ["tcail", "standardized"]].mean()

    abstention = {
        "by_scenario": evaluation.groupby("scenario")["tcail_abstain"].mean().round(4).to_dict(),
        "by_support_stratum": evaluation.groupby(
            "support_stratum")["tcail_abstain"].mean().round(4).to_dict(),
        "q_m2_m3_conflict_rate": float(
            (evaluation["tcail_abstain_reason"].fillna("")
             .str.contains("MODEL_ORDER_SIGN_CONFLICT")).mean()),
    }

    report = {
        "status": "EXPLORATORY_POST_HOC",
        "warning": "Not a confirmatory result; must not be used to claim gate pass.",
        "q_variant_comparisons": comparisons,
        "variant_scenario_means": per_scenario.groupby(
            ["variant", "scenario"])["auprc"].mean().unstack().round(4).to_dict(),
        "support_strata_auprc": strata.round(4).to_dict(),
        "abstention": abstention,
    }
    (ROOT / "posthoc_diagnostics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
