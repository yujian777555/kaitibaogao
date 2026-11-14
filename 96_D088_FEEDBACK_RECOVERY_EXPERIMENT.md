# 96_D088 反馈驱动动态恢复策略：Train 实验与独立复制

**日期：** 2026-11-15
**分支：** `pilot-a-stateful-recovery`
**代码：** `experiments/d088_recovery/`
**性质：** Train-only 开发实验 + 冻结候选的 Fresh family 复制（非正式 Validation/Test）

## 1. D-087 失败机制审计（反事实诊断）

从原始账本独立重放 rv02/rv03/rv04 repeat 4 的 30 条失败轨迹，确认失败机制：

| 失败模式 | 冻结策略行为 | 反事实合法序列 | 决策数 |
|---|---|---|---:|
| rv02 D3 | 串行 delayed-alternate，每工具 6 步 × 3 | primary 依赖序 C→B→A（立即回执） | 7 |
| rv04 D3 | 同上 | primary 序 A→B→C | 7 |
| rv02 D4 | 同上 | C primary×2 + A alternate×3（批量等待） | 15 |
| rv04 D4 | 同上 | A primary×2 + C alternate×3 | 15 |
| rv03 D4 | 同上 | A/B alternate 并行三轮 | 19 |
| rv03 D3 | 同上 | 交错调度（A/B alternate 破环 + C primary 跟进） | ≤24（可达） |

**结论：** 30 条失败全部源于两个可修复机制——①失败后不切换路线（继续用低成本 delayed alternate）②串行等待（不利用跨工具并行等待窗口）。24 步预算内存在合法完成序列。rv03 R3 存在紧下界（约 23–25 步），需要精细调度。

公开信息足以驱动改进：工具状态、合同、路线元数据（cost/hint/requires/attempts/last_receipt/pending）、决策预算。不使用隐藏 outcomes 与真实延迟。

## 2. 三个候选机制（A/B/C）

| 机制 | 核心行为 | 演化参数 |
|---|---|---|
| **A 失败反馈路线切换** | FAILED/DEPENDENCY_BLOCKED/CONTRACT_BLOCKED 计为失败证据；阈值后切换 sibling 路线；primary 永久不可达时强制启用 alternate | route_failure_penalty, alternate_boost, failure_switch_threshold |
| **B 延迟感知自适应确认** | 批量派发（独立工具先发后等）；从公开 tick 学习回执延迟；PENDING 探针反馈延长学习延迟；预算感知派发门控（保证能清结回执后终止） | delay_probe_wait, wait_batch_weight, max_verify_probes |
| **C 依赖感知路径协同** | 拓扑排序；primary 依赖环检测并用 alternate 破环；解锁依赖的优先级提升 | topo_order_weight, unlock_priority, cycle_break_alternate |

组合组：AB/AC/BC/ABC。机制开关固定按组，突变/交叉永不翻转开关（保证组间隔离）。

实现期间发现并修复三个策略缺陷：①探针返回 PENDING 后不学习延迟（浪费决策）②停止前不清结 pending（产生违规）③预算耗尽前仍派发新补偿。修复后所有组硬违规=0。

## 3. 实验设置

- **开发场景：** 96（6 families × 4 strata × 4 repeats），namespace `d088r|train|`，manifest SHA-256 `e32ddd2f…`
- **Fresh 复制场景：** 80（5 全新 families × 4 strata × 4 repeats），namespace `d088r|train2|`，搜索阶段从未使用
- **决策上限：** 24/episode；**种子：** 711/822/933（配对）
- **搜索预算：** pop=12 × 7 代（84 评价）/arm/seed；RandomSearch 同预算
- **基线：** Hand, RuleBased, Greedy, AdaptiveProbe, CostAware, Random, FixedPrefix
- **搜索臂：** RandomSearch / NSGA-II / NSGA-III × {A,B,C,AB,AC,BC,ABC}

## 4. 开发集结果（零违规前提下）

Greedy 基线：R3=0.792，R4=0.750，harm=0.021。

| 臂 | R3 | R4 | harm | cost | 说明 |
|---|---:|---:|---:|---:|---|
| RandomSearch/B | **0.833** | 0.167 | 0.375 | 7.1 | R3 全 seed 一致 |
| NSGA-II/C seed711 | 0.792 | **0.833** | **0.083** | 10.6 | R4 超基线，R3 持平 |
| NSGA-II/A seed711 | 0.792 | 0.833 | 0.083 | 10.6 | 同上 |
| NSGA-II/BC seed711 | 0.792 | 0.792 | 0.250 | 9.0 | 均衡 |
| NSGA-II/AC seed711 | 0.792 | 0.792 | 0.115 | 10.5 | 均衡，低 harm |

**机制 B 的 R3 提升（+4.1pp）在 9/9 seed-run 一致出现；但 RandomSearch/B 同分——该收益归因于延迟感知机制设计，不能归因于演化搜索。**

## 5. 独立复算与 Fresh 复制

独立复算：63 个 search run 的 best_rows 全部重算，与报告汇总 **0 处不一致**。

冻结候选（开发集零违规最优）→ Fresh families 一次性评估：

| 候选 | 开发 R3/R4 | Fresh R3/R4 | Fresh harm | 判定 |
|---|---|---|---|---|
| best_r4（NSGA-II/A s711） | 0.792/0.833 | 0.650/0.750 | 0.113 | 与 Greedy 打平，harm 更高——**未复制** |
| best_r3（NSGA-III/B s822） | 0.833/0.167 | **0.800**/0.200 | 0.450 | **R3 +15pp 超 Greedy（0.650），零违规——已复制** |
| Greedy 基线 | 0.792/0.750 | 0.650/0.750 | 0.062 | — |

**真实可重复提升：** 机制 B（延迟感知批量调度）使 R3 CorrectEscalation 在 Fresh family 上从 0.650 → 0.800（+15pp），安全硬约束全零。
**必须保留的权衡：** R4 从 0.750 → 0.200，AvoidableHarm 从 0.062 → 0.450。B 组倾向提前 ESCALATE 保住 R3，牺牲损害遏制。
**演化计算作用（诚实结论）：** 目前 R3 收益由机制设计贡献；RandomSearch 同预算找到相同水平。演化搜索尚未证明超越随机搜索——需要反馈条件化变异或更大预算再验证。

## 6. 安全约束

全部 63+7 运行：constraint_violation=0、duplicate_compensation=0、pending_compensation=0（修复后）。无 Test 访问、无 LLM/API、无 A800。

## 7. 下一轮改进

1. **补 R4 短板：** 机制 B 的"提前 ESCALATE"倾向需要 stop_residual/成本敏感目标联合优化；候选：R4-aware 停止条件（残余>min_reachable 时不许停）。
2. **证明演化价值：** 反馈条件化变异（按失败轨迹引导）、更大预算（pop=24×20 代）、NSGA-II vs RandomSearch 配对显著性。
3. **组合 BC：** 开发集 BC 均衡最好；Fresh 上需单独冻结验证。
4. 机制交互消融（A/B/C 二阶效应）。

## 8. 产物

- `experiments/d088_recovery/counterfactual_search.py` + `counterfactual_results.json`
- `experiments/d088_recovery/d088_genome.py` / `d088_policies.py` / `d088_scenarios.py`
- `experiments/d088_recovery/d088_experiment.py` / `d088_audit.py`
- `experiments/d088_recovery/results/d088_train_manifest.json`
- `experiments/d088_recovery/results/d088_experiment_report.json`（SHA `7c62a7de…`）
- `experiments/d088_recovery/results/d088_independent_audit.json`
