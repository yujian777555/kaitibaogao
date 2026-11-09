# 64-R3 — Pilot A-3b 正式预注册（修订版 R3，待独立复审与批准）

**日期：** 2026-11-10（D-064-R2 Corrective Revision）  
**状态：** PREREGISTRATION CANDIDATE R3 — **未经独立审计 ACCEPTED、导师 MDE 认可、用户明确批准与 §5 pre-flight 全通过，不得运行任何正式实验**  
**历史版本：** R1/R2 原文保留于 `64_A3B_PREREGISTRATION_CANDIDATE.md`（不覆盖，审计可追溯）；R1 审计见 `70_64R2_INDEPENDENT_REVIEW_R1.md`；修复记录见 `71_64R2_CORRECTIVE_RESPONSE_AND_R3_VALIDATION.md`  
**冻结原则：** 本文件一经批准不得依据任何结果修改；修改须新编号并重新批准。

---

## 0. R1 六项修订摘要

| 发现 | 修订 |
|---|---|
| R2-001 主检验定义冲突 | §2/§4 统一为**唯一主检验 = 双侧 family 级 Student-t**；bootstrap/符号翻转降级定位 |
| R2-002 df=39 固定错误 | **df = F_observed − 1**（34→33、40→39）；代码 `family_t_df()` 实现并测试 |
| R2-003 manifest SHA 不一致 | 当前冻结值 **fb832bcc…**（独立重建+CI 双重确认）；af83f065… 标注 superseded |
| R2-004 attrition 表述 | 定性为"15% 规划损耗的向下取整保守保留（34×5）"；缺失规则/家族门槛/设计偏离门禁写入 §6 |
| R2-005 MDE 审批门 | §7 正式执行必要条件显式包含**导师 MDE 认可** |
| R2-006 次要终点不足 | §3 H2–H5 逐项定义估计量/检验/Holm family；H4/H5 标注探索性 |

## 1. 研究假设与比较

**主要假设 H1**：在锁箱 test 任务族上，AB 相对 canonical NSGA-II 的 family-equal-weight CondRecSucc（R1+R2）更高。

**唯一主要比较（confirmatory）**：AB vs NSGA-II。  
**描述性参考**：AB vs Hand（不纳入确认性主张；历史负结果保留——AB 未超 Hand）。

## 2. 主要终点与唯一主检验（冻结）

- **主要终点**：`family-equal-weight CondRecSucc`——每个 task family 内对其 R1/R2 primary-eligible composition clusters 的 CondRecSucc 等权平均得 family 值；family 间**等权**平均（与 `condrec_analysis.py`/`power_hierarchical.py` 实现一致，见 71 号验证）。
- **主要检验**：**双侧 family 级 Student-t**（单样本，对 family 级配对差值 d_f = CondRecSucc_AB(f) − CondRecSucc_NSGAII(f)）；**α = 0.05**；**分析单位 = 独立 task family**（seed 与 composition 为嵌套重复，不作独立单位）。
- **自由度**：**df = F_observed − 1**（`family_t_df(F)`）。F=40→39；规划损耗后 F=34→33；实际观察数低于设计时按实际值，禁止固定 39。
- **辅助分析**：family 级符号翻转 = **敏感性分析**（F≤15 精确枚举，否则 10,000 次 MC）；**bootstrap CI = 描述性区间，不得作为 α 显著性检验**（D-064-B Type-I 0.08–0.14 反保守）。
- **显著性结论仅由主检验给出**；辅助分析不得推翻或替代主检验结论。

## 3. 次要终点（H2–H5，四项 Holm family）

| 假设 | 指标与计算 | 配对单位 | family 汇总 | 检验 | 校正与边界 |
|---|---|---|---|---|---|
| H2 AB>A | 同主要终点（CondRecSucc 差值 AB−A） | (scenario,seed) 配对 → seed 均值 → cluster → family | family 等权 | family 级双侧 t（df=F−1） | **Holm family {H2,H3,H4,H5}，α=0.05** |
| H3 AwaitSLA>A | 同上（AwaitSLA−A） | 同上 | 同上 | 同上 | 同上 |
| H4 AwaitSLA>AwaitFixed | 同上 | 同上 | 同上 | 同上 | 同上；**探索性标注**（D-064-B 未单独校准该对比的 Type-I） |
| H5 AB>AwaitSLA | 同上 | 同上 | 同上 | 同上 | 同上；**探索性标注**（同上） |

- 安全终点（R3 CorrectEscalation、R4 DamageContainment、硬违规率）：**独立报告**，不入主要/次要 Holm family，不与主要终点互抵；硬安全违规 >0 的方法判该对比不通过。
- 解释边界：H2/H3 若 Holm 后显著可作机制级确认性主张；H4/H5 无论显著与否均为探索性；主终点校准（Student-t）**不自动**推广为所有次要终点已验证。

