"""D-064-C independent audit tests: adversarial semantics, composition
truth-consistency, labeler boundaries and determinism."""
import copy
import json
import unittest

from a3_bridge import scenario_verdict
from formal_scenario_generator import (
    ALLOWED_CLASSES_BY_COMPOSITION, FAULT_COMPOSITION_NOTES, FORMAL_COMPOSITIONS,
    build_candidate_manifest, make_fault_vector, stable_seed,
)
from pilot_a3 import TOOLS
from reachability import classify as robust_classify
from task_semantics import (
    build_task_family, enumerate_primary_compatible_sequences,
    validate_task_family,
)


GOOD_TOOLS = ("calendar", "ledger", "shipment")  # comp, non-comp, non-comp


def good_spec():
    return build_task_family(GOOD_TOOLS)


class AdversarialValidatorTests(unittest.TestCase):
    """D-064-C-1: malicious mutations must all be rejected."""

    def _expect_reject(self, spec, needle):
        res = validate_task_family(spec)
        self.assertFalse(res["ok"], f"validator accepted tampered spec ({needle})")
        self.assertTrue(any(needle in e for e in res["errors"]),
                        f"expected error containing {needle!r}, got {res['errors']}")

    def test_delete_required_precondition(self):
        spec = good_spec()
        spec["steps"][1]["preconditions"] = ["workflow_open"]  # dropped valid payload + predecessor
        self._expect_reject(spec, "precondition")

    def test_modify_postcondition(self):
        spec = good_spec()
        spec["steps"][0]["postconditions"] = ["side_effect_recorded"]  # dropped receipt_emitted
        self._expect_reject(spec, "postcondition")

    def test_replace_tool_mid_sequence(self):
        spec = good_spec()
        spec["steps"][1]["tool"] = "order"
        self._expect_reject(spec, "tool order mismatch")

    def test_tamper_tool_contract(self):
        spec = good_spec()
        spec["steps"][1]["tool_contract"]["compensatable"] = True  # ledger is not compensatable
        self._expect_reject(spec, "contract mismatch")

    def test_forge_effect_receipt(self):
        spec = good_spec()
        spec["steps"][2]["outputs"]["commit_status"] = "PARTIAL"
        self._expect_reject(spec, "EffectReceipt")

    def test_modify_predecessor_receipt(self):
        spec = good_spec()
        spec["steps"][2]["required_predecessor"]["producer"] = "calendar"
        self._expect_reject(spec, "predecessor")

    def test_break_compensation_order(self):
        spec = good_spec()
        spec["compensation_order"] = "forward_commit_order"
        self._expect_reject(spec, "reverse commit order")

    def test_modify_task_goal(self):
        spec = good_spec()
        spec["goal"]["predicate"] = "any_step_committed"
        self._expect_reject(spec, "goal")

    def test_inject_duplicate_tool(self):
        spec = good_spec()
        spec["tools"] = ["calendar", "calendar", "shipment"]
        self._expect_reject(spec, "at most once")

    def test_tamper_primary_compatible_flag(self):
        """A family with non-compensatable first step must not pass the
        primary-compatible requirement even if requested."""
        spec = build_task_family(("ledger", "calendar", "shipment"))
        res = validate_task_family(spec, require_primary_support=True)
        self.assertFalse(res["ok"])
        self.assertTrue(any("compensatable first step" in e for e in res["errors"]))

    def test_spoof_legacy_flag_with_wrong_id(self):
        spec = good_spec()
        spec["family_id"] = "fake_legacy_id"
        spec["legacy_task_family"] = True
        self._expect_reject(spec, "family_id does not match")

    def test_payload_type_tamper(self):
        spec = good_spec()
        spec["initial_context"]["payload_types"] = ["X", "Y", "Z"]
        self._expect_reject(spec, "payload types")


