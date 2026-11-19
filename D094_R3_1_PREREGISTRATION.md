# D-094 R3.1 预注册修订：预算安全的五臂机制冒烟实验

> 执行登记（不改变下述冻结设计）：R3.1已于2026-11-19完成一次真实执行，状态`COMPLETED`、科学结论`NO_CLEAR_GAIN`；结果见`D094_R3_1_RESULT.md`，独立复算见`D094_R3_1_INDEPENDENT_AUDIT.md`。下文保留预注册时的状态与参数，不得据结果回改实验设计。

冻结时状态：`READY_FOR_INDEPENDENT_REVIEW / NOT RUN`。本修订保留原 `D094_R3_PREREGISTRATION.md`，不覆盖原设计或 R1/R2 证据。

## 1. 修订原因与执行授权

原 R3 在 `deepseek-flash` 峰值价格（输入 0.3、输出 1.2 USD/百万 tokens）下的保守上界为 **7032 次真实 HTTP、5.2993152 USD**，超过冻结的 1500 次和 0.50 USD 上限。真实配置纯预检产物为 `experiments/d094_llm_agent/results/r3_budget_preflight/`；状态 `BLOCKED_BUDGET`，实际请求和 episodes 均为 0。

价格与 Base URL 来源为 DeepSeek 官方文档：https://api-docs.deepseek.com/quick_start/pricing/ 。峰值价格用于保守预算，不把缓存命中或 off-peak 低价作为实验可执行的前提。

接管任务明确要求完成独立审查、预算预检并取得用户明确授权后尽快运行，同时给出“现在开始执行”的指令。本文件将其记录为**附门禁条件的真实执行授权**：只有独立只读复核通过、完整回归通过且本预注册保持冻结时才可执行；门禁失败不得借此授权强行运行。

## 2. 冻结规模

- 模型=`deepseek-flash`，Base URL=`https://api.deepseek.com`，temperature=0，`thinking={"type":"disabled"}`，严格 JSON。
- 仅使用 Train 任务 `d094_r3_train_compensation_0`，不读取 Validation/Test。
- 配对 seeds=`201,202`，每个候选评价 `1×2=2` 个 episodes。
- B1 Fixed LLM：2 个 episodes。
- B2/B3/B4/B5：初始种群 2、1 代、每臂最多 4 个唯一搜索候选；每臂 search=8 episodes，独立 final=2 episodes。
- 五臂总设计量=`2+4×(8+2)=42` episodes；设计量不得写成实际完成数。
- 全局真实 HTTP 上限=1500，成本上限=0.50 USD，最大输出=128 tokens，timeout=20 秒，并发=4，重试=0。
- 每个请求 canonical messages 字节硬上限=4096；超限在传输前报错，不得通过扩大上限追加预算。

## 3. 实现一致性与缺陷修复边界

真实运行前完成以下实现修复，并要求独立复核：

1. B3 失败分类读取 Agent 实际的嵌套 `tool_result.error`；B4 与标准臂的 infeasible 填充顺序一致。
2. 请求前同时预留成本与请求槽；B1 和四个 final 池独立保护；预算拒绝不记为真实请求。
3. `recent_trajectory` 保留最近三个公开事件，移除 request ID、prompt hash、token、latency 等请求元数据，并将记忆投影中的 rationale 限为前 80 个 UTF-8 字节；`structured_failures` 保留最近三个失败事件及总失败计数。三种模式的**完整 memory 对象**统一限制为至多 512 个 canonical JSON 字节：recent/structured 优先丢弃最旧 entry，compressed 优先丢弃最旧 tool name 并保留真实事件/失败计数；发生截断时记录 `truncated=true`，若单条仍超限，则确定性地回退为对应空列表。原始轨迹仍完整保存，不改变环境或 genome 基因。对 tool name/arguments 增加公开决策字节边界，避免无界回灌。
4. episode Phenotype 使用公开行为的 canonical hash，不再使用包含请求元数据的原始事件 hash；候选聚合直接使用实际事件，不重复添加 `run_finished`。
5. 执行锁覆盖 Agent、Client、Ledger、Evaluator、Genome、Prompt、Task、演化算法和 Runner 等全部关键源码 SHA-256。
6. 每笔请求保存预算 ID、pool、请求前预留上界、结算实际上界、结算状态和超预留标记；未知 usage 或实际结算超过预留均使实验 INVALID。

