"""Pilot B2: multi-step cross-tool Saga recovery simulator.

Exploratory feasibility pilot only. No LLM API, no A800 model training, no EC search.
"""
from __future__ import annotations
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

TASKS = {
    "order_fulfillment": [
        {"tool":"inventory","operation":"reserve_stock","idempotency":"native","compensable":True,"consistency":"strong","max_visibility_delay":0,"compensation":"release_stock"},
        {"tool":"order","operation":"create_order","idempotency":"keyed","compensable":True,"consistency":"eventual","max_visibility_delay":3,"compensation":"cancel_order"},
        {"tool":"ledger","operation":"post_charge","idempotency":"native","compensable":True,"consistency":"strong","max_visibility_delay":0,"compensation":"refund_charge"},
    ],
    "appointment_confirmation": [
        {"tool":"calendar","operation":"reserve_slot","idempotency":"none","compensable":True,"consistency":"eventual","max_visibility_delay":5,"compensation":"release_slot"},
        {"tool":"ledger","operation":"post_deposit","idempotency":"native","compensable":True,"consistency":"strong","max_visibility_delay":0,"compensation":"refund_deposit"},
        {"tool":"calendar","operation":"confirm_appointment","idempotency":"none","compensable":True,"consistency":"eventual","max_visibility_delay":5,"compensation":"cancel_appointment"},
    ],
    "return_refund": [
        {"tool":"order","operation":"cancel_order","idempotency":"keyed","compensable":True,"consistency":"eventual","max_visibility_delay":3,"compensation":"restore_order"},
        {"tool":"inventory","operation":"release_stock","idempotency":"native","compensable":True,"consistency":"strong","max_visibility_delay":0,"compensation":"reserve_stock"},
        {"tool":"ledger","operation":"post_refund","idempotency":"native","compensable":True,"consistency":"strong","max_visibility_delay":0,"compensation":"reverse_refund"},
    ],
}
PROFILES = (
    "timeout_before", "timeout_after", "partial_commit",
    "delayed_timeout_after", "timeout_rate_before", "timeout_rate_after",
    "schema_before", "permission_before", "partial_compensation_unavailable",
    "partial_previous_comp_failure", "partial_timeout_delayed",
)
POLICIES = ("blind_retry","verify_then_retry","contract_resume","rollback_on_ambiguous","oracle_upper_bound")
TRAIN_SEEDS=tuple(range(3000,3040))
VALIDATION_SEEDS=tuple(range(3100,3120))
TEST_SEEDS=tuple(range(3120,3160))

def make_episode(task, step_index, profile, seed):
    rng=random.Random(seed*1009 + list(TASKS).index(task)*97 + step_index*17 + list(PROFILES).index(profile)*13)
    steps=[dict(x) for x in TASKS[task]]
    current=steps[step_index]
    outcome,effects="NONE",0
    signals=[]
    delay,retry_after=0,0
    schema_valid,permission=True,True
    current_comp_available=True
    previous_comp_failure_index=None
    def vis_delay():
        return rng.randint(1,current["max_visibility_delay"]) if current["consistency"]=="eventual" else 0
    if profile=="timeout_before":
        signals=["TIMEOUT"]
    elif profile=="timeout_after":
        signals=["TIMEOUT"]; outcome,effects="COMMITTED",1
    elif profile=="partial_commit":
        signals=["PARTIAL_RESPONSE"]; outcome,effects="PARTIAL",1
    elif profile=="delayed_timeout_after":
        signals=["TIMEOUT"]; outcome,effects="COMMITTED",1; delay=vis_delay()
    elif profile=="timeout_rate_before":
        signals=["TIMEOUT","RATE_LIMIT"]; retry_after=rng.randint(1,3)
    elif profile=="timeout_rate_after":
        signals=["TIMEOUT","RATE_LIMIT"]; outcome,effects="COMMITTED",1
        retry_after,delay=rng.randint(1,3),vis_delay()
    elif profile=="schema_before":
        signals=["SCHEMA_VALIDATION"]; schema_valid=False
    elif profile=="permission_before":
        signals=["PERMISSION"]; permission=False
    elif profile=="partial_compensation_unavailable":
        signals=["PARTIAL_RESPONSE"]; outcome,effects="PARTIAL",1; current_comp_available=False
    elif profile=="partial_previous_comp_failure":
        signals=["PARTIAL_RESPONSE"]; outcome,effects="PARTIAL",1
        previous_comp_failure_index=step_index-1 if step_index>0 else None
    elif profile=="partial_timeout_delayed":
        signals=["TIMEOUT"]; outcome,effects="PARTIAL",1; delay=vis_delay()
    else:
        raise ValueError(profile)
    return {
        "task":task,"step_index":step_index,"steps":steps,"profile":profile,"seed":seed,
        "current_outcome":outcome,"current_effects":effects,"signals":tuple(signals),
        "visibility_delay":delay,"retry_after":retry_after,"schema_valid":schema_valid,
        "permission":permission,"current_comp_available":current_comp_available,
        "previous_comp_failure_index":previous_comp_failure_index,
    }

