"""Stage-2 diagnostic experiment: small-scale mechanism comparison.

DIAGNOSTIC ONLY — not a confirmatory A-3b run (that stays HOLD pending
preregistration freeze and user approval). Uses freshly generated scenarios
(new seeds, not the frozen A-3 held-out dataset) and reports per-composition
breakdowns so nothing is hidden.

Methods: hand FSM, Random Search, GA, NSGA-II, NSGA-III, A, B, A+B.
All share the same initial candidate pool, scenario set and episode budget.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from collections import defaultdict
from pathlib import Path

from a3_bridge import (
    FSMGenome,
    evaluate_controller,
    hand_genome,
    label_scenario,
    random_genome,
    run_episode_fsm,
)
from ea import run_evolution
from pilot_a3 import ALL_COMPOSITIONS, ALL_TASKS, TOOLS, make_fault_vector

SEEDS = [11, 23, 37]
NEW_SEED_BASE = 2026110700
REPEATS = 4
POP = 24
GENS = 20
SCENARIOS_PER_EVAL_CAP = 240  # safety cap


def build_diagnostic_scenarios():
    scenarios = []
    idx = 0
    for task in ALL_TASKS:
        for comp in ALL_COMPOSITIONS:
            for rep in range(REPEATS):
                seed = NEW_SEED_BASE + idx * 7 + rep
                scenarios.append(
                    {
                        "scenario_id": f"diag|{task}|{comp}|{rep}",
                        "split": "diagnostic",
                        "task": task,
                        "composition": comp,
                        "seed": seed,
                        "tools": TASKS_TOOLS(task),
                        "faults": make_fault_vector(task, comp, seed),
                    }
                )
                idx += 1
    return scenarios


def TASKS_TOOLS(task):
    from pilot_a3 import TASKS

    return TASKS[task]


def make_init_pool(rng, n=40):
    """Primary comparison uses RANDOM-ONLY init pool (review 56 M1): the hand
    policy is a separate baseline, not a search seed. Hand-seeded init is a
    separate ablation, not mixed into the main contrast."""
    return [random_genome(rng) for _ in range(n)]


def throughput_probe(scenarios, seconds=2.0):
    g = hand_genome()
    t0 = time.time()
    n = 0
    while time.time() - t0 < seconds:
        for sc in scenarios[:20]:
            run_episode_fsm(g, sc)
            n += 1
    dt = time.time() - t0
    return n / dt


def main():
    out_dir = Path(__file__).parent
    scenarios = build_diagnostic_scenarios()
    labels = {sc["scenario_id"]: label_scenario(sc) for sc in scenarios}
    label_counts = defaultdict(int)
    for v in labels.values():
        label_counts[v] += 1

    eps = throughput_probe(scenarios)
    budget = POP * (GENS + 1) * len(scenarios)
    print(f"scenarios={len(scenarios)} labels={dict(label_counts)}")
    print(f"throughput={eps:.0f} episodes/s; budget/method/seed={budget} eps (~{budget/eps:.1f}s)")

    methods = ["hand", "random", "ga", "nsga2", "nsga3", "A", "B", "AB"]
    runs = []
    for seed in SEEDS:
        rng = random.Random(seed * 1000 + 7)
        init_pool = make_init_pool(rng)
        for method in methods:
            if method == "hand":
                res = evaluate_controller(hand_genome(), scenarios, labels)
                rows = [
                    {"scenario_id": sc["scenario_id"], "label": labels[sc["scenario_id"]],
                     "composition": sc["composition"], "task": sc["task"],
                     "class_success": r["class_success"], "task_success": r["task_success"],
                     "invariant_violation": r["invariant_violation"], "duplicate": r["duplicate"],
                     "escalated": r["escalated"], "action_count": r["action_count"],
                     "unresolved": r["unresolved"], "active_effects": r["active_effects"]}
                    for sc, r in zip(scenarios, res["rows"])
                ]
                runs.append(
                    {
                        "method": method,
                        "seed": seed,
                        "episodes": len(scenarios),
                        "metrics": {k: res[k] for k in res if k != "rows"},
                        "history": [],
                        "rules": [[k[0], k[1], k[2], v.action, v.wait_n] for k, v in hand_genome().rules.items()],
                        "rows": rows,
                    }
                )
                print(
                    f"seed={seed} hand    cond_rec={res['cond_rec']:.3f} "
                    f"corr_esc={res['corr_esc']:.3f} cont={res['containment']:.3f} "
                    f"dup={res['dup']:.3f} viol={res['violations']:.3f} "
                    f"unnec_esc={res['unnec_esc']:.3f} eps={len(scenarios)}"
                )
                continue
            t0 = time.time()
            out = run_evolution(
                method,
                init_pool,
                scenarios,
                labels,
                pop_size=POP,
                generations=GENS,
                eval_budget=budget * 2,
                seed=seed,
            )
            res = out["best_result"]
            rows = [
                {"scenario_id": sc["scenario_id"], "label": labels[sc["scenario_id"]],
                 "composition": sc["composition"], "task": sc["task"],
                 "class_success": r["class_success"], "task_success": r["task_success"],
                 "invariant_violation": r["invariant_violation"], "duplicate": r["duplicate"],
                 "escalated": r["escalated"], "action_count": r["action_count"],
                 "unresolved": r["unresolved"], "active_effects": r["active_effects"]}
                for sc, r in zip(scenarios, res["rows"])
            ]
            runs.append(
                {
                    "method": method,
                    "seed": seed,
                    "episodes": out["episodes"],
                    "wall": round(time.time() - t0, 2),
                    "metrics": {k: res[k] for k in res if k != "rows"},
                    "history": out["history"],
                    "best_obj": list(res["objectives"]),
                    "rules": [[k[0], k[1], k[2], v.action, v.wait_n] for k, v in out["best"].rules.items()],
                    "rows": rows,
                }
            )
            print(
                f"seed={seed} {method:7s} cond_rec={res['cond_rec']:.3f} "
                f"corr_esc={res['corr_esc']:.3f} cont={res['containment']:.3f} "
                f"dup={res['dup']:.3f} viol={res['violations']:.3f} "
                f"unnec_esc={res['unnec_esc']:.3f} eps={out['episodes']}"
            )

    # per-composition breakdown for the best method and NSGA-II reference
    def per_composition(method, seed):
        for r in runs:
            if r["method"] == method and r["seed"] == seed:
                return r
        return None

    payload = {
        "kind": "DIAGNOSTIC_NOT_CONFIRMATORY",
        "scenario_seed_base": NEW_SEED_BASE,
        "n_scenarios": len(scenarios),
        "label_counts": dict(label_counts),
        "throughput_eps_per_s": round(eps, 1),
        "pop": POP,
        "generations": GENS,
        "seeds": SEEDS,
        "budget_episodes_per_method_seed": budget,
        "runs": runs,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    payload["manifest_sha256"] = digest
    (out_dir / "diagnostic_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("wrote diagnostic_results.json", digest[:16])


if __name__ == "__main__":
    main()
