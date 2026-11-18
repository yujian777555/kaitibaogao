"""D-092 guarded execution, receipt accounting and independent state monitoring."""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_HERE = Path(__file__).resolve().parent
if str(_HERE.parent / "pilot_a3b") not in sys.path:
    sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))
from dependency_recovery import DependencyRecoveryEnv  # noqa: E402
from d092_genome import canonical_json_bytes, compensation_attempt_id, episode_reference  # noqa: E402

ACTION_LENGTHS = {"WAIT": 1, "RETRY_WORKFLOW": 1, "VERIFY": 2, "COMPENSATE": 3, "ESCALATE": 1, "STOP_SAFE": 1}
KNOWN_STATES = {"NOT_COMMITTED", "COMMITTED", "PARTIAL", "COMPENSATED"}
FAILURE_RECEIPTS = {"FAILED", "DEPENDENCY_BLOCKED", "CONTRACT_BLOCKED"}


def safe_action_snapshot(value: Any, active: Optional[set] = None) -> str:
    active = set() if active is None else active

    def convert(item: Any) -> Any:
        if item is None or type(item) in (bool, int, str):
            return item
        if type(item) is float:
            return item if math.isfinite(item) else {"type": "float", "value": str(item)}
        if type(item) in (tuple, list, dict):
            identity = id(item)
            if identity in active:
                return {"cycle": type(item).__name__}
            active.add(identity)
            try:
                if type(item) in (tuple, list):
                    return {"type": type(item).__name__, "items": [convert(x) for x in item]}
                return {"type": "dict", "items": [[convert(key), convert(val)] for key, val in item.items()]}
            finally:
                active.remove(identity)
        item_type = type(item)
        return {"unsupported_type": item_type.__module__ + "." + item_type.__qualname__}

    return canonical_json_bytes(convert(value)).decode("utf-8")


def validate_action(action: Any, view: Dict[str, Any]) -> bool:
    if type(action) not in (tuple, list) or not action:
        return False
    if type(action[0]) is not str or action[0] not in ACTION_LENGTHS:
        return False
    if len(action) != ACTION_LENGTHS[action[0]]:
        return False
    if any(type(value) is not str for value in action[1:]):
        return False
    if action[0] == "VERIFY":
        return action[1] in view["tools"]
    if action[0] == "COMPENSATE":
        tool = view["tools"].get(action[1])
        return tool is not None and any(route["name"] == action[2] for route in tool["routes"])
    return True


def public_action_allowed(action: Tuple[str, ...], view: Dict[str, Any]) -> bool:
    if action[0] != "RETRY_WORKFLOW":
        return True
    fault = view["terminal_fault"]
    if fault in ("permission", "timeout_before"):
        return True
    current = view["current_tool"]
    tool = view["tools"][current]
    pending = any(route["pending"] for route in tool["routes"])
    return tool["state"] == "COMPENSATED" and not pending


class AttemptLedger:
    def __init__(self, episode: str):
        self.episode = episode
        self.records: List[Dict[str, Any]] = []
        self.pending_by_tool: Dict[str, Tuple[str, str]] = {}
        self.verify_ordinal = 0

    def record_dispatch(self, tool: str, route: str, receipt: str, tick: int) -> Dict[str, Any]:
        ordinal = len(self.records)
        attempt_id = compensation_attempt_id(self.episode, ordinal)
        key = (self.episode, attempt_id)
        record = {
            "compensation_attempt_id": attempt_id,
            "attempt_key": key,
            "dispatch_ordinal": ordinal,
            "tool": tool,
            "route": route,
            "dispatch_tick": tick,
            "dispatch_observation": receipt,
            "closing_receipt": None,
            "terminal_receipt": None,
            "terminal_tick": None,
            "source_verify_ordinal": None,
            "terminal_recorded": False,
            "unresolved_at_episode_end": False,
            "failure_class": None,
        }
        if receipt != "TIMEOUT":
            record.update(
                closing_receipt=receipt,
                terminal_receipt=receipt,
                terminal_tick=tick,
                terminal_recorded=True,
                failure_class=receipt if receipt in FAILURE_RECEIPTS else None,
            )
        elif tool in self.pending_by_tool:
            raise ValueError("multiple pending routes for one tool")
        else:
            self.pending_by_tool[tool] = key
        self.records.append(record)
        return record

    def record_verify(self, tool: str, receipt: str, tick: int, had_pending: bool) -> None:
        ordinal = self.verify_ordinal
        self.verify_ordinal += 1
        if not had_pending or receipt == "PENDING":
            return
        if receipt not in ("COMPENSATED", "FAILED") or tool not in self.pending_by_tool:
            raise ValueError("VERIFY receipt cannot be linked to original attempt")
        key = self.pending_by_tool.pop(tool)
        matches = [record for record in self.records if record["attempt_key"] == key]
        if len(matches) != 1 or matches[0]["terminal_recorded"]:
            raise ValueError("attempt missing or closed twice")
        record = matches[0]
        record.update(
            closing_receipt=receipt,
            terminal_receipt=receipt,
            terminal_tick=tick,
            source_verify_ordinal=ordinal,
            terminal_recorded=True,
            failure_class="FAILED" if receipt == "FAILED" else None,
        )

    def finalize(self) -> None:
        for record in self.records:
            if not record["terminal_recorded"]:
                record["unresolved_at_episode_end"] = True

    def feedback_counts(self) -> Dict[str, int]:
        return {
            "attempt_count": len(self.records),
            "failure_attempt_count": sum(record["failure_class"] in FAILURE_RECEIPTS for record in self.records),
            "dependency_blocked_attempt_count": sum(record["failure_class"] == "DEPENDENCY_BLOCKED" for record in self.records),
        }


