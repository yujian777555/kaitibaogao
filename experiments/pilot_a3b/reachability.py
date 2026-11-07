"""Observation-based robust reachability checker and R1-R4/UNKNOWN classifier.

Implements the semantics frozen in 55_PILOT_A3B_RESEARCH_DESIGN_R1.md section 3:
a recoverability label is decided by the existence of a CONTINGENT POLICY that
maps PUBLIC OBSERVATION HISTORIES to actions and robustly achieves a goal for
ALL hidden states in the scenario's observation-equivalence class.

Key properties (see review 56 B3):
- Hidden states are used only inside the evaluator; policies never read them.
- Nodes are BELIEF STATES (sets of hidden states consistent with one public
  observation history). At each node the policy chooses ONE action for the
  whole belief (policies cannot branch on hidden state). Continuation branches
  split by public observation, and each branch may choose its own next action.
- A single hidden-state action sequence is NOT sufficient for classification.
- If no policy can be proved within horizon/resource limits, the result is
  UNKNOWN, never a forced class.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, FrozenSet, Hashable, Iterable, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Result vocabulary
# ---------------------------------------------------------------------------
CLS_R1 = "R1"
CLS_R2 = "R2"
CLS_R3 = "R3"
CLS_R4 = "R4"
CLS_UNKNOWN = "UNKNOWN"
ALL_CLASSES = (CLS_R1, CLS_R2, CLS_R3, CLS_R4, CLS_UNKNOWN)

GOAL_TASK = "TASK_COMPLETE"
GOAL_ZERO_RESIDUAL = "ZERO_RESIDUAL_TERMINAL"
GOAL_CONTAINMENT = "CONTAINMENT"


@dataclass(frozen=True)
class AugState:
    """Search state = hidden environment state + policy-visible trace flags."""

    hidden: Hashable
    used_compensate: bool = False
    used_escalate: bool = False
    steps: int = 0
    harm: int = 0  # prohibited/irreversible side effects caused so far


@dataclass
class EpisodeSpec:
    """Finite deterministic episode transition system with explicit beliefs.

    transition(h, action) -> (h2, public_obs, harm_delta)
    obs_key(aug2) -> hashable public observation of the new state
    goal(aug) -> bool  (goal predicates receive the augmented state)
    initial_hidden: the full set Theta of hidden initial states that share the
        same public observation (the observation-equivalence class).
    min_reachable_harm: evaluator-declared baseline for R4 avoidable-harm.
    """

    name: str
    initial_hidden: Sequence[Hashable]
    actions: Tuple[str, ...]
    transition: Callable[[Hashable, str], Tuple[Hashable, Hashable, int]]
    obs_key: Callable[[AugState], Hashable]
    terminal: Callable[[AugState], bool]
    goal_task: Callable[[AugState], bool]
    goal_zero_residual: Callable[[AugState], bool]
    min_reachable_harm: int = 0
    expected_class: str = ""
    notes: str = ""


@dataclass
class ReachabilityResult:
    reachable: bool
    proved: bool  # True if search completed (unreachable proved), False if cut off
    policy_tree: dict = field(default_factory=dict)  # obs-history -> action (certificate)
    nodes_expanded: int = 0


class ReachabilityChecker:
    """AND-OR belief-state solver with bounded horizon.

    Semantics:
      - OR node: pick ONE action for the whole belief (policy choice).
      - AND node: every hidden state in the belief must reach the goal, and
        every distinct public-observation continuation must be solvable by
        its own contingent continuation (different histories may differ).
      - Belief merging: states reached with the same public observation
        history are merged into one belief, which enforces that policies are
        functions of observation histories only.
    """

    def __init__(self, spec: EpisodeSpec, horizon: int = 12, max_nodes: int = 200_000):
        self.spec = spec
        self.horizon = horizon
        self.max_nodes = max_nodes
        self.nodes_expanded = 0
        self._cache: dict = {}
        self._cutoff = False

    # -- public API ---------------------------------------------------------
    def solve(self, goal: str, forbid_compensate: bool = False) -> ReachabilityResult:
        self.nodes_expanded = 0
        self._cache = {}
        self._cutoff = False
        aug0 = tuple(AugState(h) for h in self.spec.initial_hidden)
        proved_reachable = self._or_solve(aug0, goal, forbid_compensate)
        if proved_reachable:
            # extract a policy certificate from the successful recursion
            cert = {}
            self._extract(aug0, goal, forbid_compensate, (), cert)
            return ReachabilityResult(True, True, cert, self.nodes_expanded)
        if self._cutoff:
            return ReachabilityResult(False, False, {}, self.nodes_expanded)
        return ReachabilityResult(False, True, {}, self.nodes_expanded)

    # -- recursion ----------------------------------------------------------
    def _or_solve(self, belief: Tuple[AugState, ...], goal: str, forbid_comp: bool) -> bool:
        """OR node: exists an action that wins for all hidden states."""
        if self._cutoff:
            return False
        key = (frozenset(belief), goal, forbid_comp)
        if key in self._cache:
            return self._cache[key]
        self.nodes_expanded += 1
        if self.nodes_expanded > self.max_nodes:
            self._cutoff = True
            return False
        if all(self._goal_met(a, goal) for a in belief):
            self._cache[key] = True
            return True
        if any(a.steps >= self.horizon for a in belief):
            # horizon exceeded on this branch; cannot prove from here
            self._cache[key] = False
            return False

        for action in self.spec.actions:
            if forbid_comp and "COMPENSATE" in action:
                continue
            branches: dict = {}
            stuck = False
            for a in belief:
                if self._goal_met(a, goal):
                    continue  # already terminal-good; nothing more needed
                if self.spec.terminal(a) and not self._goal_met(a, goal):
                    stuck = True
                    break
                h2, obs, harm_delta = self.spec.transition(a.hidden, action)
                aug2 = AugState(
                    hidden=h2,
                    used_compensate=a.used_compensate or ("COMPENSATE" in action),
                    used_escalate=a.used_escalate or action in ("ESCALATE", "STOP_SAFE"),
                    steps=a.steps + 1,
                    harm=a.harm + max(0, harm_delta),
                )
                branches.setdefault(self.spec.obs_key(aug2), []).append(aug2)
            if stuck:
                continue
            ok = True
            for _obs, states in branches.items():
                sub = tuple(states)
                if not self._or_solve(sub, goal, forbid_comp):
                    ok = False
                    break
            if ok:
                self._cache[key] = True
                return True
        self._cache[key] = False
        return False

    def _goal_met(self, a: AugState, goal: str) -> bool:
        if goal == GOAL_TASK:
            return self.spec.goal_task(a)
        if goal == GOAL_ZERO_RESIDUAL:
            return self.spec.goal_zero_residual(a)
        if goal == GOAL_CONTAINMENT:
            return (
                self.spec.terminal(a)
                and a.harm <= self.spec.min_reachable_harm
            )
        raise ValueError(goal)

    def _extract(self, belief, goal, forbid_comp, hist, cert) -> None:
        """Best-effort certificate extraction (one winning policy tree)."""
        if all(self._goal_met(a, goal) for a in belief):
            return
        for action in self.spec.actions:
            if forbid_comp and "COMPENSATE" in action:
                continue
            branches: dict = {}
            stuck = False
            for a in belief:
                if self._goal_met(a, goal):
                    continue
                if self.spec.terminal(a) and not self._goal_met(a, goal):
                    stuck = True
                    break
                h2, obs, harm_delta = self.spec.transition(a.hidden, action)
                aug2 = AugState(
                    hidden=h2,
                    used_compensate=a.used_compensate or ("COMPENSATE" in action),
                    used_escalate=a.used_escalate or action in ("ESCALATE", "STOP_SAFE"),
                    steps=a.steps + 1,
                    harm=a.harm + max(0, harm_delta),
                )
                branches.setdefault(self.spec.obs_key(aug2), []).append(aug2)
            if stuck:
                continue
            ok = True
            for obs, states in branches.items():
                sub = tuple(states)
                probe = ReachabilityChecker(self.spec, self.horizon, self.max_nodes)
                probe._cache = self._cache
                if not probe._or_solve(sub, goal, forbid_comp):
                    ok = False
                    break
            if ok:
                cert[hist] = action
                for obs, states in branches.items():
                    self._extract(tuple(states), goal, forbid_comp, hist + ((action, obs),), cert)
                return


@dataclass
class Classification:
    label: str
    evidence: dict


def classify(spec: EpisodeSpec, horizon: int = 12, max_nodes: int = 200_000) -> Classification:
    """R1-R4 / UNKNOWN decision procedure (mutually exclusive, in order).

    R1: robust TASK_COMPLETE reachable without any COMPENSATE action.
    R2: robust TASK_COMPLETE reachable (necessarily with compensation/rollback).
    R3: task unreachable, robust ZERO_RESIDUAL_TERMINAL reachable.
    R4: zero-residual unreachable, robust CONTAINMENT reachable.
    UNKNOWN: nothing proved within resources, or only non-robust reachability.
    """
    ev: dict = {"spec": spec.name, "horizon": horizon}
    c1 = ReachabilityChecker(spec, horizon, max_nodes).solve(GOAL_TASK, forbid_compensate=True)
    ev["r1_no_comp_task"] = {"reachable": c1.reachable, "proved": c1.proved, "nodes": c1.nodes_expanded}
    if c1.reachable:
        return Classification(CLS_R1, ev)

    c2 = ReachabilityChecker(spec, horizon, max_nodes).solve(GOAL_TASK, forbid_compensate=False)
    ev["r2_task_with_comp"] = {"reachable": c2.reachable, "proved": c2.proved, "nodes": c2.nodes_expanded}
    if c2.reachable:
        return Classification(CLS_R2, ev)

    c3 = ReachabilityChecker(spec, horizon, max_nodes).solve(GOAL_ZERO_RESIDUAL)
    ev["r3_zero_residual"] = {"reachable": c3.reachable, "proved": c3.proved, "nodes": c3.nodes_expanded}
    if c3.reachable:
        return Classification(CLS_R3, ev)

    c4 = ReachabilityChecker(spec, horizon, max_nodes).solve(GOAL_CONTAINMENT)
    ev["r4_containment"] = {"reachable": c4.reachable, "proved": c4.proved, "nodes": c4.nodes_expanded}
    if c4.reachable:
        return Classification(CLS_R4, ev)

    ev["reason"] = (
        "horizon/resource cutoff"
        if (not c1.proved or not c2.proved or not c3.proved or not c4.proved)
        else "all goals proved robustly unreachable"
    )
    return Classification(CLS_UNKNOWN, ev)
