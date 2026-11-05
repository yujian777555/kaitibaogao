"""Pilot B: contract-constrained evolutionary search over recovery controllers.

Uses fresh seeds only:
  train 1000-1039, validation 1100-1119, test 1120-1159.
The test panel is evaluated once after algorithm selection.
"""
from __future__ import annotations
import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.pilot_a2_multitool.pilot_a2 import (
    Env, TOOLS, PROFILES, make_episode, METRICS
)

WAIT_FACTORS = (0.0, 0.5, 1.0, 1.25)
GENE_SIZES = (2, 3, 3, 4, 2, 2, 4, 2, 4)
GENOME_LEN = len(GENE_SIZES)
TASK_SUCCESS_FLOOR = 0.70
POPULATION = 16
GENERATIONS = 10
EVAL_BUDGET = POPULATION * GENERATIONS
ALGORITHM_SEEDS = (13, 29, 47)
TRAIN_SEEDS = tuple(range(1000, 1040))
VALIDATION_SEEDS = tuple(range(1100, 1120))
TEST_SEEDS = tuple(range(1120, 1160))
ALGORITHMS = ("random_valid_fsm", "standard_ga", "contract_preserving_ga", "nsga2")

# Genome:
# 0 timeout on idempotent tool: 0=same-key retry, 1=verify first
# 1 timeout on non-idempotent tool: 0=bounded wait+verify, 1=escalate, 2=immediate verify
# 2 partial outcome: 0=direct compensate, 1=wait+verify+compensate, 2=escalate
# 3 partial wait factor; 4 schema handling; 5 rate handling
# 6 retry-after wait factor; 7 keyed retry; 8 non-idempotent visibility wait factor
MANUAL_V1 = (0, 0, 1, 2, 0, 0, 2, 0, 2)
MANUAL_V2 = (0, 0, 0, 0, 0, 0, 2, 0, 2)

def random_genome(rng: random.Random) -> tuple[int, ...]:
    return tuple(rng.randrange(n) for n in GENE_SIZES)

