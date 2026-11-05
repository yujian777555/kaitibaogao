"""Pilot B3: fixed-budget evolutionary search over multi-step Saga controllers."""
from __future__ import annotations
import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from experiments.pilot_b2_multistep_saga.pilot_b2 import Env,TASKS,PROFILES,make_episode

WAIT_FACTORS=(0.0,0.5,1.0,1.25)
GENE_SIZES=(2,3,3,4,2,2,4,4,2,2)
GENOME_LEN=len(GENE_SIZES)
POPULATION=16
GENERATIONS=10
EVAL_BUDGET=POPULATION*GENERATIONS
ALGORITHM_SEEDS=(31,47,59)
ALGORITHMS=("random_valid_fsm","standard_ga","contract_preserving_ga","canonical_nsga2")
TRAIN_SEEDS=tuple(range(4000,4040))
VALIDATION_SEEDS=tuple(range(4100,4120))
TEST_SEEDS=tuple(range(4320,4360))
TASK_SUCCESS_FLOOR=0.0
ESCALATION_CEILING=1.0
COST_ESCALATION_WEIGHT=2.0

# Genome:
# 0 idempotent timeout: 0=same-key retry, 1=verify first
# 1 non-idempotent timeout: 0=wait+verify, 1=escalate, 2=immediate verify
# 2 partial response: 0=direct compensation, 1=wait+verify+compensate, 2=escalate
# 3 partial visibility wait factor; 4 schema: repair/escalate; 5 rate: wait/escalate
# 6 retry-after wait factor; 7 visibility wait factor; 8 use keyed idempotency key; 9 rollback completed prefix
MANUAL_SAGA=(0,0,0,0,0,0,2,2,0,1)
MANUAL_SAGA_VERIFY=(1,0,1,2,0,0,2,2,0,1)

def random_genome(rng):
    return tuple(rng.randrange(n) for n in GENE_SIZES)

def repair_contracts(genome):
    g=list(genome)
    g[1]=0
    if g[2]==1:g[3]=max(2,g[3])
    g[4]=0
    g[5]=0
    g[6]=max(2,g[6])
    g[7]=max(2,g[7])
    g[8]=0
    g[9]=1
    return tuple(g)

def rollback_observed(env,obs,include_prefix):
    failed=env.act("COMPENSATE_CURRENT")=="COMPENSATION_FAILED"
    if include_prefix:
        for idx in range(obs["step_index"]-1,-1,-1):
            if env.act("COMPENSATE_PREVIOUS",index=idx)!="COMPENSATED":
                failed=True
                break
    elif obs["step_index"]>0:
        failed=True
    if failed:
        env.act("ESCALATE")
    else:
        env.act("FINALIZE_ROLLBACK")

def execute_genome(spec,genome):
    env=Env(spec)
    obs=env.observe()
    c=obs["current_operation"]
    signals=set(obs["signals"])

    def retry():
        action="RETRY_CURRENT_WITH_KEY" if c["idempotency"]=="keyed" and genome[8]==0 else "RETRY_CURRENT"
        return env.act(action)

    def fail_and_rollback():
        rollback_observed(env,obs,bool(genome[9]))

    def handle_partial():
        if genome[2]==2:
            env.act("ESCALATE")
        elif genome[2]==1:
            if c["consistency"]=="eventual":
                env.act("WAIT",math.ceil(c["max_visibility_delay"]*WAIT_FACTORS[genome[3]]))
            status=env.act("VERIFY_CURRENT")
            if status=="PARTIAL":
                fail_and_rollback()
            else:
                env.act("ESCALATE")
        else:
            fail_and_rollback()

    def resume():
        env.act("RESUME")

    if not obs["permission"]:
        fail_and_rollback()
        env.act("ESCALATE")
    else:
        if not obs["schema_valid"]:
            if genome[4]==0:
                env.act("REPAIR_SCHEMA")
            else:
                fail_and_rollback()
                env.act("ESCALATE")

        if not env.escalated and "RATE_LIMIT" in signals:
            if genome[5]==0:
                env.act("WAIT",math.ceil(obs["retry_after"]*WAIT_FACTORS[genome[6]]))
            else:
                fail_and_rollback()
                env.act("ESCALATE")

        if not env.escalated:
            if "PARTIAL_RESPONSE" in signals:
                handle_partial()
            elif "TIMEOUT" in signals:
                if c["idempotency"] in ("native","keyed") and genome[0]==0:
                    result=retry()
                    if result in ("COMMITTED","ALREADY_COMMITTED"):
                        resume()
                    elif result=="ALREADY_PARTIAL":
                        handle_partial()
                    elif not env.escalated:
                        fail_and_rollback()
                        env.act("ESCALATE")
                elif c["idempotency"]=="none" and genome[1]==1:
                    fail_and_rollback()
                    env.act("ESCALATE")
                else:
                    if c["consistency"]=="eventual":
                        env.act("WAIT",math.ceil(c["max_visibility_delay"]*WAIT_FACTORS[genome[7]]))
                    status=env.act("VERIFY_CURRENT")
                    if status=="COMMITTED":
                        resume()
                    elif status=="PARTIAL":
                        handle_partial()
                    elif status=="NOT_FOUND":
                        result=retry()
                        if result in ("COMMITTED","ALREADY_COMMITTED"):
                            resume()
                        elif result=="ALREADY_PARTIAL":
                            handle_partial()
                        elif not env.escalated:
                            fail_and_rollback()
                            env.act("ESCALATE")
            else:
                result=retry()
                if result in ("COMMITTED","ALREADY_COMMITTED"):
                    resume()
                elif result=="ALREADY_PARTIAL":
                    handle_partial()
                elif not env.escalated:
                    fail_and_rollback()
                    env.act("ESCALATE")

    return env.result()

