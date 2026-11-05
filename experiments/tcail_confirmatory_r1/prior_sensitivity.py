#!/usr/bin/env python3
"""Validation-only prior sensitivity for the TCAIL M2/M3 estimator.

This diagnostic never touches held-out seeds and is not used to select or tune
the confirmatory model.  It repeats the frozen fit on a small validation subset
with half and double fixed-effect prior scales.
"""
from __future__ import annotations

import argparse
import copy
from concurrent.futures import ProcessPoolExecutor
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from experiments.tcail_confirmatory_r1.run_estimator_gate import (
    SCENARIOS, fit_graph, load_config,
)

SCALES = (1.0, 0.5, 2.0)


def _fit(task):
    scale, scenario, seed, config = task
    _, evaluation, _ = fit_graph(seed, scenario, "validation", config)
    return evaluation.loc[:, [
        "seed", "scenario", "pair_i", "pair_j", "parent_id",
        "tcail_q", "tcail_w", "tcail_abstain", "label",
        "direction", "delta_mean_m2", "delta_mean_m3",
    ]].assign(prior_scale=scale)


def scaled_config(config, scale):
    output = copy.deepcopy(config)
    prior = output["estimator"]["fixed_effect_sd_by_order"]
    for key in list(prior):
        prior[key] = float(prior[key]) * scale
    log_sd = output["estimator"]["log_random_effect_sd_prior"]
    log_sd["sd"] = float(log_sd["sd"]) * scale
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="40,41,42")
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/tcail_confirmatory_r1/results/prior_sensitivity"))
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    seeds = [int(value) for value in args.seeds.split(",")]
    args.output.mkdir(parents=True, exist_ok=True)
    base_config = load_config(Path("experiments/tcail_confirmatory_r1/experiment_config.json"))

    tasks = [
        (scale, scenario, seed, scaled_config(base_config, scale))
        for scale in SCALES for scenario in SCENARIOS for seed in seeds
    ]
    if args.jobs > 1:
        for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                         "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            os.environ.setdefault(variable, "1")
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            rows = list(pool.map(_fit, tasks))
    else:
        rows = [_fit(task) for task in tasks]
    for task, result in zip(tasks, rows):
        print(task[0], task[1], task[2], len(result), flush=True)

    frame = pd.concat(rows, ignore_index=True)
    frame.to_csv(args.output / "prior_sensitivity_pairs.csv.gz",
                 index=False, compression="gzip")
    baseline = frame.loc[frame["prior_scale"] == 1.0].set_index(
        ["seed", "scenario", "pair_i", "pair_j", "parent_id"])
    summary = []
    for scale in SCALES:
        other = frame.loc[frame["prior_scale"] == scale].set_index(
            ["seed", "scenario", "pair_i", "pair_j", "parent_id"])
        joined = baseline.join(other, lsuffix="_base", rsuffix="_alt", how="inner")
        shared = joined.dropna(subset=["tcail_q_base", "tcail_q_alt"])
        rho = (
            float(spearmanr(shared["tcail_q_base"], shared["tcail_q_alt"]).statistic)
            if len(shared) > 2 else float("nan")
        )
        selected_base = joined["tcail_q_base"] > 0.8
        selected_alt = joined["tcail_q_alt"] > 0.8
        summary.append({
            "prior_scale": scale,
            "n_pairs": int(len(joined)),
            "q_spearman": rho,
            "mean_abs_q_change": float(np.mean(np.abs(
                joined["tcail_q_alt"] - joined["tcail_q_base"]))),
            "selection_agreement": float(np.mean(selected_base == selected_alt)),
            "base_selected": int(selected_base.sum()),
            "alt_selected": int(selected_alt.sum()),
        })
    pd.DataFrame(summary).to_csv(args.output / "prior_sensitivity_summary.csv", index=False)
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
