#!/usr/bin/env python3
"""Seed-level confirmatory metrics; no held-out tuning is performed here."""
from __future__ import annotations
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score


def average_precision(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    valid = np.isfinite(scores) & np.isfinite(labels)
    labels = labels[valid]
    scores = scores[valid]
    if len(labels) == 0:
        return float("nan")
    if np.sum(labels) == 0:
        return 0.0
    return float(average_precision_score(labels, scores))


def expected_calibration_error(labels, probabilities, bins=10):
    labels = np.asarray(labels, dtype=float)
    probabilities = np.asarray(probabilities, dtype=float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    error = 0.0
    for index in range(bins):
        if index == bins - 1:
            mask = (probabilities >= edges[index]) & (probabilities <= edges[index + 1])
        else:
            mask = (probabilities >= edges[index]) & (probabilities < edges[index + 1])
        if np.any(mask):
            error += np.mean(mask) * abs(np.mean(labels[mask]) - np.mean(probabilities[mask]))
    return float(error)


def calibration_summary(labels, probabilities):
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    valid = np.isfinite(probabilities)
    labels = labels[valid]
    probabilities = probabilities[valid]
    if len(labels) == 0:
        return {"brier": float("nan"), "ece": float("nan"),
                "calibration_intercept": float("nan"), "calibration_slope": float("nan")}
    result = {
        "brier": float(np.mean((probabilities - labels) ** 2)),
        "ece": expected_calibration_error(labels, probabilities),
    }
    if len(np.unique(labels)) < 2:
        result.update({"calibration_intercept": float("nan"),
                       "calibration_slope": float("nan")})
        return result
    logits = np.log(np.clip(probabilities, 1e-6, 1 - 1e-6)
                    / (1 - np.clip(probabilities, 1e-6, 1 - 1e-6)))
    model = LogisticRegression(penalty=None, solver="lbfgs", max_iter=1000)
    model.fit(logits.reshape(-1, 1), labels)
    result["calibration_intercept"] = float(model.intercept_[0])
    result["calibration_slope"] = float(model.coef_[0, 0])
    return result


def risk_coverage(labels, probabilities, supported, abstain, thresholds=None):
    labels = np.asarray(labels, dtype=int)
    probabilities = np.asarray(probabilities, dtype=float)
    supported = np.asarray(supported, dtype=bool)
    abstain = np.asarray(abstain, dtype=bool)
    if thresholds is None:
        thresholds = np.linspace(0.0, 1.0, 101)
    rows = []
    for threshold in thresholds:
        selected = supported & ~abstain & (probabilities >= threshold)
        count = int(selected.sum())
        rows.append({
            "threshold": float(threshold),
            "coverage": float(np.mean(selected)),
            "selected": count,
            "false_selected": int(np.sum(selected & (labels == 0))),
            "risk": float(np.sum(selected & (labels == 0)) / max(count, 1)),
        })
    return rows


def macro_auprc_by_seed(frame, score_column):
    rows = []
    for (seed, scenario), group in frame.groupby(["seed", "scenario"], sort=True):
        rows.append({
            "seed": seed, "scenario": scenario,
            "auprc": average_precision(group["label"], group[score_column]),
            "n": int(len(group)), "positive_n": int(group["label"].sum()),
        })
    detail = rows
    macro = []
    for seed, group in frame.groupby("seed", sort=True):
        scenario_values = [row["auprc"] for row in detail if row["seed"] == seed]
        macro.append({"seed": seed, "macro_auprc": float(np.mean(scenario_values))})
    return detail, macro


def paired_bootstrap_ci(differences, seed=20261105, draws=50000, level=0.95):
    differences = np.asarray(differences, dtype=float)
    rng = np.random.default_rng(seed)
    boot = np.asarray([
        rng.choice(differences, size=len(differences), replace=True).mean()
        for _ in range(draws)
    ])
    alpha = (1 - level) / 2
    return [float(np.quantile(boot, alpha)), float(np.quantile(boot, 1 - alpha))]


def select_strongest_baseline(validation_macro_by_method):
    methods = sorted(validation_macro_by_method)
    means = {
        method: float(np.mean(validation_macro_by_method[method]))
        for method in methods
    }
    strongest = max(methods, key=lambda method: (means[method], -methods.index(method)))
    return {"method": strongest, "validation_mean_macro_auprc": means[strongest],
            "all_validation_means": means}