def evaluate(genome,seeds):
    rows=[execute_genome(make_episode(task,step,profile,seed),genome)
          for task in TASKS for step in range(3) for profile in PROFILES for seed in seeds]
    n=len(rows)
    m={
        "task_success":sum(r["task_success"] for r in rows)/n,
        "invariant_violation":sum(r["invariant_violation"] for r in rows)/n,
        "tool_actions":sum(r["tool_actions"] for r in rows)/n,
        "wait_units":sum(r["wait_units"] for r in rows)/n,
        "safe_resolution":sum(r["safe_resolution"] for r in rows)/n,
        "escalated_rate":sum(r["escalated"] for r in rows)/n,
        "rollback_complete_rate":sum(r["rollback_complete"] for r in rows)/n,
        "unresolved_rate":sum(r["unresolved"] for r in rows)/n,
    }
    m["feasible"]=int(
        m["invariant_violation"]==0
        and m["task_success"]>=TASK_SUCCESS_FLOOR
        and m["escalated_rate"]<=ESCALATION_CEILING
        and m["unresolved_rate"]==0
    )
    m["cost"]=m["tool_actions"]+0.1*m["wait_units"]+COST_ESCALATION_WEIGHT*m["escalated_rate"]
    return m

def fitness_key(m):
    return (0 if m["feasible"] else 1,m["invariant_violation"],
            max(0.0,TASK_SUCCESS_FLOOR-m["task_success"]),
            max(0.0,m["escalated_rate"]-ESCALATION_CEILING),
            m["cost"],-m["task_success"])

def mutate(g,rng):
    x=list(g)
    for _ in range(1+int(rng.random()<0.25)):
        j=rng.randrange(GENOME_LEN)
        x[j]=rng.randrange(GENE_SIZES[j])
    return tuple(x)

def crossover(a,b,rng):
    return tuple(a[i] if rng.random()<0.5 else b[i] for i in range(GENOME_LEN))

def tournament(pop,scores,rng,k=3):
    ids=[rng.randrange(len(pop)) for _ in range(k)]
    return min(ids,key=lambda i:fitness_key(scores[i]))

def dominates(a,b):
    av=(a["invariant_violation"],max(0,TASK_SUCCESS_FLOOR-a["task_success"]),
        max(0,a["escalated_rate"]-ESCALATION_CEILING),a["tool_actions"],a["wait_units"])
    bv=(b["invariant_violation"],max(0,TASK_SUCCESS_FLOOR-b["task_success"]),
        max(0,b["escalated_rate"]-ESCALATION_CEILING),b["tool_actions"],b["wait_units"])
    return all(x<=y for x,y in zip(av,bv)) and any(x<y for x,y in zip(av,bv))

def fronts(scores):
    n=len(scores);dominated=[[] for _ in range(n)];count=[0]*n;result=[[]]
    for p in range(n):
        for q in range(n):
            if p==q:continue
            if dominates(scores[p],scores[q]):dominated[p].append(q)
            elif dominates(scores[q],scores[p]):count[p]+=1
        if count[p]==0:result[0].append(p)
    i=0
    while i<len(result) and result[i]:
        nxt=[]
        for p in result[i]:
            for q in dominated[p]:
                count[q]-=1
                if count[q]==0:nxt.append(q)
        if nxt:result.append(nxt)
        i+=1
    return result

