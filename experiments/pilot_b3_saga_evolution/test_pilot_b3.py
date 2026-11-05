import ast
import random
import unittest
from pathlib import Path

from experiments.pilot_b2_multistep_saga.pilot_b2 import Env, TASKS, PROFILES, make_episode
from experiments.pilot_b3_saga_evolution.pilot_b3 import (
    GENE_SIZES, MANUAL_SAGA, MANUAL_SAGA_VERIFY, TRAIN_SEEDS,
    VALIDATION_SEEDS, TEST_SEEDS, EVAL_BUDGET, random_genome,
    repair_contracts, execute_genome, fronts, rank_crowding
)

class PilotB3Tests(unittest.TestCase):
    def test_new_seed_panels_are_disjoint_from_prior_pilots(self):
        prior=set(range(100))|set(range(1000,1160))|set(range(3120,3160))
        self.assertTrue(set(TRAIN_SEEDS).isdisjoint(prior))
        self.assertTrue(set(VALIDATION_SEEDS).isdisjoint(prior))
        self.assertTrue(set(TEST_SEEDS).isdisjoint(prior))
        self.assertTrue(set(TRAIN_SEEDS).isdisjoint(set(TEST_SEEDS)))
        self.assertTrue(set(VALIDATION_SEEDS).isdisjoint(set(TEST_SEEDS)))

    def test_genome_shape_and_contract_repair(self):
        rng=random.Random(31)
        for _ in range(300):
            g=repair_contracts(random_genome(rng))
            self.assertEqual(len(g),len(GENE_SIZES))
            self.assertEqual(g[1],0)
            self.assertEqual(g[4],0)
            self.assertEqual(g[5],0)
            self.assertGreaterEqual(g[6],2)
            self.assertGreaterEqual(g[7],2)
            self.assertEqual(g[8],0)
            self.assertEqual(g[9],1)
            if g[2]==1:self.assertGreaterEqual(g[3],2)

    def test_manual_genomes_are_contract_valid(self):
        self.assertEqual(repair_contracts(MANUAL_SAGA),MANUAL_SAGA)
        self.assertEqual(repair_contracts(MANUAL_SAGA_VERIFY),MANUAL_SAGA_VERIFY)

    def test_manual_saga_has_no_critical_violations_on_small_panel(self):
        rows=[
            execute_genome(make_episode(task,step,profile,seed),MANUAL_SAGA)
            for task in TASKS for step in range(3) for profile in PROFILES
            for seed in range(4000,4005)
        ]
        self.assertEqual(sum(r["invariant_violation"] for r in rows),0)

    def test_genome_executor_does_not_read_hidden_state(self):
        path=Path(__file__).with_name("pilot_b3.py")
        tree=ast.parse(path.read_text(encoding="utf-8"))
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="execute_genome")
        hidden={"current_outcome","current_effects","visibility_delay",
                "current_comp_available","previous_comp_failure_index"}
        for node in ast.walk(fn):
            if isinstance(node,ast.Attribute):self.assertNotIn(node.attr,hidden)
            if isinstance(node,ast.Subscript) and isinstance(node.slice,ast.Constant):
                self.assertNotIn(node.slice.value,hidden)

    def test_nsga2_fronts_and_rank_are_well_formed(self):
        scores=[
            {"invariant_violation":0.0,"task_success":0.70,"tool_actions":4.0,"wait_units":1.0},
            {"invariant_violation":0.0,"task_success":0.70,"tool_actions":3.0,"wait_units":1.0},
            {"invariant_violation":0.1,"task_success":0.80,"tool_actions":2.0,"wait_units":0.0},
        ]
        fs=fronts(scores)
        rank,distance=rank_crowding(scores)
        self.assertEqual(sorted(i for front in fs for i in front),[0,1,2])
        self.assertLess(rank[1],rank[0])
        self.assertEqual(set(distance),{0,1,2})

    def test_fixed_budget_and_seed_protocol(self):
        self.assertEqual(EVAL_BUDGET,160)
        self.assertEqual(TRAIN_SEEDS,tuple(range(4000,4040)))
        self.assertEqual(VALIDATION_SEEDS,tuple(range(4100,4120)))
        self.assertEqual(TEST_SEEDS,tuple(range(4120,4160)))

if __name__=="__main__":
    unittest.main()
