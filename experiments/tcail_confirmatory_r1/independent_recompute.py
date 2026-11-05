#!/usr/bin/env python3
"""Independently recompute the frozen estimator-gate headline numbers.

Reads only the per-seed macro CSVs and the held-out pair evaluation, then
recomputes the paired bootstrap and null false-link rate from those files.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("experiments/tcail_confirmatory_r1/results")
DRAWS = 50000
SEED = 20261105


def bootstrap_ci(values, seed, draws=DRAWS):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = np.array([
        rng.choice(values, size=len(values), replace=True).mean()
        for _ in range(draws)
    ])
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def load_macro(method):
    frame = pd.read_csv(ROOT / f"held_out_macro_{method}.csv")
    return frame.set_index(["seed", "scenario"])["auprc"]


def main():
    summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    strongest = summary["strongest_baseline"]
    methods = [path.stem.replace("held_out_macro_", "")
               for path in ROOT.glob("held_out_macro_*.csv")]
    tcail_q = load_macro("tcail_q")
    per_seed = tcail_q.groupby(level="seed").mean()
    baseline = load_macro(strongest).groupby(level="seed").mean()
    common = per_seed.index.intersection(baseline.index)
    differences = (per_seed.loc[common] - baseline.loc[common]).to_numpy()
    overall = {
        "mean_difference": float(np.mean(differences)),
        "ci": bootstrap_ci(differences, SEED),
    }
    scenarios = {}
    for scenario in sorted(tcail_q.index.get_level_values("scenario").unique()):
        t = tcail_q.xs(scenario, level="scenario")
        b = load_macro(strongest).xs(scenario, level="scenario")
        common = t.index.intersection(b.index)
        differences = (t.loc[common] - b.loc[common]).to_numpy()
        scenarios[scenario] = {
            "mean_difference": float(np.mean(differences)),
            "ci": bootstrap_ci(differences, SEED + 1),
        }
    held_out = pd.read_csv(ROOT / "held_out_evaluation_raw.csv")
    null_rows = held_out.loc[held_out["scenario"] == "additive_null"]
    null_false_link = {}
    thresholds = summary["thresholds"]
    for method in methods:
        score_column = method if method.startswith("tcail") else f"{method}_score"
        if score_column not in null_rows:
            continue
        abstain_column = ("tcail_abstain" if method.startswith("tcail")
                          else f"{method}_abstain")
        score = pd.to_numeric(null_rows[score_column], errors="coerce")
        abstain = null_rows[abstain_column].astype("boolean").fillna(True).astype(bool)
        selected = (~abstain) & np.isfinite(score) & (score > thresholds[method])
        selected &= null_rows["support_status"] != "unsupported"
        null_false_link[method] = float(selected.mean())
    report = {
        "strongest_baseline": strongest,
        "n_held_out_seeds": int(len(common)),
        "recomputed_overall": overall,
        "summary_overall": summary["estimator_gate"]["overall_paired_bootstrap_95pct_ci"],
        "recomputed_scenarios": scenarios,
        "summary_scenarios": {
            key: value["ci"]
            for key, value in summary["estimator_gate"]["scenario_results"].items()
        },
        "recomputed_null_false_link": null_false_link,
        "summary_null_false_link": summary["null_false_link"],
        "gate_pass": bool(overall["ci"][0] > 0),
        "status": summary["status"],
    }
    (ROOT / "independent_recompute.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
