# Pilot B — Fixed-budget evolutionary search on single-operation recovery controllers

**Status:** EXPLORATORY RESULT COMPLETE / NO ALGORITHM IMPROVEMENT OVER STRONG HAND-CODED POLICY  
**GitHub Actions run:** 42023597413 (success)  
**Result commit:** 4f254ab41001c98b32c9d1eb61a3373744c3b397

## 1. Design

- Reused the Pilot A-2 simulator mechanism but used new, disjoint seed ranges:
  - train: 1000–1039;
  - validation: 1100–1119;
  - held-out test: 1120–1159.
- 4 tools × 13 fault profiles × 40 train seeds = 2,080 episodes per candidate fitness evaluation.
- Population 16 × 10 generations = 160 fitness evaluations per search run.
- 3 algorithm seeds (13, 29, 47) per search method.
- Methods: random contract-valid FSM search, standard GA, contract-preserving GA, and an NSGA-II-style hybrid (nondominated environmental selection with scalar feasibility-first mating tournament).
- Strong hand-coded baselines: contract-optimized v1 (verify then compensate) and v2 (direct compensation on explicit partial response).
- Objective: invariant violations = 0 hard constraint; task success ≥ 0.70; minimize mean tool actions + 0.1 × wait units.
- Oracle not used in search. No A800 training, ARWM, real LLM API or RSI loop.

## 2. Held-out test results

| Method | Task success | Safe resolution | Invariant violation | Mean tool actions | Wait units | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Random valid FSM | 0.701923 | 1.000000 | 0 | 1.923077 | 1.196154 | 2.042692 |
| Standard GA | 0.701923 | 1.000000 | 0 | 1.923077 | 1.196154 | 2.042692 |
| Contract-preserving GA | 0.701923 | 1.000000 | 0 | 1.923077 | 1.196154 | 2.042692 |
| NSGA-II-style hybrid | 0.701923 | 1.000000 | 0 | 1.923077 | 1.196154 | 2.042692 |
| Manual contract v1 | 0.701923 | 1.000000 | 0 | 2.384615 | 1.811538 | 2.565769 |
| **Manual contract v2** | **0.701923** | **1.000000** | **0** | **1.923077** | **1.196154** | **2.042692** |

All search methods selected the same effective policy as manual v2 on held-out test. Their paired difference from manual v2 was exactly zero for task success and tool actions (40 paired test seeds; 10,000 bootstrap draws).

Manual v2 improved on manual v1 by 0.461538 mean tool actions while preserving success and safety. This is a hand-designed rule refinement, not an evolutionary algorithm gain.

## 3. Interpretation

1. The single-operation controller grammar is too easy / low-dimensional for the current search budget: random valid search, standard GA, contract-preserving GA and the NSGA-II-style hybrid all recover the same effective policy.
2. There is no evidence that GA or contract-preserving operators outperform random search or the strong hand-coded v2 policy.
3. The search result therefore does **not** establish an EC algorithmic contribution. It is a negative result for this problem representation and simulator complexity.
4. The result does not show that evolutionary recovery control is impossible in richer stateful workflows. It shows that this single-operation task family does not provide enough search difficulty or structural interaction to demonstrate an EC advantage.
5. The current NSGA-II implementation is an NSGA-II-style hybrid: it uses nondominated sorting/crowding for environmental selection but scalar feasibility-first tournament selection for mating. It is not a canonical NSGA-II reproduction and must be corrected before any definitive NSGA-II comparison.

## 4. Gate decision

**NO-GO for claiming an EC innovation from the current single-operation grammar. CONDITIONAL GO for a new multi-step transactional workflow pilot. A800/ARWM remains HOLD.**

The next pilot should model multi-step cross-tool transactions, not merely add more one-step fault labels. Candidate workflows:
- reserve inventory → create order → post ledger entry;
- reserve calendar slot → charge deposit → confirm booking;
- cancel order → release inventory → issue refund.

The simulator must model transaction dependencies, partial commits across steps, reverse-order compensation, idempotency keys per operation, delayed reads and failures during compensation. Recovery policies must decide whether to resume, reconcile, compensate or escalate at workflow level.

Only if the richer workflow leaves measurable headroom between strong hand-coded Saga/recovery policies and an oracle, should we compare random FSM, canonical GA/GP, contract-preserving operators and canonical NSGA-II/III under equal evaluation budgets.

## 5. Limitations

- Synthetic simulator and single-operation recovery episodes.
- Genome is a small structured rule vector, not general program synthesis.
- Current NSGA-II is a hybrid as described above.
- 160 fitness evaluations per run and three optimizer seeds; exploratory budget only.
- Paired bootstrap intervals are degenerate because all search methods selected the same effective policy.
- No A800, ARWM, LLM API or RSI experiment was run.

## 6. Reproducibility

- Code: experiments/pilot_b_policy_search/pilot_b.py
- Tests: experiments/pilot_b_policy_search/test_pilot_b.py
- Raw test episodes: experiments/pilot_b_policy_search/results/test_policy_episodes.csv
- Summary: experiments/pilot_b_policy_search/results/summary.json
- Workflow: .github/workflows/pilot-b-policy-search.yml