class Env:
    def __init__(self,spec):
        self.spec=spec
        self.tick=0
        self.current_outcome=spec["current_outcome"]
        self.current_effects=spec["current_effects"]
        self.previous_stack=list(range(spec["step_index"]))
        self.violation=False
        self.escalated=False
        self.rollback_complete=False
        self.actions=spec["step_index"]+1  # successful prefix plus failed operation attempt
        self.wait_units=0
        self.compensated_current=False
        self.compensated_previous=[]

    def observe(self):
        i=self.spec["step_index"]
        return {
            "task":self.spec["task"],"step_index":i,"total_steps":len(self.spec["steps"]),
            "current_operation":dict(self.spec["steps"][i]),
            "completed_prefix":[dict(self.spec["steps"][j]) for j in self.previous_stack],
            "signals":tuple(self.spec["signals"]),
            "schema_valid":self.spec["schema_valid"],"permission":self.spec["permission"],
            "retry_after":self.spec["retry_after"],
        }

    def act(self,action,duration=0,index=None):
        s=self.spec
        if action=="WAIT":
            duration=max(0,int(duration));self.tick+=duration;self.wait_units+=duration;return "WAITED"
        if action=="REPAIR_SCHEMA":
            s["schema_valid"]=True;return "SCHEMA_REPAIRED"
        if action=="ESCALATE":
            self.escalated=True;return "ESCALATED"
        if action=="VERIFY_CURRENT":
            if self.tick<s["visibility_delay"]:return "NOT_FOUND"
            return "NOT_FOUND" if self.current_outcome=="NONE" else self.current_outcome
        if action in ("RETRY_CURRENT","RETRY_CURRENT_WITH_KEY"):
            if not s["permission"]:return "PERMISSION_DENIED"
            if not s["schema_valid"]:return "SCHEMA_REJECTED"
            if self.tick<s["retry_after"]:return "RATE_LIMITED"
            c=s["steps"][s["step_index"]]
            dedup=(c["idempotency"]=="native" and action=="RETRY_CURRENT") or (c["idempotency"]=="keyed" and action=="RETRY_CURRENT_WITH_KEY")
            self.actions+=1
            if self.current_effects>0:
                if dedup:
                    return "ALREADY_COMMITTED" if self.current_outcome=="COMMITTED" else "ALREADY_PARTIAL"
                self.current_effects+=1;self.violation=True;return "DUPLICATE"
            self.current_outcome,self.current_effects="COMMITTED",1
            return "COMMITTED"
        if action=="COMPENSATE_CURRENT":
            c=s["steps"][s["step_index"]]
            self.actions+=1
            if (self.current_outcome in ("COMMITTED","PARTIAL") and c["compensable"]
                    and s["current_comp_available"]):
                self.current_outcome,self.current_effects="NONE",0
                self.compensated_current=True
                return "COMPENSATED"
            return "COMPENSATION_FAILED"
        if action=="COMPENSATE_PREVIOUS":
            self.actions+=1
            if not self.previous_stack or index!=self.previous_stack[-1]:
                self.violation=True;return "COMPENSATION_ORDER_VIOLATION"
            if s["previous_comp_failure_index"]==index:
                return "COMPENSATION_FAILED"
            self.previous_stack.pop();self.compensated_previous.append(index)
            return "COMPENSATED"
        if action=="RESUME":
            if self.current_outcome!="COMMITTED" or self.violation:
                return "CANNOT_RESUME"
            remaining=len(s["steps"])-s["step_index"]-1
            self.actions+=remaining
            self.current_outcome="WORKFLOW_COMPLETE"
            return "RESUMED"
        raise ValueError(action)

    def rollback(self):
        if self.current_outcome in ("COMMITTED","PARTIAL"):
            if self.act("COMPENSATE_CURRENT")!="COMPENSATED":
                self.act("ESCALATE")
        while self.previous_stack:
            idx=self.previous_stack[-1]
            if self.act("COMPENSATE_PREVIOUS",index=idx)!="COMPENSATED":
                self.act("ESCALATE")
                break
        if self.current_outcome=="NONE" and not self.previous_stack:
            self.rollback_complete=True

    def result(self):
        success=self.current_outcome=="WORKFLOW_COMPLETE" and not self.violation
        safe=success or self.rollback_complete or self.escalated
        return {
            "task_success":int(success),"safe_resolution":int(safe),
            "invariant_violation":int(self.violation),"unresolved":int(not safe),
            "escalated":int(self.escalated),"rollback_complete":int(self.rollback_complete),
            "tool_actions":self.actions,"wait_units":self.wait_units,
        }

