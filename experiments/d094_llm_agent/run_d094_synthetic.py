"""Generate reproducible D-094 synthetic selector and adaptive-evolution evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from d094_adaptive_evolution import run_synthetic_ablation
from d094_behavior import behavior_representation
from d094_diversity import compare_selectors
from d094_evolution import Candidate
from d094_genome import AgentGenome, enumerate_genomes


def _behavior(tool_name: str) -> dict[str, Any]:
    return behavior_representation(
        [
            {
                "event_type": "decision",
                "payload": {
                    "action": "tool_call",
                    "tool_name": tool_name,
                    "tool_arguments": {},
                },
            },
            {
                "event_type": "tool_result",
                "payload": {
                    "tool_name": tool_name,
                    "success": True,
                    "observation": {"status": "OK"},
                    "done": True,
                    "before_state": {"step": 0},
                    "after_state": {"step": 1},
                },
            },
        ],
        agent_status="COMPLETED",
    )


def synthetic_evaluate(genome: AgentGenome) -> Candidate:
    """Map genes to public synthetic behavior and failure profiles, never real performance."""
    tool = {
        "retry_priority": "retry_primary",
        "verify_priority": "verify_state",
        "compensation_priority": "compensate_primary",
        "dependency_aware": "inspect_state",
    }[genome.recovery_mode]
    behavior = _behavior(tool)
    failing = genome.recovery_mode in {"retry_priority", "compensation_priority"}
    return Candidate(
        genome=genome,
        objectives=(float(genome.max_plan_steps), float(genome.max_plan_steps)),
        phenotype_hash=behavior["canonical_sha256"],
        behavior=behavior,
        failure_profile={
            "counts": {"recovery_failure": int(failing)},
            "denominators": {"episode_count": 1, "recovery_attempt_count": 1},
            "rates": {
                "planning_failure": 0.0,
                "tool_call_failure": 0.0,
                "dependency_failure": 0.0,
                "recovery_failure": float(failing),
                "verification_failure": 0.0,
                "task_incompletion": float(failing),
                "unnecessary_tool_call": 0.0,
            },
        },
    )


def main() -> None:
    """Write deterministic synthetic-only evidence without network access."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    ablation = run_synthetic_ablation(
        synthetic_evaluate, population_size=4, generations=1, seed=42
    )
    genomes = enumerate_genomes()[:4]
    behaviors = [
        _behavior("verify_state"),
        _behavior("verify_state"),
        _behavior("retry_primary"),
        _behavior("compensate_primary"),
    ]
    candidates = [
        Candidate(
            genome=genome,
            objectives=(1.0, 1.0),
            phenotype_hash=behavior["canonical_sha256"],
            behavior=behavior,
        )
        for genome, behavior in zip(genomes, behaviors)
    ]
    selectors = compare_selectors(candidates, 2)
    metadata = {
        "protocol": "D094_R3_SYNTHETIC_V1",
        "scientific_scope": "SYNTHETIC_ONLY",
        "api_used": False,
        "seed": 42,
        "population_size": 4,
        "generations": 1,
        "source_files": {
            name: hashlib.sha256(
                (Path(__file__).parent / name).read_bytes()
            ).hexdigest()
            for name in (
                "d094_adaptive_evolution.py",
                "d094_behavior.py",
                "d094_diversity.py",
                "d094_evolution.py",
                "d094_feedback_evolution.py",
                "d094_genome.py",
                "run_d094_synthetic.py",
            )
        },
    }
    for name, value in (
        ("ablation.json", ablation),
        ("selector_comparison.json", selectors),
        ("metadata.json", metadata),
    ):
        (args.outdir / name).write_text(
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    print(
        json.dumps(
            {
                "scope": "SYNTHETIC_ONLY",
                "ablation_arms": len(ablation),
                "selector_controls": len(selectors),
            }
        )
    )


if __name__ == "__main__":
    main()
