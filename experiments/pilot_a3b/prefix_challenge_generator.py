"""D-085 development-only Prefix-aware challenge manifest and lock.

No Validation/Test catalog from the formal benchmark is constructed. The final
Test namespace is reserved metadata, not generated or accessed scenario data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from a3_bridge import scenario_verdict
from a3_verdicts import classify_scenario
from d079_challenge_generator import (
    _assign,
    _base_faults,
    build_train_family_catalog,
    stable_seed,
)
from pilot_a3 import TOOLS

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "results" / "d085_prefix_challenge" / "prefix_challenge_manifest.json"
LOCK_PATH = HERE / "prefix_manifest_lock.json"
GENERATOR_VERSION = "d085-prefix-development-v1"
SEED_BASE = 2026111500
REPEATS = 3
STRATA = (
    "P1_PERMISSION_COMPENSATABLE_PREFIX",
    "P2_PERMISSION_COMPENSATION_UNAVAILABLE",
    "P3_RECOVERABLE_PARTIAL_CONTROL",
    "P4_CLEAR_PRECOMMIT_TIMEOUT_CONTROL",
)
EXPECTED_LABELS = dict(zip(STRATA, ("R3", "R4", "R2", "R1")))
TEST_PROTOCOL = {
    "split": "test",
    "seed_base": 2026111900,
    "family_count": 40,
    "repeats_per_stratum": 5,
    "scenario_count": 800,
    "strata": list(STRATA),
    "scenario_id_namespace": "d085|test|",
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


def _permission_index(tools, pattern_seed):
    import random
    rng = random.Random(pattern_seed)
    candidates = [
        index for index in (1, 2)
        if all(TOOLS[tools[j]]["compensatable"] for j in range(index))
    ]
    if not candidates:
        raise ValueError("no compensatable committed-prefix permission site")
    return rng.choice(candidates)


def make_faults(tools, stratum, pattern_seed, parameter_seed):
    import random
    tools = tuple(tools)
    faults = _base_faults(tools)
    pattern_rng = random.Random(pattern_seed)
    parameter_rng = random.Random(parameter_seed)
    if stratum in STRATA[:2]:
        index = _permission_index(tools, pattern_seed)
        _assign(faults, tools, index, "permission_denied", parameter_rng)
        for prior in range(index):
            faults[prior]["compensation_available"] = stratum == STRATA[0]
    elif stratum == "P3_RECOVERABLE_PARTIAL_CONTROL":
        candidates = [i for i, tool in enumerate(tools) if TOOLS[tool]["compensatable"]]
        index = pattern_rng.choice(candidates)
        _assign(faults, tools, index, "partial_commit", parameter_rng, compensation_available=True)
    elif stratum == "P4_CLEAR_PRECOMMIT_TIMEOUT_CONTROL":
        candidates = [i for i, tool in enumerate(tools) if not TOOLS[tool]["idempotent"]]
        index = pattern_rng.choice(candidates or [0])
        _assign(faults, tools, index, "timeout_before", parameter_rng)
    else:
        raise ValueError("unknown Prefix challenge stratum: " + str(stratum))
    return faults


def build_prefix_manifest(seed_base=SEED_BASE):
    families = build_train_family_catalog()
    ordered = sorted(families, key=lambda family: stable_seed(seed_base, "partition", family["family_id"]))
    allocation = {
        "train": sorted(family["family_id"] for family in ordered[:6]),
        "validation": sorted(family["family_id"] for family in ordered[6:]),
    }
    scenarios = []
    for split, family_ids in allocation.items():
        for family_id in family_ids:
            family = next(item for item in families if item["family_id"] == family_id)
            tools = tuple(family["tools"])
            for stratum in STRATA:
                pattern_seed = stable_seed(seed_base, family_id, stratum, "pattern")
                for repeat in range(REPEATS):
                    seed = stable_seed(seed_base, split, family_id, stratum, repeat)
                    scenario_id = f"d085|{split}|{family_id}|{stratum}|r{repeat}"
                    scenario = {
                        "scenario_id": scenario_id,
                        "cluster_id": family_id + "|" + stratum,
                        "task": family_id,
                        "task_family_id": family_id,
                        "split": split,
                        "evaluation_role": "search" if split == "train" else "validation_selection",
                        "difficulty_stratum": stratum,
                        "composition": stratum,
                        "repeat": repeat,
                        "seed": seed,
                        "tools": list(tools),
                        "faults": make_faults(tools, stratum, pattern_seed, seed),
                    }
                    robust = classify_scenario(scenario)
                    analytic = scenario_verdict(scenario)
                    if robust["class"] != EXPECTED_LABELS[stratum] or analytic["class"] != robust["class"]:
                        raise RuntimeError("Prefix challenge label mismatch: " + scenario_id)
                    scenario.update({
                        "label": robust["class"],
                        "analytic_label": analytic["class"],
                        "labeler": "observation-based-AND-OR-robust-reachability-v1",
                        "label_evidence_sha256": _sha256(robust["evidence"]),
                        "min_reachable_harm": analytic["min_reachable_harm"],
                        "unavoidable_residual": analytic["unavoidable_residual"],
                    })
                    scenarios.append(scenario)
    manifest = {
        "protocol_id": "D-085-PREFIX",
        "generator_version": GENERATOR_VERSION,
        "seed_base": seed_base,
        "development_only": True,
        "test_included": False,
        "test_outcomes_read": False,
        "test_protocol": dict(TEST_PROTOCOL),
        "repeats_per_family_stratum": REPEATS,
        "strata": list(STRATA),
        "expected_labels": dict(EXPECTED_LABELS),
        "allocation": allocation,
        "family_counts": {split: len(ids) for split, ids in allocation.items()},
        "scenario_counts": dict(sorted(Counter(row["split"] for row in scenarios).items())),
        "scenario_count": len(scenarios),
        "families": [
            {"family_id": family["family_id"], "tools": list(family["tools"])}
            for family in families
        ],
        "label_counts": {
            split: dict(sorted(Counter(
                row["label"] for row in scenarios if row["split"] == split
            ).items()))
            for split in allocation
        },
        "scenarios": scenarios,
    }
    manifest["manifest_sha256"] = _sha256(manifest)
    return manifest


def validate_prefix_manifest(manifest):
    problems = []
    scenarios = manifest.get("scenarios", [])
    if manifest.get("development_only") is not True:
        problems.append("development-only declaration missing")
    if manifest.get("test_included") is not False or manifest.get("test_outcomes_read") is not False:
        problems.append("Test isolation declaration failed")
    if manifest.get("test_protocol") != TEST_PROTOCOL:
        problems.append("sealed Test protocol metadata changed")
    if manifest.get("scenario_count") != 96 or len(scenarios) != 96:
        problems.append("expected 96 development scenarios")
    if manifest.get("scenario_counts") != {"train": 72, "validation": 24}:
        problems.append("scenario counts differ from 72 Train / 24 Validation")
    if manifest.get("family_counts") != {"train": 6, "validation": 2}:
        problems.append("family counts differ from six Train / two Validation")
    allocation = manifest.get("allocation", {})
    if set(allocation.get("train", [])) & set(allocation.get("validation", [])):
        problems.append("Train/Validation families overlap")
    if len({row.get("scenario_id") for row in scenarios}) != 96:
        problems.append("scenario IDs are not unique")
    family_tools = {item["family_id"]: tuple(item["tools"]) for item in manifest.get("families", [])}
    for row in scenarios:
        split = row.get("split")
        family_id = row.get("task_family_id")
        stratum = row.get("difficulty_stratum")
        repeat = row.get("repeat")
        if split not in ("train", "validation") or family_id not in allocation.get(split, []):
            problems.append("scenario allocation mismatch: " + str(row.get("scenario_id")))
            continue
        expected_id = f"d085|{split}|{family_id}|{stratum}|r{repeat}"
        pattern_seed = stable_seed(manifest.get("seed_base"), family_id, stratum, "pattern")
        seed = stable_seed(manifest.get("seed_base"), split, family_id, stratum, repeat)
        if row.get("scenario_id") != expected_id or row.get("seed") != seed:
            problems.append("scenario identity or seed mismatch: " + expected_id)
        if tuple(row.get("tools", [])) != family_tools.get(family_id):
            problems.append("scenario tools differ from family registry: " + expected_id)
        elif row.get("faults") != make_faults(row["tools"], stratum, pattern_seed, seed):
            problems.append("fault vector is not reproducible: " + expected_id)
        if row.get("label") != EXPECTED_LABELS.get(stratum) or row.get("analytic_label") != row.get("label"):
            problems.append("unexpected or unapproved label: " + expected_id)
        verdict = scenario_verdict(row)
        if row.get("min_reachable_harm") != verdict["min_reachable_harm"]:
            problems.append("minimum harm mismatch: " + expected_id)
        if row.get("evaluation_role") == "diagnostic":
            problems.append("D-079 diagnostic role reused: " + expected_id)
    expected_hash = _sha256({key: value for key, value in manifest.items() if key != "manifest_sha256"})
    if manifest.get("manifest_sha256") != expected_hash:
        problems.append("manifest canonical SHA-256 mismatch")
    return {"ok": not problems, "problems": sorted(set(problems))}


def make_manifest_lock(manifest):
    return {
        "lock_schema_version": 1,
        "protocol_id": "D-085-PREFIX",
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
        "lock_status": "FROZEN_DEVELOPMENT_MANIFEST_NOT_EXPERIMENT_AUTHORIZATION",
    }


def validate_manifest_lock(manifest, lock_path=LOCK_PATH):
    path = Path(lock_path)
    if not path.is_file():
        return {"ok": False, "problems": ["Prefix manifest lock is missing"]}
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "problems": ["cannot read Prefix manifest lock: " + str(exc)]}
    expected = make_manifest_lock(manifest)
    problems = ["lock mismatch: " + key for key in expected if lock.get(key) != expected[key]]
    return {"ok": not problems, "problems": problems}


def _write_once(path, value):
    path = Path(path)
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") != text:
        raise FileExistsError("refusing to overwrite a different frozen artifact: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(MANIFEST_PATH.parent))
    parser.add_argument("--lock-path", default=str(LOCK_PATH))
    args = parser.parse_args()
    manifest = build_prefix_manifest()
    gate = validate_prefix_manifest(manifest)
    if not gate["ok"]:
        raise RuntimeError("; ".join(gate["problems"]))
    manifest_path = Path(args.outdir) / MANIFEST_PATH.name
    _write_once(manifest_path, manifest)
    lock = make_manifest_lock(manifest)
    _write_once(args.lock_path, lock)
    lock_gate = validate_manifest_lock(manifest, args.lock_path)
    if not lock_gate["ok"]:
        raise RuntimeError("; ".join(lock_gate["problems"]))
    print(json.dumps({
        "status": "D085_DEVELOPMENT_MANIFEST_LOCKED_NOT_EXPERIMENT_AUTHORIZATION",
        "manifest_sha256": manifest["manifest_sha256"],
        "scenario_counts": manifest["scenario_counts"],
        "label_counts": manifest["label_counts"],
        "test_outcomes_read": False,
        "optimizer_runs": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
