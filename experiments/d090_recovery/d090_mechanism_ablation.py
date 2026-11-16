"""D-090 固定规则块消融，保存逐场景原始 rows。"""
from __future__ import annotations

import json
from pathlib import Path

from d090_genome import base_genome
from d090_experiment import evaluate, summarize
from d090_scenarios import build_manifest

VARIANTS = {
    "legacy": {"pair_rule": 1, "fallback_mode": 0, "completion_mode": 0, "harm_order_mode": 0,
               "pair_race_alternate": False, "exhaustive_fallback": False,
               "completion_gate": False, "harm_first_ordering": False},
    "P1_pair_race": {"pair_rule": 0, "fallback_mode": 0, "completion_mode": 0, "harm_order_mode": 0,
                     "pair_race_alternate": True, "exhaustive_fallback": False,
                     "completion_gate": False, "harm_first_ordering": False},
    "P2_exhaustive_fallback": {"pair_rule": 1, "fallback_mode": 2, "completion_mode": 0, "harm_order_mode": 0,
                               "pair_race_alternate": False, "exhaustive_fallback": True,
                               "completion_gate": False, "harm_first_ordering": False},
    "P3_completion_gate": {"pair_rule": 1, "fallback_mode": 0, "completion_mode": 2, "harm_order_mode": 0,
                           "pair_race_alternate": False, "exhaustive_fallback": False,
                           "completion_gate": True, "harm_first_ordering": False},
    "P4_harm_order": {"pair_rule": 1, "fallback_mode": 0, "completion_mode": 0, "harm_order_mode": 2,
                      "pair_race_alternate": False, "exhaustive_fallback": False,
                      "completion_gate": False, "harm_first_ordering": True,
                      "harm_budget_threshold": 12},
}


def main():
    scenarios = build_manifest()["scenarios"]
    result = {"protocol_id": "D-090-FIXED-MECHANISM-ABLATION", "scenario_count": len(scenarios), "variants": {}}
    for name, overrides in VARIANTS.items():
        genome = base_genome(**overrides)
        rows = [evaluate(genome, [scenario])[1][0] for scenario in scenarios]
        result["variants"][name] = {
            "genome": genome.fingerprint(),
            "summary": summarize(rows),
            "pair_race_r3_failures": sum(1 for row in rows if "PAIR_RACE|D3" in row["scenario_id"] and not row["class_success"]),
            "rows": rows,
        }
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    (out / "d090_mechanism_ablation.json").write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(out / "d090_mechanism_ablation.json")


if __name__ == "__main__":
    main()
