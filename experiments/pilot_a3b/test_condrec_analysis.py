"""Tests for the CondRecSucc primary-endpoint analysis (D-064-A Task E)."""
import json
import unittest
from pathlib import Path

from condrec_analysis import analyze, endpoint_table, integrity_checks, safety_endpoint


def row(sid, task, comp, split, label, cs, seed):
    return {"scenario_id": sid, "split": split, "task": task, "composition": comp,
            "seed": seed, "label": label, "class_success": cs, "task_success": cs,
            "invariant_violation": 0, "duplicate": 0, "sla_violation": 0,
            "avoidable_harm": 0, "policy_selected_escalation": 1 if cs else 0,
            "decision_count": 3, "active_effects": 0}


def payload(methods=("AB", "nsga2"), seeds=(1, 2)):
    """Mini fixture: 3 clusters; cluster C has only R3 rows (zero denominator).
    AB beats nsga2 by exactly +0.5 on every R1/R2 scenario."""
    runs = []
    design = [
        ("t1", "c1", "R1"), ("t1", "c2", "R2"), ("t2", "c1", "R3"), ("t2", "c2", "R4"),
        ("t1", "c3", "R3"),
    ]
    for m in methods:
        for s in seeds:
            rows = []
            for task, comp, lab in design:
                sid = f"s|{task}|{comp}|{lab}"
                base = 1 if lab in ("R1", "R2") else 1
                if lab in ("R1", "R2"):
                    cs_a = 1 if m == "AB" else 0  # paired diff = +1 here... use 1 vs 0.5 via dup rows?
                else:
                    cs_a = base
                rows.append(row(sid, task, comp, "train", lab, cs_a, s))
            runs.append({"method": m, "seed": s, "episodes": len(rows), "rows": rows})
    # make AB=1.0, nsga2=0.0 on R1/R2 -> scenario diff +1.0 (fixture uses binary)
    p = {"kind": "TEST", "methods": list(methods), "seeds": list(seeds), "runs": runs}
    return p


class EndpointFilterTests(unittest.TestCase):
    def test_r1_r2_filter_only(self):
        tbl = endpoint_table(payload())
        # clusters t1|c1 (R1), t1|c2 (R2) eligible; t2|c1, t2|c2, t1|c3 zero-denom
        self.assertEqual(tbl["primary_eligible_clusters"], 2)
        self.assertEqual(tbl["zero_denominator_clusters"], 3)
        self.assertEqual(tbl["total_design_clusters"], 5)

    def test_r3_r4_excluded_from_primary(self):
        tbl = endpoint_table(payload())
        ids = set(tbl["per_cluster_r12_denominator"])
        self.assertNotIn("t2|c1", ids)   # R3-only cluster
        self.assertNotIn("t2|c2", ids)   # R4-only cluster

    def test_pairing_and_seed_nesting(self):
        tbl = endpoint_table(payload())
        self.assertEqual(tbl["pairing_completeness"], 1.0)
        self.assertEqual(tbl["n_paired_scenarios"], 2)
        # AB 1 vs nsga2 0 -> diff +1 on both scenarios
        self.assertAlmostEqual(tbl["mean_paired_diff"], 1.0)
        self.assertAlmostEqual(tbl["scenario_weighted_diff"], 1.0)

    def test_cluster_equal_weighting(self):
        # cluster t1|c1 has 1 scenario; give t1|c2 two scenarios with diff +1 and -1
        p = payload()
        for run in p["runs"]:
            for extra_lab, cs_a in (("R2b", 1), ("R2c", 0)):
                cs = cs_a if run["method"] == "AB" else 0
                run["rows"].append(row(f"s|t1|c2|{extra_lab}", "t1", "c2", "train", "R2", cs, run["seed"]))
        tbl = endpoint_table(p)
        by = {c["cluster"]: c for c in tbl["cluster_table"]}
        # t1|c2 scenario diffs: +1 (s|R2), +1 (R2b), 0 (R2c) -> mean 2/3
        self.assertAlmostEqual(by["t1|c2"]["mean_paired_diff"], 2 / 3, places=6)
        self.assertAlmostEqual(by["t1|c1"]["mean_paired_diff"], 1.0, places=6)
        # cluster-equal mean = (1 + 2/3)/2 = 5/6
        self.assertAlmostEqual(tbl["mean_paired_diff"], 5 / 6, places=6)
        # scenario-weighted = (1+1+0+1)/4 wait: scenarios s|R1(1), s|R2(1), R2b(1), R2c(0) -> 0.75
        self.assertAlmostEqual(tbl["scenario_weighted_diff"], 0.75, places=6)

    def test_zero_denominator_registered_not_filled(self):
        tbl = endpoint_table(payload())
        self.assertEqual(len(tbl["zero_denominator_cluster_ids"]), 3)
        for cid in tbl["zero_denominator_cluster_ids"]:
            self.assertNotIn(cid, tbl["per_cluster_r12_denominator"])

    def test_missing_pair_reported(self):
        p = payload()
        for run in p["runs"]:
            if run["method"] == "nsga2" and run["seed"] == 2:
                run["rows"] = [r for r in run["rows"] if r["scenario_id"] != "s|t1|c1|R1"]
        tbl = endpoint_table(p)
        self.assertTrue(tbl["missing_pairs"])
        self.assertLess(tbl["pairing_completeness"], 1.0)

    def test_duplicate_episode_rejected(self):
        p = payload()
        p["runs"][0]["rows"].append(p["runs"][0]["rows"][0].copy())
        rep = integrity_checks(p)
        self.assertTrue(any("duplicate episode" in x for x in rep["problems"]))

    def test_cluster_mismatch_rejected(self):
        p = payload()
        bad = row("s|t1|c1|R1", "tX", "cY", "train", "R1", 1, 1)
        p["runs"][0]["rows"].append(bad)
        rep = integrity_checks(p)
        self.assertTrue(any("metadata mismatch" in x for x in rep["problems"]))

    def test_bootstrap_and_signflip_reproducible(self):
        t1 = endpoint_table(payload())
        t2 = endpoint_table(payload())
        self.assertEqual(t1["ci95"], t2["ci95"])
        self.assertEqual(t1["signflip_p"], t2["signflip_p"])

    def test_signflip_is_monte_carlo_not_z(self):
        """signflip_p must be a grid value of the form (k+1)/(reps+1) up to the
        6-decimal rounding applied in the output."""
        from condrec_analysis import SIGNFLIP_REPS
        t = endpoint_table(payload())
        grid_value = t["signflip_p"] * (SIGNFLIP_REPS + 1)
        self.assertAlmostEqual(grid_value, round(grid_value), delta=0.01)


