"""Evolutionary search for recovery-controller FSMs.

All methods share: the same FSM representation (a3_bridge.FSMGenome), the same
initial candidate pool, the same scenario set and the same evaluation budget
(counted in real simulator episodes). Mechanism attribution holds the NSGA-II
backbone fixed and adds only the A (contract-preserving repair) or B
(counterexample-guided) component.
"""
from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict

from a3_bridge import (
    ACTIONS,
    ERRORS,
    FSMGenome,
    Rule,
    evaluate_controller,
    is_legal,
    random_genome,
    repair_genome,
)


# ---------------------------------------------------------------------------
# Variation
# ---------------------------------------------------------------------------
def mutate(genome: FSMGenome, rng: random.Random, rate: float = 0.2) -> FSMGenome:
    g = genome.clone()
    for rule in g.rules.values():
        if rng.random() < rate:
            rule.action = rng.choice(ACTIONS)
        if rng.random() < rate * 0.5:
            rule.wait_n = rng.randint(1, 4)
    if rng.random() < rate:
        g.default_action = rng.choice(ACTIONS)
    return g


def crossover(a: FSMGenome, b: FSMGenome, rng: random.Random) -> FSMGenome:
    rules = []
    for key in sorted(set(a.rules) | set(b.rules)):
        src = a.rules[key] if (key in a.rules and rng.random() < 0.5) else b.rules.get(key)
        if src is None:
            src = a.rules.get(key) or b.rules[key]
        rules.append(src.clone())
    default = (a.default_action, a.default_wait) if rng.random() < 0.5 else (b.default_action, b.default_wait)
    return FSMGenome(rules, default)


# ---------------------------------------------------------------------------
# Mechanism A: contract-preserving repair wrapper
# ---------------------------------------------------------------------------
def op_a(genome, rng):
    return repair_genome(mutate(genome, rng))


def op_a_cross(a, b, rng):
    return repair_genome(crossover(a, b, rng))


def op_plain(genome, rng):
    return mutate(genome, rng)


def op_plain_cross(a, b, rng):
    return crossover(a, b, rng)


# ---------------------------------------------------------------------------
# Mechanism B: counterexample-guided evaluation weighting + targeting
# ---------------------------------------------------------------------------
class CounterexamplePool:
    """Clusters failing episodes by (label, dominant public error pattern)."""

    def __init__(self):
        self.weights = defaultdict(float)

    def update(self, genome, result_rows):
        self.weights.clear()
        for r in result_rows:
            if r["class_success"] in (1, None):
                continue
            key = (r["label"], int(r["invariant_violation"]), int(r["unresolved"]), int(r["duplicate"]))
            self.weights[key] += 1.0

    def scenario_weights(self, scenarios, labels):
        """Return per-scenario weight multiplier (<=2x) targeting worst clusters."""
        if not self.weights:
            return [1.0] * len(scenarios)
        # worst = clusters with most failures
        worst = sorted(self.weights.items(), key=lambda kv: -kv[1])[:3]
        worst_keys = {k for k, _ in worst}
        out = []
        for sc in scenarios:
            lab = labels[sc["scenario_id"]]
            hit = any(k[0] == lab for k in worst_keys)
            out.append(2.0 if hit else 1.0)
        return out

    def targeted_mutate(self, genome, rng, labels, scenarios):
        """Bias mutation toward rules that matter for worst clusters."""
        g = genome.clone()
        worst_lab = None
        if self.weights:
            worst_lab = sorted(self.weights.items(), key=lambda kv: -kv[1])[0][0][0]
        for rule in g.rules.values():
            p = 0.2 if (worst_lab in (None, "R1", "R2") and rule.error in ("TIMEOUT", "PARTIAL")) else 0.35
            if rng.random() < p:
                rule.action = rng.choice(ACTIONS)
        return g


# ---------------------------------------------------------------------------
# NSGA-II backbone
# ---------------------------------------------------------------------------
def dominates(u, v):
    return all(x <= y for x, y in zip(u, v)) and any(x < y for x, y in zip(u, v))


