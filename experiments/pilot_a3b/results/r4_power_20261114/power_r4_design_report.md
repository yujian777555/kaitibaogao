# D-064-R4 — ICC / Type-I / power re-calibration

- Input raw SHA-256: b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c
- Input canonical-content SHA-256: 9b1d90279852843bf93d92e66dab3e726ff1e19bc14b94e07ba260fc34eb68a7
- Code commit: 33672562ebaeb6c3a533e7e0fd975cbac045b5e3
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
| 33 | 0.05 | null_type_i | 0.00 | 0.0460 | 0.0021 | [0.0421, 0.0503] | False |
| 33 | 0.05 | mde_power | 0.10 | 0.9507 | 0.0022 | [0.9463, 0.9548] | False |
| 33 | 0.10 | null_type_i | 0.00 | 0.0506 | 0.0022 | [0.0465, 0.0551] | False |
| 33 | 0.10 | mde_power | 0.10 | 0.9121 | 0.0028 | [0.9064, 0.9175] | False |
| 33 | 0.20 | null_type_i | 0.00 | 0.0467 | 0.0021 | [0.0427, 0.0510] | False |
| 33 | 0.20 | mde_power | 0.10 | 0.8308 | 0.0037 | [0.8233, 0.8380] | False |
| 34 | 0.00 | null_type_i | 0.00 | 0.0479 | 0.0021 | [0.0439, 0.0523] | True |
| 34 | 0.00 | mde_power | 0.10 | 0.9798 | 0.0014 | [0.9769, 0.9824] | True |
| 34 | 0.05 | null_type_i | 0.00 | 0.0496 | 0.0022 | [0.0455, 0.0540] | True |
| 34 | 0.05 | mde_power | 0.10 | 0.9529 | 0.0021 | [0.9486, 0.9569] | True |
| 34 | 0.10 | null_type_i | 0.00 | 0.0480 | 0.0021 | [0.0440, 0.0524] | True |
| 34 | 0.10 | mde_power | 0.10 | 0.9197 | 0.0027 | [0.9142, 0.9249] | True |
| 34 | 0.20 | null_type_i | 0.00 | 0.0491 | 0.0022 | [0.0450, 0.0535] | True |
| 34 | 0.20 | mde_power | 0.10 | 0.8427 | 0.0036 | [0.8354, 0.8497] | True |
| 40 | 0.00 | null_type_i | 0.00 | 0.0507 | 0.0022 | [0.0466, 0.0552] | True |
| 40 | 0.00 | mde_power | 0.10 | 0.9912 | 0.0009 | [0.9892, 0.9929] | True |
| 40 | 0.05 | null_type_i | 0.00 | 0.0490 | 0.0022 | [0.0449, 0.0534] | True |
| 40 | 0.05 | mde_power | 0.10 | 0.9781 | 0.0015 | [0.9750, 0.9808] | True |
| 40 | 0.10 | null_type_i | 0.00 | 0.0479 | 0.0021 | [0.0439, 0.0523] | True |
| 40 | 0.10 | mde_power | 0.10 | 0.9523 | 0.0021 | [0.9479, 0.9563] | True |
| 40 | 0.20 | null_type_i | 0.00 | 0.0538 | 0.0023 | [0.0495, 0.0584] | True |
| 40 | 0.20 | mde_power | 0.10 | 0.9028 | 0.0030 | [0.8968, 0.9085] | True |

## Technical-missing sensitivity (MCAR at composition-cluster level)

