"""Deterministic Pilot A for stateful tool recovery policies.

Run: python pilot_a.py
Only the oracle policy reads the hidden fault subtype.
"""
import json

FAULTS = (
    "timeout_before_dispatch", "timeout_after_commit", "partial_commit",
    "delayed_visibility", "rate_limit", "schema_drift", "permission_denied",
)
POLICIES = (
    "blind_retry", "verify_then_retry", "wait_verify_retry",
    "conservative_escalate", "state_aware", "oracle_upper_bound",
)

class Env:
    def __init__(self, fault, seed):
        self.fault, self.seed, self.tick = fault, seed, 0
        self.delay = 1 + seed % 3 if fault == "delayed_visibility" else 0
        self.rate_wait = 1 + seed % 2 if fault == "rate_limit" else 0
        self.status, self.effects, self.schema = "NOT_DISPATCHED", 0, fault != "schema_drift"
        self.permission = fault != "permission_denied"
        self.violation = self.resolved = False
        if fault == "timeout_after_commit":
            self.status, self.effects = "COMMITTED", 1
        elif fault == "partial_commit":
            self.status, self.effects = "PARTIAL", 1
        elif fault == "delayed_visibility":
            self.status, self.effects = "COMMITTED", 1
        self.actions = 0

    def observe(self):
        failure = ("TIMEOUT" if self.fault in (
            "timeout_before_dispatch", "timeout_after_commit", "delayed_visibility"
        ) else {
            "partial_commit": "PARTIAL_RESPONSE", "rate_limit": "RATE_LIMIT",
            "schema_drift": "SCHEMA_VALIDATION", "permission_denied": "PERMISSION",
        }[self.fault])
        return {"failure": failure,
                "retry_after": self.rate_wait if self.fault == "rate_limit" else None,
                "schema_valid": self.schema, "permission": self.permission}

    def act(self, action):
        self.actions += 1
        if action == "WAIT":
            self.tick += 1
            return "WAITED"
        if action == "VERIFY":
            if self.fault == "delayed_visibility" and self.tick < self.delay:
                return "NOT_DISPATCHED"  # stale but legal read
            return self.status
        if action == "REPLAN":
            if self.fault == "schema_drift":
                self.schema = True
                return "SCHEMA_REPAIRED"
            return "REPLANNED"
        if action == "COMPENSATE":
            if self.status == "PARTIAL":
                self.status, self.effects = "NOT_DISPATCHED", 0
                return "COMPENSATED"
            return "NOT_COMPENSATABLE"
        if action == "ESCALATE":
            self.resolved = True
            return "ESCALATED"
        if action == "RETRY":
            if not self.permission:
                return "PERMISSION_DENIED"
            if not self.schema:
                return "SCHEMA_REJECTED"
            if self.fault == "rate_limit" and self.tick < self.rate_wait:
                return "RATE_LIMITED"
            if self.status in ("COMMITTED", "PARTIAL"):
                self.effects += 1
                self.violation = True
                return "DUPLICATE"
            self.status, self.effects = "COMMITTED", 1
            return "COMMITTED"
        raise ValueError(action)

    def result(self, policy):
        success = self.status == "COMMITTED" and self.effects == 1 and not self.violation
        return {"policy": policy, "fault": self.fault, "seed": self.seed,
                "task_success": int(success),
                "safe_resolution": int(success or self.resolved),
                "duplicate_side_effect": int(self.effects > 1),
                "invariant_violation": int(self.violation),
                "unresolved": int(not success and not self.resolved),
                "tool_actions": self.actions}


def run(policy, fault, seed):
    env = Env(fault, seed)
    obs = env.observe()
    act = env.act
    if policy == "blind_retry":
        act("RETRY")
    elif policy == "verify_then_retry":
        status = act("VERIFY")
        if status == "NOT_DISPATCHED":
            act("RETRY")
        elif status == "PARTIAL":
            act("COMPENSATE"); act("RETRY")
    elif policy == "wait_verify_retry":
        act("WAIT")
        status = act("VERIFY")
        if status == "NOT_DISPATCHED":
            act("RETRY")
        elif status == "PARTIAL":
            act("COMPENSATE"); act("RETRY")
    elif policy in ("conservative_escalate", "state_aware"):
        if obs["failure"] == "TIMEOUT":
            waits = 1 if policy == "conservative_escalate" else 3
            for _ in range(waits):
                act("WAIT")
            status = act("VERIFY")
            if status == "NOT_DISPATCHED":
                act("RETRY")
            elif status == "PARTIAL":
                act("COMPENSATE"); act("RETRY")
        elif obs["failure"] == "RATE_LIMIT":
            for _ in range(obs["retry_after"]):
                act("WAIT")
            act("RETRY")
        elif obs["failure"] == "PARTIAL_RESPONSE":
            act("VERIFY"); act("COMPENSATE"); act("RETRY")
        elif obs["failure"] == "SCHEMA_VALIDATION":
            act("REPLAN"); act("RETRY")
        else:
            act("ESCALATE")
    elif policy == "oracle_upper_bound":
        # Diagnostic only: hidden subtype is intentionally available here.
        if fault == "timeout_before_dispatch":
            act("RETRY")
        elif fault in ("timeout_after_commit", "delayed_visibility"):
            act("VERIFY")
        elif fault == "partial_commit":
            act("COMPENSATE"); act("RETRY")
        elif fault == "rate_limit":
            for _ in range(env.rate_wait):
                act("WAIT")
            act("RETRY")
        elif fault == "schema_drift":
            act("REPLAN"); act("RETRY")
        else:
            act("ESCALATE")
    else:
        raise ValueError(policy)
    return env.result(policy)


def summarize(rows):
    result = {}
    metrics = ("task_success", "safe_resolution", "duplicate_side_effect",
               "invariant_violation", "unresolved", "tool_actions")
    for policy in POLICIES:
        group = [r for r in rows if r["policy"] == policy]
        result[policy] = {"episodes": len(group)}
        for metric in metrics:
            result[policy][metric] = round(
                sum(r[metric] for r in group) / len(group), 4
            )
    return result


if __name__ == "__main__":
    rows = [run(p, f, s) for p in POLICIES for f in FAULTS for s in range(10)]
    print(json.dumps({
        "design": {"fault_families": FAULTS, "seeds_per_fault": 10,
                   "episodes_per_policy": len(FAULTS) * 10,
                   "policies": POLICIES,
                   "note": "exploratory deterministic simulator; oracle sees hidden subtype"},
        "summary": summarize(rows),
    }, indent=2))
