# D-094 R3 预注册：反馈与行为多样性感知演化

状态：`PRE-REGISTERED_FOR_REVIEW / NOT APPROVED / NOT RUN`。本文件是执行审查基线，不是实验结果。

## 1. 继承与不变量

- 保留 D-094 R1/R2 INVALID 及全部原始 API 账本。
- 不把 R2 搜索候选 `b5dbe97a0ff4…18abe` 当作已验证最优解，也不把它注入 R3 初始种群。
- 模型=`deepseek-flash`，temperature=0，显式 `thinking={"type":"disabled"}`，结构化 JSON。
- 不修改 D-092/D-093，不读取 Validation/Test，不启动 A800 训练。
- 不通过追加预算挽救 R1/R2；R3 使用独立预算与账本。

## 2. 科学问题与比较

| 比较 | 论证职责 |
|---|---|
| B3−B2 | 失败反馈驱动算子选择的独立贡献 |
| B4−B2 | 行为多样性感知 survivor 的独立贡献 |
| B5−B3 | 在反馈基础上增加行为选择的增益 |
| B5−B4 | 在行为选择基础上增加反馈的增益 |

B1 是固定 LLM 参考基线。B2 是标准 NSGA-II；B3 仅启用反馈；B4 仅启用完整行为选择；B5 仅组合二者。不能将 B5 的效果重复归因。

## 3. 独立 Train 与配对

新建6个任务，ID为 `d094_r3_train_{verification|transient|compensation}_{0|1}`，每个家族2个。环境状态机使用 D-094 公开工具约束，不使用 R2 结果生成任务。

配对 seeds=201、202。每个候选在相同6任务×2 seeds=12 episodes 上评价。温度、工具 Schema、模型、价格口径、预算规则和所有臂的评价任务完全一致。

R3 为机制探索；两个 seeds 不支持统计显著或普遍性能结论。

## 4. 冻结搜索规模

- B1 fixed：12 episodes。
- B2/B3/B4/B5：每臂初始种群4、1代、最多8个唯一搜索候选，search≤96 episodes。
- 每个演化臂从可行 Pareto front 选1个候选，final=12 episodes。
- 总设计 episodes=12+4×(96+12)=444；不得将设计量写成实际完成数。
- 全局真实 HTTP 上限=1500，Token 成本上限=0.50 USD，不超过 R2 预算。
- 最大输出=128 tokens，timeout=20秒，有限重试最多1次，实际并发和墙钟全部记录。

## 5. 算法冻结

- B4 使用 `D094_DIVERSITY_AWARE_NSGA2.md` 的完整 crowding+novelty 分数、编辑距离、0.5/0.5权重和唯一 phenotype 控制。
- B3 使用 `D094_FAILURE_FEEDBACK_EVOLUTION.md` 的七类失败、映射矩阵、β=2、τ=0.25、ε=0.1。
- B5 仅组合上述冻结机制，不增加参数。
- 所有变异/交叉产生合法 Typed Genome；全局 evaluated 集合禁止重复评价。
- 硬约束优先于 Pareto/行为新颖性，不使用单一加权总分替代多目标结果。

## 6. 预算预留硬门禁

使用 `d094_budget.py` 的请求前预留机制：

1. 在任何搜索请求前，根据实际 canonical messages 字节数和 max_tokens 计算每次请求保守成本上界。
2. B1 固定基线池与四个 final 池必须在搜索前建立，搜索不能使用这些池。
3. 若无法完整预留，返回 `BLOCKED_BUDGET`，首个请求不得发送。
4. 请求完成后以真实 Token 结算；无 usage/网络错误保留请求上界并标 unknown，失败和重试均记账。
5. 搜索池耗尽时停止新候选；不得生成没有真实 API 能力的 final 运行。
6. final 必须有真实请求、真实结构化决策和完整工具轨迹，否则该臂 INVALID。
7. 真实发送、预算拒绝、预留、pending、结算、cache hit 和成本上下界分别记录；缓存命中不得冒充新评价。

独立审查必须验证 R3 的完整规模在上述1500/0.50 USD 上限内可执行。未通过预算预检不得运行。

## 7. 必须补齐的账本

- mutation locus、before/after、intermediate/offspring/parent Genome；
- 所有 duplicate proposal、cache hit、operator invocation 和反馈概率；
- 每代 survivor Genome/Phenotype/objectives 和三种多样性；
- 每 episode 的逐事件 hash-chain；
- 请求预留、结算、错误、重试和最终成本；
- 原始 episodes、请求账本、执行锁及全部 SHA-256。

## 8. 指标与判据

报告 Task/Recovery Success、Harm、Constraint Violation、Tool Cost、Token Cost、Latency、行为多样性、唯一候选、重复评价、Pareto front 和搜索评价数。

- 主要机制信号需总体方向及201/202两个配对 seeds 同向；展示全部差值，不做确认性显著性宣称。
- 仅增加行为多样性而无性能/搜索效率收益=`NO_CLEAR_GAIN`。
- 仅增加 Token/API 成本而无对应收益=`NO_CLEAR_GAIN`。
- 预算/执行/账本不完整=`INVALID`。
- 有正向小样本信号=`POSITIVE_SIGNAL`，但必须另做独立复现，不等于创新成立。

## 9. 执行门禁

必须依次完成：实现、静态测试、合成行为/失败/预算测试、完整回归、本预注册审查、新独立会话的实现一致性复核、用户明确批准。

当前状态：`IMPLEMENTED / UNIT_TESTED / SYNTHETIC_VALIDATED`；`INDEPENDENT_REVIEWED=NO`、`APPROVED_FOR_EXPERIMENT=NO`、`EXPERIMENT_COMPLETED=NO`、`POSITIVE_SIGNAL=NO`。
