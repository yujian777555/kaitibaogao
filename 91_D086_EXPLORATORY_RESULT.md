# 91 — D-086 非封顶恢复任务与演化探索结果

**日期：** 2026-11-11
**状态：** EXPLORATORY / 不是确认性统计结论
**核心结论：** **Full C-NSGA-III = NO_GO；普通 NSGA-III 出现可复现的探索性积极信号，但尚不能称为新算法创新。**

## 1. D-085 独立复审

`88_D085_INDEPENDENT_REVIEW_D086.md` = **ACCEPTED_WITH_LIMITATIONS**。96 行机制数据、192 行封顶数据和 manifest 均可重生成，Train/Validation family 无交集，未发现隐藏故障或 gold label 进入策略，历史结果保留完整。

封顶的真实原因是旧环境没有有效决策差异：独立补偿使顺序不改变结果或成本，失败重试只返回缓存结果，验证只重读同一回执。它不代表固定 Prefix 能处理所有状态化恢复任务。

## 2. 哪些机制自然产生策略差异

新环境只使用公开合同、噪声提示和自身回执，形成三类真实差异：

1. **依赖闭合：** 不同依赖图和备选路径要求不同补偿顺序；错误顺序会增加残余。
2. **可靠性与成本异质性：** 高提示路径不一定可靠，便宜路径可能失败并产生额外确认成本；失败反馈能改变后续选择。
3. **状态不确定和确认预算：** 延迟回执需要 WAIT/VERIFY，未知成功时重复非幂等补偿会造成违规。长链确认使“低成本但超时”和“高成本但成功”同时存在。

这些机制符合依赖安全补偿、瞬时故障、超时和幂等性边界，不是仅增加文字复杂度。图和 Saga 补偿本身仍不是创新。

## 3. 新挑战集与非封顶空间

- Train=72、Validation=24，family 完全分离；Test 未生成、未读取。
- manifest SHA=`362e7a8a0acafbb40f6ddccf207bede85a656193c6544bf3cd949c1fe43ffd67`。
- 8 个固定方法产生 768 行原始数据，无共同支配方法。
- Greedy Train R3=18/18、成本 14.00，Validation R3=6/6、成本 15.17。
- AdaptiveProbe/CostAware 在 Validation 未全通过，长链确认预算形成真实可学习边界。

所以，新集合不是人为让 Prefix 失败，而是具备自然非封顶空间。Greedy 是必须保留的强基线，不能只用弱 Hand 证明演化有用。

## 4. 实际演化实验

预注册：`90_D086_EVOLUTION_PREREGISTRATION.md`；运行器提交：`bcc5ff3b672872853186c40bf42e5e1f0ca2d25d`；序列化/split 修复提交：`ed5dd2edea71f93290874df2608e25ea41b8a61a`。

- 8 个搜索/消融臂 × 5 seeds = **40 runs**。
- 每 arm/seed 上限 6,048 Train episode-equivalent，实际未超限，范围为 5,472–6,048。
- 原始 Train+Validation 账本 **316,416 行**；重复指纹和缓存命中单独计数。
- 无真实 LLM API、无模型训练、无 Test、无正式 A-3b/Pilot B。
- 独立审计全部通过：初始池、预算、原始行数、ledger 统计、选中指标和 NO_GO 判据均可重算。

首次执行因多行 JSON 误写 JSONL 而失败，原目录保留为 `d086_evolution_failed_pretty_jsonl/`。修复还加入 split 缓存键，防止同 ID Train 结果复用为 Validation。审计初版错误地要求跨 seeds 使用同一初始池，失败报告保留为 `d086_independent_artifact_audit.pre_pairing_fix.json`；按 seed×消融分组后审计通过。这些不是算法结果修饰。

## 5. 主要结果

### 5.1 普通搜索方法（Validation）

| 方法 | R3 | R4 | CondRecSucc | 平均 R3 成本 | 硬约束 |
|---|---:|---:|---:|---:|---:|
| Greedy（固定门基线） | 1.000 | 1.000 | 1.000 | 15.1667 | 0 |
| Random Search | 0.8667 | 1.000 | 1.000 | 5.8000 | 0 |
| NSGA-II | 0.9333 | 1.000 | 1.000 | 5.4000 | 0 |
| **NSGA-III** | **1.000** | **1.000** | **1.000** | **5.0000** | **0** |
| **Full C-NSGA-III** | 0.9000 | 1.000 | 1.000 | 5.6000 | 0 |

普通 NSGA-III 在五个 seeds 上均为 R3/R4/CondRecSucc=1、零重复补偿、零未决回执，平均成本 5.0。它低于 Greedy 的 15.1667，且相对 Random Search 和 NSGA-II 没有逐 seed 退化。`nsga3_candidate_assessment.json` 保存了完整逐 seed 判据。

