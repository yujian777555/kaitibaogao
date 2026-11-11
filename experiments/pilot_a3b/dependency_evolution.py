"""D-086 budgeted evolutionary search and frozen Validation selection."""
from __future__ import annotations

import dataclasses
import random

from dependency_gate import summarize
from dependency_genome import (
    GenomePolicy,
    crossover,
    make_initial_pool,
    mutate,
    random_genome,
)
from dependency_recovery import run_episode
from ea import crowding_distance, fast_non_dominated_sort, niching_select, reference_dirs

METHODS = ("RandomSearch", "NSGA-II", "NSGA-III", "C-NSGA-III")
ABLATIONS = {
    "NoDependencyPriority": {"dependency_weight": 0.0},
    "NoFailureFeedback": {"failure_weight": 0.0},
    "NoAlternate": {"allow_alternate": False},
    "NoPendingVerification": {"allow_verify": False},
}


def fingerprint(genome):
    return repr(sorted(genome.fingerprint().items()))


class BudgetExceeded(Exception):
    pass


class EvaluationLedger:
    def __init__(self, manifest_sha, episode_cap=6048, evaluator_version="d086-dependency-v1"):
        self.manifest_sha = manifest_sha
        self.episode_cap = int(episode_cap)
        self.evaluator_version = evaluator_version
        self.rows = {}
        self.stats = {
            "evaluation_calls": {"train": 0, "validation": 0},
            "unique_episode_equivalent": {"train": 0, "validation": 0},
            "cache_hits": {"train": 0, "validation": 0},
        }

    def evaluate(self, genome, scenarios, role):
        if role not in self.stats["evaluation_calls"]:
            raise ValueError("unknown evaluation role")
        output = []
        fp = fingerprint(genome)
        for scenario in scenarios:
            if scenario["split"] != role:
                raise ValueError("evaluation split is restricted to " + role)
            key = (
                "d086-dependency-v1", self.manifest_sha, self.evaluator_version,
                fp, scenario["scenario_id"], scenario["seed"], role,
            )
            self.stats["evaluation_calls"][role] += 1
            if key in self.rows:
                self.stats["cache_hits"][role] += 1
                output.append(self.rows[key])
                continue
            if role == "train" and self.stats["unique_episode_equivalent"][role] >= self.episode_cap:
                raise BudgetExceeded("unique Train episode-equivalent cap reached")
            result = run_episode(GenomePolicy(genome), scenario)
            result.update({
                "method": "candidate",
                "task_family_id": scenario["task_family_id"],
                "difficulty_stratum": scenario["difficulty_stratum"],
                "composition": scenario["composition"],
                "repeat": scenario["repeat"],
            })
            self.rows[key] = result
            self.stats["unique_episode_equivalent"][role] += 1
            output.append(result)
        return output

    def rows_for(self, genome):
        fp = fingerprint(genome)
        return [row for key, row in self.rows.items() if key[3] == fp]


def _metrics(rows):
    split = rows[0]["split"]
    summary = summarize(rows)
    by_label = {
        label: summary[f"{split}|candidate|{label}"]
        for label in ("R1", "R2", "R3", "R4")
        if f"{split}|candidate|{label}" in summary
    }
    r3_success = by_label.get("R3", {}).get("correct_escalation_mean", 0.0)
    r4_success = by_label.get("R4", {}).get("class_success_mean", 0.0)
    recoverable = [
        by_label[label]["conditional_recovery_success_mean"]
        for label in ("R1", "R2") if label in by_label
    ]
    condrec = sum(recoverable) / len(recoverable) if recoverable else 0.0
    avoid = sum(item["avoidable_harm_mean"] for item in by_label.values()) / len(by_label)
    r3_cost = by_label.get("R3", {}).get("recovery_cost_mean", 0.0)
    metrics = {
        "r3_success": r3_success,
        "r4_success": r4_success,
        "condrec": condrec,
        "avoid_harm": avoid,
        "r3_cost": r3_cost,
        "label_coverage": sorted(by_label),
        "residual": sum(item["residual_side_effects_mean"] for item in by_label.values()) / len(by_label),
        "total_cost": sum(item["action_cost_mean"] for item in by_label.values()) / len(by_label),
        "constraint_count": sum(row["constraint_violation"] for row in rows),
        "pending_count": sum(row["pending_compensation"] for row in rows),
        "duplicate_count": sum(row["duplicate_compensation"] for row in rows),
    }
    return {
        "summary": summary,
        "metrics": metrics,
        "objectives": (
            1.0 - r3_success,
            avoid,
            r3_cost,
            1.0 - r4_success,
            1.0 - condrec,
        ),
    }


def evaluate_genome(genome, scenarios, ledger, role="train"):
    rows = ledger.evaluate(genome, scenarios, role)
    return {"genome": genome, **_metrics(rows)}


def _ranks_crowding(population):
    objectives = [record["objectives"] for record in population]
    fronts = fast_non_dominated_sort(objectives)
    ranks = {}
    crowd = {}
    for index, front in enumerate(fronts):
        for member in front:
            ranks[member] = index
        crowd.update(crowding_distance(objectives, front))
    return ranks, crowd


def _nsga3_survivors(population, size, rng):
    objectives = [record["objectives"] for record in population]
    fronts = fast_non_dominated_sort(objectives)
    picked = []
    directions = reference_dirs(m=5, p=3)
    for front in fronts:
        if len(picked) + len(front) <= size:
            picked.extend(front)
            continue
        remaining = list(front)
        while remaining and len(picked) < size:
            chosen = niching_select(
                objectives, remaining, directions, selected=picked,
                rng=rng, extreme_indices=fronts[0],
            )
            if not chosen:
                break
            picked.append(chosen[0])
            remaining.remove(chosen[0])
        break
    return [population[index] for index in picked]


