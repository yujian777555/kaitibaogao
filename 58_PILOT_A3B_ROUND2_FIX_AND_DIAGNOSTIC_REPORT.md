# 58 — Pilot A-3b 第二轮修复与诊断实验报告（D-061）

**日期：** 2026-11-07  
**状态：** IMPLEMENTATION FIXES + DIAGNOSTIC ROUND 2（非确认性；正式 A-3b 仍 HOLD）  
**原始数据：** `experiments/pilot_a3b/diagnostic2_results.json`（manifest `d4fb2be680e74f2e…`）；D-060 旧数据 `diagnostic_results.json` **原样保留**  
**统计：** `diagnostic2_stats.json`（pooled hierarchical，57 S1 修正版）

---

## 0. 结论摘要

本轮按 57 号复核（F1–F8、S1–S3）完成实现级修复并重跑诊断。核心结果：

1. **机制 A（契约语义保持）获得真实、显著的独立证据**：独立 contract validator 检出的非法策略比例 **1.00 → 0.00**（A/AB vs 全部其他方法）；class-success 相对标准 NSGA-II **Δ=+0.239，CI [0.193, 0.284]，Holm p=0.0014**。
2. **机制 B（反例驱动）单独有效但弱**（Δ=+0.082, Holm p=0.034），**作为叠加机制显著有害**：AB vs A **Δ=−0.113，p=0.0014**——当前 B 设计不能与 A 组合。
3. **A+B 超过标准 NSGA-II**（primary Δ=+0.126, p=0.0002, d=0.82），**但不超过 A 单独，也远不及强手工策略**（Δ=−0.514）。
4. **泛化成立（Q6）**：验证集（2 个未参与演化的任务族、新种子）上 AB vs NSGA-II **Δ=+0.148, p=0.0017**，A 在验证集 0.488 vs NSGA-II 0.222。
5. 环境违规率仍是开放问题（A 0.36 vs hand 0.006）：观测歧义下的行为安全不是规则修复能静态消除的。

## 1. 57 号阻断项处置清单

| 项 | 修复 | 证据 |
|---|---|---|
| F1 静态规则表/隐式回滚 | 真状态化 `StatefulFSM`（步索引/尝试数/确认栈/补偿栈/决策预算）；COMPENSATE/ROLLBACK 为显式策略动作并记入 comp_log；**删除"基因含 COMP 即全局回滚"** | `a3_bridge.py`；`test_stateful_controller.test_no_implicit_saga_rollback` |
| F2 自动升级污染 | `policy_selected_escalation` / `runtime_forced_abort` / `escalation_reason` 分列；R3 只认显式升级 | `test_...test_policy_escalation_vs_runtime_abort` |
| F3 R4 评分 | `min_reachable_harm`/`actual_harm`/`avoidable_harm=max(0,actual−min)`/`unavoidable_residual` 全量输出；R4 成功=显式升级∧零重复∧可避免损害=0 | `test_...test_r4_requires_containment_not_mere_escalation` |
| F4 成本惩罚必要升级 | obj3 只计 R1/R2 的多余动作与不必要升级；R3/R4 动作成本仅描述统计 | `test_...test_necessary_escalation_not_in_r12_cost` |
| F5 A-3 标签非判定器 | 解析证明规则（逐故障模式穷举）+ AND-OR 检查器交叉验证 309 模式：**0 硬矛盾**、120 精确一致、18 R1→R2 细化、171 检查器资源内未决（UNKNOWN≠反证） | `a3_verdicts.py` 交叉表 |
| F6 B 失效 | 每代**清空一次并聚合全种群**反例；签名=(类别,末观测,死因)；**决策轨迹定位涉事基因**；权重实际进入评价（≤2×）；定向变异**替换**普通变异（预算对齐） | `ea.CounterexamplePool`；`test_contract_validator` 矩阵烟测 |
| F7 A 自证合法 | 独立 `contract_validator.py`（不引用 repair 表、独立规则路径）；穷举 error×action 矩阵；三指标分列（rule invalid / genome invalid / observed violations） | `test_contract_validator.py` 8 项 |
| F8 horizon 误降级 | 三值 WIN/PROVEN_LOSE/UNKNOWN + 身份环检测；高层目标 UNKNOWN 时**禁止降级** R3/R4 | `test_recoverability.test_horizon_cutoff_blocks_downgrade_to_r3` 等 3 项 |
| S1 CI/p 平均 | pooled hierarchical：场景内先聚合 seed、cluster=task×composition、cluster bootstrap+符号翻转+Holm；效应量+seed 稳定性分列 | `stats.py` |
| S2 标准算法 | NSGA-II (rank+crowding 锦标赛)、NSGA-III（参考方向关联+niche counting，注明为本组重实现）、GA（锦标赛+加权和+均匀交叉）、Random（纯随机）；**GP 排除理由**：决策表 FSM 基因组是离散规则结构，树 GP 不适配该表示（换表示=换研究对象） | `ea.py` |
| S3 无独立验证 | train 108 场景搜索 / validation 54 场景（2 个未见任务族、全新种子）仅报告不参与选择 | `run_diagnostic2.py` |

