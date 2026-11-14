"""D-089 independent recompute, policy-level ablation, fresh replication."""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "pilot_a3b"))
sys.path.insert(0, str(_HERE.parent / "d088_recovery"))

from d088_experiment import evaluate_rows, summarize_rows, FIXED  # noqa: E402
from d089_genome import D089Genome  # noqa: E402
from d089_policies import D089BudgetPolicy  # noqa: E402
from d089_scenarios import build_manifest  # noqa: E402

OUT = _HERE / "results"


def recompute(report):
    problems, checked = [], 0
    for run in report["runs"]:
        s = summarize_rows(run["best_rows"])
        r = run["best_summary"]
        for m in ("r3_success", "r4_success", "avoid_harm", "recovery_cost",
                  "constraint_violation", "pending_compensation"):
            if abs(float(s[m]) - float(r[m])) > 1e-9:
                problems.append(f"{run['tag']}/seed{run['seed']}: {m}")
        checked += 1
    return {"checked": checked, "mismatches": problems}


def main():
    report = json.loads((OUT / "d089_search_report.json").read_text(encoding="utf-8"))
    audit = {"recompute": recompute(report)}
    print("recompute:", audit["recompute"]["checked"], "runs,",
          len(audit["recompute"]["mismatches"]), "mismatches")

    # ---- policy-level ablation on the best frozen genome ----
    # pick best balanced genome across all runs (train-time)
    best = max(
        [r for r in report["runs"]
         if r["best_summary"]["constraint_violation"] == 0
         and r["best_summary"]["pending_compensation"] == 0],
        key=lambda r: (min(r["best_summary"]["r3_success"], r["best_summary"]["r4_success"]),
                       r["best_summary"]["r3_success"] + r["best_summary"]["r4_success"],
                       -r["best_summary"]["avoid_harm"])
    )
    print("best run:", best["tag"], "seed", best["seed"])
    genome = D089Genome(**best["best_genome"])
    dev = build_manifest("development")["scenarios"]
    policy_ablation = {}
    for mode, label in ((0, "legacy_stop"), (1, "strict_stop"), (2, "adaptive_stop")):
        g = dataclasses.replace(genome, stop_mode=mode)
        rows = evaluate_rows(lambda: D089BudgetPolicy(g), dev)
        policy_ablation[label] = summarize_rows(rows)
        s = policy_ablation[label]
        print(f"  policy {label}: R3={s['r3_success']:.3f} R4={s['r4_success']:.3f} "
              f"harm={s['avoid_harm']:.3f} cost={s['recovery_cost']:.1f}")
    # reserve / safety ablations
    for kw, label in (({"escalation_reserve": 0.0}, "no_reserve"),
                      ({"cost_safety": 0.5}, "low_safety"),
                      ({"cost_safety": 2.0}, "high_safety")):
        g = dataclasses.replace(genome, **kw)
        rows = evaluate_rows(lambda: D089BudgetPolicy(g), dev)
        policy_ablation[label] = summarize_rows(rows)
        s = policy_ablation[label]
        print(f"  policy {label}: R3={s['r3_success']:.3f} R4={s['r4_success']:.3f} "
              f"harm={s['avoid_harm']:.3f} cost={s['recovery_cost']:.1f}")
    audit["policy_ablation"] = policy_ablation
    audit["frozen"] = {"name": best["tag"], "seed": best["seed"],
                       "genome": best["best_genome"], "summary": best["best_summary"]}

    # ---- Pareto candidates: per-preference summaries on dev ----
    cands = best.get("candidates") or {}
    audit["pareto_candidates_dev"] = {k: v["summary"] for k, v in cands.items()}

    # ---- fresh replication (64 unseen scenarios) ----
    fresh = build_manifest("fresh")["scenarios"]
    rep = {}
    g = D089Genome(**best["best_genome"])
    rows = evaluate_rows(lambda: D089BudgetPolicy(g), fresh)
    rep["frozen_best"] = summarize_rows(rows)
    print(f"fresh frozen_best: R3={rep['frozen_best']['r3_success']:.3f} "
          f"R4={rep['frozen_best']['r4_success']:.3f} harm={rep['frozen_best']['avoid_harm']:.3f} "
          f"viol={rep['frozen_best']['constraint_violation']}")
    for name, factory in FIXED.items():
        rows = evaluate_rows(lambda: factory(20261122), fresh)
        rep[name] = summarize_rows(rows)
        print(f"fresh fixed {name}: R3={rep[name]['r3_success']:.3f} "
              f"R4={rep[name]['r4_success']:.3f} harm={rep[name]['avoid_harm']:.3f}")
    audit["fresh_replication"] = rep
    (OUT / "d089_audit.json").write_text(
        json.dumps(audit, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    print("audit written")


if __name__ == "__main__":
    main()
