"""Synthetic end-to-end tests for the R4 formal analysis runner.

No real Test manifest payload, labels, or outcomes are used.
"""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from formal_runner import _code_sha256, run_formal_analysis, write_formal_analysis_outputs
from split_access import execute_final_evaluation_once


SEEDS = (411, 522)
COMPOSITIONS = tuple(f"C{i:02d}" for i in range(5))
METHODS = ("AB", "nsga2", "A", "AwaitSLA", "AwaitFixed")
GIT_HEAD = "c" * 40


def manifest_hash(manifest):
    value = {k: v for k, v in manifest.items() if k != "manifest_sha256"}
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_manifest():
    manifest = {
        "schema_version": "synthetic-r4-runner",
        "power_design_candidate": {
            "primary_analysis_composition_ids": list(COMPOSITIONS),
        },
        "splits": {"test_locked": {"payload_disclosed": False}},
    }
    manifest["manifest_sha256"] = manifest_hash(manifest)
    return manifest


def make_fixture(n_families=34):
    roster = []
    runs = []
    for method in METHODS:
        for seed in SEEDS:
            rows = []
            for fi in range(n_families):
                family = f"F{fi:02d}"
                for ci, composition in enumerate(COMPOSITIONS):
                    for si in range(2):
                        sid = f"{family}|{composition}|S{si}"
                        if method in ("AB", "nsga2") and fi == 0 and ci == 0 and si == 0 and seed == SEEDS[0]:
                            roster.append({
                                "scenario_id": sid,
                                "family_id": family,
                                "composition_id": composition,
                                "label": "R1",
                                "split": "test",
                            })
                        value = int((fi + ci + si + len(method)) % 3 != 0)
                        if method == "AB":
                            value = 1
                        rows.append({
                            "scenario_id": sid,
                            "split": "test",
                            "family_id": family,
                            "composition_id": composition,
                            "label": "R1",
                            "class_success": value,
                        })
            runs.append({"method": method, "seed": seed, "rows": rows})
    # Add every scenario to the roster, not just the first run's marker.
    roster = []
    for fi in range(n_families):
        for ci, composition in enumerate(COMPOSITIONS):
            for si in range(2):
                roster.append({
                    "scenario_id": f"F{fi:02d}|{composition}|S{si}",
                    "family_id": f"F{fi:02d}",
                    "composition_id": composition,
                    "label": "R1" if si == 0 else "R2",
                    "split": "test",
                })
    return make_manifest(), {"kind": "SYNTHETIC_R4_RUNNER", "runs": runs}, roster


