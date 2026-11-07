"""Stage-3 statistical analysis of the diagnostic experiment.

Cluster = task-family x fault-composition (the independent statistical unit).
Paired cluster bootstrap + sign-flip permutation on per-scenario outcomes.
Holm correction across the secondary contrast family.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent


def load():
    return json.loads((HERE / "diagnostic_results.json").read_text(encoding="utf-8"))


def cluster_key(row):
    return (row["task"], row["composition"])


def paired_cluster_bootstrap(rows_a, rows_b, field="class_success", reps=4000, seed=20261107):
    """Paired difference a-b clustered by (task, composition)."""
    idx_a = {r["scenario_id"]: r for r in rows_a}
    idx_b = {r["scenario_id"]: r for r in rows_b}
    clusters = defaultdict(list)
    for sid, ra in idx_a.items():
        rb = idx_b.get(sid)
        if rb is None:
            continue
        va, vb = ra.get(field), rb.get(field)
        if va is None or vb is None:
            continue
        clusters[cluster_key(ra)].append(float(va) - float(vb))
    keys = sorted(clusters)
    if not keys:
        return None
    all_vals = [v for k in keys for v in clusters[k]]
    mean = sum(all_vals) / len(all_vals)
    rng = random.Random(seed)
    est = []
    for _ in range(reps):
        sampled = [rng.choice(keys) for _ in keys]
        vals = [v for k in sampled for v in clusters[k]]
        est.append(sum(vals) / len(vals))
    est.sort()
    lo = est[int(0.025 * (len(est) - 1))]
    hi = est[int(0.975 * (len(est) - 1))]
    # sign-flip permutation p-value (cluster means)
    cm = [sum(clusters[k]) / len(clusters[k]) for k in keys]
    obs = abs(sum(cm) / len(cm))
    extreme = 0
    for _ in range(4000):
        s = sum(c * (1 if rng.random() < 0.5 else -1) for c in cm) / len(cm)
        if abs(s) >= obs - 1e-12:
            extreme += 1
    p = (extreme + 1) / 4001
    return {
        "mean_diff": round(mean, 4),
        "ci95": [round(lo, 4), round(hi, 4)],
        "clusters": len(keys),
        "permutation_p": round(p, 4),
    }


def holm(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * ps[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def main():
    data = load()
    runs = data["runs"]
    by_ms = {(r["method"], r["seed"]): r for r in runs}
    methods = ["hand", "random", "ga", "nsga2", "nsga3", "A", "B", "AB"]
    seeds = data["seeds"]

    # ---- aggregate means across seeds -----------------------------------
    agg = {}
    for m in methods:
        keys = ["cond_rec", "corr_esc", "containment", "dup", "violations", "unnec_esc", "avoid_resid"]
        row = {}
        for k in keys:
            vals = [by_ms[(m, s)]["metrics"][k] for s in seeds]
            row[k + "_mean"] = round(sum(vals) / len(vals), 4)
            row[k + "_per_seed"] = [round(v, 4) for v in vals]
        # illegal ratio final gen
        irr = []
        for s in seeds:
            h = by_ms[(m, s)]["history"]
            irr.append(h[-1]["illegal_ratio"] if h else 0.0)
        row["illegal_ratio_final_mean"] = round(sum(irr) / len(irr), 4)
        row["illegal_ratio_final_per_seed"] = irr
        agg[m] = row

    # ---- contrasts (per-seed paired then averaged) ----------------------
    def contrast(ma, mb, field="class_success"):
        out = []
        for s in seeds:
            ra = by_ms[(ma, s)]["rows"]
            rb = by_ms[(mb, s)]["rows"]
            res = paired_cluster_bootstrap(ra, rb, field=field)
            if res:
                out.append(res)
        if not out:
            return None
        return {
            "mean_diff_avg": round(sum(o["mean_diff"] for o in out) / len(out), 4),
            "ci95_avg": [
                round(sum(o["ci95"][0] for o in out) / len(out), 4),
                round(sum(o["ci95"][1] for o in out) / len(out), 4),
            ],
            "permutation_p_avg": round(sum(o["permutation_p"] for o in out) / len(out), 4),
            "clusters": out[0]["clusters"],
            "per_seed": out,
        }

    primary = contrast("AB", "nsga2")
    secondary_names = [
        ("A", "nsga2"), ("B", "nsga2"), ("AB", "A"), ("AB", "B"),
        ("AB", "ga"), ("AB", "nsga3"), ("AB", "hand"),
    ]
    secondary = {f"{a} vs {b}": contrast(a, b) for a, b in secondary_names}
    ps = [secondary[f"{a} vs {b}"]["permutation_p_avg"] for a, b in secondary_names if secondary[f"{a} vs {b}"]]
    adj = holm(ps)
    names = [f"{a} vs {b}" for a, b in secondary_names]
    for name, p_adj in zip(names, adj):
        if secondary[name]:
            secondary[name]["holm_p"] = round(p_adj, 4)

    # ---- per-composition breakdown -------------------------------------
    per_comp = defaultdict(lambda: defaultdict(list))
    for r in runs:
        for row in r["rows"]:
            per_comp[r["method"]][row["composition"]].append(row)
    comp_table = {}
    for m in methods:
        comp_table[m] = {}
        for comp, rows in sorted(per_comp[m].items()):
            vals = [x["class_success"] for x in rows if x["class_success"] is not None]
            comp_table[m][comp] = {
                "n": len(rows),
                "class_success": round(sum(vals) / len(vals), 4) if vals else None,
                "viol": round(sum(x["invariant_violation"] for x in rows) / len(rows), 4),
            }

    report = {
        "kind": data["kind"],
        "label_counts": data["label_counts"],
        "throughput_eps_per_s": data["throughput_eps_per_s"],
        "budget_episodes_per_method_seed": data["budget_episodes_per_method_seed"],
        "aggregate": agg,
        "primary_contrast_AB_vs_nsga2": primary,
        "secondary_contrasts": secondary,
        "per_composition": comp_table,
    }
    (HERE / "diagnostic_stats.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # console summary
    print("== aggregate (mean over seeds) ==")
    print(f"{'method':8s} {'cond_rec':>9s} {'corr_esc':>9s} {'cont':>7s} {'dup':>6s} {'viol':>6s} {'unnec':>6s} {'illegal%':>9s}")
    for m in methods:
        a = agg[m]
        print(
            f"{m:8s} {a['cond_rec_mean']:9.3f} {a['corr_esc_mean']:9.3f} {a['containment_mean']:7.3f} "
            f"{a['dup_mean']:6.3f} {a['violations_mean']:6.3f} {a['unnec_esc_mean']:6.3f} "
            f"{a['illegal_ratio_final_mean']:9.3f}"
        )
    print()
    print("== primary: AB vs nsga2 (class_success, cluster bootstrap) ==")
    print(json.dumps(primary, indent=1)[:500])
    print()
    print("== secondary (holm-adjusted) ==")
    for k, v in secondary.items():
        if v:
            print(f"{k:14s} diff={v['mean_diff_avg']:+.4f} ci={v['ci95_avg']} p={v['permutation_p_avg']} holm={v.get('holm_p')}")


if __name__ == "__main__":
    main()
