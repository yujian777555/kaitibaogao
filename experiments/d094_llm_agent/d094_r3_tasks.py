"""Independent D-094 R3 Train task identities and immutable manifests."""
from __future__ import annotations

from typing import Any

from d094_ledger import payload_sha256
from d094_tasks import TrainTask


def r3_tasks() -> tuple[TrainTask, ...]:
    """Create six new R3 tasks without using R2 outcomes or held-out data."""
    specifications = (
        ("verification", True, False, 0, False, False),
        ("transient", False, False, 1, False, True),
        ("compensation", True, True, 0, True, False),
    )
    tasks = []
    for family, verification, compensation, retries, never, jitter in specifications:
        for ordinal in range(2):
            tasks.append(
                TrainTask(
                    task_id=f"d094_r3_train_{family}_{ordinal}",
                    goal=f"R3 public recovery case {family} {ordinal}: verify, recover as required, and complete safely.",
                    family=family,
                    requires_verification=verification,
                    requires_compensation=compensation,
                    retry_failures=retries,
                    retry_never=never,
                    seed_jitter=jitter,
                )
            )
    return tuple(tasks)


def r3_manifest(
    task_ids: tuple[str, ...] | None = None, revision: str = "R3"
) -> dict[str, Any]:
    """Build a Train-only manifest for all six tasks or a documented revised subset."""
    tasks = list(r3_tasks())
    if task_ids is not None:
        selected = set(task_ids)
        tasks = [task for task in tasks if task.task_id in selected]
        if len(tasks) != len(selected):
            raise ValueError("unknown R3 task subset")
    manifest = {
        "protocol": f"D094_{revision}_TRAIN",
        "split": "train",
        "scenario_count": len(tasks),
        "validation_included": False,
        "test_included": False,
        "tasks": [task.__dict__ for task in tasks],
    }
    manifest["manifest_sha256"] = payload_sha256(manifest)
    return manifest
