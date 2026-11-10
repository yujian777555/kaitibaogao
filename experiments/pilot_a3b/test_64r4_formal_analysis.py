"""Synthetic-only tests for the R4 family-level confirmatory analysis.

No real Test payload or labels are read by these tests.
"""
import unittest

from formal_analysis import analyze_primary_endpoint as _analyze_primary_endpoint

PROVENANCE = {
    "manifest_sha256": "a" * 64,
    "code_sha256": "b" * 64,
    "git_head": "c" * 40,
    "primary_composition_ids": ["C00", "C01", "C02", "C03", "C04"],
}

def analyze_primary_endpoint(*args, **kwargs):
    kwargs.setdefault("provenance", PROVENANCE)
    kwargs.setdefault("primary_composition_ids", PROVENANCE["primary_composition_ids"])
    return _analyze_primary_endpoint(*args, **kwargs)


METHODS = ("AB", "nsga2")
SEEDS = (11, 22)


def fixture(n_families=34, compositions=5, scenarios_per_composition=2):
    roster = []
    rows = []
    for fi in range(n_families):
        family = f"F{fi:02d}"
        for ci in range(compositions):
            composition = f"C{ci:02d}"
            for si in range(scenarios_per_composition):
                scenario = f"{family}|{composition}|S{si:02d}"
                roster.append({
                    "scenario_id": scenario,
                    "family_id": family,
                    "composition_id": composition,
                    "label": "R1" if si == 0 else "R2",
                    "split": "test",
                })
                for seed in SEEDS:
                    for method in METHODS:
                        rows.append({
                            "scenario_id": scenario,
                            "seed": seed,
                            "method": method,
                            "class_success": 1 if method == "AB" else 0,
                            "split": "test",
                        })
    return roster, rows


class FormalPrimaryAnalysisTests(unittest.TestCase):
    def test_forty_families_with_five_compositions_are_eligible(self):
        roster, rows = fixture(n_families=40)
        result = analyze_primary_endpoint(rows, roster, SEEDS)
        self.assertEqual(result["n_families"], 40)
        self.assertEqual(result["confirmatory_status"], "ELIGIBLE")
        self.assertTrue(all(n == 5 for n in result["family_composition_counts"].values()))
        self.assertAlmostEqual(result["family_equal_weight_effect"], 1.0)
        self.assertEqual(result["student_t"]["df"], 39)

    def test_wrong_primary_composition_roster_fails_closed(self):
        roster, rows = fixture()
        wrong_roster = [dict(item) for item in roster]
        wrong_roster[0]["composition_id"] = "C99"
        with self.assertRaisesRegex(ValueError, "composition IDs do not match"):
            analyze_primary_endpoint(rows, wrong_roster, SEEDS)

    def test_missing_provenance_withholds_confirmatory_inference(self):
        roster, rows = fixture()
        result = _analyze_primary_endpoint(rows, roster, SEEDS)
        self.assertEqual(result["confirmatory_status"], "NOT_ELIGIBLE_PROVENANCE_INCOMPLETE")
        self.assertIsNone(result["student_t"])
        self.assertEqual(result["provenance_status"], "INCOMPLETE")

    def test_fewer_than_34_observed_families_is_underpowered(self):
        roster, rows = fixture(n_families=33)
        result = analyze_primary_endpoint(rows, roster, SEEDS)
        self.assertEqual(result["n_families"], 33)
        self.assertEqual(result["confirmatory_status"], "NOT_ELIGIBLE_UNDERPOWERED")
        self.assertTrue(result["design_deviation"])
        self.assertIsNone(result["student_t"])

    def test_unexplained_missing_run_fails_closed(self):
        roster, rows = fixture()
        rows.pop()
        with self.assertRaisesRegex(ValueError, "unexplained missing"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_technical_missing_is_counted_and_family_is_lost(self):
        roster, rows = fixture()
        missing = rows.pop(0)
        technical = [{
            "scenario_id": missing["scenario_id"],
            "seed": missing["seed"],
            "method": missing["method"],
            "category": "infrastructure",
            "reason": "synthetic runner process terminated",
        }]
        result = analyze_primary_endpoint(rows, roster, SEEDS, technical_missing=technical)
        self.assertEqual(result["technical_missing_runs"], 1)
        self.assertEqual(result["family_loss"], ["F00"])
        self.assertEqual(result["n_families"], 33)
        self.assertTrue(result["design_deviation"])

    def test_labelled_null_fails_closed(self):
        roster, rows = fixture()
        rows[0]["class_success"] = None
        with self.assertRaisesRegex(ValueError, "labelled null"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_duplicate_run_fails_closed(self):
        roster, rows = fixture()
        rows.append(dict(rows[0]))
        with self.assertRaisesRegex(ValueError, "duplicate run"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_unknown_scenario_fails_closed(self):
        roster, rows = fixture()
        rows[0]["scenario_id"] = "not-in-frozen-roster"
        with self.assertRaisesRegex(ValueError, "outside frozen roster"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_behavioral_failure_is_zero_and_kept_in_denominator(self):
        roster, rows = fixture()
        rows[0]["class_success"] = 0
        rows[0]["behavioral_failure"] = True
        result = analyze_primary_endpoint(rows, roster, SEEDS)
        self.assertEqual(result["behavioural_failure_count"], 1)
        self.assertEqual(result["paired_run_count"], len(roster) * len(SEEDS))
        self.assertEqual(result["n_families"], 34)

    def test_behavioral_failure_cannot_have_nonzero_success(self):
        roster, rows = fixture()
        rows[0]["behavioral_failure"] = True
        with self.assertRaisesRegex(ValueError, "behavioral failure must score zero"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_expected_roster_requires_exactly_five_compositions_per_family(self):
        roster, rows = fixture(compositions=4)
        with self.assertRaisesRegex(ValueError, "exactly 5 primary compositions"):
            analyze_primary_endpoint(rows, roster, SEEDS)

    def test_technical_missing_requires_explicit_infrastructure_reason(self):
        roster, rows = fixture()
        missing = rows.pop()
        technical = [{
            "scenario_id": missing["scenario_id"],
            "seed": missing["seed"],
            "method": missing["method"],
            "category": "unknown",
            "reason": "",
        }]
        with self.assertRaisesRegex(ValueError, "technical missing record"):
            analyze_primary_endpoint(rows, roster, SEEDS, technical_missing=technical)


if __name__ == "__main__":
    unittest.main()
