# TCAIL Estimator-only Synthetic Diagnostic — Pilot

**Status:** EXPLORATORY / PROXY ONLY  
**Date:** 2026-11-04  
**Script:** experiments/tcail_estimator_gate_pilot/run_estimator_pilot.py

## Question

Does a task-block local posterior q/w score add useful signal beyond a simple local four-cell contrast, and does parent conditioning avoid the cancellation caused by pooling contexts with opposite interaction signs?

## Design

- 20 independent synthetic seeds; seeds 0–9 estimate the prior scale, seeds 10–19 are held-out.
- Each seed: 200 candidate pairs × 2 parent contexts.
- Per context: 20 positive, 20 negative, 20 sign-flipping across contexts, 20 weak (true |delta|=0.04), 120 null; 10 pairs are unsupported; 20 supported pairs have only 8 task blocks; other supported pairs have 128 blocks.
- Practical-effect threshold delta_local = 0.08; strong effects are ±0.20.
- Four Bernoulli cell outcomes are observed on the same task block. A shared additive block shift induces within-block dependence.
- The local posterior proxy uses paired block contrasts d_b = Y11 - Y10 - Y01 + Y00, a Normal(0,tau²) prior and a Normal likelihood for the mean contrast. tau is estimated by method of moments on training seeds only.
- Baselines: Student-t paired contrast, absolute local contrast, standardized local contrast, context-pooled absolute contrast.

This is not the full TCAIL M2/M3 Bernoulli GLMM. It is a deliberately small estimator diagnostic.

## Held-out results (seeds 10–19)

| Score | AUPRC |
|---|---:|
| EB posterior q | **0.802** |
| EB posterior w | 0.797 |
| Local standardized contrast | 0.785 |
| Student-t posterior q | 0.767 |
| Local raw absolute contrast | 0.619 |
| Context-pooled absolute contrast | 0.598 |

EB posterior q minus local standardized contrast:
- Mean per-seed AUPRC difference: **+0.0169**.
- Wins / ties / losses across 10 held-out seeds: **10 / 0 / 0**.
- Exact one-sided sign test: **p = 0.000977**.
- Bootstrap 95% CI over held-out seeds: **[0.0120, 0.0221]**.

Posterior q Brier score:
- EB q: **0.153**.
- Student-t q: **0.255**.

At EB q ≥ 0.8:
- Precision: **91.1%**.
- Recall: **38.1%**.
- False-positive rate: **1.57%**.

Support sensitivity:
- 128-block supported subset AUPRC: **0.830**.
- 8-block low-support subset AUPRC: **0.353**.

## Interpretation

This is a positive but small signal for an uncertainty-aware, shrinkage-based local q/w estimator over a simple local standardized contrast in this synthetic design. Context pooling loses substantial signal when true interaction signs flip between parent contexts.

It is not proof of TCAIL. The estimator is a normal-normal empirical-Bayes proxy, not the specified M2/M3 GLMM; the baselines are simple four-cell contrasts, not paper-exact FBL/scaled-FBLT; and the data generator is not a logistic GLMM. The low-support subset remains weak and must abstain rather than produce confident edges.

## Decision

Continue only to a direct, matched estimator comparison:
1. implement the specified local task-block model or an explicitly bounded approximation;
2. compare against paper-faithful FBL/scaled-FBLT and cDLED adaptations;
3. preserve held-out seeds/task blocks and raw per-pair contrasts;
4. test posterior calibration, null false-link rate, sign-flip recovery, abstention and FOS recovery;
5. stop if the q/w gain disappears against the faithful strong baselines.

No active acquisition, retry mechanism, real Agent API, A800 training, CI-GOM or IMCE-RSI was used.
