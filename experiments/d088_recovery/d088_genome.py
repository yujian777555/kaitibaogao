"""D-088 recovery genomes: evolvable parameters for three mechanisms.

A (Feedback-Driven):  route switching after observed failure.
B (Delay-Aware):      batch dispatch, learned receipt delay, adaptive confirm.
C (Dependency-Aware): topological order, cycle breaking via alternate routes.

Mechanism enable flags are FIXED per experimental arm and are never mutated.
"""
from __future__ import annotations

import dataclasses
import random
import sys
from dataclasses import dataclass
from pathlib import Path

_D087 = Path(__file__).resolve().parent.parent / "pilot_a3b"
if str(_D087) not in sys.path:
    sys.path.insert(0, str(_D087))

from dependency_genome import RecoveryGenome  # noqa: E402

# --- A: feedback-driven route switching ---
A_CONTINUOUS = {
    "route_failure_penalty": (-3.0, 0.0),
    "alternate_boost": (0.0, 3.0),
}
A_DISCRETE = {
    "failure_switch_threshold": (1, 2, 3),
}

# --- B: delay-aware adaptive confirmation ---
B_CONTINUOUS = {
    "delay_probe_wait": (0.0, 2.0),     # expected waits before first VERIFY
    "wait_batch_weight": (0.0, 2.0),    # preference for dispatching while others pending
}
B_DISCRETE = {
    "max_verify_probes": (1, 2, 3),     # max VERIFY probes before forcing a WAIT
}

# --- C: dependency-aware path coordination ---
C_CONTINUOUS = {
    "topo_order_weight": (0.0, 2.0),
    "unlock_priority": (0.0, 3.0),
}
C_BOOLEAN = ("cycle_break_alternate",)

MECH_NAMES = (
    list(A_CONTINUOUS) + list(A_DISCRETE)
    + list(B_CONTINUOUS) + list(B_DISCRETE)
    + list(C_CONTINUOUS) + list(C_BOOLEAN)
)


@dataclass(frozen=True)
class D088RecoveryGenome:
    # shared base
    hint_weight: float = 2.0
    cost_weight: float = -0.2
    failure_weight: float = -1.5
    position_weight: float = 0.0
    dependency_weight: float = 1.0
    max_attempts: int = 3
    stop_residual: int = 0
    allow_alternate: bool = True
    allow_verify: bool = True
    stop_action: str = "ESCALATE"
    # A
    enable_a: bool = False
    route_failure_penalty: float = -1.0
    alternate_boost: float = 1.5
    failure_switch_threshold: int = 1
    # B
    enable_b: bool = False
    delay_probe_wait: float = 1.0
    wait_batch_weight: float = 1.0
    max_verify_probes: int = 2
    # C
    enable_c: bool = False
    topo_order_weight: float = 1.0
    unlock_priority: float = 2.0
    cycle_break_alternate: bool = True

    def fingerprint(self):
        return dataclasses.asdict(self)


def arm_flags(label: str) -> dict:
    """Map an arm label to fixed mechanism flags."""
    table = {
        "L": {"enable_a": False, "enable_b": False, "enable_c": False},
        "A": {"enable_a": True, "enable_b": False, "enable_c": False},
        "B": {"enable_a": False, "enable_b": True, "enable_c": False},
        "C": {"enable_a": False, "enable_b": False, "enable_c": True},
        "AB": {"enable_a": True, "enable_b": True, "enable_c": False},
        "AC": {"enable_a": True, "enable_b": False, "enable_c": True},
        "BC": {"enable_a": False, "enable_b": True, "enable_c": True},
        "ABC": {"enable_a": True, "enable_b": True, "enable_c": True},
    }
    return dict(table[label])


SHARED_CONTINUOUS = {
    "hint_weight": (-3.0, 3.0),
    "cost_weight": (-3.0, 0.0),
    "failure_weight": (-3.0, 0.0),
    "position_weight": (-1.0, 1.0),
    "dependency_weight": (0.0, 2.0),
}
SHARED_DISCRETE = {"max_attempts": (1, 2, 3, 4), "stop_residual": (0, 1, 2)}


