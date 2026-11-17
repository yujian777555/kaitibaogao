"""D-092 R2.3 NSGA-II/III and feasibility-first candidate selection."""
from __future__ import annotations

import dataclasses
import functools
import itertools
import math
import random
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

TOLERANCE = 1e-12


@dataclasses.dataclass(frozen=True)
class Candidate:
    genome_hash: str
    objectives: Tuple[float, ...]
    hard_constraints: Dict[str, int] = dataclasses.field(default_factory=dict)
    phenotype_hashes: Dict[str, str] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.objectives) != 5:
            raise ValueError("expected five objectives")

    @property
    def feasible(self) -> bool:
        return all(value == 0 for value in self.hard_constraints.values())


def _dominates(a: Sequence[float], b: Sequence[float]) -> bool:
    return all(x <= y + TOLERANCE for x, y in zip(a, b)) and any(x < y - TOLERANCE for x, y in zip(a, b))


def non_dominated_fronts(candidates: Sequence[Candidate]) -> List[List[Candidate]]:
    remaining = list(candidates)
    fronts = []
    while remaining:
        front = [
            candidate for candidate in remaining
            if not any(_dominates(other.objectives, candidate.objectives) for other in remaining if other is not candidate)
        ]
        if not front:
            raise ValueError("empty non-dominated front")
        fronts.append(sorted(front, key=lambda candidate: candidate.genome_hash))
        remaining = [candidate for candidate in remaining if candidate not in front]
    return fronts


def crowding_distances(front: Sequence[Candidate]) -> Dict[str, float]:
    if not front:
        return {}
    distances = {candidate.genome_hash: 0.0 for candidate in front}
    for index in range(5):
        ordered = sorted(front, key=lambda candidate: (candidate.objectives[index], candidate.genome_hash))
        low = ordered[0].objectives[index]
        high = ordered[-1].objectives[index]
        if high - low <= TOLERANCE:
            continue
        distances[ordered[0].genome_hash] = math.inf
        distances[ordered[-1].genome_hash] = math.inf
        for position in range(1, len(ordered) - 1):
            distances[ordered[position].genome_hash] += (
                ordered[position + 1].objectives[index] - ordered[position - 1].objectives[index]
            ) / (high - low)
    return distances


def nsga2_survivor(candidates: Sequence[Candidate], size: int) -> List[Candidate]:
    selected = []
    for front in non_dominated_fronts(candidates):
        if len(selected) + len(front) <= size:
            selected.extend(front)
            continue
        distances = crowding_distances(front)
        ordered = sorted(front, key=lambda candidate: (-distances[candidate.genome_hash], candidate.genome_hash))
        selected.extend(ordered[: size - len(selected)])
        break
    return selected


def reference_directions() -> Tuple[Tuple[float, ...], ...]:
    integer_directions = sorted(
        values for values in itertools.product(range(4), repeat=5) if sum(values) == 3
    )
    return tuple(tuple(value / 3.0 for value in values) for values in integer_directions)


