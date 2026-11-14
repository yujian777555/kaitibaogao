"""D-089 960-evaluation paired search experiment.

Methods (each exactly 960 UNIQUE genome evaluations per run):
  RandomSearch / NSGA-II / NSGA-III / EvoBudget (new: feedback mutation +
  segment crossover + Pareto archive B1 + counterfactual anchors)

Ablations of EvoBudget (same budget):
  No-Pareto-Archive / No-Escalation-Reserve / No-Reachability-Aware /
  No-Parameterized-Stop / No-Counterfactual-Anchor

Paired seeds: 711/822/933/1044/1155.  All arms share scenarios, evaluator,
decision cap 24, and safety gates.  Budget accounting counts every unique
genome evaluation; duplicate re-evaluations are not charged (cache hits are
recorded but free — identical to all methods).
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import random
import sys
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))
sys.path.insert(0, str(_HERE.parent / "d088_recovery"))

from d088_experiment import evaluate_rows, summarize_rows  # noqa: E402
from d088_genome import arm_flags  # noqa: E402
from d089_genome import (  # noqa: E402
    D089Genome, random_genome, mutate, mutate_feedback, crossover_segments,
    pareto_front, select_by_preference,
)
from d089_policies import D089BudgetPolicy  # noqa: E402
from d089_scenarios import build_manifest  # noqa: E402

OUT = _HERE / "results"
SEEDS = [711, 822, 933, 1044, 1155]
POP = 32
BUDGET = 960          # unique genome evaluations per run
MAX_ACTIONS = 24
ARM = "ABC"


# ---------------------------------------------------------------------------
# Counterfactual anchors (Train-failure-analysis derived; provenance recorded)
# ---------------------------------------------------------------------------
# Derived from D-088-R2 train-failure budget analysis (97 report §1):
# early-stop failures -> adaptive stop + escalation reserve + low stop_residual.
ANCHORS = [
    dict(stop_mode=2, escalation_reserve=1.5, cost_safety=1.0, stop_residual=0,
         strict_residual_stop=True, enable_a=True, enable_b=True, enable_c=True),
    dict(stop_mode=2, escalation_reserve=2.0, cost_safety=1.5, stop_residual=0,
         strict_residual_stop=True, enable_a=True, enable_b=True, enable_c=True),
    dict(stop_mode=1, escalation_reserve=1.0, cost_safety=1.0, stop_residual=0,
         strict_residual_stop=True, enable_a=True, enable_b=True, enable_c=True),
]
ANCHOR_PROVENANCE = "d089-budget-analysis-of-d088r2-train-traces-v1"


def make_anchor(rng):
    spec = dict(ANCHORS[rng.randrange(len(ANCHORS))])
    g = random_genome(rng, ARM)
    return dataclasses.replace(g, **spec)


# ---------------------------------------------------------------------------
# Search engine (shared): returns best + archive, charges evals
# ---------------------------------------------------------------------------
def summarize_obj(s):
    return [
        float(s["constraint_violation"] + s["pending_compensation"]),
        1.0 - s["cond_rec"], 1.0 - s["r3_success"], 1.0 - s["r4_success"],
        s["avoid_harm"], s["recovery_cost"],
    ]


def dominates(a, b):
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def fast_nds(objs):
    n = len(objs)
    fronts = [[]]
    dc = [0] * n
    dom = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if dominates(objs[i], objs[j]):
                dom[i].append(j); dc[j] += 1
            elif dominates(objs[j], objs[i]):
                dom[j].append(i); dc[i] += 1
    for i in range(n):
        if dc[i] == 0:
            fronts[0].append(i)
    k = 0
    while fronts[k]:
        nxt = []
        for i in fronts[k]:
            for j in dom[i]:
                dc[j] -= 1
                if dc[j] == 0:
                    nxt.append(j)
        k += 1
        fronts.append(nxt)
    return fronts[:-1]


def crowding(objs, front):
    n = len(front)
    dist = {i: 0.0 for i in front}
    if n <= 2:
        return {i: float("inf") for i in front}
    for d in range(len(objs[0])):
        vals = sorted(front, key=lambda i: objs[i][d])
        dist[vals[0]] = dist[vals[-1]] = float("inf")
        span = objs[vals[-1]][d] - objs[vals[0]][d] or 1.0
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
    import itertools
    m = len(objs[0])
    fronts = fast_nds(objs)
    chosen, last = [], None
    for front in fronts:
        if len(chosen) + len(front) <= size:
            chosen.extend(front)
        else:
            last = front
            break
    if last is None:
        return [pop[i] for i in chosen]
    ideal = [min(o[d] for o in objs) for d in range(m)]
    shifted = [[objs[i][d] - ideal[d] for d in range(m)] for i in range(len(objs))]
    p = 3
    dirs = []
    for combo in itertools.combinations(range(p + m - 1), m - 1):
        prev, counts = -1, []
        for c in combo:
            counts.append(c - prev - 1); prev = c
        counts.append(p + m - 2 - prev)
        dirs.append([c / p for c in counts])
    def d2(vec, ref):
        w = [max(x, 1e-12) for x in ref]
        proj = sum(vec[j] * w[j] for j in range(len(vec))) / sum(x * x for x in w)
        return sum((vec[j] - proj * w[j]) ** 2 for j in range(len(vec)))
    assoc, niche = {}, {}
    for i in list(chosen) + list(last):
        best_d, best_j = None, 0
        for j, ref in enumerate(dirs):
            dd = d2(shifted[i], ref)
            if best_d is None or dd < best_d:
                best_d, best_j = dd, j
        assoc[i] = best_j
        if i in chosen:
            niche[best_j] = niche.get(best_j, 0) + 1
    need = size - len(chosen)
    remaining = list(last)
    while remaining and need > 0:
        mn = min(niche.get(assoc[i], 0) for i in remaining)
        cand = [i for i in remaining if niche.get(assoc[i], 0) == mn]
        pick = cand[rng.randrange(len(cand))]
        chosen.append(pick)
        niche[assoc[pick]] = niche.get(assoc[pick], 0) + 1
        remaining.remove(pick)
        need -= 1
    return [pop[i] for i in chosen]


def failure_profile(rows):
    prof = {"route_failures": 0, "pending_residue": 0,
            "dependency_block": 0, "budget_exhaust": 0, "early_stop": 0}
    for r in rows:
        if r["runtime_forced_abort"]:
            prof["budget_exhaust"] += 1
        if r["pending_compensation"]:
            prof["pending_residue"] += 1
        if r["residual_side_effects"] > r["min_reachable_harm"]:
            prof["dependency_block"] += 1
        if (r["policy_selected_escalation"] and not r["runtime_forced_abort"]
                and not r["class_success"]):
            prof["early_stop"] += 1
        for t in r.get("trace", []):
            if t.get("observation") == "FAILED":
                prof["route_failures"] += 1
    total = max(1, len(rows))
    return {k: v / total for k, v in prof.items()}


def run_search(scenarios, method, seed, use_anchor=True, use_pareto=True,
               use_feedback=True):
    """960-eval search. method: random | nsga2 | nsga3 | evobudget"""
    rng = random.Random(seed * 7919 + 29)
    evals = 0
    cache = {}
    archive_rows = []   # (summary, genome, rows)

    def evaluate(g):
        nonlocal evals
        fp = json.dumps(g.fingerprint(), sort_keys=True)
        if fp in cache:
            return cache[fp]
        if evals >= BUDGET:
            raise RuntimeError("budget exceeded")
        rows = evaluate_rows(lambda: D089BudgetPolicy(g), scenarios)
        s = summarize_rows(rows)
        cache[fp] = (s, rows)
        evals += 1
        return (s, rows)

    t0 = time.time()
    if method == "random":
        while evals < BUDGET:
            g = random_genome(random.Random(seed * 31 + evals * 7 + 5), ARM)
            s, rows = evaluate(g)
            archive_rows.append((s, g, rows))
    else:
        pop = []
        if use_anchor:
            for i in range(4):
                pop.append(make_anchor(random.Random(seed * 13 + i)))
        while len(pop) < POP:
            pop.append(random_genome(random.Random(seed * 131 + len(pop) * 17 + 3), ARM))
        scored = [evaluate(g) for g in pop]
        objs = [summarize_obj(s) for s, _ in scored]
        archive_rows.extend((s, g, rows) for (s, rows), g in zip(scored, pop))
        while evals < BUDGET:
            off = []
            n_off = min(POP, BUDGET - evals)
            profile = None
            if use_feedback and method == "evobudget":
                all_rows = []
                for (s, rows) in scored[-POP:]:
                    all_rows.extend(rows)
                profile = failure_profile(all_rows)
            for _ in range(n_off):
                if method == "evobudget":
                    if rng.random() < 0.7:
                        child = mutate_feedback(rng.choice(pop), rng, profile)
                    else:
                        child = crossover_segments(rng.choice(pop), rng.choice(pop), rng)
                        child = mutate_feedback(child, rng, profile)
                else:
                    if rng.random() < 0.7:
                        child = mutate(rng.choice(pop), rng)
                    else:
                        child = crossover_segments(rng.choice(pop), rng.choice(pop), rng)
                        child = mutate(child, rng)
                off.append(child)
            off_scored = [evaluate(g) for g in off]
            archive_rows.extend((s, g, rows) for (s, rows), g in zip(off_scored, off))
            combined = pop + off
            combined_s = scored + off_scored
            combined_objs = [summarize_obj(s) for s, _ in combined_s]
            if method == "nsga3":
                keep = nsga3_select(combined, combined_objs, POP, rng)
            else:
                keep = nsga2_select(combined, combined_objs, POP, rng)
            idx = {id(g): i for i, g in enumerate(combined)}
            pop = keep
            scored = [combined_s[idx[id(g)]] for g in pop]

    # ---- selection (B1) ----
    feasible = [c for c in archive_rows
                if c[0]["constraint_violation"] == 0 and c[0]["pending_compensation"] == 0]
    pool = feasible or archive_rows
    if use_pareto:
        front = pareto_front(pool)
        best = select_by_preference(front, "balanced")
    else:
        best = max(pool, key=lambda c: (
            min(c[0]["r3_success"], c[0]["r4_success"]),
            c[0]["r3_success"] + c[0]["r4_success"],
            -c[0]["avoid_harm"], -c[0]["recovery_cost"]))
    # per-preference candidates (train-time only)
    candidates = {}
    if use_pareto:
        front = pareto_front(pool)
        for pref in ("R3_priority", "R4_priority", "cost_priority", "balanced", "harm_priority"):
            sel = select_by_preference(front, pref)
            candidates[pref] = {"genome": sel[1].fingerprint(), "summary": sel[0]}
    return {
        "method": method, "seed": seed, "evals": evals,
        "seconds": round(time.time() - t0, 2),
        "use_anchor": use_anchor, "use_pareto": use_pareto,
        "best_summary": best[0], "best_genome": best[1].fingerprint(),
        "best_rows": best[2], "candidates": candidates,
        "anchor_provenance": ANCHOR_PROVENANCE if use_anchor else None,
    }


def main():
    OUT.mkdir(exist_ok=True)
    manifest = build_manifest("development")
    scenarios = manifest["scenarios"]
    print(f"[D-089] scenarios={len(scenarios)} sha={manifest['manifest_sha256'][:16]}")
    results = {"protocol": "D-089-960EVAL", "budget": BUDGET, "pop": POP,
               "seeds": SEEDS, "manifest_sha256": manifest["manifest_sha256"],
               "runs": []}

    def do(tag, **kw):
        for seed in SEEDS:
            r = run_search(scenarios, **kw, seed=seed)
            r["tag"] = tag
            results["runs"].append(r)
            s = r["best_summary"]
            print(f"  {tag}/seed{seed}: R3={s['r3_success']:.3f} R4={s['r4_success']:.3f} "
                  f"harm={s['avoid_harm']:.3f} cost={s['recovery_cost']:.1f} "
                  f"viol={s['constraint_violation']} evals={r['evals']} ({r['seconds']}s)")

    # main comparison
    do("RandomSearch", method="random")
    do("NSGA-II", method="nsga2")
    do("NSGA-III", method="nsga3")
    do("EvoBudget", method="evobudget")

    # ablations (EvoBudget minus one component each)
    do("No-Pareto-Archive", method="evobudget", use_pareto=False)
    do("No-Counterfactual-Anchor", method="evobudget", use_anchor=False)
    do("No-Feedback-Mutation", method="evobudget", use_feedback=False)

    results["report_sha256"] = hashlib.sha256(
        json.dumps(results, sort_keys=True, default=str).encode()
    ).hexdigest()
    path = OUT / "d089_search_report.json"
    path.write_text(json.dumps(results, indent=1, ensure_ascii=False, default=str) + "\n",
                    encoding="utf-8")
    print("written:", path)


if __name__ == "__main__":
    main()
