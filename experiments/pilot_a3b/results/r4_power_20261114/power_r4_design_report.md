# D-064-R4 — ICC / Type-I / power re-calibration

- Input raw SHA-256: 2946bcf97883c74c407a204d5ce50bb325e4597a47be4831ccaff4ef8a4f414c
- Input canonical-content SHA-256: 9b1d90279852843bf93d92e66dab3e726ff1e19bc14b94e07ba260fc34eb68a7
- Code commit: 013f5174d125ed96df4bab5f9237f389e37399f5
- Repetitions per cell: 10000
- Base seed: 20261114
- Pilot total variance: 0.10166903
- Empirical residual pool size: 42
- Design: 5 frozen primary compositions/family; F=33 boundary, F=34 minimum eligible, F=40 planned

## Results

| F | ICC | Role | μ | Rejection rate | MCSE | 95% Wilson CI | Eligible |
|---:|---:|---|---:|---:|---:|---|---|
| 33 | 0.00 | null_type_i | 0.00 | 0.0490 | 0.0022 | [0.0449, 0.0534] | False |
| 33 | 0.00 | mde_power | 0.10 | 0.9788 | 0.0014 | [0.9758, 0.9814] | False |
| 33 | 0.05 | null_type_i | 0.00 | 0.0475 | 0.0021 | [0.0435, 0.0518] | False |
| 33 | 0.05 | mde_power | 0.10 | 0.9507 | 0.0022 | [0.9463, 0.9548] | False |
| 33 | 0.10 | null_type_i | 0.00 | 0.0522 | 0.0022 | [0.0480, 0.0567] | False |
| 33 | 0.10 | mde_power | 0.10 | 0.9121 | 0.0028 | [0.9064, 0.9175] | False |
| 33 | 0.20 | null_type_i | 0.00 | 0.0482 | 0.0021 | [0.0442, 0.0526] | False |
| 33 | 0.20 | mde_power | 0.10 | 0.8308 | 0.0037 | [0.8233, 0.8380] | False |
| 34 | 0.00 | null_type_i | 0.00 | 0.0479 | 0.0021 | [0.0439, 0.0523] | True |
| 34 | 0.00 | mde_power | 0.10 | 0.9798 | 0.0014 | [0.9769, 0.9824] | True |
| 34 | 0.05 | null_type_i | 0.00 | 0.0508 | 0.0022 | [0.0467, 0.0553] | True |
| 34 | 0.05 | mde_power | 0.10 | 0.9529 | 0.0021 | [0.9486, 0.9569] | True |
| 34 | 0.10 | null_type_i | 0.00 | 0.0489 | 0.0022 | [0.0448, 0.0533] | True |
| 34 | 0.10 | mde_power | 0.10 | 0.9197 | 0.0027 | [0.9142, 0.9249] | True |
| 34 | 0.20 | null_type_i | 0.00 | 0.0503 | 0.0022 | [0.0462, 0.0548] | True |
| 34 | 0.20 | mde_power | 0.10 | 0.8427 | 0.0036 | [0.8354, 0.8497] | True |
| 40 | 0.00 | null_type_i | 0.00 | 0.0507 | 0.0022 | [0.0466, 0.0552] | True |
| 40 | 0.00 | mde_power | 0.10 | 0.9912 | 0.0009 | [0.9892, 0.9929] | True |
| 40 | 0.05 | null_type_i | 0.00 | 0.0498 | 0.0022 | [0.0457, 0.0542] | True |
| 40 | 0.05 | mde_power | 0.10 | 0.9781 | 0.0015 | [0.9750, 0.9808] | True |
| 40 | 0.10 | null_type_i | 0.00 | 0.0490 | 0.0022 | [0.0449, 0.0534] | True |
| 40 | 0.10 | mde_power | 0.10 | 0.9523 | 0.0021 | [0.9479, 0.9563] | True |
| 40 | 0.20 | null_type_i | 0.00 | 0.0547 | 0.0023 | [0.0504, 0.0593] | True |
| 40 | 0.20 | mde_power | 0.10 | 0.9028 | 0.0030 | [0.8968, 0.9085] | True |

## Technical-missing sensitivity (MCAR at composition-cluster level)

| F design | Missing rate | Role | Mean complete F | Eligibility rate | Conditional rejection when eligible | Joint rejection rate |
|---:|---:|---|---:|---:|---:|---:|
| 34 | 0.00% | null_type_i | 34.00 | 1.0000 | 0.0491 | 0.0491 |
| 34 | 0.00% | mde_power | 34.00 | 1.0000 | 0.8472 | 0.8472 |
| 34 | 1.00% | null_type_i | 32.36 | 0.1857 | 0.0495 | 0.0092 |
| 34 | 1.00% | mde_power | 32.33 | 0.1801 | 0.8368 | 0.1507 |
| 34 | 2.00% | null_type_i | 30.71 | 0.0318 | 0.0566 | 0.0018 |
| 34 | 2.00% | mde_power | 30.71 | 0.0299 | 0.8629 | 0.0258 |
| 34 | 5.00% | null_type_i | 26.28 | 0.0002 | 0.0000 | 0.0000 |
| 34 | 5.00% | mde_power | 26.33 | 0.0001 | 1.0000 | 0.0001 |
| 40 | 0.00% | null_type_i | 40.00 | 1.0000 | 0.0552 | 0.0552 |
| 40 | 0.00% | mde_power | 40.00 | 1.0000 | 0.9026 | 0.9026 |
| 40 | 1.00% | null_type_i | 38.03 | 0.9970 | 0.0509 | 0.0507 |
| 40 | 1.00% | mde_power | 38.03 | 0.9963 | 0.8857 | 0.8824 |
| 40 | 2.00% | null_type_i | 36.12 | 0.9141 | 0.0520 | 0.0475 |
| 40 | 2.00% | mde_power | 36.17 | 0.9160 | 0.8702 | 0.7971 |
| 40 | 5.00% | null_type_i | 30.94 | 0.1641 | 0.0451 | 0.0074 |
| 40 | 5.00% | mde_power | 30.96 | 0.1704 | 0.8539 | 0.1455 |

## Independent-seed Type-I replication (F=40, ICC=0.20, null)

- Replicates: 5 × 10,000 MC
- Pooled Type-I: 0.0489
- Pooled 95% Wilson CI: [0.0470, 0.0508]

## Interpretation limits

- F=33 cells are boundary sensitivity only and are not confirmatory-eligible.
- Type-I cells use μ=0; power cells use the proposed absolute MDE=0.10.
- ICC values are imposed sensitivity scenarios, not estimates from six diagnostic families.
- Variance and residual shape are calibrated from the historical six-family diagnostic input; this is a pilot-based simulation assumption, not independent evidence of the true population distribution.
- This simulation does not inspect Test labels/results and does not authorize formal A-3b.

