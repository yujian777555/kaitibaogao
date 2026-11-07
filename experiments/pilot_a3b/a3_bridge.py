"""A-3 environment bridge v2: STATEFUL recovery-controller FSM + fixed evaluator.

Addresses 57-review F1-F4:
- F1: real stateful controller (controller state, observation input, explicit
  state transitions, compensation stack / saga progress). NO implicit global
  saga rollback from unused genes; compensation is an explicit controller
  action with a full compensation log.
- F2: policy_selected_escalation vs runtime_forced_abort recorded separately;
  CorrectEscalation only counts explicit policy escalation.
- F4: action-cost objectives are class-conditional; necessary escalation on
  R3/R4 is never penalised.
- Evaluator harm accounting (F3) is computed in the scorer, not the runner.

The environment semantics (ToolRuntime/PublicToolView) are REUSED from the
audited pilot_a3 simulator; this module does not re-implement the environment.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pilot_a_recovery"))

from pilot_a3 import PublicToolView, TOOLS, ToolRuntime, accepted  # noqa: E402

# ---------------------------------------------------------------------------
# Action / observation vocabulary
# ---------------------------------------------------------------------------
ACT_RETRY = "RETRY"
ACT_VERIFY = "VERIFY"
ACT_WAIT = "WAIT"
ACT_COMPENSATE = "COMPENSATE"
ACT_ROLLBACK = "ROLLBACK"
ACT_REPAIR = "REPAIR"
ACT_ESCALATE = "ESCALATE"
ACT_STOP = "STOP_SAFE"
ACTIONS = (ACT_RETRY, ACT_VERIFY, ACT_WAIT, ACT_COMPENSATE, ACT_ROLLBACK,
           ACT_REPAIR, ACT_ESCALATE, ACT_STOP)

OBS_START = "START"
OBS_COMMITTED = "COMMITTED"
OBS_NOT_COMMITTED = "NOT_COMMITTED"
OBS_TIMEOUT = "TIMEOUT"
OBS_PARTIAL = "PARTIAL"
OBS_RATE_LIMIT = "RATE_LIMIT"
OBS_SCHEMA = "SCHEMA"
OBS_PERMISSION = "PERMISSION"
OBS_WAITED = "WAITED"
OBS_COMPENSATED = "COMPENSATED"
OBS_COMP_FAILED = "COMP_FAILED"
OBS_DUPLICATE = "DUPLICATE"
OBS_NOOP = "NOOP"
OBS_ALL = (OBS_START, OBS_TIMEOUT, OBS_PARTIAL, OBS_RATE_LIMIT, OBS_SCHEMA,
           OBS_PERMISSION, OBS_COMMITTED, OBS_NOT_COMMITTED, OBS_WAITED,
           OBS_COMPENSATED, OBS_COMP_FAILED, OBS_DUPLICATE, OBS_NOOP)

MAX_DECISIONS = 24  # per-episode controller decision budget


# ---------------------------------------------------------------------------
# Stateful FSM genome
# ---------------------------------------------------------------------------
class Gene:
    __slots__ = ("error", "att_bucket", "stack", "action", "wait_n")

    def __init__(self, error, att_bucket, stack, action, wait_n=2):
        self.error = error
        self.att_bucket = int(att_bucket)
        self.stack = bool(stack)
        self.action = action
        self.wait_n = int(wait_n)

    def key(self):
        return (self.error, self.att_bucket, self.stack)

    def clone(self):
        return Gene(self.error, self.att_bucket, self.stack, self.action, self.wait_n)


class ControllerState:
    """Policy-maintained state. NO hidden environment data lives here."""

    __slots__ = ("step_idx", "attempts", "last_obs", "confirmed", "comp_stack",
                 "decisions", "phase")

    def __init__(self, n_steps):
        self.step_idx = 0
        self.attempts = 0
        self.last_obs = OBS_START
        self.confirmed = [False] * n_steps
        self.comp_stack = []  # step indices with committed effects, oldest first
        self.decisions = 0
        self.phase = "RECOVER"  # RECOVER | DONE | ABORTED

    def att_bucket(self):
        return 0 if self.attempts == 0 else (1 if self.attempts == 1 else 2)

    def snapshot(self):
        return (self.step_idx, self.attempts, self.last_obs,
                tuple(self.confirmed), tuple(self.comp_stack), self.phase)


class StatefulFSM:
    """Guarded stateful controller: (state ctx, observation) -> action.

    Genome = rule table over (obs_class, attempts_bucket, comp_stack_flag)
    plus a default action. The controller STATE (step index, attempts,
    confirmed steps, compensation stack) is maintained from PUBLIC information
    only (its own actions and public observations).
    """

    def __init__(self, genes, default=(ACT_ESCALATE, 2)):
        self.genes = {g.key(): g for g in genes}
        self.default_action, self.default_wait = default

    def clone(self):
        return StatefulFSM([g.clone() for g in self.genes.values()],
                           (self.default_action, self.default_wait))

    def decide(self, state: ControllerState):
        key = (state.last_obs, state.att_bucket(), bool(state.comp_stack))
        g = self.genes.get(key)
        if g is None:
            g = self.genes.get((state.last_obs, state.att_bucket(), False))
        if g is None:
            return self.default_action, self.default_wait
        return g.action, g.wait_n

    def genes_list(self):
        return [self.genes[k] for k in sorted(self.genes)]


def make_gene_rule_table():
    """One gene per (obs, att_bucket, stack) combination."""
    genes = []
    for obs in OBS_ALL:
        for att in (0, 1, 2):
            for stack in (True, False):
                genes.append(Gene(obs, att, stack, ACT_ESCALATE, 2))
    return genes


def random_fsm(rng):
    genes = []
    for obs in OBS_ALL:
        for att in (0, 1, 2):
            for stack in (True, False):
                genes.append(Gene(obs, att, stack, rng.choice(ACTIONS), rng.randint(1, 4)))
    return StatefulFSM(genes, (rng.choice(ACTIONS), rng.randint(1, 4)))


def hand_fsm():
    """Strong hand-written stateful baseline (generalises saga_aware)."""
    genes = []
    for att in (0, 1, 2):
        for stack in (True, False):
            genes.append(Gene(OBS_START, att, stack, ACT_RETRY, 2))
            genes.append(Gene(OBS_TIMEOUT, att, stack, ACT_WAIT, 4))   # wait out SLA then verify
            genes.append(Gene(OBS_WAITED, att, stack, ACT_VERIFY, 2))
            genes.append(Gene(OBS_NOT_COMMITTED, att, stack, ACT_RETRY, 2))
            genes.append(Gene(OBS_DUPLICATE, att, stack, ACT_ESCALATE, 2))
            genes.append(Gene(OBS_PARTIAL, att, stack, ACT_COMPENSATE, 2))
            genes.append(Gene(OBS_RATE_LIMIT, att, stack, ACT_WAIT, 3))
            genes.append(Gene(OBS_SCHEMA, att, stack, ACT_REPAIR, 2))
            genes.append(Gene(OBS_PERMISSION, att, stack, ACT_ESCALATE, 2))
            genes.append(Gene(OBS_COMMITTED, att, stack, ACT_STOP, 2))
            genes.append(Gene(OBS_COMPENSATED, att, True, ACT_ROLLBACK, 2))
            genes.append(Gene(OBS_COMPENSATED, att, False, ACT_RETRY, 2))
            genes.append(Gene(OBS_COMP_FAILED, att, stack, ACT_ESCALATE, 2))
            genes.append(Gene(OBS_NOOP, att, stack, ACT_VERIFY, 2))
    return StatefulFSM(genes, (ACT_ESCALATE, 2))


# ---------------------------------------------------------------------------
# Mechanism A: contract-preserving semantic repair (repairer side)
# ---------------------------------------------------------------------------
# Repair table (used ONLY by mechanism A). The independent validator lives in
# contract_validator.py (57 F7).
_REPAIR_MAP = {
    (OBS_TIMEOUT, ACT_RETRY): ACT_VERIFY,
    (OBS_PARTIAL, ACT_RETRY): ACT_COMPENSATE,
    (OBS_PARTIAL, ACT_WAIT): ACT_COMPENSATE,
    (OBS_PARTIAL, ACT_VERIFY): ACT_COMPENSATE,
    (OBS_PARTIAL, ACT_ROLLBACK): ACT_COMPENSATE,
    (OBS_PARTIAL, ACT_REPAIR): ACT_COMPENSATE,
    (OBS_PERMISSION, ACT_RETRY): ACT_ESCALATE,
    (OBS_PERMISSION, ACT_WAIT): ACT_ESCALATE,
    (OBS_PERMISSION, ACT_VERIFY): ACT_ESCALATE,
    (OBS_PERMISSION, ACT_COMPENSATE): ACT_ESCALATE,
    (OBS_PERMISSION, ACT_ROLLBACK): ACT_ESCALATE,
    (OBS_PERMISSION, ACT_REPAIR): ACT_ESCALATE,
    (OBS_SCHEMA, ACT_RETRY): ACT_REPAIR,
    (OBS_SCHEMA, ACT_WAIT): ACT_REPAIR,
    (OBS_SCHEMA, ACT_VERIFY): ACT_REPAIR,
    (OBS_SCHEMA, ACT_COMPENSATE): ACT_REPAIR,
    (OBS_SCHEMA, ACT_ROLLBACK): ACT_REPAIR,
    (OBS_COMMITTED, ACT_COMPENSATE): ACT_VERIFY,
    (OBS_COMPENSATED, ACT_COMPENSATE): ACT_VERIFY,
    (OBS_DUPLICATE, ACT_COMPENSATE): ACT_ESCALATE,
    (OBS_NOOP, ACT_COMPENSATE): ACT_VERIFY,
}


def repair_fsm(fsm: StatefulFSM) -> StatefulFSM:
    g2 = fsm.clone()
    for gene in g2.genes_list():
        fix = _REPAIR_MAP.get((gene.error, gene.action))
        if fix is not None:
            gene.action = fix
        if gene.action == ACT_REPAIR and gene.error != OBS_SCHEMA:
            gene.action = ACT_VERIFY
        gene.wait_n = max(1, min(4, gene.wait_n))
    if g2.default_action == ACT_REPAIR:
        g2.default_action = ACT_ESCALATE
    g2.default_wait = max(1, min(4, g2.default_wait))
    return g2


# ---------------------------------------------------------------------------
# Episode execution (stateful loop, explicit compensation)
# ---------------------------------------------------------------------------
def _obs_of_result(result):
    if result in ("COMMITTED", "IDEMPOTENT_REPLAY"):
        return OBS_COMMITTED
    if result == "TIMEOUT":
        return OBS_TIMEOUT
    if result == "PARTIAL":
        return OBS_PARTIAL
    if result == "PARTIAL_REPLAY":
        return OBS_PARTIAL
    if result == "RATE_LIMIT":
        return OBS_RATE_LIMIT
    if result == "SCHEMA":
        return OBS_SCHEMA
    if result == "PERMISSION":
        return OBS_PERMISSION
    if result == "NOT_COMMITTED":
        return OBS_NOT_COMMITTED
    if result == "WAITED":
        return OBS_WAITED
    if result == "COMPENSATED":
        return OBS_COMPENSATED
    if result == "FAILED":
        return OBS_COMP_FAILED
    if result == "CONTRACT_BLOCKED":
        return OBS_COMP_FAILED
    if result == "NO_EFFECT":
        return OBS_NOOP
    if result == "DUPLICATE":
        return OBS_DUPLICATE
    return OBS_NOOP


def run_episode_fsm(fsm: StatefulFSM, scenario):
    """Run one episode. Explicit controller loop; full event log.

    NO implicit saga rollback: the only compensation comes from the
    controller's COMPENSATE / ROLLBACK actions (57 F1).
    """
    tools = [ToolRuntime(name, spec) for name, spec in zip(scenario["tools"], scenario["faults"])]
    n = len(tools)
    state = ControllerState(n)
    decision_trace = []           # (obs, att_bucket, stack, action) for mech B
    comp_log = []                 # (target_step, order, result)
    policy_selected_escalation = False
    runtime_forced_abort = False
    escalation_reason = ""
    downstream_violation = 0

    def step_done(idx):
        return tools[idx].state == "COMMITTED"

    while state.phase == "RECOVER":
        idx = state.step_idx
        if idx >= n:
            state.phase = "DONE"
            break
        # saga gate: no downstream step before prior commits
        if idx > 0 and not all(step_done(j) for j in range(idx)):
            downstream_violation += 1
            runtime_forced_abort = True
            escalation_reason = "downstream_before_commit"
            state.phase = "ABORTED"
            break

        tool = PublicToolView(tools[idx])

        # first call of this step
        if state.attempts == 0 and state.last_obs == OBS_START:
            result = tools[idx].execute()
            state.attempts += 1
            state.last_obs = _obs_of_result(result)
            if accepted(result):
                state.confirmed[idx] = True
                state.comp_stack.append(idx)
                state.step_idx += 1
                state.attempts = 0
                state.last_obs = OBS_START
                continue

        # recovery decision loop
        if state.decisions >= MAX_DECISIONS:
            runtime_forced_abort = True
            escalation_reason = "decision_budget"
            state.phase = "ABORTED"
            break

        action, wait_n = fsm.decide(state)
        decision_trace.append((state.last_obs, state.att_bucket(),
                               bool(state.comp_stack), action))
        state.decisions += 1

        if action in (ACT_ESCALATE, ACT_STOP):
            policy_selected_escalation = True
            escalation_reason = "policy_" + action.lower()
            state.phase = "ABORTED"
            break

        if action == ACT_VERIFY:
            result = tool.verify()
            state.attempts += 1
            state.last_obs = _obs_of_result(result)
            if result == "COMMITTED":
                state.confirmed[idx] = True
                state.comp_stack.append(idx)
                state.step_idx += 1
                state.attempts = 0
                state.last_obs = OBS_START
            continue

        if action == ACT_WAIT:
            for _ in range(wait_n):
                tool.wait()
            state.attempts += 1
            state.last_obs = OBS_WAITED
            continue

        if action == ACT_RETRY:
            result = tool.retry()
            state.attempts += 1
            state.last_obs = _obs_of_result(result)
            if accepted(result):
                state.confirmed[idx] = True
                state.comp_stack.append(idx)
                state.step_idx += 1
                state.attempts = 0
                state.last_obs = OBS_START
            continue

        if action == ACT_REPAIR:
            tool.repair_schema()
            result = tool.retry()
            state.attempts += 1
            state.last_obs = _obs_of_result(result)
            if accepted(result):
                state.confirmed[idx] = True
                state.comp_stack.append(idx)
                state.step_idx += 1
                state.attempts = 0
                state.last_obs = OBS_START
            continue

        if action == ACT_COMPENSATE:
            res = tool.compensate()
            comp_log.append((idx, "current", res))
            state.attempts += 1
            state.last_obs = _obs_of_result(res)
            continue

        if action == ACT_ROLLBACK:
            # explicit reverse-order compensation of confirmed prior steps
            order = 0
            for j in reversed(list(state.comp_stack)):
                order += 1
                res = tools[j].compensate()
                comp_log.append((j, f"rollback{order}", res))
                if res == "COMPENSATED":
                    state.confirmed[j] = False
            state.comp_stack = []
            state.attempts += 1
            state.last_obs = OBS_COMPENSATED
            continue

        # unknown action: treat as no-op observation
        state.attempts += 1
        state.last_obs = OBS_NOOP

    # ---------------- episode accounting ----------------
    violation = downstream_violation + sum(t.violation_count for t in tools)
    task_success = int(
        state.phase == "DONE"
        and all(t.state == "COMMITTED" for t in tools)
        and violation == 0
    )
    active = sum(t.active_effects for t in tools)
    duplicates = sum(t.duplicate_count for t in tools)
    comp_failures = sum(t.compensation_failures for t in tools)
    return {
        "task_success": task_success,
        "safe": int(violation == 0),
        "invariant_violation": int(violation > 0),
        "duplicate_count": duplicates,
        "duplicate": int(duplicates > 0),
        "active_effects": active,
        "unresolved": int(not task_success and active > 0),
        "policy_selected_escalation": int(policy_selected_escalation),
        "runtime_forced_abort": int(runtime_forced_abort),
        "escalation_reason": escalation_reason,
        "compensation_attempts": len(comp_log),
        "compensation_failures": comp_failures,
        "compensation_failure": int(comp_failures > 0),
        "decision_count": state.decisions,
        "action_count": state.decisions + n,  # decisions + first calls
        "decision_trace": decision_trace,
        "comp_log": comp_log,
    }


# ---------------------------------------------------------------------------
# Scenario verdicts: class + unavoidable residual + min reachable harm
# Analytic prover over A-3 semantics (57 F5); each rule is a proof case.
# ---------------------------------------------------------------------------
def scenario_verdict(scenario):
    """Return {class, unavoidable_residual, min_reachable_harm, reason}.

    Rules (exhaustive over the A-3 fault vocabulary; see report 58):
    - permission on any required step => task impossible.
        committed prefix effects that cannot be compensated => R4
        else => R3 (rollback reaches zero residue)
    - partial_commit without usable compensation => R4 (unavoidable residue)
    - partial_commit with usable compensation, or timeout_after-style wrong
      completion that needs compensation => R2
    - otherwise => R1
    """
    tools = scenario["tools"]
    faults = scenario["faults"]

    def comp_ok(i):
        return bool(TOOLS[tools[i]]["compensatable"] and faults[i]["compensation_available"])

    def commits_effect(i):
        return faults[i]["fault"] in ("partial_commit", "timeout_after", "delayed_visibility")

    for i, f in enumerate(faults):
        if f["fault"] == "permission_denied":
            unavoidable = sum(1 for j in range(i) if commits_effect(j) and not comp_ok(j))
            if unavoidable:
                return {"class": "R4", "unavoidable_residual": unavoidable,
                        "min_reachable_harm": unavoidable,
                        "reason": "permission with uncompensable committed prefix"}
            return {"class": "R3", "unavoidable_residual": 0, "min_reachable_harm": 0,
                    "reason": "permission; rollback reaches zero residue"}

    for i, f in enumerate(faults):
        if f["fault"] == "partial_commit" and not comp_ok(i):
            other = sum(1 for j in range(i) if commits_effect(j) and not comp_ok(j))
            return {"class": "R4", "unavoidable_residual": 1 + other,
                    "min_reachable_harm": 1 + other,
                    "reason": "partial commit without usable compensation"}

    need_comp = any(f["fault"] == "partial_commit" and comp_ok(i) for i, f in enumerate(faults))
    if need_comp:
        return {"class": "R2", "unavoidable_residual": 0, "min_reachable_harm": 0,
                "reason": "compensation then redo completes"}
    return {"class": "R1", "unavoidable_residual": 0, "min_reachable_harm": 0,
            "reason": "verify/wait/repair suffices"}


# ---------------------------------------------------------------------------
# Class-conditional scoring (55-R1 section 5, 57 F2/F3/F4)
# ---------------------------------------------------------------------------
def score_episode(verdict, row):
    label = verdict["class"]
    task = row["task_success"]
    residual = row["active_effects"]
    min_harm = verdict["min_reachable_harm"]
    actual_harm = row["duplicate_count"] + residual
    avoidable_harm = max(0, actual_harm - min_harm)
    explicit_esc = row["policy_selected_escalation"] == 1

    if label == "R1":
        ok = task
    elif label == "R2":
        ok = task
    elif label == "R3":
        ok = int(explicit_esc and residual == 0 and not task)
    elif label == "R4":
        ok = int(explicit_esc and row["duplicate"] == 0 and avoidable_harm == 0)
    else:
        ok = None
    return {
        "class_success": ok,
        "actual_harm": actual_harm,
        "avoidable_harm": avoidable_harm,
        "unavoidable_residual": verdict["unavoidable_residual"],
    }


def evaluate_controller(fsm, scenarios, verdicts, scenario_weights=None):
    """Aggregate objectives; weights (<=2x) may emphasise counterexample
    clusters for mechanism B -- the SAME weights apply to all methods in the
    shared evaluation, and the search budget is unchanged."""
    rows = []
    for i, sc in enumerate(scenarios):
        row = run_episode_fsm(fsm, sc)
        v = verdicts[sc["scenario_id"]]
        s = score_episode(v, row)
        row.update(s)
        row["label"] = v["class"]
        row["scenario_id"] = sc["scenario_id"]
        row["weight"] = 1.0 if not scenario_weights else scenario_weights[i]
        rows.append(row)

    by_class = defaultdict(list)
    wsum = defaultdict(float)
    for r in rows:
        by_class[r["label"]].append(r)
        wsum[r["label"]] += r["weight"]

    def wrate(rs, key):
        tot = sum(r["weight"] for r in rs) or 1.0
        return sum(r["weight"] * r[key] for r in rs) / tot

    r12 = by_class["R1"] + by_class["R2"]
    r3 = by_class["R3"]
    r4 = by_class["R4"]
    cond_rec = wrate(r12, "class_success") if r12 else 0.0
    corr_esc = wrate(r3, "class_success") if r3 else 0.0
    containment = wrate(r4, "class_success") if r4 else 0.0
    dup = wrate(rows, "duplicate")
    avoid_resid = sum(r["weight"] * r["avoidable_harm"] for r in rows) / (sum(r["weight"] for r in rows) or 1.0)
    unnec_esc = wrate(r12, "policy_selected_escalation") if r12 else 0.0
    # F4: action cost on R1/R2 only (necessary R3/R4 escalation unpunished)
    if r12:
        unnec_actions = sum(r["weight"] * (r["decision_count"] + r["policy_selected_escalation"]) for r in r12) / sum(r["weight"] for r in r12)
    else:
        unnec_actions = 0.0
    violations = wrate(rows, "invariant_violation")
    r34_actions = (sum(r["decision_count"] for r in r3 + r4) / len(r3 + r4)) if (r3 or r4) else 0.0

    obj1 = 1.0 - cond_rec
    obj2 = dup + avoid_resid
    obj3 = unnec_esc + unnec_actions / 10.0
    return {
        "objectives": (obj1, obj2, obj3),
        "cond_rec": cond_rec,
        "corr_esc": corr_esc,
        "containment": containment,
        "dup": dup,
        "avoid_resid": avoid_resid,
        "unnec_esc": unnec_esc,
        "unnec_actions_r12": unnec_actions,
        "r34_action_cost_desc": r34_actions,
        "violations": violations,
        "n_r1": len(by_class["R1"]),
        "n_r2": len(by_class["R2"]),
        "n_r3": len(by_class["R3"]),
        "n_r4": len(by_class["R4"]),
        "rows": rows,
    }
