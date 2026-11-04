# TCAIL Estimator Pilot — Matched Scaled-FBL Adaptation

**Status:** EXPLORATORY / SYNTHETIC / NOT CONFIRMATORY  
**Date:** 2026-11-04

## 1. Direct comparison

The prior estimator-only diagnostic is extended with a task-block binary adaptation of the scaled fitness-based linkage (FBL) dependency measure. The original FBL paper defines the scaled pair dependency from the relative changes in the fitness effect of variable i under two settings of variable j, and gates dependency detection using a four-point fitness-difference tolerance. The adaptation here replaces deterministic real-valued fitness values with matched Bernoulli task-block success rates; it is not an original-paper reproduction.

For each pair/context, let:
- Δ_i|j=0 = mean(Y_10 - Y_00) across matched task blocks;
- Δ_i|j=1 = mean(Y_11 - Y_01) across matched task blocks.

The scaled score is:

\[
s^{FBL}_{ij}=1-
\frac{\min(|\Delta_{i|j=0}|,|\Delta_{i|j=1}|)}
{\max(|\Delta_{i|j=0}|,|\Delta_{i|j=1}|)}
\]

when the denominator is nonzero. The FBL-style edge gate uses epsilon equal to the 95th percentile of the absolute four-cell contrast on training null pairs. Its score is set to zero when the gate fails. The EB q threshold is independently calibrated to the 95th percentile of q on the same training null pairs. Thus the two edge gates target a matched training-null false-positive operating point.

## 2. Held-out design

- Seeds 0–9: prior-scale and null-threshold calibration only.
- Seeds 10–19: held-out evaluation only.
- 200 pairs × 2 parent contexts per seed.
- Positive, negative, parent-sign-flipping, weak, null, unsupported and low-support cases.
- 128 task blocks for ordinary supported pairs; 8 for low-support pairs.
- Same four-cell task-block data for EB q/w and FBL adaptation.
- Practical threshold 0.08; strong effect magnitude 0.20; weak effect magnitude 0.04.

## 3. Held-out results

| Score | AUPRC |
|---|---:|
| EB posterior q | **0.802** |
| EB posterior w | 0.797 |
| Local standardized contrast | 0.784 |
| Student-t posterior q | 0.767 |
| Local raw contrast | 0.619 |
| Context-pooled contrast | 0.598 |
| Scaled-FBL binary adaptation (epsilon-gated) | 0.414 |

Paired per-seed AUPRC, EB q minus scaled-FBL adaptation:
- Mean difference: **+0.3845**.
- Wins / ties / losses: **10 / 0 / 0**.
- Exact one-sided sign test: **p = 0.000977**.
- Bootstrap 95% CI over held-out seeds: **[0.3704, 0.3990]**.

At training-null-calibrated thresholds:
- EB q: threshold 0.651; precision 81.5%, recall 58.7%, FPR 5.62%.
- Scaled-FBL adaptation: epsilon 0.25; precision 69.7%, recall 31.5%, FPR 5.81%.

EB q Brier score is 0.153. Its AUPRC is 0.830 on 128-block supported pairs but only 0.353 on 8-block low-support pairs.

## 4. Decision and limitations

This is a **positive synthetic signal** that an uncertainty-aware empirical-Bayes local q/w proxy can outperform this task-block binary adaptation of scaled FBL under the specified data generator and matched training-null thresholds.

It does **not** establish that:
- the original real-valued FBL algorithm has been faithfully reproduced;
- TCAIL's specified M2/M3 Bernoulli GLMM has been implemented;
- the gain survives other landscape families, realistic logistic random effects, severe support sparsity or task drift;
- cDLED-P3M, CGOMEA or GAwLL2 have been beaten;
- the FOS or downstream GOM search improves;
- TCAIL is novel or publishable.

The low-support failure is material: 8-block pairs must be marked unresolved/abstain rather than forced into the FOS. Next, test on more synthetic families and paper-faithful FBL/scaled-FBLT, cDLED-P3M and GAwLL2 baselines before any active-acquisition experiment.

## 5. Reproduction

Install the existing requirements in this folder, then run:

    python run_fbl_comparison.py --output-dir results

The script writes the per-pair/context four-cell contrast data and JSON summary. Independent clean rerun is required.
