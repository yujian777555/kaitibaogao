"""Manifest, reachability, and isolation tests for the D-086 challenge."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from dependency_challenge import (
    LOCK_PATH,
    MANIFEST_PATH,
    STRATA,
    build_manifest,
    make_lock,
    validate_lock,
    validate_manifest,
)
from dependency_recovery import classify_scenario, public_view


class DependencyChallengeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_manifest()

    def test_deterministic_partition_and_no_test_payload(self):
        self.assertEqual(self.manifest, build_manifest())
        self.assertEqual(self.manifest["scenario_count"], 96)
        self.assertEqual(self.manifest["scenario_counts"], {"train": 72, "validation": 24})
        self.assertEqual(self.manifest["family_counts"], {"train": 6, "validation": 2})
        allocation = self.manifest["allocation"]
        self.assertFalse(set(allocation["train"]) & set(allocation["validation"]))
        self.assertFalse(self.manifest["test_included"])
        self.assertFalse(self.manifest["test_outcomes_read"])
        self.assertEqual(self.manifest["test_protocol"]["status"], "SEALED_NOT_GENERATED_OR_READ")
        for row in self.manifest["scenarios"]:
            self.assertIn(row["split"], ("train", "validation"))
            self.assertTrue(row["scenario_id"].startswith("d086|"))
            self.assertNotIn("test", row["split"])

    def test_every_label_and_minimum_harm_recomputes(self):
        for split in ("train", "validation"):
            rows = [row for row in self.manifest["scenarios"] if row["split"] == split]
            self.assertEqual({row["label"] for row in rows}, {"R1", "R2", "R3", "R4"})
            self.assertEqual({row["difficulty_stratum"] for row in rows}, set(STRATA))
        for row in self.manifest["scenarios"]:
            label, minimum = classify_scenario(row)
            self.assertEqual(label, row["label"])
            self.assertEqual(minimum, row["min_reachable_harm"])
            self.assertGreaterEqual(row["min_reachable_harm"], 0)
            self.assertEqual(len({route["name"] for tool in row["tools"] for route in tool["routes"]}), 2)

    def test_dependency_alternate_and_receipt_mechanisms_are_executable_fields(self):
        r3 = [row for row in self.manifest["scenarios"] if row["label"] == "R3"]
        self.assertTrue(any(
            route["requires"]
            for row in r3 for tool in row["tools"] for route in tool["routes"]
        ))
        self.assertTrue(any(
            len(tool["routes"]) > 1
            for row in r3 for tool in row["tools"]
        ))
        self.assertTrue(any(
            route["receipt"] == "delayed" and not route["idempotent"]
            for row in r3 for tool in row["tools"] for route in tool["routes"]
        ))
        self.assertTrue(any(
            route["outcomes"].count(False) > 0
            for row in r3 for tool in row["tools"] for route in tool["routes"]
        ))

    def test_public_view_never_exposes_scenario_or_latent_schedule(self):
        for row in self.manifest["scenarios"]:
            view = public_view(row)
            self.assertNotIn("scenario_id", view)
            self.assertNotIn("seed", view)
            self.assertNotIn("label", view)
            self.assertNotIn("min_reachable_harm", view)
            for tool in view["tools"].values():
                for route in tool["routes"]:
                    self.assertNotIn("outcomes", route)
                    self.assertNotIn("receipt_delay", route)
                    self.assertNotIn("receipt", route)
                    self.assertNotIn("pending_success", route)

    def test_all_recoverable_controls_execute_to_completion(self):
        from dependency_policies import make_policy
        from dependency_recovery import run_episode
        for row in self.manifest["scenarios"]:
            if row["label"] not in ("R1", "R2"):
                continue
            with self.subTest(scenario_id=row["scenario_id"]):
                result = run_episode(make_policy("AdaptiveProbe"), row)
                self.assertEqual(result["class_success"], 1)
                self.assertEqual(result["constraint_violation"], 0)
                self.assertGreater(result["decision_count"], 0)

    def test_manifest_and_lock_tampering_fail_closed(self):
        changed = copy.deepcopy(self.manifest)
        changed["scenarios"][0]["tools"][0]["routes"][0]["outcomes"][0] = False
        self.assertFalse(validate_manifest(changed)["ok"])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "lock.json"
            lock = make_lock(self.manifest)
            lock["manifest_sha256"] = "0" * 64
            path.write_text(json.dumps(lock), encoding="utf-8")
            self.assertFalse(validate_lock(self.manifest, path)["ok"])
            self.assertFalse(validate_lock(self.manifest, Path(temp) / "missing")["ok"])

    def test_saved_manifest_and_lock_match(self):
        saved = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.manifest)
        self.assertTrue(LOCK_PATH.is_file())
        self.assertTrue(validate_lock(saved, LOCK_PATH)["ok"])
        canonical = json.dumps(saved, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        payload = dict(saved)
        stored = payload.pop("manifest_sha256")
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(hashlib.sha256(canonical.encode("utf-8")).hexdigest(), stored)


if __name__ == "__main__":
    unittest.main()
