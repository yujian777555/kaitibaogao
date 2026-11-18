"""D-092 Probe specification and synthetic-environment tests; no 960 execution here."""
from __future__ import annotations

import unittest

from d092_probe import build_execution_lock_payload, p07_trace_prefix_valid, probe_panel_sha256
from d092_runtime import run_guarded_episode
from test_d092_runtime import SequencePolicy


class TestProbeLock(unittest.TestCase):
    def test_lock_is_bound_to_seed_panel_protocol_and_runtime(self):
        runtime = {
            "python_version": "3.11.9",
            "numpy_version": "1.26.4",
            "platform": "Ubuntu 22.04 LTS x86_64",
            "pythonhashseed": "0",
        }
        lock = build_execution_lock_payload(runtime)
        self.assertEqual(lock["seed"], 711)
        self.assertEqual(lock["planned_episodes"], 960)
        self.assertTrue(lock["no_cache"])
        self.assertEqual(lock["runtime"], runtime)
        self.assertEqual(len(lock["probe_genomes"]), 10)
        self.assertEqual(lock["probe_panel_sha256"], probe_panel_sha256())
        self.assertEqual(lock["status"], "LOCKED_BEFORE_ROLLOUT")


class TestP07SyntheticTrace(unittest.TestCase):
    def test_exact_fourteen_action_prefix_uses_real_environment(self):
        scenario = {
            "scenario_id": "synthetic|p07-prefix",
            "split": "train",
            "terminal_fault": "permission",
            "current_tool": "D",
            "tools": [
                {
                    "id": tool,
                    "state": "COMMITTED",
                    "compensation_available": True,
                    "routes": [
                        {
                            "name": "primary",
                            "outcomes": [True] if tool == "A" else [False, True],
                            "cost": 3,
                            "reliability_hint": "HIGH",
                            "requires": {"A": ["B"], "B": ["C"], "C": []}[tool],
                            "receipt": "delayed",
                            "receipt_delay": 2,
                            "idempotent": False,
                            "visibility_bound": 3,
                        },
                        {
                            "name": "alternate",
                            "outcomes": [False, False, True] if tool in ("B", "C") else [True],
                            "cost": 1,
                            "reliability_hint": "LOW",
                            "requires": [],
                            "receipt": "delayed",
                            "receipt_delay": 2,
                            "idempotent": False,
                            "visibility_bound": 3,
                        },
                    ],
                }
                for tool in ("A", "B", "C")
            ] + [{"id": "D", "state": "NOT_COMMITTED", "compensation_available": True, "routes": []}],
        }
        actions = [
            ("COMPENSATE", "C", "primary"),
            ("WAIT",),
            ("VERIFY", "C"),
            ("WAIT",),
            ("WAIT",),
            ("VERIFY", "C"),
            ("COMPENSATE", "C", "primary"),
            ("COMPENSATE", "B", "primary"),
            ("WAIT",),
            ("VERIFY", "B"),
            ("WAIT",),
            ("WAIT",),
            ("VERIFY", "B"),
            ("VERIFY", "C"),
        ]
        report = run_guarded_episode(SequencePolicy(actions), scenario)
        self.assertTrue(p07_trace_prefix_valid(report))
        self.assertEqual(report["decision_count"], 15)
        self.assertEqual(report["transition_records"][13]["after"]["decision_count"], 14)
        self.assertEqual(report["transition_records"][6]["after"]["tools"]["C"]["state"], "COMPENSATED")
        self.assertEqual(report["transition_records"][7]["action"], ["COMPENSATE", "B", "primary"])


if __name__ == "__main__":
    unittest.main()
