"""Reproducibility tests for the fixed-controller ceiling audit."""
import json
import unittest

from prefix_ceiling_audit import CEILING_PATH, MANIFEST_PATH, audit_fixed_controllers


class PrefixCeilingTests(unittest.TestCase):
    def test_saved_ceiling_audit_is_reproducible_and_has_no_optimizer(self):
        summary, rows = audit_fixed_controllers(MANIFEST_PATH)
        self.assertEqual(len(rows), 192)
        self.assertEqual(summary["optimizer_runs"], 0)
        self.assertFalse(summary["test_accessed"])
        self.assertTrue(summary["ceiling_for_required_behavior"])
        prefix = [row for row in rows if row["method"] == "PrefixAware"]
        self.assertTrue(all(row["class_success"] == 1 for row in prefix))
        self.assertTrue(all(row["avoidable_harm"] == 0 for row in prefix))
        self.assertTrue(all(row["constraint_violation"] == 0 for row in prefix))
        saved = json.loads(CEILING_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, {"summary": summary, "rows": rows})


if __name__ == "__main__":
    unittest.main()