def repair_contracts(g: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    x = list(g)
    # Never retry a non-idempotent operation before the declared visibility bound.
    x[1] = 0
    # A partial response can be compensated directly; if verify-first is chosen,
    # wait at least the contractual visibility bound.
    if x[2] == 1:
        x[3] = max(2, x[3])
    # Repair known schema faults and respect retry-after headers.
    x[4] = 0
    x[5] = 0
    x[6] = max(2, x[6])
    # Preserve idempotency keys for keyed tools.
    x[7] = 0
    x[8] = max(2, x[8])
    return tuple(x)

def execute_genome(spec: dict, genome: tuple[int, ...]) -> dict:
    env = Env(spec)
    obs = env.observe()
    c = obs["contract"]
    signals = set(obs["signals"])

    def retry() -> str:
        action = "RETRY_WITH_KEY" if c["idempotency"] == "keyed" and genome[7] == 0 else "RETRY"
        result = env.act(action)
        if result in ("RATE_LIMITED", "PERMISSION_DENIED", "SCHEMA_REJECTED"):
            env.act("ESCALATE")
        return result

    def handle_partial() -> None:
        if genome[2] == 2:
            env.act("ESCALATE")
            return
        if genome[2] == 1:
            if c["consistency"] == "eventual":
                env.act("WAIT", math.ceil(c["max_visibility_delay"] * WAIT_FACTORS[genome[3]]))
            status = env.act("VERIFY")
            if status != "PARTIAL":
                env.act("ESCALATE")
                return
        if c["compensable"]:
            if env.act("COMPENSATE") == "COMPENSATED":
                retry()
            else:
                env.act("ESCALATE")
        else:
            env.act("ESCALATE")

    if not obs["permission"]:
        env.act("ESCALATE")
    else:
        if not obs["schema_valid"]:
            if genome[4] == 0:
                env.act("REPAIR_SCHEMA")
            else:
                env.act("ESCALATE")
        if "RATE_LIMIT" in signals:
            if genome[5] == 0:
                env.act("WAIT", math.ceil(obs["retry_after"] * WAIT_FACTORS[genome[6]]))
            else:
                env.act("ESCALATE")

        if not env.escalated:
            if "PARTIAL_RESPONSE" in signals:
                handle_partial()
            elif "TIMEOUT" in signals:
                if c["idempotency"] in ("native", "keyed") and genome[0] == 0:
                    result = retry()
                    # The idempotency service's response is observable and
                    # distinguishes the prior committed/partial operation.
                    if result == "ALREADY_PARTIAL":
                        handle_partial()
                elif c["idempotency"] == "none" and genome[1] == 1:
                    env.act("ESCALATE")
                else:
                    if c["consistency"] == "eventual":
                        if c["idempotency"] == "none":
                            factor = WAIT_FACTORS[genome[8]]
                        else:
                            factor = WAIT_FACTORS[genome[8]]
                        env.act("WAIT", math.ceil(c["max_visibility_delay"] * factor))
                    status = env.act("VERIFY")
                    if status == "COMMITTED":
                        pass
                    elif status == "PARTIAL":
                        handle_partial()
                    elif status == "NOT_FOUND":
                        retry()
            else:
                retry()

    result = env.result()
    return result

def evaluate(genome: tuple[int, ...], seeds: tuple[int, ...]) -> dict:
    rows = [
        execute_genome(make_episode(tool, profile, seed), genome)
        for tool in TOOLS for profile in PROFILES for seed in seeds
    ]
    n = len(rows)
    metrics = {
        "task_success": sum(r["task_success"] for r in rows) / n,
        "invariant_violation": sum(r["invariant_violation"] for r in rows) / n,
        "tool_actions": sum(r["tool_actions"] for r in rows) / n,
        "wait_units": sum(r["wait_units"] for r in rows) / n,
        "safe_resolution": sum(r["safe_resolution"] for r in rows) / n,
        "escalated": sum(r["escalated"] for r in rows) / n,
    }
    metrics["feasible"] = int(
        metrics["invariant_violation"] == 0.0
        and metrics["task_success"] >= TASK_SUCCESS_FLOOR
    )
    metrics["cost"] = metrics["tool_actions"] + 0.1 * metrics["wait_units"]
    return metrics

def fitness_key(m: dict) -> tuple:
    return (
        0 if m["feasible"] else 1,
        m["invariant_violation"],
        max(0.0, TASK_SUCCESS_FLOOR - m["task_success"]),
        m["cost"],
        -m["task_success"],
    )

def tournament(pop, scores, rng, k=3):
    choices = [rng.randrange(len(pop)) for _ in range(k)]
    return min(choices, key=lambda i: fitness_key(scores[i]))

def crossover(a, b, rng):
    return tuple(a[i] if rng.random() < 0.5 else b[i] for i in range(GENOME_LEN))

def mutate(g, rng):
    x = list(g)
    for _ in range(1 + int(rng.random() < 0.25)):
        j = rng.randrange(GENOME_LEN)
        x[j] = rng.randrange(GENE_SIZES[j])
    return tuple(x)

def dominates(a, b):
    av = (a["invariant_violation"], max(0, TASK_SUCCESS_FLOOR-a["task_success"]),
          a["tool_actions"], a["wait_units"])
    bv = (b["invariant_violation"], max(0, TASK_SUCCESS_FLOOR-b["task_success"]),
          b["tool_actions"], b["wait_units"])
    return all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv))

def nondominated_fronts(scores):
    n = len(scores)
    dominated = [[] for _ in range(n)]
    count = [0] * n
    fronts = [[]]
    for p in range(n):
        for q in range(n):
            if p == q: continue
            if dominates(scores[p], scores[q]):
                dominated[p].append(q)
            elif dominates(scores[q], scores[p]):
                count[p] += 1
        if count[p] == 0:
            fronts[0].append(p)
    i = 0
    while i < len(fronts) and fronts[i]:
        nxt = []
        for p in fronts[i]:
            for q in dominated[p]:
                count[q] -= 1
                if count[q] == 0:
                    nxt.append(q)
        if nxt: fronts.append(nxt)
        i += 1
    return fronts

def crowding(front, scores):
    if len(front) <= 2:
        return {i: float("inf") for i in front}
    keys = ("invariant_violation", "task_success", "tool_actions", "wait_units")
    distances = {i: 0.0 for i in front}
    for key in keys:
        ordered = sorted(front, key=lambda i: scores[i][key])
        distances[ordered[0]] = distances[ordered[-1]] = float("inf")
        lo, hi = scores[ordered[0]][key], scores[ordered[-1]][key]
        if hi == lo: continue
        for j in range(1, len(ordered)-1):
            distances[ordered[j]] += (
                scores[ordered[j+1]][key] - scores[ordered[j-1]][key]
            ) / (hi-lo)
    return distances

