"""D-092 R2.3 five-arm search runner with auditable real-evaluation budgets."""
from __future__ import annotations

import hashlib
import math
import random
from typing import Any, Dict, List, Optional

from d092_evaluator import assert_optimizer_view, complete_phenotype_collapse
from d092_feedback import combine_feedback, compute_feedback, feedback_features, operator_probabilities
from d092_genome import (
    BLOCKS,
    TypedGenome,
    canonical_json_bytes,
    enumerate_typed_genomes,
    genome_sha256,
    typed_crossover,
    typed_mutation,
)
from d092_selectors import Candidate, nsga3_survivor, non_dominated_fronts, select_final_candidate, select_survivors

ARMS = ("A0", "A1", "A2", "A3", "A4")
SEEDS = (711, 822, 933, 1044, 1155)
MU = 12
LAMBDA = 12
ROUNDS = 7
UNIQUE_TARGET = 96
ATTEMPT_CAP = 384
UNIFORM = (0.25, 0.25, 0.25, 0.25)
STREAMS = ("init", "random_proposal", "variation", "selection_niching")


class BudgetError(RuntimeError):
    pass


class EvaluationInterrupted(RuntimeError):
    def __init__(self, partial_episodes: int):
        super().__init__("evaluation interrupted")
        self.partial_episodes = partial_episodes