def _nsga2_survivors(population, size):
    objectives = [record["objectives"] for record in population]
    fronts = fast_non_dominated_sort(objectives)
    picked = []
    for front in fronts:
        if len(picked) + len(front) <= size:
            picked.extend(front)
        else:
            distance = crowding_distance(objectives, front)
            picked.extend(sorted(front, key=lambda index: -distance[index])[:size - len(picked)])
            break
    return [population[index] for index in picked]


def choose_validation_metrics(records):
    feasible = [record for record in records if record["metrics"]["constraint_count"] == 0]
    if not feasible:
        return {
            "status": "HOLD",
            "reason": "no candidate satisfies duplicate/pending hard constraints",
            "feasible_count": 0,
        }
    fronts = fast_non_dominated_sort([record["objectives"] for record in feasible])
    candidates = [feasible[index] for index in fronts[0]]
    chosen = min(
        candidates,
        key=lambda record: (
            -record["metrics"]["r3_success"],
            -record["metrics"]["r4_success"],
            record["metrics"]["avoid_harm"],
            -record["metrics"]["condrec"],
            record["metrics"]["r3_cost"],
            fingerprint(record["genome"]),
        ),
    )
    return {
        "status": "SELECTED",
        "genome": chosen["genome"],
        "metrics": chosen["metrics"],
        "objectives": chosen["objectives"],
        "feasible_count": len(feasible),
        "selection_rule": "feasible Pareto; R3; R4; harm; CondRecSucc; cost; fingerprint",
    }


def select_validation(search_result, scenarios):
    ledger = search_result["ledger"]
    records = [
        evaluate_genome(record["genome"], scenarios, ledger, role="validation")
        for record in search_result["archive"]
    ]
    selected = choose_validation_metrics(records)
    selected["ledger"] = ledger.stats
    if selected["status"] == "SELECTED":
        selected["validation_rows"] = ledger.rows_for(selected["genome"])
    return selected


def run_search(method, seed, scenarios, population_size=12, generations=6,
               episode_cap=6048, manifest_sha="synthetic", ablation=None):
    if method not in METHODS:
        raise ValueError("unknown D-086 search method: " + str(method))
    if ablation is not None and (method != "C-NSGA-III" or ablation not in ABLATIONS):
        raise ValueError("ablation is defined only for the full C-NSGA-III method")
    if any(scenario.get("split") != "train" for scenario in scenarios):
        raise ValueError("evolution accepts Train scenarios only")
    rng = random.Random(seed * 104729 + 37)
    changes = ABLATIONS.get(ablation, {})
    initial = [dataclasses.replace(genome, **changes) for genome in make_initial_pool(seed)][:population_size]
    initial_pool = [fingerprint(genome) for genome in initial]
    ledger = EvaluationLedger(manifest_sha=manifest_sha, episode_cap=episode_cap)
    archive = {}
    history = []

    def evaluate(genome):
        key = fingerprint(genome)
        if key not in archive:
            archive[key] = evaluate_genome(genome, scenarios, ledger, role="train")
        return archive[key]

    def tournament(population):
        ranks, crowd = _ranks_crowding(population)
        first, second = rng.sample(population, 2)
        if method == "C-NSGA-III" and first["metrics"]["constraint_count"] != second["metrics"]["constraint_count"]:
            return first if first["metrics"]["constraint_count"] < second["metrics"]["constraint_count"] else second
        if ranks[population.index(first)] != ranks[population.index(second)]:
            return first if ranks[population.index(first)] < ranks[population.index(second)] else second
        return first if crowd[population.index(first)] >= crowd[population.index(second)] else second

    budget_exhausted = False
    population = []
    try:
        population = [evaluate(genome) for genome in initial]
        for generation in range(generations):
            offspring = []
            if method == "RandomSearch":
                offspring = [evaluate(random_genome(rng)) for _ in range(population_size)]
            else:
                while len(offspring) < population_size:
                    child = crossover(
                        tournament(population)["genome"],
                        tournament(population)["genome"], rng,
                    )
                    child = mutate(child, rng)
                    child = dataclasses.replace(child, **changes)
                    offspring.append(evaluate(child))
            combined = population + offspring
            if method == "RandomSearch":
                population = rng.sample(combined, len(combined))
            elif method == "NSGA-II":
                population = _nsga2_survivors(combined, population_size)
            else:
                constrained = combined
                if method == "C-NSGA-III":
                    feasible = [record for record in combined if record["metrics"]["constraint_count"] == 0]
                    if feasible:
                        constrained = feasible
                    else:
                        minimum = min(record["metrics"]["constraint_count"] for record in combined)
                        constrained = [record for record in combined if record["metrics"]["constraint_count"] == minimum]
                population = _nsga3_survivors(constrained, population_size, rng)
            history.append({
                "generation": generation,
                "unique_episode_equivalent": dict(ledger.stats["unique_episode_equivalent"]),
                "cache_hits": dict(ledger.stats["cache_hits"]),
                "feasible_population_count": sum(record["metrics"]["constraint_count"] == 0 for record in population),
            })
    except BudgetExceeded:
        budget_exhausted = True
    return {
        "method": method,
        "seed": seed,
        "ablation": ablation,
        "archive": list(archive.values()),
        "initial_pool": initial_pool,
        "final_population": population,
        "history": history,
        "ledger": ledger,
        "budget_exhausted": budget_exhausted,
        "test_accessed": False,
    }
