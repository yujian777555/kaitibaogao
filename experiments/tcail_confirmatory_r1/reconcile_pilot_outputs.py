#!/usr/bin/env python3
"""Check independently recomputed metrics against the original pilot summaries."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path,
                        default=Path("experiments/tcail_confirmatory_r1/r1a_original_code"))
    args = parser.parse_args()
    root = args.root
    checks = {}
    for kind in ["estimator", "fbl"]:
        original = json.loads((root / kind / "summary.json").read_text())
        recomputed = json.loads((root / kind / "recomputed.json").read_text())
        source = original["test"] if kind == "estimator" else original["heldout"]
        ap_key = "ap" if kind == "estimator" else "auprc"
        brier_key = "brier" if kind == "estimator" else "brier_q"
        paired_key = ("paired_ap_q_eb_minus_zscore" if kind == "estimator"
                      else "paired_seed_ap_difference_q_minus_fbl")
        for metric, expected in source[ap_key].items():
            actual = recomputed[ap_key][metric]
            assert abs(actual - expected) <= 1e-12, (kind, metric, actual, expected)
        for metric, expected in source[brier_key].items():
            actual = recomputed[brier_key][metric]
            assert abs(actual - expected) <= 1e-12, (kind, metric, actual, expected)
        assert np.allclose(source[paired_key]["bootstrap_95pct_ci"],
                           recomputed[paired_key]["bootstrap_95pct_ci"],
                           atol=1e-12, rtol=0)
        checks[kind] = {"summary_metrics_match": True, "bootstrap_ci_match": True}

    fbl = json.loads((root / "fbl" / "recomputed.json").read_text())
    audit = fbl["raw_four_cell_audit"]
    assert audit["cell_contrast_max_abs_error"] == 0
    assert audit["mean_contrast_max_abs_error"] <= 1e-12
    assert audit["gate_identity_max_abs_error"] <= 1e-12
    checks["fbl"]["raw_four_cell_audit"] = audit

    original = json.loads((root / "oracle" / "summary.json").read_text())
    recomputed = json.loads((root / "oracle" / "recomputed.json").read_text())
    for landscape in ["trap4", "additive"]:
        for method, expected in original[landscape]["by_method"].items():
            actual = recomputed["landscapes"][landscape]["by_method"][method]
            for key in ["n", "mean_best", "sd_best", "median_best", "successes",
                        "mean_evaluations_used"]:
                assert abs(actual[key] - expected[key]) <= 1e-12, (
                    landscape, method, key, actual[key], expected[key])
    for comparator, expected in original["trap4"]["paired"].items():
        actual = recomputed["landscapes"]["trap4"]["paired"][comparator]
        for key in ["mean_paired_difference", "median_paired_difference",
                    "wins_ties_losses", "exact_sign_test_one_sided_p",
                    "wilcoxon_signed_rank_one_sided_p", "paired_bootstrap_95pct_ci"]:
            if isinstance(expected[key], list):
                assert np.allclose(actual[key], expected[key], atol=1e-12, rtol=0), (
                    comparator, key)
            else:
                assert abs(actual[key] - expected[key]) <= 1e-12, (comparator, key)
    checks["oracle"] = {
        "summary_and_paired_statistics_match": True,
        "budget_audit": recomputed["budget_audit"],
    }

    for kind in ["oracle", "estimator", "fbl"]:
        raw = root / kind / ("per_seed_results.csv" if kind == "oracle"
                             else "per_pair_context_raw.csv")
        checks[kind]["raw_sha256"] = hashlib.sha256(raw.read_bytes()).hexdigest()
    output = root / "reconciliation.json"
    output.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