class SafetyEndpointTests(unittest.TestCase):
    def test_r3_r4_independent(self):
        p = payload()
        r3 = safety_endpoint(p, "R3", "x", "AB")
        r4 = safety_endpoint(p, "R4", "x", "AB")
        self.assertEqual(r3["n_eligible_clusters"], 2)  # t2|c1 and t1|c3
        self.assertEqual(r4["n_eligible_clusters"], 1)  # t2|c2
        self.assertEqual(r3["n_episodes"], 4)  # 2 clusters x 2 seeds


class NoHardcodingTests(unittest.TestCase):
    def test_program_contains_no_summary_constants(self):
        src = Path(__file__).parent / "condrec_analysis.py"
        text = src.read_text(encoding="utf-8")
        for banned in ("0.3175", "0.3189", "0.1049", "0.5582", "0.2407"):
            self.assertNotIn(banned, text, f"hardcoded summary {banned} found in program")

    def test_real_data_full_regression(self):
        real = Path(__file__).parent / "diagnostic3_results.json"
        if not real.exists():
            self.skipTest("real artifact missing")
        rep = analyze(real)
        p = rep["primary"]
        self.assertEqual(rep["integrity_checks"]["problems"], [])
        self.assertEqual(p["primary_eligible_clusters"], 42)
        self.assertEqual(p["zero_denominator_clusters"], 12)
        self.assertGreater(p["mean_paired_diff"], 0)
        self.assertGreater(p["ci95"][0], 0)          # CI excludes 0
        self.assertLess(p["signflip_p"], 0.05)
        self.assertAlmostEqual(p["pairing_completeness"], 1.0)
        # consistency with scenario-weighted sensitivity
        self.assertLess(abs(p["mean_paired_diff"] - p["scenario_weighted_diff"]), 0.05)
        # R3/R4 keep independent denominators
        self.assertGreater(rep["safety_r3"]["AB"]["n_eligible_clusters"], 0)
        self.assertGreater(rep["safety_r4"]["AB"]["n_eligible_clusters"], 0)
        # input hash recorded
        self.assertEqual(len(rep["input_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
