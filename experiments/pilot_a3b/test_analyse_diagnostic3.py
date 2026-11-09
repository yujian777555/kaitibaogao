"""Independent tests for the diagnostic3 recomputation entry (D-063 Stage 0)."""
import copy
import json
import unittest
from pathlib import Path

from analyse_diagnostic3 import (
    analyze, contrast_stats, holm_adjust, structural_checks, sha256_file,
)


def make_row(sid, split, task, comp, seed, label="R1", cs=1, **kw):
    row = {
        "scenario_id": sid, "split": split, "task": task, "composition": comp,
        "seed": seed, "label": label, "class_success": cs,
        "task_success": cs, "invariant_violation": 0, "downstream_violation": 0,
        "sla_violation": 0, "duplicate": 0, "avoidable_harm": 0,
        "policy_selected_escalation": 0, "decision_count": 4, "active_effects": 0,
    }
    row.update(kw)
    return row


def make_payload(methods=("A", "AB"), seeds=(1, 2)):
    """Synthetic paired payload: 2 tasks x 2 compositions x 2 seeds."""
    runs = []
    for m in methods:
        for s in seeds:
            rows = []
            for ti, task in enumerate(["task_x", "task_y"]):
                for ci, comp in enumerate(["comp_1", "comp_2"]):
                    sid = f"t3train|{task}|{comp}|{s}"
                    cs = 1 if (m == "AB" or ti == 0) else 0
                    rows.append(make_row(sid, "train", task, comp, s, cs=cs))
            runs.append({"method": m, "seed": s, "episodes": len(rows),
                         "rows": rows, "rules": [], "train_metrics": {},
                         "val_metrics": {}, "validator_illegal_ratio": 0.0})
    payload = {"kind": "TEST", "methods": list(methods), "seeds": list(seeds),
               "n_train": 8, "n_val": 0, "runs": runs}
    payload["manifest_sha256"] = "x"
    return payload


class StructuralCheckTests(unittest.TestCase):
    def test_normal_pairing_ok(self):
        rep, problems = structural_checks(make_payload())
        self.assertEqual(problems, [])
        self.assertEqual(rep["n_clusters"], 4)

    def test_missing_arm_detected(self):
        payload = make_payload()
        payload["runs"] = [r for r in payload["runs"]
                           if not (r["method"] == "AB" and r["seed"] == 2)]
        rep, problems = structural_checks(payload)
        self.assertTrue(any("missing arm/seed: AB/2" in p for p in problems))

    def test_duplicate_episode_detected(self):
        payload = make_payload()
        payload["runs"][0]["rows"].append(payload["runs"][0]["rows"][0].copy())
        rep, problems = structural_checks(payload)
        self.assertTrue(any("duplicate episodes" in p for p in problems))

    def test_cluster_mismatch_detected(self):
        payload = make_payload()
        # give AB an extra scenario -> pairing broken
        extra = make_row("t3train|task_z|comp_1|1", "train", "task_z", "comp_1", 1)
        for r in payload["runs"]:
            if r["method"] == "AB" and r["seed"] == 1:
                r["rows"].append(extra)
        rep, problems = structural_checks(payload)
        self.assertTrue(any("pairing broken" in p for p in problems))

    def test_seed_missing_detected(self):
        payload = make_payload()
        payload["seeds"] = [1, 2, 3]
        rep, problems = structural_checks(payload)
        self.assertTrue(any("missing arm/seed" in p and "/3" in p for p in problems))

    def test_split_leakage_detected(self):
        payload = make_payload()
        for r in payload["runs"]:
            r["rows"].append(make_row("t3val|task_x|comp_1|1", "validation", "task_x", "comp_1", r["seed"]))
        rep, problems = structural_checks(payload)
        self.assertTrue(any("split leakage" in p for p in problems))

    def test_wrong_denominator_detected(self):
        payload = make_payload()
        payload["runs"][0]["rows"][0]["class_success"] = None  # labelled row w/o value
        rep, problems = structural_checks(payload)
        self.assertTrue(any("null class_success" in p for p in problems))


