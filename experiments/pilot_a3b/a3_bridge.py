"""A-3 environment bridge: episode runner for evolved FSM controllers.

Reuses the audited Pilot A-3 simulator semantics (ToolRuntime/PublicToolView
from experiments/pilot_a_recovery/pilot_a3.py) WITHOUT re-implementing the
environment. Adds:
- a generic controller interface (guarded FSM) at each step's recovery point;
- analytic recoverability labels (R1-R4/UNKNOWN) per scenario, derived from
  the 55-R1 ladder and validated against the Stage-1 reachability checker
  semantics (see a3_labels tests);
- class-conditional scoring per 55-R1 section 5.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pilot_a_recovery"))

from pilot_a3 import (  # noqa: E402
    PublicToolView,
    TOOLS,
    ToolRuntime,
    accepted,
    build_scenarios,
    make_fault_vector,
)

# ---------------------------------------------------------------------------
# Controller interface
# ---------------------------------------------------------------------------
ACTION_BLIND = "BLIND_RETRY"
ACTION_VERIFY = "VERIFY_THEN_RETRY"
ACTION_WAIT = "WAIT_VERIFY_RETRY"
ACTION_COMP = "COMPENSATE_THEN_RETRY"
ACTION_REPAIR = "REPAIR_THEN_RETRY"
ACTION_ESCALATE = "ESCALATE"
ACTIONS = (ACTION_BLIND, ACTION_VERIFY, ACTION_WAIT, ACTION_COMP, ACTION_REPAIR, ACTION_ESCALATE)

ERRORS = ("TIMEOUT", "PARTIAL", "RATE_LIMIT", "SCHEMA", "PERMISSION", "NONE")


class Rule:
    __slots__ = ("error", "idem", "comp", "action", "wait_n")

    def __init__(self, error, idem, comp, action, wait_n=2):
        self.error = error
        self.idem = idem
        self.comp = comp
        self.action = action
        self.wait_n = int(wait_n)

    def key(self):
        return (self.error, self.idem, self.comp)

    def clone(self):
        return Rule(self.error, self.idem, self.comp, self.action, self.wait_n)


class FSMGenome:
    """Guarded FSM as a rule table: (error, idem, comp) -> macro-action."""

    def __init__(self, rules, default=(ACTION_ESCALATE, 2)):
        self.rules = {r.key(): r for r in rules}
        self.default_action, self.default_wait = default

    def rule_for(self, error, idem, comp):
        return self.rules.get((error, idem, comp))

    def decide(self, error, idem, comp):
        r = self.rule_for(error, idem, comp)
        if r is None:
            return self.default_action, self.default_wait
        return r.action, r.wait_n

    def clone(self):
        return FSMGenome([r.clone() for r in self.rules.values()], (self.default_action, self.default_wait))

    def rule_keys(self):
        return sorted(self.rules)


def make_rules(grid):
    """grid: dict (error, idem, comp) -> (action, wait_n)"""
    return [Rule(k[0], k[1], k[2], v[0], v[1]) for k, v in grid.items()]


def random_genome(rng):
    import itertools

    rules = []
    for error, idem, comp in itertools.product(ERRORS, (True, False), (True, False)):
        action = rng.choice(ACTIONS)
        wait_n = rng.randint(1, 4)
        rules.append(Rule(error, idem, comp, action, wait_n))
    return FSMGenome(rules, (rng.choice(ACTIONS), rng.randint(1, 4)))


def hand_genome():
    """Strong hand-written baseline (generalises saga_aware/contract_aware).

    Mirrors pilot_a3.saga_aware semantics: ambiguous TIMEOUT waits out the
    public visibility SLA before concluding non-commit; partial commit is
    compensated when the contract allows; permission/schema have one right
    move; rate limit waits out the public retry hint.
    """
    grid = {}
    for idem in (True, False):
        for comp in (True, False):
            grid[("PERMISSION", idem, comp)] = (ACTION_ESCALATE, 2)
            grid[("SCHEMA", idem, comp)] = (ACTION_REPAIR, 2)
            grid[("RATE_LIMIT", idem, comp)] = (ACTION_WAIT, 3)
            grid[("NONE", idem, comp)] = (ACTION_VERIFY, 2)
            # ambiguous outcome: wait out visibility SLA (bound=4), then verify
            grid[("TIMEOUT", idem, comp)] = (ACTION_WAIT, 4)
            if comp:
                grid[("PARTIAL", idem, comp)] = (ACTION_COMP, 2)
            else:
                grid[("PARTIAL", idem, comp)] = (ACTION_ESCALATE, 2)
    return FSMGenome(make_rules(grid))


# ---------------------------------------------------------------------------
# Contract-preserving semantic repair (mechanism A)
# ---------------------------------------------------------------------------
ILLEGAL = {
    # non-idempotent tool + ambiguous outcome must not be a bare retry
    ("TIMEOUT", False): {ACTION_BLIND},
    ("PARTIAL", False): {ACTION_BLIND, ACTION_WAIT, ACTION_VERIFY},
    # partial commit: only compensation can clear; blind/wait/verify won't
    ("PARTIAL", True): {ACTION_BLIND, ACTION_WAIT},
    # permission denial: retry/wait never helps
    ("PERMISSION", True): {ACTION_BLIND, ACTION_WAIT, ACTION_VERIFY, ACTION_COMP, ACTION_REPAIR},
    ("PERMISSION", False): {ACTION_BLIND, ACTION_WAIT, ACTION_VERIFY, ACTION_COMP, ACTION_REPAIR},
    # schema drift: only repair can fix
    ("SCHEMA", True): {ACTION_BLIND, ACTION_WAIT, ACTION_VERIFY, ACTION_COMP},
    ("SCHEMA", False): {ACTION_BLIND, ACTION_WAIT, ACTION_VERIFY, ACTION_COMP},
}
LEGAL_FIX = {
    ("TIMEOUT", False): (ACTION_VERIFY, ACTION_COMP),
    ("PARTIAL", False): (ACTION_COMP, ACTION_ESCALATE),
    ("PARTIAL", True): (ACTION_COMP, ACTION_ESCALATE),
    ("PERMISSION", True): (ACTION_ESCALATE,),
    ("PERMISSION", False): (ACTION_ESCALATE,),
    ("SCHEMA", True): (ACTION_REPAIR,),
    ("SCHEMA", False): (ACTION_REPAIR,),
}


def repair_genome(genome: FSMGenome) -> FSMGenome:
    """Deterministic semantic repair: replace illegal rules with legal ones."""
    g = genome.clone()
    for key, rule in g.rules.items():
        error, idem, comp = key
        illegal = ILLEGAL.get((error, idem), set())
        if rule.action in illegal:
            fix = LEGAL_FIX[(error, idem)]
            rule.action = fix[0]
        if rule.action == ACTION_COMP and not comp:
            rule.action = ACTION_ESCALATE
        if rule.action == ACTION_REPAIR and error != "SCHEMA":
            rule.action = ACTION_VERIFY
        rule.wait_n = max(1, min(4, rule.wait_n))
    return g


def is_legal(genome: FSMGenome) -> bool:
    for key, rule in genome.rules.items():
        error, idem, comp = key
        if rule.action in ILLEGAL.get((error, idem), set()):
            return False
        if rule.action == ACTION_COMP and not comp:
            return False
    return True


# ---------------------------------------------------------------------------
# Macro-action execution against PublicToolView (mirrors recover_tool)
# ---------------------------------------------------------------------------
def _compensate_then_retry(tool):
    if not tool.contract["compensatable"]:
        return False
    if tool.compensate() != "COMPENSATED":
        return False
    return accepted(tool.retry())


def execute_macro(genome, error, tool):
    action, wait_n = genome.decide(error, tool.contract["idempotent"], tool.contract["compensatable"])
    if action == ACTION_BLIND:
        return accepted(tool.retry())
    if action == ACTION_VERIFY:
        state = tool.verify()
        if state == "COMMITTED":
            return True
        if state == "PARTIAL":
            return _compensate_then_retry(tool)
        return accepted(tool.retry())
    if action == ACTION_WAIT:
        for _ in range(wait_n):
            tool.wait()
        state = tool.verify()
        if state == "COMMITTED":
            return True
        if state == "PARTIAL":
            return _compensate_then_retry(tool)
        return accepted(tool.retry())
    if action == ACTION_COMP:
        return _compensate_then_retry(tool)
    if action == ACTION_REPAIR:
        tool.repair_schema()
        return accepted(tool.retry())
    if action == ACTION_ESCALATE:
        return False
    return False


# ---------------------------------------------------------------------------
# Episode runner (mirrors pilot_a3.run_episode structure)
# ---------------------------------------------------------------------------
def run_episode_fsm(genome, scenario):
    tools = [ToolRuntime(name, spec) for name, spec in zip(scenario["tools"], scenario["faults"])]
    failed = False
    escalated = False
    rollback_order = []
    downstream_violation = 0

    for index, tool in enumerate(tools):
        if index and any(p.state != "COMMITTED" for p in tools[:index]):
            downstream_violation += 1
            failed = True
            escalated = True
            break
        first = tool.execute()
        if accepted(first):
            continue
        recovered = execute_macro(genome, first, PublicToolView(tool))
        if recovered and tool.state == "COMMITTED":
            continue
        failed = True
        escalated = True
        # evolved controllers may carry a saga flag via default action naming;
        # rollback only for controllers whose default is ESCALATE and any rule
        # used COMP (approximation of saga-awareness, shared across methods).
        if any(r.action == ACTION_COMP for r in genome.rules.values()):
            for t in reversed(tools[: index + 1]):
                if t.active_effects <= 0:
                    continue
                if not t.contract["compensatable"]:
                    rollback_order.append(t.name + ":BLOCKED")
                    continue
                res = t.compensate()
                rollback_order.append(t.name if res == "COMPENSATED" else t.name + ":FAILED")
        break

    violation = downstream_violation + sum(t.violation_count for t in tools)
    task_success = int(not failed and all(t.state == "COMMITTED" for t in tools) and violation == 0)
    active = sum(t.active_effects for t in tools)
    comp_failures = sum(t.compensation_failures for t in tools)
    actions = sum(t.action_count for t in tools) + int(escalated)
    return {
        "task_success": task_success,
        "safe": int(violation == 0),
        "invariant_violation": int(violation > 0),
        "duplicate": int(any(t.duplicate_count > 0 for t in tools)),
        "unresolved": int(not task_success and active > 0),
        "escalated": int(escalated),
        "compensation_failure": int(comp_failures > 0),
        "active_effects": active,
        "action_count": actions,
        "rollback_order": ">".join(rollback_order),
    }


# ---------------------------------------------------------------------------
# Analytic recoverability labels for A-3 scenarios (55-R1 ladder)
# ---------------------------------------------------------------------------
def label_scenario(scenario):
    """Return R1/R2/R3/R4/UNKNOWN for one A-3 scenario.

    Rules (validated by test_a3_labels against the Stage-1 checker ladder):
    - permission_denied on any REQUIRED step => task impossible.
        committed prefix all compensatable AND compensation available => R3
        else (unavoidable residue) => R4
    - partial_commit whose compensation is unavailable/non-compensatable => R4
      (residue unavoidable) unless later required step also blocked earlier.
    - partial_commit with compensation available OR timeout_after-style
      completion blocked without compensation => R2
    - otherwise (verify/wait/repair suffices) => R1
    """
    tools = scenario["tools"]
    faults = scenario["faults"]

    def comp_ok(i):
        f = faults[i]
        tool = tools[i]
        return bool(TOOLS[tool]["compensatable"] and f["compensation_available"])

    # task impossible due to permission on a required step
    for i, f in enumerate(faults):
        if f["fault"] == "permission_denied":
            # steps before i were attempted; committed effects that cannot be
            # compensated leave unavoidable residue => R4 instead of R3
            unavoidable = False
            for j in range(i):
                fj = faults[j]
                if fj["fault"] in ("partial_commit", "timeout_after", "delayed_visibility"):
                    if not comp_ok(j):
                        unavoidable = True
            return "R4" if unavoidable else "R3"

    # unavoidable residue from partial commit w/o compensation
    for i, f in enumerate(faults):
        if f["fault"] == "partial_commit" and not comp_ok(i):
            return "R4"

    # needs compensation to complete: partial commit with compensation
    need_comp = any(f["fault"] == "partial_commit" and comp_ok(i) for i, f in enumerate(faults))
    if need_comp:
        return "R2"

    # timeout_after / delayed_visibility: verify/wait completes without comp
    return "R1"


# ---------------------------------------------------------------------------
# Class-conditional scoring (55-R1 section 5)
# ---------------------------------------------------------------------------
def score_class(label, row):
    """Return per-episode dict of class-conditional success and burdens."""
    task = row["task_success"]
    zero_res = row["active_effects"] == 0
    if label == "R1":
        ok = task
    elif label == "R2":
        ok = task  # R2 success = final completion (safe abort does NOT count)
    elif label == "R3":
        ok = int(row["escalated"] == 1 and zero_res and not task)
    elif label == "R4":
        ok = int(row["escalated"] == 1 and row["duplicate"] == 0)  # containment
    else:
        ok = None
    return ok


def evaluate_controller(genome, scenarios, labels):
    """Aggregate objectives over a scenario list (all with labels)."""
    rows = []
    for sc in scenarios:
        row = run_episode_fsm(genome, sc)
        lab = labels[sc["scenario_id"]]
        row["label"] = lab
        row["class_success"] = score_class(lab, row)
        rows.append(row)

    by_class = defaultdict(list)
    for r in rows:
        by_class[r["label"]].append(r)

    def rate(rs, key):
        return sum(r[key] for r in rs) / len(rs) if rs else 0.0

    r12 = by_class["R1"] + by_class["R2"]
    r3 = by_class["R3"]
    r4 = by_class["R4"]
    cond_rec = (
        sum(r["class_success"] for r in r12) / len(r12) if r12 else 0.0
    )
    corr_esc = sum(r["class_success"] for r in r3) / len(r3) if r3 else 0.0
    containment = sum(r["class_success"] for r in r4) / len(r4) if r4 else 0.0
    dup = rate(rows, "duplicate")
    # avoidable residual proxy: active_effects left when not R4 (R4 baseline is
    # scenario-declared unavoidable; for A-3 partial-comp-failure the residue is
    # unavoidable). Charge only non-R4 unresolved residue.
    avoid_resid = 0.0
    if rows:
        avoid_resid = sum(
            r["active_effects"] for r in rows if r["label"] != "R4" and r["unresolved"]
        ) / len(rows)
    unnec_esc = sum(r["escalated"] for r in r12) / len(r12) if r12 else 0.0
    norm_actions = rate(rows, "action_count") / 10.0
    violations = rate(rows, "invariant_violation")

    obj1 = 1.0 - cond_rec
    obj2 = dup + avoid_resid
    obj3 = unnec_esc + norm_actions
    return {
        "objectives": (obj1, obj2, obj3),
        "cond_rec": cond_rec,
        "corr_esc": corr_esc,
        "containment": containment,
        "dup": dup,
        "avoid_resid": avoid_resid,
        "unnec_esc": unnec_esc,
        "norm_actions": norm_actions,
        "violations": violations,
        "n_r1": len(by_class["R1"]),
        "n_r2": len(by_class["R2"]),
        "n_r3": len(by_class["R3"]),
        "n_r4": len(by_class["R4"]),
        "rows": rows,
    }
