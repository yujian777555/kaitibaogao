# TCAIL Oracle Linkage Gate — Pilot Results

**Status:** EXPLORATORY PILOT / G2-ORACLE PRECONDITION ONLY  
**Date:** 2026-11-04  
**Experiment:** experiments/tcail_oracle_gate_pilot/run_oracle_gate.py

## 1. Question

Before spending effort on TCAIL's posterior estimator and active acquisition, test the necessary EC premise: if the correct local interaction groups were known, would a GOM-style optimizer benefit from using them under the same maximum objective-evaluation budget?

If oracle linkage cannot help, learned linkage is unlikely to rescue the linkage-to-GOM hypothesis. A positive oracle result is necessary but not sufficient for TCAIL.

## 2. Experimental setup

- Binary search space: 40 variables.
- Population: 50.
- Maximum objective evaluations: 5,000, including initial population evaluations.
- Paired seeds: 20 for the deceptive trap; 12 for additive control.
- Same simplified GOM mixing routine, donor selection, random subset order and evaluation cap across methods.
- Stop on global optimum, budget exhaustion, or 150 generations without strict improvement.
- Oracle, learned LT and random FOS each contain 79 subsets; singleton has 40.
- All methods start from the same initial population within each seed.

### Deceptive epistatic landscape

Ten disjoint 4-bit blocks. For each block with u ones:

\[
f_{\mathrm{trap4}}(u)=
\begin{cases}
4,&u=4\\
3-u,&u<4.
\end{cases}
\]

Total optimum is 40, attained by all-one blocks. The true linkage partition is the ten known 4-bit blocks.

### Additive control

\[
f_{\mathrm{add}}(x)=\sum_{i=1}^{40}x_i.
\]

This control has no epistatic structure and should not reward a special block linkage.

## 3. Methods

1. **Oracle FOS:** true 4-bit blocks, hierarchical subsets inside blocks, then merge block roots.
2. **Learned LT:** empirical pairwise mutual information from the current population, average-linkage tree rebuilt each generation.
3. **Random FOS:** randomized binary hierarchy with the same 79-subset count as Oracle/LT.
4. **Singleton:** only one-variable subsets.

All four use the same simplified GOM prototype. This is not claimed to be an official GOMEA implementation.

## 4. Deceptive trap results

| Method | Mean best / 40 | SD | Median | Global optimum |
|---|---:|---:|---:|---:|
| Oracle FOS | **39.55** | 0.686 | 40 | **13/20 (65%)** |
| Learned LT | 38.55 | 0.887 | 39 | 2/20 (10%) |
| Random FOS | 33.80 | 0.768 | 34 | 0/20 |
| Singleton | 33.60 | 0.681 | 33.5 | 0/20 |

Oracle minus Learned LT, paired by seed:
- Mean paired difference: **+1.00 / 40**.
- Wins / ties / losses: **13 / 6 / 1**.
- Exact one-sided sign test: p = 0.000916.
- One-sided paired Wilcoxon signed-rank: p = 0.000919.
- Paired bootstrap 95% CI for mean difference: **[0.55, 1.45]**.
- Success table: both success 2; Oracle-only 11; Learned-only 0; neither 7.
- Exact one-sided McNemar/binomial test on discordant successes: p = 0.000488.

Oracle also exceeds Random by 5.75 objective points on average (20/20 paired wins), and Singleton by 5.95 points (20/20 paired wins).

Mean actual evaluations used before stopping: Oracle 3,603; Learned LT 4,709; Random 5,000; Singleton 5,000. The cap is equal, but actual evaluations are lower when a method converges/stalls under the shared stopping rule; report both objective quality and actual cost.

## 5. Additive control

With 12 paired seeds, all four methods reached the global optimum 40/40 in all 12 runs:
- Oracle FOS: 12/12.
- Learned LT: 12/12.
- Random FOS: 12/12.
- Singleton: 12/12.

This is consistent with the expected boundary: special linkage is useful on this deceptive epistatic problem, but does not improve the final optimum on the additive control. Mean evaluations to termination were 1,919 (Oracle), 1,988 (Learned LT), 1,941 (Random), and 1,505 (Singleton).

## 6. Decision

**G2 Oracle precondition: POSITIVE on this synthetic landscape family.**

The result supports only this narrow claim: correctly supplied 4-bit linkage groups can materially improve a simplified GOM prototype on a concatenated deceptive 4-bit trap landscape, compared with population-MI LT, random linkage and singleton mixing.

It does **not** prove that TCAIL can estimate those groups; that posterior q/w is better calibrated than FBL/cDLED; that active acquisition is useful; that the gain persists on overlapping, higher-order, constrained or noisy landscapes; that the result transfers to stochastic Agent rollouts; or that TCAIL is novel/publishable.

No TCAIL algorithm was implemented. No LLM API, A800 training, CI-GOM or IMCE-RSI was used.

## 7. Next experiment — shortest route to testing TCAIL

Do not revise the full specification or add more theory modules. Run an **estimator-only synthetic gate with fixed full-factorial observations**, deliberately avoiding the unresolved acquisition and retry mechanisms:

1. Generate task-block Bernoulli outcomes from known parent-conditioned pair interactions, including null, weak, strong, sign-flipping and unsupported pairs.
2. Give every estimator the same complete four-cell task-block observations and the same episode-equivalent budget.
3. Compare TCAIL local posterior q/w (initial transparent prototype; calibration claims remain provisional), FBL/scaled FBLT adaptation, pooled/global interaction score and oracle local graph.
4. Evaluate edge precision/recall, AUPRC, null false-link rate, sign-flip recovery, abstention and FOS recovery.
5. Only if TCAIL is calibrated and improves on FBL/scaled FBLT should active acquisition be tested.

The fixed full-factorial design means this next gate does not rely on the currently unresolved R2 acquisition interval or retry ledger. It tests the central local-interaction estimator directly.

## 8. Reproduction

Install requirements and run:

    python run_oracle_gate.py --seeds 20 --budget 5000 --additive-seeds 12

The script writes per-seed CSV and a JSON summary. Results in this document are recorded pilot outputs; independent clean rerun is still required before confirmatory claims.
