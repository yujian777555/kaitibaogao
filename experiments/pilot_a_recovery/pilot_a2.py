"""Pilot A-2: compositional multi-tool transaction recovery simulator.

Exploratory only. Policies receive public observations, never latent fault labels.
Run: python experiments/pilot_a_recovery/pilot_a2.py
"""
import json
from collections import defaultdict

TOOLS = {
    "inventory": {"idempotent": False, "compensatable": True},
    "calendar": {"idempotent": True, "compensatable": True},
    "order": {"idempotent": False, "compensatable": True},
    "ledger": {"idempotent": False, "compensatable": False},
}
POLICIES = ("blind_retry", "verify_retry", "fixed_wait_verify", "escalate_on_unknown",
            "contract_aware", "oracle_diagnostic")
TASKS = ("reserve_inventory_then_order", "book_calendar_then_charge",
         "reserve_inventory_then_ledger", "book_calendar_then_order")
FAULTS = ("timeout_before", "timeout_after", "partial_commit", "stale_read",
          "rate_limit", "compound_timeout_stale", "compound_partial_rate",
          "schema_drift", "permission_denied")


class Tool:
    def __init__(self, name, fault, seed):
        self.name=name; self.contract=TOOLS[name]; self.fault=fault
        self.tick=0; self.effects=0; self.committed=False; self.partial=False
        self.delay=1+seed%4; self.retry_after=1+seed%3
        self.schema_ok=fault!="schema_drift"; self.permission=fault!="permission_denied"
        self.dispatched=fault not in ("timeout_before",)
        if fault in ("timeout_after","stale_read","compound_timeout_stale"):
            self.committed=True; self.effects=1
        if fault in ("partial_commit","compound_partial_rate"):
            self.partial=True; self.effects=1
        self.violation=False; self.calls=0; self.compensated=False

    def observe(self):
        # Public observations deliberately collapse latent timeout subtypes.
        if self.fault in ("timeout_before","timeout_after","stale_read","compound_timeout_stale"):
            err="TIMEOUT"
        elif self.fault in ("partial_commit","compound_partial_rate"): err="PARTIAL"
        elif self.fault=="rate_limit": err="RATE_LIMIT"
        elif self.fault=="schema_drift": err="SCHEMA"
        elif self.fault=="permission_denied": err="PERMISSION"
        else: err="OK"
        visible = self.committed and not (
            self.fault in ("stale_read","compound_timeout_stale") and self.tick < self.delay
        )
        return {"error":err,"visible_committed":visible,"partial_visible":self.partial,
                "retry_after":self.retry_after if err=="RATE_LIMIT" else 0,
                "idempotent":self.contract["idempotent"],
                "compensatable":self.contract["compensatable"],
                "schema_ok":self.schema_ok,"permission":self.permission}

    def act(self, action):
        self.calls += 1
        if action=="WAIT": self.tick+=1; return "WAITED"
        if action=="VERIFY":
            return "COMMITTED" if self.observe()["visible_committed"] else ("PARTIAL" if self.partial else "NOT_COMMITTED")
        if action=="REPAIR_SCHEMA": self.schema_ok=True; return "REPAIRED"
        if action=="COMPENSATE":
            if self.partial and self.contract["compensatable"]:
                self.partial=False; self.effects=0; self.compensated=True; return "COMPENSATED"
            return "UNAVAILABLE"
        if action=="ESCALATE": return "ESCALATED"
        if action=="RETRY":
            if not self.permission: return "DENIED"
            if not self.schema_ok: return "SCHEMA_REJECTED"
            if self.fault in ("rate_limit","compound_partial_rate") and self.tick<self.retry_after:
                return "RATE_LIMITED"
            if self.committed or self.partial:
                if not self.contract["idempotent"] or self.partial:
                    self.effects+=1; self.violation=True; return "DUPLICATE"
                return "IDEMPOTENT_REPLAY"
            self.committed=True; self.effects+=1; self.dispatched=True; return "COMMITTED"
        raise ValueError(action)


