"""D-094 reproducible synthetic-ablation CLI test; no real API."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestSyntheticCLI(unittest.TestCase):
    def test_cli_writes_reproducible_synthetic_ablation_and_selector_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(__file__).resolve().parent / "run_d094_synthetic.py"
            subprocess.run(
                [sys.executable, str(script), "--outdir", directory],
                check=True,
                capture_output=True,
                text=True,
            )
            ablation = json.loads(
                (Path(directory) / "ablation.json").read_text(encoding="utf-8")
            )
            selectors = json.loads(
                (Path(directory) / "selector_comparison.json").read_text(
                    encoding="utf-8"
                )
            )
            metadata = json.loads(
                (Path(directory) / "metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                set(ablation),
                {
                    "standard",
                    "genome",
                    "phenotype",
                    "feedback",
                    "diversity",
                    "combined",
                },
            )
            self.assertTrue(
                all(row["scope"] == "SYNTHETIC_ONLY" for row in ablation.values())
            )
            self.assertEqual(selectors["standard"]["unique_phenotypes"], 1)
            self.assertEqual(selectors["full"]["unique_phenotypes"], 2)
            self.assertFalse(metadata["api_used"])
            self.assertEqual(metadata["scientific_scope"], "SYNTHETIC_ONLY")


if __name__ == "__main__":
    unittest.main()