def normalize_objectives(
    objectives: Sequence[Sequence[float]],
    extreme_points: Optional[Sequence[Sequence[float]]] = None,
    candidate_hashes: Optional[Sequence[str]] = None,
) -> Dict:
    raw = [tuple(float(value) for value in row) for row in objectives]
    if not raw or any(len(row) != 5 for row in raw):
        raise ValueError("normalization requires nonempty five-objective input")
    if any(not math.isfinite(value) for row in raw for value in row):
        raise ValueError("nonfinite objective")
    ideal = tuple(min(row[index] for row in raw) for index in range(5))
    translated = [tuple(row[index] - ideal[index] for index in range(5)) for row in raw]
    if extreme_points is None:
        extremes = []
        for axis in range(5):
            def asf(index: int) -> float:
                return max(
                    translated[index][objective] / (1.0 if objective == axis else 1e-6)
                    for objective in range(5)
                )
            best_score = min(asf(index) for index in range(len(raw)))
            tied = [index for index in range(len(raw)) if asf(index) <= best_score + TOLERANCE]
            if candidate_hashes is not None:
                tied.sort(key=lambda index: candidate_hashes[index])
            extremes.append(raw[tied[0]])
    else:
        if len(extreme_points) != 5:
            raise ValueError("expected five extreme points")
        extremes = [tuple(float(value) for value in row) for row in extreme_points]
    matrix = [tuple(row[index] - ideal[index] for index in range(5)) for row in extremes]
    solution = None
    intercepts = None
    fallback = False
    try:
        candidate_solution = np.linalg.solve(np.asarray(matrix, dtype=float), np.ones(5))
        if np.all(np.isfinite(candidate_solution)) and np.all(candidate_solution != 0.0):
            candidate_intercepts = 1.0 / candidate_solution
            if np.all(np.isfinite(candidate_intercepts)) and np.all(candidate_intercepts > TOLERANCE):
                solution = tuple(float(value) for value in candidate_solution)
                intercepts = tuple(float(value) for value in candidate_intercepts)
    except np.linalg.LinAlgError:
        pass
    if intercepts is None:
        fallback = True
        intercepts = tuple(max(row[index] for row in translated) for index in range(5))
    raw_scale = tuple(float(value) for value in intercepts)
    zero_span = tuple(value <= TOLERANCE for value in raw_scale)
    scale = tuple(1.0 if is_zero else value for value, is_zero in zip(raw_scale, zero_span))
    normalized = []
    for row in translated:
        normalized_row = []
        for value, divisor, is_zero in zip(row, scale, zero_span):
            if is_zero:
                normalized_row.append(0.0)
                continue
            if value < 0.0 and value < -TOLERANCE:
                raise ValueError("negative translated objective")
            normalized_row.append(max(0.0, value) / divisor)
        normalized.append(tuple(normalized_row))
    return {
        "ideal": ideal,
        "translated": translated,
        "extreme_points": extremes,
        "matrix": matrix,
        "solution": solution,
        "intercepts": raw_scale,
        "raw_scale": raw_scale,
        "scale": scale,
        "zero_span": zero_span,
        "fallback": fallback,
        "normalized": normalized,
    }


def associate_to_reference(
    normalized: Sequence[float],
    directions: Sequence[Sequence[float]],
) -> Tuple[int, float]:
    best_index = None
    best_distance = None
    for index, direction in enumerate(directions):
        norm = sum(value * value for value in direction)
        if norm <= 0.0:
            raise ValueError("zero reference direction")
        projection = sum(a * b for a, b in zip(normalized, direction)) / norm
        distance = sum((value - projection * target) ** 2 for value, target in zip(normalized, direction))
        if best_distance is None or distance < best_distance - TOLERANCE:
            best_index, best_distance = index, distance
    if best_index is None:
        raise ValueError("empty reference directions")
    return best_index, best_distance


def select_niche_candidate(
    remaining: Sequence[Candidate],
    niche_counts: Sequence[int],
    associations: Dict[str, int],
    distances: Dict[str, float],
    rng: random.Random,
    audit: List[Dict],
) -> Candidate:
    if not remaining:
        raise ValueError("empty niching candidate set")
    available_directions = sorted({associations[candidate.genome_hash] for candidate in remaining})
    minimum = min(niche_counts[direction] for direction in available_directions)
    tied_directions = [direction for direction in available_directions if niche_counts[direction] == minimum]
    direction = tied_directions[0] if len(tied_directions) == 1 else tied_directions[rng.randrange(len(tied_directions))]
    eligible = sorted(
        [candidate for candidate in remaining if associations[candidate.genome_hash] == direction],
        key=lambda candidate: candidate.genome_hash,
    )
    if minimum == 0:
        best_distance = min(distances[candidate.genome_hash] for candidate in eligible)
        tied = [candidate for candidate in eligible if distances[candidate.genome_hash] <= best_distance + TOLERANCE]
        selected = tied[0]
    else:
        selected = eligible[rng.randrange(len(eligible))]
    audit.append({
        "direction": direction,
        "niche_count": minimum,
        "tied_directions": tied_directions,
        "eligible": [candidate.genome_hash for candidate in eligible],
        "selected": selected.genome_hash,
    })
    return selected


