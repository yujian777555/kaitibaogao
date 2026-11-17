"""D-092 R2.3 aggregate-only dynamic failure feedback."""
from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple

FEEDBACK_NAMES = ("r", "d", "p", "a", "u", "h")
MARGINAL_NAMES = (
    "row_count",
    "attempt_count",
    "failure_attempt_count",
    "dependency_blocked_attempt_count",
    "pending_row_count",
    "runtime_abort_row_count",
    "unsuccessful_escalation_row_count",
    "avoidable_harm_sum",
)
MATRIX = (
    (0.0, 0.5, 0.0, 0.5, 0.0, 0.0),
    (0.5, 0.5, 0.0, 0.0, 0.0, 0.0),
    (0.0, 0.0, 0.5, 0.25, 0.25, 0.0),
    (0.0, 0.0, 0.0, 0.0, 0.0, 1.0),
)


def combine_feedback(views: Iterable[Dict]) -> Dict[str, float]:
    combined = {name: 0.0 for name in MARGINAL_NAMES}
    count = 0
    for view in views:
        marginals = view["feedback_marginals"]
        if set(marginals) != set(MARGINAL_NAMES):
            raise ValueError("unexpected feedback marginal schema")
        for name in MARGINAL_NAMES:
            value = marginals[name]
            if not math.isfinite(value):
                raise ValueError("nonfinite feedback marginal")
            combined[name] += value
        count += 1
    if count == 0:
        raise ValueError("feedback requires a nonempty completed offspring set")
    combined["row_count"] = int(combined["row_count"])
    return combined


def compute_feedback(combined: Dict[str, float]) -> Dict[str, float]:
    n = combined["row_count"]
    if n <= 0 or n != int(n):
        raise ValueError("invalid feedback row denominator")
    c = combined["attempt_count"]
    failed = combined["failure_attempt_count"]
    dependency = combined["dependency_blocked_attempt_count"]
    if min(c, failed, dependency) < 0 or failed > c or dependency > failed:
        raise ValueError("invalid attempt/failure/dependency counts")
    result = {
        "r": failed / max(1.0, c),
        "d": dependency / max(1.0, c),
        "p": combined["pending_row_count"] / n,
        "a": combined["runtime_abort_row_count"] / n,
        "u": combined["unsuccessful_escalation_row_count"] / n,
        "h": min(1.0, combined["avoidable_harm_sum"] / (4.0 * n)),
    }
    for name in ("pending_row_count", "runtime_abort_row_count", "unsuccessful_escalation_row_count", "avoidable_harm_sum"):
        if combined[name] < 0:
            raise ValueError("negative feedback count: " + name)
    if not 0.0 <= result["d"] <= result["r"] <= 1.0:
        raise ValueError("attempt-level r/d bounds violated")
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in result.values()):
        raise ValueError("feedback feature outside [0,1]")
    return result


def feedback_features(features: Dict[str, float]) -> Tuple[float, float, float, float]:
    vector = tuple(features[name] for name in FEEDBACK_NAMES)
    if len(vector) != 6:
        raise ValueError("feedback vector must have six features")
    return tuple(sum(row[index] * vector[index] for index in range(6)) for row in MATRIX)


def operator_probabilities(
    features: Tuple[float, ...],
    beta: float = 2.0,
    tau: float = 0.25,
    epsilon: float = 0.1,
) -> Tuple[float, float, float, float]:
    if len(features) != 4:
        raise ValueError("expected four operator-block features")
    if not all(math.isfinite(value) for value in features):
        raise ValueError("nonfinite operator feature")
    if min(tau, epsilon, 1.0 - epsilon) <= 0.0:
        raise ValueError("invalid tau/epsilon")
    logits = [beta * value / tau for value in features]
    shift = max(logits)
    weights = [math.exp(value - shift) for value in logits]
    total = sum(weights)
    probabilities = tuple((1.0 - epsilon) * weight / total + epsilon / 4.0 for weight in weights)
    if abs(sum(probabilities) - 1.0) > 1e-12:
        raise ValueError("operator probabilities are not normalized")
    return probabilities
