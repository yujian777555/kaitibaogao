#!/usr/bin/env python3
"""Estimator-only task-block interaction pilot; not the full TCAIL GLMM."""
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
    d = np.asarray(d, dtype=float)
    n = len(d)
    if n == 0:
        return np.nan, np.nan
    mean = float(d.mean())
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    if sd < 1e-12:
        return float(abs(mean) > delta), float(max(abs(mean) - delta, 0.0))
    df = n - 1
    scale = sd / np.sqrt(n)
    q = float(student_t.sf((delta - mean) / scale, df=df) +
              student_t.cdf((-delta - mean) / scale, df=df))
    def positive_part(location, threshold):
        z = (threshold - location) / scale
        survival = student_t.sf(z, df=df)
        density = student_t.pdf(z, df=df)
        tail_first_moment = ((df + z*z) / (df - 1)) * density
        return scale * (tail_first_moment - z * survival)
    w = positive_part(mean, delta) + positive_part(-mean, delta)
    return q, float(w)

def normal_posterior_qw(mean, se, delta, tau):
    prior_var, se_var = tau*tau, se*se
    denom = prior_var + se_var
    if denom <= 0:
        post_mean, post_sd = 0.0, 0.0
    else:
        post_mean = prior_var / denom * mean
        post_sd = np.sqrt(prior_var * se_var / denom)
    if post_sd <= 1e-12:
        return float(abs(post_mean) > delta), float(max(abs(post_mean)-delta, 0.0))
    q = norm.cdf((-delta-post_mean)/post_sd) + norm.sf((delta-post_mean)/post_sd)
    z1 = (delta-post_mean)/post_sd
    z2 = (delta+post_mean)/post_sd
    w_pos = post_sd*norm.pdf(z1) + (post_mean-delta)*norm.sf(z1)
    w_neg = post_sd*norm.pdf(z2) + (-post_mean-delta)*norm.sf(z2)
    return float(q), float(w_pos+w_neg)

def simulate_seed(seed, n_pairs=200, n_contexts=2, b_full=128, b_low=8):
    rng = np.random.default_rng(seed)
    classes = (["pos"]*20 + ["neg"]*20 + ["flip"]*20 +
               ["weak"]*20 + ["null"]*120)
    rng.shuffle(classes)
    unsupported = set(rng.choice(n_pairs, size=10, replace=False).tolist())
    low_support = set(rng.choice(
        [i for i in range(n_pairs) if i not in unsupported],
        size=20, replace=False).tolist())
    rows, context_data, pooled_signed = [], {}, {}
    for pair_id, cls in enumerate(classes):
        base = float(rng.uniform(0.32, 0.62))
        main_i = float(rng.uniform(-0.025, 0.025))
        main_j = float(rng.uniform(-0.025, 0.025))
        for context in range(n_contexts):
            if pair_id in unsupported:
                rows.append({
                    "seed":seed,"pair":pair_id,"context":context,"class":cls,
                    "true_delta":np.nan,"supported":0,"n_blocks":0,
                    "block_contrasts":"","mean_d":np.nan,"se":np.nan,
                    "q_student":np.nan,"w_student":np.nan,"raw":np.nan,
                    "zscore":np.nan,"label":np.nan,"pooled_abs":np.nan,
                    "q_eb":np.nan,"w_eb":np.nan
                })
                continue
            target = {"pos":0.20,"neg":-0.20,
                      "flip":(0.20 if context == 0 else -0.20),
                      "weak":0.04,"null":0.0}[cls]
            p_cells = np.asarray([
                base, base+main_i, base+main_j,
                base+main_i+main_j+target
            ])
            n_blocks = b_low if pair_id in low_support else b_full
            contrasts = []
            for _ in range(n_blocks):
                shared_block_shift = float(rng.normal(0, 0.04))
                probabilities = np.clip(p_cells+shared_block_shift, 0.02, 0.98)
                y = rng.binomial(1, probabilities)
                contrasts.append(int(y[3]-y[1]-y[2]+y[0]))
            q_s, w_s = student_qw(contrasts)
            mean_d = float(np.mean(contrasts))
            se = float(np.std(contrasts, ddof=1) / np.sqrt(n_blocks))
            zscore = abs(mean_d) / (se + 0.015)
            label = int(abs(target) > DELTA)
            rows.append({
                "seed":seed,"pair":pair_id,"context":context,"class":cls,
                "true_delta":target,"supported":1,"n_blocks":n_blocks,
                "block_contrasts":";".join(map(str, contrasts)),
                "mean_d":mean_d,"se":se,"q_student":q_s,"w_student":w_s,
                "raw":abs(mean_d),"zscore":zscore,"label":label,
                "pooled_abs":np.nan,"q_eb":np.nan,"w_eb":np.nan
            })
            context_data[(pair_id,context)] = contrasts
    for pair_id in range(n_pairs):
        all_contrasts = [v for (i,_),v in context_data.items() if i == pair_id]
        if all_contrasts:
            pooled_signed[pair_id] = float(np.mean(np.concatenate(
                [np.asarray(v,dtype=float) for v in all_contrasts])))
    for row in rows:
        if row["supported"]:
            row["pooled_abs"] = abs(pooled_signed[row["pair"]])
    return rows

