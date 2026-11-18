"""Typed D-094 Agent Genome, canonical identity and legal variation."""
from __future__ import annotations

import dataclasses
import itertools
import random
from typing import Any

from d094_ledger import payload_sha256
from d094_prompts import prompt_template_sha256


ALLOWED_VALUES = {
    "planning_mode": ("direct", "stepwise", "verification_first"),
    "recovery_mode": (
        "retry_priority",
        "verify_priority",
        "compensation_priority",
        "dependency_aware",
    ),
    "reflection_trigger": ("none", "after_failure", "after_subtask"),
    "memory_mode": ("recent_trajectory", "structured_failures", "compressed_summary"),
    "tool_call_guard": ("strict_schema", "post_plan_verify"),
    "max_plan_steps": (3, 5, 8),
}
PROMPT_VERSION = "d094-react-json-v1"


@dataclasses.dataclass(frozen=True)
class AgentGenome:
    """Six typed genes controlling an executable LLM Agent configuration."""

    planning_mode: str = "stepwise"
    recovery_mode: str = "dependency_aware"
    reflection_trigger: str = "after_failure"
    memory_mode: str = "structured_failures"
    tool_call_guard: str = "post_plan_verify"
    max_plan_steps: int = 5

    def __post_init__(self) -> None:
        for field, allowed in ALLOWED_VALUES.items():
            value = getattr(self, field)
            if not any(
                type(value) is type(option) and value == option for option in allowed
            ):
                raise ValueError(f"invalid {field}: {value!r}")

    def to_dict(self) -> dict[str, Any]:
        """Return only the six evolvable genes."""
        return dataclasses.asdict(self)

    def to_agent_config(self) -> dict[str, Any]:
        """Map this genome to a deterministic executable Agent configuration."""
        return {
            **self.to_dict(),
            "prompt_version": PROMPT_VERSION,
            "prompt_template_sha256": prompt_template_sha256(PROMPT_VERSION),
        }


FIXED_GENOME = AgentGenome()


def genome_sha256(genome: AgentGenome) -> str:
    """Compute the unique canonical identity of a typed genome."""
    return payload_sha256(genome.to_dict())


def enumerate_genomes() -> tuple[AgentGenome, ...]:
    """Enumerate all 648 legal configurations in canonical order."""
    values = list(ALLOWED_VALUES.values())
    genomes = [AgentGenome(*items) for items in itertools.product(*values)]
    return tuple(sorted(genomes, key=genome_sha256))


def mutate_genome(genome: AgentGenome, rng: random.Random) -> AgentGenome:
    """Replace exactly one gene with a different legal value."""
    fields = tuple(ALLOWED_VALUES)
    field = fields[rng.randrange(len(fields))]
    alternatives = [
        value for value in ALLOWED_VALUES[field] if value != getattr(genome, field)
    ]
    return dataclasses.replace(
        genome, **{field: alternatives[rng.randrange(len(alternatives))]}
    )


def crossover_genomes(
    first: AgentGenome, second: AgentGenome, rng: random.Random
) -> AgentGenome:
    """Inherit every gene independently from one of two legal parents."""
    values = {
        field: getattr(first if rng.random() < 0.5 else second, field)
        for field in ALLOWED_VALUES
    }
    return AgentGenome(**values)


def phenotype_sha256(events: list[dict[str, Any]]) -> str:
    """Hash public behavior, excluding request timing, tokens and model metadata."""
    projected = []
    for event in events:
        if event.get("event_type") == "decision":
            payload = event["payload"]
            projected.append(
                {
                    "event_type": "decision",
                    "action": payload["action"],
                    "tool_name": payload["tool_name"],
                    "tool_arguments": payload["tool_arguments"],
                }
            )
        elif event.get("event_type") in {"tool_result", "tool_rejected"}:
            payload = event["payload"]
            projected.append(
                {
                    "event_type": event["event_type"],
                    "tool_name": payload.get("tool_name"),
                    "observation": payload.get("observation"),
                    "success": payload.get("success"),
                }
            )
    return payload_sha256(projected)