def fast_non_dominated_sort(objs):
    S = [[] for _ in objs]
    n = [0] * len(objs)
    front = [[]]
    for i in range(len(objs)):
        for j in range(len(objs)):
            if i == j:
                continue
            if dominates(objs[i], objs[j]):
                S[i].append(j)
            elif dominates(objs[j], objs[i]):
                n[i] += 1
        if n[i] == 0:
            front[0].append(i)
    k = 0
    while front[k]:
        nxt = []
        for i in front[k]:
            for j in S[i]:
                n[j] -= 1
                if n[j] == 0:
                    nxt.append(j)
        k += 1
        front.append(nxt)
    return front[:-1]


def crowding(objs, front):
    n = len(front)
    if n <= 2:
        return {i: float("inf") for i in front}
    dist = {i: 0.0 for i in front}
    m = len(objs[0])
    for d in range(m):
        srt = sorted(front, key=lambda i: objs[i][d])
        dist[srt[0]] = dist[srt[-1]] = float("inf")
        lo, hi = objs[srt[0]][d], objs[srt[-1]][d]
        span = (hi - lo) or 1.0
        for k in range(1, n - 1):
            dist[srt[k]] += (objs[srt[k + 1]][d] - objs[srt[k - 1]][d]) / span
    return dist


# ---------------------------------------------------------------------------
# NSGA-III (simplified: reference-direction niching on last front)
# ---------------------------------------------------------------------------
def reference_dirs(m=3, p=6):
    dirs = []
    for combo in itertools.combinations_with_replacement(range(p + 1), m - 1):
        pass
    # Das-Dennis simplex lattice
    def rec(remain, dims, acc):
        if dims == 1:
            acc2 = acc + [remain]
            s = sum(acc2) or 1
            dirs.append([x / s for x in acc2])
            return
        for v in range(remain + 1):
            rec(remain - v, dims - 1, acc + [v])
    rec(p, m, [])
    return dirs


def niching_select(objs, front, dirs):
    # normalize
    m = len(objs[0])
    mn = [min(objs[i][d] for i in front) for d in range(m)]
    mx = [max(objs[i][d] for i in front) for d in range(m)]
    span = [(mx[d] - mn[d]) or 1.0 for d in range(m)]
    assoc = {}
    for i in front:
        z = [(objs[i][d] - mn[d]) / span[d] for d in range(m)]
        best, bestd = None, 1e18
        for di, dvec in enumerate(dirs):
            # perpendicular distance
            t = sum(z[k] * dvec[k] for k in range(m))
            perp = math.sqrt(max(0.0, sum((z[k] - t * dvec[k]) ** 2 for k in range(m))))
            if perp < bestd:
                best, bestd = di, perp
        assoc[i] = best
    by_dir = defaultdict(list)
    for i, d in assoc.items():
        by_dir[d].append(i)
    chosen = []
    remaining = set(front)
    # niche picking
    order = sorted(by_dir, key=lambda d: len(by_dir[d]))
    while remaining and len(chosen) < len(front):
        progressed = False
        for d in order:
            cand = [i for i in by_dir[d] if i in remaining]
            if not cand:
                continue
            pick = min(cand, key=lambda i: sum(objs[i]))
            chosen.append(pick)
            remaining.discard(pick)
            progressed = True
            if len(chosen) >= len(front):
                break
        if not progressed:
            chosen.extend(sorted(remaining))
            break
    return chosen


