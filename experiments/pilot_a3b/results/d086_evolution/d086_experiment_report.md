# D-086 exploratory evolutionary results

This is not a confirmatory statistical conclusion. No Test data or real LLM API was accessed.

- Decision: **NO_GO**
- Runs: 40 across 8 arms and 5 seeds.
- Raw evaluation rows: 316416.
- Failed criteria: ['r3_all_one', 'no_regression_vs_ea'].

| Arm | Seed | R3 | R4 | CondRec | R3 cost | Constraints | Train unique episodes |
|---|---:|---:|---:|---:|---:|---:|---:|
| RandomSearch | 711 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| RandomSearch | 822 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| RandomSearch | 933 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| RandomSearch | 1044 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| RandomSearch | 1155 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| NSGA-II | 711 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5976 |
| NSGA-II | 822 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| NSGA-II | 933 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| NSGA-II | 1044 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 5976 |
| NSGA-II | 1155 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| NSGA-III | 711 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| NSGA-III | 822 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| NSGA-III | 933 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| NSGA-III | 1044 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| NSGA-III | 1155 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| C-NSGA-III | 711 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| C-NSGA-III | 822 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 6048 |
| C-NSGA-III | 933 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5976 |
| C-NSGA-III | 1044 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 6048 |
| C-NSGA-III | 1155 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 5832 |
| Full/NoDependencyPriority | 711 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 5976 |
| Full/NoDependencyPriority | 822 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 5976 |
| Full/NoDependencyPriority | 933 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5760 |
| Full/NoDependencyPriority | 1044 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5832 |
| Full/NoDependencyPriority | 1155 | 0.8333 | 1.0000 | 1.0000 | 6.0000 | 0 | 5832 |
| Full/NoFailureFeedback | 711 | 1.0000 | 1.0000 | 1.0000 | 15.1667 | 0 | 5976 |
| Full/NoFailureFeedback | 822 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| Full/NoFailureFeedback | 933 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| Full/NoFailureFeedback | 1044 | 1.0000 | 1.0000 | 1.0000 | 5.0000 | 0 | 5904 |
| Full/NoFailureFeedback | 1155 | 1.0000 | 1.0000 | 1.0000 | 12.1667 | 0 | 5472 |
| Full/NoAlternate | 711 | 0.5000 | 0.0000 | 1.0000 | 10.6667 | 0 | 5832 |
| Full/NoAlternate | 822 | 0.5000 | 0.0000 | 1.0000 | 10.0000 | 0 | 5904 |
| Full/NoAlternate | 933 | 0.5000 | 0.0000 | 1.0000 | 10.0000 | 0 | 5904 |
| Full/NoAlternate | 1044 | 0.5000 | 0.0000 | 1.0000 | 10.6667 | 0 | 5904 |
| Full/NoAlternate | 1155 | 0.5000 | 0.0000 | 1.0000 | 10.6667 | 0 | 5760 |
| Full/NoPendingVerification | 711 | 0.1667 | 0.0000 | 1.0000 | 2.5000 | 0 | 5760 |
| Full/NoPendingVerification | 822 | 0.1667 | 0.0000 | 1.0000 | 2.5000 | 0 | 5976 |
| Full/NoPendingVerification | 933 | 0.0000 | 0.0000 | 1.0000 | 4.0000 | 0 | 5832 |
| Full/NoPendingVerification | 1044 | 0.0000 | 0.0000 | 1.0000 | 4.0000 | 0 | 5832 |
| Full/NoPendingVerification | 1155 | 0.0000 | 0.0000 | 1.0000 | 6.0000 | 0 | 5976 |
