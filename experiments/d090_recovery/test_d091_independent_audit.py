from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import d091_independent_audit as audit_module
from d091_independent_audit import (
    ARTIFACT_NAMES,
    audit_candidates,
    audit_dispatch,
    audit_metrics,
    audit_sources,
    extract_ablation_failures,
    load_inputs,
    replay_r2_witness,
    run_audit,
    shortest_r2_path,
)


class TestD091IndependentAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.report, cls.ablation = load_inputs()

    def test_source_integrity_and_hashes(self):
        result = audit_sources()
        self.assertEqual(result["status"], "PASS_WITH_LIMITATIONS")
        self.assertEqual(len(result["files"]), 3)
        self.assertTrue(all(item["git_blob_matches"] for item in result["files"]))
        self.assertEqual(len(result["registry_corrections"]), 1)
        correction = result["registry_corrections"][0]
        self.assertEqual(correction["path"], "experiments/d090_recovery/d090_policies.py")
        self.assertTrue(correction["matches_d090_source_commit"])

    def test_source_integrity_without_historical_git_objects(self):
        real_git_blob = audit_module.git_blob

        def shallow_git_blob(path, ref="HEAD"):
            return real_git_blob(path, ref) if ref == "HEAD" else None

        with patch.object(audit_module, "git_blob", side_effect=shallow_git_blob):
            result = audit_sources()
        self.assertEqual(result["status"], "PASS_WITH_LIMITATIONS")
        self.assertEqual(len(result["registry_corrections"]), 1)

    def test_metric_recomputation_and_per_family_counts(self):
        result = audit_metrics(self.manifest, self.report, self.ablation)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["search_run_count"], 15)
        self.assertEqual(result["ablation_variant_count"], 5)
        self.assertEqual(result["saved_search_scenario_rows"], 1440)
        self.assertEqual(result["saved_ablation_scenario_rows"], 480)
        self.assertEqual(result["maximum_absolute_metric_difference"], 0.0)
        self.assertEqual(len(result["per_family_records"]), 480)
        self.assertEqual(len(result["per_scenario_records"]), 1920)

    def test_method_identity_is_not_accepted_from_labels(self):
        result = audit_dispatch(self.report)
        methods = {item["method"]: item for item in result["methods"]}
        self.assertEqual(methods["random"]["actual_search_identity"], "NSGA-II-equivalent")
        self.assertEqual(methods["nsga2"]["actual_search_identity"], "NSGA-II")
        self.assertEqual(methods["nsga3"]["actual_search_identity"], "NSGA-III-simplified")
        self.assertFalse(methods["state_evo"]["dynamic_failure_feedback"])
        self.assertTrue(methods["state_random"]["direct_random_sampling"])
        self.assertEqual(result["operator_invocation_status"], "NOT_AUDITABLE_FROM_SAVED_TRACE")
        self.assertEqual(result["generation_count_status"], "NOT_AUDITABLE_FROM_SAVED_TRACE")

    def test_candidate_genotype_and_phenotype_diversity(self):
        result = audit_candidates(self.report)
        self.assertEqual(result["candidate_count"], 15)
        self.assertEqual(result["unique_genome_count"], 8)
        self.assertEqual(result["unique_trace_phenotype_count"], 1)
        self.assertEqual(result["unique_outcome_signature_count"], 1)
        self.assertEqual(result["pairwise_equivalent_count"], 105)
        self.assertEqual(result["observed_behavior_changing_loci"], [])
        self.assertEqual(len(result["pairwise_records"]), 105)

    def test_ablation_failure_and_hard_constraint_extraction(self):
        result = extract_ablation_failures(self.ablation)
        self.assertEqual(result["counts"]["P1_pair_race"]["class_failures"], 17)
        self.assertEqual(result["counts"]["P2_exhaustive_fallback"]["constraint_rows"], 2)
        self.assertEqual(result["counts"]["P2_exhaustive_fallback"]["pending_total"], 4)
        self.assertEqual(result["counts"]["P4_harm_order"]["constraint_rows"], 2)
        self.assertEqual(result["counts"]["P4_harm_order"]["pending_total"], 2)
        self.assertEqual(result["counts"]["P3_completion_gate"]["pair_race_r3_failures"], 4)
        self.assertTrue(all(not row["constraint_violation"] for row in result["P1_pair_race"]))

    def test_r2_witness_replays_in_real_environment(self):
        result = replay_r2_witness(self.manifest)
        self.assertEqual(result["scenario_id"], "d090r|train|d090_PAIR_RACE|D3_DEPENDENT_ABORT|r2")
        self.assertEqual(result["decision_count"], 23)
        self.assertEqual(result["class_success"], 1)
        self.assertEqual(result["pending_compensation"], 0)
        self.assertEqual(result["constraint_violation"], 0)
        self.assertEqual(len(result["steps"]), 23)

    def test_r2_bfs_finds_and_proves_shortest_path(self):
        result = shortest_r2_path(self.manifest)
        self.assertEqual(result["status"], "CLAIM_FALSIFIED")
        self.assertLessEqual(result["decision_count"], 23)
        self.assertEqual(result["class_success"], 1)
        self.assertEqual(result["constraint_violation"], 0)
        self.assertEqual(result["pending_compensation"], 0)
        self.assertTrue(result["breadth_first_order"])
        self.assertEqual(result["decision_count"], len(result["path"]))
        self.assertGreater(result["expanded_states"], 0)

    def test_audit_writes_only_new_d091_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = run_audit(directory)
            self.assertTrue(ARTIFACT_NAMES.issubset(outputs))
            for name in ARTIFACT_NAMES:
                self.assertTrue((Path(directory) / name).is_file(), name)
            report = json.loads((Path(directory) / "d091_metric_recompute.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
