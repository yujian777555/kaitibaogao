"""SBCG comparison matrix and fair-accounting adapters.

No experiment is authorized by this module. Reflection is a deterministic
non-LLM proxy because real LLM API calls are forbidden in this phase.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from a3_bridge import (
    ACT_VERIFY,
    OBS_RATE_LIMIT,
    OBS_TIMEOUT,
    evaluate_controller,
    hand_fsm,
)
from ea import run_evolution
from sbcg import fsm_fingerprint
from sbcg_runner import run_sbcg_evolution
from split_access import validate_evaluation_scenarios


@dataclass(frozen=True)
class AlgorithmSpec:
    name: str
    kind: str
    method: str = ""
    config: dict = field(default_factory=dict)


def algorithm_specs():
    """Required baselines, matched controls, and one-factor ablations."""
    specs = [
        AlgorithmSpec("Hand FSM", "fixed", "hand"),
        AlgorithmSpec("Random", "legacy_ea", "random"),
        AlgorithmSpec("Rule-based", "fixed", "rule_based"),
        AlgorithmSpec("Reflection", "fixed", "reflection_proxy"),
        AlgorithmSpec("NSGA-II", "legacy_ea", "nsga2"),
        AlgorithmSpec("NSGA-III", "legacy_ea", "nsga3"),
        AlgorithmSpec("Matched-objective NSGA-II", "sbcg", config={
            "optimizer": "nsga2", "use_five_objectives": True,
            "use_stratified_counterexamples": False, "use_elite_archive": False,
            "remove_hand_from_pool": False,
        }),
        AlgorithmSpec("Matched-objective NSGA-III", "sbcg", config={
            "optimizer": "nsga3", "use_five_objectives": True,
            "use_stratified_counterexamples": False, "use_elite_archive": False,
            "remove_hand_from_pool": False,
        }),
        AlgorithmSpec("A", "legacy_ea", "A"),
        AlgorithmSpec("AB", "legacy_ea", "AB"),
        AlgorithmSpec("SBCG-NSGA-III", "sbcg", config={
            "optimizer": "nsga3", "use_five_objectives": True,
            "use_stratified_counterexamples": True, "use_elite_archive": True,
            "remove_hand_from_pool": False,
        }),
        AlgorithmSpec("SBCG-NSGA-III-no-M1", "sbcg", config={
            "optimizer": "nsga3", "use_five_objectives": False,
            "use_stratified_counterexamples": True, "use_elite_archive": True,
            "remove_hand_from_pool": False,
        }),
        AlgorithmSpec("SBCG-NSGA-III-no-M2", "sbcg", config={
            "optimizer": "nsga3", "use_five_objectives": True,
            "use_stratified_counterexamples": False, "use_elite_archive": True,
            "remove_hand_from_pool": False,
        }),
        AlgorithmSpec("SBCG-NSGA-III-no-M3", "sbcg", config={
            "optimizer": "nsga3", "use_five_objectives": True,
            "use_stratified_counterexamples": True, "use_elite_archive": False,
            "remove_hand_from_pool": True,
        }),
    ]
    return specs


def rule_based_fsm():
    """Fixed-wait observable-state rule baseline, distinct from Hand."""
    fsm = hand_fsm()
    for gene in fsm.genes_list():
        if gene.error == OBS_TIMEOUT:
            gene.wait_n = 1
    fsm.fixed_wait = True
    return fsm


def reflection_proxy_fsm():
    """Deterministic non-LLM reflection proxy: verify ambiguity before waiting."""
    fsm = hand_fsm()
    for gene in fsm.genes_list():
        if gene.error == OBS_TIMEOUT:
            gene.action = ACT_VERIFY
        elif gene.error == OBS_RATE_LIMIT:
            gene.wait_n = 2
    return fsm


def _fixed_policy(method):
    if method == "hand":
        return hand_fsm()
    if method == "rule_based":
        return rule_based_fsm()
    if method == "reflection_proxy":
        return reflection_proxy_fsm()
    raise ValueError(f"unknown fixed policy: {method}")


def run_algorithm_arm(
    spec,
    initial_pool,
    scenarios,
    verdicts,
    *,
    eval_budget,
    seed,
    pop_size,
    generations,
):
    """Execute one arm through its registered implementation, never on Test."""
    if eval_budget < 0:
        raise ValueError("evaluation budget must be non-negative")
    if spec.kind == "fixed":
        validate_evaluation_scenarios(scenarios)
        policy = _fixed_policy(spec.method)
        metrics = evaluate_controller(policy, scenarios, verdicts, None)
        out = {
            "best": policy,
            "best_result": metrics,
            "selection": {"status": "EVALUATED", "candidate": None},
            "episodes": len(scenarios),
            "unique_evaluations": 1,
            "cache_hits": 0,
            "evaluation_calls": 1,
        }
    elif spec.kind == "legacy_ea":
        out = run_evolution(
            spec.method, initial_pool, scenarios, verdicts,
            pop_size=pop_size, generations=generations,
            eval_budget=eval_budget, seed=seed,
        )
    elif spec.kind == "sbcg":
        out = run_sbcg_evolution(
            initial_pool, scenarios, verdicts,
            pop_size=pop_size, generations=generations,
            eval_budget=eval_budget, seed=seed, **spec.config,
        )
    else:
        raise ValueError(f"unknown algorithm kind: {spec.kind}")

    fingerprints = [fsm_fingerprint(candidate) for candidate in initial_pool]
    input_pool_sha = hashlib.sha256(json.dumps(fingerprints).encode("utf-8")).hexdigest()
    split = scenarios[0].get("split") if scenarios else "unknown"
    return {
        "algorithm": spec.name,
        "kind": spec.kind,
        "config": dict(spec.config),
        "seed": seed,
        "eval_budget": eval_budget,
        "episodes": out.get("episodes"),
        "unique_evaluations": out.get("unique_evaluations"),
        "cache_hits": out.get("cache_hits"),
        "evaluation_calls": out.get("evaluation_calls"),
        "initial_pool_sha256": out.get("initial_pool_sha256", input_pool_sha),
        "information_scope": f"{split}_only_no_test",
        "validation_calls": 0,
        "best": out.get("best"),
        "best_result": out.get("best_result", out.get("selection", {}).get("candidate")),
        "selection": out.get("selection"),
        "history": out.get("history", []),
        "strata": out.get("strata", []),
        "mutation_audit": out.get("mutation_audit", []),
        "raw_result": out,
    }