| F design | Missing rate | Role | Mean complete F | Eligibility rate | Eligible N | Conditional rejection | Conditional 95% CI | Joint rejection rate |
|---:|---:|---|---:|---:|---:|---:|---|---:|
| 34 | 0.00% | null_type_i | 34.00 | 1.0000 | 10000 | 0.0484 | [0.0444, 0.0528] | 0.0484 |
| 34 | 0.00% | mde_power | 34.00 | 1.0000 | 10000 | 0.8472 | [0.8400, 0.8541] | 0.8472 |
| 34 | 1.00% | null_type_i | 32.36 | 0.1857 | 1857 | 0.0485 | [0.0396, 0.0592] | 0.0090 |
| 34 | 1.00% | mde_power | 32.33 | 0.1801 | 1801 | 0.8368 | [0.8190, 0.8531] | 0.1507 |
| 34 | 2.00% | null_type_i | 30.71 | 0.0318 | 318 | 0.0535 | [0.0336, 0.0839] | 0.0017 |
| 34 | 2.00% | mde_power | 30.71 | 0.0299 | 299 | 0.8629 | [0.8193, 0.8973] | 0.0258 |
| 34 | 5.00% | null_type_i | 26.28 | 0.0002 | 2 | 0.0000 | [0.0000, 0.6576] | 0.0000 |
| 34 | 5.00% | mde_power | 26.33 | 0.0001 | 1 | 1.0000 | [0.2065, 1.0000] | 0.0001 |
| 40 | 0.00% | null_type_i | 40.00 | 1.0000 | 10000 | 0.0544 | [0.0501, 0.0590] | 0.0544 |
| 40 | 0.00% | mde_power | 40.00 | 1.0000 | 10000 | 0.9026 | [0.8966, 0.9083] | 0.9026 |
| 40 | 1.00% | null_type_i | 38.03 | 0.9970 | 9970 | 0.0496 | [0.0456, 0.0541] | 0.0495 |
| 40 | 1.00% | mde_power | 38.03 | 0.9963 | 9963 | 0.8857 | [0.8793, 0.8918] | 0.8824 |
| 40 | 2.00% | null_type_i | 36.12 | 0.9141 | 9141 | 0.0508 | [0.0464, 0.0555] | 0.0464 |
| 40 | 2.00% | mde_power | 36.17 | 0.9160 | 9160 | 0.8702 | [0.8632, 0.8769] | 0.7971 |
| 40 | 5.00% | null_type_i | 30.94 | 0.1641 | 1641 | 0.0439 | [0.0350, 0.0549] | 0.0072 |
| 40 | 5.00% | mde_power | 30.96 | 0.1704 | 1704 | 0.8539 | [0.8363, 0.8698] | 0.1455 |

## Adversarial contiguous-prefix technical missing (ICC=0.20)

| F design | Missing rate | Role | Eligible N | Conditional rejection | Conditional 95% CI | Joint rejection rate |
|---:|---:|---|---:|---:|---|---:|
| 34 | 0.00% | null_type_i | 10000 | 0.0503 | [0.0462, 0.0548] | 0.0503 |
| 34 | 0.00% | mde_power | 10000 | 0.8488 | [0.8416, 0.8557] | 0.8488 |
| 34 | 1.00% | null_type_i | 0 | NA | NA | 0.0000 |
| 34 | 1.00% | mde_power | 0 | NA | NA | 0.0000 |
| 34 | 2.00% | null_type_i | 0 | NA | NA | 0.0000 |
| 34 | 2.00% | mde_power | 0 | NA | NA | 0.0000 |
| 34 | 5.00% | null_type_i | 0 | NA | NA | 0.0000 |
| 34 | 5.00% | mde_power | 0 | NA | NA | 0.0000 |
| 40 | 0.00% | null_type_i | 10000 | 0.0531 | [0.0489, 0.0577] | 0.0531 |
| 40 | 0.00% | mde_power | 10000 | 0.8992 | [0.8931, 0.9049] | 0.8992 |
| 40 | 1.00% | null_type_i | 10000 | 0.0490 | [0.0449, 0.0534] | 0.0490 |
| 40 | 1.00% | mde_power | 10000 | 0.8954 | [0.8892, 0.9012] | 0.8954 |
| 40 | 2.00% | null_type_i | 10000 | 0.0499 | [0.0458, 0.0543] | 0.0499 |
| 40 | 2.00% | mde_power | 10000 | 0.8947 | [0.8885, 0.9006] | 0.8947 |
| 40 | 5.00% | null_type_i | 10000 | 0.0476 | [0.0436, 0.0519] | 0.0476 |
| 40 | 5.00% | mde_power | 10000 | 0.8828 | [0.8763, 0.8890] | 0.8828 |

## Independent-seed Type-I replication (F=40, ICC=0.20, null)

- Replicates: 5 × 10,000 MC
- Pooled Type-I: 0.0475
- Pooled 95% Wilson CI: [0.0457, 0.0494]

## Interpretation limits

- F=33 cells are boundary sensitivity only and are not confirmatory-eligible.
- Type-I cells use μ=0; power cells use the proposed absolute MDE=0.10.
- ICC values are imposed sensitivity scenarios, not estimates from six diagnostic families.
- Variance and residual shape are calibrated from the historical six-family diagnostic input; this is a pilot-based simulation assumption, not independent evidence of the true population distribution.
- This simulation does not inspect Test labels/results and does not authorize formal A-3b.

