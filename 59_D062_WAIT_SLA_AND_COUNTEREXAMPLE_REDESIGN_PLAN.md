# 59 — D-062：WAIT-SLA 行为安全与反例驱动演化任务计划

**建立日期：** 2026-11-08  
**状态：** READY_FOR_EXECUTION（仅授权代码修复、测试和新诊断；正式确认性实验仍 HOLD）  
**基线分支：** `pilot-a-stateful-recovery`  
**建立时 HEAD：** `ac042b4e96b80edb8ca727009f0e34ef32179a1f`  
**Main：** `683b3fe7fc52c86e917d523fdc6bbb13abbfd653`  
**建立时 compare：** ahead 102 / behind 0  
**前序报告：** `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`  
**完整接管入口：** `NEXT_SESSION_PROMPT.md` 的 D-062 节

---

## 0. 本计划的边界

本文件记录下一轮任务，不代表 D-062 已经执行，也不代表 WAIT-SLA 或 B-new 已经有效。

D-061 的数值来自 58 号报告，下一会话必须先从原始 artifact 独立复算，不得只引用汇总表。D-061 当前结论保持：

- A（契约语义保持）相对 NSGA-II 有显著正向诊断证据；
- B 单独只有较弱正向结果，叠加到 A 后显著有害；
- A+B 未超过 A，也未超过强手工策略；
- A 的环境行为违规率报告为 0.36，Hand 为 0.006；
- 第一项创新仅部分成立，尚未达到投稿标准。

D-060、D-061 原始 artifact 必须保留，禁止覆盖或把旧验证集调参后继续称为独立验证。

## 1. D-061 基线事实与待核验项

58 号报告给出的诊断配置为 8 方法 × 3 seeds，population 48 × 60 generations，每方法每 seed 报告 316,224 real episodes；train 108 个场景，validation 54 个场景（报告称包含 2 个未参与演化的任务族和新 seeds）。

报告的主要对比：

| 对比 | 报告 Δ | 95% CI | Holm p | 当前解释 |
|---|---:|---|---:|---|
| A vs NSGA-II | +0.239 | [0.193, 0.284] | 0.0014 | 诊断性显著正向 |
| AB vs NSGA-II | +0.126 | [0.086, 0.167] | 0.0002 | 诊断性正向 |
| AB vs A | -0.113 | [-0.152, -0.078] | 0.0014 | B 叠加有害 |
| B vs NSGA-II | +0.082 | [0.025, 0.144] | 0.034 | 单独弱正向 |
| AB vs Hand | -0.514 | [-0.613, -0.416] | 0.0014 | 未超过强手工策略 |
| validation AB vs NSGA-II | +0.148 | [0.080, 0.216] | 0.002 | 报告称验证集正向 |

上述数字在 D-062 Stage 0 必须从 `diagnostic2_results.json`、`diagnostic2_stats.json` 和评分代码独立复算。若复算不一致，以原始逐 episode 数据和可执行复算脚本为准，修正报告和维护文档。

**关键待核验：** 环境违规率 A=0.36、Hand=0.006 的分母、episode/action 口径、重复事件去重方式、task-family 分布和具体失败轨迹。未完成该复核前，不允许直接把 TIMEOUT→VERIFY→RETRY→DUPLICATE 当成唯一根因。

## 2. Stage 0 — D-061 失败轨迹独立复核（首先执行）

输入：
- `experiments/pilot_a3b/diagnostic2_results.json`
- `experiments/pilot_a3b/diagnostic2_stats.json`
- `experiments/pilot_a3b/a3_bridge.py`
- `experiments/pilot_a3b/ea.py`
- `experiments/pilot_a3b/contract_validator.py`
- `experiments/pilot_a3b/run_diagnostic2.py`
- `experiments/pilot_a3b/stats.py`
- `58_PILOT_A3B_ROUND2_FIX_AND_DIAGNOSTIC_REPORT.md`

任务：
1. 记录 artifact SHA-256、manifest、运行配置和原始记录数量。
2. 独立复算 A 与 Hand 的行为违规率；分别给出 episode-level、action-level 指标，避免混淆。
3. 检查同一 episode 多个违规是否被重复计数。
4. 按 task family、fault composition、seed、controller genome 分层统计。
5. 提取所有重复副作用轨迹及其前序公开观测和策略动作。
6. 对失败样本区分：提交未发生、提交已发生但 ACK 丢失、已提交但查询未可见、仍处理中、结果不可判、工具合同缺少可见性保证。
7. 对成功与失败样本做配对比较，识别真正导致违规的状态转移。
8. 形成 `58_D061_FAILURE_TRACE_INDEPENDENT_AUDIT.md`；若编号已被占用，先检查并选择下一个可用编号。

验收：
- 违规率有明确分子、分母和事件定义；
- 每个典型失败轨迹可回溯到原始 episode；
- 能说明 Hand 的 0.006 与 A 的 0.36 是否同口径；
- 根因判断不读取策略不可见的隐藏状态；
- 复算脚本独立于原评分实现，且有回归测试。

