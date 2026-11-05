# Pilot A — Stateful recovery policy headroom

Status: exploratory prototype; not a confirmatory experiment.

The pilot compares six policies over seven fault families and ten deterministic seeds per family (70 episodes per policy). Fault observations intentionally collapse timeout-before-dispatch, timeout-after-commit, and delayed-visibility into the same public `TIMEOUT` signature. Policies cannot read the hidden fault subtype. The oracle upper bound may use hidden simulator truth and is never an implementable baseline.

Metrics: task success, safe resolution, duplicate side effects, invariant violations, unresolved episodes, and tool actions.

This first pilot only tests whether hand-designed policies leave measurable headroom. It does not train ARWM, use an LLM API, or establish algorithm novelty. Any follow-up scenario changes must be treated as a new exploratory pilot, not held-out confirmation.

## Pilot A-3

Frozen protocol: `../../47_PILOT_A3_PROTOCOL.md`

Run locally:
```bash
python -m unittest discover -s experiments/pilot_a_recovery -p "test_*.py" -v
python experiments/pilot_a_recovery/pilot_a3.py
```

Pilot A-3 adds per-tool independent fault vectors, six three-step saga task families, separate task-family and fault-composition splits, partial commit, delayed visibility, compensation failure and reverse-order rollback. It writes `pilot_a3_results.json` and `pilot_a3_episodes.csv`; CI uploads both as `pilot-a3-results`.

Status report: `PILOT_A3_IMPLEMENTATION_STATUS.md`. Do not report A-3 as tested or gate-passed until the Actions run and artifacts have been inspected.