def derive_stream_seed(seed: int, stream: str) -> int:
    if stream not in STREAMS:
        raise ValueError("unknown RNG stream: " + stream)
    digest = hashlib.sha256(f"D092-R2|{seed}|{stream}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


class StreamRNG:
    def __init__(self, seed: int, stream: str, arm: str):
        self.stream = stream
        self.arm = arm
        self.seed_integer = derive_stream_seed(seed, stream)
        self.rng = random.Random(self.seed_integer)
        self.events: List[Dict[str, Any]] = []

    def random(self) -> float:
        value = self.rng.random()
        self.events.append({"ordinal": len(self.events), "stream": self.stream, "arm": self.arm, "api": "random", "value": value})
        return value

    def randrange(self, n: int) -> int:
        if n <= 0:
            raise ValueError("randrange requires n>0")
        value = self.rng.randrange(n)
        self.events.append({"ordinal": len(self.events), "stream": self.stream, "arm": self.arm, "api": "randrange", "n": n, "value": value})
        return value


class BudgetLedger:
    def __init__(
        self,
        evaluator,
        arm: str,
        seed: int,
        attempt_cap: int = ATTEMPT_CAP,
        episodes_per_genome: int = 96,
    ):
        self.evaluator = evaluator
        self.arm = arm
        self.seed = seed
        self.attempt_cap = attempt_cap
        self.episodes_per_genome = episodes_per_genome
        self.attempts = 0
        self.unique_evaluations = 0
        self.cache_hits = 0
        self.duplicate_proposals = 0
        self.full_episodes = 0
        self.partial_episodes = 0
        self.partial_episodes_unknown = False
        self.invalid_reason = ""
        self.proposal_seen = set()
        self.completed_cache: Dict[str, Dict[str, Any]] = {}
        self.archive: Dict[str, Dict[str, Any]] = {}
        self.proposal_log: List[Dict[str, Any]] = []
        self.feedback_log: List[Dict[str, Any]] = []
        self.survivor_log: List[Dict[str, Any]] = []
        self.rounds_log: List[Dict[str, Any]] = []
        self.streams: Dict[str, StreamRNG] = {}
        self.initial_hashes: List[str] = []
        self.audit_archive: List[Dict[str, Any]] = []

    def _offer_failure(self, log: Dict[str, Any], status: str, error: Exception, reason: str, unknown: bool) -> None:
        self.invalid_reason = reason
        log.update(
            status=status,
            error_type=type(error).__name__,
            error=str(error),
            partial_episodes_unknown=unknown,
        )
        if unknown:
            self.partial_episodes_unknown = True

    def offer(self, genome: TypedGenome, round_id: int, variation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.attempts >= self.attempt_cap:
            self.invalid_reason = "INVALID_ATTEMPT_CAP"
            raise BudgetError(self.invalid_reason)
        self.attempts += 1
        key = genome_sha256(genome)
        log = {
            "proposal_id": f"{self.arm}|{self.seed}|{self.attempts}",
            "arm": self.arm,
            "seed": self.seed,
            "round": round_id,
            "genome_sha256": key,
            "genome": genome.to_dict(),
            "variation": dict(variation or {}),
            "attempt": self.attempts,
            "status": "PENDING",
            "partial_episodes_unknown": False,
        }
        self.proposal_log.append(log)
        try:
            if key in self.proposal_seen:
                self.duplicate_proposals += 1
                if key not in self.completed_cache:
                    raise BudgetError("INVALID_INCOMPLETE_PRIOR_PROPOSAL")
                self.cache_hits += 1
                log.update(status="DUPLICATE_CACHED", unique_ordinal=self.completed_cache[key]["unique_ordinal"])
                return {"status": "DUPLICATE_CACHED", "entry": self.completed_cache[key]}
            self.proposal_seen.add(key)
            unique_ordinal = self.unique_evaluations
            if hasattr(self.evaluator, "evaluate"):
                result = self.evaluator.evaluate(genome, self.seed, unique_ordinal)
            else:
                result = self.evaluator(genome, self.seed, unique_ordinal)
            view = result.get("optimizer_reward_view") if isinstance(result, dict) and "optimizer_reward_view" in result else result
            try:
                assert_optimizer_view(view)
            except Exception:
                self.invalid_reason = "OPTIMIZER_VIEW_INVALID"
                raise
            if view["genome_sha256"] != key:
                self.invalid_reason = "EVALUATOR_IDENTITY_MISMATCH"
                raise BudgetError(self.invalid_reason)
            if view["feedback_marginals"]["row_count"] != self.episodes_per_genome:
                self.invalid_reason = "EPISODE_COUNT_MISMATCH"
                raise BudgetError(self.invalid_reason)
            fitness = view["fitness"]
            candidate = Candidate(
                genome_hash=key,
                objectives=(
                    1.0 - fitness["R3"], 1.0 - fitness["R4"], 1.0 - fitness["CondRec"],
                    fitness["Harm"], fitness["RecoveryCost"],
                ),
                hard_constraints=view["hard_constraints"],
                phenotype_hashes=view["phenotype_hashes"],
            )
            entry = {
                "genome_object": genome,
                "genome": genome.to_dict(),
                "genome_sha256": key,
                "unique_ordinal": unique_ordinal,
                "round": round_id,
                "optimizer_reward_view": view,
                "candidate": candidate,
            }
            if isinstance(result, dict) and "audit_only_view" in result:
                self.audit_archive.append({
                    "unique_ordinal": unique_ordinal,
                    "genome_sha256": key,
                    "audit_only_view": result["audit_only_view"],
                })
            self.completed_cache[key] = entry
            self.archive[key] = entry
            self.unique_evaluations += 1
            self.full_episodes += self.episodes_per_genome
            log.update(status="NEW_UNIQUE", unique_ordinal=unique_ordinal)
            return {"status": "NEW_UNIQUE", "entry": entry}
        except EvaluationInterrupted as error:
            self.partial_episodes += error.partial_episodes
            log["partial_episodes"] = error.partial_episodes
            self._offer_failure(log, "INTERRUPTED", error, "EVALUATION_INTERRUPT", False)
            raise
        except Exception as error:
            reason = self.invalid_reason or "EVALUATOR_ERROR"
            self._offer_failure(log, "FAILED", error, reason, True)
            raise

    def finalize(self) -> Dict[str, int]:
        expected_episodes = self.unique_evaluations * self.episodes_per_genome
        if self.invalid_reason or self.attempts > self.attempt_cap or self.unique_evaluations != UNIQUE_TARGET or self.full_episodes != expected_episodes or self.partial_episodes:
            self.invalid_reason = self.invalid_reason or "INCOMPLETE_BUDGET"
            raise BudgetError(self.invalid_reason)
        return self.status()

    def status(self) -> Dict[str, Any]:
        return {
            "attempts": self.attempts,
            "unique_evaluations": self.unique_evaluations,
            "cache_hits": self.cache_hits,
            "duplicate_proposals": self.duplicate_proposals,
            "full_episodes": self.full_episodes,
            "partial_episodes": self.partial_episodes,
            "partial_episodes_unknown": self.partial_episodes_unknown,
            "invalid_reason": self.invalid_reason,
        }


def _json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else ("Infinity" if value > 0 else ("-Infinity" if value < 0 else "NaN"))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if hasattr(value, "item"):
        return _json_safe(value.item())
    raise ValueError("non-serializable audit value: " + type(value).__name__)


def _select_block(probabilities, rng: StreamRNG) -> str:
    value = rng.random()
    cumulative = 0.0
    for block, probability in zip(BLOCKS, probabilities):
        cumulative += probability
        if value < cumulative:
            return block
    return "harm"


def _archive_public(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "genome": entry["genome"],
        "genome_sha256": entry["genome_sha256"],
        "unique_ordinal": entry["unique_ordinal"],
        "round": entry["round"],
        "optimizer_reward_view": entry["optimizer_reward_view"],
    }


def _run_arm(arm: str, seed: int, evaluator, episodes_per_genome: int = 96, ledger: Optional[BudgetLedger] = None) -> Dict[str, Any]:
    if arm not in ARMS:
        raise ValueError("unknown arm: " + arm)
    streams = {name: StreamRNG(seed, name, arm) for name in STREAMS}
    ledger = ledger or BudgetLedger(evaluator, arm, seed, episodes_per_genome=episodes_per_genome)
    ledger.streams = streams
    initial_pool = list(enumerate_typed_genomes())
    initial = []
    for _ in range(MU):
        index = streams["init"].randrange(len(initial_pool))
        initial.append(initial_pool.pop(index))
    population = []
    for genome in initial:
        outcome = ledger.offer(genome, 0, {"operator": "initialization"})
        population.append(outcome["entry"])
    initial_hashes = [genome_sha256(genome) for genome in initial]
    ledger.initial_hashes = initial_hashes
    probabilities = UNIFORM
    feedback_log = ledger.feedback_log
    survivor_log = ledger.survivor_log
    rounds_log = ledger.rounds_log
    for round_id in range(1, ROUNDS + 1):
        accepted = []
        if arm == "A0":
            remaining = [genome for genome in enumerate_typed_genomes() if genome_sha256(genome) not in ledger.proposal_seen]
            for _ in range(LAMBDA):
                index = streams["random_proposal"].randrange(len(remaining))
                genome = remaining.pop(index)
                outcome = ledger.offer(genome, round_id, {"operator": "random_without_replacement"})
                accepted.append(outcome["entry"])
        else:
            while len(accepted) < LAMBDA:
                ordered = sorted(population, key=lambda entry: entry["genome_sha256"])
                if streams["variation"].random() < 0.7:
                    parent = ordered[streams["variation"].randrange(len(ordered))]
                    working = parent["genome_object"]
                    operator = "mutation"
                    parents = [parent["genome_sha256"]]
                else:
                    first = streams["variation"].randrange(MU)
                    second = streams["variation"].randrange(MU - 1)
                    if second >= first:
                        second += 1
                    parent_a, parent_b = ordered[first], ordered[second]
                    working = typed_crossover(parent_a["genome_object"], parent_b["genome_object"], streams["variation"])
                    operator = "crossover_mutation"
                    parents = [parent_a["genome_sha256"], parent_b["genome_sha256"]]
                block = _select_block(probabilities, streams["variation"])
                child = typed_mutation(working, block, streams["variation"])
                locus = [field for field in child.to_dict() if child.to_dict()[field] != working.to_dict()[field]]
                outcome = ledger.offer(child, round_id, {
                    "operator": operator,
                    "parents": parents,
                    "block": block,
                    "locus": locus,
                })
                if outcome["status"] == "NEW_UNIQUE":
                    accepted.append(outcome["entry"])
        combined = None
        feature_values = None
        phi = None
        if arm == "A3":
            combined = combine_feedback([entry["optimizer_reward_view"] for entry in accepted])
            feature_values = compute_feedback(combined)
            phi = feedback_features(feature_values)
            probabilities = operator_probabilities(phi)
        elif arm == "A4":
            feature_values = {name: 0.0 for name in ("r", "d", "p", "a", "u", "h")}
            phi = (0.0, 0.0, 0.0, 0.0)
            probabilities = UNIFORM
        else:
            probabilities = UNIFORM
        feedback_log.append({
            "round": round_id,
            "input_genomes": [entry["genome_sha256"] for entry in accepted],
            "combined": combined,
            "features": feature_values,
            "phi": phi,
            "probabilities": list(probabilities),
            "next_probabilities": list(probabilities),
            "rng_counts": {name: len(stream.events) for name, stream in streams.items()},
        })
        selection_audit = None
        if arm != "A0":
            candidates = [entry["candidate"] for entry in population + accepted]
            if arm == "A2" and sum(candidate.feasible for candidate in candidates) >= MU:
                feasible_candidates = [candidate for candidate in candidates if candidate.feasible]
                selected, selection_audit = nsga3_survivor(feasible_candidates, MU, streams["selection_niching"])
            else:
                selected = select_survivors(candidates, arm, MU, streams["selection_niching"])
                selection_audit = {
                    "fronts": [[candidate.genome_hash for candidate in front] for front in non_dominated_fronts(candidates)],
                }
            selected_by_hash = {candidate.genome_hash: candidate for candidate in selected}
            population = [entry for entry in population + accepted if entry["genome_sha256"] in selected_by_hash]
            population.sort(key=lambda entry: [candidate.genome_hash for candidate in selected].index(entry["genome_sha256"]))
            survivor_log.append({
                "round": round_id,
                "status": "SURVIVOR_SELECTION",
                "selected": [candidate.genome_hash for candidate in selected],
                "audit": selection_audit,
            })
        else:
            survivor_log.append({"round": round_id, "status": "NO_SURVIVOR", "selected": []})
        rounds_log.append({
            "round": round_id,
            "accepted": [entry["genome_sha256"] for entry in accepted],
            "next_probabilities": list(probabilities),
            "survivor_status": survivor_log[-1]["status"],
        })
    budget = ledger.finalize()
    archive = list(ledger.archive.values())
    final = select_final_candidate([entry["candidate"] for entry in archive])
    if isinstance(final, str):
        final_report = {"status": final}
    else:
        entry = ledger.archive[final.genome_hash]
        final_report = {
            "status": "OK",
            "genome": final.genome_hash and entry["genome"],
            "genome_sha256": final.genome_hash,
            "fitness": entry["optimizer_reward_view"]["fitness"],
        }
    result = {
        "protocol": "D092-R2.3",
        "status": "VALID",
        "arm": arm,
        "seed": seed,
        "initial_genomes": initial_hashes,
        "budget": budget,
        "proposal_log": ledger.proposal_log,
        "rounds": rounds_log,
        "feedback": feedback_log,
        "survivor_log": survivor_log,
        "archive": [_archive_public(entry) for entry in archive],
        "audit_archive": ledger.audit_archive,
        "final_candidate": final_report,
        "phenotype": complete_phenotype_collapse([entry["optimizer_reward_view"] for entry in archive]),
        "rng": {name: stream.events for name, stream in streams.items()},
        "episodes_per_genome": episodes_per_genome,
        "synthetic_or_train": getattr(evaluator, "data_role", "SYNTHETIC"),
    }
    return _json_safe(result)


def run_arm(arm: str, seed: int, evaluator, episodes_per_genome: int = 96) -> Dict[str, Any]:
    ledger = BudgetLedger(evaluator, arm, seed, episodes_per_genome=episodes_per_genome)
    try:
        return _run_arm(arm, seed, evaluator, episodes_per_genome, ledger)
    except Exception as error:
        archive = list(ledger.archive.values())
        phenotype = complete_phenotype_collapse([entry["optimizer_reward_view"] for entry in archive]) if archive else {
            "H_trace": 0, "H_outcome": 0, "H_joint": 0,
            "diversity_ratio_trace": 0.0, "diversity_ratio_outcome": 0.0, "diversity_ratio_joint": 0.0,
            "complete_phenotype_collapse": True,
        }
        reason = ledger.invalid_reason or "INVALID_RUN"
        result = {
            "protocol": "D092-R2.3",
            "status": "INVALID",
            "error_type": type(error).__name__,
            "invalid_reason": reason,
            "arm": arm,
            "seed": seed,
            "initial_genomes": ledger.initial_hashes,
            "budget": ledger.status(),
            "proposal_log": ledger.proposal_log,
            "rounds": ledger.rounds_log,
            "feedback": ledger.feedback_log,
            "survivor_log": ledger.survivor_log,
            "archive": [_archive_public(entry) for entry in archive],
            "audit_archive": ledger.audit_archive,
            "final_candidate": {"status": "INVALID", "reason": reason},
            "phenotype": phenotype,
            "rng": {name: stream.events for name, stream in ledger.streams.items()},
            "episodes_per_genome": episodes_per_genome,
            "synthetic_or_train": getattr(evaluator, "data_role", "SYNTHETIC"),
        }
        return _json_safe(result)


def m1_equivalence(first: Dict[str, Any], second: Dict[str, Any]) -> bool:
    if first["arm"] != "A1" or second["arm"] != "A4":
        raise ValueError("M1 compares A1 with A4")
    keys = (
        "seed", "status", "initial_genomes", "budget", "proposal_log", "rounds",
        "survivor_log", "archive", "final_candidate", "phenotype", "episodes_per_genome", "rng",
    )
    left = {key: first[key] for key in keys}
    right = {key: second[key] for key in keys}
    for target in (left, right):
        target["proposal_log"] = [
            {key: value for key, value in row.items() if key not in ("proposal_id", "arm")}
            for row in target["proposal_log"]
        ]
        target["rng"] = {
            stream: [
                {key: value for key, value in event.items() if key != "arm"}
                for event in events
            ]
            for stream, events in target["rng"].items()
        }
    return canonical_json_bytes(left) == canonical_json_bytes(right)
