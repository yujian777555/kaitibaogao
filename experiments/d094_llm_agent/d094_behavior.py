"""Canonical public behavior representation and frozen D-094 distance functions."""
from __future__ import annotations

from typing import Any

from d094_ledger import canonical_json_bytes, payload_sha256
from d094_prompts import assert_public_input


FEATURE_WEIGHTS = {
    "tool_call_count": 2.0,
    "verification_count": 1.0,
    "recovery_count": 2.0,
    "failed_call_count": 2.0,
    "rejected_call_count": 1.0,
    "retry_count": 2.0,
    "completed": 1.0,
    "runtime_abort": 1.0,
    "state_transition_count": 1.0,
}
FEATURE_SCALES = {
    "tool_call_count": 8.0,
    "verification_count": 4.0,
    "recovery_count": 4.0,
    "failed_call_count": 8.0,
    "rejected_call_count": 8.0,
    "retry_count": 8.0,
    "completed": 1.0,
    "runtime_abort": 1.0,
    "state_transition_count": 16.0,
}
FEATURE_WEIGHT_SUM = sum(FEATURE_WEIGHTS.values())


def behavior_representation(
    events: list[dict[str, Any]],
    agent_status: str = "UNKNOWN",
    final_public_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project public execution events into behavior, excluding wording and cost metadata."""
    assert_public_input(events)
    if final_public_observation is not None:
        assert_public_input(final_public_observation)
    sequence = []
    features = {name: 0.0 for name in FEATURE_WEIGHTS}
    transitions = []
    for event in events:
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        if event_type == "decision":
            action = payload.get("action")
            tool_name = payload.get("tool_name")
            arguments = canonical_json_bytes(payload.get("tool_arguments", {})).decode(
                "utf-8"
            )
            sequence.append(f"D|{action}|{tool_name}|{arguments}")
            if action == "tool_call":
                features["tool_call_count"] += 1
                features["verification_count"] += "verify" in str(tool_name)
                features["recovery_count"] += any(
                    word in str(tool_name) for word in ("recover", "compensate")
                )
                features["retry_count"] += "retry" in str(tool_name)
        elif event_type in {"tool_result", "tool_rejected"}:
            observation = canonical_json_bytes(payload.get("observation", {})).decode(
                "utf-8"
            )
            success = bool(payload.get("success"))
            done = bool(payload.get("done"))
            sequence.append(
                f"R|{event_type}|{payload.get('tool_name')}|{success}|{done}|{observation}"
            )
            features["failed_call_count"] += event_type == "tool_result" and not success
            features["rejected_call_count"] += event_type == "tool_rejected"
            if "before_state" in payload and "after_state" in payload:
                before = payload["before_state"]
                after = payload["after_state"]
                if before != after:
                    transitions.append({"before": before, "after": after})
        elif event_type == "run_finished":
            sequence.append(f"T|{payload.get('status')}")
    features["state_transition_count"] = float(len(transitions))
    final_state = (final_public_observation or {}).get("state", {})
    features["completed"] = float(
        agent_status == "COMPLETED" or final_state.get("completed") is True
    )
    features["runtime_abort"] = float(agent_status == "MAX_STEPS")
    canonical = {
        "sequence": sequence,
        "features": features,
        "terminal_status": agent_status,
        "state_transitions": transitions,
    }
    return {**canonical, "canonical_sha256": payload_sha256(canonical)}


def sequence_edit_distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Compute Levenshtein distance divided by the longer sequence length."""
    left = first["sequence"]
    right = second["sequence"]
    if not left and not right:
        return 0.0
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (a != b),
                )
            )
        previous = current
    return previous[-1] / max(len(left), len(right))


def feature_distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Compute frozen weighted, normalized absolute behavior-feature distance."""
    total = 0.0
    for name, weight in FEATURE_WEIGHTS.items():
        scale = FEATURE_SCALES[name]
        difference = abs(first["features"][name] - second["features"][name]) / scale
        total += weight * min(1.0, difference)
    return total / FEATURE_WEIGHT_SUM


def behavior_distance(
    first: dict[str, Any], second: dict[str, Any], metric: str = "edit"
) -> float:
    """Select one pre-registered public behavior distance."""
    if metric == "edit":
        return sequence_edit_distance(first, second)
    if metric == "feature":
        return feature_distance(first, second)
    raise ValueError("unknown behavior distance: " + metric)
