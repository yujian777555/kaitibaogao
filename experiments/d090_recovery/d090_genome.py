"""D-090 状态条件化规则 genome。

连续预算协同参数继承 D-089 的冻结 B3 基础，只搜索结构化规则块。
"""
from __future__ import annotations

import dataclasses
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "d089_recovery"))
from d089_genome import D089Genome  # noqa: E402


# D-089 Train best balanced genome, copied from results/d089_audit.json.
BASE = {
    "hint_weight": 2.6509817960097104,
    "cost_weight": -0.8139095483790335,
    "failure_weight": -2.3815959653354297,
    "position_weight": -0.19679943030699998,
    "dependency_weight": 1.8641568173333096,
    "max_attempts": 4,
    "stop_residual": 0,
    "allow_alternate": False,
    "allow_verify": True,
    "stop_action": "ESCALATE",
    "strict_residual_stop": True,
    "enable_a": True,
    "route_failure_penalty": -1.0718335627792737,
    "alternate_boost": 0.11651686470331235,
    "failure_switch_threshold": 1,
    "enable_b": True,
    # D-090 searches this confirmation rule explicitly. The D-089 value
    # rounded to two waits and created avoidable pair-race budget loss.
    "delay_probe_wait": 1.0,
    "wait_batch_weight": 1.6448162524187415,
    "max_verify_probes": 1,
    "enable_c": True,
    "topo_order_weight": 0.033076174992007656,
    "unlock_priority": 2.806698143873237,
    "cycle_break_alternate": True,
    "escalation_reserve": 1.4394363260422889,
    "cost_safety": 1.0459642139791787,
    "stop_mode": 2,
}

RULES = {
    "pair_rule": (0, 1, 2),
    "fallback_mode": (0, 1, 2),
    "completion_mode": (0, 1, 2),
    "harm_order_mode": (0, 1, 2),
    "harm_budget_threshold": (4, 8, 12),
    "pair_race_alternate": (False, True),
    "exhaustive_fallback": (False, True),
    "completion_gate": (False, True),
    "harm_first_ordering": (False, True),
    "delay_probe_wait": (0.0, 1.0, 2.0),
}

RULE_BLOCKS = {
    "pair": ("pair_rule", "pair_race_alternate"),
    "fallback": ("fallback_mode", "exhaustive_fallback"),
    "completion": ("completion_mode", "completion_gate", "delay_probe_wait"),
    "harm": ("harm_order_mode", "harm_budget_threshold", "harm_first_ordering"),
}


@dataclasses.dataclass(frozen=True)
class D090Genome(D089Genome):
    pair_rule: int = 0
    fallback_mode: int = 2
    completion_mode: int = 1
    harm_order_mode: int = 1
    harm_budget_threshold: int = 8
    pair_race_alternate: bool = True
    exhaustive_fallback: bool = True
    completion_gate: bool = True
    harm_first_ordering: bool = True

    def fingerprint(self):
        return dataclasses.asdict(self)


def base_genome(**rules) -> D090Genome:
    values = dict(BASE)
    values.update(rules)
    return D090Genome(**values)


def random_d090_genome(rng: random.Random) -> D090Genome:
    return base_genome(**{name: rng.choice(values) for name, values in RULES.items()})


def mutate_d090(genome: D090Genome, rng: random.Random, profile: dict | None = None) -> D090Genome:
    weights = {name: 1.0 for name in RULES}
    if profile:
        weights["pair_rule"] += profile.get("pair", 0.0)
        weights["fallback_mode"] += profile.get("fallback", 0.0)
        weights["completion_mode"] += profile.get("completion", 0.0)
        weights["harm_order_mode"] += profile.get("harm", 0.0)
    names = list(RULES)
    pick = rng.random() * sum(weights.values())
    chosen = names[-1]
    for name in names:
        pick -= weights[name]
        if pick <= 0:
            chosen = name
            break
    values = RULES[chosen]
    current = getattr(genome, chosen)
    alternatives = [v for v in values if v != current]
    return dataclasses.replace(genome, **{chosen: rng.choice(alternatives)})


def crossover_blocks(a: D090Genome, b: D090Genome, rng: random.Random) -> D090Genome:
    values = a.fingerprint()
    for names in RULE_BLOCKS.values():
        source = a if rng.random() < 0.5 else b
        for name in names:
            values[name] = getattr(source, name)
    return D090Genome(**values)
