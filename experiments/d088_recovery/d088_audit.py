"""D-088 independent recomputation and frozen-candidate replication.

1. Recompute every arm's summary from its saved best_rows and compare with
   the reported summary (independent recomputation check).
2. Freeze the best zero-violation candidate genomes and evaluate them ONCE
   on fresh families (new scenario ids, never used during search).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "pilot_a3b"))

from d088_genome import D088RecoveryGenome  # noqa: E402
from d088_policies import D088RecoveryPolicy  # noqa: E402
from d088_scenarios import build_manifest  # noqa: E402
from d088_experiment import evaluate_rows, summarize_rows, FIXED  # noqa: E402

OUT = HERE / "results"


def recompute_check(report):
    problems = []
    checked = 0
    for method, arms in report["search"].items():
        for arm, runs in arms.items():
            for run in runs:
                rows = run["best_rows"]
                s = summarize_rows(rows)
                r = run["best_summary"]
                for key in ("cond_rec", "r3_success", "r4_success", "avoid_harm",
                            "recovery_cost", "constraint_violation", "pending_compensation"):
                    if abs(float(s[key]) - float(r[key])) > 1e-9:
                        problems.append(f"{method}/{arm}/seed{run['seed']}: {key} "
                                        f"reported={r[key]} recomputed={s[key]}")
                checked += 1
    return {"checked_runs": checked, "mismatches": problems}


def main():
    report = json.loads((OUT / "d088_experiment_report.json").read_text(encoding="utf-8"))
    audit = {"recompute": recompute_check(report)}
    print("recompute checked:", audit["recompute"]["checked_runs"],
          "mismatches:", len(audit["recompute"]["mismatches"]))
    for m in audit["recompute"]["mismatches"][:5]:
        print("  !", m)

    # ---- freeze best zero-violation candidates per metric focus ----
    candidates = {}
    for method, arms in report["search"].items():
        for arm, runs in arms.items():
            for run in runs:
                s = run["best_summary"]
                if s["constraint_violation"] or s["pending_compensation"]:
                    continue
                key = f"{method}/{arm}/seed{run['seed']}"
                candidates[key] = {
                    "genome": run["best_genome"],
                    "r3": s["r3_success"], "r4": s["r4_success"],
                    "harm": s["avoid_harm"], "cost": s["recovery_cost"],
                }
    best_r4 = max(candidates.items(), key=lambda kv: (kv[1]["r4"], kv[1]["r3"], -kv[1]["harm"]))
    best_r3 = max(candidates.items(), key=lambda kv: (kv[1]["r3"], kv[1]["r4"], -kv[1]["harm"]))
    print("best R4 candidate:", best_r4[0], best_r4[1]["r4"], best_r4[1]["r3"])
    print("best R3 candidate:", best_r3[0], best_r3[1]["r3"], best_r3[1]["r4"])
    audit["frozen"] = {"best_r4": {"name": best_r4[0], **best_r4[1]},
                       "best_r3": {"name": best_r3[0], **best_r3[1]}}

    # ---- independent replication on FRESH families ----
    fresh = build_manifest(tier="fresh")["scenarios"]
    print("fresh scenarios:", len(fresh))
    rep = {}
    for label, spec in (("best_r4", best_r4), ("best_r3", best_r3)):
        g = D088RecoveryGenome(**spec[1]["genome"])
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), fresh)
        rep[label] = summarize_rows(rows)
        print(f"fresh {label} ({spec[0]}): R3={rep[label]['r3_success']:.3f} "
              f"R4={rep[label]['r4_success']:.3f} harm={rep[label]['avoid_harm']:.3f} "
              f"viol={rep[label]['constraint_violation']}")
    for name, factory in FIXED.items():
        rows = evaluate_rows(lambda: factory(20261122), fresh)
        rep[name] = summarize_rows(rows)
        print(f"fresh fixed {name}: R3={rep[name]['r3_success']:.3f} "
              f"R4={rep[name]['r4_success']:.3f} harm={rep[name]['avoid_harm']:.3f}")
    audit["fresh_replication"] = rep
    (OUT / "d088_independent_audit.json").write_text(
        json.dumps(audit, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    print("audit written")


if __name__ == "__main__":
    main()