def _route_map(view: Dict[str, Any], tool: str) -> Dict[str, Dict]:
    return {route["name"]: route for route in view["tools"][tool]["routes"]}


def _transition_legal(
    before: Dict[str, Any],
    after: Dict[str, Any],
    action: Tuple[str, ...],
    observation: str,
    before_tick: int,
    after_tick: int,
    env: DependencyRecoveryEnv,
) -> bool:
    if set(before["tools"]) != set(after["tools"]):
        return False
    if any(tool["state"] not in KNOWN_STATES for tool in after["tools"].values()):
        return False
    expected_states = {tool: data["state"] for tool, data in before["tools"].items()}
    kind = action[0]
    if kind == "RETRY_WORKFLOW":
        current = before["current_tool"]
        state = expected_states[current]
        if before["terminal_fault"] == "timeout_before" and state == "NOT_COMMITTED" and observation == "COMMITTED":
            expected_states[current] = "COMMITTED"
        elif before["terminal_fault"] == "partial_recover" and state == "COMPENSATED" and observation == "COMMITTED":
            expected_states[current] = "COMMITTED"
    elif kind == "COMPENSATE" and observation in ("TIMEOUT", "COMPENSATED"):
        tool, route_name = action[1], action[2]
        if observation == "COMPENSATED":
            expected_states[tool] = "COMPENSATED"
        else:
            pending_success = env.routes[tool][route_name]["pending_success"]
            if pending_success is True:
                expected_states[tool] = "COMPENSATED"
    actual_states = {tool: data["state"] for tool, data in after["tools"].items()}
    if actual_states != expected_states:
        return False
    if after_tick != before_tick + (1 if kind == "WAIT" else 0):
        return False

    def pending_map(view: Dict[str, Any]) -> Dict[Tuple[str, str], bool]:
        return {
            (tool, route["name"]): route["pending"]
            for tool, data in view["tools"].items() for route in data["routes"]
        }

    before_pending = pending_map(before)
    after_pending = pending_map(after)
    expected_pending = dict(before_pending)
    if kind == "VERIFY":
        tool_pending = [route for route in _route_map(before, action[1]).values() if route["pending"]]
        if observation in ("COMPENSATED", "FAILED"):
            if len(tool_pending) != 1:
                return False
            expected_pending[(action[1], tool_pending[0]["name"])] = False
    elif kind == "COMPENSATE" and observation == "TIMEOUT":
        if before_pending[(action[1], action[2])]:
            return False
        expected_pending[(action[1], action[2])] = True
    if after_pending != expected_pending:
        return False

    before_attempts = {
        (tool, route["name"]): route["attempts"]
        for tool, data in before["tools"].items() for route in data["routes"]
    }
    after_attempts = {
        (tool, route["name"]): route["attempts"]
        for tool, data in after["tools"].items() for route in data["routes"]
    }
    if kind == "COMPENSATE" and observation in ("TIMEOUT", "FAILED", "COMPENSATED"):
        key = (action[1], action[2])
        if after_attempts[key] != before_attempts[key] + 1:
            return False
        after_attempts[key] = before_attempts[key]
    if after_attempts != before_attempts:
        return False
    if kind in ("ESCALATE", "STOP_SAFE"):
        return env.terminal_action == kind
    return env.terminal_action is None


