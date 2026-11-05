### Overall estimator gate

| Quantity | Value |
|---|---|
| Strongest validation baseline | standardized |
| Held-out seeds | 40 |
| Mean macro-AUPRC difference | -0.0996 |
| Paired 95% CI | [-0.1139, -0.0858] |
| Key scenarios not significantly worse | False |
| Gate | ESTIMATOR_GATE_FAIL |

### Per-scenario paired differences

| Scenario | Mean difference | 95% CI |
|---|---|---|
| additive_null | 0.0000 | [0.0000, 0.0000] |
| sparse_pairwise | -0.0393 | [-0.0741, -0.0102] |
| parent_sign_flip | -0.3541 | [-0.4081, -0.2983] |
| overlapping_higher_order | -0.1511 | [-0.1938, -0.1101] |
| low_support_drift | 0.0462 | [0.0261, 0.0674] |

### Held-out macro-AUPRC by method

| Method | Mean | Scenario means |
|---|---|---|
| oracle | 0.8000 | additive_null=0.000, low_support_drift=1.000, overlapping_higher_order=1.000, parent_sign_flip=1.000, sparse_pairwise=1.000 |
| standardized | 0.7732 | additive_null=0.000, low_support_drift=0.902, overlapping_higher_order=0.995, parent_sign_flip=0.989, sparse_pairwise=0.980 |
| local_raw | 0.7698 | additive_null=0.000, low_support_drift=0.889, overlapping_higher_order=0.994, parent_sign_flip=0.989, sparse_pairwise=0.976 |
| cdled | 0.7698 | additive_null=0.000, low_support_drift=0.889, overlapping_higher_order=0.994, parent_sign_flip=0.989, sparse_pairwise=0.976 |
| cgomea | 0.7698 | additive_null=0.000, low_support_drift=0.889, overlapping_higher_order=0.994, parent_sign_flip=0.989, sparse_pairwise=0.976 |
| context_pooled | 0.6908 | additive_null=0.000, low_support_drift=0.922, overlapping_higher_order=0.888, parent_sign_flip=0.690, sparse_pairwise=0.953 |
| tcail_q | 0.6736 | additive_null=0.000, low_support_drift=0.949, overlapping_higher_order=0.844, parent_sign_flip=0.635, sparse_pairwise=0.941 |
| tcail_w | 0.6731 | additive_null=0.000, low_support_drift=0.954, overlapping_higher_order=0.840, parent_sign_flip=0.631, sparse_pairwise=0.941 |
| fbl_abs | 0.6616 | additive_null=0.000, low_support_drift=0.636, overlapping_higher_order=0.980, parent_sign_flip=0.832, sparse_pairwise=0.860 |
| random | 0.5721 | additive_null=0.000, low_support_drift=0.580, overlapping_higher_order=0.857, parent_sign_flip=0.635, sparse_pairwise=0.789 |
| fbl_signed | 0.5516 | additive_null=0.000, low_support_drift=0.559, overlapping_higher_order=0.853, parent_sign_flip=0.570, sparse_pairwise=0.776 |

### Null false-link rate (held-out additive/null)

| Method | Rate |
|---|---|
| cdled | 0.0750 |
| cgomea | 0.0750 |
| context_pooled | 0.0958 |
| fbl_abs | 0.0000 |
| fbl_signed | 0.0063 |
| local_raw | 0.0750 |
| oracle | 0.0000 |
| random | 0.0583 |
| standardized | 0.0583 |
| tcail_q | 0.0375 |
| tcail_w | 0.0396 |

### Calibration of TCAIL q

| Brier | ECE | Intercept | Slope |
|---|---|---|---|
| 0.2537 | 0.1789 | 0.137 | 0.130 |

### FOS recovery (mean over held-out seed/parent/module)

| Method | Precision | Recall | F1 | False merge | VI |
|---|---|---|---|---|---|
| cdled | 0.757 | 0.752 | 0.738 | 0.103 | 0.132 |
| cgomea | 0.757 | 0.752 | 0.738 | 0.103 | 0.132 |
| local_raw | 0.757 | 0.752 | 0.738 | 0.103 | 0.132 |
| standardized | 0.772 | 0.727 | 0.729 | 0.066 | 0.129 |
| oracle | 0.657 | 0.800 | 0.704 | 0.280 | 0.160 |
| context_pooled | 0.447 | 0.435 | 0.422 | 0.099 | 0.502 |
| tcail_q | 0.428 | 0.375 | 0.373 | 0.068 | 0.543 |
| tcail_w | 0.392 | 0.358 | 0.351 | 0.070 | 0.567 |
| random | 0.189 | 0.055 | 0.080 | 0.033 | 0.909 |
| fbl_signed | 0.060 | 0.014 | 0.022 | 0.001 | 0.928 |
| fbl_abs | 0.000 | 0.000 | 0.000 | 0.000 | 0.949 |

### Fit quality

| Model | Fit ok | PPC extreme rate | Mean seconds |
|---|---|---|---|
| M2 | 0.935 | 0.005 | 17.05 |
| M3 | 0.925 | 0.000 | 16.60 |
