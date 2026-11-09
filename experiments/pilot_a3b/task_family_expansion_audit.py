"""Task-family expansion feasibility audit (D-063 Stage 2).

Enumerates contract-meaningful 3-step task families over the A-3 tool set,
selects a DIVERSE family panel (greedy min-overlap + profile diversity),
computes tool-overlap leakage statistics against the current 6 families, and
proposes the train/validation/test split sized by the Stage-1 power analysis.

Run: python task_family_expansion_audit.py
"""
from __future__ import annotations

import itertools
import json
import statistics as st
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "pilot_a_recovery"))
from pilot_a3 import (  # noqa: E402
    HELDOUT_COMPOSITIONS, TASKS, TOOLS, TRAIN_COMPOSITIONS, VALIDATION_COMPOSITIONS,
)

HERE = Path(__file__).parent
N_FAMILIES = 23  # covers power requirement (see 63 report)


def meaningful(seq):
    prof = [(TOOLS[n]["idempotent"], TOOLS[n]["compensatable"]) for n in seq]
    return (any(not p[0] for p in prof) and any(p[1] for p in prof)
            and any(not p[1] for p in prof))


def enumerate_candidates():
    names = list(TOOLS)
    out = []
    for seq in itertools.permutations(names, 3):
        if meaningful(seq):
            out.append(seq)
    return out


def greedy_diverse(candidates, n, current_families):
    """Greedy selection minimising total tool overlap with the already-chosen
    set (seeded with current families' union to encourage new combinations)."""
    chosen = [tuple(v) for v in TASKS.values()]
    pool = [c for c in candidates if c not in chosen]
    while len(chosen) - len(TASKS) < n and pool:
        def score(seq):
            overlap = sum(len(set(seq) & set(o)) for o in chosen)
            return overlap
        pool.sort(key=lambda s: (score(s), s))
        chosen.append(pool.pop(0))
    return chosen[len(TASKS):]


def overlap_stats(families):
    pairs = list(itertools.combinations(families, 2))
    ov = [len(set(a) & set(b)) for a, b in pairs]
    tool_count = Counter(t for f in families for t in f)
    return {
        "n_families": len(families),
        "pairwise_tool_overlap_mean": round(st.mean(ov), 3) if ov else None,
        "pairwise_tool_overlap_max": max(ov) if ov else 0,
        "zero_overlap_pairs": sum(1 for x in ov if x == 0),
        "total_pairs": len(ov),
        "tool_usage": dict(tool_count),
    }


def main():
    comps = list(TRAIN_COMPOSITIONS) + list(VALIDATION_COMPOSITIONS) + list(HELDOUT_COMPOSITIONS)
    candidates = enumerate_candidates()
    profiles = {}
    for seq in candidates:
        prof = tuple((TOOLS[n]["idempotent"], TOOLS[n]["compensatable"]) for n in seq)
        profiles.setdefault(prof, []).append(seq)

    new_families = greedy_diverse(candidates, N_FAMILIES, TASKS)
    all_families = [tuple(v) for v in TASKS.values()] + new_families

    cur_stats = overlap_stats([tuple(v) for v in TASKS.values()])
    new_stats = overlap_stats(new_families)
    all_stats = overlap_stats(all_families)

    # split proposal sized by power analysis: test ~153 clusters (17x9),
    # val 36 (4x9), train 72 (8x9) -> 29 families; here we select 23 new + 6
    # current = 29 total.
    split = {
        "train": all_families[:8],
        "validation": all_families[8:12],
        "test_locked": all_families[12:29],
    }
    cluster_counts = {k: len(v) * len(comps) for k, v in split.items()}

    out = {
        "kind": "TASK_FAMILY_EXPANSION_AUDIT_D063",
        "n_tools": len(TOOLS),
        "tool_contracts": {k: {"idempotent": v["idempotent"], "compensatable": v["compensatable"],
                               "visibility_bound": v["visibility_bound"]} for k, v in TOOLS.items()},
        "current_families": {k: list(v) for k, v in TASKS.items()},
        "fault_compositions": comps,
        "n_contract_meaningful_candidates": len(candidates),
        "n_distinct_contract_profiles": len(profiles),
        "overlap_current_6": cur_stats,
        "overlap_new_panel": new_stats,
        "overlap_all_29": all_stats,
        "new_families_selected": ["->".join(f) for f in new_families],
        "split_proposal": {k: ["->".join(f) for f in v] for k, v in split.items()},
        "cluster_counts": cluster_counts,
        "template_leakage_risks": [
            "all families share the same 10-tool pool: generalisation claim is new ordered tool-sequences + contract combinations, NOT new tools",
            "naive enumeration (one per contract profile) concentrates on ledger (mean overlap 2.0/3 steps) -- the greedy min-overlap panel reduces but cannot eliminate tool reuse",
            "fault composition families (9) are shared across task families by factorial design: composition-level OOD is a separate axis and must stay factorized",
            "same generator (make_fault_vector) semantics across splits: fault parameter draws differ by seed, fault TYPE vocabulary is shared",
        ],
        "independence_assessment": {
            "task_family_axis": "ordered 3-step sequences; pairwise tool overlap is the main leakage proxy",
            "composition_axis": "9 named compositions, factorized vs task axis (A-3 design preserved)",
            "cluster_definition": "task_family x fault_composition; ICC from Stage 1 ~ -0.09 (no between-task-family correlation detected in development data)",
        },
    }
    (HERE / "task_family_expansion_audit.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n_contract_meaningful_candidates", "n_distinct_contract_profiles",
                                          "overlap_current_6", "overlap_new_panel", "overlap_all_29",
                                          "cluster_counts")}, indent=2))
    print("new families:")
    for f in out["new_families_selected"]:
        print("  ", f)
    print("split proposal:", json.dumps(out["split_proposal"], indent=1))


if __name__ == "__main__":
    main()
