"""Frozen exploratory paired statistics for D-094 R4; no data-dependent tuning."""
from __future__ import annotations

import itertools
import math
import random
from typing import Any, Sequence


R4_STATISTICAL_SEED = 20261120
R4_BOOTSTRAP_REPLICATES = 20_000


def _pairs(values: Sequence[float]) -> list[float]:
    result = list(values)
    if len(result) != 4 or any(not math.isfinite(value) for value in result):
        raise ValueError("R4 paired statistics require four finite task/seed differences")
    return result


def exact_sign_flip_test(differences: Sequence[float]) -> dict[str, Any]:
    """Two-sided exhaustive 2^4 sign-flip test for the mean paired difference."""
    values = _pairs(differences)
    observed = sum(values) / len(values)
    null = [
        sum(sign * value for sign, value in zip(signs, values)) / len(values)
        for signs in itertools.product((-1.0, 1.0), repeat=len(values))
    ]
    extreme = sum(abs(value) >= abs(observed) - 1e-15 for value in null)
    return {
        "method": "two_sided_exact_sign_flip_all_16_sign_patterns",
        "unit_count": len(values),
        "observed_mean_difference": observed,
        "p_value": extreme / len(null),
        "extreme_count": extreme,
        "null_count": len(null),
        "interpretation": "exploratory_only_four_units_cannot_establish_generalization",
    }


def _quantile(sorted_values: Sequence[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    low = math.floor(position)
    high = math.ceil(position)
    fraction = position - low
    return sorted_values[low] * (1.0 - fraction) + sorted_values[high] * fraction


def paired_bootstrap_ci(
    differences: Sequence[float],
    *,
    seed: int = R4_STATISTICAL_SEED,
    replicates: int = R4_BOOTSTRAP_REPLICATES,
) -> dict[str, Any]:
    """Percentile bootstrap over paired units, with a pre-frozen seed and replicate count."""
    values = _pairs(differences)
    if replicates != 20_000 or replicates <= 0:
        raise ValueError("R4 freezes exactly 20,000 bootstrap replicates")
    rng = random.Random(seed)
    means = []
    for _ in range(replicates):
        means.append(sum(values[rng.randrange(4)] for _ in range(4)) / 4)
    means.sort()
    return {
        "method": "paired_unit_percentile_bootstrap_95_percent",
        "seed": seed,
        "replicates": replicates,
        "lower": _quantile(means, 0.025),
        "upper": _quantile(means, 0.975),
        "interpretation": "uncertainty_over_four_observed_units_not_population_generalization",
    }


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Apply Holm family-wise adjustment without hiding any raw p-value."""
    if not p_values or any(not 0.0 <= value <= 1.0 for value in p_values.values()):
        raise ValueError("invalid p-value family")
    ordered = sorted(p_values, key=lambda key: (p_values[key], key))
    adjusted = {}
    running = 0.0
    count = len(ordered)
    for rank, key in enumerate(ordered):
        running = max(running, min(1.0, (count - rank) * p_values[key]))
        adjusted[key] = running
    return adjusted


def preregistered_analysis(
    paired_differences: dict[str, Sequence[float]],
) -> dict[str, Any]:
    """Run all four frozen comparisons; labels define the fixed multiplicity family."""
    expected = ("B3_minus_B2", "B4_minus_B2", "B3_minus_B4", "B2_minus_B1")
    if set(paired_differences) != set(expected):
        raise ValueError("R4 statistical comparison family is incomplete or changed")
    results = {}
    raw_p = {}
    for ordinal, label in enumerate(expected):
        values = _pairs(paired_differences[label])
        sign = exact_sign_flip_test(values)
        interval = paired_bootstrap_ci(values, seed=R4_STATISTICAL_SEED + ordinal)
        results[label] = {
            "ordered_task_seed_differences": values,
            "sign_flip": sign,
            "bootstrap_95_ci": interval,
            "minimum_meaningful_effect": 0.25 if label == "B3_minus_B2" else None,
        }
        raw_p[label] = sign["p_value"]
    adjusted = holm_adjust(raw_p)
    for label in expected:
        results[label]["holm_adjusted_p_value"] = adjusted[label]
    return {
        "scope": "SMALL_SAMPLE_EXPLORATORY_MECHANISM_COMPARISON",
        "primary_comparison": "B3_minus_B2",
        "minimum_meaningful_task_success_effect": 0.25,
        "holm_family": list(expected),
        "comparisons": results,
        "significance_or_general_improvement_claim_allowed": False,
    }
