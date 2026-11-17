# D-091 independent audit artifact

This artifact reads saved D-090 evidence. It does not run genome search, select candidates, access Validation/Test, train models, or call an LLM.

| Gate | Status |
|---|---|
| DATA_INTEGRITY | PASS_WITH_LIMITATIONS |
| METRIC_RECOMPUTE | PASS |
| METHOD_IDENTITY | FAIL |
| PHENOTYPE_DIVERSITY | FAIL |
| R2_REACHABILITY | CLAIM_FALSIFIED |
| ABLATION_SAFETY | FAIL |

## Evidence

- Search best rows: 1440; fixed-ablation rows: 480; maximum metric difference: 0.0.
- Candidate genomes: 8/15; trace phenotypes: 1; outcome signatures: 1.
- The `random` label follows the NSGA-II path; `state_evo` uses a static mutation profile. Actual proposal/operator/generation logs are NOT_AUDITABLE_FROM_SAVED_TRACE.
- g03-r2 witness decisions: 23; BFS shortest: 21; historical 25-step claim: CLAIM_FALSIFIED.
- P2/P4 preserve hard-constraint failures; no Harm or cost improvement can compensate them.

The historical 25-step lower bound is withdrawn. Equal aggregate search metrics are not evidence of algorithmic improvement or a fair independent Random Search comparison.