def nsga3_survivor(
    candidates: Sequence[Candidate],
    size: int,
    rng: random.Random,
) -> Tuple[List[Candidate], Dict]:
    fronts = non_dominated_fronts(candidates)
    selected = []
    last_front = None
    for front in fronts:
        if len(selected) + len(front) <= size:
            selected.extend(front)
        else:
            last_front = front
            break
    normalization = normalize_objectives(
        [candidate.objectives for candidate in candidates],
        candidate_hashes=[candidate.genome_hash for candidate in candidates],
    )
    directions = reference_directions()
    associations = {}
    distances = {}
    for candidate, normalized in zip(candidates, normalization["normalized"]):
        direction, distance = associate_to_reference(normalized, directions)
        associations[candidate.genome_hash] = direction
        distances[candidate.genome_hash] = distance
    niche_counts = [0] * len(directions)
    for candidate in selected:
        niche_counts[associations[candidate.genome_hash]] += 1
    niching_audit = []
    if last_front is not None:
        remaining = list(last_front)
        while len(selected) < size:
            chosen = select_niche_candidate(remaining, niche_counts, associations, distances, rng, niching_audit)
            remaining.remove(chosen)
            selected.append(chosen)
            niche_counts[associations[chosen.genome_hash]] += 1
    return selected, {
        "fronts": [[candidate.genome_hash for candidate in front] for front in fronts],
        "last_front": None if last_front is None else [candidate.genome_hash for candidate in last_front],
        "normalization": normalization,
        "reference_directions": directions,
        "association": associations,
        "association_distances": distances,
        "niche_counts": niche_counts,
        "niching": niching_audit,
    }


def _infeasible_key(candidate: Candidate) -> Tuple:
    hard = candidate.hard_constraints
    return (
        hard.get("duplicate_count", 0) > 0,
        hard.get("unauthorized_action_count", 0) > 0,
        hard.get("illegal_state_transition_count", 0),
        hard.get("invalid_action_count", 0),
        hard.get("pending_count", 0),
        hard.get("runtime_abort_count", 0),
        sum(hard.values()),
        candidate.genome_hash,
    )


def select_survivors(candidates: Sequence[Candidate], arm: str, size: int, rng: Optional[random.Random] = None) -> List[Candidate]:
    feasible = [candidate for candidate in candidates if candidate.feasible]
    if len(feasible) >= size:
        if arm in ("A1", "A3", "A4"):
            return nsga2_survivor(feasible, size)
        if arm == "A2":
            if rng is None:
                raise ValueError("NSGA-III requires selection_niching RNG")
            return nsga3_survivor(feasible, size, rng)[0]
        raise ValueError("unknown evolutionary survivor arm: " + arm)
    infeasible = sorted([candidate for candidate in candidates if not candidate.feasible], key=_infeasible_key)
    ordered = sorted(feasible, key=lambda candidate: candidate.genome_hash) + infeasible
    return ordered[:size]


def _final_compare(a: Candidate, b: Candidate) -> int:
    def values(candidate: Candidate) -> Tuple[float, float, float, float, float]:
        r3 = 1.0 - candidate.objectives[0]
        r4 = 1.0 - candidate.objectives[1]
        cond = 1.0 - candidate.objectives[2]
        return min(r3, r4), r3 + r4, cond, candidate.objectives[3], candidate.objectives[4]
    for left, right, maximize in zip(values(a), values(b), (True, True, True, False, False)):
        if abs(left - right) <= TOLERANCE:
            continue
        if maximize:
            return -1 if left > right else 1
        return -1 if left < right else 1
    return -1 if a.genome_hash < b.genome_hash else (1 if a.genome_hash > b.genome_hash else 0)


def select_final_candidate(candidates: Sequence[Candidate]):
    for candidate in candidates:
        if any(not math.isfinite(value) for value in candidate.objectives):
            raise ValueError("nonfinite final-selection objective")
    feasible = [candidate for candidate in candidates if candidate.feasible]
    if not feasible:
        return "NO_FEASIBLE_CANDIDATE"
    front = non_dominated_fronts(feasible)[0]
    return sorted(front, key=functools.cmp_to_key(_final_compare))[0]
