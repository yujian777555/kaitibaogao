# Pilot A-2 — Multi-tool recovery benchmark

**Status:** EXPLORATORY RESULT COMPLETE / NO LLM API / NO A800 TRAINING / NO EC SEARCH  
**Run:** GitHub Actions 42022440268  
**Result commit:** fc4de5bf8117e852e88d3a3319b813428055a587

## 1. Experimental design

- 4 tool/task families: inventory reservation, order creation, calendar booking, ledger posting.
- Distinct declared contracts: native idempotency, key-based idempotency, no idempotency; compensability; strong/eventual read consistency and visibility bounds.
- 13 fault profiles, including before/after-dispatch timeout, committed timeout, partial commit, delayed visibility, rate-limit composites, schema failures, permission failures and partial outcomes with compensation unavailable.
- 100 deterministic parameter seeds.
- 8 policies; 5,200 episodes per policy; 41,600 policy-episodes total.
- Policies: blind retry, verify-then-retry, idempotency-only, conservative escalation, contract-basic, contract-bounded, contract-optimized, oracle upper bound.
- Public policy observation: tool/task family, declared contract, public failure signals, schema validity, permission result and retry-after header.
- Hidden simulator state is excluded from all executable policies. Only the diagnostic oracle reads hidden outcome/compensation state.
- Seeds 0–39 / 40–59 / 60–99 are labelled train / validation / held-out test parameter ranges. No learned model is fitted in this pilot; these labels are not a learned-model generalization split.
- Ledger is reported separately as a held-out tool family; transfer evidence is preliminary because it is one tool family and shares some contract properties with inventory.

## 2. Aggregate results

| Policy | Task success | Safe resolution | Invariant violation | Escalation | Mean tool actions | Wait units |
|---|---:|---:|---:|---:|---:|---:|
| Blind retry | 0.2308 | 0.2308 | 0.1923 | 0.0000 | 1.0000 | 0.0000 |
| Verify then retry | 0.3462 | 0.3462 | 0.0769 | 0.0000 | 1.9379 | 0.0000 |
| Idempotency only | 0.2885 | 0.4808 | 0.0000 | 0.2500 | 1.0000 | 0.0000 |
| Conservative escalation | 0.2308 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0000 |
| Contract basic | 0.6187 | 0.9154 | 0.0587 | 0.2967 | 2.1585 | 0.6129 |
| Contract bounded | 0.6998 | 1.0000 | 0.0000 | 0.3002 | 2.5000 | 1.9975 |
| **Contract optimized** | **0.6998** | **1.0000** | **0.0000** | **0.3002** | **2.3462** | **1.7090** |
| Oracle upper bound | 0.6998 | 1.0000 | 0.0000 | 0.3002 | 1.3921 | 0.6129 |

## 3. Held-out test results

Held-out parameter seeds 60–99, all four tool families:

| Policy | Task success | Safe resolution | Invariant violation | Mean tool actions |
|---|---:|---:|---:|---:|
| Contract basic | 0.6221 | 0.9178 | 0.0567 | 2.1611 |
| Contract bounded | 0.7000 | 1.0000 | 0.0000 | 2.5000 |
| **Contract optimized** | **0.7000** | **1.0000** | **0.0000** | **2.3462** |
| Oracle upper bound | 0.7000 | 1.0000 | 0.0000 | 1.3923 |

Held-out ledger tool family (seeds 60–99):

| Policy | Task success | Safe resolution | Invariant violation | Mean tool actions |
|---|---:|---:|---:|---:|
| Contract basic | 0.5385 | 1.0000 | 0.0000 | 1.9231 |
| Contract bounded | 0.5385 | 1.0000 | 0.0000 | 1.9231 |
| **Contract optimized** | **0.5385** | **1.0000** | **0.0000** | **1.8462** |
| Oracle upper bound | 0.5385 | 1.0000 | 0.0000 | 1.2308 |

## 4. Paired bootstrap diagnostics

Unit of resampling: seed, paired across policies; 10,000 bootstrap draws; held-out seeds 60–99.

- Contract-optimized minus contract-bounded task success: 0.0000, 95% interval [0.0000, 0.0000].
- Contract-optimized minus contract-bounded tool actions: -0.1538, 95% interval [-0.1538, -0.1538].
- Contract-optimized minus oracle task success: 0.0000, 95% interval [0.0000, 0.0000].
- Contract-optimized minus oracle tool actions: +0.9538, 95% interval [+0.9505, +0.9577].

The degenerate interval for contract-optimized vs bounded actions occurs because their per-seed action-count difference is constant in this deterministic design. It should not be interpreted as broad population-level statistical certainty.

## 5. Interpretation

1. Naive retry is unsafe: blind retry has 19.23% invariant violations on the full matrix.
2. A contract-aware policy using only declared contract and public observations reaches 69.98% task success, 100% safe resolution and zero invariant violations in this simulator.
3. The contract-optimized policy matches the diagnostic oracle on success/safety, including the held-out seed range and the held-out ledger tool family. Thus this pilot does not show a success-rate or safety gap for evolutionary search to close.
4. It does show an action-efficiency gap: contract-optimized averages 2.346 tool actions versus oracle 1.392. But the oracle uses hidden state and is not implementable; the gap is only a diagnostic lower bound, not evidence that EC can attain it.
5. Contract-optimized reduces mean tool actions from 2.500 to 2.346 relative to contract-bounded while preserving success/safety. This is a hand-designed rule comparison, not an evolutionary algorithm result.
6. Contract-basic still violates invariants because it verifies before the eventual-consistency visibility bound. This supports the need for explicit consistency contracts and bounded reconciliation.

## 6. Gate decision

**CONDITIONAL GO for a narrowly scoped Pilot B on cost-aware policy search; NO-GO for immediate A800 training.**

Do not claim that an evolutionary algorithm improves Agent recovery yet. Next compare:
- hand-designed contract-optimized controller;
- random valid finite-state controllers;
- standard GA/GP over the same controller grammar;
- contract-preserving GA/GP operators;
- NSGA-II/III feasibility-first multiobjective search.

Hard safety is a feasibility constraint, not a reward trade-off. Primary objective: minimize tool actions / wait cost subject to zero critical invariant violations and a pre-registered minimum task-success constraint. Use identical policy evaluation episodes, paired seeds and a separate held-out set. The search must outperform the strong hand-designed contract-optimized policy on cost without losing safety or task success.

Only if Pilot B demonstrates a repeatable EC advantage should ARWM be trained. ARWM then becomes a surrogate for action-effect/risk estimation, tested against LightGBM/MLP and under the same true rollout budget.

## 7. Limitations

- Synthetic deterministic simulator, not production tools or a real LLM Agent.
- Single-operation recovery episodes; no multi-step cross-tool transaction yet.
- Train/validation/test labels refer to parameter seed ranges, not learned-model splits.
- Ledger is one held-out tool family; generalization evidence is preliminary.
- Oracle reads hidden simulator state and is not an implementable baseline.
- No LLM API calls, A800 training, ARWM, GA/GP, NSGA-II/III or RSI loop was run.

## 8. Reproducibility

- Source: experiments/pilot_a2_multitool/pilot_a2.py
- Tests: experiments/pilot_a2_multitool/test_pilot_a2.py
- Raw episode rows: experiments/pilot_a2_multitool/results/episodes.csv
- Summary and paired bootstrap: experiments/pilot_a2_multitool/results/summary.json
- Workflow: .github/workflows/pilot-a2-multitool.yml
- Run command: python experiments/pilot_a2_multitool/pilot_a2.py
