"""D-089 new Train-only scenario generator.

Namespace ``d089r|train|`` (development) and ``d089r|train2|`` (fresh
replication).  Families stress R3/R4 budget competition directly:
delayed failing compensations, mixed receipt delays, alternate paths,
blocked contracts, deeper dependency chains, and budget-scarcity repeats.

Only public route metadata is stored in the manifest; hidden outcomes are
part of the deterministic route definition used by the shared environment.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))

from dependency_recovery import classify_scenario  # noqa: E402

STRATA = (
    "D1_RECOVERABLE_TIMEOUT",
    "D2_PARTIAL_THEN_REDO",
    "D3_DEPENDENT_ABORT",
    "D4_BLOCKED_COMPENSATION",
)
EXPECTED_LABELS = dict(zip(STRATA, ("R1", "R2", "R3", "R4")))
REPEATS = 4

DEV_FAMILIES = {
    # slow alternates + fast primaries behind a chain: budget race
    "g01_CHAIN_RACE": {
        "requires": {"A": ["B"], "B": ["C"], "C": []},
        "primary_cost": 4, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 1, 1, 2],
        "alternate_delay": [2, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[True], [False, True], [False, True], [False, False, True]],
    },
    # fork with one fragile branch
    "g02_FORK_FRAGILE": {
        "requires": {"A": ["B", "C"], "B": [], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "C",
        "primary_delay": [0, 1, 2, 1],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [True], [False, True], [False, False, True]],
    },
    # mutual pair, cheap fragile alternates (R3/R4 competition)
    "g03_PAIR_RACE": {
        "requires": {"A": ["B"], "B": ["A"], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 1, 1, 2],
        "alternate_delay": [2, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[False, True], [False, True], [False, False, True], [False, False, True]],
    },
    # hub with heavy delayed failures on the hub itself
    "g04_HUB_SLOW": {
        "requires": {"A": ["C"], "B": ["C"], "C": []},
        "primary_cost": 5, "alternate_cost": 2, "block": "C",
        "primary_delay": [1, 2, 2, 2],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [False, True], [False, False, True]],
    },
    # independent trio with staggered delays (batch dispatch opportunity)
    "g05_TRIO_STAGGER": {
        "requires": {"A": [], "B": [], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "A",
        "primary_delay": [1, 1, 2, 2],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[True], [False, True], [True], [False, True]],
    },
    # deep chain 3-level with cost pressure (budget scarce repeats)
    "g06_DEEP_PRESSURE": {
        "requires": {"A": ["B"], "B": ["C"], "C": []},
        "primary_cost": 2, "alternate_cost": 1, "block": "C",
        "primary_delay": [1, 2, 2, 2],
        "alternate_delay": [2, 2, 2, 2],
        "primary_patterns": [[True], [False, True], [False, True], [True]],
        "alternate_patterns": [[False, True], [False, True], [False, False, True], [False, False, True]],
    },
}

FRESH_FAMILIES = {
    "h01_LADDER": {
        "requires": {"A": ["B"], "B": ["C"], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 2, 1, 2],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, False, True]],
    },
    "h02_SPLIT_JOIN": {
        "requires": {"A": ["B", "C"], "B": [], "C": []},
        "primary_cost": 4, "alternate_cost": 1, "block": "B",
        "primary_delay": [1, 1, 2, 2],
        "alternate_delay": [2, 2, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[False, True], [True], [False, True], [False, False, True]],
    },
    "h03_LOOP_BREAK": {
        "requires": {"A": ["C"], "B": ["A"], "C": ["B"]},
        "primary_cost": 3, "alternate_cost": 1, "block": "A",
        "primary_delay": [1, 1, 2, 2],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[True], [False, True], [True], [False, False, True]],
    },
    "h04_SLOW_FANOUT": {
        "requires": {"A": ["C"], "B": ["C"], "C": []},
        "primary_cost": 4, "alternate_cost": 2, "block": "C",
        "primary_delay": [2, 2, 2, 2],
        "alternate_delay": [1, 1, 2, 2],
        "primary_patterns": [[True], [True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [False, True], [True]],
    },
}


def _route(spec, tool_id, alternate, repeat):
    patterns = spec["alternate_patterns"] if alternate else spec["primary_patterns"]
    delays = spec["alternate_delay"] if alternate else spec["primary_delay"]
    outcomes = patterns[min(repeat, len(patterns) - 1)]
    delay = delays[min(repeat, len(delays) - 1)]
    return {
        "name": "alternate" if alternate else "primary",
        "outcomes": list(outcomes),
        "cost": spec["alternate_cost"] if alternate else spec["primary_cost"],
        "reliability_hint": "LOW" if alternate else "HIGH",
        "requires": [] if alternate else list(spec["requires"].get(tool_id, [])),
        "receipt": "delayed" if delay else "immediate",
        "receipt_delay": delay,
        "idempotent": delay == 0,
        "visibility_bound": 3,
    }


def make_scenario(family, stratum, repeat, tier="development"):
    specs = DEV_FAMILIES if tier != "fresh" else FRESH_FAMILIES
    if family not in specs or stratum not in STRATA or repeat not in range(REPEATS):
        raise ValueError("invalid D-089 family/stratum/repeat")
    spec = specs[family]
    terminal = {
        "D1_RECOVERABLE_TIMEOUT": "timeout_before",
        "D2_PARTIAL_THEN_REDO": "partial_recover",
    }.get(stratum, "permission")
    tools = []
    for tool_id in ("A", "B", "C"):
        tools.append({
            "id": tool_id,
            "state": "COMMITTED",
            "compensation_available": not (
                stratum == "D4_BLOCKED_COMPENSATION" and tool_id == spec["block"]
            ),
            "routes": [_route(spec, tool_id, False, repeat), _route(spec, tool_id, True, repeat)],
        })
    tools.append({
        "id": "D",
        "state": "PARTIAL" if stratum == "D2_PARTIAL_THEN_REDO" else "NOT_COMMITTED",
        "compensation_available": True,
        "routes": [_route(spec, "D", False, 0), _route(spec, "D", True, 0)],
    })
    label, minimum = classify_scenario({"terminal_fault": terminal, "tools": tools})
    if label != EXPECTED_LABELS[stratum]:
        raise RuntimeError(f"D-089 label mismatch: {family}/{stratum}: {label}")
    ns = "d089r|train" + ("" if tier != "fresh" else "2")
    return {
        "scenario_id": f"{ns}|{family}|{stratum}|r{repeat}",
        "cluster_id": f"{family}|{stratum}",
        "task_family_id": family,
        "split": "train",
        "evaluation_role": ("d089_train_development" if tier != "fresh"
                            else "d089_frozen_replication"),
        "tier": tier,
        "difficulty_stratum": stratum,
        "composition": family,
        "repeat": repeat,
        "terminal_fault": terminal,
        "current_tool": "D",
        "tools": tools,
        "label": label,
        "min_reachable_harm": minimum,
        "labeler": "d089-train-reachability-v1",
    }


def build_manifest(tier="development"):
    specs = DEV_FAMILIES if tier != "fresh" else FRESH_FAMILIES
    scenarios = [make_scenario(f, s, r, tier=tier)
                 for f in specs for s in STRATA for r in range(REPEATS)]
    manifest = {
        "protocol_id": ("D-089-TRAIN-DEVELOPMENT" if tier != "fresh"
                        else "D-089-FROZEN-REPLICATION"),
        "generator_version": "d089-train-v1",
        "tier": tier,
        "split": "train",
        "test_included": False,
        "test_outcomes_read": False,
        "family_count": len(specs),
        "scenario_count": len(scenarios),
        "scenario_ids": [s["scenario_id"] for s in scenarios],
        "scenarios": scenarios,
    }
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    manifest["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return manifest


def validate_manifest(manifest):
    ids = [s["scenario_id"] for s in manifest["scenarios"]]
    if len(ids) != len(set(ids)):
        return {"ok": False, "reason": "duplicate ids"}
    if any(not s["scenario_id"].startswith("d089r|train") for s in manifest["scenarios"]):
        return {"ok": False, "reason": "namespace"}
    if manifest.get("test_included") is not False:
        return {"ok": False, "reason": "test access"}
    return {"ok": True, "scenario_count": len(ids)}


if __name__ == "__main__":
    for tier in ("development", "fresh"):
        m = build_manifest(tier=tier)
        print(tier, m["scenario_count"], m["manifest_sha256"][:16], validate_manifest(m))
        out = _HERE / "results"
        out.mkdir(exist_ok=True)
        name = "d089_train_manifest.json" if tier != "fresh" else "d089_fresh_manifest.json"
        (out / name).write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
