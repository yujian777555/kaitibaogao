#!/usr/bin/env python3
"""Minimal reproducible Oracle-Linkage Gate for TCAIL's linkage-to-GOM hypothesis.
This is a simplified GOM prototype, not an official GOMEA implementation.
Dependencies: numpy, numba, scipy.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, random
from pathlib import Path
import numpy as np
from numba import njit
from scipy import stats

METHOD_OFFSET = {"oracle": 11, "learned_lt": 22, "random": 33, "singleton": 44}
METHODS = ("oracle", "learned_lt", "random", "singleton")

@njit
def trap_fitness(x, n, k):
    total = 0
    for start in range(0, n, k):
        u = 0
        for j in range(start, start + k):
            u += x[j]
        total += k if u == k else k - 1 - u
    return total

@njit
def additive_fitness(x, n):
    total = 0
    for j in range(n):
        total += x[j]
    return total

@njit
def mix_generation(pop, fits, fos_mask, n, k, seed, remaining_budget, additive):
    np.random.seed(seed)
    p, m = pop.shape[0], fos_mask.shape[0]
    order = np.random.permutation(m)
    evals, improved = 0, False
    for ti in range(p):
        if evals >= remaining_budget:
            break
        for oi in range(m):
            if evals >= remaining_budget:
                break
            si = order[oi]
            di = np.random.randint(p - 1)
            if di >= ti:
                di += 1
            changed = False
            for j in range(n):
                if fos_mask[si, j] != 0 and pop[ti, j] != pop[di, j]:
                    changed = True
                    break
            if not changed:
                continue
            child = pop[ti].copy()
            for j in range(n):
                if fos_mask[si, j] != 0:
                    child[j] = pop[di, j]
            cf = additive_fitness(child, n) if additive else trap_fitness(child, n, k)
            evals += 1
            if cf >= fits[ti]:
                if cf > fits[ti]:
                    improved = True
                pop[ti] = child
                fits[ti] = cf
    return pop, fits, evals, improved

def make_blocks(n, k):
    if n % k:
        raise ValueError("n must be divisible by k")
    return [tuple(range(i, i + k)) for i in range(0, n, k)]

def mi_matrix(pop):
    x = np.asarray(pop, dtype=np.int64)
    count, n = x.shape
    sums = x.sum(axis=0)
    both = x.T @ x
    p11 = both / count
    p10 = (sums[:, None] - both) / count
    p01 = (sums[None, :] - both) / count
    p00 = 1.0 - p11 - p10 - p01
    p1, p0 = sums / count, 1.0 - sums / count
    weights = np.zeros((n, n), dtype=float)
    for p, pa, pb in (
        (p11, p1[:, None], p1[None, :]),
        (p10, p1[:, None], p0[None, :]),
        (p01, p0[:, None], p1[None, :]),
        (p00, p0[:, None], p0[None, :]),
    ):
        den = pa * pb
        mask = (p > 0) & (den > 0)
        weights[mask] += p[mask] * np.log2(p[mask] / den[mask])
    np.fill_diagonal(weights, 0.0)
    return weights

def average_linkage_tree(n, weights):
    clusters = [(i,) for i in range(n)]
    fos = list(clusters)
    while len(clusters) > 1:
        best_i, best_j, best_weight = 0, 1, -1e99
        for i, a in enumerate(clusters):
            for j in range(i + 1, len(clusters)):
                b = clusters[j]
                value = float(weights[np.ix_(a, b)].mean())
                if (value > best_weight + 1e-14 or
                    (abs(value - best_weight) <= 1e-14 and
                     (a, b) < (clusters[best_i], clusters[best_j]))):
                    best_i, best_j, best_weight = i, j, value
        a, b = clusters[best_i], clusters[best_j]
        merged = tuple(sorted(a + b))
        clusters = [c for z, c in enumerate(clusters)
                    if z not in (best_i, best_j)] + [merged]
        clusters.sort()
        fos.append(merged)
    return fos

def oracle_fos(n, blocks):
    fos, roots = [(i,) for i in range(n)], []
    for block in blocks:
        level = [(i,) for i in block]
        while len(level) > 1:
            nxt = []
            for z in range(0, len(level), 2):
                if z + 1 < len(level):
                    merged = tuple(sorted(level[z] + level[z + 1]))
                    fos.append(merged); nxt.append(merged)
                else:
                    nxt.append(level[z])
            level = nxt
        roots.extend(level)
    level = roots
    while len(level) > 1:
        nxt = []
        for z in range(0, len(level), 2):
            if z + 1 < len(level):
                merged = tuple(sorted(level[z] + level[z + 1]))
                fos.append(merged); nxt.append(merged)
            else:
                nxt.append(level[z])
        level = nxt
    return fos

def random_fos(n, rng):
    fos, level = [(i,) for i in range(n)], [(i,) for i in range(n)]
    while len(level) > 1:
        rng.shuffle(level)
        nxt = []
        for z in range(0, len(level), 2):
            if z + 1 < len(level):
                merged = tuple(sorted(level[z] + level[z + 1]))
                fos.append(merged); nxt.append(merged)
            else:
                nxt.append(level[z])
        level = nxt
    return fos

def to_mask(fos, n):
    mask = np.zeros((len(fos), n), dtype=np.uint8)
    for i, subset in enumerate(fos):
        mask[i, list(subset)] = 1
    return mask

def make_fos(method, pop, n, blocks, seed):
    if method == "oracle":
        return to_mask(oracle_fos(n, blocks), n)
    if method == "random":
        return to_mask(random_fos(n, random.Random(seed * 1009 + METHOD_OFFSET[method])), n)
    if method == "singleton":
        return to_mask([(i,) for i in range(n)], n)
    if method == "learned_lt":
        return to_mask(average_linkage_tree(n, mi_matrix(pop)), n)
    raise ValueError(method)

def paired_generation_seed(seed, generation):
    return seed * 100000 + generation


def run_one(method, seed, landscape, budget, n=40, k=4, pop_size=50):
    blocks = make_blocks(n, k)
    init_rng = np.random.default_rng(seed)
    pop = init_rng.integers(0, 2, size=(pop_size, n), dtype=np.int64)
    initial_population_hash = hashlib.sha256(pop.tobytes()).hexdigest()
    additive = landscape == "additive"
    if additive:
        fits = np.asarray([additive_fitness(x, n) for x in pop], dtype=np.int64)
    elif landscape == "trap4":
        fits = np.asarray([trap_fitness(x, n, k) for x in pop], dtype=np.int64)
    else:
        raise ValueError(landscape)
    optimum, evaluations, generation, no_improvement = n, pop_size, 0, 0
    fixed_fos = None
    if method in ("oracle", "random", "singleton"):
        fixed_fos = make_fos(method, pop, n, blocks, seed)
    while (evaluations < budget and generation < 1000 and
           no_improvement < 150 and int(fits.max()) < optimum):
        generation += 1
        fos_mask = (make_fos("learned_lt", pop, n, blocks, seed)
                    if method == "learned_lt" else fixed_fos)
        generation_seed = paired_generation_seed(seed, generation)
        pop, fits, used, improved = mix_generation(
            pop, fits, fos_mask, n, k, generation_seed,
            budget - evaluations, additive)
        evaluations += used
        no_improvement = 0 if improved else no_improvement + 1
        if used == 0:
            no_improvement += 1
    return {
        "landscape": landscape, "seed": seed, "method": method,
        "initial_population_hash": initial_population_hash,
        "mixing_seed_policy": "seed*100000+generation",
        "best": int(fits.max()), "evaluations": evaluations,
        "generations": generation, "success": int(fits.max()) >= optimum,
    }

def paired_summary(rows, comparator, bootstrap_seed=20261104):
    by = {(r["seed"], r["method"]): r for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    diffs = np.asarray([
        by[(s, "oracle")]["best"] - by[(s, comparator)]["best"] for s in seeds
    ], dtype=float)
    wins, ties, losses = int(sum(diffs > 0)), int(sum(diffs == 0)), int(sum(diffs < 0))
    sign_p = float(stats.binomtest(wins, wins + losses, 0.5,
                                   alternative="greater").pvalue)
    wilcoxon_p = float(stats.wilcoxon(diffs, alternative="greater",
                                      zero_method="wilcox").pvalue)
    rng = np.random.default_rng(bootstrap_seed)
    boot = np.asarray([rng.choice(diffs, size=len(diffs), replace=True).mean()
                       for _ in range(30000)])
    return {
        "comparator": comparator,
        "mean_paired_difference": float(diffs.mean()),
        "median_paired_difference": float(np.median(diffs)),
        "wins_ties_losses": [wins, ties, losses],
        "exact_sign_test_one_sided_p": sign_p,
        "wilcoxon_signed_rank_one_sided_p": wilcoxon_p,
        "paired_bootstrap_95pct_ci": [
            float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))
        ],
    }

def summarize(rows, seeds, landscape):
    selected = [r for r in rows if r["landscape"] == landscape]
    by_method = {}
    for method in METHODS:
        group = [r for r in selected if r["method"] == method]
        values = np.asarray([r["best"] for r in group], dtype=float)
        by_method[method] = {
            "n": len(group), "mean_best": float(values.mean()),
            "sd_best": float(values.std(ddof=1)),
            "median_best": float(np.median(values)),
            "successes": int(sum(r["success"] for r in group)),
            "mean_evaluations_used": float(np.mean([r["evaluations"] for r in group])),
        }
    result = {"landscape": landscape, "by_method": by_method}
    if landscape == "trap4":
        result["paired"] = {
            m: paired_summary(selected, m) for m in ("learned_lt", "random", "singleton")
        }
        oracle_success = [next(r["success"] for r in selected
                               if r["seed"] == s and r["method"] == "oracle")
                          for s in range(seeds)]
        learned_success = [next(r["success"] for r in selected
                                if r["seed"] == s and r["method"] == "learned_lt")
                           for s in range(seeds)]
        both = sum(o and l for o, l in zip(oracle_success, learned_success))
        oracle_only = sum(o and not l for o, l in zip(oracle_success, learned_success))
        learned_only = sum((not o) and l for o, l in zip(oracle_success, learned_success))
        neither = sum((not o) and (not l) for o, l in zip(oracle_success, learned_success))
        result["oracle_vs_learned_success_mcnemar"] = {
            "both_success": both, "oracle_only": oracle_only,
            "learned_only": learned_only, "neither": neither,
            "exact_one_sided_p": float(stats.binomtest(
                oracle_only, oracle_only + learned_only, 0.5,
                alternative="greater").pvalue),
        }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--budget", type=int, default=5000)
    parser.add_argument("--n", type=int, default=40)
    parser.add_argument("--k", type=int, default=4)
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--additive-seeds", type=int, default=12)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in range(args.seeds):
        for method in METHODS:
            rows.append(run_one(method, seed, "trap4", args.budget,
                                args.n, args.k, args.population))
    for seed in range(args.additive_seeds):
        for method in METHODS:
            rows.append(run_one(method, seed, "additive", args.budget,
                                args.n, args.k, args.population))
    csv_path = args.output_dir / "per_seed_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    summary = {
        "configuration": vars(args) | {"output_dir": str(args.output_dir)},
        "trap4": summarize(rows, args.seeds, "trap4"),
        "additive": summarize(rows, args.additive_seeds, "additive"),
        "limitations": [
            "Simplified GOM prototype; not an official GOMEA implementation.",
            "Oracle FOS uses the true disjoint 4-bit block partition.",
            "This tests upper-bound linkage value, not TCAIL estimation.",
            "Deterministic objective; no task-block noise, posterior calibration or active acquisition.",
            "Synthetic pilot only; independent clean rerun and more landscapes are required."
        ],
    }
    json_path = args.output_dir / "summary.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("Wrote:", csv_path, "and", json_path)

if __name__ == "__main__":
    main()