class ContrastTests(unittest.TestCase):
    def test_effect_direction_and_pairing(self):
        st = contrast_stats(make_payload(), "AB", "A", scope="all")
        self.assertGreater(st["mean_diff"], 0)
        self.assertEqual(st["n_clusters"], 4)
        self.assertEqual(st["n_seeds_nested"], 2)

    def test_bootstrap_and_signflip_reproducible(self):
        st1 = contrast_stats(make_payload(), "AB", "A")
        st2 = contrast_stats(make_payload(), "AB", "A")
        self.assertEqual(st1["ci95"], st2["ci95"])
        self.assertEqual(st1["signflip_p"], st2["signflip_p"])

    def test_seed_nesting_not_inflated(self):
        """Doubling seeds must NOT halve the p-value as if episodes were
        independent -- cluster unit stays 4."""
        p1 = make_payload(seeds=(1, 2))
        p2 = make_payload(seeds=(1, 2, 3, 4))
        st1 = contrast_stats(p1, "AB", "A")
        st2 = contrast_stats(p2, "AB", "A")
        self.assertEqual(st1["n_clusters"], st2["n_clusters"])

    def test_missing_arm_returns_none(self):
        payload = make_payload()
        payload["runs"] = [r for r in payload["runs"] if r["method"] != "AB"]
        self.assertIsNone(contrast_stats(payload, "AB", "A"))


class HolmTests(unittest.TestCase):
    def test_holm_known_values(self):
        adj = holm_adjust([0.01, 0.04, 0.03])
        self.assertAlmostEqual(adj[0], 0.03)   # 0.01*3
        self.assertAlmostEqual(adj[2], 0.06)   # max(0.03, 0.03*2=0.06)
        self.assertAlmostEqual(adj[1], 0.06)   # max(0.06, 0.04*1)
        self.assertTrue(all(a <= 1.0 for a in adj))

    def test_holm_monotone_in_rank(self):
        pvals = [0.002, 0.019, 0.021, 0.04]
        adj = holm_adjust(pvals)
        order = sorted(range(4), key=lambda i: pvals[i])
        seq = [adj[i] for i in order]
        self.assertEqual(seq, sorted(seq))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(__file__).parent / "_test_fixture.json"
        payload = make_payload()
        self.tmp.write_text(json.dumps(payload), encoding="utf-8")

    def tearDown(self):
        if self.tmp.exists():
            self.tmp.unlink()
        for name in ("diagnostic3_recomputed.json", "diagnostic3_recomputed.csv",
                     "diagnostic3_recomputed_report.md"):
            p = Path(__file__).parent / name
            # only clean test artifacts with TEST kind
            if p.exists() and '"kind": "TEST"' in p.read_text(encoding="utf-8")[:200]:
                p.unlink()

    def test_hash_change_detected(self):
        rep = analyze(self.tmp)
        h1 = rep["input_sha256"]
        self.tmp.write_text(self.tmp.read_text(encoding="utf-8") + " ", encoding="utf-8")
        rep2 = analyze(self.tmp)
        self.assertNotEqual(h1, rep2["input_sha256"])

    def test_manifest_mismatch_flagged(self):
        rep = analyze(self.tmp)
        self.assertFalse(rep["manifest_match"])  # fixture manifest is 'x'

    def test_full_pipeline_runs(self):
        rep = analyze(self.tmp)
        self.assertEqual(rep["kind"], "DIAGNOSTIC3_INDEPENDENT_RECOMPUTATION")
        self.assertTrue(rep["contrasts"])
        keys = {(c["method_a"], c["method_b"], c["scope"]) for c in rep["contrasts"]}
        self.assertIn(("AB", "A", "all"), keys)

    def test_real_diagnostic3_file_structure(self):
        """The real artifact must pass structural checks with zero problems."""
        real = Path(__file__).parent / "diagnostic3_results.json"
        if not real.exists():
            self.skipTest("real artifact not present")
        rep = analyze(real)
        self.assertEqual(rep["blocking_problems"], [], msg=str(rep["blocking_problems"]))
        self.assertTrue(rep["manifest_match"])


if __name__ == "__main__":
    unittest.main()
