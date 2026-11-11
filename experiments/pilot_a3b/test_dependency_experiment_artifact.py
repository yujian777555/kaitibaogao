"""Saved D-086 experiment artifact and independent-analysis tests."""
import hashlib
import json
import unittest
from pathlib import Path

from dependency_experiment_audit import OUTDIR, audit_artifact


class ExperimentArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit_artifact(OUTDIR)

    def test_independent_audit_passes(self):
        self.assertTrue(self.report["ok"], self.report)
        self.assertEqual(self.report["run_count"], 40)
        self.assertEqual(self.report["optimizer_runs_in_audit"], 0)
        self.assertFalse(self.report["test_accessed"])

    def test_artifact_manifest_hashes_match(self):
        path = OUTDIR / "d086_experiment_artifact_manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        for filename, expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((OUTDIR / filename).read_bytes()).hexdigest(), expected)

    def test_decision_is_exploratory_not_confirmation(self):
        summary = json.loads((OUTDIR / "d086_experiment_summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "EXPLORATORY_RESULTS_NOT_CONFIRMATION")
        self.assertIn(summary["analysis"]["status"], {"NO_GO", "CANDIDATE_IMPROVEMENT_EXPLORATORY"})
        self.assertFalse(summary["test_accessed"])


if __name__ == "__main__":
    unittest.main()