def run_policy(spec,policy):
    env=Env(spec);obs=env.observe();c=obs["current_operation"];signals=set(obs["signals"])
    def retry():
        action="RETRY_CURRENT_WITH_KEY" if c["idempotency"]=="keyed" else "RETRY_CURRENT"
        result=env.act(action)
        if result in ("RATE_LIMITED","PERMISSION_DENIED","SCHEMA_REJECTED"):
            env.act("ESCALATE")
        return result
    def handle_partial():
        env.rollback()
    def resume_if_committed():
        if env.current_outcome=="COMMITTED":
            env.act("RESUME")
    if policy=="blind_retry":
        result=env.act("RETRY_CURRENT")
        if result in ("COMMITTED","ALREADY_COMMITTED"):resume_if_committed()
        elif result=="ALREADY_PARTIAL":handle_partial()
        elif result=="DUPLICATE":env.act("ESCALATE")
        else:
            env.rollback()
            env.act("ESCALATE")
    elif policy=="verify_then_retry":
        status=env.act("VERIFY_CURRENT")
        if status=="COMMITTED":env.act("RESUME")
        elif status=="PARTIAL":handle_partial()
        elif status=="NOT_FOUND":
            result=env.act("RETRY_CURRENT")
            if result in ("COMMITTED","ALREADY_COMMITTED"):resume_if_committed()
            elif result=="DUPLICATE":env.act("ESCALATE")
            else:
                env.rollback();env.act("ESCALATE")
    elif policy=="contract_resume":
        if not obs["permission"]:
            env.rollback();env.act("ESCALATE")
        else:
            if not obs["schema_valid"]:env.act("REPAIR_SCHEMA")
            if "RATE_LIMIT" in signals:env.act("WAIT",obs["retry_after"])
            if "PARTIAL_RESPONSE" in signals:
                handle_partial()
            elif "TIMEOUT" in signals:
                if c["idempotency"] in ("native","keyed"):
                    result=retry()
                    if result in ("COMMITTED","ALREADY_COMMITTED"):resume_if_committed()
                    elif result=="ALREADY_PARTIAL":handle_partial()
                    elif not env.escalated:
                        env.rollback();env.act("ESCALATE")
                else:
                    if c["consistency"]=="eventual":env.act("WAIT",c["max_visibility_delay"])
                    status=env.act("VERIFY_CURRENT")
                    if status=="COMMITTED":env.act("RESUME")
                    elif status=="PARTIAL":handle_partial()
                    elif status=="NOT_FOUND":
                        result=retry()
                        if result=="COMMITTED":env.act("RESUME")
                        elif not env.escalated:
                            env.rollback();env.act("ESCALATE")
            else:
                result=retry()
                if result in ("COMMITTED","ALREADY_COMMITTED"):resume_if_committed()
                elif result=="ALREADY_PARTIAL":handle_partial()
                elif not env.escalated:
                    env.rollback();env.act("ESCALATE")
    elif policy=="rollback_on_ambiguous":
        if c["consistency"]=="eventual":env.act("WAIT",c["max_visibility_delay"])
        status=env.act("VERIFY_CURRENT")
        if status=="NOT_FOUND":
            env.current_outcome="NONE"
        env.rollback()
    elif policy=="oracle_upper_bound":
        if not obs["permission"]:
            env.rollback();env.act("ESCALATE")
        else:
            if not obs["schema_valid"]:env.act("REPAIR_SCHEMA")
            if env.tick<obs["retry_after"]:env.act("WAIT",obs["retry_after"]-env.tick)
            if env.current_outcome=="COMMITTED":env.act("RESUME")
            elif env.current_outcome=="PARTIAL":handle_partial()
            else:
                result=retry()
                if result in ("COMMITTED","ALREADY_COMMITTED"):resume_if_committed()
                elif result=="ALREADY_PARTIAL":handle_partial()
                elif not env.escalated:
                    env.rollback();env.act("ESCALATE")
    else:raise ValueError(policy)
    return {"policy":policy,"task":spec["task"],"step_index":spec["step_index"],
            "fault_profile":spec["profile"],"seed":spec["seed"],**env.result()}

