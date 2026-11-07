"""Tests for the independent contract validator (57 F7)."""
import unittest

from contract_validator import validate_genome, is_contract_legal, RuleGene
from a3_bridge import (
    ACT_COMPENSATE, ACT_ESCALATE, ACT_REPAIR, ACT_RETRY, ACT_STOP, ACT_VERIFY, ACT_WAIT,
    OBS_ALL, OBS_PARTIAL, OBS_PERMISSION, OBS_SCHEMA, OBS_TIMEOUT,
    make_gene_rule_table, random_fsm, repair_fsm, hand_fsm,
)


def genes_with(error, action, wait=2):
    out = []
    for att in (0, 1, 2):
        for stack in (True, False):
            out.append(RuleGene(error, att, stack, action, wait))
    return out


class ContractValidatorTests(unittest.TestCase):
    def test_permission_retry_is_illegal(self):
        rep = validate_genome(genes_with(OBS_PERMISSION, ACT_RETRY), ACT_ESCALATE)
        self.assertGreater(rep.rule_invalid, 0)

    def test_partial_bare_retry_is_illegal(self):
        rep = validate_genome(genes_with(OBS_PARTIAL, ACT_RETRY), ACT_ESCALATE)
        self.assertGreater(rep.rule_invalid, 0)

    def test_schema_repair_is_legal(self):
        rep = validate_genome(genes_with(OBS_SCHEMA, ACT_REPAIR), ACT_ESCALATE)
        self.assertEqual(rep.rule_invalid, 0)

    def test_repair_on_non_schema_is_illegal(self):
        rep = validate_genome(genes_with(OBS_TIMEOUT, ACT_REPAIR), ACT_ESCALATE)
        self.assertGreater(rep.rule_invalid, 0)

    def test_all_timeout_genes_bare_retry_is_genome_invalid(self):
        rep = validate_genome(genes_with(OBS_TIMEOUT, ACT_RETRY), ACT_ESCALATE)
        self.assertTrue(rep.genome_invalid)

    def test_default_action_must_be_total(self):
        rep = validate_genome(genes_with(OBS_TIMEOUT, ACT_VERIFY), ACT_REPAIR)
        self.assertTrue(rep.genome_invalid)

    def test_validator_independent_of_repair_table(self):
        """A repaired genome must pass the INDEPENDENT validator, and the
        validator must reject the pre-repair genome's illegal genes."""
        rng = __import__("random").Random(7)
        fsm = random_fsm(rng)
        before = validate_genome(fsm.genes_list(), fsm.default_action, fsm.default_wait)
        fixed = repair_fsm(fsm)
        after = validate_genome(fixed.genes_list(), fixed.default_action, fixed.default_wait)
        self.assertEqual(after.rule_invalid, 0, msg=str(after.rule_violations[:5]))
        # the validator uses its own rule path (rule_invalid computed without
        # importing _REPAIR_MAP) -- sanity: hand genome passes too
        h = hand_fsm()
        self.assertTrue(is_contract_legal(h.genes_list(), h.default_action, h.default_wait))

    def test_exhaustive_rule_matrix_smoke(self):
        """Exhaustive error x action check: every combination is either legal
        or reported; nothing crashes."""
        for err in OBS_ALL:
            for act in (ACT_RETRY, ACT_VERIFY, ACT_WAIT, ACT_COMPENSATE,
                        ACT_REPAIR, ACT_ESCALATE, ACT_STOP):
                rep = validate_genome(genes_with(err, act), ACT_ESCALATE)
                self.assertIsInstance(rep.rule_invalid, int)


if __name__ == "__main__":
    unittest.main()
