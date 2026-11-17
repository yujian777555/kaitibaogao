"""D-092 R2.3 typed genome adapter and canonical identity functions."""
from __future__ import annotations

import dataclasses
import hashlib
import itertools
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

_HERE = Path(__file__).resolve().parent
if str(_HERE.parent / "d090_recovery") not in sys.path:
    sys.path.insert(0, str(_HERE.parent / "d090_recovery"))
from d090_genome import BASE, D090Genome  # noqa: E402

BLOCKS = {
    "pair": ("cycle_mode",),
    "fallback": ("fallback_enabled",),
    "completion": ("completion_guarded", "probe_wait"),
    "harm": ("harm_reorder_budget",),
}
ALLOWED_VALUES = {
    "cycle_mode": ("OFF", "FILTER_ONLY", "ALT_AND_FILTER"),
    "fallback_enabled": (False, True),
    "completion_guarded": (False, True),
    "harm_reorder_budget": (None, 4, 8, 12),
    "probe_wait": (0.0, 1.0, 2.0),
}
CONTROL_FIELDS = (
    "pair_rule", "pair_race_alternate", "exhaustive_fallback", "fallback_mode",
    "completion_gate", "completion_mode", "harm_first_ordering", "harm_order_mode",
    "harm_budget_threshold", "delay_probe_wait",
)


def _canonicalize(value: Any) -> Any:
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NaN/Inf is not canonical JSON")
        if value == 0.0:
            return 0.0
        return float(format(value, ".12g"))
    if isinstance(value, (tuple, list)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("canonical object keys must be strings")
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    raise ValueError("unsupported canonical type: " + type(value).__name__)


def canonical_json_bytes(payload: Any) -> bytes:
    normalized = _canonicalize(payload)
    return json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


@dataclasses.dataclass(frozen=True)
class TypedGenome:
    cycle_mode: str = "ALT_AND_FILTER"
    fallback_enabled: bool = True
    completion_guarded: bool = True
    harm_reorder_budget: Optional[int] = 8
    probe_wait: float = 1.0

    def __post_init__(self) -> None:
        for field, allowed in ALLOWED_VALUES.items():
            value = getattr(self, field)
            if not any(type(value) is type(option) and value == option for option in allowed):
                raise ValueError("invalid value for %s: %r" % (field, value))

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    def allowed_values(self, field: str) -> Tuple[Any, ...]:
        return ALLOWED_VALUES[field]

    def to_d090(self) -> D090Genome:
        values = dict(BASE)
        values.update(dict(zip(
            ("pair_rule", "pair_race_alternate"),
            {
                "OFF": (1, False),
                "FILTER_ONLY": (0, False),
                "ALT_AND_FILTER": (0, True),
            }[self.cycle_mode],
        )))
        values.update(
            exhaustive_fallback=self.fallback_enabled,
            fallback_mode=2 if self.fallback_enabled else 0,
            completion_gate=self.completion_guarded,
            completion_mode=1 if self.completion_guarded else 0,
            harm_first_ordering=self.harm_reorder_budget is not None,
            harm_order_mode=1 if self.harm_reorder_budget is not None else 0,
            harm_budget_threshold=8 if self.harm_reorder_budget is None else self.harm_reorder_budget,
            delay_probe_wait=self.probe_wait,
        )
        return D090Genome(**values)

    @classmethod
    def from_d090(cls, genome: D090Genome) -> "TypedGenome":
        full = genome.fingerprint()
        for key, expected in BASE.items():
            if key not in CONTROL_FIELDS and full.get(key) != expected:
                raise ValueError("non-search BASE field changed: " + key)
        pair = (full["pair_rule"], full["pair_race_alternate"])
        cycle = {(1, False): "OFF", (0, False): "FILTER_ONLY", (0, True): "ALT_AND_FILTER"}.get(pair)
        if cycle is None:
            raise ValueError("noncanonical pair controls")
        if (full["exhaustive_fallback"], full["fallback_mode"]) not in ((False, 0), (True, 2)):
            raise ValueError("noncanonical fallback controls")
        if (full["completion_gate"], full["completion_mode"]) not in ((False, 0), (True, 1)):
            raise ValueError("noncanonical completion controls")
        if not full["harm_first_ordering"] and full["harm_order_mode"] == 0:
            harm = None
            if full["harm_budget_threshold"] != 8:
                raise ValueError("disabled harm ordering requires neutral threshold 8")
        elif full["harm_first_ordering"] and full["harm_order_mode"] == 1:
            harm = full["harm_budget_threshold"]
        else:
            raise ValueError("noncanonical harm controls")
        return cls(
            cycle_mode=cycle,
            fallback_enabled=full["exhaustive_fallback"],
            completion_guarded=full["completion_gate"],
            harm_reorder_budget=harm,
            probe_wait=full["delay_probe_wait"],
        )


def genome_sha256(genome: Any) -> str:
    payload = genome.to_dict() if isinstance(genome, TypedGenome) else genome
    return sha256_hex(payload)


def enumerate_typed_genomes() -> Tuple[TypedGenome, ...]:
    genomes = [TypedGenome(*values) for values in itertools.product(*ALLOWED_VALUES.values())]
    return tuple(sorted(genomes, key=lambda genome: canonical_json_bytes(genome.to_dict())))


def episode_reference(seed: int, unique_ordinal: int, typed_genome_sha256: str, scenario_id: str) -> str:
    return sha256_hex({
        "seed": seed,
        "unique_ordinal": unique_ordinal,
        "genome_sha256": typed_genome_sha256,
        "scenario_id": scenario_id,
    })


def compensation_attempt_id(episode: str, dispatch_ordinal: int) -> str:
    return sha256_hex({"episode_reference": episode, "dispatch_ordinal": dispatch_ordinal})


def typed_mutation(genome: TypedGenome, block: str, rng: random.Random) -> TypedGenome:
    fields = BLOCKS[block]
    field = fields[rng.randrange(len(fields))]
    alternatives = [value for value in ALLOWED_VALUES[field] if value != getattr(genome, field)]
    return dataclasses.replace(genome, **{field: alternatives[rng.randrange(len(alternatives))]})


def typed_crossover(a: TypedGenome, b: TypedGenome, rng: random.Random) -> TypedGenome:
    values = a.to_dict()
    for fields in BLOCKS.values():
        source = a if rng.random() < 0.5 else b
        for field in fields:
            values[field] = getattr(source, field)
    return TypedGenome(**values)


def probe_typed_genomes() -> Dict[str, TypedGenome]:
    base = TypedGenome()
    return {
        "P00": base,
        "P01": dataclasses.replace(base, cycle_mode="OFF"),
        "P02": dataclasses.replace(base, cycle_mode="FILTER_ONLY"),
        "P03": dataclasses.replace(base, cycle_mode="OFF", fallback_enabled=False),
        "P04": dataclasses.replace(base, completion_guarded=False),
        "P05": dataclasses.replace(base, harm_reorder_budget=None),
        "P06": dataclasses.replace(base, harm_reorder_budget=4),
        "P07": dataclasses.replace(base, harm_reorder_budget=12),
        "P08": dataclasses.replace(base, probe_wait=0.0),
        "P09": dataclasses.replace(base, probe_wait=2.0),
    }
