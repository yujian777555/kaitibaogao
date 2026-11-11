# 88 — D-085 独立复审（D-086 接管）

**日期：** 2026-11-11
**审查角色：** D-086 接管后的实现与证据复审；不将工程通过解释为算法有效
**审查基线：** `c5a4db452d30688c317bf9e6173c5e5413dd1c14`
**main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`，未修改
**结论：** **ACCEPTED_WITH_LIMITATIONS**

## 1. 范围与方法

逐项读取 85/86/87、Prefix 控制器、A-3 运行时和 bridge、挑战集生成器、专项测试、96 行机制 CSV/JSON、192 行封顶数据、独立复算、manifest lock 和 CI 证据。重新运行完整回归、两个审计入口和 manifest 生成器，并直接检查原始行与字段，而非仅引用历史报告。

- 工作分支和 main 的远端 SHA 与接管值一致；ahead 269 / behind 0；工作区初始干净。
- 最新 regression `43020422598` 为 success。
- 本次基线回归：pilot_a3b 341 + pilot_a_recovery 28 = **369/369**。

## 2. 八项复核结论

| 审查项 | 证据与结论 |
|---|---|
| 固定 Prefix 封顶 | **确认。** 重新生成的 192 行与 committed JSON 完全一致；Train/Validation 均全部类别成功、零可避免伤害、零硬约束违规。 |
| 隐藏信息 | **未发现泄漏。** `fsm.decide(state)` 只接收公开状态；PublicToolView 不暴露 fault、delay、真实 ToolRuntime.state 或隐藏补偿计数。超时不会把内部提交写入 prefix。 |
| 金标准标签 | **仅限 evaluator。** verdict 用于 score_episode，未传入控制器。正常前缀补偿不可用的旧标签反例已保守修正；D-079 v2 manifest SHA 未改变。 |
| 补偿顺序差异 | **只有动作次序，没有旧环境结果差异。** 补偿相互独立，`prefix_reverse` 可改变日志顺序，但不改变最终残余或成本。 |
| 失败与未知状态 | **当前覆盖范围内正确。** 空回滚和失败回滚不能伪装成功；失败重试有 24 次上限；不可补偿影响保留。验证只重读公开回执，不是独立事实验证。 |
| Train/Validation 隔离 | **确认。** Train 72、Validation 24，family ID 无交集，scenario ID 唯一，无 Test payload。manifest 重新生成完全一致。 |
| 独立统计复算 | **确认。** 96 行重新生成逐字一致；48 个场景双方法配对；既有 33 项复算全部通过，当前来源哈希也一致。 |
| 历史结果 | **确认保留。** 原始 D-078/D-079 目录无覆盖差异；D-085 的 pre-fix 文件以独立后缀保留。 |

## 3. 限制与不能推出的结论

### L1：旧环境没有有效的顺序决策

`prefix_reverse` 只改变独立补偿的执行顺序；没有依赖图、先后顺序导致的可达性差异或顺序成本。因此不能据此主张“演化学会了恢复排序”。

### L2：旧环境没有真正的补偿重试学习

`ToolRuntime.compensate()` 在 `compensation_attempted=True` 后直接返回 `last_compensation_result`。永久失败重试不会获得新信息或新结果，只消耗预算。它不能证明策略会学习补偿可靠性。

### L3：回执读取不等于独立验证

`VERIFY_PREFIX` 重读同一公开补偿回执，不提供独立外部状态，也没有回执延迟、矛盾或验证误差模型。其信息增益在当前环境中不能成立。

### L4：终止标志需要在下一协议拆分

旧 runner 将 `ESCALATE` 与 `STOP_SAFE` 都写入 `policy_selected_escalation`。D-085 的 96 行成功样本均实际使用 `policy_escalate`，因此不改变本次数值；但后续 CorrectEscalation 必须单独统计真正的 ESCALATE，STOP_SAFE 只作为安全终止，不得混称人工升级。

### L5：R4 与广义标签仍有边界

D6 的“达到最小残余”不等于零副作用。广义 `crosscheck_all_patterns()` 的 UNKNOWN/不一致仍是 OPEN；新状态模型必须另行提供可复算状态转移和标签证明，不能继承旧标签器的全部假定。

## 4. 对 R4 和算法结论的限定

85 号 ACCEPTED 仅是 R4 代码与协议复审通过，不是正式 A-3b 批准，也不自动覆盖后续 Prefix/标签修改。导师 MDE、用户批准与真实 pre-flight 仍为独立门禁。

本复审没有发现需要推翻 D-085 原始数值的证据；也没有发现 EC 提升证据。固定 Prefix 封顶是旧环境表达力不足导致的真实封顶，不能靠调参或更换事后指标将其包装为算法创新。

## 5. 下一任务

建立**独立的新状态转移与评价模型**，优先研究公开补偿依赖、异构补偿可靠性、瞬时/不确定回执及真实成本。先验证可达性、公开信息边界、非封顶固定策略差异和标签一致性，再决定是否运行任何 NSGA-II/III。Test 继续不生成、不读取；正式 A-3b、Pilot B、A800/ARWM、真实 LLM API、UndoBench TEST、ThinkingBox 和 main merge 继续禁止。
