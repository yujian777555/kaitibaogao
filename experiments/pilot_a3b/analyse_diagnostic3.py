"""Independent recomputation entry for diagnostic3 (D-063 Stage 0).

Reads the RAW episode rows from diagnostic3_results.json and recomputes every
metric and every statistical contrast from scratch -- no hardcoded values from
any previous summary. Statistical unit = (task-family x fault-composition)
cluster; algorithm seeds are NESTED repeats (averaged inside each cluster),
never treated as independent samples.

Outputs (in --outdir):
  diagnostic3_recomputed.json   full machine-readable recomputation
  diagnostic3_recomputed.csv    one row per contrast x scope
  diagnostic3_recomputed_report.md  human-readable report incl. delta vs 61

Usage:
  python analyse_diagnostic3.py --input diagnostic3_results.json --outdir .
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

BOOT_REPS = 4000
BOOT_SEED = 20261110
SIGNFLIP_REPS = 4000

REQUIRED_CONTRASTS = [
    ("AB", "nsga2"),
    ("AB", "A"),
    ("AwaitSLA", "A"),
    ("AwaitSLA", "AwaitFixed"),
    ("AB", "AwaitSLA"),
    ("AB", "hand"),
    ("B", "nsga2"),
]
SECONDARY_FAMILY = [
    ("AB", "A"), ("AwaitSLA", "A"), ("AwaitSLA", "AwaitFixed"),
    ("AB", "AwaitSLA"), ("AB", "hand"), ("B", "nsga2"),
]
SCOPES = ("all", "train", "validation")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# structural checks
# ---------------------------------------------------------------------------
def structural_checks(data):
    """Pairing, seed nesting, cluster grouping, duplicates, split leakage,
    denominator sanity. Returns (report dict, list of blocking problems)."""
    problems = []
    runs = data["runs"]
    methods = data["methods"]
    seeds = data["seeds"]

    by_ms = {}
    for r in runs:
        key = (r["method"], r["seed"])
        if key in by_ms:
            problems.append(f"duplicate run record {key}")
        by_ms[key] = r
    for m in methods:
        for s in seeds:
            if (m, s) not in by_ms:
                problems.append(f"missing arm/seed: {m}/{s}")

    # scenario sets per run and pairing across methods within seed
    scen_by_ms = {k: {row["scenario_id"] for row in v["rows"]} for k, v in by_ms.items()}
    per_seed_sets = {}
    for s in seeds:
        sets = [scen_by_ms[(m, s)] for m in methods if (m, s) in scen_by_ms]
        if sets:
            union = set().union(*sets)
            for m in methods:
                if (m, s) in scen_by_ms and scen_by_ms[(m, s)] != union:
                    problems.append(f"pairing broken: {m}/{s} scenario set differs")
            per_seed_sets[s] = union

    # duplicate episode rows
    for (m, s), r in by_ms.items():
        ids = [row["scenario_id"] for row in r["rows"]]
        dup = [i for i, c in Counter(ids).items() if c > 1]
        if dup:
            problems.append(f"duplicate episodes in {m}/{s}: {dup[:3]}")

    # cluster grouping
    clusters = set()
    cluster_sizes = Counter()
    task_by_split = defaultdict(set)
    for (m, s), r in by_ms.items():
        if m != methods[0]:
            continue
        for row in r["rows"]:
            clusters.add((row["task"], row["composition"]))
            cluster_sizes[(row["task"], row["composition"])] += 1
            task_by_split[row["split"]].add(row["task"])

    # split leakage: train vs validation tasks disjoint, scenario prefixes distinct
    train_tasks = task_by_split.get("train", set())
    val_tasks = task_by_split.get("validation", set())
    if train_tasks & val_tasks:
        problems.append(f"split leakage: tasks shared {train_tasks & val_tasks}")
    for s, ids in per_seed_sets.items():
        train_ids = {i for i in ids if i.startswith("t3train|")}
        val_ids = {i for i in ids if i.startswith("t3val|")}
        other = ids - train_ids - val_ids
        if train_ids & val_ids:
            problems.append(f"split leakage in scenario ids (seed {s})")
        if other:
            problems.append(f"unclassified scenario ids (seed {s}): {sorted(other)[:3]}")

    # denominator sanity: class_success null only when label is UNKNOWN
    for (m, s), r in by_ms.items():
        for row in r["rows"]:
            if row["class_success"] is None and row["label"] != "UNKNOWN":
                problems.append(f"null class_success on labelled row {m}/{s}/{row['scenario_id']}")
            if row["class_success"] is not None and row["label"] == "UNKNOWN":
                problems.append(f"class_success on UNKNOWN row {m}/{s}/{row['scenario_id']}")

    return {
        "methods": methods,
        "seeds": seeds,
        "n_runs": len(by_ms),
        "n_clusters": len(clusters),
        "cluster_size_min": min(cluster_sizes.values()) if cluster_sizes else 0,
        "cluster_size_max": max(cluster_sizes.values()) if cluster_sizes else 0,
        "train_tasks": sorted(train_tasks),
        "val_tasks": sorted(val_tasks),
        "problems": problems,
    }, problems


# ---------------------------------------------------------------------------
# metric recomputation
# ---------------------------------------------------------------------------
def filter_rows(data, scope):
    for r in data["runs"]:
        for row in r["rows"]:
            if scope == "all" or row["split"] == scope:
                yield r["method"], r["seed"], row


def recompute_metrics(data):
    out = {}
    for scope in SCOPES:
        out[scope] = {}
        rows_by_ms = defaultdict(list)
        for m, s, row in filter_rows(data, scope):
            rows_by_ms[(m, s)].append(row)
        for m in data["methods"]:
            rows = []
            for s in data["seeds"]:
                rows.extend(rows_by_ms.get((m, s), []))
            lab = defaultdict(list)
            for row in rows:
                lab[row["label"]].append(row)
            r12 = lab["R1"] + lab["R2"]
            r3, r4 = lab["R3"], lab["R4"]

            def rate(rs, key):
                vals = [r[key] for r in rs if r.get(key) is not None]
                return round(sum(vals) / len(vals), 6) if vals else None

            out[scope][m] = {
                "n_episodes": len(rows),
                "class_success": rate(rows, "class_success"),
                "cond_rec_r12": rate(r12, "class_success"),
                "corr_esc_r3": rate(r3, "class_success"),
                "containment_r4": rate(r4, "class_success"),
                "sla_violation": rate(rows, "sla_violation"),
                "duplicate": rate(rows, "duplicate"),
                "invariant_violation": rate(rows, "invariant_violation"),
                "avoidable_harm_mean": rate(rows, "avoidable_harm"),
                "unnec_escalation_r12": rate(r12, "policy_selected_escalation"),
                "n_r1": len(lab["R1"]), "n_r2": len(lab["R2"]),
                "n_r3": len(lab["R3"]), "n_r4": len(lab["R4"]),
            }
    return out


# ---------------------------------------------------------------------------
# contrasts: pooled hierarchical paired cluster inference
# ---------------------------------------------------------------------------
def contrast_stats(data, method_a, method_b, scope="all", field="class_success"):
    """Paired cluster bootstrap + sign-flip. Seeds nested: per-scenario diff
    averaged over seeds first; then clustered by (task, composition)."""
    a = defaultdict(dict)  # sid -> seed -> value
    b = defaultdict(dict)
    meta = {}
    for m, s, row in filter_rows(data, scope):
        if row.get(field) is None:
            continue
        if m == method_a:
            a[row["scenario_id"]][s] = row[field]
            meta[row["scenario_id"]] = (row["task"], row["composition"])
        elif m == method_b:
            b[row["scenario_id"]][s] = row[field]
    sc_diff = {}
    for sid, per_seed in a.items():
        diffs = [float(v) - float(b[sid][sd]) for sd, v in per_seed.items()
                 if sid in b and sd in b[sid]]
        if diffs:
            sc_diff[sid] = sum(diffs) / len(diffs)
    clusters = defaultdict(list)
    for sid, d in sc_diff.items():
        clusters[meta[sid]].append(d)
    keys = sorted(clusters)
    if not keys:
        return None
    means = {k: sum(v) / len(v) for k, v in clusters.items()}
    vals = [means[k] for k in keys]
    mean = sum(vals) / len(vals)
    sd = (sum((x - mean) ** 2 for x in vals) / max(1, len(vals) - 1)) ** 0.5

    rng = random.Random(BOOT_SEED)
    boot = []
    for _ in range(BOOT_REPS):
        sampled = [rng.choice(keys) for _ in keys]
        boot.append(sum(means[k] for k in sampled) / len(sampled))
    boot.sort()
    lo = boot[int(0.025 * (len(boot) - 1))]
    hi = boot[int(0.975 * (len(boot) - 1))]

    rng2 = random.Random(BOOT_SEED + 1)
    obs = abs(mean)
    extreme = 0
    for _ in range(SIGNFLIP_REPS):
        ssum = sum(c * (1 if rng2.random() < 0.5 else -1) for c in vals) / len(vals)
        if abs(ssum) >= obs - 1e-12:
            extreme += 1
    p = (extreme + 1) / (SIGNFLIP_REPS + 1)

    return {
        "method_a": method_a, "method_b": method_b, "scope": scope, "field": field,
        "n_scenarios": len(sc_diff), "n_clusters": len(keys),
        "n_seeds_nested": len({s for per in a.values() for s in per}),
        "mean_diff": round(mean, 6),
        "cluster_sd": round(sd, 6),
        "effect_size_d": round(mean / sd, 6) if sd > 1e-9 else None,
        "ci95": [round(lo, 6), round(hi, 6)],
        "signflip_p": round(p, 6),
        "stat_method": "paired cluster bootstrap (percentile) + cluster-level sign-flip permutation; seeds nested within scenarios",
        "bootstrap_reps": BOOT_REPS, "signflip_reps": SIGNFLIP_REPS,
    }


def holm_adjust(pvals):
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * pvals[i])
        adj[i] = min(1.0, running)
    return adj


def seed_stability(data, method, scope="all", field="class_success"):
    per = {}
    for m, s, row in filter_rows(data, scope):
        if m != method or row.get(field) is None:
            continue
        per.setdefault(s, []).append(row[field])
    out = {str(s): round(sum(v) / len(v), 6) for s, v in sorted(per.items())}
    nums = list(out.values())
    mean = sum(nums) / len(nums) if nums else None
    sd = (sum((x - mean) ** 2 for x in nums) / max(1, len(nums) - 1)) ** 0.5 if len(nums) > 1 else 0.0
    return {"per_seed": out, "mean": round(mean, 6) if mean is not None else None,
            "sd": round(sd, 6)}


# ---------------------------------------------------------------------------
# pipeline
# ---------------------------------------------------------------------------
def analyze(input_path):
    raw = Path(input_path).read_bytes()
    data = json.loads(raw)
    manifest = data.get("manifest_sha256")
    recomputed_manifest = hashlib.sha256(
        json.dumps({k: v for k, v in data.items() if k != "manifest_sha256"},
                   sort_keys=True).encode()).hexdigest()

    checks, problems = structural_checks(data)
    metrics = recompute_metrics(data)

    contrasts = []
    for scope in SCOPES:
        for a, b in REQUIRED_CONTRASTS:
            st = contrast_stats(data, a, b, scope=scope)
            if st:
                contrasts.append(st)
    # Holm within the secondary family, per scope (all = primary family)
    for scope in SCOPES:
        fam = [c for c in contrasts if c["scope"] == scope
               and (c["method_a"], c["method_b"]) in SECONDARY_FAMILY]
        if fam:
            adj = holm_adjust([c["signflip_p"] for c in fam])
            for c, p_ad in zip(fam, adj):
                c["holm_p"] = round(p_ad, 6)

    stability = {m: seed_stability(data, m) for m in data["methods"]}

    return {
        "kind": "DIAGNOSTIC3_INDEPENDENT_RECOMPUTATION",
        "input_file": str(input_path),
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_manifest_field": manifest,
        "input_manifest_recomputed": recomputed_manifest,
        "manifest_match": manifest == recomputed_manifest,
        "analysis_command": "python analyse_diagnostic3.py --input diagnostic3_results.json --outdir .",
        "statistical_unit": "task x fault-composition cluster; seeds nested",
        "structural_checks": checks,
        "metrics": metrics,
        "contrasts": contrasts,
        "seed_stability": stability,
        "blocking_problems": problems,
    }


# 61-report reference values for the delta table (REFERENCE ONLY -- never used
# in any computation above).
REPORT61 = {
    ("AB", "nsga2", "all"): (0.1049, 0.062),
    ("AB", "A", "all"): (0.1193, 0.0002),
    ("AwaitSLA", "A", "all"): (0.0885, 0.0047),
    ("AwaitSLA", "AwaitFixed", "all"): (0.0535, 0.0032),
    ("AB", "AwaitSLA", "all"): (0.0309, 0.0072),
    ("AB", "hand", "all"): (-0.2819, 0.0002),
    ("B", "nsga2", "all"): (-0.0741, 0.0007),
    ("AB", "nsga2", "validation"): (0.1173, 0.2277),
    ("AB", "A", "validation"): (0.1420, 0.0082),
    ("AB", "AwaitSLA", "validation"): (0.0309, 0.2437),
}


def write_outputs(report, outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "diagnostic3_recomputed.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    with (outdir / "diagnostic3_recomputed.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scope", "method_a", "method_b", "n_clusters", "n_scenarios",
                    "mean_diff", "cluster_sd", "effect_size_d", "ci95_low", "ci95_high",
                    "signflip_p", "holm_p", "stat_method"])
        for c in report["contrasts"]:
            w.writerow([c["scope"], c["method_a"], c["method_b"], c["n_clusters"],
                        c["n_scenarios"], c["mean_diff"], c["cluster_sd"],
                        c["effect_size_d"], c["ci95"][0], c["ci95"][1],
                        c["signflip_p"], c.get("holm_p", ""), c["stat_method"]])

    lines = ["# diagnostic3 独立复算报告", "",
             f"- 输入：`{report['input_file']}`",
             f"- SHA-256：`{report['input_sha256']}`",
             f"- manifest 字段：`{report['input_manifest_field'][:16]}…`，复算一致：{report['manifest_match']}",
             f"- 统计单位：{report['statistical_unit']}",
             f"- 分析命令：`{report['analysis_command']}`", ""]
    lines.append("## 结构检查")
    sc = report["structural_checks"]
    lines.append(f"- runs={sc['n_runs']} clusters={sc['n_clusters']} "
                 f"cluster_size=[{sc['cluster_size_min']},{sc['cluster_size_max']}] "
                 f"train_tasks={sc['train_tasks']} val_tasks={sc['val_tasks']}")
    lines.append(f"- 问题：{sc['problems'] if sc['problems'] else '无'}")
    lines.append("")
    lines.append("## 对比（与 61 号报告逐项比较）")
    lines.append("| scope | 对比 | Δ (复算) | 95% CI | p | Holm p | 61号 Δ | 61号 p | 差异 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for c in report["contrasts"]:
        key = (c["method_a"], c["method_b"], c["scope"])
        ref = REPORT61.get(key)
        if ref:
            ddiff = round(c["mean_diff"] - ref[0], 4)
            pdiff = abs(c["signflip_p"] - ref[1])
            if abs(ddiff) < 0.001 and pdiff < 0.001:
                note = "一致"
            elif abs(ddiff) < 0.001:
                note = f"Δ一致；p 差 {pdiff:.4f}(置换MC)"
            else:
                note = f"Δ差 {ddiff}"
        else:
            ref = ("—", "—")
            note = "61号未报告该 scope"
        lines.append(f"| {c['scope']} | {c['method_a']} vs {c['method_b']} | {c['mean_diff']:+.4f} | "
                     f"[{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] | {c['signflip_p']} | "
                     f"{c.get('holm_p', '—')} | {ref[0]} | {ref[1]} | {note} |")
    lines.append("")
    lines.append("## Seed 稳定性（class_success）")
    for m, st in report["seed_stability"].items():
        lines.append(f"- {m}: {st['per_seed']} (sd={st['sd']})")
    lines.append("")
    lines.append("## 方法说明")
    lines.append("paired cluster bootstrap（percentile, 4000 次, seed 20261110）+ "
                 "cluster 级配对符号翻转置换检验（4000 次）；seed 为嵌套重复（场景内先平均），"
                 "不把 episode 当独立样本；次要家族 Holm 校正。")
    (outdir / "diagnostic3_recomputed_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    return outdir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="diagnostic3_results.json")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()
    report = analyze(args.input)
    write_outputs(report, args.outdir)
    print(f"blocking problems: {report['blocking_problems'] or 'none'}")
    for c in report["contrasts"]:
        if c["scope"] == "all":
            print(f"  {c['method_a']:9s} vs {c['method_b']:9s} d={c['mean_diff']:+.4f} "
                  f"ci={c['ci95']} p={c['signflip_p']} holm={c.get('holm_p')}")
    print("wrote diagnostic3_recomputed.{json,csv} and diagnostic3_recomputed_report.md")


if __name__ == "__main__":
    main()
