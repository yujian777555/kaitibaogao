# Pilot A-3 implementation status

**Status: IMPLEMENTED / CI VALIDATED AFTER REMEDIATION / RESULTS PENDING INDEPENDENT AUDIT**

## Added

- Frozen protocol: `47_PILOT_A3_PROTOCOL.md`
- Simulator: `pilot_a3.py`
- Regression tests: `test_pilot_a3.py`
- Workflow step: run Pilot A-3 after A1/A2 and upload JSON + episode-level CSV.

## Implemented mechanics

- Six three-step task families with train / validation / held-out task-family splits.
- Nine fault-composition families with separate train / validation / held-out composition splits.
- Per-tool fault vectors; faults are no longer broadcast to every tool in a task.
- Distinct idempotency and compensation contracts across ten tool types.
- Ambiguous public TIMEOUT for timeout-before, timeout-after-commit and delayed visibility.
- Partial commit, rate limit, schema drift, permission denial, variable visibility delay and compensation failure.
- Saga dependencies: no downstream step before prior commit; saga-aware policy compensates in reverse order.
- Public policy facade hides latent fault labels, true visibility time and compensation availability.
- Seven predeclared policies, including contract-aware, saga-aware and privileged diagnostic reference.
- Per-episode CSV, per-split/per-policy JSON, held-out worst-group summaries and paired cluster bootstrap.

## Frozen design budget

Per policy: 954 episodes (144 train, 120 validation, 690 held-out).  
Seven policies: 6,678 policy episodes.  
All policies share scenario IDs, seeds and fault realizations.

## Tests

Sixteen regression tests are authored: the original fifteen cover split disjointness, frozen budget, per-tool independent faults, timeout-observation collapse, policy information boundary, idempotent/non-idempotent retry, visibility SLA, reverse-order rollback, dependency stopping, compensation failure, paired scenario identity and reproducibility and slice-wise safety-gate enforcement. The sixteenth is a crash-regression test added during CI remediation (2026-11-06): every implementable policy is driven through `recover_tool` on a `PublicToolView` for every public error signature, so policy code can never again dereference hidden runtime fields.

## CI remediation (2026-11-06)

- Symptom: all A-3 workflow runs from `76f62c09` onward failed at the "Run Pilot A-3 simulator" step; artifact upload was skipped, so no A-3 result file ever existed.
- Root cause: `recover_tool` read `tool.tick` (a `ToolRuntime` field) through the restricted `PublicToolView`, which intentionally exposes only `contract`, `retry_after` and method calls. `AttributeError: 'PublicToolView' object has no attribute 'tick'`.
- Fix: implementable policies now count their own waits against the public `retry_after` hint instead of reading the runtime clock. `PublicToolView` is unchanged, so the policy-observation boundary stays exactly as tested. `oracle_recover` keeps privileged access to `tick`/`visible_at` because it receives the raw `ToolRuntime`.
- After the fix: 28 tests pass locally and `pilot_a3.py` completes, writing `pilot_a3_results.json` and `pilot_a3_episodes.csv`.

**Important:** The existence of tests and workflow configuration is not a test pass. Do not report A-3 results until the GitHub Actions run and uploaded artifacts have been inspected and independently recomputed. Do not start Pilot B, A800 training, ARWM or real LLM API evaluation before the A-3 gate is evaluated.
