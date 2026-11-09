"""Monte Carlo power simulation for the A-3b preregistration (D-063 Stage 1).

Uses EMPIRICAL cluster-level paired differences from diagnostic3 (development
data only). Cluster = task x fault-composition; the simulation draws cluster
diffs at the cluster level (seeds already nested inside cluster means).

Outputs: power_simulation.json + power_simulation_report.md
"""
from __future__ import annotations

import json
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
MC_SIMS = 2000
MC_SEED = 20261110
ALPHA = 0.05
MDES = (0.08, 0.10, 0.1173)
N_CLUSTER_GRID = (18, 36, 54, 72, 90, 110, 123, 145, 163, 190, 254)
ATTRITION = 0.15


def load_cluster_diffs(method_a, method_b, scope):
    raw = json.loads((HERE / "diagnostic3_results.json").read_text(encoding="utf-8"))
    A, B, meta = defaultdict(dict), defaultdict(dict), {}
    for r in raw["runs"]:
        for row in r["rows"]:
            if scope != "all" and row["split"] != scope:
                continue
            if row["class_success"] is None:
                continue
            meta[row["scenario_id"]] = (row["task"], row["composition"])
            if r["method"] == method_a:
                A[row["scenario_id"]][r["seed"]] = row["class_success"]
            elif r["method"] == method_b:
                B[row["scenario_id"]][r["seed"]] = row["class_success"]
    cl = defaultdict(list)
    for sid, per in A.items():
        diffs = [v - B[sid][s] for s, v in per.items() if s in B.get(sid, {})]
        if diffs:
            cl[meta[sid]].append(sum(diffs) / len(diffs))
    return {k: sum(v) / len(v) for k, v in cl.items()}


def icc_task_families(cluster_diffs):
    """One-way random-effects ICC of cluster diffs grouped by task family:
    how much of the variance sits between task families (cluster correlation)."""
    by_task = defaultdict(list)
    for (task, _comp), v in cluster_diffs.items():
        by_task[task].append(v)
    groups = list(by_task.values())
    k = len(groups)
    n = sum(len(g) for g in groups)
    if k < 2 or n <= k:
        return None
    grand = st.mean([x for g in groups for x in g])
    ssb = sum(len(g) * (st.mean(g) - grand) ** 2 for g in groups)
    ssw = sum(sum((x - st.mean(g)) ** 2 for x in g) for g in groups)
    msb, msw = ssb / (k - 1), ssw / (n - k)
    n0 = n / k
    icc = (msb - msw) / (msb + (n0 - 1) * msw) if (msb + (n0 - 1) * msw) > 0 else 0.0
    return {"k_task_families": k, "n_clusters": n, "icc": round(icc, 4),
            "between_task_sd": round(st.stdev([st.mean(g) for g in groups]), 4) if k > 1 else None}


def mc_power(empirical_diffs, mde, n_clusters, sims=MC_SIMS, seed=MC_SEED,
             test="t", assume_mean_shift=True):
    """Power of a one-sample test on cluster means under H1: true mean = mde.

    Two generators:
      normal: N(mde, sd_empirical)
      resample: bootstrap from centered empirical diffs + mde shift
    Two tests: t (cluster-mean one-sample t) and signflip.
    """
    vals = list(empirical_diffs.values()) if isinstance(empirical_diffs, dict) else list(empirical_diffs)
    mu0 = st.mean(vals)
    sd = st.stdev(vals) if len(vals) > 1 else 0.0
    rng = random.Random(seed + int(mde * 1000) + n_clusters)
    centered = [v - mu0 for v in vals]
    rej = 0
    for _ in range(sims):
        if assume_mean_shift:
            sample = [rng.gauss(mde, sd) for _ in range(n_clusters)]
        else:
            sample = [rng.choice(centered) + mde for _ in range(n_clusters)]
        m = st.mean(sample)
        s = st.stdev(sample) if len(sample) > 1 else 1e-9
        if test == "t":
            tval = m / (s / math.sqrt(n_clusters))
            # two-sided normal approx for t with large df
            p = 2 * (1 - 0.5 * (1 + math.erf(abs(tval) / math.sqrt(2))))
        else:  # signflip MC-lite: analytic approximation via normal of mean
            z = m / (s / math.sqrt(n_clusters))
            p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        if p < ALPHA:
            rej += 1
    return round(rej / sims, 4)