def nsga_select(pop, scores, size):
    chosen = []
    for front in nondominated_fronts(scores):
        if len(chosen) + len(front) <= size:
            chosen.extend(front)
        else:
            cd = crowding(front, scores)
            chosen.extend(sorted(front, key=lambda i: cd[i], reverse=True)[:size-len(chosen)])
            break
    return [pop[i] for i in chosen], [scores[i] for i in chosen]

def search(algorithm: str, seed: int) -> dict:
    rng = random.Random(seed)
    pop = [random_genome(rng) for _ in range(POPULATION)]
    if algorithm in ("random_valid_fsm", "contract_preserving_ga"):
        pop = [repair_contracts(g) for g in pop]
    scores = [evaluate(g, TRAIN_SEEDS) for g in pop]
    evals = len(pop)
    while evals < EVAL_BUDGET:
        if algorithm == "random_valid_fsm":
            child = repair_contracts(random_genome(rng))
            pop.append(child); scores.append(evaluate(child, TRAIN_SEEDS)); evals += 1
            # Keep best diverse random samples.
            order = sorted(range(len(pop)), key=lambda i: fitness_key(scores[i]))
            keep = order[:POPULATION]
            pop, scores = [pop[i] for i in keep], [scores[i] for i in keep]
        elif algorithm == "nsga2":
            children = []
            while len(children) < min(POPULATION, EVAL_BUDGET-evals):
                a = pop[tournament(pop, scores, rng)]
                b = pop[tournament(pop, scores, rng)]
                child = mutate(crossover(a, b, rng), rng)
                children.append(child)
            child_scores = [evaluate(g, TRAIN_SEEDS) for g in children]
            evals += len(children)
            pop, scores = pop + children, scores + child_scores
            pop, scores = nsga_select(pop, scores, POPULATION)
        else:
            children = []
            while len(children) < min(POPULATION, EVAL_BUDGET-evals):
                a = pop[tournament(pop, scores, rng)]
                b = pop[tournament(pop, scores, rng)]
                child = mutate(crossover(a, b, rng), rng)
                if algorithm == "contract_preserving_ga":
                    child = repair_contracts(child)
                children.append(child)
            child_scores = [evaluate(g, TRAIN_SEEDS) for g in children]
            evals += len(children)
            combined = pop + children
            combined_scores = scores + child_scores
            order = sorted(range(len(combined)), key=lambda i: fitness_key(combined_scores[i]))
            keep = order[:POPULATION]
            pop = [combined[i] for i in keep]
            scores = [combined_scores[i] for i in keep]
    best_i = min(range(len(pop)), key=lambda i: fitness_key(scores[i]))
    return {
        "algorithm": algorithm, "algorithm_seed": seed,
        "genome": list(pop[best_i]), "train_metrics": scores[best_i],
        "fitness_evaluations": evals,
    }

def paired_bootstrap(rows_a, rows_b, metric, seeds, draws=10000):
    by_a, by_b = defaultdict(list), defaultdict(list)
    for row in rows_a: by_a[row["seed"]].append(row[metric])
    for row in rows_b: by_b[row["seed"]].append(row[metric])
    diffs = [
        sum(by_a[s])/len(by_a[s]) - sum(by_b[s])/len(by_b[s])
        for s in seeds
    ]
    rng = random.Random(20261105 + len(metric))
    samples = sorted(
        sum(diffs[rng.randrange(len(diffs))] for _ in diffs)/len(diffs)
        for _ in range(draws)
    )
    return {
        "mean_difference_A_minus_B": round(sum(diffs)/len(diffs), 6),
        "ci95": [round(samples[int(0.025*draws)], 6),
                 round(samples[min(draws-1, int(0.975*draws))], 6)],
        "n_seeds": len(seeds), "bootstrap_draws": draws,
    }

def evaluate_rows(genome, seeds, policy_name):
    rows=[]
    for tool in TOOLS:
        for profile in PROFILES:
            for seed in seeds:
                result=execute_genome(make_episode(tool,profile,seed),genome)
                rows.append({"policy":policy_name,"tool":tool,"profile":profile,"seed":seed,**result})
    return rows

