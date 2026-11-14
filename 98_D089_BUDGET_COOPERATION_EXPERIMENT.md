# 98_D089 预算协同优化与 960 评价演化搜索实验

**日期：** 2026-11-15
**分支：** `pilot-a-stateful-recovery`
**代码：** `experiments/d089_recovery/`
**性质：** Train-only 开发实验（96 场景）+ 冻结候选 Fresh 复制（64 场景，全新 families）

## 1. R3/R4 预算竞争分析（第一任务）

对 D-088-R2 原始账本逐动作统计（`_budget` 分析，29 runs）：

**关键发现：失败 100% 为"提前停止"型，0 例 24 步预算耗尽。**

| 失败模式 | 典型轨迹 | 决策数 | 残余 |
|---|---|---:|---|
| strict0（R3 型胜者） | 1-2 次 COMPENSATE 后立即 ESCALATE | 2–7 | resid=2 > min |
| strict1（严格停止） | 反复补偿 16–17 次至预算边缘 | 21–23 | resid=3 > min |

竞争本质不是"确认/补偿动作耗尽预算"，而是**停止条件无法区分"还有可达恢复"与"再恢复也无益"**：
- 放松停止（strict0）：过早放弃 → R4 塌缩（残余 > min_reachable）；
- 收紧停止（strict1）：拒绝放弃 → 预算被恢复动作占满 → R3 需要的 ESCALATE 被挤掉。

动作构成佐证：失败 run 的 mean_dec 仅 2.6–4.0（strict0）或 21+（strict1），WAIT/VERIFY 占比低——延迟等待的机会成本不是主因；**停止决策**是主因。

## 2. 预算协同机制实现（第二任务，B1–B4）

| 机制 | 实现 | 文件 |
|---|---|---|
| **B1 Pareto Archive** | `pareto_front` + 5 偏好选择器（R3/R4/cost/balanced/harm），Train 阶段完成候选选择 | `d089_genome.py` |
| **B2 Escalation Reserve** | `escalation_reserve` 基因（0–3）；派发门控保留终止步 + 在途回执清结预算 | `d089_policies.py` |
| **B3 Reachability-Aware** | `public_min_harm`（公开不动点计算不可避残余下界）+ `reachable_routes`；停止判断只用公开信息 | `d089_budget.py` |
| **B4 Parameterized Stop** | `stop_mode` 基因（0 legacy / 1 strict / 2 adaptive）+ `cost_safety`；adaptive 用随时势成本估算（每未完成工具一轮尝试成本） | `d089_policies.py` + `d089_budget.py` |

修复记录：B4 初版成本估算假设"全部尝试都会失败"，导致 adaptive 立即停止（R3=0）；改为随时势单轮估算后正常（§4 消融）。

## 3. 新 Train 数据（第四任务）

- 开发：96 场景（g01–g06 × 4 strata × 4 repeats），`d089r|train|`，manifest `b2307404…`
- Fresh 复制：64 场景（h01–h04 全新 families），`d089r|train2|`，manifest `2ee16a6b…`
- 家族设计直接针对 R3/R4 竞争：互依对（g03）、慢回执竞速（g01/g04）、预算压力重复（g06）、批量派发机会（g05）

## 4. 960 评价配对实验（第三任务）

配置：pop=32，**每 run 恰好 960 次唯一 genome 评价**（缓存命中不计费、不计入），5 配对 seeds（711/822/933/1044/1155），同任务/同预算/同 evaluator/同安全约束。35 runs 全部零违规。

| 方法 | R3（5 seeds） | R4 | harm | 备注 |
|---|---|---|---|---|
| RandomSearch | 0.833×5 | 1.000×5 | 0.083 | **5/5 稳定** |
| NSGA-II | 4×0.833, 1×0.708 | 4×1.000, 1×0.958 | 0.083–0.188 | seed822 塌 |
| NSGA-III | 3×0.833, 2×0.667–0.708 | 0.667–1.000 | 0.083–0.354 | 不稳定 |
| EvoBudget | 4×0.833, 1×0.708 | 3×1.000, 1×0.958, 1×0.708 | — | ≈ NSGA-II |

**消融（EvoBudget − 1 组件）：**
- No-Pareto-Archive：与 EvoBudget 相同 → **B1 在该预算下无增益**
- No-Counterfactual-Anchor：4/5 稳定 → 锚点无一致贡献（记录来源与评价成本）
- No-Feedback-Mutation：略差（1×0.708/0.667）→ 轻微信号，不显著

