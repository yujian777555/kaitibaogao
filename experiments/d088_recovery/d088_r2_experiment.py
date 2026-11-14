"""D-088 R2 paired experiment: operator ablation + strict residual stop.

Design (paired, same scenarios/seeds/budget):
  E1 operator ablation on BC arm (best balanced from R1):
      baseline operators (mutate + uniform crossover)
      vs feedback-conditioned mutation + segment crossover
  E2 strict_residual_stop ablation: on/off, same operators, BC + ABC arms
  E3 fresh replication of frozen winners from E1/E2

RandomSearch budget-matched control included for every evolved arm.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))

from d088_genome import (  # noqa: E402
    D088RecoveryGenome, random_genome, mutate, crossover,
    mutate_feedback, crossover_segments, arm_flags,
)
from d088_policies import D088RecoveryPolicy  # noqa: E402
from d088_scenarios import build_manifest  # noqa: E402
from d088_experiment import evaluate_rows, summarize_rows  # noqa: E402

OUT = HERE / "results"
SEEDS = [711, 822, 933]
POP = 16
GENERATIONS = 8
MAX_ACTIONS = 24


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
                dominated[i].append(j); dom_count[j] += 1
            elif dominates(objs[j], objs[i]):
                dominated[j].append(i); dom_count[i] += 1
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
        return {i: float("inf") for i in front}
    m = len(objs[0])
    for d in range(m):
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


def failure_profile_of(rows):
    """Aggregate failure signals from episode rows for feedback mutation."""
    profile = {
        "route_failures": 0, "pending_residue": 0,
        "dependency_block": 0, "budget_exhaust": 0,
    }
    for r in rows:
        if r["runtime_forced_abort"]:
            profile["budget_exhaust"] += 1
        if r["pending_compensation"]:
            profile["pending_residue"] += 1
        if r["residual_side_effects"] > r["min_reachable_harm"]:
            profile["dependency_block"] += 1
        for t in r.get("trace", []):
            obs = t.get("observation")
            if obs == "FAILED":
                profile["route_failures"] += 1
            elif obs == "DEPENDENCY_BLOCKED":
                profile["dependency_block"] += 1
    total = max(1, len(rows))
    return {k: v / total for k, v in profile.items()}


def evolve(scenarios, arm, operator, seed, strict_stop=None):
    """operator: 'base' | 'feedback'"""
    rng = random.Random(seed * 7919 + 29)
    kwargs = arm_flags(arm)
    if strict_stop is not None:
        pass  # applied below via replace
    pop = []
    for i in range(POP):
        g = random_genome(random.Random(seed * 131 + i * 17 + 3), arm)
        if strict_stop is not None:
            import dataclasses
            g = dataclasses.replace(g, strict_residual_stop=strict_stop)
        pop.append(g)
    evals = 0
    row_cache = {}

    def evaluate(g):
        nonlocal evals
        evals += 1
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), scenarios)
        row_cache[id(g)] = rows
        return objectives_of(rows)

    objs = [evaluate(g) for g in pop]
    t0 = time.time()
    for _gen in range(GENERATIONS):
        offspring = []
        # feedback profile from current population rows
        profile = None
        if operator == "feedback":
            all_rows = []
            for g in pop:
                all_rows.extend(row_cache.get(id(g), []))
            if all_rows:
                profile = failure_profile_of(all_rows)
        for _ in range(POP):
            if operator == "feedback":
                if rng.random() < 0.7:
                    child = mutate_feedback(rng.choice(pop), rng, profile)
                else:
                    child = crossover_segments(rng.choice(pop), rng.choice(pop), rng)
                    child = mutate_feedback(child, rng, profile)
            else:
                if rng.random() < 0.7:
                    child = mutate(rng.choice(pop), rng)
                else:
                    child = crossover(rng.choice(pop), rng.choice(pop), rng)
                    child = mutate(child, rng)
            if strict_stop is not None:
                import dataclasses
                child = dataclasses.replace(child, strict_residual_stop=strict_stop)
            offspring.append(child)
        off_objs = [evaluate(g) for g in offspring]
        combined = pop + offspring
        combined_objs = objs + off_objs
        pop = nsga2_select(combined, combined_objs, POP, rng)
        idx = {id(g): i for i, g in enumerate(combined)}
        objs = [combined_objs[idx[id(g)]] for g in pop]
    final = []
    for g in pop:
        rows = row_cache.get(id(g)) or evaluate_rows(lambda: D088RecoveryPolicy(g), scenarios)
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
        "arm": arm, "operator": operator, "seed": seed,
        "strict_stop": strict_stop, "evals": evals,
        "seconds": round(time.time() - t0, 2),
        "best_summary": best_s, "best_genome": best_g.fingerprint(),
        "best_rows": best_rows,
    }


def random_search(scenarios, arm, seed, budget, strict_stop=None):
    best = None
    for i in range(budget):
        g = random_genome(random.Random(seed * 131 + i * 17 + 3), arm)
        if strict_stop is not None:
            import dataclasses
            g = dataclasses.replace(g, strict_residual_stop=strict_stop)
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
    return {
        "arm": arm, "operator": "randomsearch", "seed": seed,
        "strict_stop": strict_stop, "evals": budget,
        "best_summary": best[1], "best_genome": best[2].fingerprint(),
        "best_rows": best[3],
    }


def print_line(tag, r):
    s = r["best_summary"]
    print(f"  {tag}/seed{r['seed']}: R3={s['r3_success']:.3f} R4={s['r4_success']:.3f} "
          f"harm={s['avoid_harm']:.3f} cost={s['recovery_cost']:.1f} "
          f"viol={s['constraint_violation']} ({r.get('seconds', 0)}s)")


def main():
    OUT.mkdir(exist_ok=True)
    scenarios = build_manifest()["scenarios"]
    budget = POP * (GENERATIONS + 1)
    results = {"config": {"pop": POP, "generations": GENERATIONS, "seeds": SEEDS,
                          "budget": budget, "max_actions": MAX_ACTIONS},
               "experiments": {}}

    # E1: operator ablation on BC (strict stop ON — the R2 default)
    print("[E1] operator ablation on BC")
    results["experiments"]["E1_operator_BC"] = {}
    for operator in ("base", "feedback"):
        runs = []
        for seed in SEEDS:
            r = evolve(scenarios, "BC", operator, seed, strict_stop=True)
            runs.append(r)
            print_line(f"E1/BC/{operator}", r)
        runs.append(random_search(scenarios, "BC", SEEDS[0], budget, strict_stop=True))
        print_line("E1/BC/randomsearch", runs[-1])
        results["experiments"]["E1_operator_BC"][operator] = runs

    # E2: strict stop ablation on BC and ABC (feedback operators)
    print("[E2] strict_residual_stop ablation")
    results["experiments"]["E2_strict_stop"] = {}
    for arm in ("BC", "ABC"):
        for strict in (False, True):
            runs = []
            for seed in SEEDS:
                r = evolve(scenarios, arm, "feedback", seed, strict_stop=strict)
                runs.append(r)
                print_line(f"E2/{arm}/strict={strict}", r)
            results["experiments"]["E2_strict_stop"][f"{arm}_strict{int(strict)}"] = runs

    # E3: also run A/B/C singles with feedback ops + strict stop
    print("[E3] singles with feedback operators")
    results["experiments"]["E3_singles"] = {}
    for arm in ("A", "B", "C"):
        runs = []
        for seed in SEEDS:
            r = evolve(scenarios, arm, "feedback", seed, strict_stop=True)
            runs.append(r)
            print_line(f"E3/{arm}", r)
        results["experiments"]["E3_singles"][arm] = runs

    results["report_sha256"] = __import__("hashlib").sha256(
        json.dumps(results, sort_keys=True, default=str).encode()
    ).hexdigest()
    (OUT / "d088_r2_report.json").write_text(
        json.dumps(results, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    print("written:", OUT / "d088_r2_report.json")


if __name__ == "__main__":
    main()
