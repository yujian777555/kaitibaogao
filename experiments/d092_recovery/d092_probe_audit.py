"""Independent, read-only recomputation of the executed D-092 Probe artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

from d092_genome import TypedGenome
from d088_policies import D088RecoveryPolicy
from d090_policies import D090Policy
from d089_budget import public_min_harm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results" / "probe"
MANIFEST = ROOT / "experiments" / "d090_recovery" / "results" / "d090_train_manifest.json"
PROBE_IDS = tuple(f"P{index:02d}" for index in range(10))
HARD_FIELDS = (
    "invalid_action_count",
    "unauthorized_action_count",
    "illegal_state_transition_count",
    "pending_count",
    "duplicate_count",
    "runtime_abort_count",
)
FAILURE_RECEIPTS = {"FAILED", "DEPENDENCY_BLOCKED", "CONTRACT_BLOCKED"}
ANCHORS = {
    "Q0": "d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r0",
    "Q0b": "d090r|train|d090_PAIR_RACE|D4_BLOCKED_COMPENSATION|r0",
    "Q1": "d090r|train|d090_MULTI_ROUTE|D3_DEPENDENT_ABORT|r0",
    "Q2": "d090r|train|d090_FANOUT_DELAY|D3_DEPENDENT_ABORT|r1",
    "Q3": "d090r|train|d090_DEEP_CHAIN|D3_DEPENDENT_ABORT|r1",
    "Q4": "d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r1",
}
P07_PREFIX = [
    (("COMPENSATE", "C", "primary"), "TIMEOUT"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "C"), "PENDING"),
    (("WAIT",), "WAITED"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "C"), "FAILED"),
    (("COMPENSATE", "C", "primary"), "TIMEOUT"),
    (("COMPENSATE", "B", "primary"), "TIMEOUT"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "B"), "PENDING"),
    (("WAIT",), "WAITED"),
    (("WAIT",), "WAITED"),
    (("VERIFY", "B"), "FAILED"),
    (("VERIFY", "C"), "COMPENSATED"),
]


def _normalized(value: Any) -> Any:
    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("nonfinite canonical value")
        return 0.0 if value == 0.0 else float(format(value, ".12g"))
    if isinstance(value, list):
        return [_normalized(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("nonstring canonical key")
        return {key: _normalized(value[key]) for key in sorted(value)}
    raise ValueError("unsupported canonical type: " + type(value).__name__)


def _digest(value: Any) -> str:
    encoded = json.dumps(
        _normalized(value), ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _file_digest(path: Path) -> Tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _add_error(errors: List[str], condition: bool, code: str) -> None:
    if not condition and code not in errors:
        errors.append(code)


def _expected_hashes(report: Dict[str, Any]) -> Dict[str, str]:
    trace_hash = _digest(report["trace"])
    excluded = {"trace", "transition_records", "attempt_records", "adapter_events", "episode_reference"}
    outcome_hash = _digest({key: value for key, value in report.items() if key not in excluded})
    joint_hash = _digest({
        "episode_reference": report["episode_reference"],
        "outcome": outcome_hash,
        "trace": trace_hash,
    })
    return {"trace_sha256": trace_hash, "outcome_sha256": outcome_hash, "joint_sha256": joint_hash}


def audit_episode_row(row: Dict[str, Any], lock: Dict[str, Any], train_ids: set[str]) -> List[str]:
    errors: List[str] = []
    probe = row.get("probe_id")
    if probe not in PROBE_IDS:
        return ["probe_identity_mismatch"]
    report = row["report"]
    scenario_id = row["scenario_id"]
    expected_typed = lock["probe_genomes"][probe]["typed"]
    expected_genome_hash = _digest(expected_typed)
    _add_error(errors, row["typed_genome"] == expected_typed, "typed_genome_mismatch")
    _add_error(errors, row["genome_sha256"] == expected_genome_hash == _digest(row["typed_genome"]), "genome_hash_mismatch")
    _add_error(errors, lock["probe_genomes"][probe]["genome_sha256"] == expected_genome_hash, "lock_genome_hash_mismatch")
    _add_error(errors, scenario_id in train_ids and scenario_id.split("|")[1] == "train", "train_membership_mismatch")
    _add_error(errors, report["scenario_id"] == scenario_id, "scenario_identity_mismatch")
    episode = _digest({
        "seed": lock["seed"], "unique_ordinal": PROBE_IDS.index(probe),
        "genome_sha256": expected_genome_hash, "scenario_id": scenario_id,
    })
    _add_error(errors, report["episode_reference"] == episode, "episode_reference_mismatch")

    trace = report["trace"]
    transitions = report["transition_records"]
    adapter_events = report["adapter_events"]
    _add_error(errors, report["decision_count"] == len(trace), "decision_count_mismatch")
    _add_error(errors, report["recovery_cost"] == sum(event["cost"] for event in trace), "recovery_cost_mismatch")
    trace_index = 0
    previous_after = None
    for transition in transitions:
        mask = transition["mask_result"]
        _add_error(errors, mask in {"ALLOWED", "SENTINEL", "UNAUTHORIZED"}, "unknown_mask_result")
        transition_fields = {"before", "action", "mask_result", "observation", "after", "before_tick", "after_tick", "legal"}
        _add_error(errors, set(transition) == transition_fields, "transition_schema_mismatch")
        if previous_after is not None:
            _add_error(errors, transition["before"] == previous_after, "transition_chain_mismatch")
        previous_after = transition["after"]
        before = transition["before"]
        after = transition["after"]
        if mask == "UNAUTHORIZED":
            _add_error(errors, before == after and transition["before_tick"] == transition["after_tick"], "unauthorized_state_mutation")
            _add_error(errors, transition["observation"] == "UNAUTHORIZED_ACTION", "unauthorized_receipt_mismatch")
            continue
        _add_error(errors, after["decision_count"] == before["decision_count"] + 1, "transition_decision_mismatch")
        _add_error(errors, after["budget_remaining"] == before["budget_remaining"] - 1, "transition_budget_mismatch")
        if trace_index >= len(trace):
            _add_error(errors, False, "trace_transition_mismatch")
            continue
        event = trace[trace_index]
        _add_error(
            errors,
            transition["action"] == event["action"] and transition["observation"] == event["observation"],
            "trace_transition_mismatch",
        )
        trace_index += 1
    _add_error(errors, trace_index == len(trace), "trace_transition_mismatch")

    unauthorized = [transition for transition in transitions if transition["mask_result"] == "UNAUTHORIZED"]
    _add_error(errors, len(unauthorized) == report["unauthorized_action_count"], "unauthorized_count_mismatch")
    _add_error(
        errors,
        Counter(_digest(event["action"]) for event in unauthorized)
        == Counter(_digest(event["action"]) for event in adapter_events if event["kind"] == "unauthorized"),
        "unauthorized_event_mismatch",
    )
    _add_error(errors, sum(not transition["legal"] for transition in transitions) == report["illegal_state_transition_count"], "illegal_count_mismatch")
    grammar_invalid = sum(event["kind"] == "grammar_invalid" for event in adapter_events)
    invalid = grammar_invalid + sum(
        event["observation"] == "INVALID_ACTION" and event["action"] != ["INVALID"] for event in trace
    )
    _add_error(errors, invalid == report["invalid_action_count"], "invalid_count_mismatch")
    duplicates = sum(event["observation"] == "DUPLICATE_COMPENSATION" for event in trace)
    _add_error(errors, duplicates == report["duplicate_count"] == report["duplicate_compensation"], "duplicate_count_mismatch")
    _add_error(errors, report["pending_count"] == report["pending_compensation"], "pending_count_mismatch")
    _add_error(errors, report["runtime_abort_count"] == int(bool(report["runtime_forced_abort"])), "runtime_abort_mismatch")
    expected_constraint = int(any(report[field] > 0 for field in HARD_FIELDS))
    _add_error(errors, report["constraint_episode"] == expected_constraint, "constraint_episode_mismatch")

    dispatches = [
        event for event in trace
        if event["action"][0] == "COMPENSATE" and event["observation"] != "INVALID_ACTION"
    ]
    attempts = report["attempt_records"]
    _add_error(errors, len(attempts) == len(dispatches), "attempt_count_mismatch")
    verifies = [event for event in trace if event["action"][0] == "VERIFY"]
    lifecycle_valid = True
    for ordinal, (record, event) in enumerate(zip(attempts, dispatches)):
        attempt_id = _digest({"episode_reference": episode, "dispatch_ordinal": ordinal})
        expected = {
            "compensation_attempt_id": attempt_id,
            "attempt_key": [episode, attempt_id],
            "dispatch_ordinal": ordinal,
            "tool": event["action"][1],
            "route": event["action"][2],
            "dispatch_tick": event["tick"],
            "dispatch_observation": event["observation"],
        }
        if any(record.get(key) != value for key, value in expected.items()):
            lifecycle_valid = False
        receipt = event["observation"]
        if receipt != "TIMEOUT":
            closed = {
                "closing_receipt": receipt, "terminal_receipt": receipt,
                "terminal_tick": event["tick"], "source_verify_ordinal": None,
                "terminal_recorded": True, "unresolved_at_episode_end": False,
                "failure_class": receipt if receipt in FAILURE_RECEIPTS else None,
            }
            if any(record.get(key) != value for key, value in closed.items()):
                lifecycle_valid = False
        elif not record["terminal_recorded"]:
            open_record = {
                "closing_receipt": None, "terminal_receipt": None, "terminal_tick": None,
                "source_verify_ordinal": None, "unresolved_at_episode_end": True, "failure_class": None,
            }
            if any(record.get(key) != value for key, value in open_record.items()):
                lifecycle_valid = False
        else:
            verify_ordinal = record["source_verify_ordinal"]
            if not isinstance(verify_ordinal, int) or not 0 <= verify_ordinal < len(verifies):
                lifecycle_valid = False
                continue
            verify = verifies[verify_ordinal]
            terminal = verify["observation"]
            closed = {
                "closing_receipt": terminal, "terminal_receipt": terminal,
                "terminal_tick": verify["tick"], "unresolved_at_episode_end": False,
                "failure_class": "FAILED" if terminal == "FAILED" else None,
            }
            if verify["action"][1] != record["tool"] or terminal not in {"COMPENSATED", "FAILED"}:
                lifecycle_valid = False
            if any(record.get(key) != value for key, value in closed.items()):
                lifecycle_valid = False
    _add_error(errors, lifecycle_valid, "attempt_lifecycle_mismatch")
    expected_feedback = {
        "attempt_count": len(attempts),
        "failure_attempt_count": sum(record["failure_class"] in FAILURE_RECEIPTS for record in attempts),
        "dependency_blocked_attempt_count": sum(record["failure_class"] == "DEPENDENCY_BLOCKED" for record in attempts),
        "contract_blocked_attempts": sum(record["closing_receipt"] == "CONTRACT_BLOCKED" for record in attempts),
        "dependency_blocked_attempts": sum(record["closing_receipt"] == "DEPENDENCY_BLOCKED" for record in attempts),
    }
    _add_error(errors, all(report.get(key) == value for key, value in expected_feedback.items()), "feedback_count_mismatch")

    expected_hashes = _expected_hashes(report)
    hash_error_codes = {
        "trace_sha256": "trace_hash_mismatch",
        "outcome_sha256": "outcome_hash_mismatch",
        "joint_sha256": "joint_hash_mismatch",
    }
    for key, value in expected_hashes.items():
        _add_error(errors, row["episode_hashes"].get(key) == value, hash_error_codes[key])
    return errors


def _events(report: Dict[str, Any]) -> List[Tuple[Tuple[str, ...], str]]:
    return [(tuple(event["action"]), event["observation"]) for event in report["trace"]]


def _first_difference(first: Dict[str, Any], second: Dict[str, Any]) -> int | None:
    left = _events(first)
    right = _events(second)
    for index, pair in enumerate(zip(left, right)):
        if pair[0] != pair[1]:
            return index
    return None if len(left) == len(right) else min(len(left), len(right))


def _action(report: Dict[str, Any], index: int) -> Tuple[str, ...]:
    return tuple(report["trace"][index]["action"])


def _before(report: Dict[str, Any], index: int) -> Dict[str, Any]:
    return report["transition_records"][index]["before"]


def _genome(lock: Dict[str, Any], probe: str):
    return TypedGenome(**lock["probe_genomes"][probe]["typed"]).to_d090()


def _available(lock: Dict[str, Any], probe: str, view: Dict[str, Any], fallback: bool = False):
    policy = D090Policy(_genome(lock, probe))
    return policy._available_or_fallback(view) if fallback else policy._available(view)


def _ordinary(lock: Dict[str, Any], probe: str, view: Dict[str, Any], available) -> Tuple[str, str]:
    return D088RecoveryPolicy(_genome(lock, probe))._priority(view, available)[1:]


def _tight(lock: Dict[str, Any], probe: str, view: Dict[str, Any], available) -> Tuple[str, str]:
    return D090Policy(_genome(lock, probe))._priority(view, available)[1:]


def _p07_valid(report: Dict[str, Any]) -> bool:
    if len(report["trace"]) < 14 or len(report["transition_records"]) < 14:
        return False
    if _events(report)[:14] != P07_PREFIX:
        return False
    after7 = report["transition_records"][6]["after"]
    after14 = report["transition_records"][13]["after"]
    return (
        after7["tools"]["C"]["state"] == "COMPENSATED"
        and report["transition_records"][6]["observation"] == "TIMEOUT"
        and after14["decision_count"] == 14
        and after14["budget_remaining"] == 10
        and after14["tools"]["C"]["state"] == "COMPENSATED"
        and not any(route["pending"] for route in after14["tools"]["C"]["routes"])
        and after14["tools"]["B"]["routes"][0]["last_receipt"] == "FAILED"
    )


def _recompute_criteria(
    lock: Dict[str, Any], anchors: Dict[Tuple[str, str], Dict[str, Any]],
    counts: Counter, legal: Dict[str, bool],
) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}

    def row(probe: str, anchor: str) -> Dict[str, Any]:
        return anchors[(probe, ANCHORS[anchor])]["report"]

    def finish(probe: str, checks: Dict[str, bool], details: Dict[str, Any]) -> None:
        checks = {"complete_96_and_legal_monitor": counts[probe] == 96 and legal[probe], **checks}
        result[probe] = {
            "episode_count": counts[probe], "checks": checks, "details": details,
            "status": "PASS" if all(checks.values()) else "HOLD",
        }

    for probe in PROBE_IDS:
        if probe == "P00":
            finish(probe, {}, {"baseline": "complete 96 rows; no performance gate"})
        elif probe in {"P01", "P02"}:
            baseline = row("P00", "Q0")
            other = row(probe, "Q0")
            first = next(event for event in baseline["trace"] if event["action"][0] == "COMPENSATE")
            contrast = next(event for event in other["trace"] if event["action"][0] == "COMPENSATE")
            q0 = (
                first["action"][1] in {"A", "B"} and first["action"][2] == "alternate"
                and contrast["action"] == ["COMPENSATE", "C", "primary"]
                and _first_difference(baseline, other) is not None
            )
            off = row("P01", "Q0b")
            filtered = row("P02", "Q0b")
            difference = _first_difference(off, filtered)
            q0b = False
            if difference is not None:
                state = _before(off, difference)
                q0b = (
                    _before(off, difference) == _before(filtered, difference)
                    and _action(off, difference) == ("COMPENSATE", "C", "primary")
                    and _action(filtered, difference) == ("WAIT",)
                    and any(route["pending"] for tool in ("A", "B") for route in state["tools"][tool]["routes"])
                )
            finish(probe, {"q0_alternate_vs_primary": q0, "q0b_off_vs_filter": q0b}, {"q0b_first_difference": difference})
        elif probe == "P03":
            enabled = row("P01", "Q1")
            disabled = row("P03", "Q1")
            state = enabled["transition_records"][0]["before"]
            normal = _available(lock, "P01", state)
            fallback = D090Policy(_genome(lock, "P01"))._fallback_available(state)
            fallback_set = {(tool, route["name"]) for tool, route in fallback}
            passed = (
                not normal and fallback_set == {("A", "alternate"), ("B", "alternate"), ("C", "alternate")}
                and _action(enabled, 0)[0] == "COMPENSATE" and _action(enabled, 0)[2] == "alternate"
                and _action(disabled, 0) == ("ESCALATE",) and _first_difference(enabled, disabled) == 0
            )
            finish(probe, {"q1_initial_fallback": passed}, {"fallback_candidates": [list(item) for item in sorted(fallback_set)]})
        elif probe == "P04":
            baseline = row("P00", "Q2")
            disabled = row("P04", "Q2")
            difference = _first_difference(baseline, disabled)
            passed = False
            if difference is not None:
                state = _before(baseline, difference)
                available = _available(lock, "P00", state, fallback=True)
                active = sum(tool["state"] in {"COMMITTED", "PARTIAL"} for tool in state["tools"].values())
                passed = (
                    state == _before(disabled, difference)
                    and active > public_min_harm(state) and bool(available)
                    and D090Policy(_genome(lock, "P00"))._can_dispatch_more(state)
                    and _action(baseline, difference)[0] not in {"ESCALATE", "STOP_SAFE"}
                    and _action(disabled, difference) in {("ESCALATE",), ("STOP_SAFE",)}
                )
            finish(probe, {"q2_completion_override": passed}, {"first_difference": difference})
        elif probe in {"P05", "P06"}:
            baseline = row("P00", "Q3")
            other = row(probe, "Q3")
            difference = _first_difference(baseline, other)
            passed = False
            if difference is not None:
                state = _before(baseline, difference)
                available = _available(lock, "P00", state)
                if len(available) >= 2:
                    ordinary = _ordinary(lock, "P00", state, available)
                    tight = _tight(lock, "P00", state, available)
                    budget = state["budget_remaining"]
                    in_window = budget <= 8 if probe == "P05" else 4 < budget <= 8
                    passed = (
                        state == _before(other, difference) and in_window and ordinary != tight
                        and _action(baseline, difference)[1:] == tight
                        and _action(other, difference)[1:] == ordinary
                    )
            finish(probe, {"q3_harm_priority_window": passed}, {"first_difference": difference})
        elif probe == "P07":
            ordinary_probe = row("P06", "Q3")
            tight_probe = row("P07", "Q3")
            prefix = _p07_valid(ordinary_probe) and _p07_valid(tight_probe)
            state = ordinary_probe["transition_records"][13]["after"]
            available = _available(lock, "P06", state)
            ordinary = _ordinary(lock, "P06", state, available)
            tight = _tight(lock, "P07", state, available)
            branch = (
                len(ordinary_probe["trace"]) > 14 and len(tight_probe["trace"]) > 14
                and state["budget_remaining"] == 10 and state["tools"]["C"]["state"] == "COMPENSATED"
                and _action(ordinary_probe, 14)[1:] == ordinary == ("B", "primary")
                and _action(tight_probe, 14)[1:] == tight == ("B", "alternate")
                and _first_difference(ordinary_probe, tight_probe) == 14
            )
            finish(probe, {"q3_exact_14_prefix": prefix, "q3_budget_10_branch": branch}, {"first_difference": _first_difference(ordinary_probe, tight_probe)})
        elif probe in {"P08", "P09"}:
            baseline = row("P00", "Q4")
            other = row(probe, "Q4")
            difference = _first_difference(baseline, other)
            passed = False
            if difference is not None:
                state = _before(baseline, difference)
                available = _available(lock, "P00", state)
                prefix = baseline["trace"][:difference]
                dispatch = max((index for index, event in enumerate(prefix) if event["action"][0] == "COMPENSATE"), default=None)
                elapsed = 0 if dispatch is None else sum(event["action"][0] == "WAIT" for event in prefix[dispatch + 1:])
                no_pending_verify = True if dispatch is None else not any(
                    event["action"][0] == "VERIFY" and event["observation"] == "PENDING"
                    for event in prefix[dispatch + 1:]
                )
                pending = any(route["pending"] for tool in state["tools"].values() for route in tool["routes"])
                if probe == "P08":
                    expected = elapsed == 0 and _action(baseline, difference) == ("WAIT",) and _action(other, difference)[0] == "VERIFY"
                else:
                    expected = elapsed == 1 and _action(baseline, difference)[0] == "VERIFY" and _action(other, difference) == ("WAIT",)
                passed = (
                    state == _before(other, difference) and pending and not available
                    and no_pending_verify and expected
                )
            finish(probe, {"q4_delay_probe_cadence": passed}, {"first_difference": difference})
    return result


def _q3_diagnostic(lock: Dict[str, Any], anchors: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, Any]:
    baseline = anchors[("P00", ANCHORS["Q3"])]["report"]
    p05 = anchors[("P05", ANCHORS["Q3"])]["report"]
    p06 = anchors[("P06", ANCHORS["Q3"])]["report"]
    states = []
    p05_eligible = []
    p06_eligible = []
    for index, transition in enumerate(baseline["transition_records"]):
        state = transition["before"]
        budget = state["budget_remaining"]
        if budget > 8:
            continue
        available = _available(lock, "P00", state)
        ordinary = list(_ordinary(lock, "P00", state, available)) if available else None
        tight = list(_tight(lock, "P00", state, available)) if available else None
        actual = transition["action"]
        pending = any(route["pending"] for tool in state["tools"].values() for route in tool["routes"])
        can_dispatch = D090Policy(_genome(lock, "P00"))._can_dispatch_more(state)
        item = {
            "step": index, "budget_remaining": budget,
            "available": [[tool, route["name"]] for tool, route in available],
            "ordinary": ordinary, "tight": tight, "actual_action": actual,
            "pending": pending, "can_dispatch_more": can_dispatch,
        }
        states.append(item)
        eligible = (
            len(available) >= 2 and ordinary != tight
            and actual == ["COMPENSATE", *tight]
        )
        if eligible:
            p05_eligible.append(index)
            if 4 < budget <= 8:
                p06_eligible.append(index)
    return {
        "p00_p05_trace_equal": _events(baseline) == _events(p05),
        "p00_p06_trace_equal": _events(baseline) == _events(p06),
        "p00_p05_first_difference": _first_difference(baseline, p05),
        "p00_p06_first_difference": _first_difference(baseline, p06),
        "p05_eligible_steps": p05_eligible,
        "p06_eligible_steps": p06_eligible,
        "reason_code": "NO_EXECUTABLE_PRIORITY_DIVERGENCE_IN_PREREGISTERED_WINDOW",
        "states": states,
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError("Probe audit failed: " + message)


def audit_probe(outdir: Path = RESULTS) -> Dict[str, Any]:
    outdir = Path(outdir)
    episodes_path = outdir / "episodes.jsonl"
    lock_path = outdir / "execution_lock.json"
    summary_path = outdir / "probe_summary.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest_raw = MANIFEST.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    manifest_internal = dict(manifest)
    internal_hash = manifest_internal.pop("manifest_sha256")
    _require(_digest(manifest_internal) == internal_hash, "Train manifest internal SHA")
    manifest_canonical = hashlib.sha256(b"\n".join(manifest_raw.splitlines())).hexdigest()
    _require(manifest_canonical == lock["manifest_canonical_sha256"], "Train manifest canonical SHA")
    _require(internal_hash == lock["manifest_internal_sha256"], "Train manifest hash binding")
    _require(manifest["scenario_count"] == 96 and len(manifest["scenarios"]) == 96, "Train scenario count")
    _require(not manifest["test_included"] and not manifest["test_outcomes_read"], "Train-only manifest flags")
    train_ids = {scenario["scenario_id"] for scenario in manifest["scenarios"]}
    _require(len(train_ids) == 96 and all(scenario["split"] == "train" for scenario in manifest["scenarios"]), "Train membership")
    _require(tuple(lock["probe_genomes"]) == PROBE_IDS, "P00-P09 lock identities")
    _require(lock["seed"] == 711 and lock["planned_episodes"] == 960 and lock["no_cache"], "Probe execution lock")
    _require(lock["status"] == "LOCKED_BEFORE_ROLLOUT" and bool(lock["created_utc"]), "pre-rollout execution lock")

    episodes_hash, episodes_bytes = _file_digest(episodes_path)
    lock_hash, _ = _file_digest(lock_path)
    counts: Counter = Counter()
    legal = {probe: True for probe in PROBE_IDS}
    hard: Counter = Counter()
    anchors: Dict[Tuple[str, str], Dict[str, Any]] = {}
    seen_pairs = set()
    episode_references = set()
    attempt_ids = set()
    per_probe_scenarios = {probe: set() for probe in PROBE_IDS}
    anchor_ids = set(ANCHORS.values())
    with episodes_path.open(encoding="utf-8") as source:
        for ordinal, line in enumerate(source):
            row = json.loads(line)
            _require(row["episode_ordinal"] == ordinal, f"episode ordinal {ordinal}")
            probe = row["probe_id"]
            scenario_id = row["scenario_id"]
            pair = (probe, scenario_id)
            _require(pair not in seen_pairs, f"duplicate probe/scenario {pair}")
            seen_pairs.add(pair)
            errors = audit_episode_row(row, lock, train_ids)
            _require(not errors, f"episode {ordinal}: {','.join(errors)}")
            episode = row["report"]["episode_reference"]
            _require(episode not in episode_references, f"duplicate episode reference {ordinal}")
            episode_references.add(episode)
            for record in row["report"]["attempt_records"]:
                attempt_id = record["compensation_attempt_id"]
                _require(attempt_id not in attempt_ids, f"duplicate attempt ID {ordinal}")
                attempt_ids.add(attempt_id)
            counts[probe] += 1
            per_probe_scenarios[probe].add(scenario_id)
            legal[probe] = legal[probe] and row["report"]["illegal_state_transition_count"] == 0
            for field in HARD_FIELDS:
                hard[field] += row["report"][field]
            if scenario_id in anchor_ids:
                anchors[pair] = row
    _require(ordinal == 959 and len(seen_pairs) == 960, "960 episode rows")
    _require(all(counts[probe] == 96 and per_probe_scenarios[probe] == train_ids for probe in PROBE_IDS), "complete 10x96 panel")
    expected_anchors = {(probe, scenario) for probe in PROBE_IDS for scenario in anchor_ids}
    _require(set(anchors) == expected_anchors, "probe anchor completeness")

    criteria = _recompute_criteria(lock, anchors, counts, legal)
    computed_hard = {field: hard[field] for field in HARD_FIELDS}
    summary_matches = (
        summary["protocol"] == lock["protocol"] == "D092-R2.3"
        and summary["seed"] == lock["seed"] == 711
        and summary["episode_count"] == summary["expected_episode_count"] == 960
        and summary["cache_hits"] == 0
        and summary["execution_lock_sha256"] == lock_hash
        and summary["execution_lock_created_utc"] == lock["created_utc"]
        and summary["runtime"] == lock["runtime"]
        and summary["criteria"] == criteria
        and summary["hard_constraints"] == computed_hard
        and summary["compensation_attempts"] == len(attempt_ids)
        and summary["episodes_jsonl_sha256"] == episodes_hash
        and summary["episodes_jsonl_bytes"] == episodes_bytes
        and summary["overall_pass"] == (summary["status"] == "PASS")
        and summary["status"] == ("PASS" if all(item["status"] == "PASS" for item in criteria.values()) else "HOLD")
        and isinstance(summary["elapsed_seconds"], (int, float)) and summary["elapsed_seconds"] >= 0
    )
    _require(summary_matches, "summary does not match raw ledger")
    probe_status = "PASS" if all(item["status"] == "PASS" for item in criteria.values()) else "HOLD"
    return {
        "audit_schema": "d092_probe_independent_audit_v1",
        "status": "PASS",
        "probe_status": probe_status,
        "overall_pass": probe_status == "PASS",
        "protocol": "D092-R2.3",
        "seed": 711,
        "episode_count": len(seen_pairs),
        "unique_episode_references": len(episode_references),
        "unique_compensation_attempt_ids": len(attempt_ids),
        "cache_hits": 0,
        "no_cache_locked": lock["no_cache"],
        "train_scenarios_per_probe": 96,
        "validation_test_rows": 0,
        "episodes_jsonl_sha256": episodes_hash,
        "episodes_jsonl_bytes": episodes_bytes,
        "execution_lock_sha256": lock_hash,
        "execution_lock_source_head": lock["source_head"],
        "summary_matches_raw": summary_matches,
        "criteria": criteria,
        "hard_constraints": computed_hard,
        "q3_harm_priority_diagnostic": _q3_diagnostic(lock, anchors),
        "scientific_claim": "Artifact integrity and mechanism identifiability only; no algorithm performance claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=RESULTS)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = audit_probe(args.outdir)
    output = args.output or args.outdir / "independent_audit.json"
    output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit": result["status"], "probe": result["probe_status"], "episodes": result["episode_count"], "output": str(output)}))


if __name__ == "__main__":
    main()
