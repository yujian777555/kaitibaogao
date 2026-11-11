"""Isolation, lock, and reachability evidence tests for the D-085 candidate."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path

from prefix_challenge_generator import (
    LOCK_PATH,
    MANIFEST_PATH,
    STRATA,
    build_prefix_manifest,
    make_manifest_lock,
    validate_manifest_lock,
    validate_prefix_manifest,
)
from prefix_mechanism_audit import audit_prefix_mechanisms, write_audit_outputs

ROOT = Path(__file__).resolve().parents[2]
D079_MANIFEST = ROOT / "experiments/pilot_a3b/results/d079_challenge_v2/d079_challenge_manifest.json"


class PrefixChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_prefix_manifest()
        cls.d079 = json.loads(D079_MANIFEST.read_text(encoding="utf-8"))

    def test_development_partition_is_deterministic_and_disjoint(self):
        self.assertEqual(self.manifest, build_prefix_manifest())
        self.assertEqual(self.manifest["scenario_count"], 96)
        self.assertEqual(self.manifest["scenario_counts"], {"train": 72, "validation": 24})
        self.assertEqual(self.manifest["family_counts"], {"train": 6, "validation": 2})
        train = set(self.manifest["allocation"]["train"])
        validation = set(self.manifest["allocation"]["validation"])
        self.assertFalse(train & validation)
        self.assertEqual(self.manifest["test_included"], False)
        self.assertEqual(self.manifest["test_outcomes_read"], False)
        self.assertEqual(self.manifest["test_protocol"]["status"], "SEALED_NOT_GENERATED_OR_READ")
        self.assertTrue(self.manifest["test_protocol"]["family_roster"].startswith("OPEN_"))

    def test_all_strata_have_reachable_decisive_labels(self):
        self.assertEqual(len(STRATA), 4)
        self.assertTrue(validate_prefix_manifest(self.manifest)["ok"])
        for split in ("train", "validation"):
            rows = [row for row in self.manifest["scenarios"] if row["split"] == split]
            self.assertEqual({row["label"] for row in rows}, {"R1", "R2", "R3", "R4"})
            self.assertEqual({row["difficulty_stratum"] for row in rows}, set(STRATA))
            self.assertEqual(len({row["scenario_id"] for row in rows}), len(rows))
            self.assertTrue(all(row["label"] == row["analytic_label"] for row in rows))
        for row in self.manifest["scenarios"]:
            if row["difficulty_stratum"] == "P2_PERMISSION_COMPENSATION_UNAVAILABLE":
                self.assertEqual(row["label"], "R4")
                self.assertGreater(row["min_reachable_harm"], 0)
                denied = next(i for i, fault in enumerate(row["faults"])
                              if fault["fault"] == "permission_denied")
                self.assertTrue(any(not row["faults"][i]["compensation_available"]
                                    for i in range(denied)))

    def test_d079_diagnostic_is_not_reused(self):
        old = self.d079["scenarios"]
        new = self.manifest["scenarios"]
        self.assertFalse({row["scenario_id"] for row in old} & {row["scenario_id"] for row in new})
        self.assertFalse({row["seed"] for row in old} & {row["seed"] for row in new})
        self.assertFalse(any(row.get("evaluation_role") == "diagnostic" for row in new))
        self.assertTrue(all(row["scenario_id"].startswith("d085|") for row in new))

    def test_tampering_fails_manifest_and_lock_validation(self):
        changed = copy.deepcopy(self.manifest)
        changed["scenarios"][0]["seed"] += 1
        self.assertFalse(validate_prefix_manifest(changed)["ok"])
        with tempfile.TemporaryDirectory() as temp:
            lock_path = Path(temp) / "lock.json"
            lock = make_manifest_lock(self.manifest)
            lock["manifest_sha256"] = "0" * 64
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            self.assertFalse(validate_manifest_lock(self.manifest, lock_path)["ok"])
            self.assertFalse(validate_manifest_lock(self.manifest, Path(temp) / "missing.json")["ok"])

    def test_saved_development_manifest_and_lock_match(self):
        saved = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertTrue(LOCK_PATH.is_file())
        self.assertEqual(saved, self.manifest)
        self.assertTrue(validate_manifest_lock(saved, LOCK_PATH)["ok"])


class PrefixMechanismAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary, cls.rows = audit_prefix_mechanisms(str(D079_MANIFEST))

    def test_raw_rows_reproduce_r3_reachability_and_r4_failure(self):
        self.assertEqual(len(self.rows), 96)
        self.assertEqual(self.summary["optimizer_runs"], 0)
        for method in ("Hand", "PrefixAware"):
            r3 = [row for row in self.rows if row["method"] == method and row["label"] == "R3"]
            r4 = [row for row in self.rows if row["method"] == method and row["label"] == "R4"]
            self.assertEqual(len(r3), 24)
            self.assertEqual(len(r4), 24)
            expected = 0 if method == "Hand" else 24
            self.assertEqual(sum(row["class_success"] for row in r3), expected)
            self.assertEqual(self.summary["methods"][method]["R3"]["class_success_sum"], expected)
            self.assertEqual(sum(row["class_success"] for row in r4), expected)
            self.assertEqual(self.summary["methods"][method]["R4"]["class_success_sum"], expected)
        prefix_r4 = [row for row in self.rows
                     if row["method"] == "PrefixAware" and row["label"] == "R4"]
        self.assertTrue(all(row["active_effects"] == row["min_reachable_harm"] for row in prefix_r4))
        self.assertTrue(all(row["avoidable_harm"] == 0 for row in prefix_r4))
        prefix_r3 = [row for row in self.rows
                     if row["method"] == "PrefixAware" and row["label"] == "R3"]
        self.assertTrue(all(row["active_effects"] == 0 for row in prefix_r3))
        self.assertTrue(all(row["prefix_compensation_success"] == 1 for row in prefix_r3))
        self.assertTrue(all(row["decision_count"] == 2 for row in prefix_r3))

    def test_audit_outputs_are_reproducible_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            first = write_audit_outputs(self.summary, self.rows, temp)
            second = write_audit_outputs(self.summary, self.rows, temp)
            self.assertEqual(first, second)
            with (Path(temp) / "prefix_mechanism_rows.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 96)
            changed = dict(self.summary)
            changed["optimizer_runs"] = 1
            with self.assertRaises(FileExistsError):
                write_audit_outputs(changed, self.rows, temp)

    def test_audit_rejects_a_wrong_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wrong.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit_prefix_mechanisms(str(D079_MANIFEST), lock_path=path)


if __name__ == "__main__":
    unittest.main()
