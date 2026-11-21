# D-094 R3.1 深度分析：从真实轨迹到 R4 主假设

日期：2026-11-21。分析对象仅为已完成的 R3.1 Train 真实实验；本报告不回改预注册、不制造新性能证据。

## 1. 数据、方法与完整性

- 原始目录：`experiments/d094_llm_agent/results/r3_1_real/`。
- 只读分析器：`experiments/d094_llm_agent/analyze_d094_r3_deep.py`。
- 结构化结果：`results/r3_1_deep_analysis/analysis.json`，内部 canonical SHA-256=`2362a32e6923d6c516661b301e6d7bcdb68e3a8ef6d78b3a8ff44271ce43982e`。
- 分析器读取全部 episodes、traces、请求账本、archive、evolution、manifest、summary 和独立审计；从公开事件、终态和请求记录重建 episode 指标，并逐项核对保存值。
- 分析前后对源目录全部文件做 SHA-256 快照，不一致即失败；分析输出写到新目录，`api_used=false`。
- 42/42 episode ID、169/169 provider request ID 唯一，42 条逐事件 hash-chain 有效，execution error=0；已有独立复算状态为 `PASS`。

本报告中的事后父子信用只是分析，不参与 R3.1 的选择，不是 R4 的实验结果。

## 2. 实际实验设计

R3.1 是单任务、两 seed 的机制冒烟实验，而不是跨任务泛化或确认性统计实验。

| 项目 | 冻结值 |
|---|---|
| Train 任务 | `d094_r3_train_compensation_0` |
| seeds | 201、202 |
| B1 | Fixed LLM，2 episodes |
| B2/B3/B4/B5 | 初始种群 2、1 代、每臂 4 个唯一搜索候选 |
| 每演化臂 | search=8 episodes，独立 final=2 episodes |
| 合计 | 42 episodes、169 次真实 HTTP |
| 模型与控制 | deepseek-flash、temperature=0、非思考 JSON、重试 0 |
| 成本 | 127148/8090 输入/输出 tokens，0.0478524 USD |

final 虽重新执行，但重复同一 Train 任务和 seeds，不是 held-out 泛化证据。

## 3. 各臂逐任务、逐 seed 与配对表现

由于只有一个任务，逐任务数值等于总体数值，不能把它包装为多任务分析。

| 臂/阶段 | Task Success | Recovery | 约束数 | Harm | Tool Cost | 请求数 |
|---|---:|---:|---:|---:|---:|---:|
| B1 fixed | 1.00 | 1.00 | 0 | 0.25 | 8.4 | 9 |
| B2 search | 0.00 | 0.00 | 16 | 1.50 | 10.2 | 34 |
| B2 final | 0.00 | 0.00 | 0 | 0.50 | 3.4 | 6 |
| B3 search | 0.00 | 0.00 | 22 | 1.00 | 6.8 | 34 |
| B3 final | 0.00 | 0.00 | 0 | 0.50 | 3.4 | 6 |
| B4 search | 0.00 | 0.00 | 16 | 1.50 | 10.2 | 34 |
| B4 final | 0.00 | 0.00 | 0 | 0.50 | 3.4 | 6 |
| B5 search | 0.00 | 0.00 | 22 | 1.00 | 6.8 | 34 |
| B5 final | 0.00 | 0.00 | 0 | 0.50 | 3.4 | 6 |

逐 seed 的 Task/Recovery Success：B1 在 201、202 均为 1/1；四个演化 final 在两个 seed 均为 0/1。预注册四个比较的总体和两个 seed 成功率差均为 0：

- B3−B2=0；
- B4−B2=0；
- B5−B3=0；
- B5−B4=0。

成本或延迟的零星差异不能抵消零成功率。结论保持 `NO_CLEAR_GAIN`。

## 4. 搜索是否真正发生变化

| 臂 | 唯一 Genome | 唯一 Phenotype | variation | duplicate | feedback update |
|---|---:|---:|---:|---:|---:|
| B2 | 4 | 2 | 3 | 1 | 0 |
| B3 | 4 | 3 | 4 | 2 | 4 |
| B4 | 4 | 2 | 3 | 1 | 0 |
| B5 | 4 | 3 | 4 | 2 | 4 |

- 四臂各有 4 个不同 Genome，变异确实进入执行链。
- B3/B5 的失败反馈改变了算子概率，并增加了搜索期唯一 Phenotype；这是机制信号，不是任务改善。
- B4 与 B2 的 Genome/候选一致，唯一 Phenotype 都是 2；在该规模下没有表现出额外多样性收益。
- B5 没有显示反馈与多样性的互补收益，也没有支持继续叠加参数的证据。
- **16/16 搜索候选的 Task Success 全为 0。** 因而没有任何成功候选可供反馈、多样性或 survivor 机制学习，不能将“搜索轨迹改变”解释为“有效搜索方向已找到”。

## 5. 实际执行行为与失败模式

### 5.1 最终轨迹

