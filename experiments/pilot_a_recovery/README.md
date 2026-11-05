# Pilot A — Stateful recovery policy headroom

Status: exploratory prototype; not a confirmatory experiment.

The pilot compares six policies over seven fault families and ten deterministic seeds per family (70 episodes per policy). Fault observations intentionally collapse timeout-before-dispatch, timeout-after-commit, and delayed-visibility into the same public `TIMEOUT` signature. Policies cannot read the hidden fault subtype. The oracle upper bound may use hidden simulator truth and is never an implementable baseline.

Metrics: task success, safe resolution, duplicate side effects, invariant violations, unresolved episodes, and tool actions.

This first pilot only tests whether hand-designed policies leave measurable headroom. It does not train ARWM, use an LLM API, or establish algorithm novelty. Any follow-up scenario changes must be treated as a new exploratory pilot, not held-out confirmation.