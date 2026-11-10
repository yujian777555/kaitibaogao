# 75 — Agent × EC 算法提升候选：Safety-Balanced Counterexample-Guided NSGA-III

**日期：** 2026-11-10  
**研究状态：** CANDIDATE / NOT IMPLEMENTED / NOT VALIDATED  
**所属仓库：** yujian777555/kaitibaogao  
**边界：** 本文只分析本仓库 D-062 / Pilot A-3b 结果，不构成正式 A-3b 许可，不接触 Test。

---

## 1. 为什么必须调整算法，而不是只扩大实验

当前 AB（Contract Repair + Counterexample-Guided Mutation）在历史 diagnostic3 结果中显示出 R1/R2 条件恢复优势，但存在明显的多终点退化。

来自 experiments/pilot_a3b/diagnostic3_recomputed.json 的历史诊断汇总：

| 指标 | AB | NSGA-II | AB 相对 NSGA-II |
|---|---:|---:|---:|
| CondRecSucc（R1/R2） | 0.547170 | 0.232704 | +0.314466 |
| CorrectEscalation（R3） | 0.183908 | 0.678161 | -0.494253 |
| DamageContainment（R4） | 0.888889 | 0.962963 | -0.074074 |
| SLA violation | 0.000000 | 0.010288 | -0.010288 |
| Duplicate | 0.000000 | 0.000000 | 0 |
| Avoidable harm mean | 1.152263 | 0.497942 | +0.654321（更差） |

强手工基线 hand 的 R1/R2 CondRecSucc 为 0.981132。因而当前 AB 虽然在 R1/R2 上高于 NSGA-II，但没有超过 hand，也以 R3/R4 和 avoidable harm 退化为代价。

以上均为 diagnostic 数据，不是正式 40-family confirmatory 结果，不得写成论文结论。

## 2. 已定位的算法目标盲区

experiments/pilot_a3b/a3_bridge.py 的 evaluate_controller() 当前返回的优化目标只有：

1. 1 - CondRecSucc
2. duplicate + avoidable_harm
3. unnecessary_escalation + action_cost / 10

但它同时计算了 corr_esc（R3）、containment（R4）和 sla_viol，这些指标没有完整进入常规 Pareto 目标向量。experiments/pilot_a3b/ea.py 的 safety_battery_pass() 目前只拒绝 duplicate / SLA violation，也没有将 R3/R4 的表现作为可比较的安全维度。

此外：
- CounterexamplePool.targeted_mutate() 取全局最常见的一个 failure signature，容易把搜索压力集中在主流错误上；
- run_evolution() 的最终个体用 min(sum(objectives)) 选出，重新引入未预注册的等权标量化；
- diagnostic3 初始种群由 sensible-random FSM 组成，hand FSM 单独评估，没有作为所有 EA 方法共享的可继承精英种子。

这些是实现层可验证的缺口，是下一轮算法机制研究的依据；不是已经证明的因果解释。

## 3. 候选改进：SBCG-NSGA-III

暂定名称：**Safety-Balanced Counterexample-Guided NSGA-III（SBCG-NSGA-III）**。

### 机制 A：安全感知的五维 Pareto 目标

将 R1/R2 恢复、伤害、动作成本、R3 正确升级、R4 损害遏制纳入同一候选评价：

- f1 = 1 - CondRecSucc（最小化）
- f2 = AvoidableHarm（最小化）
- f3 = UnnecessaryActionCost（最小化）
- f4 = 1 - CorrectEscalation（最小化）
- f5 = 1 - DamageContainment（最小化）

Duplicate 和 SLA violation 不应仅作为可补偿目标；应作为预注册的硬约束/可行性优先级。具体约束定义和阈值必须在不接触 Test 的前提下冻结，不能看结果后挑阈值。

使用 NSGA-III 的参考方向保持五维目标的搜索多样性。所有对照臂必须使用相同目标定义、相同种群初始化、相同评价预算，避免把目标函数变化误当成算子增益。

### 机制 B：分层反例引导变异

替换当前全局 most_common(1) 反例策略：

- 反例按 task family × failure signature × safety class 分层；
- 对过度代表的错误类型降权，对未覆盖或高风险层保留最低采样概率；
- 变异只作用于真实 decision trace 中被触发的基因；
- 保留现有 contract repair，变异后仍通过同一合法性检查；
- 每代记录各层抽样概率、反例数、基因命中率和修复后有效率。

核心假设：分层反例覆盖可以降低“只修复总体最常见失败、牺牲稀有安全场景”的偏置。

### 机制 C：基线锚定的精英继承与 Pareto 决策

- 将 hand FSM 作为一个共享、可继承的初始精英候选；所有 EA 对照臂均获得同一个初始候选集合。
- 保留不可被安全约束淘汰的可行精英档案；档案按 family 覆盖和目标向量去重。
- 不再用 min(sum(objectives)) 选择最终控制器。
- 在 Validation 上按预注册的安全可行性优先规则，从 Pareto 候选中选择；若安全约束不满足，则返回 HOLD，不得用更高 CondRecSucc 抵消安全失败。

## 4. 可证伪实验

R4 独立审计、导师 MDE 审批和用户批准完成前，不运行正式 A-3b。之后先使用 Train/Validation 做独立诊断，不接触 Test。

对照臂：

1. Hand FSM
2. Random Search
3. NSGA-II（标准基线）
4. NSGA-III（标准基线）
5. A（Contract Repair）
6. AB（当前方法）
7. SBCG-NSGA-III（完整候选）
8. Ablation：去掉五维安全目标
9. Ablation：去掉分层反例采样
10. Ablation：去掉 hand-seed / elite archive

控制条件：
- 相同初始候选池（除明确的 hand-seed 消融外）；
- 相同训练场景、种子、rollout / episode 预算；
- 记录每个方法实际唯一评价次数，缓存命中不重复计入；
- 同一 validation 规则，不用 validation 标签进入适应度训练池；
- 不访问 Test，不以 Test 调参或选择方法。

主要评估：
- CondRecSucc 的 family-equal-weight 配对差；
- CorrectEscalation、DamageContainment；
- Duplicate、SLA violation、invariant violation；
- Avoidable harm、unnecessary action cost；
- Pareto hypervolume / feasible-front coverage；
- 跨 seed 稳定性和各 family 的异质性。

## 5. 预先定义的成功与停止条件

**不能只要求 AB 比 NSGA-II 的 CondRecSucc 高。**

候选方法至少需要：
1. 相对 NSGA-II 在 CondRecSucc 上呈现可复现的 family-level 改善；
2. R3/R4 不出现不可接受的退化，Duplicate/SLA 等硬约束满足；
3. 相对 Hand 在不降低预注册安全要求的前提下，展示恢复率—伤害—动作成本的 Pareto 改善，或明确承认无法超越 Hand；
4. 消融能证明改进来自所提出机制，而非更大预算、不同初始化或额外验证信息；
5. 统计检验、效应量和置信区间支持结论。

如果只改善 R1/R2，却继续显著牺牲 R3/R4 或 harm，则该候选判定失败，不包装为成功。

## 6. 当前结论

SBCG-NSGA-III 是基于现有诊断数据和代码目标盲区提出的**优先验证候选**，不是已实现算法，也不是已证实创新。

当前唯一执行优先级仍是 D-064-R4 corrective revision。R4 完成并通过独立审计后，再启动受控的 Train/Validation 算法诊断；正式 Test 始终保持锁定，直到单独审批。