def main():
    dev = load_cluster_diffs("AB", "A", "all")            # development contrast
    prim = load_cluster_diffs("AB", "nsga2", "all")        # primary contrast (dev data)
    prim_val = load_cluster_diffs("AB", "nsga2", "validation")

    sources = {
        "primary_AB_vs_nsga2_all_dev": prim,
        "primary_AB_vs_nsga2_validation_18cl": prim_val,
        "secondary_AB_vs_A_all_dev": dev,
    }
    iccs = {name: icc_task_families(cd) for name, cd in sources.items()}

    results = []
    for src_name, diffs in sources.items():
        sd = st.stdev(list(diffs.values()))
        mean = st.mean(list(diffs.values()))
        for mde in MDES:
            for n_cl in N_CLUSTER_GRID:
                n_eff = n_cl
                n_attr = int(math.floor(n_cl * (1 - ATTRITION)))
                p_t = mc_power(diffs, mde, n_eff, test="t")
                p_attr = mc_power(diffs, mde, n_attr, test="t")
                p_null = mc_power(diffs, 0.0, n_eff, test="t")
                results.append({
                    "source": src_name, "mde": mde, "n_clusters": n_eff,
                    "n_clusters_after_15pct_attrition": n_attr,
                    "empirical_cluster_sd": round(sd, 4),
                    "empirical_mean": round(mean, 4),
                    "power_t": p_t,
                    "power_t_attrition": p_attr,
                    "false_positive_rate_at_null": p_null,
                })

    # required n for 80/90% per source per MDE (interpolating the grid)
    req = []
    for src_name in sources:
        for mde in MDES:
            for target in (0.80, 0.90):
                hit = next((r for r in results if r["source"] == src_name
                            and r["mde"] == mde and r["power_t"] >= target), None)
                req.append({"source": src_name, "mde": mde, "target_power": target,
                            "n_clusters_required": hit["n_clusters"] if hit else None,
                            "n_with_15pct_attrition": int(math.ceil(hit["n_clusters"] / (1 - ATTRITION))) if hit else None})

    out = {
        "kind": "MONTE_CARLO_POWER_SIMULATION_D063",
        "mc_sims": MC_SIMS, "seed": MC_SEED, "alpha": ALPHA,
        "generator": "normal(mde, empirical cluster sd); seeds nested in cluster means",
        "test": "one-sample two-sided cluster-mean t (normal approx)",
        "attrition_rate": ATTRITION,
        "sources": {k: {"n_clusters": len(v), "mean": round(st.mean(list(v.values())), 4),
                        "sd": round(st.stdev(list(v.values())), 4)} for k, v in sources.items()},
        "icc_analysis": iccs,
        "results": results,
        "required_n": req,
        "caveats": [
            "validation source has only 18 clusters: sd estimate unstable (see sensitivity across sources)",
            "planning uses development data only; historical validation is NOT the formal test set",
            "no episode-level inflation: unit is the cluster",
        ],
    }
    (HERE / "power_simulation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = ["# D-063 Stage 1 — Monte Carlo 功效仿真", "",
             f"- MC 次数 {MC_SIMS}，种子 {MC_SEED}，α={ALPHA}；单位=cluster（seed 嵌套）",
             f"- 发生器：N(MDE, 经验 cluster SD)；检验：cluster 均值单样本双侧 t（正态近似）",
             f"- 失效预留 {ATTRITION:.0%}", "", "## 经验 cluster 差值分布", ""]
    for k, v in out["sources"].items():
        lines.append(f"- {k}: n={v['n_clusters']} mean={v['mean']} sd={v['sd']}")
    lines.append("")
    lines.append("## Task-family ICC（cluster 独立性评估）")
    for k, v in iccs.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## 所需 cluster 数（power ≥ 目标）")
    lines.append("| source | MDE | 80% | 90% | 含15%失效(80%) |")
    lines.append("|---|---|---|---|---|")
    by = defaultdict(dict)
    for r in req:
        by[(r["source"], r["mde"])][r["target_power"]] = r
    for (src, mde), d in sorted(by.items()):
        r80, r90 = d[0.80], d[0.90]
        lines.append(f"| {src} | {mde} | {r80['n_clusters_required']} | {r90['n_clusters_required']} | {r80['n_with_15pct_attrition']} |")
    lines.append("")
    lines.append("## 功效曲线（primary_AB_vs_nsga2_all_dev）")
    lines.append("| n_clusters | MDE=0.08 | MDE=0.10 | MDE=0.1173 | null FPR (MDE=0.10 row) |")
    lines.append("|---|---|---|---|---|")
    for n_cl in N_CLUSTER_GRID:
        row = {r["mde"]: r for r in results
               if r["source"] == "primary_AB_vs_nsga2_all_dev" and r["n_clusters"] == n_cl}
        fpr = row[0.10]["false_positive_rate_at_null"]
        lines.append(f"| {n_cl} | {row[0.08]['power_t']} | {row[0.10]['power_t']} | {row[0.1173]['power_t']} | {fpr} |")
    lines.append("")
    lines.append("## 敏感性与限制")
    for c in out["caveats"]:
        lines.append(f"- {c}")
    (HERE / "power_simulation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("required_n:")
    for r in req:
        if r["target_power"] == 0.80:
            print(f"  {r['source']:38s} MDE={r['mde']}: 80% n={r['n_clusters_required']} (attr {r['n_with_15pct_attrition']})")
    print("ICC:", json.dumps(iccs, indent=1))
    print("wrote power_simulation.json / power_simulation_report.md")


if __name__ == "__main__":
    main()
