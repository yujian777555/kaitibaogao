"""Public failure profiles and fixed/random/adaptive D-094 operator selection."""
from __future__ import annotations

import math
import random
from typing import Any

from d094_prompts import assert_public_input


FAILURE_NAMES = (
    "planning_failure",
    "tool_call_failure",
    "dependency_failure",
    "recovery_failure",
    "verification_failure",
    "task_incompletion",
    "unnecessary_tool_call",
)
OPERATOR_NAMES = (
    "planning_mutation",
    "recovery_mutation",
    "memory_mutation",
    "verification_mutation",
    "tool_guard_mutation",
    "crossover",
)
FEEDBACK_MATRIX = (
    (1.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.25),
    (0.0, 0.0, 0.25, 1.0, 0.0, 0.5, 0.0),
    (0.25, 0.0, 0.0, 0.0, 0.0, 0.25, 0.5),
    (0.0, 0.25, 0.5, 0.0, 1.0, 0.0, 0.0),
    (0.0, 1.0, 0.5, 0.0, 0.25, 0.0, 0.0),
    (0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0),
)


def classify_failures(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify only public terminal states and tool events with explicit denominators."""
    assert_public_input(episodes)
    counts = {name: 0 for name in FAILURE_NAMES}
    tool_events = 0
    recovery_attempts = 0
    verification_attempts = 0
    successful_tools = 0
    for episode in episodes:
        status = episode.get("agent_status", "UNKNOWN")
        counts["task_incompletion"] += status != "COMPLETED"
        counts["planning_failure"] += status == "PREMATURE_FINISH"
        seen_successful_tools = set()
        for event in episode.get("events", []):
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            if event_type not in {"tool_result", "tool_rejected"}:
                continue
            tool_events += 1
            tool_name = str(payload.get("tool_name"))
            success = bool(payload.get("success"))
            observation = payload.get("observation", {})
            nested = observation.get("tool_result", {})
            error = str(
                observation.get(
                    "error",
                    nested.get("error", "") if isinstance(nested, dict) else "",
                )
            )
            counts["tool_call_failure"] += error in {
                "TOOL_SCHEMA_REJECTED",
                "UNKNOWN_OR_UNAVAILABLE_TOOL",
            }
            counts["dependency_failure"] += any(
                marker in error
                for marker in (
                    "DEPENDENCY",
                    "COMPENSATION_REQUIRED",
                    "PRIMARY_RECOVERY_REQUIRED",
                )
            )
            is_recovery = any(
                marker in tool_name for marker in ("retry", "recover", "compensate")
            )
            is_verification = "verify" in tool_name
            recovery_attempts += is_recovery
            verification_attempts += is_verification
            counts["recovery_failure"] += is_recovery and not success
            counts["verification_failure"] += is_verification and not success
            if event_type == "tool_result" and success:
                successful_tools += 1
                if tool_name in seen_successful_tools:
                    counts["unnecessary_tool_call"] += 1
                seen_successful_tools.add(tool_name)
    episode_count = len(episodes)
    denominators = {
        "episode_count": episode_count,
        "tool_event_count": tool_events,
        "recovery_attempt_count": recovery_attempts,
        "verification_attempt_count": verification_attempts,
        "successful_tool_call_count": successful_tools,
    }
    rates = {
        "planning_failure": counts["planning_failure"] / episode_count
        if episode_count
        else 0.0,
        "tool_call_failure": counts["tool_call_failure"] / tool_events
        if tool_events
        else 0.0,
        "dependency_failure": counts["dependency_failure"] / tool_events
        if tool_events
        else 0.0,
        "recovery_failure": counts["recovery_failure"] / recovery_attempts
        if recovery_attempts
        else 0.0,
        "verification_failure": counts["verification_failure"] / verification_attempts
        if verification_attempts
        else 0.0,
        "task_incompletion": counts["task_incompletion"] / episode_count
        if episode_count
        else 0.0,
        "unnecessary_tool_call": counts["unnecessary_tool_call"] / successful_tools
        if successful_tools
        else 0.0,
    }
    return {"counts": counts, "denominators": denominators, "rates": rates}


def feedback_features(profile: dict[str, Any]) -> dict[str, float]:
    """Map seven failure rates to six normalized operator features."""
    rates = profile["rates"]
    if set(rates) != set(FAILURE_NAMES):
        raise ValueError("failure profile schema mismatch")
    result = {}
    for index, name in enumerate(OPERATOR_NAMES):
        weights = FEEDBACK_MATRIX[index]
        normalizer = sum(weights)
        value = (
            sum(
                weight * rates[failure]
                for weight, failure in zip(weights, FAILURE_NAMES)
            )
            / normalizer
        )
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("feedback feature outside [0,1]")
        result[name] = value
    return result


def fixed_operator_probabilities() -> dict[str, float]:
    """Uniform six-operator control."""
    return {name: 1.0 / len(OPERATOR_NAMES) for name in OPERATOR_NAMES}


def operator_probabilities(
    profile: dict[str, Any],
    beta: float = 2.0,
    tau: float = 0.25,
    epsilon: float = 0.1,
) -> dict[str, float]:
    """Stable softmax feedback with a frozen minimum exploration probability."""
    if not math.isfinite(beta) or not math.isfinite(tau) or not math.isfinite(epsilon):
        raise ValueError("nonfinite feedback parameter")
    if tau <= 0.0 or epsilon <= 0.0 or epsilon >= 1.0:
        raise ValueError("invalid tau or exploration epsilon")
    features = feedback_features(profile)
    logits = {name: beta * features[name] / tau for name in OPERATOR_NAMES}
    shift = max(logits.values())
    weights = {name: math.exp(value - shift) for name, value in logits.items()}
    total = sum(weights.values())
    probabilities = {
        name: (1.0 - epsilon) * weights[name] / total + epsilon / len(OPERATOR_NAMES)
        for name in OPERATOR_NAMES
    }
    if abs(sum(probabilities.values()) - 1.0) > 1e-12:
        raise ValueError("operator probabilities are not normalized")
    return probabilities


def random_operator_probabilities(
    probabilities: dict[str, float], rng: random.Random
) -> dict[str, float]:
    """Randomly permute dynamic probabilities without changing their multiset."""
    if set(probabilities) != set(OPERATOR_NAMES):
        raise ValueError("operator probability schema mismatch")
    values = list(probabilities.values())
    rng.shuffle(values)
    return dict(zip(OPERATOR_NAMES, values))
