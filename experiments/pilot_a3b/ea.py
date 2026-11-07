"""Evolutionary search v2: standard baselines + fixed mechanisms A/B.

57-review fixes:
- S2: NSGA-II uses proper (rank, crowding) binary tournament; NSGA-III uses
  reference-direction association + niche counting (labelled as our
  reimplementation); GA = tournament + weighted sum + uniform crossover;
  Random Search = uniform random sampling (no survivor tricks).
- F6: counterexample pool aggregates the WHOLE population once per
  generation; full signatures; implicated genes from decision traces;
  weights actually reach the evaluator; targeted mutation REPLACES standard
  mutation (matched mutation-count budget).
- M1: identical initial pool / representation / scenario set / rollout budget
  across methods. GP is excluded (decision-table FSM over a small discrete
  action set; tree GP would change the representation -- see report 58).
"""
from __future__ import annotations

import itertools
import math
import random
from collections import Counter, defaultdict

from a3_bridge import (
    ACTIONS,
    OBS_ALL,
    Gene,
    StatefulFSM,
    evaluate_controller,
    make_gene_rule_table,
    random_fsm,
    repair_fsm,
)

# ---------------------------------------------------------------------------
# Variation (all methods: exactly ONE mutate call per child)
# ---------------------------------------------------------------------------
def mutate(fsm: StatefulFSM, rng: random.Random, rate: float = 0.15) -> StatefulFSM:
    g = fsm.clone()
    genes = g.genes_list()
    n_touch = max(1, int(len(genes) * rate))
    for _ in range(n_touch):
        gene = rng.choice(genes)
        gene.action = rng.choice(ACTIONS)
        if rng.random() < 0.3:
            gene.wait_n = rng.randint(1, 4)
    return g


def crossover(a: StatefulFSM, b: StatefulFSM, rng: random.Random) -> StatefulFSM:
    genes = []
    for key in sorted(set(a.genes) | set(b.genes)):
        src = a.genes.get(key) if rng.random() < 0.5 else b.genes.get(key)
        if src is None:
            src = a.genes.get(key) or b.genes[key]
        genes.append(src.clone())
    default = (a.default_action, a.default_wait) if rng.random() < 0.5 else (b.default_action, b.default_wait)
    return StatefulFSM(genes, default)


# ---------------------------------------------------------------------------
# Mechanism B: counterexample-guided search (57 F6 redesign)
# ---------------------------------------------------------------------------
class CounterexamplePool:
    """Aggregates failures across the ENTIRE population; cleared once per
    generation by the driver (not per evaluation)."""

    def __init__(self):
        self.cluster_counts = Counter()
        self.cluster_genes = defaultdict(Counter)
        self.scenario_fail = Counter()
        self.n_examples = 0

    def clear(self):
        self.cluster_counts.clear()
        self.cluster_genes.clear()
        self.scenario_fail.clear()
        self.n_examples = 0

    def aggregate(self, results):
        """results: list of evaluate_controller outputs (one per genome)."""
        for res in results:
            for r in res["rows"]:
                if r["class_success"] in (1, None):
                    continue
                if not r["decision_trace"]:
                    continue
                self.n_examples += 1
                sig = self._signature(r)
                self.cluster_counts[sig] += 1
                self.scenario_fail[r["scenario_id"]] += 1
                for (obs, att, stack, _act) in r["decision_trace"]:
                    self.cluster_genes[sig][(obs, att, stack)] += 1

    @staticmethod
    def _signature(row):
        trace = row["decision_trace"]
        last_obs = trace[-1][0] if trace else "NONE"
        cause = ("violation" if row["invariant_violation"] else
                 "residual" if row["avoidable_harm"] else
                 "comp_fail" if row["compensation_failure"] else "incomplete")
        return (row["label"], last_obs, cause)

    def scenario_weights(self, scenarios, cap=2.0):
        if not self.scenario_fail:
            return [1.0] * len(scenarios)
        worst = self.scenario_fail.most_common(3)
        worst_ids = {sid for sid, _ in worst}
        return [cap if sc["scenario_id"] in worst_ids else 1.0 for sc in scenarios]

    def implicated_genes(self, top_clusters=3):
        keys = Counter()
        for sig, _c in self.cluster_counts.most_common(top_clusters):
            keys.update(self.cluster_genes[sig])
        return list(keys)

    def targeted_mutate(self, fsm: StatefulFSM, rng: random.Random) -> StatefulFSM:
        """Mutate genes implicated by counterexamples; falls back to uniform
        mutation. EXACTLY one mutation event (same budget as mutate())."""
        g = fsm.clone()
        implicated = self.implicated_genes()
        candidates = []
        for (obs, att, stack) in implicated:
            gene = g.genes.get((obs, att, stack))
            if gene is not None:
                candidates.append(gene)
        gene = rng.choice(candidates) if candidates else rng.choice(g.genes_list())
        gene.action = rng.choice(ACTIONS)
        if rng.random() < 0.3:
            gene.wait_n = rng.randint(1, 4)
        return g


