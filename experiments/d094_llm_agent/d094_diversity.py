"""Behavior- and genome-aware survivor selection without weakening Pareto or safety."""
from __future__ import annotations

import math
from typing import Any, Sequence

from d094_behavior import behavior_distance
from d094_evolution import (
    Candidate,
    crowding_distances,
    non_dominated_fronts,
    nsga2_survivors,
)


def behavior_novelty(
    candidate: Candidate,
    candidates: Sequence[Candidate],
    metric: str = "edit",
) -> float:
    """Nearest-other behavior distance; singleton and exact duplicate novelty are zero."""
    distances = []
    for other in candidates:
        if other is candidate:
            continue
        if candidate.behavior is not None and other.behavior is not None:
            distances.append(
                behavior_distance(candidate.behavior, other.behavior, metric)
            )
        else:
            distances.append(float(candidate.phenotype_hash != other.phenotype_hash))
    return min(distances) if distances else 0.0


def genome_novelty(candidate: Candidate, candidates: Sequence[Candidate]) -> float:
    """Nearest-other normalized six-gene Hamming distance."""
    distances = []
    for other in candidates:
        if other is candidate:
            continue
        differences = sum(
            candidate.genome.to_dict()[field] != other.genome.to_dict()[field]
            for field in candidate.genome.to_dict()
        )
        distances.append(differences / 6.0)
    return min(distances) if distances else 0.0


def _crowding_normalized(front: Sequence[Candidate]) -> dict[str, float]:
    raw = crowding_distances(front)
    finite = [value for value in raw.values() if math.isfinite(value)]
    maximum = max(finite, default=0.0)
    return {
        key: 1.0 if math.isinf(value) else (value / maximum if maximum > 0 else 0.0)
        for key, value in raw.items()
    }


def _score_map(front: Sequence[Candidate], method: str) -> dict[str, float]:
    crowding = _crowding_normalized(front)
    result = {}
    for candidate in front:
        novelty = behavior_novelty(candidate, front)
        if method in {"full", "crowding_novelty"}:
            score = 0.5 * crowding[candidate.genome_id] + 0.5 * novelty
        elif method == "phenotype":
            score = novelty
        elif method == "genome":
            score = 0.5 * crowding[candidate.genome_id] + 0.5 * genome_novelty(
                candidate, front
            )
        elif method in {"behavior_tiebreak", "behavior_cluster"}:
            score = crowding[candidate.genome_id]
        else:
            raise ValueError("unknown diversity method: " + method)
        result[candidate.genome_id] = score
    return result


def _ordered(front: Sequence[Candidate], method: str) -> list[Candidate]:
    scores = _score_map(front, method)
    if method == "behavior_tiebreak":
        return sorted(
            front,
            key=lambda candidate: (
                -scores[candidate.genome_id],
                -behavior_novelty(candidate, front),
                candidate.genome_id,
            ),
        )
    return sorted(
        front,
        key=lambda candidate: (-scores[candidate.genome_id], candidate.genome_id),
    )


def _select_with_duplicate_control(
    front: Sequence[Candidate], size: int, method: str
) -> list[Candidate]:
    if size <= 0:
        return []
    ordered = _ordered(front, method)
    if method == "genome":
        return ordered[:size]
    selected = []
    used = set()
    for candidate in ordered:
        if candidate.phenotype_hash not in used:
            selected.append(candidate)
            used.add(candidate.phenotype_hash)
            if len(selected) == size:
                return selected
    for candidate in ordered:
        if candidate not in selected:
            selected.append(candidate)
            if len(selected) == size:
                break
    return selected


def _select_clusters(front: Sequence[Candidate], size: int) -> list[Candidate]:
    clusters: list[list[Candidate]] = []
    for candidate in sorted(front, key=lambda item: item.genome_id):
        matching = [
            cluster
            for cluster in clusters
            if any(
                behavior_distance(candidate.behavior, other.behavior) <= 0.25
                if candidate.behavior is not None and other.behavior is not None
                else candidate.phenotype_hash == other.phenotype_hash
                for other in cluster
            )
        ]
        if matching:
            matching[0].append(candidate)
        else:
            clusters.append([candidate])
    representatives = []
    for cluster in clusters:
        crowding = _crowding_normalized(cluster)
        representatives.append(
            min(
                cluster,
                key=lambda candidate: (
                    -crowding[candidate.genome_id],
                    -behavior_novelty(candidate, cluster),
                    candidate.genome_id,
                ),
            )
        )
    ordered = sorted(
        representatives,
        key=lambda candidate: (
            -_crowding_normalized([candidate])[candidate.genome_id],
            candidate.genome_id,
        ),
    )
    return ordered[:size]


def diversity_survivors(
    candidates: Sequence[Candidate],
    size: int,
    method: str = "full",
) -> list[Candidate]:
    """Select within Pareto fronts, preserving hard constraints and objective ranks."""
    if size < 0:
        raise ValueError("negative survivor size")
    if size == 0:
        return []
    if method == "standard":
        return nsga2_survivors(candidates, size)
    if method not in {
        "full",
        "crowding_novelty",
        "behavior_tiebreak",
        "behavior_cluster",
        "phenotype",
        "genome",
    }:
        raise ValueError("unknown diversity method")
    unique = {}
    for candidate in candidates:
        unique.setdefault(candidate.genome_id, candidate)
    feasible = [candidate for candidate in unique.values() if candidate.feasible]
    infeasible = sorted(
        [candidate for candidate in unique.values() if not candidate.feasible],
        key=lambda candidate: (
            candidate.constraint_violation,
            candidate.execution_errors,
            candidate.genome_id,
        ),
    )
    selected = []
    for front in non_dominated_fronts(feasible):
        if len(selected) + len(front) <= size:
            selected.extend(front)
            continue
        remaining = size - len(selected)
        if method == "behavior_cluster":
            selected.extend(_select_clusters(front, remaining))
        else:
            selected.extend(_select_with_duplicate_control(front, remaining, method))
        break
    if len(selected) < size:
        selected.extend(infeasible[: size - len(selected)])
    return selected


def _mean_pairwise_distance(selected: Sequence[Candidate]) -> float:
    distances = []
    for index, first in enumerate(selected):
        for second in selected[index + 1 :]:
            if first.behavior is not None and second.behavior is not None:
                distances.append(behavior_distance(first.behavior, second.behavior))
            else:
                distances.append(float(first.phenotype_hash != second.phenotype_hash))
    return sum(distances) / len(distances) if distances else 0.0


def compare_selectors(
    candidates: Sequence[Candidate], size: int
) -> dict[str, dict[str, Any]]:
    """Run four predeclared selector controls on the same evaluated candidates."""
    result = {}
    for method in ("standard", "genome", "phenotype", "full"):
        selected = diversity_survivors(candidates, size, method)
        result[method] = {
            "selected_genome_hashes": [candidate.genome_id for candidate in selected],
            "selected_phenotype_hashes": [
                candidate.phenotype_hash for candidate in selected
            ],
            "unique_genomes": len({candidate.genome_id for candidate in selected}),
            "unique_phenotypes": len(
                {candidate.phenotype_hash for candidate in selected}
            ),
            "unique_objective_vectors": len(
                {candidate.objectives for candidate in selected}
            ),
            "mean_pairwise_behavior_distance": _mean_pairwise_distance(selected),
        }
    return result
