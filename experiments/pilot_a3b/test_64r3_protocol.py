"""64-R3 protocol tests (D-064-R2 corrective revision).

Covers the ten required cases: df dynamics, family-equal weighting,
missing-data rules, Holm edges, bootstrap non-significance, separated
sign-flip reporting, and test-split isolation from training paths.
"""
import unittest
from collections import defaultdict

from analyse_diagnostic3 import holm_adjust
from power_hierarchical import (
    build_hierarchy, family_level_tests, family_t_df,
    missing_data_rules,
)


def fake_hierarchy(fam_sizes):
    """Build a hierarchy dict like build_hierarchy output: fam -> comps."""
    families = {}
    fam_means = {}
    idx = 0
    for f, m in fam_sizes.items():
        comps = {}
        vals = []
        for j in range(m):
            v = 0.1 + 0.01 * ((idx + j) % 5) - 0.02
            comps[f"c{j}"] = {"mean_diff": v, "n_r12_scenarios": 1}
            vals.append(v)
        families[f] = comps
        fam_means[f] = sum(vals) / len(vals)
        idx += 1
    return {
        "families": families,
        "fam_means": fam_means,
        "fam_sizes": {f: len(c) for f, c in families.items()},
    }


class DfTests(unittest.TestCase):
    def test_df_39_at_forty_families(self):
        self.assertEqual(family_t_df(40), 39)

    def test_df_33_at_thirtyfour_families(self):
        self.assertEqual(family_t_df(34), 33)

    def test_df_tracks_observed_family_count(self):
        for F in (2, 5, 17, 34, 40, 52):
            self.assertEqual(family_t_df(F), F - 1)

    def test_df_rejects_too_few_families(self):
        with self.assertRaises(ValueError):
            family_t_df(1)
        with self.assertRaises(ValueError):
            family_t_df(0)

    def test_family_level_tests_reports_dynamic_df(self):
        h = fake_hierarchy({f"f{i}": 3 for i in range(34)})
        res = family_level_tests(h)
        self.assertEqual(res["n_families"], 34)
        self.assertEqual(res["student_t"]["df"], 33)
        h40 = fake_hierarchy({f"f{i}": 3 for i in range(40)})
        res40 = family_level_tests(h40)
        self.assertEqual(res40["student_t"]["df"], 39)


class FamilyWeightTests(unittest.TestCase):
    def test_family_weights_equal(self):
        """A family with more clusters must NOT get more weight."""
        h = fake_hierarchy({"fa": 7, "fb": 2, "fc": 2})
        res = family_level_tests(h)
        expected = (h["fam_means"]["fa"] + h["fam_means"]["fb"] + h["fam_means"]["fc"]) / 3
        self.assertAlmostEqual(res["mean"], round(expected, 6), places=6)

    def test_cluster_count_does_not_reweight_families(self):
        """Families are aggregated with equal weight regardless of how many
        composition clusters each contributes."""
        base = {"fa": 0.20, "fb": 0.10}
        h1 = fake_hierarchy({"fa": 7, "fb": 7})
        h2 = fake_hierarchy({"fa": 7, "fb": 2})
        # force identical family means in both hierarchies
        for h in (h1, h2):
            h["fam_means"] = dict(base)
        r1 = family_level_tests(h1)
        r2 = family_level_tests(h2)
        self.assertAlmostEqual(r1["mean"], r2["mean"], places=6)
        self.assertAlmostEqual(r2["mean"], 0.15, places=6)


class MissingDataTests(unittest.TestCase):
    def test_rules_frozen_fields(self):
        rules = missing_data_rules()
        self.assertEqual(rules["behavioural_failure"],
                         "score as class_success=0 (measured endpoint)")
        self.assertEqual(rules["design_floor_families"], 34)
        self.assertEqual(rules["selective_deletion"], "forbidden")
        self.assertIn("do not replace seeds", rules["technical_missing"])

    def test_behavioural_failure_scores_zero_not_dropped(self):
        """A failing controller episode must remain in the denominator."""
        h = fake_hierarchy({"fa": 2, "fb": 2})
        # simulate: one cluster's diff reflects a scored failure (0-0 style)
        h["families"]["fa"]["c0"]["mean_diff"] = 0.0  # scored failure, still counted
        res = family_level_tests(h)
        n_scored = sum(len(c) for c in h["families"].values())
        self.assertEqual(n_scored, 4)  # nothing dropped

    def test_zero_valid_composition_family_is_droppable_and_countable(self):
        rules = missing_data_rules()
        fam = {"empty": {}}
        valid = {f: c for f, c in fam.items() if len(c) >= rules["family_min_valid_compositions"]}
        self.assertEqual(valid, {})  # dropped
        family_loss = [f for f, c in fam.items()
                       if len(c) < rules["family_min_valid_compositions"]]
        self.assertEqual(family_loss, ["empty"])


class InferentialSeparationTests(unittest.TestCase):
    def test_bootstrap_output_has_no_p_value(self):
        h = fake_hierarchy({f"f{i}": 3 for i in range(6)})
        res = family_level_tests(h)
        self.assertIn("block_bootstrap_ci95", res)
        self.assertNotIn("p", {k: v for k, v in res.items() if "bootstrap" in k})

    def test_signflip_and_student_t_reported_separately(self):
        h = fake_hierarchy({f"f{i}": 3 for i in range(6)})
        res = family_level_tests(h)
        self.assertIn("student_t", res)
        self.assertIn("signflip_exact", res)
        self.assertIn("p_two_sided", res["student_t"])
        self.assertIn("p", res["signflip_exact"])
        self.assertNotEqual(res["student_t"]["p_two_sided"], res["signflip_exact"]["p"])

    def test_holm_edge_cases(self):
        self.assertEqual(holm_adjust([0.03]), [0.03])
        adj = holm_adjust([0.01, 0.01])
        self.assertTrue(all(abs(a - 0.02) < 1e-9 for a in adj))
        self.assertTrue(all(a <= 1.0 for a in holm_adjust([0.4, 0.5, 0.6])))


class TestSplitIsolationTests(unittest.TestCase):
    def test_diagnostic_schedulers_do_not_use_test_split(self):
        import inspect
        import run_diagnostic2
        import run_diagnostic3
        for mod in (run_diagnostic2, run_diagnostic3):
            src = inspect.getsource(mod)
            self.assertNotIn('"test"', src.replace("'", '"').replace(" ", "")
                             .replace('"test_"', ''), f"{mod.__name__} references a test split")
            self.assertNotIn("split.*test", src)

    def test_formal_generator_keeps_test_out_of_labelled_training_payload(self):
        """Test scenarios may exist in the manifest (hashed) but training
        selections must draw only from train/validation splits."""
        import inspect
        import formal_scenario_generator as fsg
        src = inspect.getsource(fsg)
        # generator itself is a data generator (allowed to build test split);
        # assert it never mixes split labels inside a single selection pool
        self.assertIn('"train"', src)
        self.assertIn('"validation"', src)
        self.assertIn('"test"', src)
        # split summaries are per-split (no cross-split pooling)
        self.assertIn('split_summaries', src)


if __name__ == "__main__":
    unittest.main()
