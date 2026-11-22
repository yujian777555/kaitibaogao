"""Final paired-difference entry point for the frozen D-094 R4 analysis."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from d094_r4_statistics import preregistered_analysis
from d094_r4_tasks import R4_SEEDS, r4_tasks


HERE = Path(__file__).resolve().parent
COMPARISONS = (
    ("B3_minus_B2", "B2", "B3"),
    ("B4_minus_B2", "B2", "B4"),
    ("B3_minus_B4", "B4", "B3"),
    ("B2_minus_B1", "B1", "B2"),
)
FINAL_UNIT_KEYS = tuple(
    sorted((task.task_id, seed) for task in r4_tasks() for seed in R4_SEEDS)
)


def final_paired_differences(arms: dict[str, Any]) -> dict[str, list[int]]:
    """Construct exactly four ordered final Task Success differences per comparison."""
    if set(arms) != {"B1", "B2", "B3", "B4"}:
        raise ValueError("R4 final analysis requires exactly B1, B2, B3 and B4")
    successes: dict[str, dict[tuple[str, int], int]] = {}
    for arm in ("B1", "B2", "B3", "B4"):
        rows = arms[arm].get("per_task_seed", [])
        keys = [(row.get("task_id"), row.get("seed")) for row in rows]
        if len(rows) != 4 or len(set(keys)) != 4 or tuple(sorted(keys)) != FINAL_UNIT_KEYS:
            raise ValueError(f"R4 final paired units are incomplete or duplicated: {arm}")
        if any(type(row.get("task_success")) is not bool for row in rows):
            raise ValueError(f"R4 final Task Success must be boolean: {arm}")
        successes[arm] = {
            (row["task_id"], row["seed"]): int(row["task_success"]) for row in rows
        }
    return {
        label: [successes[second][key] - successes[first][key] for key in FINAL_UNIT_KEYS]
        for label, first, second in COMPARISONS
    }


def analyze_final_arms(
    summary: dict[str, Any], *, execution_lock_path: Path | None = None
) -> dict[str, Any]:
    """Run the frozen formulas and optionally bind output to exact raw lock bytes."""
    result = preregistered_analysis(final_paired_differences(summary["arms"]))
    result["ordered_final_units"] = [
        {"task_id": task_id, "seed": seed} for task_id, seed in FINAL_UNIT_KEYS
    ]
    result["independent_unit_count"] = 4
    result["sign_flip_pattern_count"] = 16
    result["sign_patterns_are_not_independent_units"] = True
    if execution_lock_path is not None:
        lock_path = Path(execution_lock_path)
        lock_bytes = lock_path.read_bytes()
        lock = json.loads(lock_bytes.decode("utf-8"))
        lock_sha256 = hashlib.sha256(lock_bytes).hexdigest()
        if summary.get("execution_lock_sha256") != lock_sha256:
            raise ValueError("R4 summary and execution lock raw SHA-256 differ")
        expected_sources = {
            "d094_r4_statistics.py": HERE / "d094_r4_statistics.py",
            "d094_r4_analysis.py": HERE / "d094_r4_analysis.py",
        }
        actual_sources = {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in expected_sources.items()
        }
        for name, actual in actual_sources.items():
            if lock.get("source_files", {}).get(name) != actual:
                raise ValueError(f"R4 analysis source differs from execution lock: {name}")
        result["execution_binding"] = {
            "execution_lock_version": lock.get("execution_lock_version"),
            "execution_lock_sha256": lock_sha256,
            "train_manifest_sha256": lock.get("train_manifest_sha256"),
            "statistics_source_sha256": actual_sources["d094_r4_statistics.py"],
            "analysis_entry_source_sha256": actual_sources["d094_r4_analysis.py"],
            "statistical_method": lock.get("statistical_method"),
        }
    return result