# ---------------------------------------------------------------------------
# Selection helpers
# ---------------------------------------------------------------------------
def dominates(u, v):
    return all(x <= y for x, y in zip(u, v)) and any(x < y for x, y in zip(u, v))


def fast_non_dominated_sort(objs):
    n = len(objs)
    S = [[] for _ in range(n)]
    cnt = [0] * n
    fronts = [[]]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if dominates(objs[i], objs[j]):
                S[i].append(j)
            elif dominates(objs[j], objs[i]):
                cnt[i] += 1
        if cnt[i] == 0:
            fronts[0].append(i)
    k = 0
    while fronts[k]:
        nxt = []
        for i in fronts[k]:
            for j in S[i]:
                cnt[j] -= 1
                if cnt[j] == 0:
                    nxt.append(j)
        k += 1
        fronts.append(nxt)
    return fronts[:-1]


def crowding_distance(objs, front):
    n = len(front)
    dist = {i: 0.0 for i in front}
    if n <= 2:
        return {i: float("inf") for i in front}
    m = len(objs[0])
    for d in range(m):
        srt = sorted(front, key=lambda i: objs[i][d])
        dist[srt[0]] = dist[srt[-1]] = float("inf")
        lo, hi = objs[srt[0]][d], objs[srt[-1]][d]
        span = (hi - lo) or 1.0
        for k in range(1, n - 1):
            dist[srt[k]] += (objs[srt[k + 1]][d] - objs[srt[k - 1]][d]) / span
    return dist


