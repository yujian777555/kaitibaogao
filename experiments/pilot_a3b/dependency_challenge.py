"""D-086 dependency/reliability challenge generation and fail-closed locks."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from dependency_recovery import classify_scenario
from d079_challenge_generator import stable_seed

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "results" / "d086_dependency_challenge" / "dependency_manifest.json"
LOCK_PATH = HERE / "dependency_manifest_lock.json"
GENERATOR_VERSION = "d086-dependency-recovery-v1"
SEED_BASE = 2026112100
REPEATS = 3
STRATA = (
    "D1_RECOVERABLE_TIMEOUT",
    "D2_PARTIAL_THEN_REDO",
    "D3_DEPENDENT_ABORT",
    "D4_BLOCKED_COMPENSATION",
)
EXPECTED_LABELS = dict(zip(STRATA, ("R1", "R2", "R3", "R4")))
FAMILY_SPECS = {
    "df01": {"graph": "B_REQUIRES_A", "primary_cost": 3, "alternate_cost": 1, "alt_pattern": [True], "block": "B", "delayed": True},
    "df02": {"graph": "A_REQUIRES_B", "primary_cost": 2, "alternate_cost": 1, "alt_pattern": [False, True], "block": "B", "delayed": False, "r4_closure": True},
    "df03": {"graph": "PARALLEL", "primary_cost": 3, "alternate_cost": 1, "alt_pattern": [True], "block": "A", "delayed": True},
    "df04": {"graph": "ALT_FALLBACK", "primary_cost": 4, "alternate_cost": 1, "alt_pattern": [True], "block": "B", "delayed": False},
    "df05": {"graph": "B_REQUIRES_A", "primary_cost": 1, "alternate_cost": 4, "alt_pattern": [False, True], "block": "A", "delayed": False},
    "df06": {"graph": "A_REQUIRES_B", "primary_cost": 3, "alternate_cost": 2, "alt_pattern": [True], "block": "B", "delayed": True},
    "df07": {"graph": "LONG_CHAIN", "primary_cost": 3, "alternate_cost": 1, "alt_pattern": [True], "block": "C", "delayed": True},
    "df08": {"graph": "CROSS_ALTERNATE", "primary_cost": 4, "alternate_cost": 1, "alt_pattern": [True], "block": "B", "delayed": False},
}
ALLOCATION = {
    "train": ["df01", "df02", "df03", "df04", "df05", "df06"],
    "validation": ["df07", "df08"],
}
TEST_PROTOCOL = {
    "split": "test",
    "seed_base": 2026120100,
    "family_count": 40,
    "repeats_per_stratum": 5,
    "scenario_count": 800,
    "strata": list(STRATA),
    "scenario_id_namespace": "d086|test|",
    "family_roster": "OPEN_INDEPENDENT_CUSTODIAN_COMMITMENT_REQUIRED",
    "status": "SEALED_NOT_GENERATED_OR_READ",
}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(value):
    return hashlib.sha256(_canonical(value)).hexdigest()


def _source_sha256():
    text = Path(__file__).read_text(encoding="utf-8")
    return hashlib.sha256("\n".join(text.splitlines()).encode("utf-8")).hexdigest()


def _requires(graph, tool_id, alternate):
    if alternate or graph == "PARALLEL":
        return []
    if graph == "B_REQUIRES_A":
        return ["A"] if tool_id == "B" else []
    if graph == "A_REQUIRES_B":
        return ["B"] if tool_id == "A" else []
    if graph == "ALT_FALLBACK":
        return ["B"] if tool_id == "A" else []
    if graph == "LONG_CHAIN":
        return {"A": ["B"], "B": ["C"]}.get(tool_id, [])
    if graph == "CROSS_ALTERNATE":
        return {"A": ["B"], "B": ["A"]}.get(tool_id, [])
    raise ValueError("unknown dependency graph: " + str(graph))


def _route(family, tool_id, alternate, repeat, delayed):
    spec = FAMILY_SPECS[family]
    primary_pattern = ([True], [False, True], [False, False, True])[repeat]
    outcomes = spec["alt_pattern"] if alternate else primary_pattern
    is_delayed = delayed and (
        (repeat == 1 and tool_id == "A" and not alternate)
        or (repeat == 2 and spec["delayed"] and alternate)
    )
    return {
        "name": "alternate" if alternate else "primary",
        "outcomes": list(outcomes),
        "cost": spec["alternate_cost"] if alternate else spec["primary_cost"],
        "reliability_hint": "LOW" if alternate else "HIGH",
        "requires": _requires(spec["graph"], tool_id, alternate),
        "receipt": "delayed" if is_delayed else "immediate",
        "receipt_delay": (1 + repeat) if is_delayed else 0,
        "idempotent": not is_delayed,
        "visibility_bound": 3,
    }


def _control_tool(tool_id):
    return {
        "id": tool_id,
        "state": "COMMITTED",
        "compensation_available": True,
        "routes": [_route("df01", tool_id, False, 0, False), _route("df01", tool_id, True, 0, False)],
    }


def make_scenario(split, family, stratum, repeat, seed_base=SEED_BASE):
    if split not in ALLOCATION or family not in ALLOCATION[split]:
        raise ValueError("family is not assigned to this development split")
    if stratum not in STRATA or repeat not in range(REPEATS):
        raise ValueError("invalid stratum or repeat")
    spec = FAMILY_SPECS[family]
    graph = spec["graph"]
    prefix = ["A", "B", "C"] if graph == "LONG_CHAIN" else ["A", "B"]
    current = "D" if graph == "LONG_CHAIN" else "C"
    terminal = {
        "D1_RECOVERABLE_TIMEOUT": "timeout_before",
        "D2_PARTIAL_THEN_REDO": "partial_recover",
    }.get(stratum, "permission")
    tools = []
    for tool_id in prefix:
        state = "COMMITTED"
        if stratum == "D1_RECOVERABLE_TIMEOUT" and tool_id == current:
            state = "NOT_COMMITTED"
        if stratum == "D2_PARTIAL_THEN_REDO" and tool_id == current:
            state = "PARTIAL"
        if stratum in ("D1_RECOVERABLE_TIMEOUT", "D2_PARTIAL_THEN_REDO") and tool_id != current:
            tool = _control_tool(tool_id)
        else:
            tool = {
                "id": tool_id,
                "state": state,
                "compensation_available": not (
                    stratum == "D4_BLOCKED_COMPENSATION" and tool_id == spec["block"]
                ),
                "routes": [
                    _route(family, tool_id, False, repeat, stratum != "D4_BLOCKED_COMPENSATION"),
                    _route(family, tool_id, True, repeat, stratum != "D4_BLOCKED_COMPENSATION"),
                ],
            }
        tools.append(tool)
    tools.append({
        "id": current,
        "state": "NOT_COMMITTED" if stratum != "D2_PARTIAL_THEN_REDO" else "PARTIAL",
        "compensation_available": True,
        "routes": [
            _route(family, current, False, 0, False),
            _route(family, current, True, 0, False),
        ],
    })
    if stratum == "D4_BLOCKED_COMPENSATION" and spec.get("r4_closure"):
        blocked = spec["block"]
        for tool in tools:
            if tool["id"] != blocked and tool["state"] == "COMMITTED":
                for route in tool["routes"]:
                    route["requires"] = [blocked]
    label, minimum = classify_scenario({"terminal_fault": terminal, "tools": tools})
    if label != EXPECTED_LABELS[stratum]:
        raise RuntimeError("D-086 scenario label mismatch: " + family + "/" + stratum)
    scenario = {
        "scenario_id": f"d086|{split}|{family}|{stratum}|r{repeat}",
        "cluster_id": family + "|" + stratum,
        "task_family_id": family,
        "split": split,
        "evaluation_role": "search" if split == "train" else "validation_selection",
        "difficulty_stratum": stratum,
        "composition": graph,
        "repeat": repeat,
        "seed": stable_seed(seed_base, split, family, stratum, repeat),
        "terminal_fault": terminal,
        "current_tool": current,
        "tools": tools,
    }
    scenario.update({
        "label": label,
        "min_reachable_harm": minimum,
        "labeler": "d086-contract-and-schedule-reachability-v1",
        "label_evidence_sha256": _sha256({
            "label": label,
            "minimum": minimum,
            "tools": tools,
        }),
    })
    return scenario


def build_manifest(seed_base=SEED_BASE):
    scenarios = [
        make_scenario(split, family, stratum, repeat, seed_base=seed_base)
        for split, families in ALLOCATION.items()
        for family in families
        for stratum in STRATA
        for repeat in range(REPEATS)
    ]
    manifest = {
        "protocol_id": "D-086-DEPENDENCY",
        "generator_version": GENERATOR_VERSION,
        "seed_base": seed_base,
        "development_only": True,
        "test_included": False,
        "test_outcomes_read": False,
        "test_protocol": dict(TEST_PROTOCOL),
        "repeats_per_family_stratum": REPEATS,
        "strata": list(STRATA),
        "expected_labels": dict(EXPECTED_LABELS),
        "allocation": {key: list(value) for key, value in ALLOCATION.items()},
        "family_counts": {key: len(value) for key, value in ALLOCATION.items()},
        "scenario_counts": dict(sorted(Counter(row["split"] for row in scenarios).items())),
        "scenario_count": len(scenarios),
        "families": [
            {"family_id": family, **FAMILY_SPECS[family]}
            for family in FAMILY_SPECS
        ],
        "label_counts": {
            split: dict(sorted(Counter(row["label"] for row in scenarios if row["split"] == split).items()))
            for split in ALLOCATION
        },
        "scenarios": scenarios,
    }
    manifest["manifest_sha256"] = _sha256(manifest)
    return manifest


def validate_manifest(manifest):
    problems = []
    scenarios = manifest.get("scenarios", [])
    if manifest.get("development_only") is not True:
        problems.append("development-only declaration missing")
    if manifest.get("test_included") is not False or manifest.get("test_outcomes_read") is not False:
        problems.append("Test isolation declaration failed")
    if manifest.get("test_protocol") != TEST_PROTOCOL:
        problems.append("sealed Test protocol changed")
    if manifest.get("scenario_count") != 96 or len(scenarios) != 96:
        problems.append("expected 96 scenarios")
    if manifest.get("scenario_counts") != {"train": 72, "validation": 24}:
        problems.append("expected 72 Train / 24 Validation")
    if manifest.get("family_counts") != {"train": 6, "validation": 2}:
        problems.append("expected six Train / two Validation families")
    if manifest.get("allocation") != ALLOCATION:
        problems.append("family allocation changed")
    if len({row.get("scenario_id") for row in scenarios}) != 96:
        problems.append("scenario IDs are not unique")
    for split, families in ALLOCATION.items():
        for family in families:
            for stratum in STRATA:
                for repeat in range(REPEATS):
                    expected = make_scenario(
                        split, family, stratum, repeat,
                        seed_base=manifest.get("seed_base", SEED_BASE),
                    )
                    actual = next((row for row in scenarios if row.get("scenario_id") == expected["scenario_id"]), None)
                    if actual != expected:
                        problems.append("scenario content mismatch: " + expected["scenario_id"])
    expected_hash = _sha256({key: value for key, value in manifest.items() if key != "manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_hash:
        problems.append("manifest canonical SHA-256 mismatch")
    return {"ok": not problems, "problems": sorted(set(problems))}


def make_lock(manifest):
    return {
        "lock_schema_version": 1,
        "protocol_id": "D-086-DEPENDENCY",
        "generator_version": manifest["generator_version"],
        "generator_source_sha256": _source_sha256(),
        "manifest_sha256": manifest["manifest_sha256"],
        "seed_base": manifest["seed_base"],
        "scenario_count": manifest["scenario_count"],
        "scenario_counts": manifest["scenario_counts"],
        "family_counts": manifest["family_counts"],
        "allocation": manifest["allocation"],
        "strata": manifest["strata"],
        "development_only": True,
        "test_included": False,
        "test_outcomes_read": False,
        "test_protocol": manifest["test_protocol"],
        "lock_status": "FROZEN_DEVELOPMENT_MANIFEST_NOT_EXECUTION_AUTHORIZATION",
    }


def validate_lock(manifest, lock_path=LOCK_PATH):
    path = Path(lock_path)
    if not path.is_file():
        return {"ok": False, "problems": ["D-086 manifest lock missing"]}
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "problems": ["cannot read D-086 lock: " + str(exc)]}
    expected = make_lock(manifest)
    problems = ["lock mismatch: " + key for key in expected if lock.get(key) != expected[key]]
    return {"ok": not problems, "problems": problems}


def _write_once(path, value):
    path = Path(path)
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise FileExistsError("refusing to overwrite different frozen artifact: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(MANIFEST_PATH.parent))
    parser.add_argument("--lock-path", default=str(LOCK_PATH))
    args = parser.parse_args()
    manifest = build_manifest()
    gate = validate_manifest(manifest)
    if not gate["ok"]:
        raise RuntimeError("; ".join(gate["problems"]))
    _write_once(Path(args.outdir) / MANIFEST_PATH.name, manifest)
    lock = make_lock(manifest)
    _write_once(args.lock_path, lock)
    lock_gate = validate_lock(manifest, args.lock_path)
    if not lock_gate["ok"]:
        raise RuntimeError("; ".join(lock_gate["problems"]))
    print(json.dumps({
        "status": "D086_DEVELOPMENT_MANIFEST_LOCKED_NOT_EXECUTION_AUTHORIZATION",
        "manifest_sha256": manifest["manifest_sha256"],
        "scenario_counts": manifest["scenario_counts"],
        "label_counts": manifest["label_counts"],
        "test_outcomes_read": False,
        "optimizer_runs": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
