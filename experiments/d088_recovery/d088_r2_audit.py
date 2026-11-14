"""D-088 R2 independent recompute and fresh-family replication."""
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


def recompute(report):
    problems, checked = [], 0
    for exp, groups in report["experiments"].items():
        for key, runs in groups.items():
            for run in runs:
                s = summarize_rows(run["best_rows"])
                r = run["best_summary"]
                for m in ("r3_success", "r4_success", "avoid_harm", "recovery_cost",
                          "constraint_violation", "pending_compensation"):
                    if abs(float(s[m]) - float(r[m])) > 1e-9:
                        problems.append(f"{exp}/{key}/seed{run['seed']}: {m}")
                checked += 1
    return {"checked": checked, "mismatches": problems}


def main():
    report = json.loads((OUT / "d088_r2_report.json").read_text(encoding="utf-8"))
    audit = {"recompute": recompute(report)}
    print("recompute checked:", audit["recompute"]["checked"],
          "mismatches:", len(audit["recompute"]["mismatches"]))

    # collect zero-violation candidates
    cands = {}
    for exp, groups in report["experiments"].items():
        for key, runs in groups.items():
            for run in runs:
                s = run["best_summary"]
                if s["constraint_violation"] or s["pending_compensation"]:
                    continue
                name = f"{exp}|{key}|{run.get('operator', '?')}|seed{run['seed']}"
                cands[name] = {
                    "genome": run["best_genome"],
                    "r3": s["r3_success"], "r4": s["r4_success"],
                    "harm": s["avoid_harm"], "cost": s["recovery_cost"],
                    "balanced": min(s["r3_success"], s["r4_success"]),
                }
    frozen = {}
    for metric, keyfn in (
        ("best_balanced", lambda kv: (kv[1]["balanced"], kv[1]["r3"] + kv[1]["r4"], -kv[1]["harm"])),
        ("best_r4", lambda kv: (kv[1]["r4"], kv[1]["r3"], -kv[1]["harm"])),
        ("best_r3", lambda kv: (kv[1]["r3"], kv[1]["r4"], -kv[1]["harm"])),
    ):
        name, spec = max(cands.items(), key=keyfn)
        frozen[metric] = {"name": name, **spec}
        print(f"frozen {metric}: {name} R3={spec['r3']:.3f} R4={spec['r4']:.3f}")
    audit["frozen"] = frozen

    # fresh replication
    fresh = build_manifest(tier="fresh")["scenarios"]
    rep = {}
    for metric, spec in frozen.items():
        g = D088RecoveryGenome(**spec["genome"])
        rows = evaluate_rows(lambda: D088RecoveryPolicy(g), fresh)
        rep[metric] = summarize_rows(rows)
        print(f"fresh {metric}: R3={rep[metric]['r3_success']:.3f} "
              f"R4={rep[metric]['r4_success']:.3f} harm={rep[metric]['avoid_harm']:.3f} "
              f"viol={rep[metric]['constraint_violation']}")
    for name, factory in FIXED.items():
        rows = evaluate_rows(lambda: factory(20261122), fresh)
        rep[name] = summarize_rows(rows)
        print(f"fresh fixed {name}: R3={rep[name]['r3_success']:.3f} "
              f"R4={rep[name]['r4_success']:.3f} harm={rep[name]['avoid_harm']:.3f}")
    audit["fresh_replication"] = rep
    (OUT / "d088_r2_audit.json").write_text(
        json.dumps(audit, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    print("audit written")


if __name__ == "__main__":
    main()