def summarize_rows(rows):
    n=len(rows)
    return {
        "episodes": n,
        "task_success": round(sum(r["task_success"] for r in rows)/n,6),
        "safe_resolution": round(sum(r["safe_resolution"] for r in rows)/n,6),
        "invariant_violation": round(sum(r["invariant_violation"] for r in rows)/n,6),
        "tool_actions": round(sum(r["tool_actions"] for r in rows)/n,6),
        "wait_units": round(sum(r["wait_units"] for r in rows)/n,6),
        "cost": round((sum(r["tool_actions"] for r in rows)+0.1*sum(r["wait_units"] for r in rows))/n,6),
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",default="experiments/pilot_b_policy_search/results")
    args=parser.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)

    runs=[]
    for algorithm in ALGORITHMS:
        for seed in ALGORITHM_SEEDS:
            runs.append(search(algorithm,seed))

    # Validation chooses one run per algorithm; test is not consulted here.
    validation={}
    for run in runs:
        key=tuple(run["genome"])
        if key not in validation:
            validation[key]=evaluate(key,VALIDATION_SEEDS)
        run["validation_metrics"]=validation[key]
    selected={}
    for algorithm in ALGORITHMS:
        candidates=[r for r in runs if r["algorithm"]==algorithm]
        best=min(candidates,key=lambda r: fitness_key(r["validation_metrics"]))
        selected[algorithm]=best

    # Freeze selected genomes, then evaluate the held-out test exactly once.
    test_rows={}
    test_summary={}
    for algorithm,run in selected.items():
        rows=evaluate_rows(tuple(run["genome"]),TEST_SEEDS,algorithm)
        test_rows[algorithm]=rows
        test_summary[algorithm]=summarize_rows(rows)

    manual_genomes={"manual_contract_v1":MANUAL_V1,"manual_contract_v2":MANUAL_V2}
    for name,genome in manual_genomes.items():
        rows=evaluate_rows(genome,TEST_SEEDS,name)
        test_rows[name]=rows
        test_summary[name]=summarize_rows(rows)

    comparisons={}
    reference=test_rows["manual_contract_v2"]
    for name,rows in test_rows.items():
        comparisons[name+"_vs_manual_v2_success"]=paired_bootstrap(rows,reference,"task_success",TEST_SEEDS)
        comparisons[name+"_vs_manual_v2_actions"]=paired_bootstrap(rows,reference,"tool_actions",TEST_SEEDS)

    all_test_rows=[r for rows in test_rows.values() for r in rows]
    with (out/"test_policy_episodes.csv").open("w",encoding="utf-8",newline="") as f:
        import csv
        writer=csv.DictWriter(f,fieldnames=list(all_test_rows[0]))
        writer.writeheader(); writer.writerows(all_test_rows)

    summary={
        "status":"EXPLORATORY_PILOT_B",
        "design":{
            "train_seeds":[1000,1039],"validation_seeds":[1100,1119],
            "heldout_test_seeds":[1120,1159],
            "tools":list(TOOLS),"fault_profiles":list(PROFILES),
            "algorithms":list(ALGORITHMS),"algorithm_seeds":list(ALGORITHM_SEEDS),
            "population":POPULATION,"generations":GENERATIONS,
            "fitness_evaluation_budget_per_run":EVAL_BUDGET,
            "task_success_floor":TASK_SUCCESS_FLOOR,
            "hard_constraint":"invariant_violation == 0",
            "cost":"mean tool_actions + 0.1 * mean wait_units",
            "genome_length":GENOME_LEN,
            "oracle_not_used_for_search":True,
            "test_used_once_after_validation_selection":True,
            "no_llm_api":True,"no_a800_training":True,
        },
        "search_runs":runs,
        "selected_by_validation":selected,
        "heldout_test":test_summary,
        "paired_bootstrap_vs_manual_v2":comparisons,
        "interpretation_limits":[
            "synthetic single-operation recovery simulator",
            "finite structured controller genome, not general program synthesis",
            "GA/NSGA-II are exploratory baselines; no claim of general EC superiority",
            "manual v2 is a strong hand-designed baseline",
            "test seeds are new and disjoint from Pilot A/A-2",
        ],
    }
    with (out/"summary.json").open("w",encoding="utf-8") as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