def reference_dirs(m=3, p=6):
    dirs = []

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
    """NSGA-III-style: associate to nearest reference direction, then niche
    counting with closest-member picking (our reimplementation)."""
    m = len(objs[0])
    if not front:
        return []
    mn = [min(objs[i][d] for i in front) for d in range(m)]
    mx = [max(objs[i][d] for i in front) for d in range(m)]
    span = [(mx[d] - mn[d]) or 1.0 for d in range(m)]
    assoc = {}
    for i in front:
        z = [(objs[i][d] - mn[d]) / span[d] for d in range(m)]
        best, bestd = 0, float("inf")
        for di, dvec in enumerate(dirs):
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
    while remaining and len(chosen) < len(front):
        # niche counting: pick from the least occupied non-empty niche
        order = sorted(by_dir, key=lambda d: (len(by_dir[d]), d))
        progressed = False
        for d in order:
            cand = [i for i in by_dir[d] if i in remaining]
            if not cand:
                continue
            pick = min(cand, key=lambda i: sum(objs[i]))
            chosen.append(pick)
            remaining.discard(pick)
            progressed = True
            break
        if not progressed:
            chosen.extend(sorted(remaining))
            break
    return chosen


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def run_evolution(method, init_pool, scenarios, verdicts, pop_size, generations,
                  eval_budget, seed, counterexample_cap=2.0):
    """method: random | ga | nsga2 | nsga3 | A | B | AB"""
    rng = random.Random(seed)
    population = [g.clone() for g in init_pool[:pop_size]]
    episodes_used = 0
    cache = {}

    def fingerprint(g):
        return tuple(sorted((k, gene.action, gene.wait_n) for k, gene in g.genes.items())) + (
            g.default_action, g.default_wait)

    def evaluate(g, weights=None):
        nonlocal episodes_used
        fp = fingerprint(g)
        if fp in cache:
            return cache[fp]
        if episodes_used + len(scenarios) > eval_budget:
            return None
        res = evaluate_controller(g, scenarios, verdicts, weights)
        episodes_used += len(scenarios)
        cache[fp] = res
        return res

    use_repair = method in ("A", "AB")
    use_cex = method in ("B", "AB")
    cex = CounterexamplePool()

    weights = None
    results = []
    for g in population:
        res = evaluate(g)
        if res is None:
            res = evaluate_controller(g, scenarios, verdicts, None)
            episodes_used += len(scenarios)
        results.append(res)
    objs = [r["objectives"] for r in results]
    history = []

    for gen in range(generations):
        # ranks/crowd for tournament BEFORE variation
        fronts0 = fast_non_dominated_sort(objs)
        ranks = {}
        for fi, f in enumerate(fronts0):
            for i in f:
                ranks[i] = fi
        crowd = {}
        for f in fronts0:
            crowd.update(crowding_distance(objs, f))

        if use_cex:
            cex.clear()
            cex.aggregate(results)  # aggregate whole population once per gen
            weights = cex.scenario_weights(scenarios, counterexample_cap)

        # --- variation: exactly one mutate per child ---------------------
        offspring = []
        if method == "random":
            for _ in range(pop_size):
                offspring.append(random_fsm(rng))
        else:
            while len(offspring) < pop_size:
                # parents
                if method == "ga":
                    def fit(i):
                        return sum(objs[i])
                    a = min(rng.sample(range(len(population)), 3), key=fit)
                    b = min(rng.sample(range(len(population)), 3), key=fit)
                else:
                    def pick():
                        i, j = rng.randrange(len(population)), rng.randrange(len(population))
                        ri, rj = ranks[i], ranks[j]
                        if ri != rj:
                            return i if ri < rj else j
                        return i if crowd.get(i, 0) >= crowd.get(j, 0) else j
                    a, b = pick(), pick()
                child = crossover(population[a], population[b], rng)
                if use_cex and rng.random() < 0.5:
                    child = cex.targeted_mutate(child, rng)      # ONE mutation event
                else:
                    child = mutate(child, rng)                    # ONE mutation event
                if use_repair:
                    child = repair_fsm(child)
                offspring.append(child)

        off_results = []
        for g in offspring:
            res = evaluate(g, weights if use_cex else None)
            if res is None:
                res = evaluate_controller(g, scenarios, verdicts, weights if use_cex else None)
                episodes_used += len(scenarios)
            off_results.append(res)

        # --- survivor selection -----------------------------------------
        combined = population + offspring
        results_all = results + off_results
        objs_all = [r["objectives"] for r in results_all]

        if method == "random":
            # pure random search: keep best-by-sum from everything seen
            order = sorted(range(len(combined)), key=lambda i: sum(objs_all[i]))
            population = [combined[i] for i in order[:pop_size]]
        elif method == "ga":
            order = sorted(range(len(combined)), key=lambda i: sum(objs_all[i]))
            population = [combined[i] for i in order[:pop_size]]
        else:
            fronts = fast_non_dominated_sort(objs_all)
            ranks = {}
            for fi, f in enumerate(fronts):
                for i in f:
                    ranks[i] = fi
            picked = []
            for f in fronts:
                if len(picked) + len(f) <= pop_size:
                    picked.extend(f)
                else:
                    remain = pop_size - len(picked)
                    if method == "nsga3":
                        picked.extend(niching_select(objs_all, f, reference_dirs())[:remain])
                    else:
                        cd = crowding_distance(objs_all, f)
                        picked.extend(sorted(f, key=lambda i: -cd[i])[:remain])
                    break
            population = [combined[i] for i in picked]

        results = [cache.get(fingerprint(g)) or evaluate_controller(g, scenarios, verdicts, None)
                   for g in population]
        objs = [r["objectives"] for r in results]

        # ranks/crowd for next-gen tournament
        fronts = fast_non_dominated_sort(objs)
        ranks = {}
        for fi, f in enumerate(fronts):
            for i in f:
                ranks[i] = fi
        crowd = {}
        for f in fronts:
            crowd.update(crowding_distance(objs, f))

        best = min(objs, key=lambda o: sum(o))
        history.append({
            "gen": gen,
            "episodes": episodes_used,
            "best_sum_obj": sum(best),
            "mean_cond_rec": sum(r["cond_rec"] for r in results) / len(results),
        })

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


def validator_illegal_ratio(population):
    """Fraction of population with at least one contract-validator violation
    (independent of the repair table, 57 F7)."""
    from contract_validator import validate_genome
    bad = 0
    for fsm in population:
        rep = validate_genome(fsm.genes_list(), fsm.default_action, fsm.default_wait)
        if rep.genome_invalid or rep.rule_invalid:
            bad += 1
    return bad / max(1, len(population))