四个演化臂的 8 个 final episodes 全部沿 `inspect_state → verify_state → retry_primary` 走到三步上限。永久失败后未执行 `compensate_primary` 或 `complete_task`，终态均为 `MAX_STEPS`。final 没有工具拒绝、提前 finish、预算拒绝或传输错误。

这是直接轨迹原因，但不是唯一因果证明：B1 与演化 final 同时存在步数、规划/恢复基因等差异，单任务两 seed 不能做进一步分解。

### 5.2 搜索期拒绝循环

- B2/B4：`RECOVERY_COMPENSATION_REQUIRED` 各 16 次；B3/B5 各 22 次。
- 所有 search episodes 均 `MAX_STEPS`。
- B3/B5 的 recovery mutation 把 `retry_priority` 改为 `compensation_priority`，Phenotype 改变，但在 seed 201 和 202 均增加 3 次约束违反；事后质量信用均为 -1。
- 这说明失败频率或行为新颖性可奖励“更不同的拒绝循环”，却不能识别真实质量改进。

## 6. Genome/Phenotype、Pareto 与事后父子信用

- B2/B4 搜索唯一 Phenotype=2，B3/B5=3；final 的两 seed 行为多样性均为 0.5。
- 独立重建的 Pareto/final 与原执行一致。
- B5 的 `verification_mutation` 在七目标事后比较中得到 +1：其子代延迟/token 更低，但 Success、Recovery、Harm、约束和 Phenotype 都没有改善。
- B2/B4 也观察到纯资源变化驱动的事后 Pareto 奖励，而质量信用为 0。
- 因此，**若直接以完整七目标 Pareto 改进作为主信用，资源抖动可能被误记为算法进展。** R4 必须把硬约束、任务/恢复成功和 Harm 的主信用与资源目标分开。

## 7. 请求、Token、重试与成本

- 每请求平均输入/输出 tokens=752.3550/47.8698，最大=831/55。
- 每 episode 平均请求=4.0238；历史最大请求数=8 对应旧 max_plan_steps=8 的候选，不可套作 R4 的固定值。
- 所有实际请求成功，失败请求数=0，失败请求成本=0。
- 冻结 `max_retries=0`。请求账本中的 `attempt` 是 episode 内请求序号，不是 HTTP 重试号。
- 相同 Prompt 重发记录为 6/169=3.5503%，不得误报为 75% HTTP 重试。
- canonical message bytes 未保存于 episode，只能审计 4096-byte 冻结上限，不能补造历史最大字节数。
- 独立复算不需要真实 API。

## 8. 数据缺口

1. 只有一个 Train 任务和两个 seeds，不能支持跨任务、普遍提升或显著性结论。
2. final 不是 held-out。
3. 一代、每臂两个 offspring 无法识别稳定算子信用或长时程效果。
4. 历史 canonical request bytes 不可得。
5. 事后信用只用于解释和提出假设，不能回填为 R3.1 的在线算法收益。

## 9. 没有明确提升的具体原因

1. **可达性先于学习：** 多个候选在三步内无法完成补偿和完成动作，搜索缺乏成功信号。
2. **反馈语义错位：** 静态失败频率不能判断某算子是否在同任务、同 seed 上真正改善结果。
3. **资源信用混杂：** 完整七目标 Pareto 改善可能只来自 token/延迟变化。
4. **多样性不等于质量：** B3/B5 增加的 Phenotype 包含约束拒绝循环；B4 没有表现出独立优势。
5. **样本与搜索长度过短：** 无法据此识别稳定机制或做普遍推断；但“规模小”不能掩盖上述具体机制问题。

## 10. 最值得继续研究的三个机制

1. **质量优先的配对父子算子信用（R4 主机制）：** 在完全相同 task/seed 单元上比较父子；先约束，再 Success/Recovery/Harm，排除纯资源收益。直接对应“反馈不知道算子是否有效”的缺口。
2. **质量约束下的状态条件化行为差异（后续候选）：** 仅让达到质量门的行为差异参与生存者选择，避免奖励拒绝循环；本轮不叠加，保留独立归因。
3. **状态条件化恢复策略（后续候选）：** 根据公开恢复阶段而非粗粒度失败类型选择动作/基因；需要更多状态覆盖，当前数据不足以同时验证。

## 11. R4 决策

保留旧 B2/B3/B4/B5 源码与结果，选择 **B3=质量优先的配对父子算子信用**；B2 为标准 NSGA-II/均匀算子强基线，B4 为旧失败频率反馈消融，B1 为 Fixed LLM，不保留 B5。公共五步动作可达性是所有臂共享的有效性前提，不作为创新收益。

R4 的设计、实现和合成验证见 `D094_R4_ALGORITHM_DESIGN.md`、`D094_R4_PREREGISTRATION.md` 与 `D094_R4_IMPLEMENTATION_REVIEW.md`。真实 R4 仍未运行，独立审查与实验批准均未获得。
