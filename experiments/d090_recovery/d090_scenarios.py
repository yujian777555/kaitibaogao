"""D-090 Train-only families with new scenario IDs."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))
from dependency_recovery import classify_scenario  # noqa: E402

STRATA = ("D1_RECOVERABLE_TIMEOUT", "D2_PARTIAL_THEN_REDO", "D3_DEPENDENT_ABORT", "D4_BLOCKED_COMPENSATION")
EXPECTED = dict(zip(STRATA, ("R1", "R2", "R3", "R4")))
REPEATS = 4

FAMILIES = {
    "d090_PAIR_RACE": {"requires": {"A": ["B"], "B": ["A"], "C": []}, "block": "B", "pc": 3, "ac": 1,
                       "pd": [0, 1, 1, 2], "ad": [2, 2, 2, 2],
                       "po": [[True], [True], [False, True], [True]],
                       "ao": [[False, True], [False, True], [False, False, True], [False, False, True]]},
    "d090_FORK_JOIN": {"requires": {"A": ["B", "C"], "B": [], "C": []}, "block": "C", "pc": 4, "ac": 1,
                       "pd": [0, 1, 2, 2], "ad": [1, 2, 2, 2],
                       "po": [[True], [False, True], [True], [False, True]],
                       "ao": [[True], [False, True], [False, True], [False, False, True]]},
    "d090_FANOUT_DELAY": {"requires": {"A": ["C"], "B": ["C"], "C": []}, "block": "C", "pc": 4, "ac": 2,
                          "pd": [1, 2, 2, 2], "ad": [1, 2, 2, 2],
                          "po": [[True], [False, True], [True], [False, True]],
                          "ao": [[True], [False, True], [False, True], [False, False, True]]},
    "d090_DEEP_CHAIN": {"requires": {"A": ["B"], "B": ["C"], "C": []}, "block": "B", "pc": 3, "ac": 1,
                        "pd": [1, 2, 2, 2], "ad": [2, 2, 2, 2],
                        "po": [[True], [False, True], [False, True], [True]],
                        "ao": [[True], [False, True], [False, False, True], [False, False, True]]},
    "d090_MULTI_ROUTE": {"requires": {"A": ["C"], "B": ["C"], "C": ["A"]}, "block": "C", "pc": 3, "ac": 1,
                         "pd": [0, 1, 2, 2], "ad": [1, 2, 2, 2],
                         "po": [[True], [False, True], [True], [False, True]],
                         "ao": [[True], [False, True], [False, True], [False, False, True]]},
    "d090_RESIDUAL_HARM": {"requires": {"A": [], "B": [], "C": []}, "block": "A", "pc": 3, "ac": 1,
                           "pd": [1, 1, 2, 2], "ad": [1, 2, 2, 2],
                           "po": [[True], [True], [False, True], [True]],
                           "ao": [[True], [False, True], [True], [False, True]]},
}


def _route(spec, tool, alternate, repeat):
    delay = (spec["ad"] if alternate else spec["pd"])[repeat]
    outcomes = (spec["ao"] if alternate else spec["po"])[repeat]
    return {"name": "alternate" if alternate else "primary", "outcomes": list(outcomes),
            "cost": spec["ac"] if alternate else spec["pc"],
            "reliability_hint": "LOW" if alternate else "HIGH",
            "requires": [] if alternate else list(spec["requires"].get(tool, [])),
            "receipt": "delayed" if delay else "immediate", "receipt_delay": delay,
            "idempotent": delay == 0, "visibility_bound": 3}


def make_scenario(family, stratum, repeat):
    spec = FAMILIES[family]
    terminal = "timeout_before" if stratum == "D1_RECOVERABLE_TIMEOUT" else "partial_recover" if stratum == "D2_PARTIAL_THEN_REDO" else "permission"
    tools = []
    for tool in ("A", "B", "C"):
        tools.append({"id": tool, "state": "COMMITTED",
                      "compensation_available": not (stratum == "D4_BLOCKED_COMPENSATION" and tool == spec["block"]),
                      "routes": [_route(spec, tool, False, repeat), _route(spec, tool, True, repeat)]})
    tools.append({"id": "D", "state": "PARTIAL" if stratum == "D2_PARTIAL_THEN_REDO" else "NOT_COMMITTED",
                  "compensation_available": True, "routes": [_route(spec, "D", False, 0), _route(spec, "D", True, 0)]})
    label, minimum = classify_scenario({"terminal_fault": terminal, "tools": tools})
    if label != EXPECTED[stratum]:
        raise ValueError(f"label mismatch {family}/{stratum}: {label}")
    return {"scenario_id": f"d090r|train|{family}|{stratum}|r{repeat}", "cluster_id": f"{family}|{stratum}",
            "task_family_id": family, "split": "train", "evaluation_role": "d090_mechanism_search",
            "difficulty_stratum": stratum, "composition": family, "repeat": repeat, "terminal_fault": terminal,
            "current_tool": "D", "tools": tools, "label": label, "min_reachable_harm": minimum,
            "labeler": "d090-train-reachability-v1"}


def build_manifest():
    scenarios = [make_scenario(f, s, r) for f in FAMILIES for s in STRATA for r in range(REPEATS)]
    manifest = {"protocol_id": "D-090-TRAIN-MECHANISM", "generator_version": "d090-train-v1",
                "split": "train", "test_included": False, "test_outcomes_read": False,
                "family_count": len(FAMILIES), "scenario_count": len(scenarios),
                "label_counts": {label: sum(x["label"] == label for x in scenarios) for label in EXPECTED.values()},
                "families": sorted(FAMILIES), "scenarios": scenarios, "decision_cap_per_episode": 24}
    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    manifest["manifest_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    return manifest