**策略级消融（冻结 genome × 停止模式）：**

| 变体 | R3 | R4 | harm |
|---|---:|---:|---:|
| legacy_stop (0) | 0.833 | 1.000 | 0.083 |
| strict_stop (1) | 0.833 | 1.000 | 0.083 |
| adaptive_stop (2) | 0.542 | 0.917 | 0.333 |
| no_reserve / low_safety / high_safety | 0.833 | 1.000 | 0.083 |

诚实结论：**R3/R4 双赢来自策略类改进（可达性感知停止 + 预算门控）+ 参数搜索**；B4 adaptive 模式本身反而更差（成本估算仍偏保守）；B1/B2 参数在本预算下不敏感。

## 5. 独立复算与 Fresh 复制（第五任务）

独立复算：35 runs best_rows 全量重算，**0 处不一致**。

冻结候选（Train 零违规最优，RandomSearch/seed711）→ Fresh 64 场景一次性评估：

| | R3 | R4 | harm | cost |
|---|---:|---:|---:|---:|
| **冻结候选** | **0.750** | **1.000** | 0.188 | — |
| Greedy 基线 | 0.562 | 0.750 | 0.109 | — |
| 差值 | **+18.8pp** | **+25.0pp** | +0.079 | — |

**首次 R3 与 R4 同时超越强基线：R3 提升继续保持（+18.8pp），R4 从短板变为 +25pp 提升。** 预算竞争已解决。必须保留的权衡：AvoidableHarm 0.188 vs 0.109（+0.079）。零硬违规。

## 6. 逐问题回答

1. **R3 提升保持？** 是——Fresh +18.8pp（此前 +15pp）。
2. **R4 改善？** 是——Fresh R4=1.000 vs 0.750（+25pp），短板已修复。
3. **预算分割有效？** 预算门控+可达性停止有效（策略级消融证明）；但 B4 自适应估算与 B2 预留基因本身不敏感。
4. **贡献最大机制？** 可达性感知停止（B3 内核）+ 预算感知清结（D-088 遗产）；B4 adaptive 为负贡献。
5. **Pareto Archive 优于单点？** 否——960 预算下无差异。
6. **Reachability-Aware 有效？** 是（隐含于停止判断，策略消融中 mode0/1 均含该逻辑而 mode2 破坏它）。
7. **NSGA-II/III 优于随机搜索？** **否**——RandomSearch 5/5 稳定最优，NSGA 有塌缩 seeds。第三次观察到该现象。
8. **960 预算下出现演化优势？** 否。
9. **找到安全成立的真实提升？** **是**——冻结候选 Fresh 双指标超 Greedy（R3+18.8pp、R4+25pp），零违规；harm +0.079 权衡如实保留。
10. **下一轮？** 见 §7。

## 7. 下一阶段实验决策

1. **g03 互依对修复**：残余 4 个 R3 失败全在 g03_PAIR_RACE——stop_residual=2 允许带残余停止 + 互依对的 alternate 未被选中。候选：stop_residual 与标签类交互约束（R3 需 min=0 时禁止 stop_residual>0）、互依环破除优先级强化。
2. **harm 权衡收窄**：冻结候选 harm 0.188——研究恢复顺序对残余分布的影响。
3. **演化价值第四次尝试**：搜索空间结构性改造（状态条件化规则编码而非连续参数），或 2880 评价三倍预算下重新配对；否则正式承认"该搜索空间中随机采样即足够"并把贡献归于策略类设计。
4. B4 成本估算校准（当前仍偏保守导致 adaptive 变差）。
5. 两份冻结 genome（R1/R2 的 R3 提升 + 本轮双指标候选）待 Validation 授权后正式复制。

## 8. 产物

- `d089_budget.py`（公开预算分析）/ `d089_genome.py`（B1+B4 基因）/ `d089_policies.py`（B2+B3+B4）/ `d089_scenarios.py`（新数据）/ `d089_search_experiment.py`（960 配对）/ `d089_audit.py`（复算+消融+复制）
- `results/d089_search_report.json`（35 runs 原始账本）、`results/d089_audit.json`
- manifests：`d089_train_manifest.json`、`d089_fresh_manifest.json`
