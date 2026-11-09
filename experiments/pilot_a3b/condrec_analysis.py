"""CondRecSucc primary-endpoint analysis for diagnostic3 (D-064-A).

ESTIMAND (frozen to 64_A3B_PREREGISTRATION_CANDIDATE.md section 3):
  CondRecSucc = mean of class_success over R1+R2 scenarios ONLY.
  R3 -> CorrectEscalation; R4 -> DamageContainment; never mixed into the
  primary endpoint.

INDEPENDENCE HIERARCHY (cluster = task x fault-composition):
  1. pair AB and NSGA-II within (scenario, seed);
  2. average paired values over seeds inside each scenario (seeds are nested
     repeats, NOT independent samples);
  3. aggregate scenarios within each cluster (equal-weight cluster mean);
  4. overall effect = equal-weight mean over valid clusters.
  Scenario-weighted aggregate is reported as a sensitivity.

PRE-SPECIFIED RULE for clusters with zero R1/R2 denominator: EXCLUDED from
the primary estimand, registered as 'r34_only_clusters' with their identity;
never filled with zeros and never silently dropped.

All numbers are recomputed from raw rows; no summary values are hardcoded.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
BOOT_REPS = 4000
SIGNFLIP_REPS = 8000
BOOT_SEED = 20261110


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=str(HERE)).stdout.strip()
    except Exception:
        return "unknown"


def load_runs(input_path):
    raw = Path(input_path).read_bytes()
    data = json.loads(raw)
    return data, hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------
# integrity checks (Task B)
# ---------------------------------------------------------------------------
def integrity_checks(data, method_a="AB", method_b="nsga2"):
    problems = []
    seen = set()
    per_ms = defaultdict(set)
    scen_meta = {}
    for run in data["runs"]:
        m, s = run["method"], run["seed"]
        for row in run["rows"]:
            key = (m, s, row["scenario_id"])
            if key in seen:
                problems.append(f"duplicate episode {key}")
            seen.add(key)
            per_ms[(m, s)].add(row["scenario_id"])
            sid = row["scenario_id"]
            if sid in scen_meta:
                if scen_meta[sid] != (row["task"], row["composition"], row["split"]):
                    problems.append(f"cluster metadata mismatch for {sid}")
            else:
                scen_meta[sid] = (row["task"], row["composition"], row["split"])
    seeds = sorted({s for (m, s) in per_ms if m == method_a})
    for s in seeds:
        if per_ms.get((method_a, s)) != per_ms.get((method_b, s)):
            problems.append(f"scenario sets differ between {method_a}/{method_b} at seed {s}")
    # seed coverage uniformity
    for s in seeds:
        for m in (method_a, method_b):
            if (m, s) not in per_ms:
                problems.append(f"missing run {m}/{s}")
    return {
        "n_episode_rows": len(seen),
        "seeds": seeds,
        "n_scenarios": len(scen_meta),
        "problems": problems,
    }


# ---------------------------------------------------------------------------
# primary endpoint extraction (Tasks A, B, C)
# ---------------------------------------------------------------------------
def endpoint_table(data, method_a="AB", method_b="nsga2"):
    """Return per-scenario paired means, per-cluster aggregates, diagnostics."""
    # scenario -> method -> seed -> class_success (R1/R2 only)
    prim = defaultdict(lambda: defaultdict(dict))
    meta = {}
    r3 = defaultdict(lambda: defaultdict(dict))
    r4 = defaultdict(lambda: defaultdict(dict))
    for run in data["runs"]:
        m, s = run["method"], run["seed"]
        for row in run["rows"]:
            sid = row["scenario_id"]
            meta[sid] = (row["task"], row["composition"], row["split"], row["label"])
            lab, cs = row["label"], row["class_success"]
            if lab in ("R1", "R2"):
                prim[sid][m][s] = cs
            elif lab == "R3":
                r3[sid][m][s] = cs
            elif lab == "R4":
                r4[sid][m][s] = cs

    # pairing completeness per scenario
    scenarios = sorted(prim)
    missing = []
    sc_effect = {}      # scenario -> paired seed-mean difference (a - b)
    sc_den = {}         # scenario -> label class
    for sid in scenarios:
        a, b = prim[sid].get(method_a, {}), prim[sid].get(method_b, {})
        common = sorted(set(a) & set(b))
        lost = (set(a) ^ set(b))
        if lost:
            missing.append({"scenario_id": sid, "unpaired_seeds": sorted(lost)})
        vals = [a[k] - b[k] for k in common if a[k] is not None and b[k] is not None]
        if vals:
            sc_effect[sid] = sum(vals) / len(vals)
            sc_den[sid] = meta[sid][3]

    # cluster aggregation (equal weight)
    clusters = defaultdict(list)
    for sid, eff in sc_effect.items():
        clusters[(meta[sid][0], meta[sid][1])].append(eff)

    # ALL clusters in the design (including zero-denominator ones)
    all_clusters = {(t, c) for (t, c, _sp, _lab) in meta.values()}
    r12_clusters = set(clusters)
    zero_denom = sorted(all_clusters - r12_clusters)

    cluster_rows = []
    for key in sorted(clusters):
        effs = clusters[key]
        cluster_rows.append({
            "cluster": f"{key[0]}|{key[1]}",
            "n_r12_scenarios": len(effs),
            "mean_paired_diff": sum(effs) / len(effs),
            "n_r12_rows_a": sum(1 for sid in sc_effect
                                if (meta[sid][0], meta[sid][1]) == key and meta[sid][3] in ("R1", "R2")),
        })

    vals = [c["mean_paired_diff"] for c in cluster_rows]
    n = len(vals)
    mean = sum(vals) / n if n else None
    sd = (sum((x - mean) ** 2 for x in vals) / (n - 1)) ** 0.5 if n > 1 else 0.0

    # scenario-weighted sensitivity
    sw_mean = (sum(sc_effect.values()) / len(sc_effect)) if sc_effect else None

    # per-method CondRecSucc (R1+R2, cluster-equal-weight of cluster means)
    def method_rate(method):
        cl_m = defaultdict(list)
        for sid in scenarios:
            per = prim[sid].get(method, {})
            vals_m = [v for v in per.values() if v is not None]
            if vals_m:
                cl_m[(meta[sid][0], meta[sid][1])].append(sum(vals_m) / len(vals_m))
        rates = [sum(v) / len(v) for v in cl_m.values()]
        return sum(rates) / len(rates) if rates else None

    # cluster bootstrap CI (cluster as resampling unit)
    rng = random.Random(BOOT_SEED)
    boot = []
    for _ in range(BOOT_REPS):
        if not vals:
            break
        sample = [vals[rng.randrange(n)] for _ in range(n)]
        boot.append(sum(sample) / len(sample))
    boot.sort()
    ci = [boot[int(0.025 * (len(boot) - 1))], boot[int(0.975 * (len(boot) - 1))]] if boot else [None, None]

    # REAL cluster-level sign-flip test (Monte Carlo over sign vectors)
    rng2 = random.Random(BOOT_SEED + 1)
    if vals:
        obs = abs(mean)
        extreme = 0
        for _ in range(SIGNFLIP_REPS):
            ssum = 0.0
            for v in vals:
                ssum += v if rng2.random() < 0.5 else -v
            if abs(ssum / n) >= obs - 1e-15:
                extreme += 1
        p = (extreme + 1) / (SIGNFLIP_REPS + 1)
    else:
        p = None

    return {
        "primary_eligible_clusters": n,
        "zero_denominator_clusters": len(zero_denom),
        "zero_denominator_cluster_ids": [f"{t}|{c}" for t, c in zero_denom],
        "total_design_clusters": len(all_clusters),
        "cluster_table": cluster_rows,
        "ab_condrec_cluster_equal": method_rate(method_a),
        "nsga2_condrec_cluster_equal": method_rate(method_b),
        "mean_paired_diff": round(mean, 6) if mean is not None else None,
        "cluster_sd": round(sd, 6),
        "ci95": [round(ci[0], 6), round(ci[1], 6)],
        "signflip_p": round(p, 6) if p is not None else None,
        "scenario_weighted_diff": round(sw_mean, 6) if sw_mean is not None else None,
        "n_paired_scenarios": len(sc_effect),
        "pairing_completeness": round(1 - len(missing) / max(1, len(scenarios)), 6),
        "missing_pairs": missing,
        "per_cluster_r12_denominator": {c["cluster"]: c["n_r12_scenarios"] for c in cluster_rows},
    }


def safety_endpoint(data, label, ok_field, method="AB"):
    """Independent R3 (CorrectEscalation) or R4 (DamageContainment) stats."""
    per_cluster = defaultdict(list)
    for run in data["runs"]:
        if run["method"] != method:
            continue
        for row in run["rows"]:
            if row["label"] != label or row["class_success"] is None:
                continue
            per_cluster[(row["task"], row["composition"])].append(row["class_success"])
    cluster_rates = {f"{t}|{c}": sum(v) / len(v) for (t, c), v in per_cluster.items()}
    rates = list(cluster_rates.values())
    n = len(rates)
    mean = sum(rates) / n if n else None
    sd = (sum((x - mean) ** 2 for x in rates) / (n - 1)) ** 0.5 if n > 1 else 0.0
    rng = random.Random(BOOT_SEED + 7)
    boot = []
    for _ in range(BOOT_REPS):
        if not rates:
            break
        sample = [rates[rng.randrange(n)] for _ in range(n)]
        boot.append(sum(sample) / len(sample))
    boot.sort()
    ci = [round(boot[int(0.025 * (len(boot) - 1))], 6),
          round(boot[int(0.975 * (len(boot) - 1))], 6)] if boot else [None, None]
    denom = sum(len(v) for v in per_cluster.values())
    return {
        "label": label, "success_definition": ok_field, "method": method,
        "n_eligible_clusters": n,
        "n_episodes": denom,
        "success_rate_cluster_equal": round(mean, 6) if mean is not None else None,
        "cluster_sd": round(sd, 6),
        "ci95": ci,
        "per_cluster_rates": cluster_rates,
    }


def analyze(input_path, method_a="AB", method_b="nsga2"):
    data, input_sha = load_runs(input_path)
    checks = integrity_checks(data, method_a, method_b)
    primary = endpoint_table(data, method_a, method_b)
    r3 = safety_endpoint(data, "R3", "policy_selected_escalation & zero residual", method_a)
    r3_b = safety_endpoint(data, "R3", "policy_selected_escalation & zero residual", method_b)
    r4 = safety_endpoint(data, "R4", "explicit escalation & zero duplicate & avoidable_harm=0", method_a)
    r4_b = safety_endpoint(data, "R4", "explicit escalation & zero duplicate & avoidable_harm=0", method_b)
    return {
        "kind": "CONDREC_PRIMARY_ENDPOINT_ANALYSIS_D064A",
        "estimand": "CondRecSucc = mean class_success over R1+R2 only (cluster-equal-weight)",
        "input_file": str(input_path),
        "input_sha256": input_sha,
        "program_version": "condrec_analysis.py v1 (D-064-A)",
        "git_commit": git_sha(),
        "analysis_command": "python condrec_analysis.py --input diagnostic3_results.json --outdir .",
        "bootstrap_reps": BOOT_REPS, "signflip_reps": SIGNFLIP_REPS,
        "random_seeds": {"bootstrap": BOOT_SEED, "signflip": BOOT_SEED + 1},
        "stat_method": ("hierarchical paired: (scenario,seed) pairing -> seed-mean per "
                        "scenario -> equal-weight cluster (task x composition) means -> "
                        "cluster bootstrap percentile CI + cluster-level sign-flip MC test"),
        "zero_denominator_rule": ("clusters with no R1/R2 scenario are EXCLUDED from the "
                                  "primary estimand and registered; never zero-filled"),
        "integrity_checks": checks,
        "primary": primary,
        "safety_r3": {"AB": r3, "nsga2": r3_b},
        "safety_r4": {"AB": r4, "nsga2": r4_b},
    }


def write_outputs(report, outdir):
    outdir = Path(outdir)
    (outdir / "condrec_diagnostic3.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with (outdir / "condrec_diagnostic3.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["cluster", "n_r12_scenarios", "mean_paired_diff_AB_minus_nsga2"])
        for c in report["primary"]["cluster_table"]:
            w.writerow([c["cluster"], c["n_r12_scenarios"], c["mean_paired_diff"]])
    p = report["primary"]
    lines = [
        "# CondRecSucc 主要终点独立分析（D-064-A）", "",
        f"- 输入 `{report['input_file']}` SHA-256 `{report['input_sha256']}`",
        f"- 程序：{report['program_version']}；git `{report['git_commit']}`",
        f"- 命令：`{report['analysis_command']}`",
        f"- Bootstrap {report['bootstrap_reps']} 次（cluster 重采样，seed {report['random_seeds']['bootstrap']}）；"
        f"Sign-flip {report['signflip_reps']} 次（真实 cluster 级符号翻转 MC，seed {report['random_seeds']['signflip']}）",
        f"- 层级：{report['stat_method']}",
        f"- 零分母规则：{report['zero_denominator_rule']}", "",
        "## 主要结果（R1+R2 only）", "",
        f"- primary eligible clusters: **{p['primary_eligible_clusters']}** / 设计 clusters {p['total_design_clusters']}",
        f"- zero-denominator (R3/R4-only) clusters: {p['zero_denominator_clusters']} → {p['zero_denominator_cluster_ids']}",
        f"- AB CondRecSucc: **{p['ab_condrec_cluster_equal']}**；NSGA-II: **{p['nsga2_condrec_cluster_equal']}**",
        f"- Δ(AB−NSGA-II): **{p['mean_paired_diff']}**；Cluster SD: {p['cluster_sd']}",
        f"- 95% CI: {p['ci95']}；sign-flip p: **{p['signflip_p']}**",
        f"- scenario 加权敏感性 Δ: {p['scenario_weighted_diff']}",
        f"- 配对完整率: {p['pairing_completeness']}（缺失 {len(p['missing_pairs'])} 个 scenario-seed 对）", "",
        "## R3 / R4 独立安全统计", "",
    ]
    for name, blk in (("R3 CorrectEscalation", report["safety_r3"]),
                      ("R4 DamageContainment", report["safety_r4"])):
        lines.append(f"### {name}")
        for m, s in blk.items():
            lines.append(f"- {m}: rate={s['success_rate_cluster_equal']} "
                         f"clusters={s['n_eligible_clusters']} episodes={s['n_episodes']} "
                         f"SD={s['cluster_sd']} CI={s['ci95']}")
    lines += ["", "## 每 cluster R1/R2 分母与效应", "",
              "| cluster | n_R1/R2 | Δ |", "|---|---|---|"]
    for c in p["cluster_table"]:
        lines.append(f"| {c['cluster']} | {c['n_r12_scenarios']} | {c['mean_paired_diff']:+.4f} |")
    (outdir / "condrec_diagnostic3_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="diagnostic3_results.json")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()
    report = analyze(args.input)
    write_outputs(report, args.outdir)
    p = report["primary"]
    print("integrity problems:", report["integrity_checks"]["problems"] or "none")
    print(f"eligible clusters={p['primary_eligible_clusters']} zero-denom={p['zero_denominator_clusters']}")
    print(f"AB={p['ab_condrec_cluster_equal']} nsga2={p['nsga2_condrec_cluster_equal']} "
          f"d={p['mean_paired_diff']} sd={p['cluster_sd']} ci={p['ci95']} p={p['signflip_p']}")
    print(f"scenario-weighted d={p['scenario_weighted_diff']} pairing={p['pairing_completeness']}")
    print("wrote condrec_diagnostic3.{json,csv,report.md}")


if __name__ == "__main__":
    main()
