# 89 — D-086 非封顶恢复模型与固定策略空间审计

**日期：** 2026-11-11
**状态：** 固定策略空间门通过，允许预注册 Train 探索；不是算法提升证据
**前置复审：** `88_D085_INDEPENDENT_REVIEW_D086.md` = ACCEPTED_WITH_LIMITATIONS

## 1. 为什么 D-085 会封顶

D-085 的旧环境中，补偿相互独立，顺序只改变日志而不改变残余或成本；永久失败重试只返回缓存结果；回执验证只重读同一公开结果，不产生新的外部信息。固定 Prefix 因而能覆盖所有旧场景。其数据、复现、隔离和原始数值已在 D-086 Task 1 独立复核，不能通过调参把这些限制包装为演化创新。

## 2. 新模型的实际机制

`dependency_recovery.py` 是独立的新环境，不修改旧 A-3 状态机或金标准。每个场景有确定的工具初始状态、补偿依赖、路径成本、噪声可靠性提示、逐次尝试结果和回执延迟。

- **依赖闭合：** 路径 `requires` 中的工具未补偿完成时，该路径返回 `DEPENDENCY_BLOCKED`，不能孤儿化有效依赖方。
- **备选路径：** 每个工具提供 primary/alternate；公开提示和成本不保证真实可靠性，只有执行后才能观察结果。
- **不确定回执：** 延迟结果先为 TIMEOUT/PENDING；等待和 VERIFY 后才能解除未知状态。
- **重复副作用：** 未知成功时对非幂等补偿重复执行会记 `DUPLICATE_COMPENSATION`，是硬约束违规，不能用来提高表面成功率。
- **恢复控制：** timeout-before 可重做完成；partial 可补偿后重做完成；permission 需要补偿后安全升级。
- **真实成本：** 每次补偿、VERIFY、WAIT、RETRY 都计入实际成本；24 次决策上限不可绕过。

策略视图只含公开合同、提示、依赖、自己执行过的尝试和回执，不含 scenario ID、label、隐藏结果表、实际延迟、待确认结果或最小伤害。

## 3. 可复算标签与边界

R3 的最小残余由活动工具和路径可达性的不动点计算：只要存在一条依赖可满足且最终可成功的路径，该工具可被补偿；无法到达的工具计入 R4 最小伤害。该计算知道 evaluator 侧的确定性结果表，但不向策略公开。

`classify_scenario()` 对每种场景重新计算 label/minimum harm。测试覆盖依赖阻断、永久失败、备选路径、延迟成功/失败、未知重复补偿、带未决回执的终止、R1/R2 控制和 24 次上限。STOP_SAFE 与 ESCALATE 分账，未决回执不能算正确升级。

相关先行工作已经覆盖依赖安全补偿与依赖感知回滚，包括 [Mnemosyne](https://arxiv.org/html/2607.00269v3) 的 dependency-closed compensation 和 [Dependency-Aware Rollback](https://arxiv.org/html/1705.10208v1)。因此，图、补偿或回滚本身不是本候选的创新；只可检验自适应搜索是否能利用公开异质性。

## 4. 新挑战集与锁

`dependency_challenge.py` 生成新的 Train/Validation，而非 Test：

- Train：6 families × 4 strata × 3 repeats = 72；
- Validation：2 个不相交 families × 4 strata × 3 repeats = 24；
- 每个 split 的 R1/R2/R3/R4 = 18/6；
- manifest SHA-256 = `362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67`；
- committed lock = `experiments/pilot_a3b/dependency_manifest_lock.json`；
- 原始 D-085 manifest、数据和 lock 完全保留，新 scenario ID 为 `d086|...`。

`LONG_CHAIN` 的当前工具缺失曾导致控制场景提前完成，已补齐并加入“实际决策次数必须大于零”的回归。seed base 必须传入每个场景，不能只改元数据。最终 Test 仍只有封存规则，未生成、未读取。

## 5. 固定策略空间结果

`dependency_gate.py` 对 8 个固定方法在相同 96 场景上产生 **768 行原始结果**，不使用优化器。R3 汇总如下；成本是实际补偿、验证和等待成本，不是旧 `action_count` 近似值。

| 方法 | Train CorrectEscalation | Train 平均成本 | Validation CorrectEscalation | Validation 平均成本 |
|---|---:|---:|---:|---:|
| Hand | 0/18 | 0.00 | 0/6 | 0.00 |
| FixedPrefix | 4/18 | 4.50 | 未单独列示 | — |
| FixedPrefixForward | 3/18 | 4.22 | 未单独列示 | — |
| RuleBased | 12/18 | 10.78 | 未单独列示 | — |
| Greedy | **18/18** | 14.00 | **6/6** | 15.17 |
| AdaptiveProbe | **18/18** | 11.33 | 5/6 | 7.17 |
| CostAware | **18/18** | 8.72 | 5/6 | 6.00 |
| Random | 0/18 | 3.61 | 未单独列示 | — |

没有任何固定方法在 Train 和 Validation 上同时支配其他方法。Train 上 Greedy/AdaptiveProbe/CostAware 均全部成功、零伤害和零硬约束违规，但成本不同；Validation 上只有 Greedy 保持全部成功。故门状态为 `CANDIDATE_SPACE_REVIEW_REQUIRED`，不是 GO。

## 6. 具体可学习边界

关键场景 `d086|validation|df07|D3_DEPENDENT_ABORT|r2`：

- Greedy：10 次决策、成本 27，完成且未决回执为 0；
- CostAware：24 次决策、成本 24，缺少最后一次确认，未实际升级；
- AdaptiveProbe：24 次决策、成本 26，仍有 1 个未决回执，被硬约束判失败。

这证明可靠路径、低成本路径与确认等待之间存在真实权衡，不是人为调低某个阈值让 Prefix 失败。原始轨迹见 `results/d086_fixed_gate/validation_budget_boundary_audit.json`。

## 7. 当前结论

- 新环境确实产生依赖、可靠性和确认预算驱动的策略差异。
- 简单固定规则并非在所有场景上支配其他方法，存在研究自适应优化的合理空间。
- 但这仍不证明 NSGA-II/III 有必要或有效；强 Greedy 和成本感知反馈基线必须保留。
- 下一步只能按 `90_D086_EVOLUTION_PREREGISTRATION.md` 的冻结配置开展 Train 探索，不得根据新 Validation 反复修改任务或基线。
