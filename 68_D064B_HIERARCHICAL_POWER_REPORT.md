# 68 — D-064-B：CondRecSucc 层级功效、ICC 敏感性与任务族样本量规划

**日期：** 2026-11-09（D-064-B）  
**程序：** `experiments/pilot_a3b/power_hierarchical.py`（v1，numpy 向量化，无硬编码历史统计值）  
**测试：** `test_power_hierarchical.py` 22/22  
**产物：** `power_hierarchical.json` / `power_hierarchical_report.md` / `family_cluster_diagnostics.csv`  
**输入：** `diagnostic3_results.json` SHA-256 `b9498195b80901c2de2da928dd044e678e798cf5f6a8e30047a60bd7b93c9f4c`（与 D-064-A 记录一致）  
**MC：** key cells 10,000 次/config、sweep 2,000 次/config；seed 20261112；α=0.05 双侧

---

## 1. 层级数据复核（Task A）

- **6 task families × 7 R1/R2 eligible compositions = 42 clusters**；零分母 12（delay_rate_permission + partial_comp_failure × 6 族）；每 family 恰 7 个 eligible compositions；seed 嵌套正确、无重复 episode——**结构检查零问题**。
- 总均值 Δ=0.31746、总 SD=0.318856（与 D-064-A 一致）。
- **family 均值全部为正**：calendar_order_ledger 0.357、customer_order_shipment 0.238、inventory_calendar_order 0.302、inventory_order_payment 0.365、return_refund_restock 0.381、subscription_ledger_notification 0.262。
- 方差分解：within-family var 0.0882；between-family var(MoM) **−0.0103**（负值——family 间差异小于族内散布）。

## 2. ICC 与层级方差（Task B）

| 方法 | ICC | 说明 |
|---|---:|---|
| ANOVA / MoM（平衡单向） | **−0.1257** | 原始估计保留 |
| REML（λ≥0 边界约束） | 约束于 **0** | 解析上平衡设计 REML=ANOVA；数值优化正确落在边界 |
| family-block bootstrap CI | **[−0.159, −0.111]** | 仅 6 families，区间本身不精确 |

**纪律声明**：负 ICC 不解释为"已证明 cluster 独立"。当前开发数据未检出正的 between-family 相关，但估计基于 6 个 family，极不精确；正式规划**不依赖该点估计**，而采用 ICC=0/0.05/0.10/0.20 敏感性网格。

## 3. 层级推断（Task E：D-064-A 重评估）

| 推断方式 | 结果 | 判定 |
|---|---|---|
| 42-cluster 独立（D-064-A，对照） | Δ+0.3175，CI [0.218, 0.411]，p=0.000125 | 簇级显著 |
| **6-family 聚合 Student-t** | t=13.14, df=5, **p=4.6e-05** | **显著** |
| **6-family 精确符号翻转（2^6=64 枚举）** | **p=0.03125**（=2/64，可达到的最小双侧值） | **显著（分辨率极限）** |
| family-block bootstrap CI | **[0.272, 0.357]** | 不含 0 |

**回答关键问题**：考虑 family 内相关后**显著性结论仍成立**（Δ 保持；t 与符号翻转均过 α=0.05；CI 不变宽反而更窄——family 均值间 SD 仅 0.059）。p=0.000125 不再是层级推断的正确 p 值；层级 p = 4.6e-05（t）/ 0.031（符号翻转，F=6 分辨率下限）。**外推范围限定**：6 个 family 全正的一致性很强，但只有 6 个抽样单位，外推到新任务族的不确定性主要来自任务族数而非簇数。

## 4. 功效模拟设计（Task C）

两类生成机制：
1. **Empirical family-block resampling**（整族重采样，族内 composition 整体保留）：受限于仅 6 个经验 block——null 校准通过（t 0.063/0.049），但 MDE=0.10 功效≈1.0（经验族间 SD 被 6 族低估），**偏乐观**，仅作对照。
2. **ICC 控制层级模拟**：d_fj = μ + u_f + ε_fj，总边际方差匹配真实数据（SD 0.3189），经验残差池重采样，ICC 由 0/0.05/0.10/0.20 控制。越界率（|d|>1）≈1e-5 量级，可忽略。

