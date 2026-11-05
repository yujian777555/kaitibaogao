# Pilot B2 — Multi-step cross-tool Saga recovery feasibility

**Status:** EXPLORATORY RESULT COMPLETE / CONTRACT-RESUME POLICY MATCHES ORACLE SUCCESS-SAFETY / NO EC SEARCH  
**GitHub Actions run:** 42024900989 (tests and full matrix success)  
**Result commit:** 8c93d436d29e3e9d61ad917b93931c42d27e3d97

## 1. Design

Three three-step workflows:
1. Order fulfillment: reserve inventory → create order → post ledger charge.
2. Appointment confirmation: reserve calendar slot → post deposit → confirm appointment.
3. Return/refund: cancel order → release inventory → post refund.

The simulator includes 11 fault profiles, including timeout before/after dispatch, partial commit, delayed visibility, rate-limit composites, schema and permission faults, current-step compensation failure and previous-step compensation failure. Faults are injected at each of the three workflow positions.

- 3 workflows × 3 fault positions × 11 profiles × 40 seeds = 3,960 episodes per policy.
- 5 policies; 19,800 policy-episodes total.
- Policies: blind retry, verify-then-retry, contract-resume Saga, rollback-on-ambiguous, diagnostic oracle.
- Policies see only public task progress, completed prefix, current operation contract, public failure signals, schema/permission and retry-after. Oracle alone sees hidden current outcome and compensation availability.
- Seeds 3120–3159 are a fixed exploratory evaluation panel. There is no training/validation split because no model or search is fitted in this pilot.

## 2. Held-out exploratory results

| Policy | Task success | Safe resolution | Invariant violation | Escalated | Rollback complete | Tool actions | Wait units |
|---|---:|---:|---:|---:|---:|---:|---:|
| Blind retry | 0.191919 | 0.757576 | 0.242424 | 0.696970 | 0.474747 | 4.323232 | 0 |
| Verify then retry | 0.282828 | 0.919192 | 0.080808 | 0.545455 | 0.484848 | 4.989899 | 0 |
| **Contract-resume Saga** | **0.545455** | **1.000000** | **0** | 0.242424 | 0.303030 | 4.101010 | 0.966667 |
| Rollback on ambiguous | 0 | 1.000000 | 0 | 0.151515 | 0.848485 | 4.969697 | 1.777778 |
| Oracle upper bound | 0.545455 | 1.000000 | 0 | 0.242424 | 0.303030 | 3.606061 | 0.360606 |

## 3. Paired bootstrap diagnostics

Unit: seed, paired across policies; 10,000 draws; 40 seeds.

- Contract-resume minus oracle task success: 0.000000, 95% interval [0, 0].
- Contract-resume minus oracle tool actions: +0.494949, 95% interval [+0.494949, +0.494949].
- Contract-resume minus verify-then-retry success: +0.262626, 95% interval [+0.262626, +0.262626].
- Contract-resume minus verify-then-retry invariant violations: -0.080808, 95% interval [-0.080808, -0.080808].

The intervals are degenerate because this is a deterministic seed/profile design with constant per-seed aggregate differences. They are descriptive diagnostics, not evidence of population-level statistical certainty.

## 4. Interpretation

1. Cross-tool workflow dependencies make naive retry materially unsafe: blind retry has 24.24% invariant violations.
2. Verify-then-retry still has 8.08% invariant violations because immediate reads can be stale and compensation dependencies span multiple prior steps.
3. Contract-resume Saga reaches the oracle's task success (54.55%) and safe resolution (100%) with zero invariant violations in this simulator.
4. The oracle uses hidden current state, so its 0.495 lower mean tool-action count is diagnostic only. Contract-resume is the best implementable policy in this pilot.
5. Rollback-on-ambiguous is safe but never completes the task, demonstrating that indiscriminate rollback is not an adequate recovery policy.
6. This pilot establishes a meaningful transactional recovery task and a strong rule-based baseline. It does not establish an EC improvement.

## 5. Gate decision

**CONDITIONAL GO for Pilot B3: evolutionary search over multi-step Saga recovery controllers. A800/ARWM remains HOLD.**

Pilot B3 should search a workflow-level controller grammar that decides:
- resume current step vs verify vs retry with idempotency key;
- when to wait for read visibility;
- when to compensate current step;
- reverse-order compensation of the completed prefix;
- when to escalate after compensation failure.

Compare contract-resume Saga, random valid workflow FSM, standard GA/GP, contract-preserving GA/GP and canonical NSGA-II/III. Use equal fitness budgets and new seeds, distinct from 3120–3159. Hard invariant violations remain a feasibility constraint; task success must not fall below the contract-resume baseline; optimize tool calls and wait cost. If random search matches the strong Saga policy, or EC cannot improve cost without reducing safety/success, stop the EC claim.

## 6. Limitations

- Synthetic Saga simulator, not production APIs or a real LLM Agent.
- One injected failure per workflow plus compensation-failure variants.
- Only three workflow templates.
- Oracle uses hidden state and is diagnostic only.
- No GA/GP, NSGA-II/III, A800 training, ARWM, LLM API or RSI loop was run.

## 7. Reproducibility

- Simulator: experiments/pilot_b2_multistep_saga/pilot_b2.py
- Tests: experiments/pilot_b2_multistep_saga/test_pilot_b2.py
- Raw episodes: experiments/pilot_b2_multistep_saga/results/episodes.csv
- Summary: experiments/pilot_b2_multistep_saga/results/summary.json
- Workflow: .github/workflows/pilot-b2-multistep-saga.yml