# ---------------------------------------------------------------------------
# Evolution driver
# ---------------------------------------------------------------------------
def run_evolution(
    method,
    init_pool,
    scenarios,
    labels,
    pop_size,
    generations,
    eval_budget,
    seed,
    scenario_set_for_eval=None,
):
    """method in: random, ga, nsga2, nsga3, A, B, AB"""
    rng = random.Random(seed)
    sc_eval = scenario_set_for_eval or scenarios
    pool = [g.clone() for g in init_pool]
    rng.shuffle(pool)
    population = pool[:pop_size]
    episodes_used = 0

    def evaluate(g):
        nonlocal episodes_used
        res = evaluate_controller(g, sc_eval, labels)
        episodes_used += len(sc_eval)
        return res

    cache = {}
    def cached(g):
        key = tuple(sorted((k, r.action, r.wait_n) for k, r in g.rules.items())) + (
            g.default_action, g.default_wait)
        if key not in cache:
            cache[key] = evaluate(g)
        return cache[key]

    results = [cached(g) for g in population]
    objs = [r["objectives"] for r in results]
    history = []

    use_repair = method in ("A", "AB")
    use_cex = method in ("B", "AB")
    cex = CounterexamplePool()
    if use_cex:
        for g, r in zip(population, results):
            cex.update(g, r["rows"])

    for gen in range(generations):
        if episodes_used >= eval_budget:
            break
        # offspring
        offspring = []
        if method == "random":
            offspring = [random_genome(rng) for _ in range(pop_size)]
        else:
            while len(offspring) < pop_size:
                if method == "ga":
                    # single-objective tournament on weighted sum
                    def fit(g):
                        o = cached(g)["objectives"]
                        return sum(o)
                    a = min(rng.sample(list(range(pop_size)), 3), key=lambda i: fit(population[i]))
                    b = min(rng.sample(list(range(pop_size)), 3), key=lambda i: fit(population[i]))
                    child = op_plain_cross(population[a], population[b], rng)
                    child = op_plain(child, rng)
                else:
                    # binary tournament on dominance+crowding (NSGA-II style)
                    def pick():
                        i, j = rng.randrange(pop_size), rng.randrange(pop_size)
                        if dominates(objs[i], objs[j]):
                            return i
                        if dominates(objs[j], objs[i]):
                            return j
                        return i if rng.random() < 0.5 else j
                    a, b = pick(), pick()
                    if use_cex and rng.random() < 0.5:
                        child = cex.targeted_mutate(crossover(population[a], population[b], rng), rng, labels, sc_eval)
                    else:
                        child = op_plain_cross(population[a], population[b], rng)
                    if use_repair:
                        child = op_a(child, rng)
                    else:
                        child = op_plain(child, rng)
                if use_repair:
                    child = repair_genome(child)
                offspring.append(child)

        off_results = [cached(g) for g in offspring]
        if use_cex:
            for g, r in zip(offspring, off_results):
                cex.update(g, r["rows"])

        if method == "ga":
            combined = population + offspring
            cfit = [sum(cached(g)["objectives"]) for g in combined]
            order = sorted(range(len(combined)), key=lambda i: cfit[i])
            population = [combined[i] for i in order[:pop_size]]
            results = [cached(g) for g in population]
            objs = [r["objectives"] for r in results]
        elif method == "random":
            combined = population + offspring
            results_all = results + off_results
            objs_all = objs + [r["objectives"] for r in off_results]
            front = fast_non_dominated_sort(objs_all)
            picked = front[0][:pop_size]
            if len(picked) < pop_size:
                for f in front[1:]:
                    picked.extend(f)
                    if len(picked) >= pop_size:
                        break
            population = [combined[i] for i in picked[:pop_size]]
            results = [results_all[i] for i in picked[:pop_size]]
            objs = [r["objectives"] for r in results]
        else:
            combined = population + offspring
            results_all = results + off_results
            objs_all = [r["objectives"] for r in results_all]
            fronts = fast_non_dominated_sort(objs_all)
            picked = []
            for f in fronts:
                if len(picked) + len(f) <= pop_size:
                    picked.extend(f)
                else:
                    remain = pop_size - len(picked)
                    if method == "nsga3":
                        picked.extend(niching_select(objs_all, f, reference_dirs())[:remain])
                    else:
                        cd = crowding(objs_all, f)
                        picked.extend(sorted(f, key=lambda i: -cd[i])[:remain])
                    break
            population = [combined[i] for i in picked]
            results = [results_all[i] for i in picked]
            objs = [r["objectives"] for r in results]

        best = min(objs, key=lambda o: sum(o))
        illegal = sum(0 if is_legal(g) else 1 for g in population)
        history.append(
            {
                "gen": gen,
                "episodes": episodes_used,
                "best_sum_obj": sum(best),
                "illegal_ratio": illegal / len(population),
                "mean_cond_rec": sum(r["cond_rec"] for r in results) / len(results),
            }
        )

    best_idx = min(range(len(population)), key=lambda i: sum(objs[i]))
    return {
        "method": method,
        "seed": seed,
        "best": population[best_idx],
        "best_result": results[best_idx],
        "final_population": population,
        "final_results": results,
        "episodes": episodes_used,
        "history": history,
    }