def rank_crowding(scores):
    fs=fronts(scores);rank={};distance={}
    for r,front in enumerate(fs):
        for i in front:rank[i]=r;distance[i]=0.0
        if len(front)<=2:
            for i in front:distance[i]=float("inf")
            continue
        for key in ("invariant_violation","task_success","escalated_rate","tool_actions","wait_units"):
            ordered=sorted(front,key=lambda i:scores[i][key])
            distance[ordered[0]]=distance[ordered[-1]]=float("inf")
            lo,hi=scores[ordered[0]][key],scores[ordered[-1]][key]
            if hi==lo:continue
            for j in range(1,len(ordered)-1):
                distance[ordered[j]]+=(scores[ordered[j+1]][key]-scores[ordered[j-1]][key])/(hi-lo)
    return rank,distance

def nsga_tournament(pop,scores,rng,k=2):
    rank,distance=rank_crowding(scores)
    ids=[rng.randrange(len(pop)) for _ in range(k)]
    return min(ids,key=lambda i:(rank[i],-distance[i]))

def nsga_select(pop,scores,size):
    chosen=[]
    for front in fronts(scores):
        if len(chosen)+len(front)<=size:
            chosen.extend(front)
        else:
            _,dist=rank_crowding(scores)
            chosen.extend(sorted(front,key=lambda i:dist[i],reverse=True)[:size-len(chosen)])
            break
    return [pop[i] for i in chosen],[scores[i] for i in chosen]

def search(algorithm,seed):
    rng=random.Random(seed)
    pop=[random_genome(rng) for _ in range(POPULATION)]
    if algorithm in ("random_valid_fsm","contract_preserving_ga"):
        pop=[repair_contracts(g) for g in pop]
    scores=[evaluate(g,TRAIN_SEEDS) for g in pop]
    evals=len(pop)
    while evals<EVAL_BUDGET:
        if algorithm=="random_valid_fsm":
            child=repair_contracts(random_genome(rng))
            pop.append(child);scores.append(evaluate(child,TRAIN_SEEDS));evals+=1
            order=sorted(range(len(pop)),key=lambda i:fitness_key(scores[i]))
            keep=order[:POPULATION]
            pop=[pop[i] for i in keep];scores=[scores[i] for i in keep]
        else:
            children=[]
            while len(children)<min(POPULATION,EVAL_BUDGET-evals):
                if algorithm=="canonical_nsga2":
                    ia=nsga_tournament(pop,scores,rng);ib=nsga_tournament(pop,scores,rng)
                else:
                    ia=tournament(pop,scores,rng);ib=tournament(pop,scores,rng)
                child=mutate(crossover(pop[ia],pop[ib],rng),rng)
                if algorithm=="contract_preserving_ga":child=repair_contracts(child)
                children.append(child)
            child_scores=[evaluate(g,TRAIN_SEEDS) for g in children]
            evals+=len(children)
            combined=pop+children;combined_scores=scores+child_scores
            if algorithm=="canonical_nsga2":
                pop,scores=nsga_select(combined,combined_scores,POPULATION)
            else:
                order=sorted(range(len(combined)),key=lambda i:fitness_key(combined_scores[i]))
                keep=order[:POPULATION]
                pop=[combined[i] for i in keep];scores=[combined_scores[i] for i in keep]
    best=min(range(len(pop)),key=lambda i:fitness_key(scores[i]))
    return {"algorithm":algorithm,"algorithm_seed":seed,"genome":list(pop[best]),
            "train_metrics":scores[best],"fitness_evaluations":evals}

def paired_bootstrap(rows_a,rows_b,metric,seeds,draws=10000):
    by_a=defaultdict(list);by_b=defaultdict(list)
    for r in rows_a:by_a[r["seed"]].append(r[metric])
    for r in rows_b:by_b[r["seed"]].append(r[metric])
    diffs=[sum(by_a[s])/len(by_a[s])-sum(by_b[s])/len(by_b[s]) for s in seeds]
    rng=random.Random(20261105+len(metric))
    samples=sorted(sum(diffs[rng.randrange(len(diffs))] for _ in diffs)/len(diffs) for _ in range(draws))
    return {"mean_difference_A_minus_B":round(sum(diffs)/len(diffs),6),
            "ci95":[round(samples[int(.025*draws)],6),round(samples[min(draws-1,int(.975*draws))],6)],
            "n_seeds":len(seeds),"bootstrap_draws":draws}

def evaluate_rows(genome,seeds,name):
    rows=[]
    for task in TASKS:
        for step in range(3):
            for profile in PROFILES:
                for seed in seeds:
                    rows.append({"policy":name,"task":task,"step_index":step,"profile":profile,"seed":seed,
                                 **execute_genome(make_episode(task,step,profile,seed),genome)})
    return rows

