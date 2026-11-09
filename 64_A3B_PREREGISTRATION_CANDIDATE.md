# 64 — Pilot A-3b 正式预注册草案（CANDIDATE，待用户批准）

**日期：** 2026-11-08（D-063 Stage 3）  
**状态：** PREREGISTRATION CANDIDATE — **未经用户批准不得运行任何正式实验**  
**依据：** 55-R1 设计、59/60/61/63 号报告、`diagnostic3_recomputed.json`（独立复算）、`power_simulation.json`（功效）、`task_family_expansion_audit.json`（划分）  
**冻结原则：** 本文件内容一经批准即不得依据任何结果修改；修改须新编号并重新批准。

---

## 1. 研究假设

**主要假设（H1）：** 在全新锁箱 test clusters（新任务族 × 9 故障组合）上，AB（契约语义保持 + 反例引导定向变异 + WAIT-SLA）相对标准 NSGA-II（同表示、同预算、同初始池）具有更高的主要恢复成功指标。

**次要假设：** H2 AB > A（反例引导的独立贡献）；H3 AwaitSLA > A（WAIT-SLA 独立贡献）；H4 AwaitSLA > Fixed-WAIT（SLA 推理优于固定等待）；H5 AB > AwaitSLA（搜索在合同语义之上的增益）。

**不设假设：** 不预设 AB 超过强手工策略（Hand 仅作参考）；不预设 B 单独有效；Safety Gate 不进入正式比较（D-062 负结果）。

## 2. 比较与显著性

| 类型 | 对比 | 检验 | 校正 |
|---|---|---|---|
| **主要（唯一）** | **AB vs NSGA-II** | cluster 级配对 bootstrap + 符号翻转 | α=0.05，双侧，无多重校正 |
| 次要 1 | AB vs A | 同上 | Holm（4 项） |
| 次要 2 | AwaitSLA vs A | 同上 | Holm |
| 次要 3 | AwaitSLA vs Fixed-WAIT | 同上 | Holm |
| 次要 4 | AB vs AwaitSLA | 同上 | Holm |
| 参考 | AB vs Hand | 同上（描述性） | 不入主张 |

主要比较不显著 ⇒ 不得声称"改进 EA 成立"；次要全部 Holm 校正后报告。

## 3. 评价指标（计算公式冻结）

- **主要指标 CondRecSucc**：在 R1+R2 场景上 `mean(class_success)`；class_success 定义（55-R1 §5.1）：R1=最终任务完成；R2=**补偿后**最终任务完成（安全放弃不计）。
- CorrectEscalation：R3 场景上 `mean(policy_selected_escalation ∧ residual=0 ∧ ¬task)`。
- DamageContainment：R4 场景上 `mean(policy_selected_escalation ∧ duplicate=0 ∧ avoidable_harm=0)`；`avoidable_harm = max(0, actual_harm − min_reachable_harm)`。
- 硬安全指标（**硬门，不可被成功率补偿**）：observed invariant violation rate、duplicate side-effect rate、sla_violation rate（非幂等 UNKNOWN_OUTCOME 下未经解锁的 RETRY）。**任何安全指标 > 0 的方法直接判定该对比不通过**；安全保证仅在 A-3 工具合同与模拟器假设范围内成立，不外推为对真实工具的绝对保证。
- RecoveryCost：R1/R2 上多余动作数与不必要升级率（必要升级不惩罚，仅描述）。
- Worst-group：task-family × fault-composition 的最差组 CondRecSucc/CorrectEscalation。
- 报告全部指标按类别分层；禁止跨类抵消。

## 4. 实验协议（冻结项）

| 项 | 冻结值 |
|---|---|
| 算法版本 | `experiments/pilot_a3b/` @ 本预注册批准时 HEAD（记录 SHA）：StatefulFSM + repair_fsm(A) + CounterexamplePool v3(B-new) + WAIT-SLA 掩码 |
| 基因组 | StatefulFSM 78 基因（13 观测×3 尝试桶×2 栈标）×(动作, wait_n∈1..4)；动作集 {RETRY,VERIFY,WAIT,COMPENSATE,ROLLBACK,REPAIR,ESCALATE,STOP_SAFE} |
| 演化参数 | pop=48，generations=60，均匀交叉，单次变异/子代（B-new 定向变异替换式），NSGA-II 三目标 (1−CondRec, dup+avoid_resid, unnec_esc+unnec_actions/10)，可行性优先 |
| 基线 | NSGA-II（同骨干）、A、AwaitFixed、AwaitSLA、B、AB、Hand（参考）；NSGA-III/GA 为补充对照 |
| 初始种群 | 每 seed 共享同一 60 个"sensible-random"FSM 池（骨架基因固定、其余随机）；所有方法同一池 |
| Train | 8 任务族 × 9 组合 × 3 repeats = 216 场景（63 号表） |
| Validation | 4 任务族 × 9 × 3 = 108 场景（仅选择/停止） |
| **Test（锁箱）** | **17 任务族 × 9 × 3 = 459 场景；生成后哈希冻结；仅最终一次性评价** |
| 随机种子 | 演化 seeds {411, 522, 633}（正式），场景 seed base 2026111100；全部记录 |
| Episode 预算 | 每方法每 seed 搜索预算 = 48×61×len(train) + battery 计费；所有真实 simulator episode 计入；缓存命中按唯一基因组记账 |
| 统计方法 | cluster=task×composition（459/3=153 test clusters）；seed 嵌套；paired cluster bootstrap（4000, seed 20261110）+ 符号翻转（4000）+ Holm；效应量与 CI |
| 排除规则 | 仅排除运行故障（进程崩溃）；不排除任何"难看"场景；UNKNOWN 类标签场景不进主要分母但单列报告 |
| 停止规则 | 预算用尽即止；不因中途显著性停止；不追加预算 |
| 原始数据 | 逐 episode JSONL + 基因组规则 + manifest（SHA-256 全量）+ 复算脚本；`ci_artifact` 式字节保真存档 |
| 功效声明 | test 153 clusters：MDE=0.10 名义功效 ≈80%（无失效预留）/略低于含预留目标；MDE=0.1173 功效 >80%（含预留）。若实际功效不足，如实报告，不加测 |

## 5. 执行前置检查清单（批准后、运行前逐项打勾）

1. 记录代码 HEAD SHA 与 27+ 测试全绿证据；
2. 生成 train/validation/test 场景清单并 SHA-256 冻结（test 清单交用户保管/或哈希公开）；
3. 验证 test 任务族与 train/val 零共享（63 号脚本重跑）；
4. 独立复算脚本 `analyse_diagnostic3.py` 泛化到正式数据的等价实现；
5. 用户明确批准本文件。

## 6. 结果解释边界（预注册）

- 主要比较显著 + 硬安全门通过 ⇒ 可声称"同预算下 AB 优于标准 NSGA-II 于未见任务族/组合"。
- 仅次要显著 ⇒ 只能声称对应机制的独立贡献。
- 任何安全指标违规 ⇒ 该方法判负，不得以成功率辩护。
- 不得将诊断实验（D-060/61/62/63）数据并入正式检验；诊断仅作先验与功效依据。
- 与 Hand 的差距如实报告，不宣称超越专家。