以上变化对五臂一致，不根据真实 R3.1 结果调整。

## 4. 公平性与最终候选规则

- 四个演化臂使用相同 search seed=711、初始种群规模、评价任务、seeds、模型、价格和预算规则。
- 重复 Genome proposal 不发起评价，也不消耗真实 HTTP；每个臂允许相同的重复 proposal 尝试上限。
- B2=标准 NSGA-II；B3 仅反馈；B4 仅行为选择；B5 仅组合二者。
- 搜索完成后，从该臂**全部已评价搜索候选**的可行第一 Pareto front 选择 final 候选。
- final 选择键冻结为 `(objectives, genome_sha256)` 的字典序最小值；不读取 final 结果来选择候选。
- final 必须重新发起真实 API 调用并生成完整工具轨迹；不得复用搜索成绩或搜索账本代替 final。
- final 使用相同 Train 任务和 seeds 的新 episodes，不是独立 held-out 泛化评价。

## 5. 逐臂预算预检

每请求保守成本上界：

`(4096×0.3 + 128×1.2)/1,000,000 = 0.0013824 USD`。

这里以 canonical messages 字节数作为输入 token 的保守代理，并以最大输出 tokens 计费；实际响应按 provider usage 结算。若实际成本超过预留或出现 unknown usage，保留上界并将实验标记为预算/账本异常，不得写成零成本。

| 臂 | 初始化请求上界 | offspring 请求上界 | final 请求上界（独立保护） | 总成本上界 USD |
|---|---:|---:|---:|---:|
| B1 | — | — | — | 0.013824 |
| B2 | 32 | 32 | 16 | 0.110592 |
| B3 | 32 | 32 | 16 | 0.110592 |
| B4 | 32 | 32 | 16 | 0.110592 |
| B5 | 32 | 32 | 16 | 0.110592 |

- B1 请求上界=10；四个演化臂各 search=64、final=16；全局总上界=330 次。
- 重复 proposal 请求上界=0；重试请求上界=0。
- 总成本上界=0.456192 USD，低于 0.50 USD；总请求上界=330，低于 1500。
- 纯预检产物：`experiments/d094_llm_agent/results/r3_1_preflight/`；状态 `PREFLIGHT_PASS`，真实请求=0，episodes=0。

## 6. 记录、复算与结论边界

必须保存并复算：每个真实请求、预留/结算、实际 tokens/成本、每个 episode 的决策与工具事件、逐 episode hash-chain、全部 Genome/Phenotype、反馈概率、mutation/crossover、duplicate、survivor、Pareto front、final 以及执行锁。

- 任一 final 缺失、final 无真实 API 调用、hash-chain 失败、执行错误或超预算，整体不得标为有效完成。
- 报告 B3−B2、B4−B2、B5−B3、B5−B4 的总体及逐 seed 差值，同时报告搜索/Pareto/行为多样性与成本。
- 本修订只有 1 个补偿任务、2 个 seeds、1 代，属于机制冒烟和探索性证据；不能支持统计显著、普遍性能提升或毕业论文创新已经成立的结论。
- 即使出现正向差值，也只标记 `POSITIVE_SIGNAL`；仅增加多样性而无性能/搜索效率收益为 `NO_CLEAR_GAIN`。

预注册冻结时（历史状态，非执行后状态）：`FULL_REGRESSION=645/645`、`D094_TESTS=103/103`、`PREFLIGHT=PASS`、`INDEPENDENT_REVIEWED=RECHECK_PENDING`、`EXPERIMENT_COMPLETED=NO`。执行后的状态见顶部“执行登记”，此处不回改冻结设计。