def average_precision(rows, score):
    y = np.asarray([r["label"] for r in rows], dtype=int)
    s = np.asarray([r[score] for r in rows], dtype=float)
    return float(average_precision_score(y,s))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--full-blocks", type=int, default=128)
    parser.add_argument("--low-blocks", type=int, default=8)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for seed in TRAIN_SEEDS + TEST_SEEDS:
        rows.extend(simulate_seed(seed, b_full=args.full_blocks, b_low=args.low_blocks))
    train = [r for r in rows if r["supported"] and r["seed"] in TRAIN_SEEDS]
    train_means = np.asarray([r["mean_d"] for r in train])
    train_se2 = np.asarray([r["se"]**2 for r in train])
    tau = float(np.sqrt(max(np.var(train_means,ddof=1)-np.mean(train_se2),0.0001)))

    test = [r for r in rows if r["supported"] and r["seed"] in TEST_SEEDS]
    for r in test:
        r["q_eb"], r["w_eb"] = normal_posterior_qw(r["mean_d"],r["se"],DELTA,tau)

    per_seed = []
    for seed in TEST_SEEDS:
        subset = [r for r in test if r["seed"] == seed]
        per_seed.append({
            "seed":seed,
            "ap_q_eb":average_precision(subset,"q_eb"),
            "ap_w_eb":average_precision(subset,"w_eb"),
            "ap_zscore":average_precision(subset,"zscore"),
            "ap_raw":average_precision(subset,"raw"),
            "ap_pooled":average_precision(subset,"pooled_abs"),
        })
    differences = np.asarray([r["ap_q_eb"]-r["ap_zscore"] for r in per_seed])
    wins = int(np.sum(differences>0))
    rng = np.random.default_rng(777)
    bootstrap = np.asarray([
        rng.choice(differences,size=len(differences),replace=True).mean()
        for _ in range(20000)
    ])
    y = np.asarray([r["label"] for r in test],dtype=int)
    qeb = np.asarray([r["q_eb"] for r in test],dtype=float)
    qstudent = np.asarray([r["q_student"] for r in test],dtype=float)
    selected = qeb >= 0.8
    tp = int(np.sum(selected & (y==1)))
    fp = int(np.sum(selected & (y==0)))
    fn = int(np.sum((~selected) & (y==1)))
    low = [r for r in test if r["n_blocks"]==args.low_blocks]
    full = [r for r in test if r["n_blocks"]==args.full_blocks]
    summary = {
        "design":{
            "train_seeds":list(TRAIN_SEEDS),"test_seeds":list(TEST_SEEDS),
            "pairs_per_seed":200,"contexts":2,"delta_local":DELTA,
            "strong_delta":0.20,"weak_delta":0.04,
            "full_task_blocks":args.full_blocks,"low_support_blocks":args.low_blocks,
            "unsupported_pairs_per_seed":10,"shared_block_shift_sd":0.04,
            "eb_prior":"Normal(0,tau^2), tau estimated by method of moments on train seeds only",
            "tau":tau
        },
        "test":{
            "n_supported_pair_contexts":len(test),
            "positive_labels":int(y.sum()),
            "ap":{
                "eb_q":average_precision(test,"q_eb"),
                "eb_w":average_precision(test,"w_eb"),
                "student_t_q":average_precision(test,"q_student"),
                "student_t_w":average_precision(test,"w_student"),
                "local_zscore":average_precision(test,"zscore"),
                "local_raw_abs_contrast":average_precision(test,"raw"),
                "context_pooled_abs_contrast":average_precision(test,"pooled_abs")
            },
            "brier":{
                "eb_q":float(np.mean((qeb-y)**2)),
                "student_t_q":float(np.mean((qstudent-y)**2))
            },
            "q_eb_threshold_0_8":{
                "precision":tp/max(tp+fp,1),
                "recall":tp/max(tp+fn,1),
                "false_positive_rate":fp/max(int(np.sum(y==0)),1),
                "selected":int(selected.sum())
            },
            "low_support_ap_eb_q":average_precision(low,"q_eb"),
            "full_support_ap_eb_q":average_precision(full,"q_eb"),
            "per_seed_ap":per_seed,
            "paired_ap_q_eb_minus_zscore":{
                "mean":float(differences.mean()),
                "wins_ties_losses":[wins,int(np.sum(differences==0)),int(np.sum(differences<0))],
                "exact_sign_test_one_sided_p":float(binomtest(wins,len(differences),0.5,alternative="greater").pvalue),
                "bootstrap_95pct_ci":[float(np.quantile(bootstrap,.025)),float(np.quantile(bootstrap,.975))]
            }
        },
        "limitations":[
            "This is a paired task-block normal-normal empirical-Bayes proxy, not the full TCAIL M2/M3 GLMM.",
            "The shared block effect is an additive probability-scale perturbation, not a fitted logistic random-intercept GLMM.",
            "The raw/z-score baselines are simple four-cell contrasts, not exact FBL or scaled-FBLT reproductions.",
            "Synthetic pilot only; no active acquisition, retry ledger, FOS-to-GOM evaluation or real Agent rollout.",
            "Low-support performance remains poor and requires explicit abstention/support gates."
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