class FormalRunnerTests(unittest.TestCase):
    def _run_synthetic(self, manifest, ledger, roster):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "one-time.json"
            code_sha = _code_sha256()
            approvals = {
                "status": "APPROVED",
                "independent_review_status": "ACCEPTED",
                "advisor_mde_approved": True,
                "user_approved": True,
                "ci_conclusion": "success",
                "tests_passed": True,
                "manifest_sha256": manifest["manifest_sha256"],
                "code_sha256": code_sha,
            }
            preflight = {"phase": "PRE_RUN_AUTHORIZATION", "status": "GO"}
            evaluated_ledger, receipt = execute_final_evaluation_once(
                ledger_path, approvals, preflight,
                manifest["manifest_sha256"], manifest["manifest_sha256"],
                code_sha, code_sha,
                payload_loader=lambda: {"synthetic_test_sentinel": True},
                evaluator=lambda _payload: ledger,
            )
            return run_formal_analysis(
                manifest, evaluated_ledger, roster, SEEDS, git_head=GIT_HEAD,
                test_execution_receipt=receipt,
            )

    def test_ledger_to_family_primary_secondary_and_provenance(self):
        manifest, ledger, roster = make_fixture()
        result = self._run_synthetic(manifest, ledger, roster)
        self.assertEqual(result["runner_version"], "d064-r4-formal-runner-v1")
        self.assertEqual(result["primary"]["n_families"], 34)
        self.assertEqual(result["post_run_integrity"]["status"], "GO")
        self.assertTrue(result["post_run_integrity"]["analysis_eligible"])
        self.assertEqual(result["primary"]["student_t"]["df"], 33)
        self.assertEqual(result["primary"]["confirmatory_status"], "ELIGIBLE")
        self.assertEqual(result["secondary"]["hypothesis_count"], 4)
        self.assertTrue(result["secondary"]["all_exploratory"])
        self.assertEqual(len(result["family_rosters"]), 34)
        self.assertEqual(len(result["family_rosters"]["F00"]["roster_sha256"]), 64)
        self.assertEqual(result["provenance"]["git_head"], GIT_HEAD)
        self.assertEqual(result["provenance"]["manifest_sha256"], manifest["manifest_sha256"])
        self.assertEqual(len(result["provenance"]["code_sha256"]), 64)
        self.assertEqual(result["provenance"]["primary_composition_ids"], list(COMPOSITIONS))
        self.assertEqual(result["data_access"], "caller_supplied_synthetic_or_unlocked_ledger")

    def test_manifest_hash_mismatch_fails_closed(self):
        manifest, ledger, roster = make_fixture()
        manifest["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "manifest hash"):
            self._run_synthetic(manifest, ledger, roster)

    def test_labelled_null_fails_closed_through_runner(self):
        manifest, ledger, roster = make_fixture()
        ledger["runs"][0]["rows"][0]["class_success"] = None
        with self.assertRaisesRegex(ValueError, "labelled null"):
            self._run_synthetic(manifest, ledger, roster)

    def test_wrong_composition_roster_fails_closed(self):
        manifest, ledger, roster = make_fixture()
        for item in roster:
            if item["composition_id"] == "C00":
                item["composition_id"] = "C99"
        with self.assertRaisesRegex(ValueError, "composition IDs"):
            self._run_synthetic(manifest, ledger, roster)

    def test_explicit_technical_missing_is_counted_without_replacement(self):
        manifest, ledger, roster = make_fixture()
        removed = None
        for run in ledger["runs"]:
            if run["method"] == "AB" and run["seed"] == SEEDS[0]:
                removed = run["rows"].pop(0)
                break
        self.assertIsNotNone(removed)
        ledger["technical_missing"] = [{
            "method": "AB", "seed": SEEDS[0], "scenario_id": removed["scenario_id"],
            "category": "infrastructure", "reason": "synthetic process crash",
        }]
        result = self._run_synthetic(manifest, ledger, roster)
        self.assertEqual(result["primary"]["technical_missing_runs"], 1)
        self.assertEqual(result["primary"]["family_loss"], ["F00"])
        self.assertEqual(result["primary"]["n_families"], 33)
        self.assertEqual(result["primary"]["confirmatory_status"], "NOT_ELIGIBLE_UNDERPOWERED")
        self.assertIsNone(result["primary"]["student_t"])

    def test_duplicate_ledger_run_fails_closed(self):
        manifest, ledger, roster = make_fixture()
        ledger["runs"][0]["rows"].append(dict(ledger["runs"][0]["rows"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate run"):
            self._run_synthetic(manifest, ledger, roster)

    def test_report_outputs_contain_real_results(self):
        manifest, ledger, roster = make_fixture()
        result = self._run_synthetic(manifest, ledger, roster)
        with tempfile.TemporaryDirectory() as tmp:
            json_path, markdown_path = write_formal_analysis_outputs(result, tmp)
            saved = json.loads(Path(json_path).read_text(encoding="utf-8"))
            self.assertEqual(saved["primary"]["n_families"], 34)
            report = Path(markdown_path).read_text(encoding="utf-8")
            self.assertIn("family-level", report)
            self.assertIn("H2-H5", report)
            self.assertIn("exploratory", report)


if __name__ == "__main__":
    unittest.main()