**但 Full 的失败标准为 `r3_all_one` 和 `no_regression_vs_ea`。** Full 在 711、822、1155 三个 seeds 上 R3=5/6，而 NSGA-III 为 6/6。因此不能声称新约束控制器优于普通 NSGA-III，也不能仅强调 Full 的平均成本 5.6 低于 Greedy。

### 5.2 消融

| 消融 | 平均 R3 | 平均 R4 | 平均成本 | 解释边界 |
|---|---:|---:|---:|---|
| Full | 0.9000 | 1.0000 | 5.6000 | 不能战胜普通 NSGA-III |
| NoDependencyPriority | 0.9000 | 1.0000 | 5.6000 | 与 Full 无差异；依赖优先级的独立贡献未识别 |
| NoFailureFeedback | 1.0000 | 1.0000 | 8.4667 | 成功保持，但成本上升；失败反馈有成本作用 |
| NoAlternate | 0.5000 | 0.0000 | 10.4000 | 备选路径是恢复可达性的关键 |
| NoPendingVerification | 0.0667 | 0.0000 | 3.8000 | 不验证会丧失正确恢复；提前终止不等于成功 |

### 5.3 是否只是复现固定策略

NSGA-III 的选中基因组并不等同于固定 Greedy：它们使用成本权重、失败反馈和 `verify_delay=1`，而非固定 Greedy 的高提示优先和立即查询。个别候选继承成本感知先验，说明初始池作用仍需消融，不能把全部收益称为新机制。

普通 NSGA-III 是预注册基线，不是新提出的方法。当前证据支持“演化搜索可能有价值”，不支持“新的约束控制器已经创新”。

## 6. 对十个必答问题的回答

1. **D-085 是否通过独立审查？** 通过事实与可复现性复审，限制明确；不是算法有效性认证。
2. **固定 Prefix 封顶的真正原因？** 旧环境没有依赖、可靠性学习、真正重试或独立验证带来的决策差异。
3. **哪些任务机制自然产生差异？** 依赖闭合、备选路径、可靠性/成本异质性、未决回执和确认预算。
4. **新挑战集是否非封顶？** 是，固定方法出现合理成功/成本/预算差异，无共同支配方法。
5. **固定 Prefix 是否仍是最强基线？** 不是唯一最强；Greedy、AdaptiveProbe、CostAware 都必须保留，普通 NSGA-III 在本轮最强。
6. **是否存在可学习边界？** 存在，可靠路径、低成本路径、失败反馈和确认等待之间存在实际权衡。
7. **演化计算是否有必要？** 有探索性必要性信号，但不能据此宣称普遍必要或新算法成立。
8. **是否值得实现 NSGA-II/III？** 已实现且有必要做对照；NSGA-III 是普通强基线，Full 的额外约束没有显示出增益。
9. **当前能否证明算法提升？** 不能作确认性证明。普通 NSGA-III 有探索性改善，Full NO_GO。
10. **下一阶段唯一任务？** 用**已冻结的普通 NSGA-III 候选**在全新的独立 Validation family 上做一次预注册复制评价；不重新调参、不增加预算、不访问 Test。

## 7. 唯一后续任务与停止边界

下一阶段应先审查本报告和 `nsga3_candidate_assessment.json`，再按 `92_D086_INDEPENDENT_VALIDATION_PREREGISTRATION.md` 执行冻结候选的独立复制。独立复制不是继续优化，也不是访问 Test。

若普通 NSGA-III 在新 family 上退化，必须保留该负结果，不能返回当前 Validation 调参。若 Full 继续落后，不再通过增加约束模块包装其失败。A800/ARWM、真实 LLM、正式 A-3b、Pilot B、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。

## 8. 最终 CI 证据

结果提交 `5210d1c40fbb41b39a51e2ef7ef544e582dc4af5` 的 regression run `43033472661` 为 success。日志实际执行 385+28=413 项测试，并重新生成 D-086 manifest、锁及 768 行固定策略门数据；D-086 artifact 已上传。该 CI 证据支持可复现性，不改变 Full NO_GO 与普通 NSGA-III 仍需独立复制的结论。

## 9. D-087 独立复制结果

D-087 按 92/93 号协议对冻结候选进行了独立复制，结果为 **REPLICATION_FAILED / NO-GO**：新 Validation 上 R3=R4=0.85、CondRecSucc=1、成本 8.85、硬约束 0，0/5 候选通过。成本虽低于 Greedy 的 20.0，但不能抵消恢复失败。

D-086 原始探索结果与 artifact 不修改，但不再支持未经验证的跨 family 泛化表述。详见 `94_D087_REPLICATION_RESULT.md`。
