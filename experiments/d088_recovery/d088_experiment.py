"""D-088 comparative experiment runner (Train-only).

Arms:
  Fixed baselines: Hand, RuleBased, Greedy, AdaptiveProbe, CostAware, Random
  Search methods: RandomSearch, NSGA-II, NSGA-III on three mechanism genomes:
    A  feedback-driven        (enable_a)
    B  delay-aware            (enable_b)
    C  dependency-aware       (enable_c)
    AB / AC / BC / ABC combos
  Each search arm evolves its genome on the SAME 96 Train scenarios with the
  same evaluation budget and paired optimizer seeds.

All evaluation is deterministic simulator-only (no LLM/API).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))

from dependency_recovery import run_episode  # noqa: E402
from dependency_policies import (  # noqa: E402
    HandPolicy, RuleBasedPolicy, GreedyCompensationPolicy,
    AdaptiveProbePolicy, RandomPolicy, FixedPrefixPolicy,
)
from d088_genome import (  # noqa: E402
    D088RecoveryGenome, random_genome, mutate, crossover, arm_flags,
)
from d088_policies import D088RecoveryPolicy  # noqa: E402
from d088_scenarios import build_manifest, validate_manifest  # noqa: E402

OUT = HERE / "results"
SEEDS = [711, 822, 933]
POP = 12
GENERATIONS = 6
MAX_ACTIONS = 24

SEARCH_ARMS = ["A", "B", "C", "AB", "AC", "BC", "ABC"]


def sha256_of(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def evaluate_rows(policy_factory, scenarios):
    rows = []
    for sc in scenarios:
        rows.append(run_episode(policy_factory(), sc, max_actions=MAX_ACTIONS))
    return rows


def summarize_rows(rows):
    def mean(vals):
        return sum(vals) / len(vals) if vals else 0.0
    r12 = [r for r in rows if r["label"] in ("R1", "R2")]
    r3 = [r for r in rows if r["label"] == "R3"]
    r4 = [r for r in rows if r["label"] == "R4"]
    return {
        "n": len(rows),
        "cond_rec": mean([r["conditional_recovery_success"] for r in r12]),
        "r3_success": mean([r["correct_escalation"] for r in r3]),
        "r4_success": mean([r["class_success"] for r in r4]),
        "avoid_harm": mean([r["avoidable_harm"] for r in rows]),
        "recovery_cost": mean([r["recovery_cost"] for r in rows]),
        "decision_count": mean([r["decision_count"] for r in rows]),
        "constraint_violation": sum(r["constraint_violation"] for r in rows),
        "duplicate_compensation": sum(r["duplicate_compensation"] for r in rows),
        "pending_compensation": sum(r["pending_compensation"] for r in rows),
        "forced_abort": sum(r["runtime_forced_abort"] for r in rows),
    }


# ---------------------------------------------------------------------------
# Fixed baselines
# ---------------------------------------------------------------------------
FIXED = {
    "Hand": lambda seed: HandPolicy(),
    "RuleBased": lambda seed: RuleBasedPolicy(),
    "Greedy": lambda seed: GreedyCompensationPolicy(),
    "AdaptiveProbe": lambda seed: AdaptiveProbePolicy(),
    "CostAware": lambda seed: AdaptiveProbePolicy(cost_first=True),
    "Random": lambda seed: RandomPolicy(seed),
    "FixedPrefix": lambda seed: FixedPrefixPolicy(),
}


def run_fixed(scenarios):
    out = {}
    for name, factory in FIXED.items():
        t0 = time.time()
        rows = evaluate_rows(lambda: factory(20261122), scenarios)
        out[name] = {"summary": summarize_rows(rows), "seconds": round(time.time() - t0, 2)}
        print(f"  fixed {name}: R3={out[name]['summary']['r3_success']:.3f} "
              f"R4={out[name]['summary']['r4_success']:.3f} "
              f"harm={out[name]['summary']['avoid_harm']:.3f}")
    return out


# ---------------------------------------------------------------------------
# Evolutionary search (RandomSearch / NSGA-II / NSGA-III)
# ---------------------------------------------------------------------------
def objectives_of(rows):
    s = summarize_rows(rows)
    return [
        float(s["constraint_violation"] + s["pending_compensation"]),
        1.0 - s["cond_rec"],
        1.0 - s["r3_success"],
        1.0 - s["r4_success"],
        s["avoid_harm"],
        s["recovery_cost"],
    ]


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def fast_nds(objs):
    n = len(objs)
    fronts = [[]]
    dom_count = [0] * n
    dominated = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if dominates(objs[i], objs[j]):
                dominated[i].append(j)
                dom_count[j] += 1
            elif dominates(objs[j], objs[i]):
                dominated[j].append(i)
                dom_count[i] += 1
    for i in range(n):
        if dom_count[i] == 0:
            fronts[0].append(i)
    k = 0
    while fronts[k]:
        nxt = []
        for i in fronts[k]:
            for j in dominated[i]:
                dom_count[j] -= 1
                if dom_count[j] == 0:
                    nxt.append(j)
        k += 1
        fronts.append(nxt)
    return fronts[:-1]


def crowding(objs, front):
    n = len(front)
    dist = {i: 0.0 for i in front}
    if n <= 2:
        for i in front:
            dist[i] = float("inf")
        return dist
    m = len(objs[0])
    for d in range(m):
        vals = sorted(front, key=lambda i: objs[i][d])
        dist[vals[0]] = dist[vals[-1]] = float("inf")
        lo, hi = objs[vals[0]][d], objs[vals[-1]][d]
        span = hi - lo or 1.0
        for k in range(1, n - 1):
            dist[vals[k]] += (objs[vals[k + 1]][d] - objs[vals[k - 1]][d]) / span
    return dist


def nsga2_select(pop, objs, size, rng):
    fronts = fast_nds(objs)
    chosen = []
    for front in fronts:
        if len(chosen) + len(front) <= size:
            chosen.extend(front)
        else:
            dist = crowding(objs, front)
            ranked = sorted(front, key=lambda i: -dist[i])
            chosen.extend(ranked[: size - len(chosen)])
            break
    return [pop[i] for i in chosen]


def nsga3_select(pop, objs, size, rng):
    """NSGA-III with reference-direction niching (Das-Dennis, 6-objective)."""
    import itertools
    m = len(objs[0])
    fronts = fast_nds(objs)
    chosen = []
    last = None
    for front in fronts:
        if len(chosen) + len(front) <= size:
            chosen.extend(front)
        else:
            last = front
            break
    if last is None:
        return [pop[i] for i in chosen]
    # normalize
    ideal = [min(objs[i][d] for i in range(len(objs))) for d in range(m)]
    shifted = [[objs[i][d] - ideal[d] for d in range(m)] for i in range(len(objs))]
    extreme = []
    for d in range(m):
        w = [1e-6] * m
        w[d] = 1.0
        extreme.append(min(range(len(shifted)), key=lambda i: max(shifted[i][j] / w[j] for j in range(m))))
    try:
        import numpy as np
        A = np.array([shifted[i] for i in extreme])
        b = np.ones(m)
        inter = np.linalg.solve(A, b)
        nadir = [1.0 / max(x, 1e-9) for x in inter]
        denom = [nadir[d] - ideal[d] if nadir[d] > ideal[d] else 1.0 for d in range(m)]
        norm = [[shifted[i][d] / denom[d] for d in range(m)] for i in range(len(objs))]
    except Exception:
        norm = shifted
    # reference dirs: Das-Dennis with p=3 on m dims -> comb(p+m-1, m-1) = C(8,5)=56
    p = 3
    dirs = []
    for combo in itertools.combinations(range(p + m - 1), m - 1):
        prev = -1
        counts = []
        for c in combo:
            counts.append(c - prev - 1)
            prev = c
        counts.append(p + m - 2 - prev)
        dirs.append([c / p for c in counts])
    # associate
    def nadir_dist(vec, ref):
        import math
        w = [max(x, 1e-12) for x in ref]
        proj = sum(vec[j] * w[j] for j in range(len(vec))) / sum(x * x for x in w)
        perp2 = sum((vec[j] - proj * w[j]) ** 2 for j in range(len(vec)))
        return math.sqrt(max(perp2, 0.0))
    assoc = {}
    niche = {}
    for i in list(chosen) + list(last):
        best_d, best_j = None, 0
        for j, ref in enumerate(dirs):
            dd = nadir_dist(norm[i], ref)
            if best_d is None or dd < best_d:
                best_d, best_j = dd, j
        assoc[i] = best_j
        if i in chosen:
            niche[best_j] = niche.get(best_j, 0) + 1
    need = size - len(chosen)
    remaining = list(last)
    while remaining and need > 0:
        min_niche = min(niche.get(assoc[i], 0) for i in remaining)
        cand = [i for i in remaining if niche.get(assoc[i], 0) == min_niche]
        pick = cand[rng.randrange(len(cand))]
        chosen.append(pick)
        niche[assoc[pick]] = niche.get(assoc[pick], 0) + 1
        remaining.remove(pick)
        need -= 1
    return [pop[i] for i in chosen]


def evolve(scenarios, arm, method, seed):
    rng = random.Random(seed * 7919 + 29)
    pop = [random_genome(random.Random(seed * 131 + i * 17 + 3), arm) for i in range(POP)]
    evals = 0

    def evaluate(g):
        nonlocal evals
        evals += 1
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), scenarios)
        return objectives_of(rows)

    objs = [evaluate(g) for g in pop]
    t0 = time.time()
    for _gen in range(GENERATIONS):
        offspring = []
        for _ in range(POP):
            if rng.random() < 0.7:
                child = mutate(rng.choice(pop), rng)
            else:
                child = crossover(rng.choice(pop), rng.choice(pop), rng)
                child = mutate(child, rng)
            offspring.append(child)
        off_objs = [evaluate(g) for g in offspring]
        combined = pop + offspring
        combined_objs = objs + off_objs
        if method == "NSGA-III":
            pop = nsga3_select(combined, combined_objs, POP, rng)
        else:
            pop = nsga2_select(combined, combined_objs, POP, rng)
        idx = {id(g): i for i, g in enumerate(combined)}
        objs = [combined_objs[idx[id(g)]] for g in pop]
    # final: pick best by lexicographic rule among zero-hard-constraint
    final = []
    for g in pop:
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), scenarios)
        s = summarize_rows(rows)
        final.append((s, g, rows))
    feasible = [x for x in final if x[0]["constraint_violation"] == 0 and x[0]["pending_compensation"] == 0]
    pool = feasible or final
    best_s, best_g, best_rows = max(pool, key=lambda x: (
        min(x[0]["r3_success"], x[0]["r4_success"]),
        x[0]["r3_success"] + x[0]["r4_success"],
        -x[0]["avoid_harm"], -x[0]["recovery_cost"]
    ))
    return {
        "arm": arm, "method": method, "seed": seed,
        "evals": evals, "seconds": round(time.time() - t0, 2),
        "best_summary": best_s,
        "best_genome": best_g.fingerprint(),
        "best_rows": best_rows,
    }


def run_search(scenarios):
    out = {"RandomSearch": {}, "NSGA-II": {}, "NSGA-III": {}}
    for method in out:
        for arm in SEARCH_ARMS:
            out[method][arm] = []
            for seed in SEEDS:
                if method == "RandomSearch":
                    rng = random.Random(seed * 7919 + 29)
                    best = None
                    for i in range(POP * (GENERATIONS + 1)):
                        g = random_genome(random.Random(seed * 131 + i * 17 + 3), arm)
                        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), scenarios)
                        s = summarize_rows(rows)
                        if s["constraint_violation"] == 0 and s["pending_compensation"] == 0:
                            key = (min(s["r3_success"], s["r4_success"]),
                                   s["r3_success"] + s["r4_success"],
                                   -s["avoid_harm"], -s["recovery_cost"])
                        else:
                            key = (-1.0, -1.0, 0.0, 0.0)
                        if best is None or key > best[0]:
                            best = (key, s, g, rows)
                    res = {
                        "arm": arm, "method": method, "seed": seed,
                        "evals": POP * (GENERATIONS + 1),
                        "best_summary": best[1],
                        "best_genome": best[2].fingerprint(),
                        "best_rows": best[3],
                    }
                else:
                    res = evolve(scenarios, arm, method, seed)
                out[method][arm].append(res)
                s = res["best_summary"]
                print(f"  {method}/{arm}/seed{seed}: R3={s['r3_success']:.3f} "
                      f"R4={s['r4_success']:.3f} harm={s['avoid_harm']:.3f} "
                      f"cost={s['recovery_cost']:.1f} viol={s['constraint_violation']}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all", choices=["fixed", "search", "all"])
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    manifest = build_manifest()
    if not validate_manifest(manifest)["ok"]:
        raise SystemExit("manifest invalid")
    manifest_path = OUT / "d088_train_manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    scenarios = manifest["scenarios"]
    print(f"[D-088] scenarios={len(scenarios)} sha={manifest['manifest_sha256'][:16]}...")
    report = {
        "protocol_id": "D-088-TRAIN-EXPERIMENT",
        "manifest_sha256": manifest["manifest_sha256"],
        "seeds": SEEDS, "pop": POP, "generations": GENERATIONS,
        "max_actions": MAX_ACTIONS,
    }
    if args.stage in ("fixed", "all"):
        report["fixed"] = run_fixed(scenarios)
    if args.stage in ("search", "all"):
        report["search"] = run_search(scenarios)
    report["report_sha256"] = sha256_of({k: v for k, v in report.items() if k != "report_sha256"})
    path = OUT / "d088_experiment_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("report:", path, "sha:", report["report_sha256"][:16])


if __name__ == "__main__":
    main()
