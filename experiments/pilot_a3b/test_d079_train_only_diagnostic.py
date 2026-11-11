"""Synthetic/sentinel tests for the locked D-079 Train-only diagnostic runner."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from a3_bridge import hand_fsm
from d079_challenge_generator import build_challenge_manifest
from d079_manifest_lock import build_manifest_lock, write_manifest_lock
from d079_train_only_diagnostic import run_d079_train_only_diagnostic
from sbcg import CandidateRecord


class TrainOnlyDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        manifest = build_challenge_manifest()
        self.manifest_path = root / "d079_challenge_manifest.json"
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        lock = build_manifest_lock(self.manifest_path)
        self.lock_path = write_manifest_lock(lock, root)
        self.outdir = root / "out"

    def tearDown(self):
        self.tmp.cleanup()

    def _record(self, fsm):
        return CandidateRecord(
            fsm=fsm,
            objectives=(0.1, 0.0, 0.1, 0.0, 0.0),
            constraints={"duplicate": 0.0, "sla_violation": 0.0, "invariant_violation": 0.0},
            per_family_condrec={"synthetic-family": 1.0},
            fingerprint="synthetic-selected",
            valid_genome=True,
            metrics={
                "cond_rec": 1.0, "corr_esc": 1.0, "containment": 1.0,
                "avoid_resid": 0.0, "unnec_actions_r12": 0.1,
                "dup": 0.0, "sla_viol": 0.0, "violations": 0.0,
                "rows": [],
            },
            source_split="train",
        )

    def test_tampered_lock_is_rejected_before_search_or_evaluation(self):
        lock = json.loads(self.lock_path.read_text(encoding="utf-8"))
        lock["seed_base"] += 1
        self.lock_path.write_text(json.dumps(lock), encoding="utf-8")
        with patch("d079_train_only_diagnostic.run_sbcg_evolution") as search, \
                patch("d079_train_only_diagnostic.evaluate_sbcg_candidate") as evaluation:
            with self.assertRaisesRegex(ValueError, "lock"):
                run_d079_train_only_diagnostic(
                    self.manifest_path, self.lock_path, self.outdir,
                    seeds=(7,), spec_names=(), pop_size=2, generations=1,
                )
        self.assertEqual(search.call_count, 0)
        self.assertEqual(evaluation.call_count, 0)

    def test_runner_uses_robust_labels_and_separates_search_from_diagnostic(self):
        def fake_record(fsm, scenarios, verdicts, **kwargs):
            scenario_ids = [s["scenario_id"] for s in scenarios]
            self.assertTrue(all("|diagnostic|" in sid for sid in scenario_ids))
            self.assertEqual(verdicts[scenario_ids[0]]["label_source"],
                             "observation-based-AND-OR-robust-reachability")
            return self._record(fsm)

        search_result = {
            "episodes": 2 * 2 * 144,
            "unique_evaluations": 4,
            "cache_hits": 0,
            "evaluation_calls": 4,
            "train_candidate_fsms": [hand_fsm()],
            "final_population": [hand_fsm()],
            "strata": [],
            "mutation_audit": [],
            "history": [],
        }
        with patch("d079_train_only_diagnostic.run_sbcg_evolution", return_value=search_result) as search, \
                patch("d079_train_only_diagnostic.evaluate_sbcg_candidate", side_effect=fake_record):
            result = run_d079_train_only_diagnostic(
                self.manifest_path, self.lock_path, self.outdir,
                seeds=(7,), spec_names=("SBCG-NSGA-III",), pop_size=2, generations=1,
            )
        self.assertEqual(search.call_count, 1)
        search_scenarios = search.call_args.args[1]
        self.assertTrue(all(s["split"] == "train" for s in search_scenarios))
        self.assertTrue(all("|search|" in s["scenario_id"] for s in search_scenarios))
        self.assertEqual(result["run_count"], 1)
        self.assertEqual(result["results"][0]["diagnostic_selection"]["status"], "SELECTED")
        self.assertEqual(result["results"][0]["diagnostic_episodes"], 144)
        self.assertEqual(result["results"][0]["search_episodes"], 576)
        self.assertEqual(result["label_source"], "observation-based-AND-OR-robust-reachability")
        self.assertTrue((self.outdir / "d079_train_only_diagnostic_results.json").exists())
        self.assertTrue((self.outdir / "d079_train_only_diagnostic_report.md").exists())

    def test_diagnostic_selector_rejects_validation_records(self):
        record = self._record(hand_fsm())
        record.source_split = "validation"
        from sbcg import select_train_diagnostic_candidate
        with self.assertRaisesRegex(ValueError, "Train"):
            select_train_diagnostic_candidate([record])

    def test_committed_content_level_lock_schema_is_accepted(self):
        manifest = build_challenge_manifest()
        lock = {
            "lock_schema_version": 1,
            "protocol_id": "D-079",
            "generator_version": manifest["generator_version"],
            "manifest_sha256": manifest["manifest_sha256"],
            "scenario_count": manifest["scenario_count"],
            "cluster_count": manifest["cluster_count"],
            "family_count": manifest["family_count"],
            "train_only": True,
            "validation_included": False,
            "test_included": False,
            "test_outcomes_read": False,
            "role_counts": {"search": 144, "diagnostic": 144},
            "label_counts_by_role": manifest["label_counts_by_role"],
        }
        content_lock_path = Path(self.tmp.name) / "content_lock.json"
        content_lock_path.write_text(json.dumps(lock), encoding="utf-8")
        search_result = {
            "episodes": 576, "unique_evaluations": 4, "cache_hits": 0,
            "evaluation_calls": 4, "train_candidate_fsms": [hand_fsm()],
            "final_population": [hand_fsm()], "strata": [],
            "mutation_audit": [], "history": [],
        }
        with patch("d079_train_only_diagnostic.run_sbcg_evolution", return_value=search_result), \
                patch("d079_train_only_diagnostic.evaluate_sbcg_candidate",
                      side_effect=lambda fsm, scenarios, verdicts, **kwargs: self._record(fsm)):
            result = run_d079_train_only_diagnostic(
                self.manifest_path, content_lock_path, self.outdir,
                seeds=(7,), spec_names=("SBCG-NSGA-III",), pop_size=2, generations=1,
            )
        self.assertEqual(result["run_count"], 1)
        self.assertEqual(result["manifest_sha256"], manifest["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()