## 4. 实验协议（冻结项）

| 项 | 冻结值 |
|---|---|
| 算法版本 | `experiments/pilot_a3b/` @ 批准时 HEAD（记录 SHA）：StatefulFSM + repair_fsm(A) + CounterexamplePool v3(B) + WAIT-SLA |
| 基因组 | StatefulFSM 78 基因；动作集 {RETRY,VERIFY,WAIT,COMPENSATE,ROLLBACK,REPAIR,ESCALATE,STOP_SAFE} |
| 演化参数 | pop=48、generations=60、均匀交叉、单次变异/子代；NSGA-II 三目标 (1−CondRec, dup+avoid_resid, unnec_esc+unnec_actions/10)；可行性优先 |
| 基线 | NSGA-II（同骨干）、A、AwaitFixed、AwaitSLA、B、AB、Hand（描述性）；NSGA-III/GA 补充对照 |
| 初始种群 | 每 seed 共享同一 60 个 sensible-random FSM 池；所有方法同池 |
| Train | 8 families × 9 组合 × 3 repeats = 216 场景 |
| Validation | 4 families × 9 × 3 = 108 场景（仅选择/停止） |
| **Test（锁箱）** | **40 families × 9 × 3 = 1,080 场景；primary-eligible 280 clusters** |
| **冻结哈希** | manifest **fb832bcc5cbbfd68557d17caf86c1af168493c75dfdfff3818599e85e2f1b31a**（R2-003 修正：af83f065… 为 POWER_DESIGN 修订前 superseded 值）；test-family **01b41df8…**；test-scenario **dded3bb7…**（独立重建与 CI run 42661732606 双重确认） |
| 随机种子 | 演化 seeds {411, 522, 633}；场景 seed 由 stable_seed 派生；统计 seed 20261112/13；全部记录 |
| Episode 预算 | 48×61×len(train)+battery 计费；真实 episode 全计入；缓存按唯一基因组记账 |
| MDE | **0.10（PROPOSED_MDE_PENDING_ADVISOR_APPROVAL）** |
| 功效 | 34 有效 families × 5 comps（见 §6 损耗）；ICC=0.20 最坏 **0.839 [0.832, 0.846]**（10,000 MC, seed 20261113；修补后复算 0.840 一致）；null 0.054 |

## 5. 正式执行必要条件（GO 顺序，缺一不可）

1. **64-R3 独立审计 ACCEPTED**；
2. **导师认可 MDE=0.10**（或按导师意见重新论证 MDE 并重跑功效模拟）；
3. **用户明确批准**最终预注册文本；
4. **§6 pre-flight 全部通过**（代码 SHA 记录、测试全绿、场景清单哈希冻结复核、test 任务族与 train/val 零共享复验）。

任何一项缺失 ⇒ 维持 HOLD；不得以"CI 绿色/代码通过"替代科学方案批准。

## 6. 缺失数据、损耗与设计偏离规则（R2-004 冻结）

- **损耗设计定性**：family 与 cluster 各按 **15% 规划损耗**，**向下取整**得保守保留规模 **34 families × 5 eligible compositions**（7→5 实际保留比例 5/7≈71%，**不是**精确 15% cluster 损耗，**不是**随机 attrition MC）。
- **技术性缺失**（进程崩溃/基础设施故障）：该 run 排除并计数；**不替换 seed**；报告 technical_missing_runs。
- **算法执行失败**：若属研究终点所测行为（如控制器产生失败 episode），**计 class_success=0 并保留在分母**，不得当缺失删除。
- **数据完整性失败**（R1/R2 标签行出现 null class_success、配对缺失）：**fail closed**（分析拒绝），不静默剔除。
- **family 门槛**：每个 family ≥1 个有效 eligible composition 即保留（family 等权）；0 有效 → 丢弃并计 family_loss。
- **设计偏离门禁**：若 F_observed < 34，分析继续但**触发 design_deviation 标志**，按 df=F_observed−1 报告并如实声明功效不足；**禁止**为补足数量选择性删除 family/cluster 或改用重复 seed 冒充。

## 7. Test 隔离（锁箱）

Train/Validation/Test 隔离；test manifest 哈希锁定（§4）；test 不参与参数调整、算法选择、early stopping；不得根据 test 结果修改预注册；test 逐场景标签不进入训练/调参路径（`test_64r3_protocol.py` 隔离测试）；正式评价一次性执行。

## 8. 停止与结果解释

- 停止：预算用尽即止；不因中途显著性停止；不追加预算。
- 主检验不显著 ⇒ 不得声称"改进 EA 成立"；次要 Holm 后显著 ⇒ 仅对应机制级主张；H4/H5 一律探索性。
- 安全终点独立报告；R3/R4 落后不得被主要终点掩盖。
- 观察效应（历史 +0.3175）不作 MDE、不作先验；负结果（AB 未超 Hand 等）保留。
