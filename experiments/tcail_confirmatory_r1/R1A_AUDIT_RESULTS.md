# R1-A 现有 Pilot Clean Rerun 与代码审计结果

**日期：** 2026-11-05
**状态：** EXPLORATORY AUDIT / NOT CONFIRMATORY / TCAIL NOT PROVEN
**基线 HEAD：** `a3cec9844332bbce04061af3041061fa94e88143`

## 1. 实际执行

使用隔离 Python 3.10.1 环境和 `environment/requirements-lock.txt`，实际运行了原始 Oracle、Estimator-only 和 Scaled-FBL 三个脚本。原始代码输出保存在 `r1a_original_code/`；修正版代码与输出保存在 `r1a_corrected/`。原 pilot 目录和报告未覆盖。

原始系统的 Numba 导入失败与 NumPy 版本不兼容；本轮使用独立虚拟环境，不修改系统环境。所有原始运行日志、CSV、JSON、独立重算和 reconciliation 结果均已保存。

## 2. 修复前后数值

| 指标 | 原始代码重跑 | 修正版 |
|---|---:|---:|
| Oracle mean best / 40 | 39.55 | 39.50 |
| Learned LT mean best / 40 | 38.55 | 38.20 |
| Oracle−Learned LT paired mean | +1.00 | +1.30 |
| 配对 bootstrap 95% CI | [0.55,1.45] | [0.60,2.00] |
| Oracle 全局最优命中 | 13/20 | 11/20 |
| Learned LT 全局最优命中 | 2/20 | 5/20 |
| EB q AUPRC | 0.801501 | 0.801501 |
| EB w AUPRC | 0.797403 | 0.797403 |
| Scaled-FBL absolute-ratio，训练-null gate | 0.413761 | 0.413761 |
| Scaled-FBL absolute-ratio，无 gate | 未报告 | 0.379217 |
| Scaled-FBL absolute-ratio，epsilon=0 | 未报告 | 0.379217 |
| FBL 论文 signed Eq.(7)，valid-only | 未报告 | 0.527312 |

Oracle 修正版使用所有方法相同的 `seed*100000+generation` mixing seed，而不是方法专属偏移；Random FOS 的结构随机流仍独立于 mixing。修正版在每个 seed/landscape 内的初始种群哈希完全一致。初始 50 次种群评价包含在预算内。

这些 Oracle 结果只表示该简化 GOM/deceptive-trap 设定存在 linkage 上界价值。随机流修正改变了数值，不能把原结果与修正版混为同一批数据；两者都保留为 exploratory。

## 3. 原始数据与统计复核

- Estimator 和 FBL 的 AP、Brier、per-seed 差值与 bootstrap CI 均可从原始 CSV 独立重算，数值一致。
- FBL 共独立重算 438,400 个 block；四格 contrast、记录均值和 gate 恒等式最大绝对误差均为 0。
- Oracle 的 mean/sd/median/success、配对差、符号检验、Wilcoxon 和 bootstrap CI 均从 per-seed CSV 独立重算一致。
- 所有 Oracle run 的实际评价数均至少包含初始种群 50 次，且不超过 5,000。
- 当前配对数据没有需要落入 sign-test 分母的未处理 ties；修正版独立审计使用 wins+losses 作为非平局符号检验单位。

## 4. FBL 公式和 epsilon 审计结论

原论文四点定义为 `Δ_i`、`Δ_i,j`，检测量为 `|Δ_i−Δ_i,j|≥ε`。现有代码的 `mean_d` 与该差值在样本均值层面恒等，cell 顺序 `00,10,01,11` 对应正确。

但现有 `fbl_scaled` 使用绝对值 min/max 比率，不是论文 Eq.(7) 的有符号分段比率。修正版将二者分开，并保留原适配，不冒充原论文复现。论文实验中的 epsilon 使用机器精度；现有 0.25 是训练-null 95th-percentile 适配，因此另报无 gate 和零 epsilon 敏感性。

Signed Eq.(7) 在该 Bernoulli 适配数据上出现 2,811/3,800 个非有限或超出论文声称 `[0,1)` 范围的输出；valid-only AUPRC 排除了它们，不能作为完整、公平的基线成绩。这是原公式与当前随机符号差分设定之间的实质适配边界。

## 5. 当前结论

- **Pilot 可靠性：** 原报告数值可重算，但 Oracle 方法专属随机偏移和 FBL 公式/epsilon 适配边界需要修正与披露。
- **TCAIL 实现：** 尚未实现；现有 EB q/w 仍是 Normal–Normal proxy。
- **Estimator Gate：** 未运行，不能声称超过强基线。
- **演化收益：** 只有 Oracle 上界信号，尚未证明 TCAIL-FOS 改善 GOM。
- **最终状态：** NO-GO 条件尚未最终判定；当前没有充分证据支持 GO。

下一步是实现并校准 Bernoulli task/block M2/M3 层级估计器，再按 42 号协议进行公平基线与 held-out Gate。不得把本审计或 Oracle 结果当成 TCAIL 成功证据。

## 6. 复现命令

```bash
experiments/tcail_confirmatory_r1/.venv/Scripts/python.exe experiments/tcail_oracle_gate_pilot/run_oracle_gate.py --seeds 20 --budget 5000 --additive-seeds 12 --output-dir experiments/tcail_confirmatory_r1/r1a_original_code/oracle
experiments/tcail_confirmatory_r1/.venv/Scripts/python.exe experiments/tcail_estimator_gate_pilot/run_estimator_pilot.py --output-dir experiments/tcail_confirmatory_r1/r1a_original_code/estimator
experiments/tcail_confirmatory_r1/.venv/Scripts/python.exe experiments/tcail_estimator_gate_pilot/run_fbl_comparison.py --output-dir experiments/tcail_confirmatory_r1/r1a_original_code/fbl
```

修正版使用 `r1a_corrected/` 中同名脚本和对应输出目录。独立重算入口为 `recompute_pilot_metrics.py`，汇总核对入口为 `reconcile_pilot_outputs.py --root <待核对目录>`。
