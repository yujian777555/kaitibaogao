"""Synthetic-only R4 tests for actual H2-H5 paired analysis and Holm."""
import unittest

from formal_analysis import analyze_secondary_endpoints as _analyze_secondary_endpoints, holm_adjust

PROVENANCE = {
    "manifest_sha256": "a" * 64,
    "code_sha256": "b" * 64,
    "git_head": "c" * 40,
    "primary_composition_ids": ["C00", "C01", "C02", "C03", "C04"],
}

def analyze_secondary_endpoints(*args, **kwargs):
    kwargs.setdefault("provenance", PROVENANCE)
    kwargs.setdefault("primary_composition_ids", PROVENANCE["primary_composition_ids"])
    return _analyze_secondary_endpoints(*args, **kwargs)


SEEDS = (11, 22)
METHODS = ("AB", "A", "AwaitSLA", "AwaitFixed", "nsga2")


def secondary_fixture(n_families=34):
    roster = []
    rows = []
    for fi in range(n_families):
        family = f"F{fi:02d}"
        for ci in range(5):
            composition = f"C{ci:02d}"
            for si in range(2):
                scenario = f"{family}|{composition}|S{si:02d}"
                roster.append({
                    "scenario_id": scenario,
                    "family_id": family,
                    "composition_id": composition,
                    "label": "R1" if si == 0 else "R2",
                    "split": "test",
                })
                for seed_idx, seed in enumerate(SEEDS):
                    k = fi * 13 + ci * 5 + si * 3 + seed_idx
                    values = {
                        "AB": int((k + 1) % 4 != 0),
                        "A": int(k % 4 == 0),
                        "AwaitSLA": int((k + 2) % 3 != 0),
                        "AwaitFixed": int(k % 3 == 0),
                        "nsga2": int(k % 5 == 0),
                    }
                    for method in METHODS:
                        rows.append({
                            "scenario_id": scenario,
                            "seed": seed,
                            "method": method,
                            "class_success": values[method],
                            "split": "test",
                        })
    return roster, rows


class SecondaryAnalysisTests(unittest.TestCase):
    def test_all_four_secondary_contrasts_are_executed_and_holm_adjusted(self):
        roster, rows = secondary_fixture()
        result = analyze_secondary_endpoints(rows, roster, SEEDS)
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(result["hypothesis_count"], 4)
        self.assertEqual(result["holm_method"], "Holm step-down")
        self.assertEqual(set(result["results"]), {"H2", "H3", "H4", "H5"})
        for hypothesis, item in result["results"].items():
            self.assertEqual(item["classification"], "exploratory")
            self.assertFalse(item["confirmatory"])
            self.assertEqual(item["student_t"]["df"], 33)
            self.assertIsNotNone(item["p_raw"])
            self.assertIsNotNone(item["p_holm_adjusted"])
            self.assertIsNotNone(item["student_t"]["ci95"])

    def test_secondary_contrasts_use_the_prespecified_method_pairs(self):
        roster, rows = secondary_fixture()
        result = analyze_secondary_endpoints(rows, roster, SEEDS)
        expected = {
            "H2": "AB - A",
            "H3": "AwaitSLA - A",
            "H4": "AwaitSLA - AwaitFixed",
            "H5": "AB - AwaitSLA",
        }
        for hypothesis, contrast in expected.items():
            self.assertEqual(result["results"][hypothesis]["primary_contrast"], contrast)

    def test_missing_arm_prevents_partial_holm_family(self):
        roster, rows = secondary_fixture()
        missing = next(
            row for row in rows
            if row["method"] == "A" and row["scenario_id"].startswith("F00|")
        )
        rows.remove(missing)
        technical = [{
            "scenario_id": missing["scenario_id"],
            "seed": missing["seed"],
            "method": missing["method"],
            "category": "infrastructure",
            "reason": "synthetic missing arm",
        }]
        result = analyze_secondary_endpoints(
            rows, roster, SEEDS, technical_missing=technical
        )
        self.assertEqual(result["status"], "NOT_ELIGIBLE")
        self.assertIsNone(result["results"]["H2"]["p_raw"])
        self.assertIsNone(result["results"]["H3"]["p_raw"])
        self.assertIsNotNone(result["results"]["H4"]["p_raw"])
        self.assertIsNotNone(result["results"]["H5"]["p_raw"])
        self.assertTrue(all(
            item["p_holm_adjusted"] is None for item in result["results"].values()
        ))

    def test_holm_adjustment_preserves_input_order_and_monotonicity(self):
        adjusted = holm_adjust([0.01, 0.04, 0.03, 0.002])
        self.assertEqual(adjusted, [0.03, 0.06, 0.06, 0.008])

    def test_holm_rejects_anything_other_than_four_hypotheses(self):
        with self.assertRaisesRegex(ValueError, "exactly four"):
            holm_adjust([0.01, 0.02, 0.03])


if __name__ == "__main__":
    unittest.main()
