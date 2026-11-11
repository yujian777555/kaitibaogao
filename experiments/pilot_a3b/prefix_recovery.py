"""Prefix-aware recovery controller genotype and public prefix semantics.

Only public controller observations and tool contracts are used. The hidden
fault vector, visibility delay, and retry_after values are never in prefix state.
"""
from __future__ import annotations

from a3_bridge import (
    ACT_ESCALATE,
    ACT_RETRY,
    ACT_ROLLBACK,
    ACT_STOP,
    ACT_VERIFY_PREFIX,
    OBS_COMPENSATED,
    OBS_COMP_FAILED,
    OBS_PERMISSION,
    OBS_PREFIX_VERIFIED,
    OBS_START,
    StatefulFSM,
    hand_fsm,
    random_fsm,
)


class PrefixAwareFSM(StatefulFSM):
    """FSM whose prefix genes control compensation-before-escalation order."""

    def __init__(
        self,
        genes,
        default_action_wait,
        sla_aware=False,
        fixed_wait=False,
        *,
        prefix_reverse=True,
        prefix_verify=False,
        prefix_retry_failed=False,
        prefix_stop_action=ACT_ESCALATE,
    ):
        if prefix_stop_action not in (ACT_ESCALATE, ACT_STOP):
            raise ValueError("prefix_stop_action must be ESCALATE or STOP_SAFE")
        super().__init__(genes, default_action_wait, sla_aware, fixed_wait)
        self.prefix_reverse = bool(prefix_reverse)
        self.prefix_verify = bool(prefix_verify)
        self.prefix_retry_failed = bool(prefix_retry_failed)
        self.prefix_stop_action = prefix_stop_action
        self.last_controller_state = None
        self._prefix_verify_pending = False

    @classmethod
    def from_fsm(cls, fsm, **overrides):
        kwargs = {
            "prefix_reverse": getattr(fsm, "prefix_reverse", True),
            "prefix_verify": getattr(fsm, "prefix_verify", False),
            "prefix_retry_failed": getattr(fsm, "prefix_retry_failed", False),
            "prefix_stop_action": getattr(fsm, "prefix_stop_action", ACT_ESCALATE),
        }
        kwargs.update(overrides)
        return cls(
            [gene.clone() for gene in fsm.genes_list()],
            (fsm.default_action, fsm.default_wait),
            fsm.sla_aware,
            fsm.fixed_wait,
            **kwargs,
        )

    def clone(self):
        return PrefixAwareFSM.from_fsm(self)

    def decide(self, state):
        if state.last_obs == OBS_START:
            self._prefix_verify_pending = False
        if state.last_obs == OBS_PERMISSION:
            pending = [
                item for item in state.prefix
                if item["state"] in ("COMMITTED", "PARTIAL") and not item["compensated"]
            ]
            if not pending:
                return self.prefix_stop_action, 2
            if any(item["compensatable"] for item in pending):
                return ACT_ROLLBACK, 2
            return self.prefix_stop_action, 2
        if state.last_obs == OBS_COMPENSATED:
            if state.compensation_scope == "CURRENT":
                self._prefix_verify_pending = False
                return super().decide(state)
            if self.prefix_verify and not self._prefix_verify_pending:
                self._prefix_verify_pending = True
                return ACT_VERIFY_PREFIX, 1
            self._prefix_verify_pending = False
            return self.prefix_stop_action, 2
        if state.last_obs == OBS_PREFIX_VERIFIED:
            self._prefix_verify_pending = False
            return self.prefix_stop_action, 2
        if state.last_obs == OBS_COMP_FAILED:
            self._prefix_verify_pending = False
            pending_prefix = [
                state.prefix[index] for index in state.comp_stack
                if not state.prefix[index]["compensated"]
            ]
            if (state.compensation_scope == "CURRENT"
                    and any(item["compensatable"] for item in pending_prefix)):
                return ACT_ROLLBACK, 2
            if self.prefix_retry_failed:
                return ACT_ROLLBACK, 2
            return self.prefix_stop_action, 2
        return super().decide(state)


def prefix_hand_fsm():
    fsm = PrefixAwareFSM.from_fsm(hand_fsm())
    for gene in fsm.genes_list():
        if gene.error == OBS_COMPENSATED:
            gene.action = ACT_RETRY
    return fsm


def prefix_random_fsm(rng, base=None):
    if base is None:
        base = random_fsm(rng)
        if rng.random() < 0.5:
            skeleton = {
                "START": "RETRY",
                "TIMEOUT": "WAIT",
                "WAITED": "VERIFY",
                "NOT_COMMITTED": "RETRY",
                "RATE_LIMIT": "WAIT",
                "SCHEMA": "REPAIR",
                "PERMISSION": "ESCALATE",
                "PARTIAL": "COMPENSATE",
            }
            for gene in base.genes_list():
                if gene.att_bucket == 0 and not gene.stack and gene.error in skeleton:
                    gene.action = skeleton[gene.error]
    return PrefixAwareFSM.from_fsm(
        base,
        prefix_reverse=rng.choice((True, False)),
        prefix_verify=rng.choice((True, False)),
        prefix_retry_failed=rng.choice((True, False)),
        prefix_stop_action=rng.choice((ACT_ESCALATE, ACT_STOP)),
    )