class CompositionTruthTests(unittest.TestCase):
    """D-064-C-2: declared note vs actual injection vs labels consistency."""

    def test_all_compositions_have_notes(self):
        for c in FORMAL_COMPOSITIONS:
            self.assertIn(c, FAULT_COMPOSITION_NOTES)

    def test_permission_prefix_injection_matches_note(self):
        """The permission composition must inject a permission fault after a
        compensatable prefix; the note must not describe stale triple faults."""
        faults = make_fault_vector(GOOD_TOOLS, "permission_after_compensatable_prefix",
                                   stable_seed("x", "p"), stable_seed("x", "q"))
        types = [f["fault"] for f in faults]
        self.assertEqual(types[1], "permission_denied")
        note = FAULT_COMPOSITION_NOTES["permission_after_compensatable_prefix"]
        self.assertNotIn("delayed visibility, rate limit", note,
                         "stale triple-fault description contradicts actual injection")

    def test_permission_prefix_step0_compensatable_in_all_families(self):
        """R3 label premise: the committed prefix must be compensatable."""
        manifest, extras = build_candidate_manifest()
        bad = [s["scenario_id"] for s in extras["development_scenarios"]
               if s["composition"] == "permission_after_compensatable_prefix"
               and not TOOLS[s["tools"][0]]["compensatable"]]
        self.assertEqual(bad, [])

    def test_labels_within_allowed_sets_and_predictable(self):
        manifest, extras = build_candidate_manifest()
        for s in extras["development_scenarios"]:
            self.assertIn(s["label"], ALLOWED_CLASSES_BY_COMPOSITION[s["composition"]],
                          s["scenario_id"])
            self.assertIn(s["analytic_label"],
                          ALLOWED_CLASSES_BY_COMPOSITION[s["composition"]])

    def test_partial_comp_failure_label_is_r4(self):
        for seed in range(6):
            faults = make_fault_vector(GOOD_TOOLS, "partial_comp_failure",
                                       seed, seed + 100)
            s = {"tools": GOOD_TOOLS, "faults": faults}
            self.assertEqual(scenario_verdict(s)["class"], "R4")

    def test_r4_primary_composition_roster_is_frozen_outcome_blind(self):
        manifest, extras = build_candidate_manifest()
        power = manifest["power_design_candidate"]
        primary = power["primary_analysis_composition_ids"]
        sensitivity = power["sensitivity_only_primary_eligible_composition_ids"]
        self.assertEqual(len(primary), 5)
        self.assertEqual(len(set(primary)), 5)
        self.assertEqual(set(primary), {
            "single_timeout",
            "timeout_then_rate_limit",
            "partial_then_delay",
            "independent_mixed_val",
            "triple_mixed",
        })
        self.assertEqual(set(sensitivity), {
            "schema_then_timeout",
            "partial_then_timeout_val",
        })
        self.assertEqual(power["test_primary_analysis_clusters"], 200)
        self.assertIn("outcome-blind", power["primary_analysis_selection_rule"])
        self.assertNotIn("test_scenarios", extras)

    def test_no_hardcoded_labels_in_scenarios(self):
        """Labels must come from the labeler, not scenario_id text or constants."""
        manifest, extras = build_candidate_manifest()
        self.assertNotIn("all_scenarios", extras)
        self.assertNotIn("test_scenarios", extras)
        self.assertNotIn("split_internal", extras)
        self.assertNotIn("scenarios", manifest["splits"]["test_locked"])
        for s in extras["development_scenarios"][:30]:
            self.assertIn("label_evidence_sha256", s)
            self.assertIn("labeler", s)
            # label must not appear as an id path segment (repeat digits like
            # 'r1' may coincidentally match 'R1' as a substring)
            self.assertNotIn(s["label"], s["scenario_id"].split("|"))


class LabelerBoundaryTests(unittest.TestCase):
    """D-064-C-3: robust checker vs analytic labels at boundaries."""

    def test_unknown_not_forced(self):
        """If the robust checker cannot prove a class within resources the
        result must be UNKNOWN, never a forced lower class."""
        from reachability import CLS_UNKNOWN
        from mini_env import all_specs
        spec = {s.name: s for s in all_specs()}["c10_depth_exceeded"]
        got = robust_classify(spec, horizon=3)
        self.assertEqual(got.label, CLS_UNKNOWN)

    def test_analytic_and_robust_agree_on_ground_truth_cases(self):
        from mini_env import all_specs
        agreed = 0
        for s in all_specs():
            got = robust_classify(s, horizon=12)
            if got.label == s.expected_class:
                agreed += 1
        self.assertGreaterEqual(agreed, 10, "mini-env ground truth mostly agreed")

    def test_noncompensatable_partial_is_r4_not_r3(self):
        s = {"tools": ("ledger", "calendar", "shipment"),
             "faults": [{"fault": "partial_commit", "delay": 0, "retry_after": 0,
                         "compensation_available": False},
                        {"fault": "none", "delay": 0, "retry_after": 0,
                         "compensation_available": True},
                        {"fault": "none", "delay": 0, "retry_after": 0,
                         "compensation_available": False}]}
        self.assertEqual(scenario_verdict(s)["class"], "R4")


class DeterminismTests(unittest.TestCase):
    """D-064-C-5: independent rebuild must reproduce identical hashes."""

    def test_stable_seed_deterministic_and_split_specific(self):
        self.assertEqual(stable_seed(1, "a", "b"), stable_seed(1, "a", "b"))
        self.assertNotEqual(stable_seed(1, "train", "f"), stable_seed(1, "test", "f"))

    def test_independent_rebuild_reproduces_manifest_hash(self):
        m1, _ = build_candidate_manifest()
        m2, _ = build_candidate_manifest()
        self.assertEqual(m1["manifest_sha256"], m2["manifest_sha256"])
        self.assertEqual(m1["hashes"], m2["hashes"])
        self.assertEqual(m1["hashes"]["test_family_sha256"],
                         "01b41df8b06c318f90a4fc7aed45f673d13b50f14c08f56304ddffbb625a1411")
        self.assertEqual(m1["hashes"]["test_scenario_sha256"],
                         "dded3bb72a08143177dd6b7f5c4c4ef5100b547028c9cc40fa2b87b6bd70c919")

    def test_tampering_changes_hash(self):
        m1, extras = build_candidate_manifest()
        payload = json.dumps(m1["splits"], sort_keys=True)
        mutated = payload.replace('"R1"', '"R2"', 1)
        from formal_scenario_generator import sha256_json
        self.assertNotEqual(sha256_json(json.loads(payload)), sha256_json(json.loads(mutated)))

    def test_scenario_ids_unique(self):
        manifest, extras = build_candidate_manifest()
        ids = [s["scenario_id"] for s in extras["development_scenarios"]]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
