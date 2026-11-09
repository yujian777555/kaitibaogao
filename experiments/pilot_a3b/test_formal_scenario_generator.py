import unittest

from formal_scenario_generator import (
    EXPECTED_LABELS,
    FORMAL_COMPOSITIONS,
    SEED_BASE,
    _build_cluster,
    make_fault_vector,
    stable_seed,
)
from task_semantics import build_split_catalog


class FormalScenarioGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.family = build_split_catalog()["train"][0]
        cls.tools = tuple(cls.family["tools"])

    def test_nine_compositions_are_frozen(self):
        self.assertEqual(len(FORMAL_COMPOSITIONS), 9)
        self.assertEqual(len(EXPECTED_LABELS), 9)

    def test_all_fault_vectors_align_with_three_tools(self):
        for composition in FORMAL_COMPOSITIONS:
            faults = make_fault_vector(self.tools, composition, 11, 29)
            self.assertEqual(len(faults), 3)
            for fault in faults:
                self.assertIn(fault["fault"], {
                    "none", "timeout_before", "timeout_after", "delayed_visibility",
                    "partial_commit", "rate_limit", "schema_drift", "permission_denied",
                })
                self.assertGreaterEqual(fault["delay"], 0)
                self.assertGreaterEqual(fault["retry_after"], 0)

    def test_pattern_is_constant_across_nested_repeats(self):
        family_id = self.family["family_id"]
        comp = "single_timeout"
        pattern_seed = stable_seed(SEED_BASE, "train", family_id, comp, "pattern")
        rows = [
            make_fault_vector(
                self.tools, comp, pattern_seed,
                stable_seed(SEED_BASE, "train", family_id, comp, rep),
            )
            for rep in range(3)
        ]
        self.assertEqual(
            [[f["fault"] for f in row] for row in rows],
            [[f["fault"] for f in row] for row in rows[:1]] * 3,
        )

    def test_seed_derivation_is_stable_and_split_specific(self):
        a = stable_seed(SEED_BASE, "train", "family", "comp", 0)
        b = stable_seed(SEED_BASE, "train", "family", "comp", 0)
        c = stable_seed(SEED_BASE, "test", "family", "comp", 0)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_expected_label_contracts_and_analytic_crosscheck(self):
        expected = {
            "single_timeout": "R1",
            "timeout_then_rate_limit": "R1",
            "partial_then_delay": "R2",
            "schema_then_timeout": "R1",
            "independent_mixed_val": "R1",
            "partial_then_timeout_val": "R2",
            "partial_comp_failure": "R4",
            "delay_rate_permission": "R3",
            "triple_mixed": "R1",
        }
        self.assertEqual(EXPECTED_LABELS, expected)
        for composition, expected_label in expected.items():
            cluster, scenarios, problems = _build_cluster(
                self.family, "train", composition
            )
            self.assertFalse(problems, problems)
            self.assertEqual(cluster["label"], expected_label)
            self.assertEqual(cluster["analytic_label"], expected_label)
            self.assertTrue(cluster["label_agreement"])
            self.assertEqual(len(scenarios), 3)
            self.assertEqual({s["label"] for s in scenarios}, {expected_label})

    def test_partial_compensation_failure_is_not_assumed_successful(self):
        faults = make_fault_vector(self.tools, "partial_comp_failure", 11, 29)
        partial_idx = next(i for i, f in enumerate(faults) if f["fault"] == "partial_commit")
        self.assertFalse(faults[partial_idx]["compensation_available"])

    def test_primary_composition_denominator_is_seven_of_nine(self):
        eligible = sum(
            1 for name, label in EXPECTED_LABELS.items() if label in ("R1", "R2")
        )
        self.assertEqual(eligible, 7)


if __name__ == "__main__":
    unittest.main()