def mean_metrics(rows):
    n=len(rows)
    keys=("task_success","safe_resolution","invariant_violation","unresolved","escalated","rollback_complete","tool_actions","wait_units")
    return {k:round(sum(r[k] for r in rows)/n,6) for k in keys}

def paired_bootstrap(rows,policy_a,policy_b,metric,seeds,draws=10000):
    by=defaultdict(lambda:defaultdict(list))
    for r in rows:by[r["seed"]][r["policy"]].append(r[metric])
    diffs=[sum(by[s][policy_a])/len(by[s][policy_a])-sum(by[s][policy_b])/len(by[s][policy_b]) for s in seeds]
    rng=random.Random(20261105+len(metric))
    samples=sorted(sum(diffs[rng.randrange(len(diffs))] for _ in diffs)/len(diffs) for _ in range(draws))
    return {"mean_difference_A_minus_B":round(sum(diffs)/len(diffs),6),
            "ci95":[round(samples[int(.025*draws)],6),round(samples[min(draws-1,int(.975*draws))],6)],
            "n_seeds":len(seeds),"bootstrap_draws":draws}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",default="experiments/pilot_b2_multistep_saga/results")
    args=parser.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    rows=[run_policy(make_episode(task,step,profile,seed),policy)
          for policy in POLICIES for task in TASKS for step in range(3)
          for profile in PROFILES for seed in TEST_SEEDS]
    summary={
        "status":"EXPLORATORY_PILOT_B2",
        "design":{"tasks":list(TASKS),"profiles":list(PROFILES),"policies":list(POLICIES),
                  "steps_per_workflow":3,"train_seeds":[3000,3039],
                  "validation_seeds":[3100,3119],"heldout_test_seeds":[3120,3159],
                  "episodes_per_policy":len(TASKS)*3*len(PROFILES)*len(TEST_SEEDS),
                  "total_policy_episodes":len(rows),
                  "oracle_reads_hidden_state":True,
                  "no_llm_api":True,"no_a800_training":True,"no_ec_search":True},
        "heldout_test":{p:mean_metrics([r for r in rows if r["policy"]==p]) for p in POLICIES},
        "paired_bootstrap":{
            "contract_resume_vs_oracle_success":paired_bootstrap(rows,"contract_resume","oracle_upper_bound","task_success",TEST_SEEDS),
            "contract_resume_vs_oracle_actions":paired_bootstrap(rows,"contract_resume","oracle_upper_bound","tool_actions",TEST_SEEDS),
            "contract_resume_vs_verify_then_retry_success":paired_bootstrap(rows,"contract_resume","verify_then_retry","task_success",TEST_SEEDS),
            "contract_resume_vs_verify_then_retry_violations":paired_bootstrap(rows,"contract_resume","verify_then_retry","invariant_violation",TEST_SEEDS),
        },
        "limitations":["synthetic Saga simulator, not a production tool API","one injected fault per workflow plus compensation-failure variants","oracle sees hidden state and is diagnostic only","no EC algorithm or trained model in this pilot"]
    }
    with (out/"summary.json").open("w",encoding="utf-8") as f:json.dump(summary,f,indent=2,ensure_ascii=False)
    with (out/"episodes.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":main()