检验比较（关键 cell，10,000 次）：
- **Student-t（family 级）：Type-I 0.050–0.056 ✓ 校准良好——推荐主检验**；
- **符号翻转**：F=6 时 0.031（离散保守）、F=17 时 0.049–0.054 ✓；
- **family-block bootstrap CI 拒绝**：F=6 时 Type-I 0.14、F=17 时 0.08——**反保守，不作为 α 检验**（仅作区间报告）。

## 5. 样本量规划（Task D；m=7 eligible compositions/family；t 检验）

| ICC | MDE | 80% 无损耗 | 80% 双 15% 损耗 | 90% 无损耗 | 90% 双 15% 损耗 |
|---|---|---:|---:|---:|---:|
| 0 | 0.05 | >40 | >40 | >40 | >40 |
| 0 | 0.08 | 22 | 40 | 30 | >40 |
| 0 | **0.10** | **15** | 22 | 17 | 30 |
| 0 | 0.1173 | 12 | 17 | 15 | 22 |
| 0 | 0.15 | 8 | 12 | 10 | 15 |
| 0.05 | **0.10** | **17** | 30 | 22 | 40 |
| 0.05 | 0.1173 | 15 | 19 | 17 | 25 |
| 0.10 | **0.10** | **22** | 40 | 30 | 40 |
| 0.10 | 0.1173 | 17 | 25 | 19 | 30 |
| 0.20 | **0.10** | **30** | 40 | 40 | >40 |
| 0.20 | 0.1173 | 22 | 30 | 30 | 40 |

设计/有效 cluster 换算：17 families × 9 comps = 153 design clusters；**R1/R2 primary-eligible ≈ 17×7 = 119**（当前结构 7/9 组合进入主要分母）；双 15% 损耗后 ≈ 86 有效 clusters / 14 有效 families。DE=1+(m−1)ρ 仅作核对，最终取模拟值。

**MDE 纪律**：0.1173 为历史观察效应（仅敏感性）；+0.3175 为诊断观察效应（非 MDE）；MDE 须事前科学论证。MDE=0.05 在 ≤40 families 网格内不可达（如实报告）。

## 6. 17-family 方案评估

**条件性充分**：
- ICC ≤ 0.05 且无损耗：MDE 0.10 功效 0.81–0.90 ✓（17 families 满足 80%）；
- ICC = 0.10：0.73 ✗ 不足；
- 双 15% 损耗（≈14 有效 families）：ICC 0 时约 0.72–0.75 ✗ 边缘不足；
- MDE 0.1173：17 families 在 ICC≤0.10 无损耗下充足（≥0.80）。

**结论：17 families 仅在"低 ICC + 低损耗 + MDE≥0.10"条件下够用；若 MDE 定为 0.08 或预期损耗 15%，须扩至 22–40 families。** 决策留待 D-064-C（任务语义验证与正式生成器）后按预注册纪律冻结。

## 7. R3/R4 安全指标（Task F，独立于 CondRecSucc）

R3 CorrectEscalation：AB 0.226 vs NSGA-II 0.679；R4 DamageContainment：AB 0.800 vs 0.933。主要终点优势**不掩盖**安全行为率落后；硬安全违规率与正确升级行为率分列。

## 8. 科学结论

1. **层级相关不推翻显著性**：6/6 family 全正，t p=4.6e-5，符号翻转 p=0.031（分辨率极限），block bootstrap CI 不含 0。
2. **42 clusters 的有效不确定性**由 6 个 family 主导；family-mean SD 0.059 远小于簇内 SD 0.319——不确定性估计应以 family 为单位。
3. **ICC 敏感性下的样本量**见 §5 表；检验选择：**Student-t 控制 α 良好，符号翻转次之，bootstrap CI 检验反保守**。
4. **17-family 条件性可行**（低 ICC/低损耗/MDE≥0.10），非无条件充分。

## 9. GO / HOLD

**GO：D-064-C**（任务语义 validator + 正式场景生成器 + 64 号样本量/MDE 唯一冻结）。  
**HOLD 不变**：正式 A-3b、test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。64 号预注册保持 REQUEST CHANGES。
