"""Paired performance, Genome and Phenotype analysis for saved D-094 Phase 2 data."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from d094_phase2_audit import _candidate, _hash, _metrics


DELTA_FIELDS = (
    "task_success_rate",
    "recovery_success_rate",
    "constraint_violation",
    "harm",
    "tool_cost",
    "input_tokens",
    "output_tokens",
    "token_cost_usd",
    "token_cost_upper_usd",
    "latency_seconds",
    "behavior_diversity",
)


def _delta(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for field in DELTA_FIELDS:
        result[field] = (
            second[field] - first[field]
            if first[field] is not None and second[field] is not None
            else None
        )
    return result


def analyze_phase2(outdir: Path) -> dict[str, Any]:
    """Analyze only saved raw episodes; never invoke an API or rerun a task."""
    outdir = Path(outdir)
    summary = json.loads((outdir / "summary.json").read_text(encoding="utf-8"))
    evolution = json.loads(
        (outdir / "evolution_ledger.json").read_text(encoding="utf-8")
    )
    rows = [
        json.loads(line)
        for line in (outdir / "episodes.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    paired = {}
    for label, first_arm, second_arm in (
        ("B1_minus_B0", "B0", "B1"),
        ("B2_minus_B1", "B1", "B2"),
        ("B2_minus_B0", "B0", "B2"),
    ):
        if second_arm not in summary["arms"]:
            paired[label] = {"status": "NOT_RUN"}
            continue
        paired[label] = {}
        for seed in summary["config"]["seeds"]:
            first_rows = [
                row
                for row in rows
                if row["arm"] == first_arm
                and row["phase"] == summary["arms"][first_arm]["phase"]
                and row["seed"] == seed
            ]
            second_rows = [
                row
                for row in rows
                if row["arm"] == second_arm
                and row["phase"] == summary["arms"][second_arm]["phase"]
                and row["seed"] == seed
            ]
            paired[label][str(seed)] = _delta(
                _metrics(first_rows), _metrics(second_rows)
            )
        if label == "B2_minus_B1":
            paired[label]["comparison_valid"] = (
                summary["status"] == "COMPLETED"
                and summary["arms"]["B2"]["execution_errors"] == 0
                and not summary["budget"]["over_budget"]
            )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["phase"] == "search":
            grouped[row["genome_sha256"]].append(row)
    candidates = [
        _candidate(genome_hash, group) for genome_hash, group in grouped.items()
    ]
    entries = []
    for candidate in candidates:
        selected_rows = candidate["rows"]
        entries.append(
            {
                "genome": candidate["genome"],
                "genome_sha256": candidate["genome_sha256"],
                "metrics": candidate["metrics"],
                "objectives": candidate["candidate"]["objectives"],
                "constraint_violation": candidate["candidate"]["constraint_violation"],
                "execution_errors": candidate["candidate"]["execution_errors"],
                "phenotype_hash": candidate["candidate"]["phenotype_hash"],
                "per_seed": {
                    str(seed): _metrics(
                        [row for row in selected_rows if row["seed"] == seed]
                    )
                    for seed in summary["config"]["seeds"]
                },
            }
        )
    entries.sort(
        key=lambda entry: (
            entry["constraint_violation"] > 0 or entry["execution_errors"] > 0,
            -entry["metrics"]["task_success_rate"],
            entry["metrics"]["token_cost_upper_usd"],
            entry["metrics"]["harm"],
            entry["metrics"]["tool_cost"],
            entry["metrics"]["latency_seconds"],
            entry["genome_sha256"],
        )
    )
    for rank, entry in enumerate(entries, 1):
        entry["exploratory_rank"] = rank

    gene_coverage = {}
    for gene in _gene_keys(entries):
        gene_coverage[gene] = dict(Counter(entry["genome"][gene] for entry in entries))
    by_hash = {entry["genome_sha256"]: entry["genome"] for entry in entries}
    child_parent_differences = {gene: 0 for gene in gene_coverage}
    variation_events = [
        event for event in evolution if event["event_type"] == "variation"
    ]
    for event in variation_events:
        child = by_hash[event["child_genome_hash"]]
        for gene in gene_coverage:
            if any(
                child[gene] != by_hash[parent][gene]
                for parent in event["parent_genome_hashes"]
            ):
                child_parent_differences[gene] += 1
    evaluation_events = [
        event for event in evolution if event["event_type"] == "evaluation"
    ]
    unique_evaluated = {event["genome_hash"] for event in evaluation_events}

    phenotype_groups = defaultdict(list)
    stable_count = 0
    for candidate in candidates:
        phenotype_groups[candidate["candidate"]["phenotype_hash"]].append(
            candidate["genome_sha256"]
        )
        per_seed_hashes = []
        for seed in summary["config"]["seeds"]:
            seed_rows = sorted(
                [row for row in candidate["rows"] if row["seed"] == seed],
                key=lambda row: row["task_id"],
            )
            per_seed_hashes.append(
                _hash([row["metrics"]["phenotype_hash"] for row in seed_rows])
            )
        stable_count += len(set(per_seed_hashes)) == 1
    genome_pair_count = 0
    same_behavior_pairs = 0
    for index, first in enumerate(entries):
        for second in entries[index + 1 :]:
            genome_pair_count += 1
            same_behavior_pairs += first["phenotype_hash"] == second["phenotype_hash"]

    selected_hash = summary["search"]["selected_genome_sha256"]
    selected_search = next(
        (entry for entry in entries if entry["genome_sha256"] == selected_hash), None
    )
    b2 = summary["arms"].get("B2")
    if (
        summary["status"] != "COMPLETED"
        or not b2
        or b2["execution_errors"]
        or summary["budget"]["over_budget"]
    ):
        decision = "INVALID"
    else:
        differences = [
            paired["B2_minus_B1"][str(seed)]["task_success_rate"]
            for seed in summary["config"]["seeds"]
        ]
        if b2["metrics"]["task_success_rate"] > summary["arms"]["B1"]["metrics"][
            "task_success_rate"
        ] and all(value > 0 for value in differences):
            decision = "POSITIVE_SIGNAL"
        elif b2["metrics"]["task_success_rate"] < summary["arms"]["B1"]["metrics"][
            "task_success_rate"
        ] and all(value <= 0 for value in differences):
            decision = "NEGATIVE_RESULT"
        else:
            decision = "NO_CLEAR_GAIN"

    result = {
        "analysis_schema": "d094_phase2_analysis_v1",
        "experiment_status": summary["status"],
        "research_decision": decision,
        "paired_differences": paired,
        "candidate_ranking": entries,
        "best_candidates": entries[:10],
        "selected_search_candidate": selected_search,
        "gene_coverage": gene_coverage,
        "child_parent_gene_difference_counts": child_parent_differences,
        "variation_event_count": len(variation_events),
        "mutation_flagged_event_count": sum(
            event["mutation"] for event in variation_events
        ),
        "mutation_counts_status": "NOT_AUDITABLE: intermediate genome and mutated locus were not logged",
        "evaluation_duplicate_count": len(evaluation_events) - len(unique_evaluated),
        "proposal_duplicate_rate": None,
        "proposal_duplicate_status": "NOT_AUDITABLE: rejected duplicate proposals were not logged",
        "selection_diversity_status": "Final Pareto diversity is available; per-generation survivor phenotypes were not logged",
        "phenotype": {
            "unique_genomes": len(entries),
            "unique_phenotypes": len(phenotype_groups),
            "complete_collapse": len(phenotype_groups) < 2,
            "identical_behavior_groups": [
                sorted(group) for group in phenotype_groups.values() if len(group) > 1
            ],
            "same_genome_stable_across_seeds_count": stable_count,
            "same_genome_stable_across_seeds_fraction": stable_count / len(entries),
            "stability_note": "Seed changes can alter task schedules; stability is not proof of API determinism",
            "different_genome_pair_count": genome_pair_count,
            "different_genome_same_behavior_pair_count": same_behavior_pairs,
            "different_genome_same_behavior_fraction": same_behavior_pairs
            / genome_pair_count
            if genome_pair_count
            else None,
        },
        "gene_effects": summary["search"]["gene_effects"],
        "innovation_evidence": {
            "behavior_changed": len(phenotype_groups) > 1,
            "paired_performance_valid": decision != "INVALID",
            "decision": decision,
        },
    }
    (outdir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def _gene_keys(entries: list[dict[str, Any]]) -> tuple[str, ...]:
    """Return the six serialized gene names in deterministic order."""
    if not entries:
        return ()
    return tuple(sorted(entries[0]["genome"]))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze_phase2(args.outdir)
    print(
        json.dumps(
            {
                "research_decision": result["research_decision"],
                "unique_phenotypes": result["phenotype"]["unique_phenotypes"],
                "candidates": len(result["candidate_ranking"]),
            }
        )
    )
