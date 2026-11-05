#!/usr/bin/env python3
"""Matched task-block comparison: EB local q/w vs a scaled-FBL binary adaptation."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
from scipy.stats import norm, t as student_t, binomtest
from sklearn.metrics import average_precision_score, roc_auc_score

DELTA = 0.08
TRAIN_SEEDS = tuple(range(10))
TEST_SEEDS = tuple(range(10, 20))

def student_qw(d, delta=DELTA):
    d=np.asarray(d,dtype=float); n=len(d)
    if n==0: return np.nan,np.nan
    mean=float(d.mean()); sd=float(d.std(ddof=1)) if n>1 else 0.0
    if sd<1e-12: return float(abs(mean)>delta),float(max(abs(mean)-delta,0.0))
    df=n-1; scale=sd/np.sqrt(n)
    q=float(student_t.sf((delta-mean)/scale,df=df)+student_t.cdf((-delta-mean)/scale,df=df))
    def positive_part(location,threshold):
        z=(threshold-location)/scale
        surv=student_t.sf(z,df=df); density=student_t.pdf(z,df=df)
        first_moment=((df+z*z)/(df-1))*density
        return scale*(first_moment-z*surv)
    w=positive_part(mean,delta)+positive_part(-mean,delta)
    return q,float(w)

def normal_qw(mean,se,delta,tau):
    prior_var,se_var=tau*tau,se*se
    denom=prior_var+se_var
    if denom<=0: post_mean,post_sd=0.0,0.0
    else:
        post_mean=prior_var/denom*mean
        post_sd=np.sqrt(prior_var*se_var/denom)
    if post_sd<=1e-12:
        return float(abs(post_mean)>delta),float(max(abs(post_mean)-delta,0.0))
    q=norm.cdf((-delta-post_mean)/post_sd)+norm.sf((delta-post_mean)/post_sd)
    z1=(delta-post_mean)/post_sd; z2=(delta+post_mean)/post_sd
    w1=post_sd*norm.pdf(z1)+(post_mean-delta)*norm.sf(z1)
    w2=post_sd*norm.pdf(z2)+(-post_mean-delta)*norm.sf(z2)
    return float(q),float(w1+w2)

def paper_signed_fbl(delta_i,delta_ij):
    if delta_i == 0.0 and delta_ij == 0.0:
        return 0.0
    if delta_i >= delta_ij:
        if delta_i == 0.0:
            return float("nan")
        return 1.0-delta_ij/delta_i
    if delta_ij == 0.0:
        return float("nan")
    return 1.0-delta_i/delta_ij


def simulate_seed(seed,n_pairs=200,b_full=128,b_low=8):
    rng=np.random.default_rng(seed)
    classes=(["pos"]*20+["neg"]*20+["flip"]*20+["weak"]*20+["null"]*120)
    rng.shuffle(classes)
    unsupported=set(rng.choice(n_pairs,size=10,replace=False).tolist())
    low_support=set(rng.choice([i for i in range(n_pairs) if i not in unsupported],
                               size=20,replace=False).tolist())
    rows=[]; context_data={}; pooled_signed={}
    for pair_id,cls in enumerate(classes):
        base=float(rng.uniform(.32,.62))
        main_i=float(rng.uniform(-.025,.025))
        main_j=float(rng.uniform(-.025,.025))
        for context in range(2):
            if pair_id in unsupported:
                rows.append({
                    "seed":seed,"pair":pair_id,"context":context,"class":cls,
                    "true_delta":np.nan,"supported":0,"n_blocks":0,"block_contrasts":"","block_cell_outcomes":"",
                    "mean_d":np.nan,"se":np.nan,"mean_i_j0":np.nan,"mean_i_j1":np.nan,
                    "q_student":np.nan,"w_student":np.nan,"raw":np.nan,"zscore":np.nan,
                    "fbl_scaled":np.nan,"fbl_abs_ungated":np.nan,
                    "fbl_abs_epsilon_zero":np.nan,"fbl_paper_signed":np.nan,
                    "fbl_gate_difference":np.nan,"fbl_paper_domain_violation":np.nan,
                    "pooled_abs":np.nan,"label":np.nan,
                    "q_eb":np.nan,"w_eb":np.nan,"fbl_calibrated":np.nan
                })
                continue
            target={"pos":.20,"neg":-.20,"flip":(.20 if context==0 else -.20),
                    "weak":.04,"null":0.0}[cls]
            p_cells=np.asarray([base,base+main_i,base+main_j,
                                base+main_i+main_j+target])
            n_blocks=b_low if pair_id in low_support else b_full
            ymat=[]
            for _ in range(n_blocks):
                shared_shift=float(rng.normal(0,.04))
                probs=np.clip(p_cells+shared_shift,.02,.98)
                ymat.append(rng.binomial(1,probs))
            ymat=np.asarray(ymat,dtype=int)
            d=ymat[:,3]-ymat[:,1]-ymat[:,2]+ymat[:,0]
            delta_i_j0=ymat[:,1]-ymat[:,0]
            delta_i_j1=ymat[:,3]-ymat[:,2]
            q_s,w_s=student_qw(d)
            mean_d=float(d.mean())
            se=float(d.std(ddof=1)/np.sqrt(n_blocks))
            zscore=abs(mean_d)/(se+.015)
            mean0=float(delta_i_j0.mean())
            mean1=float(delta_i_j1.mean())
            denom=max(abs(mean0),abs(mean1))
            # Existing absolute-ratio adaptation,kept separate from Eq.(7).
            fbl_scaled=0.0 if denom<1e-9 else 1.0-min(abs(mean0),abs(mean1))/denom
            paper_score=paper_signed_fbl(mean0,mean1)
            gate_difference=abs(mean0-mean1)
            domain_violation=int((not np.isfinite(paper_score)) or
                                 paper_score<0.0 or paper_score>=1.0)
            rows.append({
                "seed":seed,"pair":pair_id,"context":context,"class":cls,
                "true_delta":target,"supported":1,"n_blocks":n_blocks,
                "block_contrasts":";".join(map(str,d.tolist())),
                "block_cell_outcomes":";".join(",".join(map(str,row.tolist())) for row in ymat),
                "mean_d":mean_d,"se":se,"mean_i_j0":mean0,"mean_i_j1":mean1,
                "q_student":q_s,"w_student":w_s,"raw":abs(mean_d),
                "zscore":zscore,"fbl_scaled":float(fbl_scaled),
                "fbl_abs_ungated":float(fbl_scaled),
                "fbl_abs_epsilon_zero":float(fbl_scaled if gate_difference>=0.0 else 0.0),
                "fbl_paper_signed":float(paper_score),
                "fbl_gate_difference":float(gate_difference),
                "fbl_paper_domain_violation":domain_violation,
                "pooled_abs":np.nan,"label":int(abs(target)>DELTA),
                "q_eb":np.nan,"w_eb":np.nan,"fbl_calibrated":np.nan
            })
            context_data[(pair_id,context)]=d
    for pair_id in range(n_pairs):
        ds=[v for (i,_),v in context_data.items() if i==pair_id]
        if ds: pooled_signed[pair_id]=float(np.mean(np.concatenate(ds)))
    for r in rows:
        if r["supported"]: r["pooled_abs"]=abs(pooled_signed[r["pair"]])
    return rows

def ap(rows,score):
    return float(average_precision_score(
        np.asarray([r["label"] for r in rows],dtype=int),
        np.asarray([r[score] for r in rows],dtype=float)))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",type=Path,default=Path("results"))
    parser.add_argument("--full-blocks",type=int,default=128)
    parser.add_argument("--low-blocks",type=int,default=8)
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for seed in TRAIN_SEEDS+TEST_SEEDS:
        rows.extend(simulate_seed(seed,b_full=args.full_blocks,b_low=args.low_blocks))
    train=[r for r in rows if r["supported"] and r["seed"] in TRAIN_SEEDS]
    train_means=np.asarray([r["mean_d"] for r in train])
    train_se2=np.asarray([r["se"]**2 for r in train])
    tau=float(np.sqrt(max(np.var(train_means,ddof=1)-np.mean(train_se2),.0001)))
    train_null=[r for r in train if r["class"]=="null"]
    q_threshold=float(np.quantile([
        normal_qw(r["mean_d"],r["se"],DELTA,tau)[0] for r in train_null
    ],.95))
    fbl_epsilon=float(np.quantile([r["raw"] for r in train_null],.95))
    for r in train:
        r["q_eb"],r["w_eb"]=normal_qw(r["mean_d"],r["se"],DELTA,tau)
    for r in rows:
        if r["supported"] and r["seed"] in TEST_SEEDS:
            r["q_eb"],r["w_eb"]=normal_qw(r["mean_d"],r["se"],DELTA,tau)
            # FBL is first thresholded by the four-point difference epsilon,
            # then its scaled dependency strength is used as the ranking score.
            r["fbl_calibrated"]=r["fbl_scaled"] if r["raw"]>=fbl_epsilon else 0.0
    test=[r for r in rows if r["supported"] and r["seed"] in TEST_SEEDS]
    y=np.asarray([r["label"] for r in test],dtype=int)
    qeb=np.asarray([r["q_eb"] for r in test],dtype=float)
    q_student=np.asarray([r["q_student"] for r in test],dtype=float)
    q_pred=qeb>=q_threshold
    fbl_pred=np.asarray([r["fbl_calibrated"]>0 for r in test])
    def operating(pred):
        tp=int(np.sum(pred&(y==1))); fp=int(np.sum(pred&(y==0)))
        fn=int(np.sum((~pred)&(y==1)))
        return {"precision":tp/max(tp+fp,1),"recall":tp/max(tp+fn,1),
                "fpr":fp/max(int(np.sum(y==0)),1),"selected":int(pred.sum())}
    per_seed=[]
    for seed in TEST_SEEDS:
        sub=[r for r in test if r["seed"]==seed]
        paper_sub=[r for r in sub if r["fbl_paper_domain_violation"]==0]
        per_seed.append({"seed":seed,"ap_q_eb":ap(sub,"q_eb"),
                         "ap_fbl_scaled":ap(sub,"fbl_calibrated"),
                         "ap_fbl_abs_ungated":ap(sub,"fbl_abs_ungated"),
                         "ap_fbl_abs_epsilon_zero":ap(sub,"fbl_abs_epsilon_zero"),
                         "ap_fbl_paper_signed":ap(paper_sub,"fbl_paper_signed") if paper_sub else float("nan"),
                         "paper_valid_n":len(paper_sub),
                         "ap_zscore":ap(sub,"zscore")})
    differences=np.asarray([r["ap_q_eb"]-r["ap_fbl_scaled"] for r in per_seed])
    wins=int(np.sum(differences>0))
    rng=np.random.default_rng(20261104)
    boot=np.asarray([rng.choice(differences,size=len(differences),replace=True).mean()
                     for _ in range(20000)])
    low=[r for r in test if r["n_blocks"]==args.low_blocks]
    full=[r for r in test if r["n_blocks"]==args.full_blocks]
    paper_valid=[r for r in test if r["fbl_paper_domain_violation"]==0]
    summary={
        "design":{
            "train_seeds":list(TRAIN_SEEDS),"test_seeds":list(TEST_SEEDS),
            "pairs_per_seed":200,"contexts":2,"delta_local":DELTA,
            "strong_delta":.20,"weak_delta":.04,"full_task_blocks":args.full_blocks,
            "low_support_blocks":args.low_blocks,"unsupported_pairs_per_seed":10,
            "shared_probability_shift_sd":.04,
            "eb_prior":"Normal(0,tau^2); method-of-moments tau fitted on train seeds only",
            "tau":tau,"q_threshold_from_train_null_95pct":q_threshold,
            "fbl_epsilon_from_train_null_95pct":fbl_epsilon
        },
        "heldout":{
            "n_supported_pair_contexts":len(test),"positive_labels":int(y.sum()),
            "auprc":{
                "eb_q":ap(test,"q_eb"),"eb_w":ap(test,"w_eb"),
                "scaled_fbl_adaptation":ap(test,"fbl_calibrated"),
                "scaled_fbl_abs_ungated":ap(test,"fbl_abs_ungated"),
                "scaled_fbl_abs_epsilon_zero":ap(test,"fbl_abs_epsilon_zero"),
                "fbl_paper_signed_valid_only":ap(paper_valid,"fbl_paper_signed"),
                "student_t_q":ap(test,"q_student"),"local_zscore":ap(test,"zscore"),
                "local_raw_contrast":ap(test,"raw"),"context_pooled":ap(test,"pooled_abs")
            },
            "fbl_paper_signed_domain":{
                "valid_n":len(paper_valid),"total_supported_n":len(test),
                "violation_n":len(test)-len(paper_valid),
                "warning":"Valid-only AUPRC excludes undefined/out-of-range Eq.(7) outputs and is not a complete fair baseline result."
            },
            "brier_q":{
                "eb_q":float(np.mean((qeb-y)**2)),
                "student_t_q":float(np.mean((q_student-y)**2))
            },
            "matched_null_calibration_operating_points":{
                "eb_q":operating(q_pred),"scaled_fbl_adaptation":operating(fbl_pred)
            },
            "low_support_eb_q_auprc":ap(low,"q_eb"),
            "full_support_eb_q_auprc":ap(full,"q_eb"),
            "per_seed":per_seed,
            "paired_seed_ap_difference_q_minus_fbl":{
                "mean":float(differences.mean()),
                "wins_ties_losses":[wins,int(np.sum(differences==0)),int(np.sum(differences<0))],
                "exact_sign_test_one_sided_p":float(binomtest(
                    wins,len(differences),.5,alternative="greater").pvalue),
                "bootstrap_95pct_ci":[float(np.quantile(boot,.025)),
                                      float(np.quantile(boot,.975))]
            }
        },
        "limitations":[
            "This is a binary task-block adaptation of scaled FBL, not an original-paper reproduction.",
            "The EB q/w model is a Normal-normal paired-contrast proxy, not the TCAIL M2/M3 GLMM.",
            "The shared block effect is an additive probability perturbation, not a logistic GLMM.",
            "The synthetic task distribution is deliberately narrow; more landscapes and independent reruns are required.",
            "Low-support edge recovery remains poor; unresolved pairs must abstain.",
            "The pre-existing fbl_scaled score is an absolute-ratio adaptation, not Eq.(7)'s signed ratio.",
            "Paper-signed Eq.(7) is audited separately; undefined/out-of-range outputs are flagged and excluded only from its explicitly valid-only diagnostic.",
            "The calibrated epsilon and zero-epsilon/no-gate diagnostics are distinct; no original-paper threshold equivalence is claimed."
        ]
    }
    raw_path=args.output_dir/"per_pair_context_raw.csv"
    with raw_path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)
    summary_path=args.output_dir/"summary.json"
    summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print("Wrote:",raw_path,"and",summary_path)

if __name__=="__main__":
    main()