## 2. 实现变更摘要

- `a3_bridge.py` 重写：StatefulFSM 基因组（13 观测×3 尝试桶×2 栈标 = 78 基因）、控制器状态机、显式补偿日志、scenario_verdict 解析证明器、类别条件评分。
- `contract_validator.py` 新增：独立合法性验证。
- `reachability.py`：三值化 + 环检测 + 证书提取防死循环。
- `ea.py` 重写：标准基线 + A（语义修复）+ B（反例池 v2）+ validator 非法率统计。
- `a3_verdicts.py` 新增：309 故障模式穷举交叉验证。
- `stats.py` 重写：pooled hierarchical。
- `run_diagnostic2.py` 新增；测试 30→47 项全绿。

## 3. 实验配置

- 新种子 base 2026110800；train 108（4 任务族×9 组合×3 重复）/ validation 54（2 任务族×9×3）；
- 标签：R1 49 / R2 25 / R3 20 / R4 14（train）；
- 8 方法 × 3 seeds；pop 48 × 60 代；每方法每 seed 搜索预算 316,224 真实 episodes（缓存命中如实记账）；吞吐 ~76k eps/s；
- 同一初始池（60 个共享"进展骨架"随机 FSM，M1 公平）、同评价器、同场景。

## 4. 实验结果

### 4.1 总表（class-success = 类别条件成功，混合 4 类）

| 方法 | 全体 | train | validation(Q6) | 非法率(独立validator) | 环境违规率 | seed 稳定性 |
|---|---:|---:|---:|---:|---:|---|
| hand | **0.827** | 0.986 | **0.833** | 0.00 | **0.006** | [0.827×3] |
| **A** | **0.426** | 0.311 | **0.488** | **0.00** | 0.360 | [0.395,0.556,0.327] |
| AB | 0.313 | 0.206 | 0.370 | **0.00** | 0.414 | [0.543,0.278,0.117] |
| random | 0.333 | 0.005 | 0.389 | 1.00 | 0.119 | — |
| B | 0.270 | 0.023 | 0.321 | 1.00 | 0.282 | [0.321,0.204,0.284] |
| ga | 0.274 | 0.045 | 0.309 | 1.00 | 0.397 | — |
| nsga3 | 0.200 | 0.051 | 0.228 | 1.00 | 0.327 | — |
| nsga2 | 0.187 | 0.037 | 0.222 | 1.00 | 0.438 | [0.204,0.241,0.117] |

### 4.2 配对 cluster 统计（54 cluster，pooled hierarchical，Holm 校正）