Stage 0 未通过，不得开始扩大实验规模。

## 3. Stage 1 — WAIT-SLA 工具合同和状态化恢复

研究目标：解决“操作结果未知或已提交但暂不可见时，过早 VERIFY/RETRY 导致重复副作用”的行为安全问题。

### 3.1 区分环境真实状态与策略可见信息

环境可以拥有隐藏状态，但策略只能使用公开观测。候选环境状态包括：

- NOT_SUBMITTED
- SUBMITTED
- COMMITTED
- COMMITTED_BUT_NOT_VISIBLE
- NOT_COMMITTED
- UNKNOWN_OUTCOME
- COMPENSATED
- FAILED

这些状态仅用于模拟器与独立 evaluator；Agent/FSM 不得直接读取隐藏状态。策略状态只能由自身历史和公开工具响应更新。

### 3.2 每个工具合同至少定义

- submit semantics；
- visibility SLA（若存在）；
- visibility guarantee 类型和上界；
- query consistency；
- idempotency；
- idempotency-key 支持；
- safe retry preconditions；
- compensation capability；
- retry window；
- max wait / decision budget；
- escalation condition。

**不得假定所有工具都有有限可见性上界。** 若合同没有可证明的 visibility guarantee，等待固定时长不能把 UNKNOWN 自动变成 NOT_COMMITTED。

### 3.3 WAIT-SLA 决策语义

| 公开观测和合同 | 合法决策原则 |
|---|---|
| 明确未提交 | 根据提交合同决定提交/重试 |
| 结果未知，且仍在已声明的可见性窗口 | WAIT，避免非幂等重试 |
| WAIT 后仍未可见，仍在窗口内 | 有限 WAIT 或按合同 VERIFY |
| 查询确认已提交 | 禁止重复提交 |
| 查询确认未提交 | 仅在合同允许时重试 |
| 超过 SLA 仍 UNKNOWN | ESCALATE 或 STOP_SAFE |
| 无可靠 SLA/查询一致性 | 不得仅凭等待推断未提交；按安全策略升级 |
| 明确满足补偿前置条件 | 才允许 COMPENSATE |

区分 visibility SLA 和 retry SLA；WAIT 必须受最大等待和决策预算约束，不得无限循环。

### 3.4 必须测试的边界

- 可见性恰好在 SLA 边界出现；
- 可见性早于 SLA；
- 超过 SLA 仍不可见；
- 没有 visibility upper bound；
- 查询是强一致、最终一致或无保证；
- 幂等与非幂等操作；
- 幂等键存在与缺失；
- 操作仍在处理中；
- lost ACK；
- 重复查询；
- WAIT 自身失败或被限流；
- 多工具事务中的部分提交。

### 3.5 对照机制

至少比较：
1. 原始 A；
2. A + Fixed-WAIT；
3. A + SLA-aware WAIT；
4. A + SLA-aware WAIT + VERIFY；
5. A + SLA-aware WAIT + 合同约束的安全 RETRY；
6. Hand。

每个机制都要有明确的状态转移语义和独立消融。不得把固定等待伪装成 SLA 感知。

## 4. Stage 2 — B-new：反例签名到基因的局部语义修复

旧 B 的问题是反例签名过粗，定向变异可能修改已经正确的修复基因。新 B 必须按完整失败轨迹定位相关决策。

### 4.1 反例签名

至少记录：
- 公开观测序列；
- 错误类型；
- 工具合同字段；
- FSM 当前状态和事务阶段；
- 动作序列；
- 每个动作的公开结果；
- 首次偏离安全合同的位置；
- 最终副作用；
- 重复副作用/可避免残留/错误升级；
- 被触发的 FSM 基因及状态转移。

示例模式：
`UNKNOWN_OUTCOME -> VERIFY_NOT_VISIBLE -> RETRY_NON_IDEMPOTENT -> DUPLICATE`

这只是待验证示例，不得预先将所有 TIMEOUT 归为同一模式。

### 4.2 映射和变异

建立可审计映射：
`failure trace -> violated transition/contract -> implicated gene neighborhood -> semantic repair mutation`

要求：
- 只优先修改与失败转移相关的基因邻域；
- 保留已通过独立 validator 的其他规则；
- 定向变异必须替换普通变异，不增加总 mutation 次数；
- 反例池每代聚合整个种群，不能逐个个体清空；
- 反例聚类、频率和严重程度权重必须真实参与采样/评价；
- 保存每次变异前后基因差异和 validator 结果；
- 通过消融证明不是额外 rollout 或额外变异带来的增益。

不能把 B 写成硬编码 `TIMEOUT -> WAIT`。必须证明它能在不同合同和故障模式下找到不同的策略修复。

## 5. Stage 3 — A 的安全性质保护和组合机制

