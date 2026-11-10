# D-064-R4 — ICC / Type-I / power re-calibration

- Input raw SHA-256: 2946bcf97883c74c407a204d5ce50bb325e4597a47be4831ccaff4ef8a4f414c
- Input canonical-content SHA-256: 9b1d90279852843bf93d92e66dab3e726ff1e19bc14b94e07ba260fc34eb68a7
- Code commit: e92e9af964edd6963baed41b48a24073e34f99f8
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

## Interpretation limits

- F=33 cells are boundary sensitivity only and are not confirmatory-eligible.
- Type-I cells use μ=0; power cells use the proposed absolute MDE=0.10.
- ICC values are imposed sensitivity scenarios, not estimates from six diagnostic families.
- Variance and residual shape are calibrated from the historical six-family diagnostic input; this is a pilot-based simulation assumption, not independent evidence of the true population distribution.
- This simulation does not inspect Test labels/results and does not authorize formal A-3b.

