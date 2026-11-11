"""Raw-ledger format and provenance tests for the D-086 runner."""
import gzip
import json
import tempfile
import unittest
from pathlib import Path

from dependency_evolution import EvaluationLedger, evaluate_genome, fingerprint, select_validation
from dependency_experiment import _record, _selection, analyze_runs, write_outputs
from dependency_genome import RecoveryGenome
from test_dependency_evolution import small_train


class ExperimentIOTests(unittest.TestCase):
    def test_jsonl_rows_are_independently_decodable_and_keep_ledger_stats(self):
        scenario = small_train()[0]
        ledger = EvaluationLedger("synthetic", episode_cap=10)
        record = evaluate_genome(RecoveryGenome(), [scenario], ledger)
        selection = select_validation(
            {"archive": [record], "ledger": ledger},
            [dict(scenario, split="validation")],
        )
        run = {
            "arm": "C-NSGA-III",
            "seed": 711,
            "archive": [_record(record)],
            "initial_pool": [fingerprint(record["genome"])],
            "final_population": [_record(record)],
            "history": [],
            "budget_exhausted": False,
            "test_accessed": False,
            "ledger": ledger,
            "selection": _selection(selection),
        }
        analysis = analyze_runs([run])
        with tempfile.TemporaryDirectory() as temp:
            summary = write_outputs([run], analysis, temp)
            with gzip.open(Path(temp) / "d086_experiment_rows.jsonl.gz", "rt", encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle if line.strip()]
            self.assertEqual(len(rows), summary["raw_row_count"])
            self.assertEqual({row["row"]["split"] for row in rows}, {"train", "validation"})
            saved = json.loads((Path(temp) / "d086_experiment_runs.json").read_text(encoding="utf-8"))
            self.assertEqual(
                saved[0]["ledger_stats"]["unique_episode_equivalent"]["train"], 1
            )


if __name__ == "__main__":
    unittest.main()
