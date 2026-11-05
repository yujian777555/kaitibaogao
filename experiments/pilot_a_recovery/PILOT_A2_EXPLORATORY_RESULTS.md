# Pilot A-2 — multi-tool compositional recovery simulator

**Status: EXPLORATORY SIGNAL FOUND / NOT CONFIRMATORY / NO ALGORITHM CLAIM**

## Design

- Four two-tool task families: inventory→order, calendar→charge, inventory→ledger, calendar→order.
- Nine fault families: timeout-before, timeout-after, partial commit, stale read, rate limit, timeout+stale-read, partial-commit+rate-limit, schema drift, permission denied.
- 30 deterministic parameter seeds per task/fault cell.
- Six policies × 4 tasks × 9 faults × 30 seeds = 6,480 policy episodes; 1,080 per policy.
- Policies: blind retry, verify-retry, fixed-wait-verify, escalate-on-unknown, contract-aware, oracle diagnostic.
- Policies receive public observations only. Timeout latent subtypes share TIMEOUT; only oracle diagnostic reads latent fault labels.
- Tools have distinct idempotency and compensation contracts. Ledger is non-compensatable; calendar is idempotent; inventory/order/ledger are non-idempotent.

## Aggregate results

| Policy | Task success | Safe | Duplicate | Invariant violation | Unresolved | Escalated | Mean actions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Blind retry | 0.1111 | 0.5556 | 0.4444 | 0.4444 | 0.8889 | 0.0000 | 2.000 |
| Verify-retry | 0.2778 | 0.7778 | 0.2222 | 0.2222 | 0.6111 | 0.1111 | 4.111 |
| Fixed-wait-verify | 0.5815 | 0.9148 | 0.0852 | 0.0852 | 0.3074 | 0.1111 | 9.7778 |
| Escalate-on-unknown | 0.5556 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.7778 | 2.6667 |
| Contract-aware | **0.7222** | **1.0000** | **0.0000** | **0.0000** | **0.0556** | 0.2222 | 5.5167 |
| Oracle diagnostic | 0.7778 | 1.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2222 | 3.7778 |

## Initial interpretation

1. The richer multi-tool task family creates measurable headroom: contract-aware policy reaches 0.7222 task success versus the diagnostic oracle 0.7778, while both have zero invariant violations. This is a 5.56 percentage-point gap in this simulator, not yet a statistical claim.
2. Contract-aware policy improves task success by 16.67 points over fixed-wait-verify (0.7222 vs 0.5815) and maintains zero invariant violations, but uses fewer actions than fixed-wait-verify (5.52 vs 9.78).
3. Escalate-on-unknown is safe but escalates 77.78% of episodes and only succeeds in 55.56%; it illustrates the safety/utility trade-off.
4. Blind retry violates invariants in 44.44% of episodes, confirming the importance of effect-state and tool-contract handling.
5. The oracle is diagnostic only and has access to latent fault labels; it is not an implementable baseline.

## Critical limitations / model defects to fix before confirmatory use

- The current task simulator applies the same fault family to both tools in a task. This is a controlled first slice, not realistic independent/compositional fault placement. Next version must independently sample per-tool faults and include cross-step dependencies.
- The seed only changes delay/retry parameters; task and fault families are fixed. This is not a genuine held-out task/fault generalization experiment.
- The contract-aware controller uses public contract fields directly; it is a handcrafted strong baseline, not an evolved strategy.
- The oracle has hidden fault subtype access, so its score is only a loose diagnostic upper bound.
- No statistical significance, EC improvement or ARWM benefit is established.

## Gate decision

**CONDITIONAL GO to Pilot A-3 simulator refinement and standard EA feasibility test; NO-GO for A800 training now.**

The primary result is promising enough to test whether EC can close the remaining gap and improve recovery cost without violating safety. Before claiming the optimization space is robust, implement independent per-tool faults, multi-stage saga rollback, variable compensation availability and a genuinely held-out task/fault-composition split. Then compare hand-coded contract-aware baseline, random policy search, GA/GP and contract-aware EA at identical real simulator rollout budgets.

Train ARWM only after the action-outcome model has a nontrivial prediction task and can be shown to improve fixed-rollout-budget search over LightGBM/MLP and no-surrogate EA.

## Reproducibility

- Simulator: `experiments/pilot_a_recovery/pilot_a2.py`
- Tests: `experiments/pilot_a_recovery/test_pilot_a2.py`
- CI run: https://github.com/yujian777555/kaitibaogao/actions/runs/42030194929
- 12/12 tests passed; both Pilot A baseline and Pilot A-2 simulator steps passed.
- Output includes per-policy aggregate and per-task/per-fault stratified results in CI logs; JSON is also written to `pilot_a2_summary.json` in the runner workspace. Artifact upload is configured separately.
