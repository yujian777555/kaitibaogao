"""D-090 小规模 Train-only 对照。

比较 Random Search、NSGA-II、NSGA-III、State-Conditioned Evolution 和
State-Conditioned Random Search。所有方法共享冻结的 D-089 B3 基础，
只搜索状态条件化规则块。
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "d089_recovery"))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))
from d089_search_experiment import nsga2_select, nsga3_select  # noqa: E402
from dependency_recovery import run_episode  # noqa: E402
from d090_genome import D090Genome, base_genome, crossover_blocks, mutate_d090, random_d090_genome  # noqa: E402
from d090_policies import D090Policy  # noqa: E402
from d090_scenarios import build_manifest  # noqa: E402

SEEDS = (711, 822, 933)
POP = 12
GENERATIONS = 6
BUDGET = 96


def summarize(rows):
    def mean(values):
        return sum(values) / len(values) if values else 0.0
    r12 = [r for r in rows if r["label"] in ("R1", "R2")]
    r3 = [r for r in rows if r["label"] == "R3"]
    r4 = [r for r in rows if r["label"] == "R4"]
    return {
        "n": len(rows),
        "cond_rec": mean([r["conditional_recovery_success"] for r in r12]),
        "r3_success": mean([r["correct_escalation"] for r in r3]),
        "r4_success": mean([r["class_success"] for r in r4]),
        "harm": mean([r["avoidable_harm"] for r in rows]),
        "recovery_cost": mean([r["recovery_cost"] for r in rows]),
        "constraint_violation": sum(r["constraint_violation"] for r in rows),
        "duplicate_compensation": sum(r["duplicate_compensation"] for r in rows),
        "pending_compensation": sum(r["pending_compensation"] for r in rows),
    }


def objectives(summary):
    return [float(summary["constraint_violation"] + summary["pending_compensation"]),
            1 - summary["cond_rec"], 1 - summary["r3_success"],
            1 - summary["r4_success"], summary["harm"], summary["recovery_cost"]]


def evaluate(genome, scenarios):
    rows = [run_episode(D090Policy(genome), scenario, max_actions=24) for scenario in scenarios]
    return summarize(rows), rows


def _best(pool):
    feasible = [item for item in pool if item[0]["constraint_violation"] == 0 and item[0]["pending_compensation"] == 0]
    pool = feasible or pool
    return max(pool, key=lambda x: (min(x[0]["r3_success"], x[0]["r4_success"]),
                                    x[0]["r3_success"] + x[0]["r4_success"],
                                    -x[0]["harm"], -x[0]["recovery_cost"]))


def run_method(method, scenarios, seed):
    rng = random.Random(seed * 7919 + 17)
    cache = {}
    archive = []
    evals = 0

    def score(g):
        nonlocal evals
        key = json.dumps(g.fingerprint(), sort_keys=True)
        if key not in cache:
            if evals >= BUDGET:
                raise RuntimeError("D090 budget exceeded")
            cache[key] = evaluate(g, scenarios)
            evals += 1
        return cache[key]

    if method == "state_random":
        while evals < BUDGET:
            g = random_d090_genome(rng)
            s, rows = score(g)
            archive.append((s, g, rows))
    else:
        pop = [random_d090_genome(random.Random(seed * 131 + i * 17 + 3)) for i in range(POP)]
        scored = [score(g) for g in pop]
        archive.extend((s, g, rows) for g, (s, rows) in zip(pop, scored))
        while evals < BUDGET:
            offspring = []
            while len(offspring) < min(POP, BUDGET - evals):
                if method == "state_evo":
                    if rng.random() < 0.7:
                        child = mutate_d090(rng.choice(pop), rng, {"pair": 1.0, "fallback": 1.0, "completion": 1.0, "harm": 1.0})
                    else:
                        child = mutate_d090(crossover_blocks(rng.choice(pop), rng.choice(pop), rng), rng)
                else:
                    if rng.random() < 0.7:
                        child = mutate_d090(rng.choice(pop), rng)
                    else:
                        child = mutate_d090(crossover_blocks(rng.choice(pop), rng.choice(pop), rng), rng)
                offspring.append(child)
            off_scored = [score(g) for g in offspring]
            archive.extend((s, g, rows) for g, (s, rows) in zip(offspring, off_scored))
            combined = pop + offspring
            combined_scores = scored + off_scored
            objs = [objectives(s) for s, _ in combined_scores]
            if method == "nsga3":
                pop = nsga3_select(combined, objs, POP, rng)
            else:
                pop = nsga2_select(combined, objs, POP, rng)
            index = {id(g): i for i, g in enumerate(combined)}
            scored = [combined_scores[index[id(g)]] for g in pop]
    best_summary, best_genome, best_rows = _best(archive)
    return {"method": method, "seed": seed, "evals": evals,
            "best_summary": best_summary, "best_genome": best_genome.fingerprint(),
            "best_rows": best_rows}


def run_experiment(budget=BUDGET):
    global BUDGET
    BUDGET = budget
    manifest = build_manifest()
    scenarios = manifest["scenarios"]
    methods = ("random", "nsga2", "nsga3", "state_evo", "state_random")
    runs = []
    for method in methods:
        for seed in SEEDS:
            runs.append(run_method(method, scenarios, seed))
    report = {"protocol_id": "D-090-TRAIN-SMALL", "manifest_sha256": manifest["manifest_sha256"],
              "scenario_count": len(scenarios), "budget": BUDGET, "pop": POP,
              "generations": GENERATIONS, "seeds": list(SEEDS), "runs": runs}
    report["report_sha256"] = hashlib.sha256(json.dumps(report, sort_keys=True, default=str).encode()).hexdigest()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "d090_train_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / "d090_train_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=BUDGET)
    args = parser.parse_args()
    result = run_experiment(args.budget)
    print(result["report_sha256"])