比较三种设计：
1. mutation 后独立 Contract Validator；
2. 关键行为场景 Safety Gate；
3. 分层 survivor selection：硬安全约束优先，再优化恢复成功率、正确升级和不必要成本。

安全门必须拒绝违反硬约束的候选，不允许用高任务成功率抵消重复副作用。

最少对照：
- A；
- A+B-new；
- A+B-new+Safety Gate。

检验安全门是否恢复组合机制的安全性，以及是否保留 B 的搜索收益。

## 6. Stage 4 — 新诊断实验

仅在 Stage 0–3 的代码和语义测试通过后运行。

### 6.1 方法对照

- Hand；
- 标准 NSGA-II；
- A；
- A+Fixed-WAIT；
- A+WAIT-SLA；
- A+WAIT-SLA+VERIFY；
- B-new；
- A+B-new；
- A+B-new+Safety Gate。

如资源有限，可分两轮：先做机制消融，再做完整算法对照。必须保证预算和比较口径预先定义。

### 6.2 指标

- CondRecSucc；
- episode-level behavior violation rate；
- action-level violation rate；
- duplicate side-effect rate；
- SLA violation rate；
- CorrectEscalation；
- AvoidableHarm；
- 不必要动作成本；
- worst-group performance；
- 搜索效率；
- 未见任务族泛化。

安全指标单独报告，不能被平均成功率掩盖。

### 6.3 数据划分

- Search/Train；
- Validation；
- Held-out Test。

旧 D-061 validation 一旦用于机制修改或参数选择，不得继续声称为独立验证。新 D-062 开发阶段必须生成新诊断场景；正式锁箱测试仍 HOLD。

### 6.4 统计

沿用并独立审计 D-061 pooled hierarchical 框架：
- cluster = task × fault composition；
- seed 为嵌套重复；
- 配对 cluster bootstrap；
- 配对置换检验；
- Holm 校正；
- 效应量和 CI；
- seed 稳定性。

不得平均各 seed 的 CI 或 p 值。报告所有实际 rollout 和 cache hit 记账。

## 7. 必须回答的研究问题

Q1 WAIT-SLA 是否降低歧义观测下的重复副作用？  
Q2 SLA-aware WAIT 是否优于 Fixed-WAIT？  
Q3 VERIFY 是否有独立贡献？  
Q4 B-new 是否正确定位失败基因？  
Q5 B-new 是否优于标准 NSGA-II？  
Q6 A+B-new 是否优于 A？  
Q7 Safety Gate 是否防止 B 破坏 A 的安全性质？  
Q8 方法能否接近或超过强手工策略？  
Q9 未见任务族/故障组合是否仍有效？  
Q10 增益来自演化搜索，还是只来自人工编码的 WAIT-SLA 规则？

Q10 尤其重要。如果 WAIT-SLA 手工规则已解决问题而演化没有额外贡献，必须收缩算法创新主张。

## 8. Gate 和授权

**GO：**
- 原始数据独立复核；
- WAIT-SLA 合同/状态机设计；
- FSM、B-new、Safety Gate 代码；
- 单元测试和独立 validator；
- 新的非锁箱诊断场景；
- 诊断实验、统计复算；
- 仓库和接管提示词维护。

**HOLD：**
- 正式 A-3b 确认性实验；
- 旧 held-out 数据调参；
- UndoBench TEST；
- Pilot B；
- A800/ARWM；
- 大规模真实 LLM API；
- ThinkingBox；
- 未经批准的锁箱测试。

当前不启动 A800 训练。正式功效分析待指标与执行语义稳定后再做。

## 9. 仓库维护和接班要求

每个阶段完成后及时更新：
- `NEXT_SESSION_PROMPT.md`
- `SESSION_HANDOFF.md`
- `README.md`
- `05_DECISION_LOG.md`
- `51_DATA_GATE_AND_PILOT_B_ENTRY_PLAN.md`

本轮建议报告编号从 59 开始；若文件已存在，先查重再递增。D-060/D-061 原始 artifact 永久保留。

每次阶段完成：
1. 真实代码修改；
2. 新增语义测试；
3. 完整回归测试；
4. 新诊断实验（仅在相应 Gate 通过后）；
5. 原始结果与 manifest；
6. 独立复算；
7. Git commit/push；
8. CI 和远端 HEAD 核验；
9. 更新下一会话完整接管提示词。

不要把文档计划写成已经完成的实现或实验。每次汇报必须明确区分 PLANNED / IMPLEMENTED / TESTED / EXPERIMENTALLY VERIFIED。

## 10. D-062 首次启动任务

下一会话必须从 Stage 0 开始：

**独立复核 D-061 环境行为违规率 0.36 vs Hand 0.006 的分母、事件口径和完整失败轨迹。**

在 Stage 0 通过前，不得扩大 rollout。完成后直接实现 WAIT-SLA 状态转移和边界测试，再继续 B-new。

最终目标不是保留 A+B 这个名字，而是找到可复现、可归因、优于强基线的演化算法机制。
