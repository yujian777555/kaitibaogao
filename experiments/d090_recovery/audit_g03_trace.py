import json, sys
from pathlib import Path
sys.path.insert(0, "experiments/d089_recovery"); sys.path.insert(0, "experiments/pilot_a3b"); sys.path.insert(0, "experiments/d088_recovery")

rep = json.loads(Path("experiments/d089_recovery/results/d089_search_report.json").read_text(encoding="utf-8"))
best = [r for r in rep["runs"] if r["tag"]=="RandomSearch" and r["seed"]==822][0]
print("genome:", {k: round(v,2) if isinstance(v,float) else v for k,v in best["best_genome"].items() if k in ("stop_residual","allow_alternate","allow_verify","max_attempts","stop_mode","escalation_reserve","cost_safety","strict_residual_stop","enable_a","enable_b","enable_c")})
fails = [r for r in best["best_rows"] if not r["class_success"]]
print("total fails:", len(fails))
for f in fails:
    print("="*70)
    print(f["scenario_id"], f["label"], "dec", f["decision_count"], "resid", f["residual_side_effects"], "min", f["min_reachable_harm"], "avoid", f["avoidable_harm"])
    for t in f["trace"]:
        print("  ", t["action"], "->", t["observation"])
