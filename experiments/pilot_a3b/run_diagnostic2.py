"""Round-2 diagnostic experiment (D-061): stateful controller, fixed evaluator,
redesigned A/B, standard baselines, train/validation separation.

DIAGNOSTIC ONLY -- not confirmatory A-3b (that remains HOLD pending
preregistration and user approval). Fresh seeds; the frozen D-060 artifacts
(diagnostic_results.json) are preserved untouched; this run writes
diagnostic2_results.json with its own manifest.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from collections import defaultdict
from pathlib import Path

from a3_bridge import (
    evaluate_controller,
    hand_fsm,
    random_fsm,
    run_episode_fsm,
    scenario_verdict,
)
from ea import run_evolution, validator_illegal_ratio
from pilot_a3 import ALL_COMPOSITIONS, TASKS, make_fault_vector

SEEDS = [101, 202, 303]
NEW_SEED_BASE = 2026110800
REPEATS = 3
POP = 48
GENS = 60
TRAIN_TASKS = ("inventory_order_payment", "calendar_order_ledger",
               "customer_order_shipment", "inventory_calendar_order")
VAL_TASKS = ("return_refund_restock", "subscription_ledger_notification")


def sensible_random_fsm(rng):
    """Shared init-distribution variant: uniform random genes EXCEPT a small
    progress skeleton (identical for every method -- M1 fairness). The
    skeleton only guarantees the controller can make progress at all; it is
    NOT the hand policy (compensation/rollback/escalation choices remain
    random)."""
    import a3_bridge as ab
    fsm = ab.random_fsm(rng)
    skeleton = {
        ab.OBS_START: ab.ACT_RETRY,
        ab.OBS_TIMEOUT: ab.ACT_WAIT,
        ab.OBS_WAITED: ab.ACT_VERIFY,
        ab.OBS_NOT_COMMITTED: ab.ACT_RETRY,
        ab.OBS_RATE_LIMIT: ab.ACT_WAIT,
        ab.OBS_SCHEMA: ab.ACT_REPAIR,
        ab.OBS_PERMISSION: ab.ACT_ESCALATE,
        ab.OBS_PARTIAL: ab.ACT_COMPENSATE,
    }
    if rng.random() < 0.5:
        for gene in fsm.genes_list():
            if gene.att_bucket == 0 and not gene.stack and gene.error in skeleton:
                gene.action = skeleton[gene.error]
                gene.wait_n = rng.randint(2, 4) if gene.action == ab.ACT_WAIT else gene.wait_n
    return fsm


def build_scenarios():
    train, val = [], []
    idx = 0
    for task in TRAIN_TASKS:
        for comp in ALL_COMPOSITIONS:
            for rep in range(REPEATS):
                seed = NEW_SEED_BASE + idx * 13 + rep
                train.append({
                    "scenario_id": f"t2train|{task}|{comp}|{rep}",
                    "split": "train", "task": task, "composition": comp,
                    "seed": seed, "tools": TASKS[task],
                    "faults": make_fault_vector(task, comp, seed),
                })
                idx += 1
    for task in VAL_TASKS:
        for comp in ALL_COMPOSITIONS:
            for rep in range(REPEATS):
                seed = NEW_SEED_BASE + 90000 + idx * 13 + rep
                val.append({
                    "scenario_id": f"t2val|{task}|{comp}|{rep}",
                    "split": "validation", "task": task, "composition": comp,
                    "seed": seed, "tools": TASKS[task],
                    "faults": make_fault_vector(task, comp, seed),
                })
                idx += 1
    return train, val


def build_verdicts(scenarios):
    return {sc["scenario_id"]: scenario_verdict(sc) for sc in scenarios}


def pack_rows(scenarios, res, seed, split_tag):
    out = []
    for sc, r in zip(scenarios, res["rows"]):
        out.append({
            "scenario_id": sc["scenario_id"], "split": split_tag,
            "task": sc["task"], "composition": sc["composition"], "seed": seed,
            "label": r["label"],
            "class_success": r["class_success"],
            "task_success": r["task_success"],
            "invariant_violation": r["invariant_violation"],
            "duplicate": r["duplicate"],
            "avoidable_harm": r["avoidable_harm"],
            "policy_selected_escalation": r["policy_selected_escalation"],
            "runtime_forced_abort": r["runtime_forced_abort"],
            "decision_count": r["decision_count"],
            "active_effects": r["active_effects"],
        })
    return out


def main():
    out_dir = Path(__file__).parent
    train, val = build_scenarios()
    vtrain = build_verdicts(train)
    vval = build_verdicts(val)
    label_counts = defaultdict(int)
    for v in vtrain.values():
        label_counts[v["class"]] += 1

    # throughput probe
    g = hand_fsm()
    t0 = time.time()
    n = 0
    while time.time() - t0 < 1.5:
        run_episode_fsm(g, train[0])
        n += 1
    eps = n / (time.time() - t0)
    budget = POP * (GENS + 1) * len(train)
    print(f"train={len(train)} val={len(val)} labels={dict(label_counts)}")
    print(f"throughput={eps:.0f} eps/s; budget/method/seed={budget} (~{budget/max(eps,1):.1f}s)")

    methods = ["hand", "random", "ga", "nsga2", "nsga3", "A", "B", "AB"]
    runs = []
    for seed in SEEDS:
        rng = random.Random(seed * 7919 + 13)
        init_pool = [sensible_random_fsm(rng) for _ in range(60)]
        for method in methods:
            t0 = time.time()
            if method == "hand":
                fsm = hand_fsm()
                res_tr = evaluate_controller(fsm, train, vtrain)
                res_va = evaluate_controller(fsm, val, vval)
                episodes = len(train) + len(val)
                illegal = validator_illegal_ratio([fsm])
                best_rules = [[k[0], k[1], k[2], gm.action, gm.wait_n]
                              for k, gm in sorted(fsm.genes.items())]
                hist = []
            else:
                out = run_evolution(method, init_pool, train, vtrain,
                                    pop_size=POP, generations=GENS,
                                    eval_budget=budget * 2, seed=seed)
                fsm = out["best"]
                res_tr = out["best_result"]
                res_va = evaluate_controller(fsm, val, vval)
                episodes = out["episodes"] + len(val)
                illegal = validator_illegal_ratio(out["final_population"])
                best_rules = [[k[0], k[1], k[2], gm.action, gm.wait_n]
                              for k, gm in sorted(fsm.genes.items())]
                hist = out["history"]
            runs.append({
                "method": method, "seed": seed, "episodes": episodes,
                "wall": round(time.time() - t0, 2),
                "validator_illegal_ratio": illegal,
                "train_metrics": {k: res_tr[k] for k in res_tr if k != "rows"},
                "val_metrics": {k: res_va[k] for k in res_va if k != "rows"},
                "rules": best_rules,
                "history": hist,
                "rows": pack_rows(train, res_tr, seed, "train")
                       + pack_rows(val, res_va, seed, "validation"),
            })
            print(f"seed={seed} {method:7s} train_succ={res_tr['cond_rec']:.3f} "
                  f"val_succ={res_va['cond_rec']:.3f} corr_esc={res_tr['corr_esc']:.3f} "
                  f"cont={res_tr['containment']:.3f} viol={res_tr['violations']:.3f} "
                  f"illegal={illegal:.2f} eps={episodes}")

    payload = {
        "kind": "DIAGNOSTIC_ROUND2_NOT_CONFIRMATORY",
        "seed_base": NEW_SEED_BASE,
        "methods": methods,
        "seeds": SEEDS,
        "n_train": len(train),
        "n_val": len(val),
        "label_counts_train": dict(label_counts),
        "throughput_eps_per_s": round(eps, 1),
        "pop": POP, "generations": GENS,
        "budget_episodes_per_method_seed": budget,
        "runs": runs,
    }
    payload["manifest_sha256"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()
    (out_dir / "diagnostic2_results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8")
    print("wrote diagnostic2_results.json", payload["manifest_sha256"][:16])


if __name__ == "__main__":
    main()
