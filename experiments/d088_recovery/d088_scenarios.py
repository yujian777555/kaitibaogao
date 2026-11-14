"""D-088 new Train-only scenario generator.

Families use namespace ``d088r|train|`` and do not overlap D-086/D-087
scenario ids.  Coverage targets: delayed receipts, failed compensation,
alternate paths, compensation dependencies, unknown commit states,
multi-tool interaction, decision-budget exhaustion risk.

Only ``split="train"`` scenarios are produced (the D-086 environment accepts
train/validation only).  No Test access, no hidden-outcome leakage: policies
read the public view produced by DependencyRecoveryEnv.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sys
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

# Each family: requires graph, costs, per-repeat delay/pattern schedules.
# primary_patterns[r] / alternate_patterns[r] are deterministic attempt outcomes.
FAMILIES = {
    # like rv02 but reversed dependency direction and cost structure
    "t01_CHAIN_REVERSE": {
        "requires": {"A": ["B"], "B": ["C"], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 0, 1, 0],
        "alternate_delay": [0, 1, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, False, True]],
    },
    # diamond: A <- {B,C} <- D-like interactions via requires
    "t02_DIAMOND": {
        "requires": {"A": ["B", "C"], "B": [], "C": []},
        "primary_cost": 4, "alternate_cost": 1, "block": "C",
        "primary_delay": [0, 1, 0, 1],
        "alternate_delay": [0, 0, 1, 2],
        "primary_patterns": [[True], [True], [False, True], [False, True]],
        "alternate_patterns": [[True], [True], [False, True], [False, False, True]],
    },
    # mutual cycle A <-> B, C independent (cycle breaking needed)
    "t03_CYCLE_PAIR": {
        "requires": {"A": ["B"], "B": ["A"], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 0, 1, 1],
        "alternate_delay": [1, 1, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, False, True]],
    },
    # long chain A <- B <- C with heavy alternate failures
    "t04_DEEP_CHAIN": {
        "requires": {"A": ["B"], "B": ["C"], "C": []},
        "primary_cost": 5, "alternate_cost": 1, "block": "C",
        "primary_delay": [0, 1, 1, 2],
        "alternate_delay": [0, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[True], [False, True], [False, True], [False, False, True]],
    },
    # star hub: everything depends on C
    "t05_STAR_HUB": {
        "requires": {"A": ["C"], "B": ["C"], "C": []},
        "primary_cost": 3, "alternate_cost": 2, "block": "C",
        "primary_delay": [0, 0, 1, 1],
        "alternate_delay": [1, 1, 1, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, True]],
    },
    # independent parallel tools with mixed delays (batch dispatch opportunity)
    "t06_PARALLEL_MIX": {
        "requires": {"A": [], "B": [], "C": []},
        "primary_cost": 4, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 1, 0, 1],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [False, True]],
        "alternate_patterns": [[True], [False, True], [False, True], [False, False, True]],
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


# ---------------------------------------------------------------------------
# Fresh tier: unseen families for frozen-candidate replication only.
# These ids/families are NEVER used during search or tuning.
# ---------------------------------------------------------------------------
FRESH_FAMILIES = {
    # reversed star: hub depends on leaves
    "f01_INV_STAR": {
        "requires": {"A": ["B", "C"], "B": [], "C": []},
        "primary_cost": 3, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 1, 0, 2],
        "alternate_delay": [1, 2, 1, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [False, True], [False, False, True]],
    },
    # three-tool chain with delayed hub
    "f02_SLOW_HUB": {
        "requires": {"A": ["C"], "B": ["C"], "C": []},
        "primary_cost": 4, "alternate_cost": 2, "block": "C",
        "primary_delay": [0, 1, 2, 1],
        "alternate_delay": [1, 1, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, True]],
    },
    # pair with one-way dependency and cheap-but-fragile alternates
    "f03_FRAGILE_ALT": {
        "requires": {"A": ["B"], "B": [], "C": []},
        "primary_cost": 2, "alternate_cost": 1, "block": "B",
        "primary_delay": [0, 0, 1, 1],
        "alternate_delay": [2, 2, 2, 2],
        "primary_patterns": [[True], [False, True], [True], [False, True]],
        "alternate_patterns": [[False, True], [False, True], [False, False, True], [False, False, True]],
    },
    # full triangle cycle
    "f04_TRI_CYCLE": {
        "requires": {"A": ["C"], "B": ["A"], "C": ["B"]},
        "primary_cost": 3, "alternate_cost": 1, "block": "A",
        "primary_delay": [1, 1, 1, 2],
        "alternate_delay": [1, 2, 2, 2],
        "primary_patterns": [[True], [True], [False, True], [True]],
        "alternate_patterns": [[True], [False, True], [True], [False, False, True]],
    },
    # independent tools with heavy primary delays
    "f05_HEAVY_DELAY": {
        "requires": {"A": [], "B": [], "C": []},
        "primary_cost": 5, "alternate_cost": 1, "block": "C",
        "primary_delay": [1, 2, 2, 2],
        "alternate_delay": [1, 1, 2, 2],
        "primary_patterns": [[True], [True], [True], [False, True]],
        "alternate_patterns": [[True], [False, True], [True], [False, True]],
    },
}


def make_scenario(family, stratum, repeat, tier="development"):
    specs = FAMILIES if tier != "fresh" else FRESH_FAMILIES
    if family not in specs or stratum not in STRATA or repeat not in range(REPEATS):
        raise ValueError("invalid D-088 train family/stratum/repeat")
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
        raise RuntimeError(f"D-088 label mismatch: {family}/{stratum}: {label}")
    scenario_id = f"d088r|train{'' if tier != 'fresh' else '2'}|{family}|{stratum}|r{repeat}"
    return {
        "scenario_id": scenario_id,
        "cluster_id": f"{family}|{stratum}",
        "task_family_id": family,
        "split": "train",
        "evaluation_role": ("d088_train_development" if tier != "fresh"
                            else "d088_frozen_replication"),
        "tier": tier,
        "difficulty_stratum": stratum,
        "composition": family,
        "repeat": repeat,
        "terminal_fault": terminal,
        "current_tool": "D",
        "tools": tools,
        "label": label,
        "min_reachable_harm": minimum,
        "labeler": "d088-train-reachability-v1",
    }


def build_manifest(tier="development"):
    specs = FAMILIES if tier != "fresh" else FRESH_FAMILIES
    scenarios = [
        make_scenario(family, stratum, repeat, tier=tier)
        for family in specs
        for stratum in STRATA
        for repeat in range(REPEATS)
    ]
    manifest = {
        "protocol_id": ("D-088-TRAIN-DEVELOPMENT" if tier != "fresh"
                        else "D-088-FROZEN-REPLICATION"),
        "generator_version": "d088-train-v1",
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
        return {"ok": False, "reason": "duplicate scenario ids"}
    prefix = "d088r|train"
    if any(not s["scenario_id"].startswith(prefix) for s in manifest["scenarios"]):
        return {"ok": False, "reason": "scenario id namespace"}
    if manifest.get("test_included") is not False or manifest.get("test_outcomes_read") is not False:
        return {"ok": False, "reason": "test access flag"}
    if any(s["split"] != "train" for s in manifest["scenarios"]):
        return {"ok": False, "reason": "non-train split"}
    return {"ok": True, "scenario_count": len(ids)}


if __name__ == "__main__":
    m = build_manifest()
    out = _HERE / "results"
    out.mkdir(exist_ok=True)
    path = out / "d088_train_manifest.json"
    path.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("scenarios:", m["scenario_count"], "sha:", m["manifest_sha256"])
    print("validate:", validate_manifest(m))