def summarize(rows):
    n=len(rows)
    keys=("task_success","safe_resolution","invariant_violation","tool_actions","wait_units")
    m={k:round(sum(r[k] for r in rows)/n,6) for k in keys}
    m["escalated_rate"]=round(sum(r["escalated"] for r in rows)/n,6)
    m["rollback_complete_rate"]=round(sum(r["rollback_complete"] for r in rows)/n,6)
    m["unresolved_rate"]=round(sum(r["unresolved"] for r in rows)/n,6)
    m["cost"]=round(m["tool_actions"]+0.1*m["wait_units"]+COST_ESCALATION_WEIGHT*m["escalated_rate"],6)
    m["episodes"]=n
    return m

def main():
    global TASK_SUCCESS_FLOOR, ESCALATION_CEILING
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",default="experiments/pilot_b3_saga_evolution/results")
    args=parser.parse_args()
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)

    manual_train=evaluate(MANUAL_SAGA,TRAIN_SEEDS)
    TASK_SUCCESS_FLOOR=max(0.0,manual_train["task_success"]-0.005)
    ESCALATION_CEILING=min(1.0,manual_train["escalated_rate"]+0.005)
    manual_train=evaluate(MANUAL_SAGA,TRAIN_SEEDS)

    runs=[]
    for algorithm in ALGORITHMS:
        for seed in ALGORITHM_SEEDS:
            runs.append(search(algorithm,seed))
    validation_cache={}
    for run in runs:
        key=tuple(run["genome"])
        if key not in validation_cache:validation_cache[key]=evaluate(key,VALIDATION_SEEDS)
        run["validation_metrics"]=validation_cache[key]

    selected={}
    for algorithm in ALGORITHMS:
        candidates=[r for r in runs if r["algorithm"]==algorithm]
        selected[algorithm]=min(candidates,key=lambda r:fitness_key(r["validation_metrics"]))

    test_rows={};test_summary={}
    for algorithm,run in selected.items():
        rows=evaluate_rows(tuple(run["genome"]),TEST_SEEDS,algorithm)
        test_rows[algorithm]=rows;test_summary[algorithm]=summarize(rows)
    for name,genome in (("manual_saga",MANUAL_SAGA),("manual_saga_verify",MANUAL_SAGA_VERIFY)):
        rows=evaluate_rows(genome,TEST_SEEDS,name)
        test_rows[name]=rows;test_summary[name]=summarize(rows)

    comparisons={}
    reference=test_rows["manual_saga"]
    for name,rows in test_rows.items():
        comparisons[name+"_vs_manual_saga_success"]=paired_bootstrap(rows,reference,"task_success",TEST_SEEDS)
        comparisons[name+"_vs_manual_saga_actions"]=paired_bootstrap(rows,reference,"tool_actions",TEST_SEEDS)
        comparisons[name+"_vs_manual_saga_escalation"]=paired_bootstrap(rows,reference,"escalated",TEST_SEEDS)

    all_rows=[r for rs in test_rows.values() for r in rs]
    with (out/"test_policy_episodes.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)

    summary={
        "status":"EXPLORATORY_PILOT_B3",
        "design":{
            "train_seeds":[4000,4039],"validation_seeds":[4100,4119],"test_seeds":[4320,4359],
            "previous_b3_test_seeds_not_reused":[4120,4159],
            "tasks":list(TASKS),"fault_profiles":list(PROFILES),
            "algorithms":list(ALGORITHMS),"algorithm_seeds":list(ALGORITHM_SEEDS),
            "population":POPULATION,"generations":GENERATIONS,"fitness_evaluation_budget_per_run":EVAL_BUDGET,
            "task_success_floor":TASK_SUCCESS_FLOOR,"floor_definition":"manual Saga train success minus 0.005",
            "escalation_rate_ceiling":ESCALATION_CEILING,
            "escalation_ceiling_definition":"manual Saga train escalation rate plus 0.005",
            "hard_constraints":["invariant_violation == 0","unresolved_rate == 0",
                                "escalated_rate <= manual_train_escalated_rate + 0.005",
                                "task_success >= manual_train_success - 0.005"],
            "cost":"mean tool_actions + 0.1 * mean wait_units + 2.0 * escalation_rate",
            "test_evaluated_once_after_validation_selection":True,
            "no_oracle_in_search":True,"no_llm_api":True,"no_a800_training":True,
        },
        "manual_train_metrics":manual_train,
        "search_runs":runs,
        "selected_by_validation":selected,
        "heldout_test":test_summary,
        "paired_bootstrap_vs_manual_saga":comparisons,
        "limitations":[
            "synthetic Saga simulator; not production tools or real Agent traces",
            "finite structured controller genome; not general program synthesis",
            "three workflow templates only",
            "test seeds disjoint from prior pilots",
            "no ARWM or RSI closed-loop experiment",
        ],
    }
    with (out/"summary.json").open("w",encoding="utf-8") as f:json.dump(summary,f,indent=2,ensure_ascii=False)
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=="__main__":main()
