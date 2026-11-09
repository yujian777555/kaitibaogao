# D-063 Stage 1 — Monte Carlo 功效仿真

- MC 次数 2000，种子 20261110，α=0.05；单位=cluster（seed 嵌套）
- 发生器：N(MDE, 经验 cluster SD)；检验：cluster 均值单样本双侧 t（正态近似）
- 失效预留 15%

## 经验 cluster 差值分布

- primary_AB_vs_nsga2_all_dev: n=54 mean=0.1049 sd=0.404
- primary_AB_vs_nsga2_validation_18cl: n=18 mean=0.1173 sd=0.3914
- secondary_AB_vs_A_all_dev: n=54 mean=0.1193 sd=0.2178

## Task-family ICC（cluster 独立性评估）
- primary_AB_vs_nsga2_all_dev: {'k_task_families': 6, 'n_clusters': 54, 'icc': -0.0923, 'between_task_sd': 0.0684}
- primary_AB_vs_nsga2_validation_18cl: {'k_task_families': 2, 'n_clusters': 18, 'icc': -0.078, 'between_task_sd': 0.0786}
- secondary_AB_vs_A_all_dev: {'k_task_families': 6, 'n_clusters': 54, 'icc': -0.0845, 'between_task_sd': 0.0411}

## 所需 cluster 数（power ≥ 目标）
| source | MDE | 80% | 90% | 含15%失效(80%) |
|---|---|---|---|---|
| primary_AB_vs_nsga2_all_dev | 0.08 | 254 | None | 299 |
| primary_AB_vs_nsga2_all_dev | 0.1 | 145 | 190 | 171 |
| primary_AB_vs_nsga2_all_dev | 0.1173 | 110 | 123 | 130 |
| primary_AB_vs_nsga2_validation_18cl | 0.08 | 254 | 254 | 299 |
| primary_AB_vs_nsga2_validation_18cl | 0.1 | 123 | 163 | 145 |
| primary_AB_vs_nsga2_validation_18cl | 0.1173 | 90 | 123 | 106 |
| secondary_AB_vs_A_all_dev | 0.08 | 72 | 90 | 85 |
| secondary_AB_vs_A_all_dev | 0.1 | 54 | 54 | 64 |
| secondary_AB_vs_A_all_dev | 0.1173 | 36 | 54 | 43 |

## 功效曲线（primary_AB_vs_nsga2_all_dev）
| n_clusters | MDE=0.08 | MDE=0.10 | MDE=0.1173 | null FPR (MDE=0.10 row) |
|---|---|---|---|---|
| 18 | 0.159 | 0.2235 | 0.2685 | 0.0685 |
| 36 | 0.226 | 0.322 | 0.4235 | 0.0585 |
| 54 | 0.335 | 0.453 | 0.5835 | 0.0495 |
| 72 | 0.3935 | 0.584 | 0.698 | 0.0545 |
| 90 | 0.454 | 0.632 | 0.785 | 0.062 |
| 110 | 0.535 | 0.734 | 0.85 | 0.047 |
| 123 | 0.5995 | 0.779 | 0.9055 | 0.057 |
| 145 | 0.653 | 0.8475 | 0.9405 | 0.0445 |
| 163 | 0.7105 | 0.885 | 0.964 | 0.0505 |
| 190 | 0.778 | 0.9205 | 0.982 | 0.045 |
| 254 | 0.893 | 0.979 | 0.996 | 0.052 |

## 敏感性与限制
- validation source has only 18 clusters: sd estimate unstable (see sensitivity across sources)
- planning uses development data only; historical validation is NOT the formal test set
- no episode-level inflation: unit is the cluster
