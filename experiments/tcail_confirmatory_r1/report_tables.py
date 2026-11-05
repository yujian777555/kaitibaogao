#!/usr/bin/env python3
"""Render markdown tables from the frozen estimator-gate outputs."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path("experiments/tcail_confirmatory_r1/results")


def fmt(value, digits=3):
    if value is None:
        return "NA"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def main():
    summary = json.loads((ROOT / "summary.json").read_text(encoding="utf-8"))
    stage = json.loads((ROOT / "stage_summary.json").read_text(encoding="utf-8"))
    gate = summary["estimator_gate"]
    lines = []
    lines.append("### Overall estimator gate\n")
    lines.append("| Quantity | Value |")
    lines.append("|---|---|")
    lines.append(f"| Strongest validation baseline | {summary['strongest_baseline']} |")
    lines.append(f"| Held-out seeds | {summary['seed_counts']['held_out']} |")
    lines.append(f"| Mean macro-AUPRC difference | {fmt(gate['overall_mean_difference'], 4)} |")
    lines.append(f"| Paired 95% CI | [{fmt(gate['overall_paired_bootstrap_95pct_ci'][0], 4)}, "
                 f"{fmt(gate['overall_paired_bootstrap_95pct_ci'][1], 4)}] |")
    lines.append(f"| Key scenarios not significantly worse | {gate['key_scenarios_not_significantly_worse']} |")
    lines.append(f"| Gate | {summary['status']} |")
    lines.append("")
    lines.append("### Per-scenario paired differences\n")
    lines.append("| Scenario | Mean difference | 95% CI |")
    lines.append("|---|---|---|")
    for scenario, result in gate["scenario_results"].items():
        lines.append(f"| {scenario} | {fmt(result['mean_difference'], 4)} | "
                     f"[{fmt(result['ci'][0], 4)}, {fmt(result['ci'][1], 4)}] |")
    lines.append("")
    lines.append("### Held-out macro-AUPRC by method\n")
    lines.append("| Method | Mean | Scenario means |")
    lines.append("|---|---|---|")
    for method, value in sorted(stage["overall_macro_auprc"].items(),
                                key=lambda item: -item[1]):
        scen = stage["scenario_auprc"][method]
        scen_text = ", ".join(f"{key}={fmt(val, 3)}" for key, val in scen.items())
        lines.append(f"| {method} | {fmt(value, 4)} | {scen_text} |")
    lines.append("")
    lines.append("### Null false-link rate (held-out additive/null)\n")
    lines.append("| Method | Rate |")
    lines.append("|---|---|")
    for method, value in sorted(summary["null_false_link"].items()):
        lines.append(f"| {method} | {fmt(value, 4)} |")
    lines.append("")
    lines.append("### Calibration of TCAIL q\n")
    lines.append("| Brier | ECE | Intercept | Slope |")
    lines.append("|---|---|---|---|")
    cal = summary["calibration"]
    lines.append(f"| {fmt(cal['brier'], 4)} | {fmt(cal['ece'], 4)} | "
                 f"{fmt(cal['calibration_intercept'], 3)} | {fmt(cal['calibration_slope'], 3)} |")
    lines.append("")
    lines.append("### FOS recovery (mean over held-out seed/parent/module)\n")
    lines.append("| Method | Precision | Recall | F1 | False merge | VI |")
    lines.append("|---|---|---|---|---|---|")
    for row in sorted(summary["FOS_recovery"], key=lambda item: -item["f1"]):
        lines.append(f"| {row['method']} | {fmt(row['precision'], 3)} | {fmt(row['recall'], 3)} | "
                     f"{fmt(row['f1'], 3)} | {fmt(row['false_merge_rate'], 3)} | "
                     f"{fmt(row['variation_of_information'], 3)} |")
    lines.append("")
    lines.append("### Fit quality\n")
    lines.append("| Model | Fit ok | PPC extreme rate | Mean seconds |")
    lines.append("|---|---|---|---|")
    for row in summary["fit_quality"]:
        lines.append(f"| M{int(row['model_order'])} | {fmt(row['fit_ok'], 3)} | "
                     f"{fmt(row['ppc_extreme_rate'], 3)} | {fmt(row['mean_seconds'], 2)} |")
    lines.append("")
    output = ROOT / "report_tables.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