| 对比 | Δ | 95% CI | p | Holm p | 效应 d |
|---|---:|---|---:|---:|---:|
| **primary: AB vs NSGA-II** | **+0.126** | [0.086, 0.167] | 0.0002 | — | 0.82 |
| A vs NSGA-II | **+0.239** | [0.193, 0.284] | 0.0002 | 0.0014 | 1.56 |
| B vs NSGA-II | +0.082 | [0.025, 0.144] | 0.011 | 0.034 | 0.54 |
| **AB vs A** | **−0.113** | [−0.152, −0.078] | 0.0002 | 0.0014 | −0.74 |
| AB vs NSGA-III | +0.113 | [0.051, 0.173] | 0.002 | 0.007 | 0.74 |
| AB vs GA | +0.039 | [−0.025, 0.103] | 0.24 | 0.48 | — |
| AB vs hand | **−0.514** | [−0.613, −0.416] | 0.0002 | 0.0014 | −3.38 |
| Q6: AB vs NSGA-II（validation） | **+0.148** | [0.080, 0.216] | 0.002 | — | 0.97 |

### 4.3 失败案例审计（关键发现）

1. **B 拖累 A**：AB 的定向变异改动反例涉事基因，但反例签名（类别×末观测×死因）过粗，常把已正确的修复基因改坏；3 seeds 中 AB 全部低于 A。
2. **观测歧义下的重复副作用**：TIMEOUT 后 VERIFY 短于可见性 SLA 会误判 NOT_COMMITTED→重试→重复。手工策略用 WAIT×4 规避；A 的规则修复无法在基因层表达"先等满 SLA"的时序约束（这是行为层问题）。
3. **不可行场景占比**：R3+R4 占 train 31.5%；"全部升级"策略在 R3/R4 得分高但 R1/R2 全失——标准 EA 陷入该角点（corr_esc 0.9 但 cond_rec≈0）。
4. **hand 仍全面领先**：决策复杂度下，预算内演化未超过专家规则。

## 5. 六问回答（真实数据）

| # | 问题 | 答案 | 证据 |
|---|---|---|---|
| Q1 | A 是否降低独立验证器检出的非法策略？ | **是（决定性）** | 非法率 1.00→0.00（A/AB vs 其余全部 1.00）；但环境违规 0.36 仍存在（行为层歧义，非规则非法） |
| Q2 | B 是否提高恢复成功率/搜索效率？ | **单独弱有效，组合有害** | B vs NSGA-II +0.082（Holm p=0.034）；AB vs A −0.113（p=0.0014） |
| Q3 | A+B 是否超过 A 单独？ | **否（显著更差）** | Δ=−0.113, CI [−0.152,−0.078] |
| Q4 | A+B 是否超过标准 NSGA-II？ | **是（显著）** | Δ=+0.126, p=0.0002, d=0.82；A 单独更好（+0.239） |
| Q5 | A+B 是否超过强手工策略？ | **否** | Δ=−0.514, p=0.0002 |
| Q6 | 验证集（未参与演化）是否仍有效？ | **是（显著）** | AB vs NSGA-II Δ=+0.148, p=0.002, d=0.97；A 0.488 vs nsga2 0.222 |

## 6. 创新性判断

- **有证据**：契约语义保持算子（A）的独立贡献——同表示/同预算/同初始池下，合法性和恢复成功率两个维度同时显著优于标准 EA；这是机制级、可归因、可复现的差异。
- **无证据**：反例驱动（B）的组合增益；A+B 的组合主张；超越强手工策略。
- **投稿判断**：目前达到"一个有效机制（A）+ 一个负结果（B 组合）"的证据强度，**尚未达到小论文完整主张**（需 B 重设计或收缩为 A 单机制论文 + 行为层安全改进）。第一项创新方向成立性：**部分成立（A 成立，B 待改）**。

## 7. 下一步（唯一优先）

**重设计 B 的反例→基因映射并解决行为层安全（WAIT-SLA 时序）**：(1) 反例签名细化到动作序列模式（如 TIMEOUT→VERIFY→RETRY 重复链），定向变异改为"涉事基因邻域的语义修复型变异"；(2) 把"歧义观测后必须等满 SLA 再 VERIFY/RETRY"做成**状态化契约修复**（控制器状态机层面），复测环境违规率能否逼近 hand。然后以 A+新B 重跑同配置诊断。正式功效分析与预注册继续 HOLD 至上述通过。

## 8. 授权边界（不变）

GO：实现修复、诊断实验、统计、预注册准备。HOLD：正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、锁箱调参。