def random_genome(rng: random.Random, arm: str = "ABC") -> D088RecoveryGenome:
    kwargs = {}
    for name, bounds in SHARED_CONTINUOUS.items():
        kwargs[name] = rng.uniform(*bounds)
    for name, values in SHARED_DISCRETE.items():
        kwargs[name] = rng.choice(values)
    kwargs["allow_alternate"] = rng.choice((True, False))
    kwargs["allow_verify"] = rng.choice((True, False))
    kwargs["stop_action"] = rng.choice(("ESCALATE", "STOP_SAFE"))
    for name, bounds in A_CONTINUOUS.items():
        kwargs[name] = rng.uniform(*bounds)
    for name, values in A_DISCRETE.items():
        kwargs[name] = rng.choice(values)
    for name, bounds in B_CONTINUOUS.items():
        kwargs[name] = rng.uniform(*bounds)
    for name, values in B_DISCRETE.items():
        kwargs[name] = rng.choice(values)
    for name, bounds in C_CONTINUOUS.items():
        kwargs[name] = rng.uniform(*bounds)
    kwargs["cycle_break_alternate"] = rng.choice((True, False))
    kwargs.update(arm_flags(arm))
    return D088RecoveryGenome(**kwargs)


def _mutate_value(name, current, rng):
    if name in SHARED_CONTINUOUS:
        lo, hi = SHARED_CONTINUOUS[name]
        delta = rng.uniform(-0.25 * (hi - lo), 0.25 * (hi - lo))
        value = min(hi, max(lo, current + delta))
        return hi if value == current and current == lo else (lo if value == current else value)
    if name in SHARED_DISCRETE:
        values = SHARED_DISCRETE[name]
        idx = values.index(current)
        return values[(idx + 1) % len(values)] if rng.random() < 0.5 else rng.choice(values)
    if name in A_CONTINUOUS or name in B_CONTINUOUS or name in C_CONTINUOUS:
        bounds = A_CONTINUOUS.get(name) or B_CONTINUOUS.get(name) or C_CONTINUOUS.get(name)
        lo, hi = bounds
        delta = rng.uniform(-0.25 * (hi - lo), 0.25 * (hi - lo))
        value = min(hi, max(lo, current + delta))
        return hi if value == current and current == lo else (lo if value == current else value)
    if name in A_DISCRETE or name in B_DISCRETE:
        values = A_DISCRETE.get(name) or B_DISCRETE.get(name)
        idx = values.index(current)
        return values[(idx + 1) % len(values)] if rng.random() < 0.5 else rng.choice(values)
    if name in ("allow_alternate", "allow_verify", "cycle_break_alternate"):
        return not current
    if name == "stop_action":
        return "STOP_SAFE" if current == "ESCALATE" else "ESCALATE"
    return current


MUTABLE_NAMES = (
    list(SHARED_CONTINUOUS) + list(SHARED_DISCRETE)
    + ["allow_alternate", "allow_verify", "stop_action"]
    + list(A_CONTINUOUS) + list(A_DISCRETE)
    + list(B_CONTINUOUS) + list(B_DISCRETE)
    + list(C_CONTINUOUS) + list(C_BOOLEAN)
)


def mutate(genome: D088RecoveryGenome, rng: random.Random) -> D088RecoveryGenome:
    """Type-preserving single-gene mutation. Mechanism enable flags never change."""
    name = rng.choice(MUTABLE_NAMES)
    new_val = _mutate_value(name, getattr(genome, name), rng)
    return dataclasses.replace(genome, **{name: new_val})


def arm_label(genome) -> str:
    """Derive the arm label from fixed mechanism flags."""
    a, b, c = genome.enable_a, genome.enable_b, genome.enable_c
    key = "".join(x for x, on in (("A", a), ("B", b), ("C", c)) if on)
    return key or "L"


def crossover(a: D088RecoveryGenome, b: D088RecoveryGenome, rng: random.Random) -> D088RecoveryGenome:
    """Uniform crossover; parent flags agree within an arm so flags stay fixed."""
    kwargs = {}
    for name in dataclasses.asdict(a):
        src = a if rng.random() < 0.5 else b
        kwargs[name] = getattr(src, name)
    kwargs.update(arm_flags(arm_label(a)))
    return D088RecoveryGenome(**kwargs)
