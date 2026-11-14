"""D-089 genome: D-088 genome + budget-cooperation parameters (B4).

stop_mode: 0 legacy / 1 strict / 2 adaptive  (see d089_policies)
escalation_reserve: extra decisions kept for the terminal action
cost_safety: multiplier on the public remaining-cost estimate
"""
from __future__ import annotations

import dataclasses
import random
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "d088_recovery"))

from d088_genome import (  # noqa: E402
    D088RecoveryGenome, arm_flags, arm_label, _mutate_value, SEGMENTS,
    SHARED_CONTINUOUS, SHARED_DISCRETE,
    A_CONTINUOUS, A_DISCRETE, B_CONTINUOUS, B_DISCRETE, C_CONTINUOUS, C_BOOLEAN,
)

D09_CONTINUOUS = {
    "escalation_reserve": (0.0, 3.0),
    "cost_safety": (0.5, 2.0),
}
D09_DISCRETE = {
    "stop_mode": (0, 1, 2),
}

ALL_NAMES = (
    list(SHARED_CONTINUOUS) + list(SHARED_DISCRETE)
    + ["allow_alternate", "allow_verify", "stop_action", "strict_residual_stop"]
    + list(A_CONTINUOUS) + list(A_DISCRETE)
    + list(B_CONTINUOUS) + list(B_DISCRETE)
    + list(C_CONTINUOUS) + list(C_BOOLEAN)
    + list(D09_CONTINUOUS) + list(D09_DISCRETE)
)

SEGMENTS_D09 = dict(SEGMENTS)
SEGMENTS_D09["B4"] = list(D09_CONTINUOUS) + list(D09_DISCRETE)


@dataclass(frozen=True)
class D089Genome(D088RecoveryGenome):
    escalation_reserve: float = 1.0
    cost_safety: float = 1.0
    stop_mode: int = 2

    def fingerprint(self):
        return dataclasses.asdict(self)


def random_genome(rng: random.Random, arm: str = "ABC") -> D089Genome:
    base = D088RecoveryGenome(**{
        k: v for k, v in dataclasses.asdict(
            __import__("d088_genome").random_genome(rng, arm)
        ).items()
    })
    return D089Genome(
        **dataclasses.asdict(base),
        escalation_reserve=rng.uniform(*D09_CONTINUOUS["escalation_reserve"]),
        cost_safety=rng.uniform(*D09_CONTINUOUS["cost_safety"]),
        stop_mode=rng.choice(D09_DISCRETE["stop_mode"]),
    )


def _mutate_d09(name, current, rng):
    if name in D09_CONTINUOUS:
        lo, hi = D09_CONTINUOUS[name]
        delta = rng.uniform(-0.25 * (hi - lo), 0.25 * (hi - lo))
        value = min(hi, max(lo, current + delta))
        return hi if value == current and current == lo else (lo if value == current else value)
    if name in D09_DISCRETE:
        values = D09_DISCRETE[name]
        idx = values.index(current)
        return values[(idx + 1) % len(values)] if rng.random() < 0.5 else rng.choice(values)
    return _mutate_value(name, current, rng)


def mutate(genome: D089Genome, rng: random.Random) -> D089Genome:
    name = rng.choice(ALL_NAMES)
    if name.startswith("enable_"):
        return mutate(genome, rng)
    return dataclasses.replace(genome, **{name: _mutate_d09(name, getattr(genome, name), rng)})


def mutate_feedback(genome: D089Genome, rng: random.Random,
                    failure_profile: dict | None = None) -> D089Genome:
    if failure_profile:
        weights = {
            "shared": 1.0 + failure_profile.get("budget_exhaust", 0),
            "A": 1.0 + failure_profile.get("route_failures", 0),
            "B": 1.0 + failure_profile.get("pending_residue", 0),
            "C": 1.0 + failure_profile.get("dependency_block", 0),
            "B4": 1.0 + failure_profile.get("early_stop", 0),
        }
        names = list(weights)
        total = sum(weights.values())
        pick = rng.random() * total
        acc = 0.0
        segment = names[-1]
        for n in names:
            acc += weights[n]
            if pick <= acc:
                segment = n
                break
    else:
        segment = rng.choice(list(SEGMENTS_D09))
    name = rng.choice(SEGMENTS_D09[segment])
    if name.startswith("enable_"):
        return mutate_feedback(genome, rng, failure_profile)
    return dataclasses.replace(genome, **{name: _mutate_d09(name, getattr(genome, name), rng)})


def crossover_segments(a: D089Genome, b: D089Genome, rng: random.Random) -> D089Genome:
    kwargs = {}
    for segment, names in SEGMENTS_D09.items():
        src = a if rng.random() < 0.5 else b
        for name in names:
            kwargs[name] = getattr(src, name)
    for name in ALL_NAMES:
        if name not in kwargs:
            kwargs[name] = getattr(a if rng.random() < 0.5 else b, name)
    kwargs.update(arm_flags(arm_label(a)))
    return D089Genome(**kwargs)


# ---------------------------------------------------------------------------
# B1: Pareto archive preservation
# ---------------------------------------------------------------------------
# Preference keys for candidate selection (train-time only):
PREFERENCE_KEYS = {
    "R3_priority": lambda s: (s["r3_success"], s["r4_success"], -s["avoid_harm"], -s["recovery_cost"]),
    "R4_priority": lambda s: (s["r4_success"], s["r3_success"], -s["avoid_harm"], -s["recovery_cost"]),
    "cost_priority": lambda s: (-s["recovery_cost"], s["r3_success"], s["r4_success"], -s["avoid_harm"]),
    "balanced": lambda s: (min(s["r3_success"], s["r4_success"]),
                           s["r3_success"] + s["r4_success"], -s["avoid_harm"], -s["recovery_cost"]),
    "harm_priority": lambda s: (-s["avoid_harm"], s["r3_success"], s["r4_success"], -s["recovery_cost"]),
}


def pareto_front(candidates):
    """candidates: list of (summary, genome, rows). Return non-dominated list."""
    def dominates(x, y):
        sx, sy = x[0], y[0]
        keys = ("constraint_violation", "r3_success", "r4_success", "avoid_harm", "recovery_cost")
        better = False
        xv = (sx["constraint_violation"], -sx["r3_success"], -sx["r4_success"], sx["avoid_harm"], sx["recovery_cost"])
        yv = (sy["constraint_violation"], -sy["r3_success"], -sy["r4_success"], sy["avoid_harm"], sy["recovery_cost"])
        for a, b in zip(xv, yv):
            if a > b:
                return False
            if a < b:
                better = True
        return better

    front = []
    for c in candidates:
        if any(dominates(o, c) for o in candidates if o is not c):
            continue
        front.append(c)
    return front


def select_by_preference(front, preference):
    key = PREFERENCE_KEYS[preference]
    feasible = [c for c in front
                if c[0]["constraint_violation"] == 0 and c[0]["pending_compensation"] == 0]
    pool = feasible or front
    return max(pool, key=lambda c: key(c[0]))