def episode(policy, task, fault, seed):
    names=TASKS.index(task)
    tool_pairs=(("inventory","order"),("calendar","ledger"),
                ("inventory","ledger"),("calendar","order"))
    tools=[Tool(n,fault,seed+idx*7) for idx,n in enumerate(tool_pairs[names])]
    actions=0; escalated=False
    for t in tools:
        obs=t.observe()
        if policy=="oracle_diagnostic":
            # Oracle sees hidden subtype; diagnostic upper bound only.
            if fault=="timeout_before": t.act("RETRY")
            elif fault in ("timeout_after","stale_read","compound_timeout_stale"): t.act("VERIFY")
            elif fault in ("partial_commit","compound_partial_rate"):
                t.act("COMPENSATE")
                if t.partial: t.act("ESCALATE"); escalated=True
                else:
                    for _ in range(t.retry_after): t.act("WAIT")
                    t.act("RETRY")
            elif fault in ("rate_limit",): 
                for _ in range(t.retry_after): t.act("WAIT")
                t.act("RETRY")
            elif fault=="schema_drift": t.act("REPAIR_SCHEMA"); t.act("RETRY")
            else: t.act("ESCALATE"); escalated=True
        elif policy=="blind_retry":
            t.act("RETRY")
        elif policy=="verify_retry":
            state=t.act("VERIFY")
            if state=="NOT_COMMITTED": t.act("RETRY")
            elif state=="PARTIAL":
                if t.contract["compensatable"]: t.act("COMPENSATE"); t.act("RETRY")
                else: t.act("ESCALATE"); escalated=True
        elif policy=="fixed_wait_verify":
            for _ in range(3): t.act("WAIT")
            state=t.act("VERIFY")
            if state=="NOT_COMMITTED": t.act("RETRY")
            elif state=="PARTIAL":
                if t.contract["compensatable"]: t.act("COMPENSATE"); t.act("RETRY")
                else: t.act("ESCALATE"); escalated=True
        elif policy=="escalate_on_unknown":
            if obs["error"] in ("TIMEOUT","PARTIAL","PERMISSION"):
                t.act("ESCALATE"); escalated=True
            elif obs["error"]=="RATE_LIMIT":
                for _ in range(obs["retry_after"]): t.act("WAIT")
                t.act("RETRY")
            elif obs["error"]=="SCHEMA": t.act("REPAIR_SCHEMA"); t.act("RETRY")
            else: t.act("RETRY")
        elif policy=="contract_aware":
            if obs["error"]=="PERMISSION":
                t.act("ESCALATE"); escalated=True
            elif obs["error"]=="SCHEMA":
                t.act("REPAIR_SCHEMA"); t.act("RETRY")
            elif obs["error"]=="RATE_LIMIT":
                for _ in range(obs["retry_after"]): t.act("WAIT")
                t.act("RETRY")
            else:
                state=t.act("VERIFY")
                if state=="NOT_COMMITTED":
                    if obs["error"] in ("TIMEOUT","PARTIAL") and not obs["idempotent"]:
                        # repeated verification after bounded visibility wait
                        for _ in range(t.delay): t.act("WAIT")
                        state=t.act("VERIFY")
                    if state=="NOT_COMMITTED": t.act("RETRY")
                elif state=="PARTIAL":
                    if obs["compensatable"]: t.act("COMPENSATE"); t.act("RETRY")
                    else: t.act("ESCALATE"); escalated=True
        actions+=t.calls
    success=all(t.committed and not t.partial and not t.violation for t in tools)
    safe=all(not t.violation for t in tools)
    return {"policy":policy,"task":task,"fault":fault,"seed":seed,
            "task_success":int(success),"safe":int(safe),
            "duplicate":int(any(t.effects>1 for t in tools)),
            "invariant_violation":int(any(t.violation for t in tools)),
            "unresolved":int(not success and not escalated),
            "escalated":int(escalated),"actions":actions,
            "tool_pair":"+".join(t.name for t in tools)}


def summarize(rows):
    out={}
    keys=("task_success","safe","duplicate","invariant_violation","unresolved","escalated","actions")
    for p in POLICIES:
        g=[r for r in rows if r["policy"]==p]
        out[p]={"episodes":len(g)}
        for k in keys: out[p][k]=round(sum(x[k] for x in g)/len(g),4)
    return out


if __name__=="__main__":
    rows=[episode(p,t,f,s) for p in POLICIES for t in TASKS
          for f in FAULTS for s in range(30)]
    # Per-task and per-fault results retained for audit.
    groups=defaultdict(list)
    for r in rows: groups[(r["policy"],r["task"],r["fault"])].append(r)
    stratified={}
    for group_key, group_rows in groups.items():
        policy = group_key[0]
        metrics = ("task_success","safe","duplicate","invariant_violation","unresolved","escalated","actions")
        record = {"episodes": len(group_rows)}
        for metric in metrics:
            record[metric] = round(sum(row[metric] for row in group_rows)/len(group_rows),4)
        stratified["|".join(group_key)] = record
    payload = {"design":{"tasks":TASKS,"faults":FAULTS,"seeds":30,
        "episodes_per_policy":len(TASKS)*len(FAULTS)*30,
        "note":"exploratory deterministic simulator; policies see public observations only; oracle diagnostic sees latent fault"},
        "summary":summarize(rows),"stratified":stratified}
    rendered = json.dumps(payload, indent=2)
    print(rendered)
    from pathlib import Path
    output = Path(__file__).parent / "pilot_a2_summary.json"
    output.write_text(rendered + "\n", encoding="utf-8")
