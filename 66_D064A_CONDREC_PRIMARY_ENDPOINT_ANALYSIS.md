# 66 — D-064-A：CondRecSucc 主要终点独立统计与复算

**日期：** 2026-11-09（D-064-A）  
**程序：** `experiments/pilot_a3b/condrec_analysis.py`（v1，无硬编码摘要值）  
**测试：** `test_condrec_analysis.py` 13/13（微型已知答案 + 真实数据全回归）  
**产物：** `condrec_diagnostic3.json` / `.csv` / `_report.md`  
**原始数据：** `diagnostic3_results.json`（未改动）SHA-256 记录于产物内

---

## 1. Estimand（冻结到 64 号 §3 定义）

**CondRecSucc = R1+R2 场景上的 class_success 均值**（cluster 等权）。R3=CorrectEscalation、R4=DamageContainment 单独统计，不混入主要终点。

**层级配对（四层）**：① (scenario, seed) 内配对 AB−NSGA-II → ② scenario 内对 seed 均值聚合（seed 为嵌套重复）→ ③ task×composition cluster 内聚合 scenario → ④ cluster 等权求总体效应。scenario 加权同时输出为敏感性对照。

**零分母预规定**：无 R1/R2 场景的 cluster **排除出主要 estimand 并登记**（不补零、不静默删除）——本条在正式 test 解盲前预置。

## 2. 结构完整性

重复 episode 0、cluster 元数据一致、AB/NSGA-II 每 seed 场景集完全相同、**配对完整率 1.000**（缺失对 0）、seed 嵌套正确。

## 3. 主要结果（真实 diagnostic3 数据）

| 项 | 值 |
|---|---|
| 设计 clusters | 54 |
| **primary eligible clusters** | **42** |
| zero-denominator (R3/R4-only) clusters | **12**（=全部 6 任务族 × {delay_rate_permission, partial_comp_failure}，设计内不可行组合） |
| AB CondRecSucc | **0.5582** |
| NSGA-II CondRecSucc | **0.2407** |
| **Δ(AB−NSGA-II)** | **+0.3175** |
| Cluster SD | **0.3189** |
| **95% CI**（cluster bootstrap, 4000, seed 20261110） | **[0.2183, 0.4114]**（不含 0） |
| **Sign-flip p**（真实 cluster 级符号翻转 MC, 8000, seed 20261111） | **0.000125** |
| scenario 加权敏感性 Δ | +0.3145（与 cluster 等权一致） |
| 配对完整率 | 1.000 |

每 cluster R1/R2 分母 1–3；分母表见 `condrec_diagnostic3_report.md`。

## 4. 与原 +0.1049 的差异解释

| | 全类别 class_success（D-063） | CondRecSucc R1/R2-only（本报告） |
|---|---|---|
| estimand | R1+R2+R3+R4 混合 | **仅 R1+R2** |
| clusters | 54 | **42** |
| Δ | +0.1049 | **+0.3175** |
| SD | 0.4040 | 0.3189 |
| CI | [−0.00, 0.206]（含 0） | **[0.218, 0.411]**（不含 0） |
| p | 0.065 | **0.000125** |

**差异根因**：12 个不可行 cluster（R3/R4-only）上两方法都靠升级/遏制拿分且差异近 0，把全类别均值差稀释约 2/3；同时剔除后 cluster SD 下降（R3/R4 组内差异大）。原 65 号快速核对值（+0.3175 / 0.3189 / 42 clusters）与本正式复算**逐位一致**——但本报告才是正式产物。**结论翻转：正确 estimand 下主要对比强显著。**

## 5. R3 / R4 独立安全统计（如实报告权衡）

| 指标 | AB | NSGA-II | 说明 |
|---|---:|---:|---|
| R3 CorrectEscalation（14 clusters, 87 eps） | **0.226** | **0.679** | NSGA-II 更擅长正确升级/放弃（AB 更倾向继续恢复） |
| R4 DamageContainment（15 clusters, 81 eps） | 0.800 | 0.933 | NSGA-II 略优 |

AB 在主要终点大幅领先但在 R3/R4 成功率上落后——**这是真实的多目标权衡**，不得用主要终点掩盖；正式实验的硬安全门（违规率）与此处的"正确行为率"是不同指标，R3/R4 行为率将作为次要报告项。

## 6. 统计测试清单（13/13 通过）

R1/R2 过滤、R3/R4 不进主要终点、配对正确、seed 嵌套、重复 episode 拒绝、缺失配对报告、cluster 失配拒绝、零分母登记不补零、cluster 等权聚合（已知答案 5/6）、scenario 加权（已知答案 0.75）、bootstrap 可复现、sign-flip 可复现且为 MC 网格值（非 z 近似）、无硬编码摘要值、真实数据全回归（42/12/Δ>0/CI 不含 0/p<0.05/配对 1.0）。

## 7. 科学结论（八问）

1. **R1/R2-only AB 是否仍优于 NSGA-II？是，且强显著**（Δ+0.3175, CI 不含 0, p=0.000125）。
2. 与 +0.1049 的区别：estimand 修正后效应量 ×3，CI 从含 0 变为不含 0——**主对比结论从"未显著"翻转为"强显著"**。
3. Cluster SD 变化（0.404→0.319）：剔除 R3/R4-only cluster（这些 cluster 上两方法差异近 0 但散布大）后组内方差下降。
4. 42 个有效 cluster 是否足以支撑功效分析？作为功效输入**够起步但偏少**（SD 估计基于 42 点）；D-064-B 将用此 estimand 的分布重做功效与层级敏感性。
5. 无 R1/R2 的 cluster：**12 个**，恰为 delay_rate_permission 与 partial_comp_failure 两组合族 × 6 任务族（结构性不可行，设计内）。
6. cluster 等权 vs scenario 加权：**一致**（0.3175 vs 0.3145），结论不依赖聚合方式。
7. 95% CI **不含 0**。
8. Sign-flip **支持正向效果**（p=0.000125，真实符号翻转 MC）。

**证据边界**：以上为诊断数据（非锁箱 test）上的机制级证据；正式主张仍需 64 号预注册的锁箱 test。R3/R4 权衡如实保留，不因主要终点显著而隐藏。

## 8. GO/HOLD

**GO：进入 D-064-B**（以本 CondRecSucc estimand 重做功效分析 + ICC 层级敏感性）。  
HOLD 不变：正式 A-3b、test 查看/调参、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox。