def run_guarded_episode(
    policy,
    scenario: Dict[str, Any],
    seed: int = 711,
    unique_ordinal: int = 0,
    typed_genome_sha256: str = "g",
) -> Dict[str, Any]:
    env = DependencyRecoveryEnv(scenario)
    episode = episode_reference(seed, unique_ordinal, typed_genome_sha256, scenario["scenario_id"])
    ledger = AttemptLedger(episode)
    invalid_count = 0
    unauthorized_count = 0
    illegal_count = 0
    adapter_events = []
    transition_records = []
    request_count = 0
    while not env.task_success() and env.terminal_action is None:
        if env.decision_count >= 24 or request_count >= 24:
            env.runtime_forced_abort = True
            break
        request_count += 1
        original_action = policy(env.view())
        before = env.view()
        before_tick = env.tick
        if not validate_action(original_action, before):
            snapshot = safe_action_snapshot(original_action)
            action = ("INVALID",)
            observation = env.step(action)
            invalid_count += 1
            adapter_events.append({
                "kind": "grammar_invalid",
                "malformed_action_snapshot": snapshot,
                "sentinel": list(action),
                "observation": observation,
                "trace_index": len(env.trace) - 1,
            })
        else:
            action = tuple(original_action)
            if not public_action_allowed(action, before):
                unauthorized_count += 1
                adapter_events.append({
                    "kind": "unauthorized",
                    "action": list(action),
                    "observation": "UNAUTHORIZED_ACTION",
                    "trace_index": None,
                })
                transition_records.append({
                    "before": before,
                    "action": list(action),
                    "mask_result": "UNAUTHORIZED",
                    "observation": "UNAUTHORIZED_ACTION",
                    "after": env.view(),
                    "before_tick": before_tick,
                    "after_tick": env.tick,
                    "legal": True,
                })
                continue
            observation = env.step(action)
        after = env.view()
        legal = _transition_legal(before, after, action, observation, before_tick, env.tick, env)
        transition_records.append({
            "before": before,
            "action": list(action),
            "mask_result": "SENTINEL" if action == ("INVALID",) else "ALLOWED",
            "observation": observation,
            "after": after,
            "before_tick": before_tick,
            "after_tick": env.tick,
            "legal": legal,
        })
        if not legal:
            illegal_count += 1
        if action[0] == "COMPENSATE" and observation != "INVALID_ACTION":
            ledger.record_dispatch(action[1], action[2], observation, env.tick)
        elif action[0] == "VERIFY":
            had_pending = any(route["pending"] for route in _route_map(before, action[1]).values())
            ledger.record_verify(action[1], observation, env.tick, had_pending)
    ledger.finalize()
    report = env.report()
    duplicate_events = sum(event["observation"] == "DUPLICATE_COMPENSATION" for event in report["trace"])
    if duplicate_events != report["duplicate_compensation"]:
        raise ValueError("duplicate ledger/report mismatch")
    counts = ledger.feedback_counts()
    report.update(counts)
    report.update({
        "episode_reference": episode,
        "attempt_records": ledger.records,
        "adapter_events": adapter_events,
        "transition_records": transition_records,
        "invalid_action_count": invalid_count + sum(event["observation"] == "INVALID_ACTION" for event in report["trace"] if event["action"] != ["INVALID"]),
        "unauthorized_action_count": unauthorized_count,
        "illegal_state_transition_count": illegal_count,
        "pending_count": report["pending_compensation"],
        "duplicate_count": report["duplicate_compensation"],
        "runtime_abort_count": int(bool(env.runtime_forced_abort)),
        "contract_blocked_attempts": sum(record["closing_receipt"] == "CONTRACT_BLOCKED" for record in ledger.records),
        "dependency_blocked_attempts": sum(record["closing_receipt"] == "DEPENDENCY_BLOCKED" for record in ledger.records),
    })
    report["constraint_episode"] = int(any(report[field] > 0 for field in (
        "invalid_action_count", "unauthorized_action_count", "illegal_state_transition_count",
        "pending_count", "duplicate_count", "runtime_abort_count",
    )))
    return report
