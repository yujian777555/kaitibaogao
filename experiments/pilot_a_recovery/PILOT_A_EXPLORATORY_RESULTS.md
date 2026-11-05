# Pilot A — Exploratory result: stateful Agent recovery policy headroom

**Status: CONDITIONAL HOLD — first simulator slice completed; not a confirmatory experiment.**

## Design

- 7 fault families: timeout before dispatch, timeout after commit, partial commit, delayed visibility, rate limit, schema drift, permission denied.
- 10 deterministic seeds per fault family.
- 70 episodes per policy; 6 policies; 420 total policy-episodes.
- Policies: blind retry, verify-then-retry, wait-verify-retry, conservative escalation, state-aware rules, diagnostic oracle upper bound.
- Crucial leakage control: timeout-before-dispatch, timeout-after-commit and delayed-visibility expose the same public failure signature TIMEOUT. Only the oracle may inspect the hidden subtype.
- Critical invariant: retrying after a committed/partial side effect without reconciliation/compensation creates a duplicate-side-effect violation.

## Aggregate results

| Policy | Task success | Safe resolution | Duplicate side effect | Invariant violation | Unresolved | Mean actions |
|---|---:|---:|---:|---:|---:|---:|
| Blind retry | 0.1429 | 0.1429 | 0.4286 | 0.4286 | 0.8571 | 1.000 |
| Verify then retry | 0.4286 | 0.4286 | 0.1429 | 0.1429 | 0.5714 | 2.000 |
| Wait-verify-retry | 0.5571 | 0.5571 | 0.0857 | 0.0857 | 0.4429 | 2.943 |
| Conservative escalation | 0.7714 | 0.9143 | 0.0857 | 0.0857 | 0.0857 | 2.300 |
| State-aware rules | **0.8571** | **1.0000** | **0.0000** | **0.0000** | 0.2857 | 3.071 |
| Oracle upper bound | **0.8571** | **1.0000** | **0.0000** | **0.0000** | 0.0000 | **1.500** |

## Interpretation

1. The environment is nontrivial relative to naive retry: blind retry has 14.29% success and 42.86% duplicate-side-effect/invariant violation; the state-aware rule reaches 85.71% success and zero violations.
2. The best handcrafted state-aware policy matches the oracle on task success, safe resolution and invariant violations. Therefore this first small fault suite does **not** establish a remaining success-rate headroom for evolutionary search.
3. There is an action-efficiency gap (3.071 vs 1.500 mean actions), but it is not yet evidence of a meaningful algorithmic opportunity. The oracle has hidden subtype information, so its action count is only a diagnostic lower bound.
4. The conservative rule still violates the invariant in delayed-visibility cases, showing why a TIMEOUT signature alone cannot justify immediate retry.
5. No LLM API, A800 training, ARWM, evolutionary algorithm or confirmatory held-out evaluation was run.

## Gate decision

**Do not start A800 training or full evolutionary search yet.** The current Pilot A slice is too easy for a competent handcrafted policy on the primary success/safety objective. Continue only with a bounded Pilot A-2 that increases partial observability and compositionality without leaking hidden labels:
- multiple tools with different idempotency contracts;
- same public failure signature across more latent outcomes;
- two-stage/compound failures (e.g. timeout plus delayed visibility, partial commit plus retry-after);
- varying read staleness and compensation availability;
- task-family holdout and fault-composition holdout.

Pre-register these additions before generating the next evaluation set. If a simple observable-state rule still matches the oracle on success/safety and approaches its cost, stop the evolutionary-recovery direction. If a real gap remains, compare standard GA/GP with contract-aware evolutionary operators. Train ARWM only if the action-effect prediction task is demonstrably difficult for structured baselines and its predictions improve fixed-real-rollout-budget search.

## Reproducibility and limitations

- Code: `experiments/pilot_a_recovery/pilot_a.py`
- Tests: `experiments/pilot_a_recovery/test_pilot_a.py`
- Run: `python experiments/pilot_a_recovery/pilot_a.py`
- The reported numbers are exploratory deterministic simulator results, not independent-seed statistical evidence. Seeds vary delay parameters; fault families are fixed.
- A separate critical-transition regression check passed for collapsed timeout observations, duplicate prevention, partial compensation, delayed visibility and permission denial. The committed pytest file has not been run in GitHub Actions; only equivalent local transition assertions were executed.


## Audit correction (2026-11-05)

An independent re-execution of the committed simulator logic found that the original `unresolved` column had been transcribed incorrectly. The corrected values are shown in the table above and in `summary.json`: verify-then-retry 0.5714; wait-verify-retry 0.4429; conservative escalation 0.0857; state-aware 0; oracle 0. Blind retry remains 0.8571.

The correction follows the code definition `unresolved = int(not success and not resolved)`. In the state-aware and oracle policies, all non-success permission-denied cases are explicitly escalated, so unresolved is zero. Safe resolution remains 1.0 and task success remains 0.8571.

Seven transition/coverage assertions passed in an independent reproduction of the simulator logic. This is not a GitHub Actions result; no workflow run was available at the time of the audit. The report's previous wording implying an already completed local test run should not be treated as evidence of CI completion.

**Decision impact:** the primary success/safety comparison is unchanged: state-aware equals oracle on task success, safe resolution and invariant violations. The action-count gap remains diagnostic only because the oracle uses hidden subtype information. Pilot A remains exploratory and does not authorize A800 training or EC search.
